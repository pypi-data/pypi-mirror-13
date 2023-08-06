#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Manuel Guenther <siebenkopf@googlemail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# This file contains the python (distutils/setuptools) instructions so your
# package can be installed on **any** host system. It defines some basic
# information like the package name for instance, or its homepage.
#
# It also defines which other packages this python package depends on and that
# are required for this package's operation. The python subsystem will make
# sure all dependent packages are installed or will install them for you upon
# the installation of this package.
#
# The 'buildout' system we use here will go further and wrap this package in
# such a way to create an isolated python working environment. Buildout will
# make sure that dependencies which are not yet installed do get installed, but
# **without** requiring administrative privileges on the host system. This
# allows you to test your package with new python dependencies w/o requiring
# administrative interventions.

from setuptools import setup, dist
dist.Distribution(dict(setup_requires=['bob.extension']))

from bob.extension.utils import load_requirements, find_packages
install_requires = load_requirements()

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    # This is the basic information about your project. Modify all this
    # information before releasing code publicly.
    name = 'bob.chapter.FRICE',
    version = open("version.txt").read().rstrip(),
    description = 'Running the experiments as described in the boock chapter "Face Recognition in Challenging Environments: An Experimental and Reproducible Research Survey"',

    license = 'GPLv3',
    author = 'Manuel Guenther',
    author_email = 'siebenkopf@googlemail.com',
    keywords = 'bob, face recognition',

    # If you have a better, long description of your package, place it on the
    # 'doc' directory and then hook it here
    long_description = open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages = find_packages(),
    include_package_data = True,

    # This line defines which packages should be installed when you "install"
    # this package. All packages that are mentioned here, but are not installed
    # on the current system will be installed locally and only visible to the
    # scripts of this package. Don't worry - You won't need administrative
    # privileges when using buildout.
    install_requires = install_requires,

    # This entry defines which scripts you will have inside the 'bin' directory
    # once you install the package (or run 'bin/buildout'). The order of each
    # entry under 'console_scripts' is like this:
    #   script-name-at-bin-directory = module.at.your.library:function
    #
    # The module.at.your.library is the python file within your library, using
    # the python syntax for directories (i.e., a '.' instead of '/' or '\').
    # This syntax also omits the '.py' extension of the filename. So, a file
    # installed under 'example/foo.py' that contains a function which
    # implements the 'main()' function of particular script you want to have
    # should be referred as 'example.foo:main'.
    #
    # In this simple example we will create a single program that will print
    # the version of bob.
    entry_points = {

      # scripts should be declared using this entry:
      'console_scripts' : [
        'image_resolution            = bob.chapter.FRICE.script.image_resolution:main',
        'image_preprocessor          = bob.chapter.FRICE.script.image_preprocessor:main',
        'configuration_optimization  = bob.chapter.FRICE.script.configuration_optimization:main',
        'occlusion                   = bob.chapter.FRICE.script.occlusion:main',
        'expression                  = bob.chapter.FRICE.script.expression:main',
        'pose                        = bob.chapter.FRICE.script.pose:main',
        'image_databases             = bob.chapter.FRICE.script.image_databases:main',
        'video_databases             = bob.chapter.FRICE.script.video_databases:main',
        'timing                      = bob.chapter.FRICE.script.timing:main',
      ],

      'bob.bio.database': [
        'arface-ill    = bob.chapter.FRICE.databases.arface:arface_illumination',
        'arface-occ    = bob.chapter.FRICE.databases.arface:arface_occlusion',
        'xm2vts        = bob.chapter.FRICE.databases.xm2vts:xm2vts',
        'lfw           = bob.bio.face.config.database.lfw_unrestricted:database',
        'mobio         = bob.bio.face.config.database.mobio_image:database',
        'mobio-video   = bob.chapter.FRICE.databases.mobio:mobio_video',
        'youtube-video = bob.chapter.FRICE.databases.youtube:youtube',
      ],

      'bob.bio.preprocessor': [
        'face-crop   = bob.chapter.FRICE.configurations.optimized:face_cropper',
        'tan-triggs  = bob.chapter.FRICE.configurations.optimized:tan_triggs',
        'inorm-lbp   = bob.chapter.FRICE.configurations.optimized:inorm_lbp',
        'lda-ir      = bob.chapter.FRICE.configurations.optimized:ldair_crop',
      ],

      'bob.bio.extractor': [
        'dct         = bob.chapter.FRICE.configurations.optimized:dct_extractor',
        'lgbphs      = bob.chapter.FRICE.configurations.optimized:lgbphs_extractor',
        'graphs      = bob.chapter.FRICE.configurations.optimized:graphs_extractor',
        'lda-ir      = bob.chapter.FRICE.configurations.optimized:ldair_extractor',
      ],

      'bob.bio.algorithm': [
        'hist        = bob.chapter.FRICE.configurations.optimized:hist_algorithm',
        'jets        = bob.chapter.FRICE.configurations.optimized:jets_algorithm',
        'isv         = bob.chapter.FRICE.configurations.optimized:isv_algorithm',
        'lda-ir      = bob.chapter.FRICE.configurations.optimized:ldair_algorithm',
      ],

      'bob.bio.grid': [
        'lgbphs            = bob.chapter.FRICE.configurations.grid:lgbphs',
        'video             = bob.chapter.FRICE.configurations.grid:video',
        'isv               = bob.chapter.FRICE.configurations.grid:isv',
      ]

    },

    # Classifiers are important if you plan to distribute this package through
    # PyPI. You can find the complete list of classifiers that are valid and
    # useful here (http://pypi.python.org/pypi?%3Aaction=list_classifiers).
    classifiers = [
      'Framework :: Bob',
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
)
