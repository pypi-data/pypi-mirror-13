__all__ = ["cythonize_extensions"]
import os
from setuptools import Command, Extension, find_packages
try:
    from Cython.Build import cythonize as _cythonize
    from Cython.Distutils import build_ext
    have_cython = True
except ImportError:
    have_cython = False

def clean_extensions(extensions):
    for ext in extensions:
        for filename in ext.sources:
            filepath, ext = os.path.splitext(filename)
            c_filepath = filepath + ".c"
            if os.path.isfile(c_filepath):
                os.remove(c_filepath)

def cythonize(extensions, clean_existing):
    if have_cython:
        if clean_existing:
            clean_extensions(extensions)
        return _cythonize(extensions)
    else:
        for ext in extensions:
            ext.sources = [os.path.splitext(f)[0] + ".c" for f in ext.sources]
        return extensions

def find_cython_modules(root, found_modules):
    modules = {}
    for module in found_modules:
        filepath = os.path.join(root,os.path.sep.join(module.split(".")))
        for found_file in os.listdir(filepath):
            filename, ext = os.path.splitext(found_file)
            if ext != ".pyx":
                continue
            modules[module + "." + filename] = [os.path.join(filepath, found_file)]
    return modules

def generate_cython_extensions(modules, includes, compile_args, libraries):
    extensions = []
    for module_name, module_files in modules.items():
        ext = Extension(module_name, module_files, includes,
                        extra_compile_args=compile_args,
                        libraries=libraries)
        if os.environ.get('READTHEDOCS', None) == 'True':
            ext.pyrex_directives = {'embedsignature': True}
        extensions.append(ext)
    return extensions

def find_cython_extensions(where=".",
                           exclude=(),
                           include=("*",),
                           compile_args=[],
                           libraries=[],
                           includes=[],
                           clean_existing=False):
    found_modules = find_packages(where=where, exclude=exclude, include=include)
    found_cython_modules = find_cython_modules(where, found_modules)
    cython_extensions = generate_cython_extensions(found_cython_modules, includes, compile_args, libraries)
    return cythonize(cython_extensions, clean_existing)

def auto_cythonize(dist, attr, value):
    assert attr == 'auto_cythonize'
    if not dist.ext_modules:
        dist.ext_modules = []
    if value:
        dist.ext_modules += find_cython_extensions(**value)


class CythonizeCommand(Command):
    description = 'Cythonize PYX sources'
    user_options = [('clean', 'c', "Remove the cythonized c files before cythonizing again")]
    boolean_options = ['clean']

    def initialize_options(self):
        self.clean = 0

    def finalize_options(self):
        pass

    def run(self):
        self.distribution.auto_cythonize["clean_existing"] = bool(self.clean)
        self.distribution.ext_modules += find_cython_extensions(**self.distribution.auto_cythonize)
