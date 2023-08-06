import argparse
import os, sys

from .tools import ALGORITHM, preprocessor, grid

import bob.extension
import bob.core
logger = bob.core.log.setup("bob.chapter.FRICE")

import bob.bio.base
import bob.bio.face
import bob.bio.gmm


PROTOCOLS = {
  'lfw'     : ['fold%d'%d for d in range(1,11)],
  'mobio'   : ['female', 'male']
}


def command_line_arguments():
  parser = argparse.ArgumentParser(description="Execute baseline algorithms with default parameters", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-x', '--task', required=True, choices = ('preprocess', 'execute', 'evaluate'), help="The task you want to execute.")
  parser.add_argument('-a', '--algorithms', choices = ['Graphs', 'LGBPHS', 'ISV', 'LDA-IR', 'COTS'], default = ['Graphs', 'LGBPHS', 'ISV', 'LDA-IR'], nargs = '+', help = "Select one (or more) algorithms that you want to execute")
  parser.add_argument('--all', action='store_true', help = "If selected, all algorithms will be executed/evaluated, including COTS, which is by default left out")
  parser.add_argument('-d', '--databases', choices = PROTOCOLS.keys(), nargs = '+', default = PROTOCOLS.keys(), help = "The database on which the algorithms are executed")
  parser.add_argument('-R', '--result-directory', default = 'FRICE/results/databases', help = 'Select the directory where to write the score files to')
  parser.add_argument('-T', '--temp-directory', default = 'FRICE/temp/databases', help = 'Select the directory where to write temporary files to')

  parser.add_argument('-q', '--dry-run', action = 'store_true', help = "Just print the commands, but do not execute them")
  parser.add_argument('-g', '--grid', action = 'store_true', help = "Execute the algorithms in the SGE grid")
  parser.add_argument('-p', '--parallel', type=int, help = 'Execute the algorithms in parallel on the local machine using the given number of parallel jobs')

  parser.add_argument('-w', '--plot', default = 'databases.pdf', help = "The file to contain the plot, where %s is replaced with the database name.")

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

  isv_executables = bob.extension.find_executable('verify_isv.py', prefixes = [os.path.dirname(sys.argv[0]), 'bin'])
  assert isv_executables, "Could not find the 'verify_isv.py' executable (usually located in the 'bin' directory. Is there anything wrong with your installation?"
  isv_executable = isv_executables[0]

  # create base call
  base_call = ['--groups', 'dev', 'eval']
  if args.verbose:
    base_call.append("-"+"v"*args.verbose)
  if args.parallel is not None:
    base_call.extend(['--parallel', str(args.parallel)])

  if args.task == 'preprocess':
    # get all the preprocessors for the current view direction
    calls = []
    for database in args.databases:
      db_call = base_call + ['--temp-directory', os.path.join(args.temp_directory, database), '--result-directory', os.path.join(args.result_directory, database), '--database', database, '--gridtk-database-file', os.path.join(args.temp_directory, 'gridtk_db', database, 'submitted.sql3')]
      for protocol in PROTOCOLS[database]:
        if 'LDA-IR' in args.algorithms:
          calls.append(db_call + ALGORITHM['LDA-IR'] + ['--sub-directory', preprocessor('LDA-IR'), '--protocol', protocol])
        if 'Graphs' in args.algorithms:
          calls.append(db_call + ALGORITHM['Graphs'] + ['--sub-directory', preprocessor('Graphs'), '--protocol', protocol])
        if 'LGBPHS' in args.algorithms or 'ISV' in args.algorithms:
          calls.append(db_call + ALGORITHM['ISV'] + ['--sub-directory', preprocessor('ISV'), '--protocol', protocol])
        if 'COTS' in args.algorithms:
          calls.append(db_call + ALGORITHM['COTS'] + ['--sub-directory', preprocessor('COTS'), '--protocol', protocol])

    # execute all required preprocessors
    for call in calls:
      # generate parameters for preprocessors
      call += ['--execute-only', 'preprocessing', '--preferred-package', 'bob.chapter.FRICE']
      if args.grid:
        call.extend(grid(database))
      if args.parameters:
        call.extend(args.parameters[1:])

      print (bob.bio.base.tools.command_line([executable] + call))
      if not args.dry_run:
        # call the faceverify script with the collected parameters
        bob.bio.base.script.verify.main(call)

  elif args.task == 'execute':
    for database in args.databases:
      db_call = base_call + ['--temp-directory', os.path.join(args.temp_directory, database), '--result-directory', os.path.join(args.result_directory, database), '--database', database, '--gridtk-database-file', os.path.join(args.temp_directory, 'gridtk_db', database, 'submitted.sql3')]
      for protocol in PROTOCOLS[database]:
        for algorithm in args.algorithms:
          call = db_call + ALGORITHM[algorithm] + ['--protocol', protocol, '--sub-directory', algorithm, '--preprocessed-directory', os.path.join('..', preprocessor(algorithm), 'preprocessed'), '--skip-preprocessing']
          if args.grid:
            call.extend(grid(database, algorithm))
          if args.parameters:
            call.extend(args.parameters[1:])

          if algorithm == 'ISV' and (args.grid or args.parallel is not None):
            # for ISV, we here use the parallel implementation, as it takes to much time and memory otherwise
            # special options for verify_isv
            call += ['--limit-training-data', '100', '--clean-intermediate']
            print (bob.bio.base.tools.command_line([isv_executable] + call))
            if not args.dry_run:
              # fortunately, it has almost the same parameters...
              bob.bio.gmm.script.verify_isv.main(call)
          else:
            # use the default script otherwise
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

    from .tools import EER, EER_HTER, RR, COLORS, MARKERS, average
    import numpy

    pdf = PdfPages(args.plot)

    if 'mobio' in args.databases:
      logger.info("Evaluating database mobio")
      protocols = PROTOCOLS['mobio']

      x = range((len(args.algorithms) * 2 + 2) * (len(protocols)+1))
      y1 = [numpy.nan] * len(x)
      y2 = [numpy.nan] * len(x)
      c = [(0,0,0,0)] * len(x)
      index = 1
      for protocol in protocols:
        for algorithm in args.algorithms:
          score_files = [os.path.join(args.result_directory, 'mobio', algorithm, protocol, 'nonorm', 'scores-%s'%g) for g in ('dev', 'eval')]
          if os.path.exists(score_files[0]) and os.path.exists(score_files[1]):
            res = [r * 100. for r in EER_HTER(score_files[0], score_files[1])]
            y1[index], y2[index] = res
            c[index] = COLORS[algorithm]
            logger.info("Results for algorithm %s in protocol %s is %3.2f EER and %3.2f HTER", algorithm, protocol, res[0], res[1])
          else:
            logger.warn("Could not find result files %s and/or %s for algorithm %s and protocol %s", score_files[0], score_files[1], algorithm, protocol)
          index += 1
        index += 2

      height = max(numpy.nanmax(y1), numpy.nanmax(y2)) * 1.35

      for y,t,s in ((y1, 'EER', 'development'), (y2, 'HTER', 'evaluation')):
        figure = plt.figure()
        plt.bar(x, y, color=c, align='center' )
        plt.axis((0, index-2, 0, height))
        ticks = [(len(args.algorithms))/2. + .5 + i * (len(args.algorithms) +2) for i in range(len(protocols))]
        plt.xticks(ticks, protocols, va='baseline')

        # dirty HACK to generate legends
        l = [plt.bar([j],[0],color=COLORS[a]) for j, a in enumerate(args.algorithms)]
        plt.legend(l, args.algorithms, loc=9, ncol=2, prop={'size':16})
        plt.ylabel('%s on MOBIO %s set in \%%' % (t,s))
        plt.xlabel('Protocol of database MOBIO')

        pdf.savefig(figure)

    if 'lfw' in args.databases:
       # for lfw, we just report the final result
      x = range((len(args.algorithms) * 2 + 1))
      y = [numpy.nan] * len(x)
      s = [numpy.nan] * len(x)
      c = [(0,0,0,0)] * len(x)

      index = 1
      algorithms = args.algorithms[:]
      for algorithm in args.algorithms:
        files = [os.path.join(args.result_directory, 'lfw', algorithm, protocol, 'nonorm', 'scores-%s') for protocol in PROTOCOLS['lfw']]
        result = average([(f%'dev', f%'eval') for f in files])
        if result is not None:
          y[index], s[index] = result
          c[index] = COLORS[algorithm]
          logger.info("  Average result of %s: mean Accuracy: %3.2f" % (algorithm, result[0]))
        index += 2

      # plot results with error bars
      figure = plt.figure()
      plt.bar(x, y, color=c, align='center', yerr=s, ecolor='k', capsize=5, error_kw={'lw':2, 'mew':2})
      plt.xticks(range(1, index, 2), [r'%2.1f\%%' % y[i] for i in range(1, index, 2)], va='baseline')
      l = [plt.bar([j],[0],color=c[j]) for j in range(1, index, 2)]
      plt.legend(l, args.algorithms, ncol=2, loc=9, prop={'size':16})
      plt.axis((0, max(x), 0, 100))

      plt.ylabel('Classification Success on LFW in \%')
#      plt.xlabel("Parameters")

      pdf.savefig(figure)

    pdf.close()
    logger.info("Wrote plot %s", args.plot)
