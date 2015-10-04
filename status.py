#!/usr/bin/env python3

import asyncio
import signal
import sys
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


async_loop = asyncio.get_event_loop()
script_location = Path(__file__).resolve().parent
scripts_dir = Path(script_location, 'scripts')

scripts = []

def print_all():
    print( ' '.join( [script.last_line for script in scripts] ) )
    sys.stdout.flush()

# Properly exit upon catching signals
def sig_handler( signum, frame ):
    exit()

# Kill all our children, leaving no orphans
def exit():
    for script in scripts:
        script.process.terminate()
    sys.exit(0)
    
# Catch some deadly signals
signal.signal( signal.SIGILL, sig_handler )
signal.signal( signal.SIGINT, sig_handler )
signal.signal( signal.SIGTERM, sig_handler )

for script_file in [ file for file in scripts_dir.iterdir() if file.is_file()]:
    path = str( script_file.resolve() )
    script = Script( path )
    scripts.append( script )
    async_loop.add_reader( script.out, script.update )

try:
    async_loop.run_forever()
except KeyboardInterrupt:
    exit()
