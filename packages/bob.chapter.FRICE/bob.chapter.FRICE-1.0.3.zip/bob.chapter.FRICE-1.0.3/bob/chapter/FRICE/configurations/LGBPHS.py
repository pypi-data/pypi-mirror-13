#!/bin/python

preprocessor = 'bob.bio.face.preprocessor.TanTriggs(face_cropper=bob.bio.face.preprocessor.FaceCrop(cropped_image_size=(80, 64), cropped_positions={"reye":(16, 15), "leye":(16, 48)}))'

extractor = "bob.bio.face.extractor.LGBPHS(block_size=#B, block_overlap=#O, lbp_neighbor_count=#N, lbp_uniform=#U, gabor_sigma=#G, gabor_maximum_frequency=#K, use_gabor_phases=#P, sparse_histogram=True)"

algorithm = "bob.bio.face.algorithm.Histogram(distance_function=#F, is_distance_function=#S)"

# Replacements in first round: block size and overlap
replace_1 = {
    'extract' : {
        # block size
        '#B' : {
            'B04' : '4',
            'B06' : '6',
            'B08' : '8',
            'B10' : '10',
            'B12' : '12',
        },

        # block overlap
        '#O' : {
            'O00' : '0',
            'O01' : '1',
            'O03' : '3',
            'O05' : '5',
            'O07' : '7',
        },
    },

    'score' : {
        '(#N, #U, #G, #K, #P, #F, #S)' : {
            '.' : (8, True, '2.*math.pi', 'math.pi/2.', False, 'bob.math.chi_square', True)
        }
    }
}



# Replacements in second round: Gabor parameters
replace_2 = {
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
        },

        '#P' : {
            'Phase'      : 'True',
            'NoPhase'    : 'False'
        }
    },

    'score' : {
        '(#B, #O, #N, #U, #F, #S)' : {
            '.' : (4, 0, 8, True, 'bob.math.chi_square', True)
        }
    }
}


# Replacements in third round: LBP parameters and histogram similarity function
replace_3 = {
    'extract' : {
        '#N' : {
            'N04' : 4,
            'N08' : 8,
        },

        '#U' : {
            'Uniform' : True,
            'Non_Uni' : False,
        }
    },

    'score' : {
        '(#F, #S)' : {
            'Chi2' : ('bob.math.chi_square', True),
            'Hist' : ('bob.math.histogram_intersection', False),
            'KbLl' : ('bob.math.kullback_leibler', True),
        },

        '(#B, #O, #G, #K, #P)':{
            '.' : (4, 0, 'math.sqrt(2.)*math.pi', 'math.pi', True)
        }
    }
}

requirements = ['#B > #O']

imports = ['bob.bio.face', 'math', 'bob.math']
