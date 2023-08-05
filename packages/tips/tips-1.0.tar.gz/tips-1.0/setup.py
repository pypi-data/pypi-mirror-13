import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

config = {
        'description': 'A tips per day tracker and displayer',
        'long_description': read('README'),
        'author': 'TiredSounds',
        'url': 'github.com/TiredSounds/tips',
        'download_url': 'github.com/TiredSounds/tips',
        'author_email': 'tiredsounds17@gmail.com',
        'version': '1.0',
        'packages': ['tips'],
        'install_requires': ['backports.shutil_get_terminal_size'],
        'entry_points': {
            'console_scripts': ['tips = tips.tips:main']
            },
        'name': 'tips'
}

setup(**config)
