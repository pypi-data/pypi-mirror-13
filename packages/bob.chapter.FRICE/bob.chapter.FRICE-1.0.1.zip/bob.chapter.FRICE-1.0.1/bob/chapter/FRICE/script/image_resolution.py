import argparse
import os, sys

from .tools import grid

import bob.extension
import bob.core
logger = bob.core.log.setup("bob.chapter.FRICE")

import bob.bio.base
import bob.bio.face
import bob.bio.gmm

import pkg_resources


def command_line_arguments():
  parser = argparse.ArgumentParser(description='Executes and evaluates face recognition algorithms in different image resolutions', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-x', '--task', required=True, choices = ('preprocess', 'execute', 'evaluate'), help='The task you want to execute.')
  parser.add_argument('-a', '--algorithms', choices = ['Graphs', 'LGBPHS', 'ISV'], default = ['Graphs', 'LGBPHS', 'ISV'], nargs = '+', help = 'Select one (or more) algorithms that you want to execute')
  parser.add_argument('-d', '--database', choices = ('banca',), default = 'banca',  help = 'The database on which the algorithms are executed')
  parser.add_argument('-R', '--result-directory', default = 'FRICE/results/image_resolution', help = 'Select the directory where to write the score files to')
  parser.add_argument('-T', '--temp-directory', default = 'FRICE/temp/image_resolution', help = 'Select the directory where to write temporary files to')

  parser.add_argument('-q', '--dry-run', action = 'store_true', help = 'Just print the commands, but do not execute them')
  parser.add_argument('-g', '--grid', action = 'store_true', help = 'Execute the algorithms in the SGE grid')
  parser.add_argument('-p', '--parallel', type=int, help = 'Execute the algorithms in parallel on the local machine using the given number of parallel jobs')

  parser.add_argument('-w', '--plot', default='resolutions.pdf', help = 'The file to contain the plot.')

  parser.add_argument('parameters', nargs = argparse.REMAINDER, help = 'Parameters directly passed to the face verification script.')

  # add logger arguments (including the default --verbose option)
  bob.core.log.add_command_line_option(parser)
  args = parser.parse_args()
  bob.core.log.set_verbosity_level(logger, args.verbose)

  return args


# Different extractors with parameters that need to be adapted using the #F parater, which is defined in bob/chapter/FRICE/configuration/image_resolution.py
features_lgbphs = 'bob.bio.face.extractor.LGBPHS(block_size=int(round(#F*8)), block_overlap=0, lbp_radius=2, gabor_sigma=2.*math.pi, gabor_maximum_frequency=math.pi/2./#F, sparse_histogram=True)'
features_graphs = 'bob.bio.face.extractor.GridGraph(gabor_sigma=2.*math.pi, gabor_maximum_frequency=math.pi/2./#F, node_distance=int(round(#F*8)))'
features_dct = 'bob.bio.face.extractor.DCTBlocks(block_size=int(round(#F*8)), block_overlap=0, number_of_dct_coefficients=45, auto_reduce_coefficients=True)'

# Different face recognition algorithms
tool_gabor_jet = 'bob.bio.face.algorithm.GaborJet(gabor_jet_similarity_type="ScalarProduct")'
tool_lgbphs = 'bob.bio.face.algorithm.Histogram(distance_function=bob.math.chi_square, is_distance_function=True)'
tool_isv = 'bob.bio.gmm.algorithm.ISV(number_of_gaussians=512, subspace_dimension_of_u=80)'


ALGORITHM = {
  'Graphs' : ['--extractor', features_graphs, '--algorithm', tool_gabor_jet],
  'LGBPHS' : ['--extractor', features_lgbphs, '--algorithm', tool_lgbphs],
  'ISV'    : ['--extractor', features_dct, '--algorithm', tool_isv],
}

def main():
  args = command_line_arguments()

  config_file = pkg_resources.resource_filename('bob.chapter.FRICE.configurations', 'image_resolution.py')
  executables = bob.extension.find_executable('grid_search.py', prefixes = [os.path.dirname(sys.argv[0]), 'bin'])
  assert executables, "Could not find the 'grid_search.py' executable (usually located in the 'bin' directory. Is there anything wrong with your installation?"
  executable = executables[0]

  base_call = ['--configuration-file', config_file, '--database', args.database, '--temp-directory', args.temp_directory, '--result-directory', args.result_directory, '--gridtk-database-directory', os.path.join(args.temp_directory, 'gridtk_db')]
  if args.verbose:
    base_call.append('-'+'v'*args.verbose)
  if args.parallel is not None:
    base_call.extend(['--parallel', str(args.parallel)])

  if args.task == 'preprocess':
    # Here, we prepare the images for the image resolution test
    # Hence, we extract images in different resolutions
    call = base_call + ['--sub-directory', 'face-crop'] + ALGORITHM['ISV']

    if args.grid:
      call += grid(args.database)
    # execute the preprocessors
    if args.parameters:
      call += args.parameters[1:]
    call += ['--', '--execute-only', 'preprocessing', '--preferred-package', 'bob.chapter.FRICE']

    print (bob.bio.base.tools.command_line([executable] + call))
    if not args.dry_run:
      # call the faceverify script with the collected parameters
      bob.bio.base.script.grid_search.main(call)

  elif args.task == 'execute':
    base_call += ['--preprocessed-directory', '../face-crop']

    executions = []
    for algorithm in args.algorithms:
      call = base_call[:]
      if args.grid:
        call += grid(args.database, algorithm)
      executions.append(call + ['--sub-directory', algorithm] + ALGORITHM[algorithm])

    for call in executions:
      if args.parameters:
        call.extend(args.parameters[1:])
      call += ['--', '--preferred-package', 'bob.chapter.FRICE']

      print (bob.bio.base.tools.command_line([executable] + call))
      if not args.dry_run:
        # call the faceverify script with the collected parameters
        bob.bio.base.script.grid_search.main(call)

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

    plt.ioff()

    from .tools import EER, COLORS
    import numpy

    protocol = bob.bio.base.load_resource(args.database, "database").protocol

    # get the score directories only
    base_call = ['--configuration-file', config_file, '--database', args.database, '--dry-run']

    results = {}
    heights = set()
    for algorithm in args.algorithms:
      call = base_call + ALGORITHM[algorithm] + ['--sub-directory', algorithm]
      result_dirs = sorted(bob.bio.base.script.grid_search.main(call))

      eers = {}
      for d in result_dirs:
        result_file = os.path.join(args.result_directory, algorithm, protocol, d, 'nonorm', 'scores-dev')
        height = int(d.split("/")[0][1:])
        heights.add(height)
        if os.path.exists(result_file):
          eer = EER(result_file)
          logger.info("Result for algorithm %s in resolution %03d is %f", algorithm, height, eer)
          eers[height] = eer
        else:
          logger.warn("Could not find result file %s for algorithm %s in resolution %03d", result_file, algorithm, height)

      results[algorithm] = eers

    if not results:
      return

    # plot the results
    pdf = PdfPages(args.plot)
    figure = plt.figure()

    # create plots split into the different expressions
    heights = sorted(heights)
    x = range((len(args.algorithms) * 2 + 2) * (len(heights)+1))
    y = [numpy.nan] * len(x)
    c = [(0,0,0,0)] * len(x)
    index = 1
    for height in heights:
      for algorithm in args.algorithms:
        if algorithm in results and height in results[algorithm]:
          y[index] = results[algorithm][height]
          c[index] = COLORS[algorithm]
        index += 1
      index += 2

    figure = plt.figure()
    plt.bar(x, y, color=c, align='center' )
    plt.axis((0, index-2, 0, numpy.nanmax(y) * 1.35))
    ticks = [(len(args.algorithms))/2. + .5 + i * (len(args.algorithms) +2) for i in range(len(heights))]
    plt.xticks(ticks, [str(h) for h in heights])


    # dirty HACK to generate legends
    l = [plt.bar([j],[0],color=COLORS[a]) for j, a in enumerate(args.algorithms)]
    plt.legend(l, args.algorithms, loc=9, ncol=3, prop={'size':16})
    plt.xlabel('Image height in pixels')
    plt.ylabel('EER on BANCA development set in \%')

    # close figure
    pdf.savefig(figure)
    pdf.close()

    logger.info("Wrote plot %s", args.plot)
