setuptools.autocythonize
========================

Setuptools keyword for generating an extensions list of cython modules,
similar to find_packages, but also cythonizing the pyx files, and appending
them to the ext_modules list.

Quickstart
----------

In your setup.py:

.. code-block:: python

    from setuptools import setup, Extension

    setup(
        ...
        # Your non cython extensions: leave blank if only using cython
        ext_modules=[Extension("*", ["*.cpp"])]
        setup_requires=['cython', 'setuptools.autocythonize'],
        # These argument will be loaded into the Extension objects for each
        # pyx file we find, this also takes the same arguments of where, include, exclude
        # just like setuptools find_packages
        auto_cythonize={
            "compile_args": ['-std=gnu99', '-ffast-math', '-w'],
            "libraries": ['opengl32', 'glu32','glew32'],
            "includes": kivy.get_includes()
        }
        ...
    )

On the commandline:

.. code-block:: bash

    python setup.py install

Your cython files will be auto detected, passed to the cythonize command
and the c file extension objects will be appended to ext_modules for this
distribution.

You can also explictly cythonize your auto detected files and even "clean" the
intermediary c files.

.. code-block:: bash

    python setup.py cythonize --clean

Enjoy Autocythonizeing!
