#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <siebenkopf@googlemail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


### we here set up the best configurations that we have found during our previous experiments

import bob.bio.face
import bob.bio.gmm
import bob.bio.csu

import facerec2010
import pyvision
import math
import numpy
import scipy.spatial
import bob.math
import copy



##############################################################################
#######################  Preprocessors  ######################################
face_cropper = bob.bio.face.preprocessor.FaceCrop(
    # face cropping parameters
    cropped_image_size = (80, 64),
    cropped_positions = {'reye': (16, 15), 'leye' : (16, 48)}
)

tan_triggs = bob.bio.face.preprocessor.TanTriggs(
    face_cropper = face_cropper
)

inorm_lbp = bob.bio.face.preprocessor.INormLBP(
    face_cropper = face_cropper,
    dtype = numpy.float64
)



##############################################################################
#########################  Extractors  #######################################
dct_extractor = bob.bio.face.extractor.DCTBlocks(
    # block setup
    block_size = 10,
    block_overlap = 9,
    # coefficients
    number_of_dct_coefficients = 45
)

lgbphs_extractor = bob.bio.face.extractor.LGBPHS(
    # block setup
    block_size = 4,
    block_overlap = 0,
    # Gabor parameters
    gabor_sigma = math.sqrt(2.)*math.pi,
    gabor_maximum_frequency = math.pi,
    use_gabor_phases = True,
    # LBP setup (we use the defaults)
    lbp_radius = 2,
    lbp_uniform = False,
    # histogram setup
    sparse_histogram = True
)

graphs_extractor = bob.bio.face.extractor.GridGraph(
    # Gabor parameters
    gabor_sigma = 2.*math.pi,
    gabor_maximum_frequency = math.pi/math.sqrt(2.),

    # setup of the fixed grid
    node_distance = (8, 8)
)




##############################################################################
#########################  Algorithms  #######################################


hist_algorithm = bob.bio.face.algorithm.Histogram(
    # Scoring
    distance_function = bob.math.histogram_intersection,
    is_distance_function = False,
    multiple_probe_scoring = 'max'
)

jets_algorithm = bob.bio.face.algorithm.GaborJet(
    # Gabor jet comparison
    gabor_jet_similarity_type = "PhaseDiffPlusCanberra",
    # Gabor wavelet setup
    gabor_sigma = 2.*math.pi,
    gabor_maximum_frequency = math.pi,
    multiple_feature_scoring = 'max_jet'
)

isv_algorithm = bob.bio.gmm.algorithm.ISV(
    # GMM parameters
    number_of_gaussians = 768,
    # ISV parameters
    subspace_dimension_of_u = 100
)


##############################################################################
###########################  LDA-IR  #########################################

# LDA-IR tuning as defaulted by facerec2010
LDAIR_REGION_ARGS = copy.deepcopy(facerec2010.baseline.lda.CohortLDA_REGIONS)
LDAIR_REGION_KEYWORDS = copy.deepcopy(facerec2010.baseline.lda.CohortLDA_KEYWORDS)
# we just disable the cohort normalization
for kwargs in LDAIR_REGION_ARGS:
  kwargs['cohort_adjust'] = False

ldair_crop = bob.bio.csu.preprocessor.LDAIR(
    # LDA-IR region specification
    LDAIR_REGION_ARGS,
    LDAIR_REGION_KEYWORDS
)

ldair_extractor = bob.bio.csu.extractor.LDAIR(
    # LDA-IR region specification
    LDAIR_REGION_ARGS,
    LDAIR_REGION_KEYWORDS
)

ldair_algorithm = bob.bio.csu.algorithm.LDAIR(
    # LDA-IR region specification
    LDAIR_REGION_ARGS,
    LDAIR_REGION_KEYWORDS,
    multiple_model_scoring = 'max',
    multiple_probe_scoring = 'max'
)
