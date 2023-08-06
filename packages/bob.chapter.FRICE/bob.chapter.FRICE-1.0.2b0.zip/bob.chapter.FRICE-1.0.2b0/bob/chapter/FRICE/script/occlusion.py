import argparse
import os, sys

from .tools import ALGORITHM, preprocessor, grid

import bob.extension
import bob.core
logger = bob.core.log.setup("bob.chapter.FRICE")

import bob.bio.base
import bob.bio.face
import bob.bio.gmm


PROTOCOLS = {'illumination':'illumination', 'occlusion':'occlusion', 'both' : 'occlusion_and_illumination'}

def command_line_arguments():
  parser = argparse.ArgumentParser(description="Execute baseline algorithms with default parameters", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-x', '--task', required=True, choices = ('preprocess', 'train', 'execute', 'evaluate'), help="The task you want to execute.")
  parser.add_argument('-a', '--algorithms', choices = ['Graphs', 'LGBPHS', 'ISV', 'LDA-IR', 'COTS'], default = ['Graphs', 'LGBPHS', 'ISV', 'LDA-IR',], nargs = '+', help = "Select one (or more) algorithms that you want to execute")
  parser.add_argument('--all', action='store_true', help = "If selected, all algorithms will be executed/evaluated, including COTS, which is by default left out")
  parser.add_argument('-d', '--database', choices = ('arface-occ',), default = 'arface-occ', help = "The database on which the algorithms are executed")
  parser.add_argument('-P', '--protocols', choices = PROTOCOLS.keys(), nargs = '+', default = PROTOCOLS.keys(), help = "Select the protocols that should be executed")
  parser.add_argument('-R', '--result-directory', default = 'FRICE/results/occlusion', help = 'Select the directory where to write the score files to')
  parser.add_argument('-T', '--temp-directory', default = 'FRICE/temp/occlusion', help = 'Select the directory where to write temporary files to')

  parser.add_argument('-q', '--dry-run', action = 'store_true', help = "Just print the commands, but do not execute them")
  parser.add_argument('-g', '--grid', action = 'store_true', help = "Execute the algorithms in the SGE grid")
  parser.add_argument('-p', '--parallel', type=int, help = 'Execute the algorithms in parallel on the local machine using the given number of parallel jobs')

  parser.add_argument('-w', '--plot', default='occlusions.pdf', help = "The file to contain the plot.")

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
  base_call = ['--temp-directory', args.temp_directory, '--result-directory', args.result_directory, '--database', args.database, '--groups', 'dev', 'eval', '--gridtk-database-file', os.path.join(args.temp_directory, 'gridtk_db', 'submitted.sql3')]
  if args.verbose:
    base_call.append("-"+"v"*args.verbose)
  if args.parallel is not None:
    base_call.extend(['--parallel', str(args.parallel)])

  if args.task == 'preprocess':
    # get all the preprocessors
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

  elif args.task == 'train':
    calls = []

    for algorithm in args.algorithms:
      call = base_call + ALGORITHM[algorithm] + ['--sub-directory', algorithm, '--preprocessed-directory', os.path.join('..', preprocessor(algorithm), 'preprocessed'), '--execute-only', 'extractor-training', 'extraction', 'projector-training', 'projection', 'enroller-training', '--preferred-package', 'bob.chapter.FRICE']
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

  elif args.task == 'execute':
    calls = []

    for algorithm in args.algorithms:
      call = base_call + ALGORITHM[algorithm] + ['--sub-directory', algorithm, '--preprocessed-directory', os.path.join('..', preprocessor(algorithm), 'preprocessed'), '--execute-only', 'enrollment', 'score-computation', 'concatenation', '--preferred-package', 'bob.chapter.FRICE']
      if args.grid:
        call.extend(grid(args.database, algorithm))
      for protocol in args.protocols:
        # create call
        calls.append(call + ['--protocol', PROTOCOLS[protocol]])

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

    # collect result files
    result_files = {}
    results = {}
    for algorithm in args.algorithms:
      result_files[algorithm] = {}
      results[algorithm] = {}
      for protocol in args.protocols:
        files = [os.path.join(args.result_directory, algorithm, PROTOCOLS[protocol], 'nonorm', 'scores-%s' %s) for s in ('dev', 'eval')]
        if os.path.exists(files[0]) and os.path.exists(files[1]):
          result_files[algorithm][protocol] = files
          res = [r * 100. for r in EER_HTER(files[0], files[1])]
          logger.info("Results for algorithm %s for protocol %s is %3.2f%% EER, %3.2f%% HTER", algorithm, protocol, res[0], res[1])
          results[algorithm][protocol] = res
        else:
          logger.warn("Could not find result files %s and/or %s for algorithm %s and protocol %s", files[0], files[1], algorithm, protocol)

    # plot the avarage results
    x = range((len(args.algorithms) * 2 + 2) * (len(args.protocols)+1))
    y1 = [numpy.nan] * len(x)
    y2 = [numpy.nan] * len(x)
    c = [(0,0,0,0)] * len(x)

    index = 1
    for protocol in args.protocols:
      for algorithm in args.algorithms:
        if algorithm in results and protocol in results[algorithm]:
          y1[index] = results[algorithm][protocol][0]
          y2[index] = results[algorithm][protocol][1]
          c[index] = COLORS[algorithm]
        index += 1
      index += 2

    pdf = PdfPages(args.plot)
    for y,t,s in ((y1, 'EER', 'development'), (y2, 'HTER', 'evaluation')):
      figure = plt.figure()
      plt.bar(x, y, color=c, align='center' )
      plt.axis((0, index-2, 0, numpy.nanmax(y) * 1.35))
      ticks = [(len(args.algorithms))/2. + .5 + i * (len(args.algorithms) +2) for i in range(len(PROTOCOLS))]
      plt.xticks(ticks, args.protocols, va='baseline')

      # dirty HACK to generate legends
      l = [plt.bar([j],[0],color=COLORS[a]) for j, a in enumerate(args.algorithms)]
      plt.legend(l, args.algorithms, loc=9, ncol=2, prop={'size':16})
      plt.ylabel('%s on AR-face %s set in \%%' % (t,s))
      plt.xlabel('Illumination and/or occlusion condition')
      pdf.savefig(figure)

    figure = plt.figure()

    # collect results specific to one occlusion type
    OCCLUSIONS = ('scarf', 'sunglasses')
    results = {}
    from bob.db.arface.models import File
    from StringIO import StringIO
    for algorithm in args.algorithms:
      if result_files[algorithm]:
        results[algorithm] = {}
        dev = {'scarf' : StringIO(), 'sunglasses' : StringIO()}
        eval = {'scarf' : StringIO(), 'sunglasses' : StringIO()}

        for protocol in args.protocols:
          if protocol in result_files[algorithm]:
            with open(result_files[algorithm][protocol][0]) as f:
              for line in f:
                splits = line.split()
                assert len(splits) == 4
                # get the image type
                occlusion = File(splits[2]).occlusion
                if occlusion in dev:
                  dev[occlusion].write(line)

            with open(result_files[algorithm][protocol][1]) as f:
              for line in f:
                splits = line.split()
                assert len(splits) == 4
                # get the image type
                occlusion = File(splits[2]).occlusion
                if occlusion in eval:
                  eval[occlusion].write(line)

        # compute HTER for both occlusion types
        for occlusion in OCCLUSIONS:
          dev[occlusion].seek(0)
          eval[occlusion].seek(0)
          res = [r * 100. for r in EER_HTER(dev[occlusion], eval[occlusion])]
          logger.info("Results for algorithm %s for occlusion %s is %3.2f%% EER, %3.2f%% HTER", algorithm, occlusion, res[0], res[1])
          results[algorithm][occlusion] = res

    # create plots split into the different occlusions
    x = range((len(args.algorithms) * 2 + 2) * (len(OCCLUSIONS)+1))
    y1 = [numpy.nan] * len(x)
    y2 = [numpy.nan] * len(x)
    c = [(0,0,0,0)] * len(x)
    index = 1
    for occlusion in OCCLUSIONS:
      for algorithm in args.algorithms:
        if algorithm in results and occlusion in results[algorithm]:
          y1[index] = results[algorithm][occlusion][0]
          y2[index] = results[algorithm][occlusion][1]
          c[index] = COLORS[algorithm]
        index += 1
      index += 2

    for y,t,s in ((y1, 'EER', 'development'), (y2, 'HTER', 'evaluation')):
      figure = plt.figure()
      plt.bar(x, y, color=c, align='center' )
      plt.axis((0, index-2, 0, numpy.nanmax(y) * 1.35))
      ticks = [(len(args.algorithms))/2. + .5 + i * (len(args.algorithms) +2) for i in range(len(OCCLUSIONS))]
      plt.xticks(ticks, OCCLUSIONS, va='baseline')

      # dirty HACK to generate legends
      l = [plt.bar([j],[0],color=COLORS[a]) for j, a in enumerate(args.algorithms)]
      plt.legend(l, args.algorithms, loc=9, ncol=2, prop={'size':16})
      plt.ylabel('%s on AR-face %s set in \%%' % (t,s))
      plt.xlabel('Occlusion type')

      pdf.savefig(figure)

    # close pdf file
    pdf.close()

    logger.info("Wrote plot %s", args.plot)
