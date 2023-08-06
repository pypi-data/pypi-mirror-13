import os
import subprocess

def test_imports():
  # tests that all tools that we require are actually installed

  import bob.bio.base
  import bob.bio.face
  import bob.bio.gmm
  import bob.bio.video

global executables
executables = {}

def test_bin():
  import bob.extension
  # find executables
  global executables
  for script in ['verify.py', 'verify_isv.py', 'grid_search.py', 'databases.py', 'image_resolution', 'image_preprocessor', 'configuration_optimization', 'occlusion', 'expression', 'pose', 'image_databases', 'video_databases', 'timing']:
    e = bob.extension.find_executable(script, prefixes = ['bin'])
    assert len(e), "The script %s could not be found" % script
    executables[script] = e[0]


def _call(cmd):
  from bob.bio.base.test.utils import Quiet
  from bob.bio.base.tools import command_line
  q = Quiet()
  with q:
    assert subprocess.call(cmd, stdout=q._stdout, stderr=q._stderr) == 0, "Command line failed: %s" % command_line(cmd)


def test_image_resolution():
  # checks that the scripts that we will need are actually installed
  from bob.io.base.test_utils import temporary_filename
  tmp = temporary_filename(suffix='.pdf')

  try:
    # image resolution
    _call([executables['image_resolution'], '-x', 'preprocess', '-q'])
    _call([executables['image_resolution'], '-x', 'execute', '-q'])
    _call([executables['image_resolution'], '-x', 'evaluate', '-w', tmp])
    assert os.path.exists(tmp)
  finally:
    if os.path.exists(tmp): os.remove(tmp)

def test_image_preprocessor():
  from bob.io.base.test_utils import temporary_filename
  tmp = temporary_filename(suffix='.pdf')

  try:
    # image preprocessor
    _call([executables['image_preprocessor'], '-x', 'preprocess', '-q'])
    _call([executables['image_preprocessor'], '-x', 'execute', '-q'])
    _call([executables['image_preprocessor'], '-x', 'evaluate', '-w', tmp])
    assert os.path.exists(tmp)
  finally:
    if os.path.exists(tmp): os.remove(tmp)

def test_configuration_optimization():
  from bob.io.base.test_utils import temporary_filename
  tmp = temporary_filename(suffix='.pdf')

  try:
    # image preprocessor
    _call([executables['configuration_optimization'], '-x', 'preprocess', '-q'])
    _call([executables['configuration_optimization'], '-x', 'execute', '-t', '1', '-q'])
    _call([executables['configuration_optimization'], '-x', 'execute', '-t', '2', '-q'])
    _call([executables['configuration_optimization'], '-x', 'execute', '-t', '3', '-q'])
    _call([executables['configuration_optimization'], '-x', 'evaluate', '--all', '-w', tmp])
    assert os.path.exists(tmp)
  finally:
    if os.path.exists(tmp): os.remove(tmp)


def test_occlusion():
  from bob.io.base.test_utils import temporary_filename
  tmp = temporary_filename(suffix='.pdf')

  try:
    # image preprocessor
    _call([executables['occlusion'], '-x', 'preprocess', '-q'])
    _call([executables['occlusion'], '-x', 'train', '-q'])
    _call([executables['occlusion'], '-x', 'execute', '-q'])
    _call([executables['occlusion'], '-x', 'evaluate', '--all', '-w', tmp])
    assert os.path.exists(tmp)
  finally:
    if os.path.exists(tmp): os.remove(tmp)

def test_expression():
  from bob.io.base.test_utils import temporary_filename
  tmp = temporary_filename(suffix='.pdf')

  try:
    # image preprocessor
    _call([executables['expression'], '-x', 'preprocess', '-q'])
    _call([executables['expression'], '-x', 'execute', '-q'])
    _call([executables['expression'], '-x', 'evaluate', '--all', '-w', tmp])
    assert os.path.exists(tmp)
  finally:
    if os.path.exists(tmp): os.remove(tmp)

def test_pose():
  from bob.io.base.test_utils import temporary_filename
  tmp = temporary_filename(suffix='.pdf')

  try:
    # image preprocessor
    _call([executables['pose'], '-x', 'preprocess', '-q'])
    _call([executables['pose'], '-x', 'execute', '-q'])
    _call([executables['pose'], '-x', 'evaluate', '--all', '-w', tmp])
    assert os.path.exists(tmp)
  finally:
    if os.path.exists(tmp): os.remove(tmp)


def test_mobio_image():
  from bob.io.base.test_utils import temporary_filename
  tmp = temporary_filename(suffix='.pdf')

  try:
    # image preprocessor
    _call([executables['image_databases'], '-d', 'mobio', '-x', 'preprocess', '-q'])
    _call([executables['image_databases'], '-d', 'mobio', '-x', 'execute', '-q'])
    _call([executables['image_databases'], '-d', 'mobio', '-x', 'evaluate', '--all', '-w', tmp])
    assert os.path.exists(tmp)
  finally:
    if os.path.exists(tmp): os.remove(tmp)

def test_lfw():
  from bob.io.base.test_utils import temporary_filename
  tmp = temporary_filename(suffix='.pdf')

  try:
    # image preprocessor
    _call([executables['image_databases'], '-d', 'lfw', '-x', 'preprocess', '-q'])
    _call([executables['image_databases'], '-d', 'lfw', '-x', 'execute', '-q'])
    _call([executables['image_databases'], '-d', 'lfw', '-x', 'evaluate', '--all', '-w', tmp])
    assert os.path.exists(tmp)
  finally:
    if os.path.exists(tmp): os.remove(tmp)


def test_mobio_video():
  from bob.io.base.test_utils import temporary_filename
  tmp = temporary_filename(suffix='.pdf')

  try:
    # image preprocessor
    _call([executables['video_databases'], '-d', 'mobio', '-n', '1', '-x', 'preprocess', '-q'])
    _call([executables['video_databases'], '-d', 'mobio', '-n', '1', '-x', 'execute', '-q'])
    _call([executables['video_databases'], '-d', 'mobio', '-x', 'evaluate', '--all', '-w', tmp])
    assert os.path.exists(tmp)
  finally:
    if os.path.exists(tmp): os.remove(tmp)

def test_youtube():
  from bob.io.base.test_utils import temporary_filename
  tmp = temporary_filename(suffix='.pdf')

  try:
    # image preprocessor
    _call([executables['video_databases'], '-d', 'youtube', '-n', '3', '-x', 'preprocess', '-q'])
    _call([executables['video_databases'], '-d', 'youtube', '-n', '3', '-x', 'execute', '-q'])
    _call([executables['video_databases'], '-d', 'youtube', '-x', 'evaluate', '--all', '-w', tmp])
    assert os.path.exists(tmp)
  finally:
    if os.path.exists(tmp): os.remove(tmp)
