#!/usr/bin/env python

import bob.db.arface
import bob.bio.base

arface_illumination = bob.bio.base.database.DatabaseBob(
    database = bob.db.arface.Database(
      original_directory = '[YOUR_ARFACE_DIRECTORY]',
    ),
    name = 'arface',
    protocol = 'illumination',

    all_files_options =          { 'expressions' : 'neutral', 'occlusions' : 'none' },
    extractor_training_options = { 'expressions' : 'neutral', 'occlusions' : 'none' },
    projector_training_options = { 'expressions' : 'neutral', 'occlusions' : 'none' },
    enroller_training_options =  { 'expressions' : 'neutral', 'occlusions' : 'none' }
)


arface_occlusion = bob.bio.base.database.DatabaseBob(
    database = bob.db.arface.Database(
      original_directory = '[YOUR_ARFACE_DIRECTORY]',
    ),
    name = 'arface',
    protocol = 'all',

    all_files_options =          { 'expressions' : 'neutral' },
    extractor_training_options = { 'expressions' : 'neutral' },
    projector_training_options = { 'expressions' : 'neutral' },
    enroller_training_options =  { 'expressions' : 'neutral' }
)
