import bob.bio.base

# define a queue specifically for the LGBPHS algorithm
lgbphs = bob.bio.base.grid.Grid(
  # feature extraction
  extraction_queue = '16G',
  # model enrollment
  enrollment_queue = '16G',
  # scoring
  scoring_queue = '16G'
)

video = bob.bio.base.grid.Grid(
  # training
  training_queue = '32G',
  # detection
  number_of_preprocessing_jobs = 64,
  preprocessing_queue = '8G-io-big',
  # feature extraction
  extraction_queue = '4G-io-big',
  # feature extraction
  projection_queue = '4G-io-big',
  # model enrollment
  enrollment_queue = '8G-io-big',
  # scoring
  scoring_queue = '8G-io-big'
)

isv = bob.bio.base.grid.Grid(
  # training
  training_queue = '16G-io-big',
  # detection
  number_of_preprocessing_jobs = 64,
  preprocessing_queue = '4G-io-big',
  # feature extraction
  extraction_queue = '8G-io-big',
  # feature projection
  projection_queue = '8G-io-big',
  # model enrollment
  enrollment_queue = '8G-io-big',
  # scoring
  scoring_queue = '8G-io-big'
)
