#!/usr/bin/env python3

import sys, os, re, glob, subprocess, pytest

__version__ = '0.5.0'

def main():
    """
    Discover and run the tests for this package.
    """
    cli_args = sys.argv[1:]
    repo_dir = discover_repository()
    test_dir, tests = discover_tests(repo_dir)
    cli_args, tests = pick_tests(cli_args, tests)
    success = run_pytest(repo_dir, test_dir, cli_args, tests)
    sys.exit(success)

def discover_repository():
    """
    Return the path the root of the git repository containing the current 
    working directory.

    This is important because everything else in this script will orient itself 
    relative to this directory.  If the git repository can't be found for any 
    reason (e.g. the current working directory isn't part of a repository, git 
    isn't installed, etc.) a ValueError will be raised.
    """
    try: 
        with open(os.devnull, 'w') as devnull:
            command = 'git', 'rev-parse', '--show-toplevel'
            stdout = subprocess.check_output(command, stderr=devnull)
            path = stdout.strip()

    except subprocess.CalledProcessError:
        raise ValueError("couldn't find git repository")

    return path.decode('utf8')

def discover_tests(repo_dir):
    """
    Return the names of all the test scripts known to pytest.
    """

    # Find the directory where the tests should be relative to the root of the 
    # repository.

    test_dir = os.path.join(repo_dir, 'tests')

    if not os.path.isdir(test_dir):
        raise ValueError("couldn't find tests/ directory")

    # Run pytest with the ``--collect-only`` flag to generate a list of all the 
    # modules that would be run by pytest.

    with open(os.devnull, 'w') as null:
        command = 'py.test', '--collect-only', test_dir
        stdout = subprocess.check_output(command, stderr=null).decode('utf-8')

    # Parse the output to create a list of the files that will be tested.

    test_paths = []
    test_path_pattern = re.compile("<Module '(.*)'>")

    for line in stdout.split('\n'):
        test_path_match = test_path_pattern.match(line.strip())
        if test_path_match:
            test_paths.append(test_path_match.group(1))

    return test_dir, test_paths

def pick_tests(cli_args, tests):
    """
    Return the tests the user actually wants to run, considering the given 
    command line arguments.

    Each discovered test is compared to each argument the user specified.  If 
    any argument is a substring of a test name, that test will be included in 
    the returned list.  For example, if one of the arguments is 'foo' and a 
    test named 'test_foo.py' exists, that test will be included.  If no tests 
    are matched, the complete list of tests is returned.  So unless the user 
    specifies otherwise, all the tests will be run.  Also returned is a list of 
    all the arguments that didn't match the name of a test.
    """
    pytest_args = cli_args[:]
    matched_tests = []

    for test in tests:
        for arg in cli_args:
            if arg in test:
                matched_tests.append(test)
                pytest_args.remove(arg)

    return pytest_args, matched_tests or tests
    
def sort_tests(tests):
    """
    Determine the order in which the tests should be run.

    By default, all the tests have a numeric prefix which indicates the order 
    they're meant to be run in, so we can simply sort the tests numerically.
    """
    return sorted(tests)

def run_pytest(repo_dir, test_dir, cli_args, tests):
    """
    Run pytest in the right directory.  
    
    Use the arguments specified on the command line on top of my preferred set 
    of default arguments.  My default arguments stop on the first failure, 
    collect coverage data, and turn on color output.
    """
    args = [
        '-x',
        '--color', 'yes',
        '--cov', deduce_package_name(repo_dir),
        '--cov-report', 'html',
    ]
    args += cli_args
    args += sort_tests(tests)

    from signal import signal, SIGPIPE, SIG_DFL
    signal(SIGPIPE, SIG_DFL)

    os.chdir(test_dir)
    return pytest.main(args)

def deduce_package_name(repo_dir):
    """
    Figure out what the name of the package being tested.

    This information is needed by coverage.  It is deduced by walking up the 
    directory tree looking for the first directory with an ``__init__.py`` 
    file.  When such a directory is found, its name is immediately returned.  
    If no suitable directory  is found, a ValueError is raised.
    """

    egg_info = glob.glob(os.path.join(repo_dir, '*.egg-info'))

    if len(egg_info) == 0:
        raise ValueError("couldn't find any *.egg-info files.  Did you run 'pip install'?")
    if len(egg_info) > 1:
        raise ValueError("found multiple *.egg-info files, couldn't deduce package name.")

    return os.path.splitext(os.path.basename(egg_info[0]))[0]

