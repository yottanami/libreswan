#!/usr/bin/env python3

# Print a test result summary gathered by scanning the OUTPUT.
#
# Copyright (C) 2015 Andrew Cagney <cagney@gnu.org>
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See <http://www.fsf.org/copyleft/gpl.txt>.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.

import argparse
import sys
from fab import testsuite
from fab import logutil

def main():

    parser = argparse.ArgumentParser(description="list all tests in the form: <test> [ <directory> ] [ <result> <details...> ]")
    parser.add_argument("--verbose", "-v", action="count", default=0)

    parser.add_argument("--print-directory", action="store_true")
    parser.add_argument("--print-name", action="store_true")
    parser.add_argument("--print-result", action="store_true")

    parser.add_argument("--list-ignored", action="store_true",
                        help="include ignored tests in the list")
    parser.add_argument("--list-untested", action="store_true",
                        help="include untested tests in the list")

    parser.add_argument("directories", metavar="TEST-DIRECTORY", nargs="+",
                        help=("Either a testsuite (only one) or test directory"))
    # Note: this argument serves as documentation only.  The
    # TEST-DIRECTORY argument always consume all remaining parameters.
    parser.add_argument("baseline", metavar="BASELINE-DIRECTORY", nargs="?",
                        help=("An optional testsuite directory containing"
                              " results from a previous test run"))
    testsuite.add_arguments(parser)
    logutil.add_arguments(parser)

    args = parser.parse_args()

    logutil.config(args)
    logger = logutil.getLogger("kvmresults")

    # The option -vvvvvvv is a short circuit for these; make
    # re-ordering easy by using V as a counter.
    v = 0
    args.print_directory = args.print_directory or args.verbose > v
    args.print_name = args.print_name or args.verbose > v
    v += 1
    args.list_untested = args.list_untested or args.verbose > v ; v += 1
    args.list_ignored = args.list_ignored or args.verbose > v ; v += 1

    # By default print the relative directory path.
    if not args.print_directory and not args.print_name:
        args.print_directory = True

    # If there is more than one directory then the last might be the
    # baseline.  Try loading it as a testsuite (baselines are
    # testsuites) to see if that is the case.
    basetests = None
    tests = None
    if len(args.directories) > 1:
        # Perhaps the last argument is the baseline?
        basetests = testsuite.load(logger, args.directories[-1])
        if basetests:
            logger.debug("basetests loaded from '%s'", basetests.directory)
            args.directories.pop()
    tests = testsuite.load_testsuite_or_tests(logger, args.directories)
    logger.debug("basetests=%s", basetests)
    logger.debug("tests=%s", tests)
    # And check
    if not tests:
        logger.error("Invalid testsuite or test directories")
        return 1

    # When an explicit list of directories was specified always print
    # all of them (otherwise, tests seem to get lost).
    if isinstance(tests, list):
        args.list_untested = True

    # Preload the baseline.  This avoids re-scanning the TESTLIST and,
    # when errors, printing those repeatedly.  Also, passing the full
    # baseline to Test.results() lets that function differentiate
    # between a baseline missing results or being entirely absent.
    baseline = None
    if basetests:
        baseline = {}
        for test in basetests:
            baseline[test.name] = test

    for test in tests:

        # Filter out tests that are being ignored?
        ignore = testsuite.ignore(test, args)
        if ignore and not args.list_ignored:
            continue

        # Filter out tests that have not been run?
        result = None
        if not ignore:
            result = test.result(baseline)
            if not result and not args.list_untested:
                continue

        sep = ""

        if args.print_name:
            print(sep, end="")
            print(test.name, end="")
            sep = " "

        if args.print_directory:
            print(sep, end="")
            print(test.directory, end="")
            sep = " "

        if ignore:
            print(sep, end="")
            print("ignored", ignore, end="")
            sep = " "

        if result:
            print(sep, end="")
            print(result, end="")
            sep = " "

        print()

        sys.stdout.flush()

    return 0


if __name__ == "__main__":
    sys.exit(main())
