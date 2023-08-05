#!/usr/bin/env python
''' mkc.project
'''
import sys
import os
from mkc import ROOT_PATH, SRC_PATH, IGNORE_PATH


def create(name, lib_name=None, output_dir=None):
    fmt = {'name': name, 'upper_name': name.upper(),
           'lib_name': lib_name or 'lib%s' % name}
    output_dir = output_dir or name
    if os.path.isdir(output_dir):
        sys.exit('%s directory already exists, exitting.')
    with open(ROOT_PATH) as f:
        root = f.read() % fmt
    with open(SRC_PATH) as f:
        src = f.read() % fmt
    with open(IGNORE_PATH) as f:
        ignore = f.read() % fmt
    src_dir = os.path.join(output_dir, 'src')
    os.mkdir(output_dir)
    os.mkdir(src_dir)
    cmake_root = os.path.join(output_dir, 'CMakeLists.txt')
    cmake_src = os.path.join(src_dir, 'CMakeLists.txt')
    ignore_path = os.path.join(output_dir, '.gitignore')
    cpp_path = os.path.join(src_dir, '%s.cpp' % name)
    h_path = os.path.join(src_dir, '%s.h' % name)
    with open(cmake_root, 'w') as f:
        f.write(root)
    with open(cmake_src, 'w') as f:
        f.write(src)
    with open(ignore_path, 'w') as f:
        f.write(ignore)
    with open(h_path, 'w') as f:
        f.write('#pragma once\n')
    with open(cpp_path, 'w') as f:
        f.write('''#include <iostream>

int main(int argc, char *argv[]) {
    std::cout << "Hello, world!" << std::endl;
}
''')
    print('Constructed project dir at %s' % output_dir)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--lib-name', '-l')
    parser.add_argument('--output-dir', '-o')
    parser.add_argument('name')
    args = parser.parse_args()
    create(args.name, lib_name=args.lib_name, output_dir=args.output_dir)


if __name__ == '__main__':
    main()
