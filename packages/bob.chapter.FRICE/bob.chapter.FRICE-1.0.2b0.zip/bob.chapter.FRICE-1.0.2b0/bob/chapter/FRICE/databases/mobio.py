#!/usr/bin/env python

import bob.db.mobio
import bob.bio.base

mobio_video = bob.bio.base.database.DatabaseBob(
    database = bob.db.mobio.Database(
      original_directory = '[YOUR_MOBIO_VIDEO_DIRECTORY]',
      original_extension = '.mp4',
    ),

    name = 'mobio',
    protocol = 'male',
    training_depends_on_protocol = False,
    models_depend_on_protocol = True,

    all_files_options = {'subworld' : 'twothirds-subsampled', 'device' : 'mobile'},
    extractor_training_options = {'subworld' : 'twothirds-subsampled', 'device' : 'mobile'},
    projector_training_options = {'subworld' : 'twothirds-subsampled', 'device' : 'mobile'},
    enroller_training_options = {'subworld' : 'twothirds-subsampled', 'device' : 'mobile'},
)
