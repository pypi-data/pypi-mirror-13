#!/bin/python

preprocessor = 'bob.bio.face.preprocessor.INormLBP(face_cropper=bob.bio.face.preprocessor.FaceCrop(cropped_image_size=(80, 64), cropped_positions={"reye":(16, 15), "leye":(16, 48)}), dtype=numpy.float64)'

extractor = 'bob.bio.face.extractor.GridGraph(gabor_sigma=#G, gabor_maximum_frequency=#K, node_distance=(#D, #D))'

algorithm = 'bob.bio.face.algorithm.GaborJet(gabor_jet_similarity_type="#S", gabor_sigma=#G, gabor_maximum_frequency=#K, multiple_feature_scoring="#M")'


# For preprocessing only
replace_0 = {
    'preprocess' : {
        '(#G, #K, #S, #D, #M)' : {
            '.': ('math.pi', 'math.pi', 'ScalarProduct', '8', 'max_graph')
        }
    }
}

# replacements in the first round: Gabor parameters and the similarity function
replace_1 = {
    'extract' : {
        '#G' : {
            'S1_2PI'     : '2.*math.pi',
            'S2_SQRT2PI' : 'math.sqrt(2.)*math.pi',
            'S3_PI'      : 'math.pi'
        },

        '#K' : {
            'K1_PI2'     : 'math.pi/2.',
            'K2_PISQRT2' : 'math.pi/math.sqrt(2.)',
            'K3_PI'      : 'math.pi'
        }
    },

    'score' : {
        '#S' : {
            'Cos'       : 'ScalarProduct',
            'Can'       : 'Canberra',
            'Disp'      : 'Disparity',
            'PhDiff'    : 'PhaseDiff',
            'PhDiffCan' : 'PhaseDiffPlusCanberra'
        },

        '(#D, #M)' : {
            '.' : (8, 'max_graph')
        }
    }
}


# replacements in the second round: grid density and scoring strategy
replace_2 = {
    'extract' : {
        '#D' : {
            'D01' : 1,
            'D02' : 2,
            'D04' : 4,
            'D08' : 8,
            'D12' : 12,
            'D16' : 16,
        }
    },

    'enroll' : {
        '#M' : {
            '1_average' : 'average',
            '3a_maximum' : 'max_jet',
            '3b_median' : 'med_jet',
            '3c_minimum' : 'min_jet',
            '2a_best' : 'max_graph',
            '2b_mean' : 'med_graph',
            '2c_worst' : 'min_graph',
        }
    },

    'score' : {
        '(#G, #K, #S)' : {
            '.'  : ('2.*math.pi', 'math.pi/math.sqrt(2.)', 'PhaseDiffPlusCanberra')
        }
    }
}

imports = ['bob.bio.face', 'math', 'scipy', 'numpy']
