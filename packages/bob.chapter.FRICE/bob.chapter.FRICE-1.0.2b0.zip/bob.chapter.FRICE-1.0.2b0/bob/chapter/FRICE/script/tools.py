import bob.measure
import os
import numpy

import logging
logger = logging.getLogger('bob.chapter.FRICE')


ALGORITHM = {
  'LDA-IR' : ['--preprocessor', 'lda-ir',     '--extractor', 'lda-ir', '--algorithm', 'lda-ir'],

  'Graphs' : ['--preprocessor', 'inorm-lbp',  '--extractor', 'graphs', '--algorithm', 'jets'],
  'LGBPHS' : ['--preprocessor', 'tan-triggs', '--extractor', 'lgbphs', '--algorithm', 'hist'],
  'ISV'    : ['--preprocessor', 'tan-triggs', '--extractor', 'dct',    '--algorithm', 'isv'],
  'COTS'   : ['--preprocessor', 'cots',       '--extractor', 'cots',   '--algorithm', 'cots'],
}

def preprocessor(algorithm):
  return ALGORITHM[algorithm][1]


def grid(database, algorithm = None):
  if algorithm == 'ISV':
    return ['--grid', 'isv']
  if 'video' in database:
    return ['--grid', 'video']
  if database in ('mobio','lfw','multipie','youtube'):
    return ['--grid', 'demanding']
  if algorithm in ('LGBPHS', 'Graphs'):
    return ['--grid', 'lgbphs']
  return ['--grid', 'grid']


def EER(score_file):
  """Computes the Equal Error Rate using the given score file"""
  # read score file
  neg, pos = bob.measure.load.split_four_column(score_file)
  # compute EER
  thres = bob.measure.eer_threshold(neg, pos)
  far, frr = bob.measure.farfrr(neg, pos, thres)

  return (far+frr) / 2.


def EER_HTER(score_file_dev, score_file_eval):
  """Computes the Equal Error Rate on the development set and the HTER on the evaluation set using the given score files"""
  # read score file
  neg, pos = bob.measure.load.split_four_column(score_file_dev)
  # compute EER on dev
  thres = bob.measure.eer_threshold(neg, pos)
  far, frr = bob.measure.farfrr(neg, pos, thres)
  eer = (far+frr) / 2.

  # read other score file
  neg, pos = bob.measure.load.split_four_column(score_file_eval)
  # compute EER on dev
  far, frr = bob.measure.farfrr(neg, pos, thres)
  hter = (far+frr) / 2.

  return (eer, hter)


def RR(score_file):
  """Computes the Recognition Rate using the given score file"""
  r = bob.measure.load.cmc_four_column(score_file)
  return bob.measure.recognition_rate(r)


def average(files):
  # computes the average EER of the given files
  accs = []
  for dev_file, eval_file in files:
    if not os.path.exists(dev_file) or not os.path.exists(eval_file):
      logger.warn("Could not find the score file '%s' and '%s' -- skipping" , dev_file, eval_file)
      continue

    # compute treshold on dev file
    neg, pos = bob.measure.load.split_four_column(dev_file)
    threshold = bob.measure.eer_threshold(neg, pos)

    # compute the Accuracy for eval files
    neg, pos = bob.measure.load.split_four_column(eval_file)
    far, frr = bob.measure.farfrr(neg, pos, threshold)
    eer = (far + frr) * 50. # / 2 * 100 %
    accs.append(100. - eer)
    logger.debug("  ... Accuracy for '%s' is %3.2f%%", eval_file, 100.-eer)

  if not accs:
    return None

  return numpy.mean(accs), numpy.std(accs)



COLORS = {
  'LDA-IR' : (0,0.4,0), # 'darkgreen',
  'Graphs' : (0,0.5,1), #'blue',
  'LGBPHS' : (.7,.7,0), #'darkyellow',
  'ISV' : (1,0,0), # 'red'
  # baselines are darkgray
  'baseline' : (0.5,0.5,0.5),
  'CohortLDA' : (0.5,0.5,0.5),
  'COTS' : (0.8,0.0,0.8), # dark purple
  'GPCA+LDA' : (0.5,0.5,0.5),
}


MARKERS = {
  'LRPCA' : '+',
  'LDA-IR' : 'v',
  'Graphs' : 'o',
  'LGBPHS' : 'h',
  'ISV' : 'd',
  'CohortLDA' : 's',
  'COTS' : 's',
  'baseline' : 's',
}

def colors(count):
  import matplotlib.pyplot
  import numpy
  cmap = matplotlib.pyplot.cm.get_cmap(name='hsv')
  return [cmap(i) for i in numpy.linspace(0, 1.0, count+1)]
