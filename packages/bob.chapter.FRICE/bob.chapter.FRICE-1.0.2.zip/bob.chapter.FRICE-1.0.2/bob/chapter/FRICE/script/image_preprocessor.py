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
  parser = argparse.ArgumentParser(description="Execute and evaluates how different face recognition algorithms work with different image preprocessors", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-x', '--task', required=True, choices = ('preprocess', 'execute', 'evaluate'), help='The task you want to execute.')
  parser.add_argument('-a', '--algorithms', choices = ['Graphs', 'LGBPHS', 'ISV'], default = ['Graphs', 'LGBPHS', 'ISV'], nargs = '+', help = 'Select one (or more) algorithms that you want to execute')
  parser.add_argument('-d', '--databases', choices = ['banca', 'arface-ill', 'multipie', 'xm2vts'], default = ['banca', 'arface-ill', 'multipie', 'xm2vts'], nargs = '+', help = "The databases on which the algorithms are executed")
  parser.add_argument('-R', '--result-directory', default = 'FRICE/results/image_preprocessor', help = 'Select the directory where to write the score files to')
  parser.add_argument('-T', '--temp-directory', default = 'FRICE/temp/image_preprocessor', help = 'Select the directory where to write temporary files to')

  parser.add_argument('-q', '--dry-run', action = 'store_true', help = "Just print the commands, but do not execute them")
  parser.add_argument('-g', '--grid', action = 'store_true', help = "Execute the algorithms in the SGE grid")
  parser.add_argument('-p', '--parallel', type=int, help = 'Execute the algorithms in parallel on the local machine using the given number of parallel jobs')

  parser.add_argument('-w', '--plot', default='preprocessor.pdf', help = "The file to contain the plot.")

  parser.add_argument('parameters', nargs = argparse.REMAINDER, help = "Parameters directly passed to the face verification script.")

  # add logger arguments (including the default --verbose option)
  bob.core.log.add_command_line_option(parser)
  args = parser.parse_args()
  bob.core.log.set_verbosity_level(logger, args.verbose)

  return args


# Different feature extractors
features_lgbphs = 'bob.bio.face.extractor.LGBPHS(block_size=8, block_overlap=0, lbp_radius=2, gabor_sigma=2.*math.pi, gabor_maximum_frequency=math.pi/2., sparse_histogram=True)'
features_graphs = 'bob.bio.face.extractor.GridGraph(gabor_sigma=2.*math.pi, gabor_maximum_frequency=math.pi/2., node_distance=8)'
features_dct = 'bob.bio.face.extractor.DCTBlocks(block_size=8, block_overlap=0, number_of_dct_coefficients=45, auto_reduce_coefficients=True)'

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

  config_file = pkg_resources.resource_filename('bob.chapter.FRICE.configurations', 'image_preprocessor.py')
  executables = bob.extension.find_executable('grid_search.py', prefixes = [os.path.dirname(sys.argv[0]), 'bin'])
  assert executables, "Could not find the 'grid_search.py' executable (usually located in the 'bin' directory. Is there anything wrong with your installation?"
  executable = executables[0]

  base_call = ['--configuration-file', config_file, '--temp-directory', args.temp_directory, '--result-directory', args.result_directory, '--gridtk-database-directory', os.path.join(args.temp_directory, 'gridtk_db')]
  if args.verbose:
    base_call.append('-'+'v'*args.verbose)
  if args.parallel is not None:
    base_call.extend(['--parallel', str(args.parallel)])

  if args.task == 'preprocess':
    preprocessings = []
    for database in args.databases:
      call = base_call + ['--database', database, '--sub-directory', os.path.join(database)] + ALGORITHM['ISV']

      if args.grid:
        call += grid(database)
      if args.parameters:
        call += args.parameters[1:]
      call += ['--', '--execute-only', 'preprocessing', '--preferred-package', 'bob.chapter.FRICE']

      if database == 'xm2vts':
        # for XM2VTS, we need the evaluation set, which uses darkened images
        call += ['--groups', 'eval']

      print (bob.bio.base.tools.command_line([executable] + call))
      if not args.dry_run:
        # call the faceverify script with the collected parameters
        bob.bio.base.script.grid_search.main(call)

  elif args.task == 'execute':
    executions = []
    for database in args.databases:
      for algorithm in args.algorithms:
        call = base_call + ['--database', database, '--sub-directory', os.path.join(database, algorithm), '--preprocessed-directory', '..' ] + ALGORITHM[algorithm]
        if args.grid:
          call += grid(database, algorithm)
        executions.append(call[:])

    for call in executions:
      if args.parameters:
        call += args.parameters[1:]
      if database == 'xm2vts':
        # for XM2VTS, we need the evaluation set, which uses darkened images
        call += ['--groups', 'eval']
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

    from .tools import EER, colors
    import numpy

    protocols = {database: bob.bio.base.load_resource(database, "database", preferred_package='bob.chapter.FRICE').protocol for database in args.databases}

    # get the score directories only
    base_call = ['--configuration-file', config_file, '--dry-run']

    results = {}
    prepros = set()
    for algorithm in args.algorithms:
      db_eers = {}
      for database in args.databases:
        call = base_call + ['--database', database, '--sub-directory', os.path.join(database, algorithm)] + ALGORITHM[algorithm] + ['--', '--preferred-package', 'bob.chapter.FRICE']
        result_dirs = sorted(bob.bio.base.script.grid_search.main(call))

        eers = {}
        for d in result_dirs:
          result_file = os.path.join(args.result_directory, database, algorithm, protocols[database], d, 'nonorm', 'scores-eval' if database == 'xm2vts' else 'scores-dev')
          prepro = d.split("/")[0]
          prepros.add(prepro)
          if os.path.exists(result_file):
            eer = EER(result_file)
            logger.info("Result for algorithm %s on database %s with preprocessor %s is %f", algorithm, database, prepro, eer)
            eers[prepro] = eer
          else:
            logger.warn("Could not find result file %s for algorithm %s on database %s with preprocessor %s", result_file, algorithm, database, prepro)
        db_eers[database] = eers
      results[algorithm] = db_eers

    if not results:
      return

    # create result matrix
    prepros = sorted(prepros)
    result_matrix = numpy.ones((len(args.databases), len(args.algorithms), len(prepros)), dtype = numpy.float) * 100
    result_matrix[:] = numpy.nan
    averages = numpy.zeros((len(prepros)), dtype = numpy.float)
    counts = numpy.zeros((len(prepros)), dtype = numpy.int32)

    # iterate the preprocessors
    counter = {p : 0 for p in prepro}
    for a, algorithm in enumerate(args.algorithms):
      if algorithm in results:
        for d, database in enumerate(args.databases):
          if database in results[algorithm]:
            for p, prepro in enumerate(prepros):
              if prepro in results[algorithm][database]:
                eer = results[algorithm][database][prepro] * 100.
                averages[p] += eer
                counts[p] += 1
                result_matrix[d, a, p] = eer

    # plot the results
    pdf = PdfPages(args.plot)
    figure = plt.figure()

    # plot the average result
    colors = colors(len(prepros))
    preprocessor_names = {'None' : 'None', 'TT' : 'T\&T', 'HEQ' : 'HEQ', 'SQI' : 'SQI', 'LBP' : 'LBP'}
    database_names = {'arface-ill' : 'ARface', 'multipie' : 'Multi-PIE', 'xm2vts' : 'XM2VTS', 'banca' : 'BANCA'}

    x = range(len(prepros) * 2)
    y = [0] * len(x)
    c = [(0,0,0,0)] * len(x)
    for p, prep in enumerate(prepros):
      y[p*2] = averages[p] / counts[p]
      c[p*2] = colors[p]

    plt.bar(x,y, color=c, align='center')
    plt.suptitle("Average")

    # dirty HACK to generate legends
    l = [plt.bar([i],[0],color=colors[i]) for i in range(len(prepros))]
    plt.legend(l, [preprocessor_names[p] for p in prepros], ncol=3, loc=9)
    plt.axis((-1, len(x)-1, 0, max(y) * 1.4))
    plt.xticks([])
    plt.ylabel('EER in \%')

    pdf.savefig(figure)

    # plot specific results per algorithm
    for a, algorithm in enumerate(args.algorithms):
      figure = plt.figure()

      x = range((len(prepros) * 2 + 2) * (len(args.databases)+1))
      y = [0] * len(x)
      c = [(0,0,0,0)] * len(x)

      # collect data
      index = 1
      for d, database in enumerate(args.databases):
        for p, preprocessor in enumerate(prepros):
          y[index] = result_matrix[d, a, p]
          c[index] = colors[p]
          index += 1
        index += 2

      plt.bar(x,y, color=c, align='center')
      plt.suptitle(algorithm)

      # dirty HACK to generate legends
      l = [plt.bar([i],[0],color=colors[i]) for i in range(len(prepros))]
      plt.legend(l, [preprocessor_names[p] for p in prepros], ncol=3, loc=9, prop={'size':16})

      plt.axis((0, index-2, 0, max(y) * 1.4))

      ticks = [(len(prepros))/2. + .5 + i * (len(prepros) +2) for i in range(len(args.databases))]
      plt.xticks(ticks, [database_names[d] for d in args.databases])
      plt.ylabel('EER in \%')

      pdf.savefig(figure)

    # close figure
    pdf.close()

    logger.info("Wrote plot %s", args.plot)
