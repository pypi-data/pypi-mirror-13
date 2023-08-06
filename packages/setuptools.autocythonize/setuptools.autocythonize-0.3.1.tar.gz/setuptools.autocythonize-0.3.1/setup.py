from setuptools import setup, find_packages

setup(
    name='setuptools.autocythonize',
    description='''A setuptools util for generating an extensions list of cython modules, similar to find_packages, but also cythonizing the pyx files''',
    author='Kyle Rockman',
    author_email='kyle.rockman@mac.com',
    long_description="https://github.com/rocktavious/setuptools.autocythonize",
    url="https://github.com/rocktavious/setuptools.autocythonize",
    setup_requires=['pyversion'],
    auto_version=True,
    packages=find_packages(),
    namespace_packages=["setuptools"],
    entry_points={
        'distutils.setup_keywords':[
            "auto_cythonize = setuptools.autocythonize:auto_cythonize",
        ],
        'distutils.commands': [
            "cythonize = setuptools.autocythonize:CythonizeCommand",
        ]
    }
)
