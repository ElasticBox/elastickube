#!/usr/bin/env python
"""
Copyright 2016 ElasticBox All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import argparse
import logging
import os
import sys

import unittest2
import xmlrunner


def get_parser():
    parser = argparse.ArgumentParser(description='Run the ElasticKube tests suite.')
    parser.add_argument(
        '-v',
        '--verbose',
        dest='verbose',
        action='store_true',
        help='Set verbosity value to 2.')

    parser.add_argument(
        '-d',
        '--debug',
        dest='debug',
        action='store_true',
        help='Set logging value to DEBUG.')

    parser.add_argument(
        '--junitxml',
        dest='junitxml',
        default='',
        help='Output result in file')

    parser.add_argument('files', nargs='*')
    return parser


def run_tests(test_files, verbose=False, debug=False, output=None):
    suite = unittest2.TestSuite()

    # Load tests
    discovery_folder = os.path.dirname(os.path.realpath(__file__))
    if test_files:
        for test_file in test_files:
            search_folder = os.path.join(discovery_folder, test_file)
            pattern = '*test*.py'

            if os.path.isfile(search_folder):
                pattern = os.path.basename(test_file)
                search_folder = os.path.dirname(search_folder)

            tests = unittest2.loader.defaultTestLoader.discover(
                search_folder,
                pattern=pattern)

            suite.addTest(tests)
    else:
        tests = unittest2.loader.defaultTestLoader.discover(
            discovery_folder,
            pattern='*test*.py')

        suite.addTest(tests)

    # Set output verbosity
    verbosity = 1
    if verbose:
        verbosity = 2

    # Set logging level
    if debug:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

    # Run tests
    if output:
        with open(output, 'wb') as output_file:
            test_result = xmlrunner.XMLTestRunner(verbosity=verbosity, output=output_file).run(suite)
    else:
        test_result = unittest2.TextTestRunner(verbosity=verbosity).run(suite)

    if not test_result.wasSuccessful():
        sys.exit(1)


def main():
    parser = get_parser()
    args = parser.parse_args()
    run_tests(args.files, args.verbose, args.debug, args.junitxml)


if __name__ == '__main__':
    main()
