from __future__ import print_function

import argparse
import os, sys, numpy

from .tools import grid, EER, EER_HTER, COLORS, colors

import bob.extension
import bob.core
logger = bob.core.log.setup("bob.chapter.FRICE")

import bob.bio.base

import pkg_resources



def command_line_arguments():
  parser = argparse.ArgumentParser(description="Runs a configuration optimization step for the given algorithms", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-x', '--task', required=True, choices = ('preprocess', 'execute', 'evaluate'), help="The task you want to execute.")
  parser.add_argument('-a', '--algorithms', choices = ['Graphs', 'LGBPHS', 'ISV'], default = ['Graphs', 'LGBPHS', 'ISV'], nargs = '+', help = "Select one (or more) algorithms that you want to execute")
  parser.add_argument('--all', action='store_true', help = "If selected, all algorithms will be evaluated using the results stored in the --timimg-directory")
  parser.add_argument('-d', '--database', choices = ('banca',), default = 'banca', help = "The database on which the algorithms are executed")
  parser.add_argument('-t', '--optimization-step', type=int, default = 1, choices=(1,2,3), help = "The step of the optimization you want to perform")
  parser.add_argument('-R', '--result-directory', default = 'FRICE/results/configuration_optimization', help = 'Select the directory where to write the score files to')
  parser.add_argument('-T', '--temp-directory', default = 'FRICE/temp/configuration_optimization', help = 'Select the directory where to write temporary files to')
  parser.add_argument('-e', '--timing-directory', default = 'FRICE/results/timing', help = 'Select the directory where the results of the timing experiments are stored (used in evaluation only)')

  parser.add_argument('-q', '--dry-run', action = 'store_true', help = "Just print the commands, but do not execute them")
  parser.add_argument('-g', '--grid', action = 'store_true', help = "Execute the algorithms in the SGE grid")
  parser.add_argument('-p', '--parallel', type=int, help = 'Execute the algorithms in parallel on the local machine using the given number of parallel jobs')

  parser.add_argument('-w', '--plot', default='configuration_optimization.pdf', help = "The file to contain the plot.")

  parser.add_argument('parameters', nargs = argparse.REMAINDER, help = "Parameters directly passed to the face verification script.")

  # add logger arguments (including the default --verbose option)
  bob.core.log.add_command_line_option(parser)
  args = parser.parse_args()
  bob.core.log.set_verbosity_level(logger, args.verbose)

  # remove the Graphs algorithm for step 3
  if args.task == 'execute' and args.optimization_step == 3 and 'Graphs' in args.algorithms:
    args.algorithms = [a for a in args.algorithms if a != 'Graphs']

  if args.task == 'evaluate' and args.all: args.algorithms = ['Graphs', 'LGBPHS', 'ISV', 'LDA-IR', 'COTS']

  return args



### Helper function to do the plotting

def _replace(algorithm, keyword):
  """Replaces the given keyword (which is a sub-directory name for a specific algorithm) to a string that can be used inside the plots."""
  if algorithm == 'Graphs':
    if keyword[0] == 'K': return {'1': r'$\pi/2$', '2': r'$\pi/\sqrt2$', '3': r'$\pi$'}[keyword[1]]
    if keyword[0] == 'S': return {'1': r'$2\pi$', '2': r'$\sqrt2\pi$', '3': r'$\pi$'}[keyword[1]]
    if keyword[0] == '0': return int(keyword)
    words = {'Can': r'$S_C$', 'Cos': r'$S_a$', 'Disp': r'$S_D$', 'PhDiff': r'$S_n$', 'PhDiffCan': r'$S_{n+C}$',
             '1_average': '1', '3c_minimum': '3c', '3b_median': '3b', '3a_maximum': '3a', '2c_worst': '2c', '2b_mean': '2b', '2a_best': '2a'}
    if keyword in words: return words[keyword]

  if algorithm == 'LGBPHS':
    words = {'Phase': 'with phases', 'NoPhase': 'w/o phases', 'Uniform': 'uniform', 'Non_Uni':'non-uniform', 'Chi2': r'$d_{\chi^2}$', 'Hist': r'$d_{\mathrm{HI}}$', 'KbLl':r'$d_{\mathrm{KL}}$'}
    if keyword in words: return words[keyword]
    if keyword[0] in ('B', 'O', 'N'): return int(keyword[1:])
    if keyword[0] == 'K': return {'1': r'$\pi/2$', '2': r'$\pi/\sqrt2$', '3': r'$\pi$'}[keyword[1]]
    if keyword[0] == 'S': return {'1': r'$2\pi$', '2': r'$\sqrt2\pi$', '3': r'$\pi$'}[keyword[1]]

  if algorithm == 'ISV':
    if keyword[0] in ('B', 'O', 'C', 'G', 'U'): return int(keyword[2:])

  return keyword


def _result_files(algorithm, step, database, protocol, result_directory):
  """Collects a list of result files for the given step of the given algorithm. No check is performed, whether the files exist"""
  # get the score directories by calling off to the grid_search script, using the --dry-run option)
  call = ['--database', database, '--dry-run', '--configuration-file', pkg_resources.resource_filename('bob.chapter.FRICE.configurations', '%s.py'%algorithm), '--replace-variable', 'replace_%d'%step, '--sub-directory', '%s-%d' % (algorithm, step)]
  result_directories = sorted(bob.bio.base.script.grid_search.main(call))
  # collect score files in the sub-directories
  return [os.path.join(result_directory, '%s-%d' %(algorithm, step), protocol, d, 'nonorm', 'scores-dev') for d in result_directories], result_directories


def _plot_1(algorithm, step, protocol, args, max_multiplier, xlabel=None):
  """Generates a 1D plot (i. e., a plot where only a single variable was changed)."""
  # collect result files
  result_files, result_directories = _result_files(algorithm, step, args.database, protocol, args.result_directory)

  # load data
  best_result = (100, None)
  results = numpy.ndarray((len(result_files),), dtype = numpy.float)
  # pre-set everything with NAN, so that missing results are not plotted
  results[:] = numpy.nan
  # get the sub-directories, each of which stores the result file of one tested value
  keywords = [k.split('/')[0] for k in sorted(result_directories)]
  for i, key in enumerate(keywords):
    if not os.path.exists(result_files[i]):
      logger.info("step %d of %s with key %s skipped: cannot find %s", step, algorithm, key, result_files[i])
      continue
    # load the file and compute the equal error rate
    results[i] = EER(result_files[i]) * 100.
    logger.info("step %d of %s with key %s got %f %% EER", step, algorithm, key, results[i])
    if results[i] < best_result[0]:
      # remember the best result
      best_result = (results[i], key)

  # plot the results
  import matplotlib.pyplot as plt
  x = range(1,len(result_files)+1)
  plt.bar(x, results, color = COLORS[algorithm], align='center')
  plt.xticks(x, [_replace(algorithm, k) for k in keywords], va='baseline')
  plt.axis((0, len(x)+1, numpy.nanmin(results) * 0.7, numpy.nanmax(results) * max_multiplier))
  plt.ylabel('EER on BANCA development set in \%')
  if xlabel is not None:
    plt.xlabel(xlabel)
  plt.suptitle(algorithm)

  print ("best result for step", step, "of algorithm", algorithm, "is", best_result)
  return best_result[0]



def _plot_2(algorithm, step, protocol, args, max_multiplier, xlabel=None, legend_title=None, legend_len=3, indices=(0,1)):
  """Generates a 2D plot (i.e., a plot where two variables were changed at the same time)."""
  # collect result files
  result_files, result_directories = _result_files(algorithm, step, args.database, protocol, args.result_directory)

  # load data
  best_result = (100, None, None)
  # collect the unique variable names in the second layer (in order to get enough space in the plot)
  dim2 = set()
  results = {}
  min_result = 100
  max_result = 0
  for i in range(len(result_files)):
    # split up the result directories into the tested variables
    splits = result_directories[i].split('/')
    d1 = splits[indices[0]]
    d2 = splits[indices[1]]
    if not os.path.exists(result_files[i]):
      logger.info("step %d of %s with keys %s, %s skipped: cannot find %s", step, algorithm, d1, d2, result_files[i])
      continue

    dim2.add(d2)
    if d1 not in results:
      results[d1] = {}

    # load the file and compute the equal error rate
    eer = EER(result_files[i]) * 100.
    results[d1][d2] = eer
    if eer < best_result[0]:
      best_result = (eer, d1, d2)
    # remember minimal and maximal reults to define a proper result range in the plot
    min_result = min(min_result, eer)
    max_result = max(max_result, eer)
    logger.info("step %d of %s with keys %s, %s got %f %% EER", step, algorithm, d1, d2, eer)
  dim2 = sorted(list(dim2))

  # collect data in desired format
  x = range(sum(len(results[k])+2 for k in results)-1)
  x_centers = []
  # pre-set everything with NAN, so that missing results are not plotted
  y = [numpy.nan] * len(x)
  c = [(0,0,0)] * len(x)
  cols = colors(len(dim2))

  # iterate over the data and add gaps between two different tested parameters
  index = 1
  for d1 in sorted(results.keys()):
    x_centers.append(index + len(results[d1])/2. - .5)
    for i, d2 in enumerate(dim2):
      if d2 in results[d1]:
        y[index] = results[d1][d2]
        c[index] = cols[i]
        index += 1
    index += 2

  # create bar plot
  import matplotlib.pyplot as plt
  plt.bar(x, y, color=c, align='center')

  # dirty HACK to generate legends
  l = [plt.bar([j],[0],color=cols[j]) for j in range(len(dim2))]
  plt.legend(l, [_replace(algorithm, k) for k in dim2], ncol = legend_len, title=legend_title, loc=9, prop={'size':16})
  plt.xticks(x_centers, [_replace(algorithm, k) for k in sorted(results.keys())], va='baseline')
  plt.axis((0, len(x), min_result * 0.7, max_result * max_multiplier))
  plt.ylabel('EER on BANCA development set in \%')
  if xlabel is not None:
    plt.xlabel(xlabel)
  plt.suptitle(algorithm)

  print ("best result for step", step, "of algorithm", algorithm, "is", best_result)
  return best_result[0]



def _plot_3(algorithm, step, protocol, args, max_multiplier, xlabel=None, legend_title=None, footer=None, indices=(0,1,2)):
  """Generates a set of 2D plots for where three variables were changed at the same time."""
  # collect result files
  result_files, result_directories = _result_files(algorithm, step, args.database, protocol, args.result_directory)

  # load data
  best_result = (100, None, None, None)
  # collect the unique variable names in the second and third layer (in order to get enough space in the plot)
  dim2 = set()
  dim3 = set()
  results = {}
  min_result = 100
  max_result = 0
  for i in range(len(result_files)):
    # split up the result directories into the tested variables
    splits = result_directories[i].split('/')
    d1 = splits[indices[0]]
    d2 = splits[indices[1]]
    d3 = splits[indices[2]]
    if not os.path.exists(result_files[i]):
      logger.info("step %d of %s with keys %s, %s, %s skipped: cannot find %s", step, algorithm, d1, d2, d3, result_files[i])
      continue

    dim2.add(d2)
    dim3.add(d3)
    if d1 not in results:
      results[d1] = {}
    if d2 not in results[d1]:
      results[d1][d2] = {}

    # load the file and compute the equal error rate
    eer = EER(result_files[i]) * 100.
    results[d1][d2][d3] = eer
    if eer < best_result[0]:
      best_result = (eer, d1, d2, d3)
    min_result = min(min_result, eer)
    max_result = max(max_result, eer)
    logger.info("step %d of %s with keys %s, %s, %s got %f %% EER", step, algorithm, d1, d2, d3, eer)
  dim2 = sorted(list(dim2))
  dim3 = sorted(list(dim3))

  if not results:
    return (100, None)

  import matplotlib.pyplot as plt

  for i, d1 in enumerate(sorted(results.keys())):
    plt.subplot(1, len(results), i+1)

    x = range(sum(len(results[d1][k])+2 for k in results[d1])-1)
    x_centers = []
    y = [numpy.nan] * len(x)
    c = [(0,0,0)] * len(x)
    cols = colors(len(dim3))

    index = 1
    for d2 in dim2:
      if d2 in results[d1]:
        x_centers.append(index + len(results[d1][d2])/2. - .5)
        for i, d3 in enumerate(dim3):
          if d3 in results[d1][d2]:
            y[index] = results[d1][d2][d3]
            c[index] = cols[i]
            index += 1
        index += 2

    # create bar plot
    plt.bar(x, y, color=c, align='center')

    # add ticks
    plt.xticks(x_centers, [_replace(algorithm, k) for k in sorted(results[d1].keys())], va='baseline')
    plt.axis((0, len(x), min_result * 0.7, max_result * max_multiplier))
    if xlabel:
      plt.xlabel(xlabel)
    if footer:
      plt.title(footer%(_replace(algorithm, d1)))

  # y-set axis plot
  for i in range(len(results)-1):
    plt.subplot(1, len(results), i+2)
    plt.setp(plt.gca().get_yticklabels(), visible=False)

  # dirty HACK to generate legends
  l = [plt.bar([j],[0],color=cols[j]) for j in range(len(dim3))]
  legend_handle = plt.figlegend(l, [_replace(algorithm, k) for k in dim3], ncol = len(dim3), title=legend_title, loc=9, prop={'size':16}, bbox_to_anchor=(0.5, 1.18))

  # choose first subplot to put the y-label on
  plt.subplot(1, len(results), 1)
  plt.ylabel('EER on BANCA development set in \%')
  plt.suptitle(algorithm)

  print ("best result for step", step, "of algorithm", algorithm, "is", best_result)
  return (best_result[0], legend_handle)




def main():
  args = command_line_arguments()

  executables = bob.extension.find_executable('grid_search.py', prefixes = [os.path.dirname(sys.argv[0]), 'bin'])
  assert executables, "Could not find the 'grid_search.py' executable (usually located in the 'bin' directory. Is there anything wrong with your installation?"
  executable = executables[0]

  base_call = ['--temp-directory', args.temp_directory, '--result-directory', args.result_directory, '--gridtk-database-directory', os.path.join(args.temp_directory, 'gridtk_db'), '--database', args.database]
  if args.verbose:
    base_call += ['-'+'v'*args.verbose]
  if args.parallel is not None:
    base_call.extend(['--parallel', str(args.parallel)])

  if args.task == 'preprocess':

    # We have two types of preprocessings, which are LBP and TanTriggs
    preprocessings = []
    if 'Graphs' in args.algorithms:
      preprocessings.append(base_call + ['--configuration-file', pkg_resources.resource_filename('bob.chapter.FRICE.configurations', 'Graphs.py'), '--sub-directory', 'inorm_lbp'])
    if 'LGBPHS' in args.algorithms or 'ISV' in args.algorithms:
      preprocessings.append(base_call + ['--configuration-file', pkg_resources.resource_filename('bob.chapter.FRICE.configurations', 'ISV.py'), '--sub-directory', 'tan_triggs'])

    # execute all required preprocessors
    for call in preprocessings:
      # generate parameters for preprocessors
      if args.grid:
        call.extend(grid(args.database))
      if args.parameters:
        call.extend(args.parameters[1:])
      call += ['--replace-variable', 'replace_0', '--', '--execute-only', 'preprocessing', '--preferred-package', 'bob.chapter.FRICE']

      print (bob.bio.base.tools.command_line([executable] + call))
      if not args.dry_run:
        # call the grid_search script with the collected parameters
        bob.bio.base.script.grid_search.main(call)

  elif args.task == 'execute':
    executions = []
    for algorithm in args.algorithms:
      preprocessed_directory = os.path.join('..', {'Graphs': 'inorm_lbp', 'LGBPHS': 'tan_triggs', 'ISV': 'tan_triggs'}[algorithm])
      executions.append(base_call + ['--preprocessed-directory', preprocessed_directory, '--configuration-file', pkg_resources.resource_filename('bob.chapter.FRICE.configurations', '%s.py' % algorithm), '--sub-directory', '%s-%d' % (algorithm, args.optimization_step), '--gridtk-database-directory', os.path.join(args.temp_directory, 'gridtk_db', '%s-%d' % (algorithm, args.optimization_step))])

    for call in executions:
      call += ['--replace-variable', 'replace_%d' % args.optimization_step]
      if args.grid:
        call.extend(grid(args.database, algorithm))
      if args.parameters:
        call += args.parameters[1:]
      call += ['--', '--preferred-package', 'bob.chapter.FRICE']

      print (bob.bio.base.tools.command_line([executable] + call))
      if not args.dry_run:
        # call the grid_search script with the collected parameters
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
    matplotlib.rcParams['xtick.major.pad'] = 16

    plt.ioff()

    import numpy

    # plot the results
    pdf = PdfPages(args.plot)
    overall_best_results = {}

    protocol = bob.bio.base.load_resource(args.database, "database", preferred_package='bob.chapter.FRICE').protocol

    if 'Graphs' in args.algorithms:
      f = plt.figure(figsize=(9,6))
      _, legend_handle = _plot_3('Graphs', 1, protocol, args, 1.1, xlabel=r'$k_{\mathrm{max}}$', legend_title="Similarity function", footer=r'$\sigma = $ %s', indices=(0,1,2))
      if legend_handle:
        pdf.savefig(f,bbox_inches='tight',pad_inches=0.25, bbox_extra_artists=[legend_handle])

      # create a 2D plot
      f = plt.figure()
      overall_best_results['Graphs'] = _plot_2('Graphs', 2, protocol, args, 1.2, xlabel="Distance of grid nodes", indices=(0,1), legend_title="Fusion strategy", legend_len=4)
      pdf.savefig(f)

    if 'LGBPHS' in args.algorithms:
      # 2D plot
      f = plt.figure()
      _plot_2('LGBPHS', 1, protocol, args, 1.1, xlabel="Block size", legend_title="Block overlap", legend_len=5)
      pdf.savefig(f)

      # create a 3D plot
      f = plt.figure(figsize=(9,6))
      _, legend_handle = _plot_3('LGBPHS', 2, protocol, args, 1.1, xlabel=r'$k_{\mathrm{max}}$', legend_title="Add Gabor phases?", footer=r'$\sigma = $ %s', indices=(0,1,2))
      if legend_handle:
        pdf.savefig(f,bbox_inches='tight',pad_inches=0.25, bbox_extra_artists=[legend_handle])

      # create another 3D plot
      f = plt.figure(figsize=(9,6))
      overall_best_results['LGBPHS'], legend_handle = _plot_3('LGBPHS', 3, protocol, args, 1.1, xlabel='LBP type', legend_title="Similarity type", footer=r'LBP size = %s', indices=(0,1,3))
      if legend_handle:
        pdf.savefig(f,bbox_inches='tight',pad_inches=0.25, bbox_extra_artists=[legend_handle])

    if 'ISV' in args.algorithms:
      # 2D plot
      f = plt.figure()
      _plot_2('ISV', 1, protocol,args, 1.25, xlabel="Block size", legend_title="Block overlap", legend_len=4)
      pdf.savefig(f)

      # create a 1D plot
      f = plt.figure()
      _plot_1('ISV', 2, protocol, args, 1.1, xlabel='Number of DCT components')
      pdf.savefig(f)

      # create another 2D plot
      f = plt.figure(figsize=(9,6))
      overall_best_results['ISV'] = _plot_2('ISV', 3, protocol, args, 1.25, xlabel='Number of Gaussians', legend_title="U subspace dimension", legend_len=5, indices=(1,2))
      pdf.savefig(f)


    # print out the best results that we have found for each algorithm
    for algorithm in args.algorithms:
      if algorithm in overall_best_results:
        print ("Best result for algorithm '%s' on BANCA development set was found to be '%2.3f %% EER" % (algorithm, overall_best_results[algorithm]))

    # plot best results from algorithms (as created in the timing tests)
    if os.path.exists(args.timing_directory):
      logger.info("Evaluating the 'timing' results")

      # collect score files
      score_files = {algorithm : [os.path.join(args.timing_directory, algorithm, 'P', 'nonorm', 'scores-%s'%g) for g in ('dev', 'eval')] for algorithm in args.algorithms}
      x = [1.5 + 3*x for x in range(len(args.algorithms))]
      y = [numpy.nan] * (3*len(args.algorithms) + 1)
      c = ['k'] * (3*len(args.algorithms))

      for a, algorithm in enumerate(args.algorithms):
        if os.path.exists(score_files[algorithm][0]) and os.path.exists(score_files[algorithm][1]):
          eer, hter = [r * 100. for r in EER_HTER(score_files[algorithm][0], score_files[algorithm][1])]
          y[3*a+1] = eer
          y[3*a+2] = hter

          c[3*a+1] = c[3*a+2] = COLORS[algorithm]
          logger.info("Results for algorithm %s is %3.2f%% EER and %3.2f%% HTER", algorithm, eer, hter)
        else:
          logger.warn("Could not find result files %s and/or %s for algorithm %s", score_files[algorithm][0], score_files[algorithm][1], algorithm)

      f = plt.figure()
      plt.bar(range(len(y)), y, color=c, align='center')

      t = [r'%2.1f\%%' % y[3*a+2] for a in range(len(args.algorithms))]
      plt.xticks(x, [r'%2.1f\%%' % y[3*a+2] for a in range(len(args.algorithms))], va='baseline')
      l = [plt.bar([a],[0],color=COLORS[alg]) for a,alg in enumerate(args.algorithms)]
      plt.legend(l, args.algorithms, ncol = 3, loc=9, prop={'size':16})
      plt.axis((0, max(x)+1.5, 0, numpy.nanmax(y) * 1.35))

      plt.ylabel('EER / HTER on BANCA in \%')
      plt.xlabel("Best HTER results of optimized configurations")

      pdf.savefig(f)

    # close figure
    pdf.close()

    logger.info("Wrote plot %s", args.plot)
