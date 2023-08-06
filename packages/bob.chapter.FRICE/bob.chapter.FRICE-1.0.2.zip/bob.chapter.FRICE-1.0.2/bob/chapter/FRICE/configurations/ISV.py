#!/bin/python

preprocessor = 'bob.bio.face.preprocessor.TanTriggs(face_cropper=bob.bio.face.preprocessor.FaceCrop(cropped_image_size=(80, 64), cropped_positions={"reye":(16, 15), "leye":(16, 48)}))'

extractor = 'bob.bio.face.extractor.DCTBlocks(block_size=#B, block_overlap=#O, number_of_dct_coefficients=#C)'

algorithm = 'bob.bio.gmm.algorithm.ISV(number_of_gaussians=#G, subspace_dimension_of_u=#U)'


# For preprocessing only
replace_0 = {
    'preprocess' : {
        '(#B, #O, #C, #G, #U)' : {
            '.': (8, 0, 45, 512, 80)
        }
    }
}

# Replacements in the first round: DCT block size and overlap
replace_1 = {
    'extract' : {
        # block size
        '#B' : {
            'B_08' : 8,
            'B_10' : 10,
            'B_12' : 12,
            'B_14' : 14,
            'B_16' : 16
        },

        # block overlap
        '#O' : {
            'O_00' : 0,
            'O_03' : 3,
            'O_05' : 5,
            'O_07' : 7,
            'O_09' : 9,
            'O_11' : 11,
            'O_13' : 13,
            'O_15' : 15
        },
    },

    'project' : {
        '(#C, #G, #U)' : {
            '.' : (45, 512, 80)
        }
    }

}


# Replacements in the second round: DCT coefficients
replace_2 = {
    'extract' : {
        # number of coefficients
        '#C' : {
            'C_05' : 5,
            'C_15' : 15,
            'C_25' : 25,
            'C_35' : 35,
            'C_45' : 45,
            'C_55' : 55,
            'C_65' : 65,
            'C_75' : 75,
            'C_85' : 85
        }
    },

    'project' : {
        '(#B, #O, #G, #U)' : {
            '.' : (10, 9, 512, 80)
        }
    }
}

# Replacements in the third round: Number of Gaussians and ISV subspace dimension
replace_3 = {
    'extract' : {
        '(#B, #O, #C)' : {
            '.' : (10, 9, 45)
        }
    },

    'project' : {
        # number of Gaussians
        '#G' : {
            'G_032' : 32,
            'G_064' : 64,
            'G_128' : 128,
            'G_256' : 256,
            'G_512' : 512,
            'G_768' : 768
        },

        # U dimension
        '#U' : {
            'U_020' : 20,
            'U_040' : 40,
            'U_060' : 60,
            'U_080' : 80,
            'U_100' : 100,
            'U_120' : 120,
            'U_140' : 140,
            'U_160' : 160,
            'U_180' : 180,
            'U_200' : 200
        }
    }
}

requirements = ["#B > #O"]
imports = ['bob.bio.face', 'bob.bio.gmm']
