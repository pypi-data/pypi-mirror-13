#! /usr/bin/env python3

"""Converts Cppcheck XML version 2 output to JUnit XML format."""

import argparse
import collections
import os
import sys
from xml.etree import ElementTree

__version__ = '1.0.0'

EXIT_SUCCESS = 0
EXIT_FAILURE = -1


class CppcheckError(object):
    def __init__(self, file, line, message, severity, error_id, verbose):
        """Constructor.

        Args:
            file (str): File error originated on.
            line (int): Line error originated on.
            message (str): Error message.
            severity (str): Severity of the error.
            error_id (str): Unique identifier for the error.
            verbose (str): Verbose error message.
        """
        self.file = file
        self.line = line
        self.message = message
        self.severity = severity
        self.error_id = error_id
        self.verbose = verbose


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Converts Cppcheck XML version 2 to JUnit XML format.\n'
                    'Usage:\n'
                    '\t$ cppcheck --xml-version=2 --enable=all . 2> cppcheck-result.xml\n'
                    '\t$ cppcheck_junit cppcheck-result.xml cppcheck-junit.xml\n',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('input_file', type=str, help='Cppcheck XML version 2 stderr file.')
    parser.add_argument('output_file', type=str, help='JUnit XML output file.')
    return parser.parse_args()


def parse_cppcheck(file_name):
    """Parses a Cppcheck XML version 2 file.

    Args:
        file_name (str): Cppcheck XML file.

    Returns:
        Dict[str, List[CppcheckError]]: Parsed errors grouped by file name.

    Raises:
        IOError: If file_name does not exist (More specifically, FileNotFoundError on Python 3).
        xml.etree.ElementTree.ParseError: If file_name is not a valid XML file.
        ValueError: If unsupported Cppcheck XML version.
    """
    root = ElementTree.parse(file_name).getroot()  # type: ElementTree.Element

    if (root.get('version') is None or
       int(root.get('version')) != 2):
        raise ValueError('Parser only supports Cppcheck XML version 2.  Use --xml-version=2.')

    error_root = root.find('errors')

    errors = collections.defaultdict(list)
    for error_element in error_root:
        location_element = error_element.find('location')  # type: ElementTree.Element
        error = CppcheckError(file=location_element.get('file'),
                              line=int(location_element.get('line')),
                              message=error_element.get('msg'),
                              severity=error_element.get('severity'),
                              error_id=error_element.get('id'),
                              verbose=error_element.get('verbose'))
        errors[error.file].append(error)

    return errors


def generate_test_suite(errors):
    """Converts parsed Cppcheck errors into JUnit XML tree.

    Args:
        errors (Dict[str, List[CppcheckError]]):

    Returns:
        ElementTree.ElementTree: XML test suite.
    """
    test_suite = ElementTree.Element('testsuite')
    test_suite.attrib['errors'] = str(len(errors))
    test_suite.attrib['failures'] = str(0)
    test_suite.attrib['name'] = 'Cppcheck errors'
    test_suite.attrib['tests'] = str(len(errors))
    test_suite.attrib['time'] = str(1)

    for file_name, errors in errors.items():
        test_case = ElementTree.SubElement(test_suite,
                                           'testcase',
                                           name=os.path.relpath(file_name))
        for error in errors:
            ElementTree.SubElement(test_case,
                                   'error',
                                   file=os.path.relpath(error.file),
                                   line=str(error.line),
                                   message='{}: ({}) {}'.format(error.line,
                                                                error.severity,
                                                                error.message))

    return ElementTree.ElementTree(test_suite)


def main():
    """Main function.

    Returns:
        int: Exit code.
    """
    args = parse_arguments()

    try:
        errors = parse_cppcheck(args.input_file)
    except ValueError as e:
        print(str(e))
        return EXIT_FAILURE
    except IOError as e:
        print(str(e))
        return EXIT_FAILURE
    except ElementTree.ParseError as e:
        print('{} is a malformed XML file. Did you use --xml-version=2?\n{}'.format(
            args.input_file, e))
        return EXIT_FAILURE

    if len(errors) > 0:
        tree = generate_test_suite(errors)
        tree.write(args.output_file, encoding='utf-8', xml_declaration=True)

    return EXIT_SUCCESS

if __name__ == '__main__':
    sys.exit(main())
