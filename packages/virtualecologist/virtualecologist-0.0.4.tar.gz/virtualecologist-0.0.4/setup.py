from setuptools import setup, find_packages
from sys import version

if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

setup(
    name = "virtualecologist",
    version = "0.0.4",
    #packages = find_packages(),
    description = "Optimize transect length in ecological surveys.",

    packages = ['virtualecologist'],
      #long_description="""""",
    #scripts = ['virtual_ecologist.py'],

    # installed or upgraded on the target machine
    install_requires = ["csv", "pandas", "numpy",\
    "scipy", "matplotlib", "prettytable"],

    include_package_data = True,

    package_data = {
        # include *.txt or *.rst files:
        '': ['*.txt', '*.rst'],
        # include *.msg files:
        '': ['*.msg'],
        # include subdirectory containing example datasets:
        'virtualecologist': ['data/*.csv'],
        },


    # metadata for PyPi
    author = "Ray",
    author_email = "rblick.ecol@gmail.com",
    keywords = ["ecology", "environment", "conservation", "modelling"],
    url = "https://github.com/rayblick/Virtual-Ecologist",   
    

    # Trove Classifiers
    classifiers=[  
        #'Development Status :: 1 - Planning',
        #'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        #'...'  
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        #'Programming Language :: Python :: 2 :: Only',#
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
          ],
)
