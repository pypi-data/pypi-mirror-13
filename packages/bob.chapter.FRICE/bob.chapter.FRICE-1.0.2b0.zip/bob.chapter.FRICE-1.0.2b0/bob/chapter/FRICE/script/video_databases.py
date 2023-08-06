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
  'mobio'   : ['female', 'male'],
  'youtube' : ['fold%d'%d for d in range(1,11)],
}

face_detector = 'bob.bio.face.preprocessor.FaceDetect(face_cropper="face-crop", use_flandmark=True)'

def detector(algorithm):
  return {
    'inorm-lbp' : 'bob.bio.face.preprocessor.INormLBP(face_cropper=%s, dtype=numpy.float64)' % face_detector,
    'tan-triggs' : 'bob.bio.face.preprocessor.TanTriggs(face_cropper=%s)' % face_detector,
    'cots' : '...',
    'lda-ir' : 'bob.bio.csu.preprocessor.LDAIR(face_detector=%s)' % face_detector
  } [preprocessor(algorithm)]


def frame_selector(args):
  return 'bob.bio.video.FrameSelector(%d, "%s", %d)' % (args.number_of_frames, args.frame_selection, args.frame_skip)

def preprocess_configuration(algorithm, fs):
  return [
    '--preprocessor', 'bob.bio.video.preprocessor.Wrapper(preprocessor=%s, frame_selector=%s)' % (detector(algorithm), fs),
    '--extractor', 'bob.bio.video.extractor.Wrapper(extractor="%s")' % ALGORITHM[algorithm][3],
    '--algorithm', 'bob.bio.video.algorithm.Wrapper(algorithm="%s")' % ALGORITHM[algorithm][5],
    '--imports', 'bob.bio.video', 'bob.bio.face', 'bob.bio.csu', 'bob.bio.gmm', 'numpy',
    '--execute-only', 'preprocessing',
    '--sub-directory', preprocessor(algorithm)
  ]

def execute_configuration(algorithm):
  return [
    '--preprocessor', 'bob.bio.video.preprocessor.Wrapper(preprocessor=%s)' % detector(algorithm), # ignored, but must be a video preprocessor
    '--preprocessed-directory', os.path.join('..', preprocessor(algorithm), 'preprocessed'), '--skip-preprocessing',
    '--extractor', 'bob.bio.video.extractor.Wrapper(extractor="%s")' % ALGORITHM[algorithm][3],
    '--algorithm', 'bob.bio.video.algorithm.Wrapper(algorithm="%s")' % ALGORITHM[algorithm][5],
    '--imports', 'bob.bio.video', 'bob.bio.face', 'bob.bio.csu', 'bob.bio.gmm', 'numpy',
    '--sub-directory', algorithm
  ]



STYLES = {
  1 : {'hatch' : '//'},
  3 : {'hatch' : '..'},
  10 : {'hatch' : '\\\\'},
  20 : {'hatch' : '**'},
  0 : {}
}

def command_line_arguments():
  parser = argparse.ArgumentParser(description="Execute baseline algorithms with default parameters", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-x', '--task', required=True, choices = ('preprocess', 'execute', 'evaluate'), help="The task you want to execute.")
  parser.add_argument('-a', '--algorithms', choices = ['Graphs', 'LGBPHS', 'ISV', 'LDA-IR', 'COTS'], default = ['Graphs', 'LGBPHS', 'ISV', 'LDA-IR'], nargs = '+', help = "Select one (or more) algorithms that you want to execute")
  parser.add_argument('--all', action='store_true', help = "If selected, all algorithms will be executed/evaluated, including COTS, which is by default left out")
  parser.add_argument('-d', '--databases', choices = PROTOCOLS.keys(), nargs = '+', default = PROTOCOLS.keys(), help = "The database on which the algorithms are executed")
  parser.add_argument('-n', '--number-of-frames', default=20, type=int, help = "Select the number of frames per video that should be kept.")
  parser.add_argument('-f', '--frame-selection', default='spread', choices = ('spread', 'step', 'quality'), help = "Select the frame selection style (quality is very slow!).")
  parser.add_argument('-s', '--frame-skip', default=10, type=int, help = "Select the number of frames that should be skipped between two valid frames (only used with --frame-selection step).")

  parser.add_argument('-R', '--result-directory', default = 'FRICE/results/video', help = 'Select the directory where to write the score files to')
  parser.add_argument('-T', '--temp-directory', default = 'FRICE/temp/video', help = 'Select the directory where to write temporary files to')

  parser.add_argument('-q', '--dry-run', action = 'store_true', help = "Just print the commands, but do not execute them")
  parser.add_argument('-g', '--grid', action = 'store_true', help = "Execute the algorithms in the SGE grid")
  parser.add_argument('-p', '--parallel', type=int, help = 'Execute the algorithms in parallel on the local machine using the given number of parallel jobs')

  parser.add_argument('-w', '--plot', default = 'video.pdf', help = "The file to contain the plot, where %%s is replaced with the database name.")

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

    calls = []
      # get all the preprocessors for the given number of frames
    for database in args.databases:
      db_call = base_call + ['--database', '%s-video' % database, '--temp-directory', os.path.join(args.temp_directory, database, "Frames_%d"%args.number_of_frames), '--result-directory', os.path.join(args.result_directory, database, "Frames_%d"%args.number_of_frames), '--gridtk-database-file', os.path.join(args.temp_directory, 'gridtk_db', database, 'submitted.sql3')]

      fs = frame_selector(args)
      for protocol in PROTOCOLS[database]:
        if 'LDA-IR' in args.algorithms or 'CohortLDA' in args.algorithms:
          calls.append(db_call + preprocess_configuration('LDA-IR', fs))
        if 'Graphs' in args.algorithms:
          calls.append(db_call + preprocess_configuration('Graphs', fs))
        if 'LGBPHS' in args.algorithms or 'ISV' in args.algorithms:
          calls.append(db_call + preprocess_configuration('ISV', fs))
        if 'COTS' in args.algorithms:
          calls.append(base_call + preprocess_configuration('COTS', fs))

    # execute all required preprocessors
    for call in calls:
      call += ['--preferred-package', 'bob.chapter.FRICE']
      if args.grid:
        call.extend(grid(database))
      if args.parameters:
        call.extend(args.parameters[1:])

      print (bob.bio.base.tools.command_line([executable] + call))
      if not args.dry_run:
        # call the faceverify script with the collected parameters
        bob.bio.base.script.verify.main(call)

  elif args.task == 'execute':
    # get all the algorithms for the given number of frames
    calls = []
    for database in args.databases:
      db_call = base_call + ['--database', '%s-video' % database, '--temp-directory', os.path.join(args.temp_directory, database, "Frames_%d"%args.number_of_frames), '--result-directory', os.path.join(args.result_directory, database, "Frames_%d"%args.number_of_frames), '--gridtk-database-file', os.path.join(args.temp_directory, 'gridtk_db', database, 'submitted.sql3')]

      for protocol in PROTOCOLS[database]:
        for algorithm in args.algorithms:
          call = db_call + execute_configuration(algorithm) + ['--protocol', protocol]

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

    frames = (1, 3, 10, 20)

    pdf = PdfPages(args.plot)
    if 'youtube' in args.databases:
      logger.info("Evaluating database 'youtube'")
      protocols = PROTOCOLS['youtube']

      x = range(((len(frames) + 1) * 2 + 2) * (len(args.algorithms)+1))
      y = [numpy.nan] * len(x)
      s = [numpy.nan] * len(x)
      c = [(0,0,0,0)] * len(x)
      v = [{} for _ in range(len(x))]

      index = 1
      algorithms = args.algorithms[:]
      for algorithm in args.algorithms:
        for count in frames:
          files = [os.path.join(args.result_directory, 'youtube', 'Frames_%d' % count, algorithm, protocol, 'nonorm', 'scores-%s') for protocol in protocols]
          result = average([(f%'dev', f%'eval') for f in files])
          if result is not None:
            y[index], s[index] = result
            c[index] = COLORS[algorithm]
            v[index] = STYLES[count]
            logger.info("  Average result of %s (%d): mean Accuracy: %3.2f", algorithm, count, result[0])
          index += 1
        index += 2


        # add baseline results
        """
        for count in (1, 20):
          for norm in args.norms:
            files = [os.path.join(args.result_directory, 'youtube', 'Baseline/m_%d-p_%d-frames/%s/%s/scores-eval' % (count, count, protocol, norm)) for protocol in YOUTUBE_PROTOCOLS]
            result = _average(files)

            styles += [_style('Baseline', norm, count)]
            facereclib.utils.info("  Average result of Baseline (%d) - %s: mean EER: %3.2f, mean cllr: %1.4f" % (count, norm, results[-1][0], results[-1][2]))
        """

      # add baselines for youtube
      y[index+1] = 65.7
      s[index+1] = 1.7
      c[index+1] = (0.2,0.2,0.2)
      y[index+2] = 76.4
      s[index+2] = 1.8
      c[index+2] = (0., 0., 0.)
      index += 3
      algorithms.append("[71]")

      # plot
      figure = plt.figure()
      for i in range(index):
        plt.bar(x[i], y[i], color=c[i], yerr=s[i], ecolor='k', capsize=5, error_kw={'lw':2, 'mew':2}, align='center', **v[i])
      plt.axis((0, index+1, 0, 100))
      ticks = [(len(frames))/2. + .5 + i * (len(frames) +2) for i in range(len(algorithms))]
      plt.xticks(ticks, algorithms, va='baseline')

      # legend
      [plt.bar([-1],[0], label = "%d Frames" % (count), color =(1., 1., 1.), **STYLES[count]) for count in frames]
      plt.bar([-1],[0], label = "LBP min dist [71]", color=c[index-2])
      plt.bar([-1],[0], label = "best of [71]", color=c[index-1])
      plt.legend(loc=9, prop = {'size':12}, ncol=3)

      plt.ylabel('Classification Success on YouTube in \%')
      pdf.savefig(figure)

    if 'mobio' in args.databases:
      # add frames=0 to indicate hand-labeled images
      frames = [f for f in frames] + [0]

      for protocol in PROTOCOLS['mobio']:
        x = range(((len(frames) + 1) * 2 + 2) * (len(args.algorithms)+1))
        y1 = [numpy.nan] * len(x)
        y2 = [numpy.nan] * len(x)
        c = [(0,0,0,0)] * len(x)
        v = [{} for _ in range(len(x))]

        index = 1
        algorithms = args.algorithms[:]
        for algorithm in args.algorithms:
          for count in frames:
            if count == 0:
              files = [os.path.join(args.result_directory.replace("video","databases"), 'mobio', algorithm, protocol, 'nonorm', 'scores-%s'%g) for g in ('dev', 'eval')]
            else:
              files = [os.path.join(args.result_directory, 'mobio', 'Frames_%d' % count, algorithm, protocol, 'nonorm', 'scores-%s' % group) for group in ('dev', 'eval')]
            if os.path.exists(files[0]) and os.path.exists(files[1]):
              y1[index], y2[index] = [r * 100. for r in EER_HTER(*files)]
              c[index] = COLORS[algorithm]
              v[index] = STYLES[count]
              logger.info("Protocol %s, Result of %s (%d): EER: %3.2f%%; HTER: %3.2f%%", protocol, algorithm, count, y1[index], y2[index])
            else:
              logger.warn("Could not find result files %s and/or %s for frame count %d in algorithm %s and protocol %s", files[0], files[1], count, algorithm, protocol)
            index += 1
          index += 2

        # plot
        for y, label in zip((y1,y2), ("EER on MOBIO development set", "HTER on MOBIO evaluation set")):
          figure = plt.figure()
          for i in range(index):
            plt.bar(x[i], y[i], color=c[i], align='center', **v[i])
#            plt.axis((0, index-2, 0, numpy.nanmax(y) * 1.35))
          plt.axis((0, index-2, 0, 35))
          ticks = [(len(frames))/2. + .5 + i * (len(frames) +2) for i in range(len(algorithms))]
          plt.xticks(ticks, algorithms, va='baseline')

          # legend
          [plt.bar([-1],[0], label = "%d Frames" % (count) if count else "Hand-labeled", color =(1., 1., 1.), **STYLES[count]) for count in frames]
          plt.legend(loc=9, prop = {'size':12}, ncol=3)

          plt.ylabel('%s in \%%' % label)
          plt.title("Protocol '%s'" % protocol)
          pdf.savefig(figure)


    pdf.close()
    logger.info("Wrote file %s", args.plot)
