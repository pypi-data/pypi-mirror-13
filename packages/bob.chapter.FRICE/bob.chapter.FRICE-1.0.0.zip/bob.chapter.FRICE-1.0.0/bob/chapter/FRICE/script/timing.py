import argparse
import os, sys

from .tools import ALGORITHM, preprocessor, grid

import bob.extension
import bob.core
logger = bob.core.log.setup("bob.chapter.FRICE")

import bob.io.base
import bob.bio.base
import bob.bio.face
import bob.bio.gmm

import time

STEPS = ['extractor-training', 'extraction', 'projector-training', 'projection', 'enroller-training', 'enrollment', 'score-computation', 'concatenation']

PARTS = {
    'LDA-IR' : (1, 1, 0, 0, 0, 1, 1, 1),
    'Graphs' : (0, 1, 0, 0, 0, 1, 1, 1),
    'LGBPHS' : (0, 1, 0, 0, 0, 1, 1, 1),
    'ISV'    : (0, 1, 1, 1, 0, 1, 1, 1),
    'COTS'   : (0, 1, 0, 0, 0, 1, 1, 1)
}

from .tools import ALGORITHM, preprocessor



def command_line_arguments():
  parser = argparse.ArgumentParser(description="Execute baseline algorithms with default parameters", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-x', '--task', required=True, choices = ('preprocess', 'execute', 'evaluate'), help="The task you want to execute.")
  parser.add_argument('-a', '--algorithms', choices = ['Graphs', 'LGBPHS', 'ISV', 'LDA-IR', 'COTS'], default = ['Graphs', 'LGBPHS', 'ISV', 'LDA-IR'], nargs = '+', help = "Select one (or more) algorithms that you want to execute")
  parser.add_argument('--all', action='store_true', help = "If selected, all algorithms will be executed/evaluated, including COTS, which is by default left out")
  parser.add_argument('-d', '--database', default = 'banca', help = "The database on which the algorithms are executed")
  parser.add_argument('-P', '--protocol', default = 'P', help = "Select the protocol that should be executed")
  parser.add_argument('-R', '--result-directory', default = 'FRICE/results/timimg', help = 'Select the directory where to write the score files to')
  parser.add_argument('-T', '--temp-directory', default = 'FRICE/temp/timimg', help = 'Select the directory where to write temporary files to')

  parser.add_argument('-q', '--dry-run', action = 'store_true', help = "Just print the commands, but do not execute them")
  # we do not provide grid or parallel option here, as we want to measure the timing

  parser.add_argument('-w', '--result', default='timing.tex', help = "The file to contain the resulting latex file.")

  parser.add_argument('parameters', nargs = argparse.REMAINDER, help = "Parameters directly passed to the face verification script.")

  # add logger arguments (including the default --verbose option)
  bob.core.log.add_command_line_option(parser)
  args = parser.parse_args()
  bob.core.log.set_verbosity_level(logger, args.verbose)

  if args.all: args.algorithms = ['Graphs', 'LGBPHS', 'ISV', 'LDA-IR', 'COTS']

  return args


def result_file(args, algorithm):
  return os.path.join(args.result_directory, algorithm + ".txt")

def main():
  args = command_line_arguments()

  executables = bob.extension.find_executable('verify.py', prefixes = [os.path.dirname(sys.argv[0]), 'bin'])
  assert executables, "Could not find the 'verify.py' executable (usually located in the 'bin' directory. Is there anything wrong with your installation?"
  executable = executables[0]

  # create base call
  base_call = ['--temp-directory', args.temp_directory, '--result-directory', args.result_directory, '--database', args.database, '--protocol', args.protocol, '--groups', 'dev', 'eval']
  if args.verbose:
    base_call.append("-"+"v"*args.verbose)

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
      call += ['--execute-only', 'preprocessing']
      # generate parameters for preprocessors
      if args.parameters:
        call.extend(args.parameters[1:])

      print (bob.bio.base.tools.command_line([executable] + call))
      if not args.dry_run:
        # call the faceverify script with the collected parameters
        bob.bio.base.script.verify.main(call)

  elif args.task == 'execute':
    bob.io.base.create_directories_safe(args.result_directory)
    for algorithm in args.algorithms:
      with open(result_file(args, algorithm), 'w') as res:
        # iterate over all steps of the algorithms
        for step in range(len(STEPS)):
          if PARTS[algorithm][step]:
            # create call
            call = base_call + ALGORITHM[algorithm] + ['--sub-directory', algorithm, '--preprocessed-directory', os.path.join('..', preprocessor(algorithm), 'preprocessed'), '--force']
            if args.parameters:
              call.extend(args.parameters[1:])
            # add skips
            call += ['--execute-only', STEPS[step]]

            print (bob.bio.base.tools.command_line([executable] + call))
            # start timer; use the child process user time
            start_time = os.times()[0]
            if not args.dry_run:
              # call the faceverify script with the collected parameters
              bob.bio.base.script.verify.main(call)
            # end timer
            end_time = os.times()[0]

            logger.info("%s, step %d: elapsed time: %f seconds", algorithm, step, end_time - start_time)
            res.write("%s, step %d: elapsed time: %f seconds\n" % (algorithm, step, end_time - start_time))

  else: # evaluate

    def tt(s):
      # formats the given time in seconds into a string
      if s == 0.:
        return '---'
      if isinstance(s, str):
        return s
      if s < 0.1:
        return "%i ms" % (int(round(s*1000)))
      elif s < 60:
        return "%2.1f s" % s
      elif s < 3600:
        return "%2.1f m" % (s/60)
      else:
        return "%2.1f h" % (s/3600)

    # collect results
    files = [result_file(args, algorithm) for algorithm in args.algorithms]

    actions = ['Training', 'Extraction', 'Projection', 'Enrollment', 'Scoring']
    times = {algorithm : [0.] * len(actions) for algorithm in args.algorithms}
    indices = {0:0, 1:1, 2:0, 3:2, 4:0, 5:3, 6:4, 7:4}

    for a, algorithm in enumerate(args.algorithms):
      if os.path.exists(files[a]):
        with open(files[a]) as f:
          for line in f:
            splits = line.rstrip().split()
            time = float(splits[-2])
            index = int(splits[2][:1])
            times[algorithm][indices[index]] += time
            logger.info("Algorithm %s, step %d (%s): %s", algorithm, index, actions[indices[index]], tt(time))
      else:
        logger.warn("Could not find file %s", files[a])

    with open(args.result, 'w') as f:
      f.write("\\bf Algorithm & " + " & ".join(args.algorithms) + " \\\\\\hline\\hline\n")
      for a in range(len(actions)):
        f.write(actions[a] + ' & ')
        for i, algorithm in enumerate(args.algorithms):
          f.write(tt(times[algorithm][a]))
          f.write(' & ' if i < len(times)-1 else ' \\\\\\hline\\hline\n' if a == 0 or a == len(actions)-1 else ' \\\\\\hline\n')
      # write a 'total' line
      f.write('\\bf total & ')
      for i, algorithm in enumerate(args.algorithms):
        s = 0.
        for a in range(len(actions)):
          s += times[algorithm][a]
        f.write(tt(s) + (' & ' if i < len(args.algorithms)-1 else '\\\\\n'))
    logger.info("Wrote LaTeX file %s", args.result)
