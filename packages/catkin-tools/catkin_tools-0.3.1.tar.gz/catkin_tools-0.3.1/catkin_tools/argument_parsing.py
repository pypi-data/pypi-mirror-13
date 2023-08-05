# Copyright 2014 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import os
import re
import sys

from multiprocessing import cpu_count

from catkin_tools.common import wide_log

from catkin_tools.make_jobserver import initialize_jobserver
from catkin_tools.make_jobserver import jobserver_arguments
from catkin_tools.make_jobserver import jobserver_supported


def add_context_args(parser):
    """Add common workspace and profile args to an argparse parser.

    :param parser: The python argparse parser object (or subparser)
    :type parser: ArgumentParser
    """

    add = parser.add_argument
    add_workspace_arg(parser)
    add('--profile', default=None,
        help='The name of a config profile to use (default: active profile)')


def add_workspace_arg(parser):
    """Add common workspace arg to an argparse parser.

    :param parser: The python argparse parser object (or subparser)
    :type parser: ArgumentParser
    """

    add = parser.add_argument
    add('--workspace', '-w', default=None,
        help='The path to the catkin_tools workspace or a directory contained within it (default: ".")')


def add_cmake_and_make_and_catkin_make_args(parser):
    """Add common make and cmake args to an argparse parser.

    :param parser: The python argparse parser object (or subparser)
    :type parser: ArgumentParser
    """

    add = parser.add_argument
    add('-p', '--parallel-packages', '--parallel-jobs', '--parallel', dest='parallel_jobs', default=None,
        help='Maximum number of packages which could be built in parallel (default is cpu count)')
    add('-j', '--jobs', default=None,
        help='Limit parallel job count through the internal GNU make job server. default is cpu count')

    add = parser.add_mutually_exclusive_group().add_argument
    add('--jobserver', dest='use_internal_make_jobserver', default=None, action='store_true',
        help='Use the internal GNU Make job server which will limit the number '
             'of Make jobs across all active packages.')
    add('--no-jobserver', dest='use_internal_make_jobserver', default=None, action='store_false',
        help='Disable the internal GNU Make job server, and use an external one (like distcc, for example).')

    add = parser.add_mutually_exclusive_group().add_argument
    add('--cmake-args', metavar='ARG', dest='cmake_args', nargs='+', required=False, type=str, default=None,
        help='Arbitrary arguments which are passes to CMake. '
             'It collects all of following arguments until a "--" is read.')
    add('--no-cmake-args', dest='cmake_args', action='store_const', const=[], default=None,
        help='Pass no additional arguments to CMake.')

    add = parser.add_mutually_exclusive_group().add_argument
    add('--make-args', metavar='ARG', dest='make_args', nargs='+', required=False, type=str, default=None,
        help='Arbitrary arguments which are passes to make.'
             'It collects all of following arguments until a "--" is read.')
    add('--no-make-args', dest='make_args', action='store_const', const=[], default=None,
        help='Pass no additional arguments to make (does not affect --catkin-make-args).')

    add = parser.add_mutually_exclusive_group().add_argument
    add('--catkin-make-args', metavar='ARG', dest='catkin_make_args',
        nargs='+', required=False, type=str, default=None,
        help='Arbitrary arguments which are passes to make but only for catkin packages.'
             'It collects all of following arguments until a "--" is read.')
    add('--no-catkin-make-args', dest='catkin_make_args', action='store_const', const=[], default=None,
        help='Pass no additional arguments to make for catkin packages (does not affect --make-args).')


def _extract_cmake_and_make_arguments(args, extract_catkin_make):
    """Extract arguments which are meant to be passed to CMake and GNU Make
    through the catkin_tools command line interface.

    :param args: system arguments from which special arguments need to be extracted
    :type args: list
    :returns: tuple of separate args, cmake_args, make args, and catkin make args
    :rtype: tuple
    """
    cmake_args = []
    make_args = []
    catkin_make_args = []

    arg_types = {}

    if '--no-cmake-args' not in args:
        arg_types['--cmake-args'] = cmake_args
    if '--no-make-args' not in args:
        arg_types['--make-args'] = make_args

    if extract_catkin_make and '--no-catkin_make_args' not in args:
        arg_types['--catkin-make-args'] = catkin_make_args

    # Determine where each arg type starts
    # Map from arg indices to arg types
    arg_indexes = {}
    for arg_type in arg_types.keys():
        if arg_type in args:
            arg_indexes[args.index(arg_type)] = arg_type

    def split_arguments(args, splitter_name):
        if splitter_name not in args:
            return args, None
        start_index = args.index(splitter_name)
        end_index = args.index('--', start_index + 1) if '--' in args else None

        if end_index:
            return args[0:index] + args[end_index + 1:], args[index + 1:end_index]
        else:
            return args[0:index], args[index + 1:]

    for index in reversed(sorted(arg_indexes.keys())):
        arg_type = arg_indexes[index]
        args, specific_args = split_arguments(args, arg_type)
        arg_types[arg_type].extend(specific_args)

    # classify -D* and -G* arguments as cmake specific arguments
    if '--cmake-args' in arg_types:
        implicit_cmake_args = [a for a in args if a.startswith('-D') or a.startswith('-G')]
        args = [a for a in args if a not in implicit_cmake_args]
        cmake_args = implicit_cmake_args + cmake_args

    if '--no-cmake-args' not in args and len(cmake_args) == 0:
        cmake_args = None
    if '--no-make-args' not in args and len(make_args) == 0:
        make_args = None
    if extract_catkin_make and '--no-catkin-make-args' not in args and len(catkin_make_args) == 0:
        catkin_make_args = None

    return args, cmake_args, make_args, catkin_make_args


def extract_cmake_and_make_and_catkin_make_arguments(args):
    """Extracts cmake, make, and catkin specific make arguments from given system arguments

    :param args: system arguments from which special arguments need to be extracted
    :type args: list
    :returns: tuple of separate args, cmake_args, make args, and catkin make args
    :rtype: tuple
    """
    return _extract_cmake_and_make_arguments(args, extract_catkin_make=True)


def extract_cmake_and_make_arguments(args):
    """Extracts cmake and make arguments from the given system arguments

    :param args: system arguments from which special arguments need to be extracted
    :type args: list
    :returns: tuple of separate args, cmake_args, and make_args
    :rtype: tuple
    """
    args, cmake_args, make_args, _ = _extract_cmake_and_make_arguments(args, extract_catkin_make=False)
    return args, cmake_args, make_args


def extract_jobs_flags_values(mflags):
    """Gets the values of tha make jobs flags

    :param mflags: string of space separated make arguments
    :type mflags: str
    :returns: dictionary mapping jobs flags to jobs flags values
    :rtype: dict
    """

    regex = r'(?:^|\s)(?:-?(j|l)(\s*[0-9]+|\s|$))' + \
            r'|' + \
            r'(?:^|\s)(?:(?:--)?(jobs|load-average)(?:(?:=|\s+)([0-9]+)|(?:\s|$)))'

    jobs_dict = {}

    matches = re.findall(regex, mflags) or []
    for k, v, key, value in matches:
        v = v.strip()
        value = value.strip()
        if k == 'j' or key == 'jobs':
            jobs_dict['jobs'] = int(v or value) if (v or value) else ''
        elif k == 'l' or key == 'load-average':
            jobs_dict['load-average'] = float(v or value)

    return jobs_dict


def extract_jobs_flags(mflags):
    """Extracts make job flags from a list of other make flags, i.e. -j8 -l8

    :param mflags: string of space separated make arguments
    :type mflags: str
    :returns: list of make jobs flags
    :rtype: list
    """
    regex = r'(?:^|\s)(-?(?:j|l)(?:\s*[0-9]+|\s|$))' + \
            r'|' + \
            r'(?:^|\s)((?:--)?(?:jobs|load-average)(?:(?:=|\s+)[0-9]+|(?:\s|$)))'
    matches = re.findall(regex, mflags) or []
    matches = [m[0] or m[1] for m in matches]
    filtered_flags = [m.strip() for m in matches] if matches else []

    return filtered_flags


def handle_make_arguments(
        input_make_args,
        force_single_threaded_when_running_tests=False):
    """Special handling for make arguments.

    If force_single_threaded_when_running_tests is True, jobs flags are
    replaced with -j1, because tests cannot handle parallelization.

    If no job flags are present and there are none in the MAKEFLAGS environment
    variable, then make flags are set to the cpu_count, e.g. -j4 -l4.

    :param input_make_args: list of make arguments to be handled
    :type input_make_args: list
    :param force_single_threaded_when_running_tests: self explanatory
    :type force_single_threaded_when_running_tests: bool
    :returns: copied list of make arguments, potentially with some modifications
    :rtype: list
    """
    make_args = list(input_make_args)

    # Get the values for the jobs flags which may be in the make args
    jobs_dict = extract_jobs_flags_values(' '.join(make_args))

    if force_single_threaded_when_running_tests:
        # force single threaded execution when running test since rostest does not support multiple parallel runs
        run_tests = [a for a in make_args if a.startswith('run_tests')]
        if run_tests:
            wide_log('Forcing "-j1" for running unit tests.')
            jobs_dict['jobs'] = 1

    if len(jobs_dict) == 0:
        make_args.extend(jobserver_arguments())
    else:
        if 'jobs' in jobs_dict:
            make_args.append('-j{0}'.format(jobs_dict['jobs']))
        if 'load-average' in jobs_dict:
            make_args.append('-l{0}'.format(jobs_dict['load-average']))

    return make_args


def configure_make_args(make_args, use_internal_make_jobserver):
    """Initialize the internal GNU Make jobserver or configure it as a pass-through

    :param make_args: arguments to be passed to GNU Make
    :type make_args: list
    :param use_internal_make_jobserver: if true, use the internal jobserver
    :type make_args: bool
    :rtype: tuple (final make_args, using makeflags, using cliflags, using jobserver)
    """

    # Configure default jobs options: use all CPUs in each package
    try:
        # NOTE: this will yeild greater than 100% CPU utilization
        n_cpus = cpu_count()
        jobs_flags = {
            'jobs': n_cpus,
            'load-average': n_cpus}
    except NotImplementedError:
        # If the number of cores cannot be determined, limit to one job
        jobs_flags = {
            'jobs': 1,
            'load-average': 1}

    # Get MAKEFLAGS from environment
    makeflags_jobs_flags = extract_jobs_flags(os.environ.get('MAKEFLAGS', ''))
    using_makeflags_jobs_flags = len(makeflags_jobs_flags) > 0
    jobs_flags.update(extract_jobs_flags_values(' '.join(makeflags_jobs_flags)))

    # Extract make jobs flags (these override MAKEFLAGS)
    cli_jobs_flags = extract_jobs_flags(' '.join(make_args))
    using_cli_flags = len(cli_jobs_flags) > 0
    jobs_flags.update(extract_jobs_flags_values(' '.join(cli_jobs_flags)))
    if cli_jobs_flags:
        # Remove jobs flags from cli args if they're present
        make_args = re.sub(' '.join(cli_jobs_flags), '', ' '.join(make_args)).split()

    # Instantiate a jobserver
    if use_internal_make_jobserver:
        initialize_jobserver(
            num_jobs=jobs_flags.get('jobs', None),
            max_load=jobs_flags.get('load-average', None))

    # If the jobserver is supported
    if jobserver_supported():
        jobs_args = []
    else:
        jobs_args = cli_jobs_flags

    return make_args + jobs_args, using_makeflags_jobs_flags, using_cli_flags, jobserver_supported()


def argument_preprocessor(args):
    """Perform processing of argument patterns which are not captured by
    argparse, before being passed to argparse

    :param args: system arguments from which special arguments need to be extracted
    :type args: list
    :returns: a tuple contianing a list of the arguments which can be handled
    by argparse and a dict of the extra arguments which this function has
    extracted
    :rtype: tuple
    """
    # CMake/make pass-through flags collect dashed options. They require special
    # handling or argparse will complain about unrecognized options.
    # NOTE: http://bugs.python.org/issue9334
    args = sys.argv[1:] if args is None else args
    extract_make_args = extract_cmake_and_make_and_catkin_make_arguments
    args, cmake_args, make_args, catkin_make_args = extract_make_args(args)

    # Extract make jobs flags (these override MAKEFLAGS later on)
    jobs_args = extract_jobs_flags(' '.join(args))
    if jobs_args:
        # Remove jobs flags from cli args if they're present
        args = re.sub(' '.join(jobs_args), '', ' '.join(args)).split()

    extras = {
        'cmake_args': cmake_args,
        'make_args': (make_args or []) + (jobs_args or []),
        'catkin_make_args': catkin_make_args,
    }
    return args, extras
