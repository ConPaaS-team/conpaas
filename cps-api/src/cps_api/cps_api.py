#!/usr/bin/env python

#
#  Tool to extract ConPaaS HTTP APIs from source code
#
#  author: Yann.Radenac@inria.fr
#  date: started on 2013-10-22
#

from argparse import ArgumentParser
import ast
import datetime
import fnmatch
import os
import sys

from api_extractor import APIExtractor


def pseudo_relative_name(path, mark):
    """ Return the given path shorten until a directory name contains a
    given mark (i.e. matches a substring)."""
    short_rel_path = ''
    condition = True
    head = os.path.abspath(path)
    while condition:
        head, tail = os.path.split(head)
        condition = tail != '' and not fnmatch.fnmatch(tail, "*%s*" % mark)
        if short_rel_path:
            short_rel_path = os.path.join(tail, short_rel_path)
        else:
            short_rel_path = tail
    return short_rel_path


def conpaas_path_name(path):
    return pseudo_relative_name(path, "conpaas")


def indent_except_sections(text):
    """Indent text except if restructured text section definition lines."""
    ret_text = []
    previous_line = None
    for line in text.split('\n'):
        if len(set(line)) == 1 \
                and previous_line is not None \
                and len(line) >= len(previous_line) \
                and len(previous_line) > 1:
            ret_text.append(previous_line)  # un-indented section title
            ret_text.append(line)  # un-indented section adornment
            previous_line = None
        else:
            if previous_line is not None:
                ret_text.append('  ' + previous_line)  # indentation
            previous_line = line
    if previous_line is not None:
        ret_text.append('  ' + previous_line)
    return '\n'.join(ret_text)


def gen_functions_doc(functions, file_as_title=False):
    file_title = None
    functions_doc = []
    for func in functions:
        if file_as_title:
            basename = os.path.basename(func['source_file'])
            func_file, _ = os.path.splitext(basename)
            if func_file != file_title:
                file_title = func_file
                functions_doc.append('\n')
                functions_doc.append('-' * len(file_title))
                functions_doc.append('\n')
                functions_doc.append(file_title)
                functions_doc.append('\n')
                functions_doc.append('-' * len(file_title))
                functions_doc.append('\n')
        functions_doc.append('\n')
        func_doc = gen_func_doc(func)
        functions_doc.extend(func_doc)
    return functions_doc


def gen_func_doc(func):
    doc = []
    if len(func['names']) == 1:
        name, methods = func['names'][0]
        doc.append(name)
        doc.append('\n')
        doc.append('=' * len(name))
        doc.append('\n')
        doc.append('HTTP methods')
        doc.append('\n')
        doc.append('  %s' % methods)
        doc.append('\n')
    else:
        all_names = ''
        for name, methods in func['names']:
            all_names += name + " " + methods + " "
        doc.append(all_names)
        doc.append('\n')
        doc.append('-' * len(all_names))
        doc.append('\n')

    doc.append('Source file')
    doc.append('\n')
    doc.append('  %s' % conpaas_path_name(func['source_file']))
    doc.append('\n')
    if 'certificate' in func:
        doc.append('* ' + func['certificate'])
        doc.append('\n')
    doc.append('Description')
    doc.append('\n')
    #fun_doc = func['doc']
    fun_doc = indent_except_sections(func['doc'])
    #doc.append('\n  '.join(fun_doc.split('\n')))
    doc.append(fun_doc)
    doc.append('\n')
    return doc


def gen_classes_doc(classes):
    classes_doc = []
    for cpsclass in classes:
        classes_doc.append('\n')
        class_doc = gen_class_doc(cpsclass)
        classes_doc.extend(class_doc)
    return classes_doc


def gen_class_doc(cpsclass):
    class_doc = []
    if cpsclass['entries']:
        class_name = cpsclass['name']
        class_doc.append('-' * len(class_name))
        class_doc.append('\n')
        class_doc.append(class_name)
        class_doc.append('\n')
        class_doc.append('-' * len(class_name))
        class_doc.append('\n')
        class_doc.append('Source file')
        class_doc.append('\n')
        class_doc.append('  %s' % conpaas_path_name(cpsclass['source_file']))
        class_doc.append('\n')
        if cpsclass['extends']:
            class_doc.append('Extends')
            class_doc.append('\n')
            for extclass in cpsclass['extends']:
                class_doc.append('  %s' % extclass)
            class_doc.append('\n')
        functions_doc = gen_functions_doc(cpsclass['entries'])
        class_doc.extend(functions_doc)
    return class_doc


def gen_doc(visitor):
    doc = []
    if visitor.all_functions_doc:
        # public entries defined outside any class (case of ConPaaS director)
        functions_doc = gen_functions_doc(visitor.all_functions_doc,
                                          file_as_title=True)
        doc.extend(functions_doc)

    if visitor.classes_doc:
        # public entries defined inside classes (case of ConPaaS managers and agents)
        doc.extend(gen_classes_doc(visitor.classes_doc))

    return doc


def print_doc(visitor):
    doc = gen_doc(visitor)
    print ''.join(doc)


def print_title(root_dir, title):
    print "=" * len(title)
    print title
    print "=" * len(title)
    print
    print "Source code root directory: %s" % conpaas_path_name(root_dir)


def print_toc():
    print
    print '.. contents::'
    print


def print_date():
    print
    print 'This document was generated on %s' % datetime.date.today()
    print


def class_comparator():
    def compare(class1, class2):
        class1_name = class1['name']
        class2_name = class2['name']
        if class1_name in class2['extends']:
            return 1
        if class2_name in class1['extends']:
            return -1
        if class1_name < class2_name:
            return -1
        if class1_name > class2_name:
            return 1
        return 0
    return compare


def sort_entries(visitor):
    if visitor.all_functions_doc:
        entries = visitor.all_functions_doc
        entries = sorted(entries, key=lambda k: k['source_file'] + k['names'][0][0])
        visitor.all_functions_doc = entries
    if visitor.classes_doc:
        # sort classes
        sorted_classes = visitor.classes_doc
        sorted_classes = sorted(sorted_classes, cmp=class_comparator())
        visitor.classes_doc = sorted_classes
        # sort entries inside classes
        for class_doc in visitor.classes_doc:
            entries = class_doc['entries']
            entries = sorted(entries, key=lambda k: k['names'][0][0])
            class_doc['entries'] = entries


def get_source_files(root_dir):
    if not os.path.isdir(root_dir):
        raise Exception("Error: %s is not a readable directory." % root_dir)
    py_src_files = []
    for root, _dirnames, filenames in os.walk(root_dir):
        for filename in fnmatch.filter(filenames, '*.py'):
            py_src_files.append(os.path.join(root, filename))
    return py_src_files


def main():
    # Parse command line argument
    parser = ArgumentParser(description='Tool to extract ConPaaS HTTP APIs from source code')
    parser.add_argument('DIR', help='root directory of source code to parse')
    parser.add_argument('--title', default='ConPaaS API',
                        help='Title of the extracted API.')
    args = parser.parse_args(sys.argv[1:])
    root_dir = args.DIR

    py_src_files = get_source_files(root_dir)
    visitor = APIExtractor()
    for src_file in py_src_files:
        source_file = open(src_file)
        source = source_file.read()
        source_file.close()
        mod = ast.parse(source)
        visitor.source_file = src_file
        visitor.visit(mod)

    sort_entries(visitor)

    print_title(root_dir, args.title)
    print_date()
    print_toc()
    print_doc(visitor)


if __name__ == '__main__':
    main()
