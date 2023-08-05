from distutils.core import setup, Extension

with open('README') as file:
    readme = file.read()

setup(
    name             = 'ufal.parsito',
    version          = '1.1.0.1',
    description      = 'Bindings to Parsito library',
    long_description = readme,
    author           = 'Milan Straka',
    author_email     = 'straka@ufal.mff.cuni.cz',
    url              = 'http://ufal.mff.cuni.cz/parsito',
    license          = 'MPL 2.0',
    py_modules       = ['ufal.parsito'],
    ext_modules      = [Extension(
        'ufal_parsito',
        ['parsito/parsito.cpp', 'parsito/parsito_python.cpp'],
        language = 'c++',
        include_dirs = ['parsito/include'],
        extra_compile_args = ['-std=c++11', '-fvisibility=hidden', '-w'])],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: C++',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries'
    ]
)
