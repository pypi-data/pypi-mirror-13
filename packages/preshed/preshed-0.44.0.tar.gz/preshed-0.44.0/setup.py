#!/usr/bin/env python
from __future__ import division, print_function
import os
import shutil
import subprocess
import sys
import contextlib
from distutils.command.build_ext import build_ext
from distutils.sysconfig import get_python_inc

try:
    from setuptools import Extension, setup
except ImportError:
    from distutils.core import Extension, setup


MAJOR      = 0
MINOR      = 44
MICRO      = 0
ISRELEASED = True
VERSION    = '%d.%d.%d' % (MAJOR, MINOR, MICRO)


PACKAGES = ['preshed']
MOD_NAMES = ['preshed.maps', 'preshed.counter']


if sys.version_info[:2] < (2, 7) or (3, 0) <= sys.version_info[0:2] < (3, 4):
    raise RuntimeError('Python version 2.7 or >= 3.4 required.')


# By subclassing build_extensions we have the actual compiler that will be used which is really known only after finalize_options
# http://stackoverflow.com/questions/724664/python-distutils-how-to-get-a-compiler-that-is-going-to-be-used
compile_options =  {'msvc'  : ['/Ox', '/EHsc'],
                    'other' : ['-O3', '-Wno-strict-prototypes', '-Wno-unused-function']}
link_options    =  {'msvc'  : [],
                    'other' : []}

if sys.platform.startswith('darwin'):
    compile_options['other'].append('-mmacosx-version-min=10.8')
    compile_options['other'].append('-stdlib=libc++')
    link_options['other'].append('-lc++')


class build_ext_options:
    def build_options(self):
        for e in self.extensions:
            e.extra_compile_args = compile_options.get(
                self.compiler.compiler_type, compile_options['other'])
        for e in self.extensions:
            e.extra_link_args = link_options.get(
                self.compiler.compiler_type, link_options['other'])


class build_ext_subclass(build_ext, build_ext_options):
    def build_extensions(self):
        build_ext_options.build_options(self)
        build_ext.build_extensions(self)


# Return the git revision as a string
def git_version():
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(cmd, stdout = subprocess.PIPE, env=env).communicate()[0]
        return out

    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        GIT_REVISION = out.strip().decode('ascii')
    except OSError:
        GIT_REVISION = 'Unknown'

    return GIT_REVISION


def get_version_info():
    # Adding the git rev number needs to be done inside write_version_py(),
    # otherwise the import of preshed.about messes up the build under Python 3.
    FULLVERSION = VERSION
    if os.path.exists('.git'):
        GIT_REVISION = git_version()
    elif os.path.exists(os.path.join('preshed', 'about.py')):
        # must be a source distribution, use existing version file
        try:
            from preshed.about import git_revision as GIT_REVISION
        except ImportError:
            raise ImportError('Unable to import git_revision. Try removing '
                              'preshed/about.py and the build directory '
                              'before building.')
    else:
        GIT_REVISION = 'Unknown'

    if not ISRELEASED:
        FULLVERSION += '.dev0+' + GIT_REVISION[:7]

    return FULLVERSION, GIT_REVISION


def write_version(path):
    cnt = """# THIS FILE IS GENERATED FROM SETUP.PY
short_version = '%(version)s'
version = '%(version)s'
full_version = '%(full_version)s'
git_revision = '%(git_revision)s'
release = %(isrelease)s
if not release:
    version = full_version
"""
    FULLVERSION, GIT_REVISION = get_version_info()

    with open(path, 'w') as f:
        f.write(cnt % {'version': VERSION,
                       'full_version' : FULLVERSION,
                       'git_revision' : GIT_REVISION,
                       'isrelease': str(ISRELEASED)})


def generate_cython(root, source):
    print('Cythonizing sources')
    p = subprocess.call([sys.executable,
                         os.path.join(root, 'bin', 'cythonize.py'),
                         source])
    if p != 0:
        raise RuntimeError('Running cythonize failed')


def is_source_release(path):
    return os.path.exists(os.path.join(path, 'PKG-INFO'))


def clean(path):
    for name in MOD_NAMES:
        name = name.replace('.', '/')
        for ext in ['.so', '.html', '.cpp', '.c']:
            file_path = os.path.join(path, name + ext)
            if os.path.exists(file_path):
                os.unlink(file_path)


@contextlib.contextmanager
def chdir(new_dir):
    old_dir = os.getcwd()
    try:
        os.chdir(new_dir)
        sys.path.insert(0, new_dir)
        yield
    finally:
        del sys.path[0]
        os.chdir(old_dir)


def setup_package():
    root = os.path.abspath(os.path.dirname(__file__))

    if len(sys.argv) > 1 and sys.argv[1] == 'clean':
        return clean(root)

    with chdir(root):
        write_version(os.path.join(root, 'preshed', 'about.py'))

        include_dirs = [
            get_python_inc(plat_specific=True),
            os.path.join(root, 'include')]

        ext_modules = []
        for mod_name in MOD_NAMES:
            mod_path = mod_name.replace('.', '/') + '.cpp'
            ext_modules.append(
                Extension(mod_name, [mod_path],
                    language='c++', include_dirs=include_dirs))

        if not is_source_release(root):
            generate_cython(root, 'preshed')

        setup(
            name='preshed',
            packages=PACKAGES,
            package_data={'preshed': ['*.pyx',
                                      '*.pxd']},
            description='Cython hash table that trusts the keys are pre-hashed',
            author='Matthew Honnibal',
            author_email='matt@spacy.io',
            version=VERSION,
            url='http://github.com/syllog1sm/preshed',
            license='MIT',
            ext_modules=ext_modules,
            classifiers=['Environment :: Console',
                         'Operating System :: OS Independent',
                         'Intended Audience :: Science/Research',
                         'Programming Language :: Cython',
                         'Topic :: Scientific/Engineering'],
            install_requires=['cymem == 1.30'],
            cmdclass = {
                'build_ext': build_ext_subclass},
        )


if __name__ == '__main__':
    setup_package()
