# This file contains the configuration for the Image Resolution test, which should be used in combination with the ./bin/parameter_test.py function of the FaceRecLib


reference_height = 80.

preprocessor = 'bob.bio.face.preprocessor.FaceCrop(cropped_image_size=(#H, #W), cropped_positions={"reye":(#H/5, #W/4-1), "leye":(#H/5, #W*3/4)})'

# Replacements
replace = {

  'preprocess' : {
    '(#H,#W,#F)' : {
      'H020' : (20, 16, 20/reference_height),
      'H040' : (40, 32, 40/reference_height),
      'H060' : (60, 48, 60/reference_height),
      'H080' : (80, 64, 80/reference_height),
      'H100' : (100, 80, 100/reference_height),
      'H120' : (120, 96, 120/reference_height),
      'H160' : (160, 128, 160/reference_height),
      'H200' : (200, 160, 200/reference_height)
    }
  }
}

imports = ['bob.bio.base', 'bob.bio.face', 'bob.bio.gmm', 'math', 'bob.math', 'scipy']
