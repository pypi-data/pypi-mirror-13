import os
from setuptools import setup

# Set external files
try:
    from pypandoc import convert
    README = convert('README.md', 'rst')	 
except ImportError:
    README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
    print("warning: pypandoc module not found, could not convert Markdown to RST")

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
    required = f.read().splitlines()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# Not happy about this..
os.system('pip install https://bitbucket.org/lazka/mutagen/get/default.tar.gz') 
setup(
    name='soundscrape',
    version='0.23.0',
    packages=['soundscrape'],
    install_requires=required,
    extras_require={ ':python_version < "3.0"': [ 'wsgiref>=0.1.2', ], },    
    include_package_data=True,
    license='MIT License',
    description='Scrape an artist from SoundCloud',
    long_description=README,
    url='https://github.com/Miserlou/SoundScrape',
    author='Rich Jones',
    author_email='rich@openwatch.net',
    entry_points={
        'console_scripts': [
            'soundscrape = soundscrape.soundscrape:main',
        ]
    },
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
