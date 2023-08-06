.. vim: set fileencoding=utf-8 :
.. Manuel Günther <manuel.guenther@idiap.ch>
.. Wed Apr 17 15:48:58 CEST 2013

Installation
============
The installation of this package is made as easy as possible.
Nonetheless, the experiments will not work out of the box, but will require some setup.


External Software
-----------------
Most of the software that is required to run the face recognition experiments are automatically downloaded from the `Python Package Index (PyPI) <https://pypi.python.org/pypi>`_.
Nonetheless, some further open source software is required in these experiments.


Bob
...
Most of the functionallity inside this package relies on Bob_, a signal processing and machine learning toolbox for researchers.
More precisely, all experiments heavily rely on the :ref:`bob.bio.base <bob.bio.base>` package.

Although all bob packages (including ``bob.bio.base``) will be automatically downloaded from PyPI_, there are some external libraries, on which Bob_ depends, which need to be installed.
For more detailed information, please read the list of `Dependencies <https://github.com/idiap/bob/wiki/Dependencies>`_ for your operating system.

.. note::
   Currently, this package only works in Unix-like environments and under MacOS.
   Due to limitations of the Bob library, MS Windows operating systems are not supported.
   We are working on a port of Bob for MS Windows, but it might take a while.


CSU face recognition resources
..............................
Due to the fact that the CSU toolkit needs to be patched to work with ``bob.bio.base``, the setup is unfortunately slightly more complicated.
To be able to run the experiments based on the CSU toolkit, i.e., the LDA-IR algorithms, please download the CSU face recognition resources from http://www.cs.colostate.edu/facerec/.
After unpacking the CSU toolkit, it needs to be patched.
Please read the documentation of :ref:`bob.bio.csu <bob.bio.csu>` for more information on how to patch the CSU toolkit.

Anyways, if you do not want to install the CSU toolkit, no worries.
All of our scripts will will take care of that.


Preparing the Experiments
.........................
This package relies on the buildout system.
After installing Bob and the CSU toolkit, you need to generate the scripts that will execute the experiments by executing the commands:

.. code-block:: sh

  $ python bootstrap-buildout.py
  $ bin/buildout buildout:csu-dir=<PATH-TO-YOUR-PATCHED-COPY-OF-THE-CSU-TOOLKIT>


This will automatically download and configure all other packages required to run the experiments.

.. note::
   If you do not have the CSU toolkit, you can replace the second line from above with:

   .. code-block:: sh

      $ bin/buildout -c buildout-without-csu.cfg

.. note::
   If you prefer to use the latest versions of all Bob_ packages, you can also check them out from GitHub_ and compile them locally.
   Simply replace the second line from above with:

   .. code-block:: sh

      $ bin/buildout buildout:csu-dir=<PATH-TO-YOUR-PATCHED-COPY-OF-THE-CSU-TOOLKIT> -c buildout-develop.cfg

   And download some additional files for the database interfaces (which are not contained in the GitHub packages):

   .. code-block:: sh

      $ bin/bob_dbmanage.py all download

Afterward, a **./bin** directory will exist, in which several scripts are provided.
You should validate your installation by running the test suite:

.. code-block:: sh

  $ bin/nosetests -vs

Please make sure that all tests pass.
Afterward, you can call the following command lines to generate and open this documentation:

.. code-block:: sh

  $ bin/sphinx-build docs sphinx
  $ firefox sphinx/index.html


Image Databases
---------------
All experiments are run on external image databases.
We do not provide the images from the databases themselves.
Hence, please contact the database owners to obtain a copy of the images.
Here is a list of websites that you might find useful:

- AR face [``arface``]: http://www2.ece.ohio-state.edu/~aleix/ARdatabase.html
- BANCA [``banca``]: http://www.ee.surrey.ac.uk/CVSSP/banca
- LFW  [``lfw``]: http://vis-www.cs.umass.edu/lfw
- MOBIO [``mobio``]: http://www.idiap.ch/dataset/mobio
- Multi-PIE [``multipie``]: http://www.multipie.org
- XM2VTS [``xm2vts``]: http://www.ee.surrey.ac.uk/CVSSP/xm2vtsdb

After downloading the databases and the eye location annotations (or some of them), you will need to tell our software, where it can find them.
Please refer to the ``Databases`` section in :ref:`bob.bio.base Installation <bob.bio.base.installation>`, which basically translates to:

1. Run ``./bin/databases.py`` and check the database directories that are listed.
   Most of them should look somewhat like ``[YOUR_<DB>_DIRECTORY]``, and they should be self-explanatory.
   If more databases are listed than you actually possess, you can simply ignore them.

2. Open the file ``~/.bob_bio_databases.txt`` with your preferred text editor.
   Write a line ``[YOUR_<DB>_DIRECTORY] = /your/path/to/db/files`` for each of the entries that you possess; for the names, please check the results of 1.
   Save the file.

3. Re-run ``./bin/databases.py`` and check the database directories are listed correctly now.


Pre-computed Score Files
------------------------
Most of the experiments will require a relatively large amount of time and memory to execute.
Furthermore, you might not possess all databases that are required to run the experiments.
Additionally, there experiments of the COTS algorithm require 3rd-party software to be installed, and the COTS vendor wants to be anonymous, so you wouldn't even know, which software to install.

Don't worry, you will still be able to generate the plots.
All you need is to download the score files that we have generated from our web server: http://www.idiap.ch/resource/biometric
Please see the "FRICE" section there.
Simply download the according score files and extract them in the main directory of this package.

.. include:: links.rst
