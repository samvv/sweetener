
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='sweetener',
    version='0.1.0',
    description='A collection of useful algorithms and data structures',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/samvv/Sweetener',
    author='Sam Vervaeck',
    author_email='samvv@pm.me',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='productivity, algorithms, data-structures, development, programming',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.5, <4',
    install_requires=[],
    extras_require={  # Optional
        'dev': [],
        'test': ['pytest'],
    },
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/samvv/Sweetener/issues',
        'Source': 'https://github.com/samvv/Sweetener/',
    },
)
