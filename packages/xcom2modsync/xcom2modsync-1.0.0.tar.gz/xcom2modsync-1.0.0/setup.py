import os
from setuptools import setup, find_packages
from xcom2modsync import __version__


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()

setup(
    name='xcom2modsync',
    version=__version__,
    description='Install Steam Workshop mods into XCOM2 mod directory.',
    author='Edvin Malinovskis',
    author_email='github@edvin.io',
    url='https://gitlab.com/nCrazed/XCOM2-Mod-Synchronizer',
    download_url='https://gitlab.com/nCrazed/XCOM2-Mod-Synchronizer/repository/archive.tar.gz?ref=%s' % __version__,
    license='MIT',
    keywords=['xcom2', 'mods'],
    packages=find_packages(),
    install_requires=['docopt'],
    entry_points={'console_scripts': ['xcom2modsync = xcom2modsync:main']},
)
