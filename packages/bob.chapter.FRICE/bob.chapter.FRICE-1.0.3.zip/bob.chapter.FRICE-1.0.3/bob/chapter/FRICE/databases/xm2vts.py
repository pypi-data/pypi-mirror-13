#!/usr/bin/env python

import bob.db.xm2vts
import bob.bio.base

# setup for XM2VTS
xm2vts = bob.bio.base.database.DatabaseBob(
    database = bob.db.xm2vts.Database(
      original_directory = '[YOUR_XM2VTS_DIRECTORY]',
    ),

    name = "xm2vts",
    protocol = 'darkened-lp1'
)
