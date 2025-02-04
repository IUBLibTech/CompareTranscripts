"""
Find and Activate the virtual environment
"""
import __main__
import os
from pathlib import Path
import sys

venv = None
here = Path(sys.path[0]) # start in the script directory
for _ in range(2):
    if (here / ".venv").is_dir():
        venv = str((here / ".venv").absolute())
        break
    here = here.parent

if not venv:
    print("ERROR: Cannot locate .venv for this script", file=sys.stderr)
    exit(99)

if os.environ.get("VIRTUAL_ENV", '') != venv:
    # we haven't activated the venv we found, let's do that in the same
    # way that the activate script does.
    os.environ['VIRTUAL_ENV'] = venv
    os.environ['PATH'] = f"{venv}/bin:{os.environ['PATH']}"
    os.environ.pop('PYTHONHOME', None)
    os.environ['PYTHONPATH'] = str(Path(venv).parent)

    # restart the script using the new environment        
    this_script = str(Path(__main__.__file__).resolve())    
    os.execve(this_script, sys.argv, os.environ)