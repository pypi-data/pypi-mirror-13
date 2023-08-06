import argparse
import os, sys

from .tools import ALGORITHM, preprocessor, grid

import bob.extension
import bob.core
logger = bob.core.log.setup("bob.chapter.FRICE")

import bob.bio.base
import bob.bio.face
import bob.bio.gmm

ANGLES= {
  +90 : 'P240',
  +75 : 'P010',
  +60 : 'P200',
  +45 : 'P190',
  +30 : 'P041',
  +15 : 'P050',
  + 0 : 'P051',
  -15 : 'P140',
  -30 : 'P130',
  -45 : 'P080',
  -60 : 'P090',
  -75 : 'P120',
  -90 : 'P110'
}

PROTOCOLS = ['P'] + [ANGLES[p] for p in sorted(ANGLES.keys())]

CAMERAS = {
  'all'     : ('05_1', '24_0', '01_0', '20_0', '19_0', '04_1', '05_0', '14_0', '13_0', '08_0', '09_0', '12_0', '11_0'),

  'frontal' : ('19_0', '04_1', '05_0', '05_1', '13_0', '14_0', '08_0'),
  'left'    : ('09_0', '11_0', '12_0'),
  'right'   : ('24_0', '01_0', '20_0'),
}

# Different directions for preprocessing
DIRECTIONS = ['frontal', 'left', 'right']

# Different database configurations are required, as different annotations are used for to align images from different views
DATABASES = {
  view : 'bob.bio.base.database.DatabaseBob(\
database=bob.db.multipie.Database(\
original_directory="[YOUR_MULTI-PIE_IMAGE_DIRECTORY]",\
annotation_directory="[YOUR_MULTI-PIE_ANNOTATION_DIRECTORY]"\
),\
name="multipie",\
protocol="P", \
all_files_options={{"cameras":("{0}")}},\
extractor_training_options={{"cameras":("{0}")}},\
projector_training_options={{"cameras":("{0}")}},\
enroller_training_options={{"cameras":("05_1",)}}\
)' .format('","'.join(CAMERAS[view])) \
  for view in (DIRECTIONS + ['all'])
}

# generate a list of preprocessors in different views that will be used to preprocess images for different algorithms
CROPPERS = {
  'frontal' : 'bob.bio.face.preprocessor.FaceCrop(cropped_image_size=(80, 64), cropped_positions={"reye": (16, 15), "leye" : (16, 48)})',
  'left' : 'bob.bio.face.preprocessor.FaceCrop(cropped_image_size=(80, 64), cropped_positions={"eye" : (16, 25), "mouth": (52, 25)})',
  'right' : 'bob.bio.face.preprocessor.FaceCrop(cropped_image_size=(80, 64), cropped_positions={"eye" : (16, 38), "mouth": (52, 38)})'
}

PREPROCESSORS = {'tan-triggs-%s' % view : 'bob.bio.face.preprocessor.TanTriggs(face_cropper=\'%s\')' % CROPPERS[view] for view in DIRECTIONS}
PREPROCESSORS.update({'inorm-lbp-%s' % view : 'bob.bio.face.preprocessor.INormLBP(face_cropper=\'%s\')' % CROPPERS[view] for view in DIRECTIONS})

# LDA-IR and COTS only have frontal preprocessors
PREPROCESSORS['lda-ir-frontal'] = 'lda-ir'
PREPROCESSORS['cots-frontal'] = 'cots'


def command_line_arguments():
  parser = argparse.ArgumentParser(description="Execute baseline algorithms with default parameters", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-x', '--task', required=True, choices = ('preprocess', 'execute', 'evaluate'), help="The task you want to execute.")
  parser.add_argument('-a', '--algorithms', choices = ['Graphs', 'LGBPHS', 'ISV', 'LDA-IR', 'COTS'], default = ['Graphs', 'LGBPHS', 'ISV', 'LDA-IR'], nargs = '+', help = "Select one (or more) algorithms that you want to execute")
  parser.add_argument('--all', action='store_true', help = "If selected, all algorithms will be executed/evaluated, including COTS, which is by default left out")
  parser.add_argument('-d', '--database', choices=('multipie',), default = 'multipie-pose', help = "The database on which the algorithms are executed")
  parser.add_argument('-P', '--protocol', choices = ('P',), default = 'P', help = "Select the protocol that should be executed")
  parser.add_argument('-R', '--result-directory', default = 'FRICE/results/pose', help = 'Select the directory where to write the score files to')
  parser.add_argument('-T', '--temp-directory', default = 'FRICE/temp/pose', help = 'Select the directory where to write temporary files to')

  parser.add_argument('-q', '--dry-run', action = 'store_true', help = "Just print the commands, but do not execute them")
  parser.add_argument('-g', '--grid', action = 'store_true', help = "Execute the algorithms in the SGE grid")
  parser.add_argument('-p', '--parallel', type=int, help = 'Execute the algorithms in parallel on the local machine using the given number of parallel jobs')

  parser.add_argument('-w', '--plot', default='poses.pdf', help = "The file to contain the plot.")

  parser.add_argument('parameters', nargs = argparse.REMAINDER, help = "Parameters directly passed to the face verification script.")

  # add logger arguments (including the default --verbose option)
  bob.core.log.add_command_line_option(parser)
  args = parser.parse_args()
  bob.core.log.set_verbosity_level(logger, args.verbose)

  if args.all: args.algorithms = ['Graphs', 'LGBPHS', 'ISV', 'LDA-IR', 'COTS']

  return args


def cam_for_angle(angle):
  # get protocol
  protocol = ANGLES[angle]
  # translate into camera
  camera = protocol[1:3] + '_' + protocol[3]
  return camera


def main():
  args = command_line_arguments()

  executables = bob.extension.find_executable('verify.py', prefixes = [os.path.dirname(sys.argv[0]), 'bin'])
  assert executables, "Could not find the 'verify.py' executable (usually located in the 'bin' directory. Is there anything wrong with your installation?"
  executable = executables[0]

  # create base call
  base_call = ['--temp-directory', args.temp_directory, '--result-directory', args.result_directory, '--groups', 'dev', 'eval', '--imports', 'bob.db.multipie', 'bob.bio.face', '--gridtk-database-file', os.path.join(args.temp_directory, 'gridtk_db', 'submitted.sql3')]
  if args.verbose:
    base_call.append("-"+"v"*args.verbose)
  if args.parallel is not None:
    base_call.extend(['--parallel', str(args.parallel)])

  if args.task == 'preprocess':
    # get all the preprocessors
    calls = []
    # get all the preprocessors for the current view direction
    if 'LDA-IR' in args.algorithms:
      calls.append(base_call + ['--preprocessor', PREPROCESSORS['lda-ir-frontal'], '--database', DATABASES['frontal'], '--sub-directory', preprocessor('LDA-IR')] + ALGORITHM['LDA-IR'][2:])
    if 'COTS' in args.algorithms:
      calls.append(base_call + ['--preprocessor', PREPROCESSORS['cots-frontal'], '--database', DATABASES['frontal'], '--sub-directory', preprocessor('COTS')] + ALGORITHM['COTS'][2:])
    for direction in DIRECTIONS:
      if 'Graphs' in args.algorithms:
        calls.append(base_call + ['--preprocessor', PREPROCESSORS['%s-%s'%(preprocessor('Graphs'), direction)], '--database', DATABASES[direction], '--sub-directory', preprocessor('Graphs')] + ALGORITHM['Graphs'][2:])
      if 'LGBPHS' in args.algorithms or 'ISV' in args.algorithms:
        calls.append(base_call + ['--preprocessor', PREPROCESSORS['%s-%s'%(preprocessor('ISV'), direction)], '--database', DATABASES[direction], '--sub-directory', preprocessor('ISV')] + ALGORITHM['ISV'][2:])

    # execute all required preprocessors
    for call in calls:
      call += ['--execute-only', 'preprocessing', '--preferred-package', 'bob.chapter.FRICE']
      if args.grid:
        call.extend(grid(args.database))
      if args.parameters:
        call.extend(args.parameters[1:])

      print (bob.bio.base.tools.command_line([executable] + call))
      if not args.dry_run:
        # call the verify script with the collected parameters
        bob.bio.base.script.verify.main(call)

  elif args.task == 'execute':

    calls = []
    for algorithm in args.algorithms:
      # select the camera to be all for most algorithms, but only frontal for LDA-IR and COTS
      view = "frontal" if algorithm in ('LDA-IR', 'COTS') else "all"
      call = base_call + ALGORITHM[algorithm] + ['--database', DATABASES[view], '--sub-directory', algorithm, '--preprocessed-directory', os.path.join('..', preprocessor(algorithm), 'preprocessed'), '--skip-preprocessing', '--preferred-package', 'bob.chapter.FRICE']
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

    from .tools import EER_HTER, COLORS, MARKERS
    import numpy

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

    from bob.db.multipie import Database
    db = Database()

    # collect results
    result_files = {}
    for algorithm in args.algorithms:
      # TODO: check if these directories are correct
      files = [os.path.join(args.result_directory, algorithm, args.protocol, 'nonorm', 'scores-%s' %s) for s in ('dev', 'eval')]
      if os.path.exists(files[0]) and os.path.exists(files[1]):
        result_files[algorithm] = files
      else:
        logger.warn("Could not find result files %s and/or %s for algorithm %s", files[0], files[1], algorithm)

    # get the results for each of the protocols, when trained with the full data set
    # each probe file belongs to exactly one sub-protocol (which is defined by the camera)
    protocol_translation = {str(f.path) : str(p) for p in PROTOCOLS[1:] for f in db.probe_files(protocol=p, groups=('dev', 'eval'))}

    # collect results and add them to the corresponding memory files (a StringIO)
    results = {}
    from StringIO import StringIO
    for algorithm in args.algorithms:
      if algorithm in result_files:
        results[algorithm] = {}
        dev = {protocol : StringIO() for protocol in PROTOCOLS[1:]}
        eval = {protocol : StringIO() for protocol in PROTOCOLS[1:]}

        for group, result in zip((dev, eval), result_files[algorithm]):
          # open score file
          with open(result) as f:
            for line in f:
              # read line from score file
              splits = line.split()
              assert len(splits) == 4
              # get the protocol, to which the probe file belongs
              protocol = protocol_translation[splits[2]]
              if protocol in group:
                # copy line of score file into score file of the protocol
                group[protocol].write(line)

        # compute HTER for each individual camera angle (sub-protocol)
        for angle in sorted(ANGLES.keys()):
          protocol = ANGLES[angle]
          if dev[protocol].tell() and eval[protocol].tell():
            # rewind to the biginning of the memory-score-file
            dev[protocol].seek(0)
            eval[protocol].seek(0)

            # compute results
            res = [r * 100. for r in EER_HTER(dev[protocol], eval[protocol])]
            logger.info("Results for algorithm %s for angle %d is %3.2f%% EER, %3.2f%% HTER", algorithm, angle, res[0], res[1])
            results[algorithm][angle] = res

    # create plots split into the different pose angles
    x = sorted(ANGLES.keys())
    y1 = numpy.ndarray((len(x), len(args.algorithms)))
    y1[:] = numpy.nan
    y2 = numpy.ndarray((len(x), len(args.algorithms)))
    y2[:] = numpy.nan
    index = 1
    for p, angle in enumerate(sorted(ANGLES.keys())):
      for a, algorithm in enumerate(args.algorithms):
        if algorithm in results and angle in results[algorithm]:
          y1[p,a] = results[algorithm][angle][0]
          y2[p,a] = results[algorithm][angle][1]

    # plot the results
    pdf = PdfPages(args.plot)

    for y,t,s in ((y1, 'EER', 'development'), (y2, 'HTER', 'evaluation')):
      figure = plt.figure()
      for a, algorithm in enumerate(args.algorithms):
        plt.plot(x, y[:,a], '-'+MARKERS[algorithm], color = COLORS[algorithm], lw=2, ms=10, mew=2)

      plt.legend(args.algorithms, loc=9, ncol=2, prop={'size':16}, numpoints=1)
      plt.xticks(x, [r'%s$^\circ$'%a for a in x], va='baseline')
      plt.axis((min(x)-10, max(x)+10, 0, 75))

      plt.xlabel('Facial pose rotation angle in degree')
      plt.ylabel('%s on Multi-PIE %s set in \%%' % (t,s))

      pdf.savefig(figure)

    # close pdf
    pdf.close()

    logger.info("Wrote plot %s", args.plot)
