''' mkc

Initialize a C++ project.
'''
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(ROOT_DIR, 'templates')
ROOT_PATH = os.path.join(TEMPLATE_DIR, 'CMakeLists_root.temp')
SRC_PATH = os.path.join(TEMPLATE_DIR, 'CMakeLists_src.temp')
IGNORE_PATH = os.path.join(TEMPLATE_DIR, 'gitignore.temp')


def main():
    from .project import main as project_main
    project_main()


if __name__ == '__main__':
    main()
