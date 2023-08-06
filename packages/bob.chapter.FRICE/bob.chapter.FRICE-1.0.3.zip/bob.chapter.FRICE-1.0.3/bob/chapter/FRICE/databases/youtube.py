import bob.db.youtube
import bob.bio.base

youtube = bob.bio.base.database.DatabaseBobZT(
    database = bob.db.youtube.Database(
        original_directory = '[YOUR_YOUTUBE_DIRECTORY]',
    ),
    name = "youtube",
    protocol = 'fold1',
    models_depend_on_protocol = True,
    training_depends_on_protocol = True,

    all_files_options = {'subworld' : 'fivefolds'},
    extractor_training_options = {'subworld' : 'fivefolds'},
    projector_training_options = {'subworld' : 'fivefolds'},
    enroller_training_options = {'subworld' : 'fivefolds'},
)
