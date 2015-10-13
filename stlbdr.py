#!/usr/bin/env python3

import asyncio
import argparse
import signal
import os
import sys
from os import R_OK, X_OK
from pathlib import Path, PurePath
from subprocess import Popen, PIPE


class Script:
    def __init__( self, path ):
        self.path = path
        self.name = Path(path).name
        self.last_line = ''
        self.process = Popen(path, stdout=PIPE)
        self.out = self.process.stdout

    def update( self ):
        self.last_line = self.out.readline().decode( 'utf-8' ).rstrip()
        print_all()

class DisplayFile:
    def __init__( self, path ):
        self.path = path
        self.name = Path( path ).name
        self.last_line = Path( path ).read_text().replace("\n", " ")


program_description="Runs a collection of scripts, printing their collective last line of output to stdout."
program_name="statusline-builder"
program_version="0.2.1"

home_script_dir = os.path.expanduser("~/.stlbdr.d")

argparser = argparse.ArgumentParser(description=program_description)
argparser.add_argument("--script-dir", "-d",
                        default = home_script_dir,
                        dest = "script_dir",
                        help="Directory of scripts to run")
argparser.add_argument("--version", "-v", action = "version", version = "%s %s" % (program_name, program_version))

args = vars(argparser.parse_args())
script_dir = Path(args['script_dir'])
async_loop = asyncio.get_event_loop()

outputs = []

def print_all():
    print( ' '.join( [output.last_line for output in outputs] ) )
    sys.stdout.flush()

# Properly exit upon catching signals
def sig_handler( signum, frame ):
    exit()

# Kill all our children, leaving no orphans
def exit(code = 0):
    for script in [output for output in outputs if isinstance( output, Script ) ]:
        script.process.terminate()
    print("\n")
    sys.exit(code)

def exit_with_error(message, code=1):
    print(message, file=sys.stderr)
    exit(code)
 



if not (script_dir.exists() and script_dir.is_dir()):
    exit_with_error("Script directory %s does not exist!" % script_dir)

   
# Catch some deadly signals
for sig in [ signal.SIGILL, signal.SIGINT, signal.SIGTERM ]:
    signal.signal(sig, sig_handler)

for file in sorted([ file for file in script_dir.iterdir() if file.is_file() and os.access(str(file.resolve()), R_OK)]):
    path = str( file.resolve() )
    if os.access(path, X_OK):
        script = Script( path )
        outputs.append( script )
        async_loop.add_reader( script.out, script.update )
    elif path.endswith(".txt"):
        output = DisplayFile( path )
        outputs.append( output )



if not outputs:
    exit_with_error("No scripts or outputs in %s" % script_dir)

print_all()

try:
    async_loop.run_forever()
except KeyboardInterrupt:
    exit()
