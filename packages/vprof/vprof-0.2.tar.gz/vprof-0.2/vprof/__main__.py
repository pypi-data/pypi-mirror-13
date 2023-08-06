"""Main module for visual profiler."""
import argparse
import os
import sys

from collections import OrderedDict
from vprof import profile_wrappers
from vprof import stats_server


_MODULE_DESC = 'Python visual profiler.'
_HOST = 'localhost'

_PROFILE_MAP = {
    'c': profile_wrappers.RuntimeProfile,
    'm': profile_wrappers.MemoryProfile,
    'h': profile_wrappers.CodeHeatmapProfile,
}

def main():
    """Visual profiler main function."""
    parser = argparse.ArgumentParser(description=_MODULE_DESC)
    parser.add_argument('profilers', metavar='opts',
                        help='Profilers configuration')
    parser.add_argument('source', metavar='src', nargs=1,
                        help='Python program to profile.')
    parser.add_argument('--port', dest='port', default=8000, type=int,
                        help='Internal webserver port.')
    args = parser.parse_args()

    if len(args.profilers) > len(set(args.profilers)):
        print('Profiler configuration is ambiguous. Remove duplicates.')
        sys.exit(1)

    for option in args.profilers:
        if option not in _PROFILE_MAP:
            print('Unrecognized option: %s' % option)
            sys.exit(2)

    sys.argv[:] = args.source
    program_name, program_stats = args.source[0], OrderedDict()
    for option in args.profilers:
        curr_profiler = _PROFILE_MAP[option](program_name)
        print('Running %s...' % curr_profiler.__class__.__name__)
        program_stats[option] = curr_profiler.run()
    sys.stderr = open(os.devnull, "w")
    print('Starting HTTP server...')
    stats_server.start(_HOST, args.port, program_stats)

if __name__ == "__main__":
    main()
