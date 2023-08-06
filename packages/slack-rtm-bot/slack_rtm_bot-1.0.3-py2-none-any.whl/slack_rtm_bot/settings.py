import importlib
import os
import sys

if 'SLACK_RTM_BOT_SETTINGS_FILE' not in os.environ:
  from . import settings_local as settings
else:
  dirname, basename = os.path.split(os.environ['SLACK_RTM_BOT_SETTINGS_FILE'])
  if dirname and dirname not in sys.path:
    sys.path.append(dirname)
  settings = importlib.import_module(os.path.splitext(basename)[0])

globals().update(settings.__dict__)
