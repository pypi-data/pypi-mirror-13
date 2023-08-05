from __future__ import print_function
from xml.etree import cElementTree as ET
from datetime import datetime
from argparse import ArgumentParser


SKIPPED_ELEMENTS = ('doc', 'status', 'arguments', 'tags')
WIDTH = 120


def popt(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    print_double_line()
    print_children(root, 0)
    print_double_line()


def print_line():
    print('{}'.format('-' * WIDTH))


def print_double_line():
    print('{}'.format('=' * WIDTH))


def print_children(element, indent):
    if element.tag == 'statistics':
        return
    print_element(element, indent)
    for child in element:
        print_children(child, indent + 2)


def print_element(element, indent):
    {'robot': print_robot,
     'kw': print_kw,
     'test': print_test,
     'suite': print_suite,
     'msg': print_msg,
     'arg': print_arg,
     'tag': print_tag}.get(element.tag, print_generic_element)(element, indent)


def print_robot(element, indent):
    for key, value in element.attrib.iteritems():
        print('{}{}: {}'.format(' ' * indent, key, value))


def print_msg(element, indent):
    timestamp = element.get('timestamp').split()[-1]
    level = element.get('level')
    if 'Arguments' in element:
        text = 'Arguments: {}'.format(element.get('Arguments'))
    elif 'Return' in element:
        text = 'Return: {}'.format(element.get('Return'))
    else:
        text = indent_lines(element.text, indent + len(timestamp) + 2 + 5 + 2)
    print('{:>{indent}}  {:<5}  {}'.format(timestamp, level, text, indent=indent + len(timestamp)))


def indent_lines(text, indent):
    indent_spaces = ' ' * indent
    return indent_spaces.join(line for line in text.splitlines(True))


def print_kw(element, indent):
    print_suite_test_kw(element, indent)


def print_test(element, indent):
    print_line()
    print_suite_test_kw(element, indent)


def print_suite(element, indent):
    print_double_line()
    print_suite_test_kw(element, indent)


def print_arg(element, indent):
    print_text_element(element, indent, 'arg')


def print_tag(element, indent):
    print_text_element(element, indent, 'tag')


def print_text_element(element, indent, element_name):
    print('{:>{indent}} {}'.format(element_name + ':', element.text, indent=(indent + len(element_name + ':'))))


def print_suite_test_kw(element, indent):
    status = element.find('status')
    name = element.get('name')
    len_of_first_part = indent + len(name)
    padding = ' ' * (WIDTH - 26 - len_of_first_part)
    print('{:>{indent}}{}{}  {}'.format(name, padding,
                                        status.get('status'), format_timestamps(status),
                                        indent=indent + len(name)))


def format_timestamps(status):
    starttime = status.get('starttime')
    endtime = status.get('endtime')
    start_dt = datetime.strptime(starttime + '000', '%Y%m%d %H:%M:%S.%f')
    end_dt = datetime.strptime(endtime + '000', '%Y%m%d %H:%M:%S.%f')
    duration = end_dt - start_dt
    return '{}  {:0>2}.{:0<3}'.format(starttime.split()[-1],
                                      duration.seconds, duration.microseconds / 1000)


def empty_format_timestamps(status):
    return ''


def print_generic_element(element, indent):
    text = element.text.strip() if element.text is not None else ''
    if element.tag not in SKIPPED_ELEMENTS:
        print('{:>{indent}} {} {}'.format(element.tag, element.attrib, text,
                                          indent=indent + len(element.tag)))


def read_arguments():
    p = ArgumentParser(description='Convert Robot Framework output.xml to human-readable textual log')
    p.add_argument('filename', type=str, help='Path to output.xml file')
    p.add_argument('--skip-timestamps', '-T', action='store_true', help='Omit all timestamps from textual log (helps in diffing logs)')
    p.add_argument('--width', type=int, help='Display width in characters. Default is 120.')
    args = p.parse_args()
    if args.skip_timestamps:
        global format_timestamps
        format_timestamps = empty_format_timestamps
    if args.width:
        global WIDTH
        WIDTH = args.width
    popt(args.filename)


if __name__ == '__main__':
    read_arguments()