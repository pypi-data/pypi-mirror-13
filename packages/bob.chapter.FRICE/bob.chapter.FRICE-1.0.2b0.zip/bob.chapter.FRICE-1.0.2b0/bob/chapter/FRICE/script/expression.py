import argparse
import os, sys

from .tools import ALGORITHM, preprocessor, grid

import bob.extension
import bob.core
logger = bob.core.log.setup("bob.chapter.FRICE")

import bob.bio.base
import bob.bio.face
import bob.bio.gmm

def command_line_arguments():
  parser = argparse.ArgumentParser(description="Execute baseline algorithms with default parameters", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-x', '--task', required=True, choices = ('preprocess', 'execute', 'evaluate'), help="The task you want to execute.")
  parser.add_argument('-a', '--algorithms', choices = ['Graphs', 'LGBPHS', 'ISV', 'LDA-IR', 'COTS'], default = ['Graphs', 'LGBPHS', 'ISV', 'LDA-IR'], nargs = '+', help = "Select one (or more) algorithms that you want to execute")
  parser.add_argument('--all', action='store_true', help = "If selected, all algorithms will be executed/evaluated, including COTS, which is by default left out")
  parser.add_argument('-d', '--database', choices=('multipie',), default = 'multipie', help = "The database on which the algorithms are executed")
  parser.add_argument('-P', '--protocol', default = 'E', help = "Select the protocol that should be executed")
  parser.add_argument('-R', '--result-directory', default = 'FRICE/results/expression', help = 'Select the directory where to write the score files to')
  parser.add_argument('-T', '--temp-directory', default = 'FRICE/temp/expression', help = 'Select the directory where to write temporary files to')

  parser.add_argument('-q', '--dry-run', action = 'store_true', help = "Just print the commands, but do not execute them")
  parser.add_argument('-g', '--grid', action = 'store_true', help = "Execute the algorithms in the SGE grid")
  parser.add_argument('-p', '--parallel', type=int, help = 'Execute the algorithms in parallel on the local machine using the given number of parallel jobs')

  parser.add_argument('-w', '--plot', default='expressions.pdf', help = "The file to contain the plot.")

  parser.add_argument('parameters', nargs = argparse.REMAINDER, help = "Parameters directly passed to the face verification script.")

  # add logger arguments (including the default --verbose option)
  bob.core.log.add_command_line_option(parser)
  args = parser.parse_args()
  bob.core.log.set_verbosity_level(logger, args.verbose)

  if args.all: args.algorithms = ['Graphs', 'LGBPHS', 'ISV', 'LDA-IR', 'COTS']

  return args


def main():
  args = command_line_arguments()

  executables = bob.extension.find_executable('verify.py', prefixes = [os.path.dirname(sys.argv[0]), 'bin'])
  assert executables, "Could not find the 'verify.py' executable (usually located in the 'bin' directory. Is there anything wrong with your installation?"
  executable = executables[0]

  # create base call
  base_call = ['--temp-directory', args.temp_directory, '--result-directory', args.result_directory, '--database', args.database, '--protocol', args.protocol, '--groups', 'dev', 'eval', '--gridtk-database-file', os.path.join(args.temp_directory, 'gridtk_db', 'submitted.sql3')]
  if args.verbose:
    base_call.append("-"+"v"*args.verbose)
  if args.parallel is not None:
    base_call.extend(['--parallel', str(args.parallel)])

  if args.task == 'preprocess':
    # get all the preprocessors for the current view direction
    calls = []
    if 'LDA-IR' in args.algorithms:
      calls.append(base_call + ALGORITHM['LDA-IR'] + ['--sub-directory', preprocessor('LDA-IR')])
    if 'Graphs' in args.algorithms:
      calls.append(base_call + ALGORITHM['Graphs'] + ['--sub-directory', preprocessor('Graphs')])
    if 'LGBPHS' in args.algorithms or 'ISV' in args.algorithms:
      calls.append(base_call + ALGORITHM['ISV'] + ['--sub-directory', preprocessor('ISV')])
    if 'COTS' in args.algorithms:
      calls.append(base_call + ALGORITHM['COTS'] + ['--sub-directory', preprocessor('COTS')])

    # execute all required preprocessors
    for call in calls:
      call += ['--execute-only', 'preprocessing', '--preferred-package', 'bob.chapter.FRICE']
      # generate parameters for preprocessors
      if args.grid:
        call.extend(grid(args.database))
      if args.parameters:
        call.extend(args.parameters[1:])

      print (bob.bio.base.tools.command_line([executable] + call))
      if not args.dry_run:
        # call the faceverify script with the collected parameters
        bob.bio.base.script.verify.main(call)

  elif args.task == 'execute':
    calls = []
    for algorithm in args.algorithms:
      call = base_call + ALGORITHM[algorithm] + ['--sub-directory', algorithm, '--preprocessed-directory', os.path.join('..', preprocessor(algorithm), 'preprocessed'), '--skip-preprocessing']
      if args.grid:
        call.extend(grid(args.database, algorithm))
      calls.append(call)

    for call in calls:
      if args.parameters:
        call.extend(args.parameters[1:])

      print (bob.bio.base.tools.command_line([executable] + call))
      if not args.dry_run:
        # call the faceverify script with the collected parameters
        bob.bio.base.script.verify.main(call)

  else: # evaluate

    # for plotting
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    # enable LaTeX interpreter
    matplotlib.rc('text', usetex=True)
    matplotlib.rc('font', family='serif')
    # increase the default font size
    matplotlib.rc('font', size=18)
    matplotlib.rcParams['xtick.major.pad'] = 16

    plt.ioff()

    from .tools import EER_HTER, COLORS
    import numpy

    from bob.db.multipie import Database
    db = Database()
    EXPRESSIONS = ['all'] + [str(e.name) for e in db.expressions()]

    expression_translation = {str(f.path) : str(f.expression.name) for f in db.probe_files(protocol=args.protocol, groups=('dev', 'eval'))}

    # collect results
    result_files = {}
    for algorithm in args.algorithms:
      files = [os.path.join(args.result_directory, algorithm, args.protocol, 'nonorm', 'scores-%s' %s) for s in ('dev', 'eval')]
      if os.path.exists(files[0]) and os.path.exists(files[1]):
        result_files[algorithm] = files
      else:
        logger.warn("Could not find result files %s and/or %s for algorithm %s", files[0], files[1], algorithm)

    results = {}
    from StringIO import StringIO
    for algorithm in args.algorithms:
      if algorithm in result_files:
        results[algorithm] = {}
        dev = {expression : StringIO() for expression in EXPRESSIONS}
        eval = {expression : StringIO() for expression in EXPRESSIONS}

        for group, result in zip((dev, eval), result_files[algorithm]):
          with open(result) as f:
            for line in f:
              splits = line.split()
              assert len(splits) == 4
              # get the image type
              expression = expression_translation[splits[2]]
              if expression in group:
                group[expression].write(line)
                group['all'].write(line)

        # compute HTER for both occlusion types
        for expression in EXPRESSIONS:
          dev[expression].seek(0)
          eval[expression].seek(0)
          res = [r * 100. for r in EER_HTER(dev[expression], eval[expression])]
          logger.info("Results for algorithm %s for expression %s is %3.2f%% EER, %3.2f%% HTER" % (algorithm, expression, res[0], res[1]))
          results[algorithm][expression] = res

    # plot the results
    pdf = PdfPages(args.plot)
    figure = plt.figure()

    # create plots split into the different expressions
    x = range((len(args.algorithms) * 2 + 2) * (len(EXPRESSIONS)+1))
    y1 = [numpy.nan] * len(x)
    y2 = [numpy.nan] * len(x)
    c = [(0,0,0,0)] * len(x)
    index = 1
    for expression in EXPRESSIONS:
      for algorithm in args.algorithms:
        if algorithm in results and expression in results[algorithm]:
          y1[index] = results[algorithm][expression][0]
          y2[index] = results[algorithm][expression][1]
          c[index] = COLORS[algorithm]
        index += 1
      index += 2

    for y,t,s in ((y1, 'EER', 'development'), (y2, 'HTER', 'evaluation')):
      figure = plt.figure()
      plt.bar(x, y, color=c, align='center' )
      plt.axis((0, index-2, 0, numpy.nanmax(y) * 1.35))
      ticks = [(len(args.algorithms))/2. + .5 + i * (len(args.algorithms) +2) for i in range(len(EXPRESSIONS))]
      plt.xticks(ticks, EXPRESSIONS, va='baseline')

      # dirty HACK to generate legends
      l = [plt.bar([j],[0],color=COLORS[a]) for j, a in enumerate(args.algorithms)]
      plt.legend(l, args.algorithms, loc=9, ncol=2, prop={'size':16})
      plt.ylabel('%s on Multi-PIE %s set in \%%' % (t,s))
      plt.xlabel('Facial Expression')

      pdf.savefig(figure)

    # close pdf file
    pdf.close()

    logger.info("Wrote plot %s", args.plot)
