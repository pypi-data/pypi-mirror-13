# This file contains the configuration for the Image Preprocessing test, which should be used in combination with the ./bin/parameter_test.py function of the FaceRecLib

face_cropper = 'bob.bio.face.preprocessor.FaceCrop(cropped_image_size=(80, 64), cropped_positions={"reye":(16, 15), "leye":(16, 48)})'

preprocessor = '#A'

# Replacements
replace = {
  'preprocess' : {
    '#A' : {
      'None' : face_cropper,
      'LBP'  : "bob.bio.face.preprocessor.INormLBP(face_cropper=%s, dtype=numpy.float64)" % face_cropper,
      'HEQ'  : "bob.bio.face.preprocessor.HistogramEqualization(face_cropper=%s)" % face_cropper,
      'SQI'  : "bob.bio.face.preprocessor.SelfQuotientImage(face_cropper=%s)" % face_cropper,
      'TT'   : "bob.bio.face.preprocessor.TanTriggs(face_cropper=%s)" % face_cropper,
    },
  }
}

imports = ['bob.bio.base', 'bob.bio.face', 'bob.bio.gmm', 'math', 'bob.math', 'numpy', 'scipy']
