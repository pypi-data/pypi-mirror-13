import os
from setuptools import setup

# catscan
# Investigate wtf you were working on... where is that damn file?


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="catscan",
    version="0.0.5",
    description=(
        "Investigate wtf you were working on... where is that damn file?"
    ),
    author="Johan Nestaas",
    author_email="johannestaas@gmail.com",
    license="GPLv3+",
    keywords="",
    url="https://www.bitbucket.org/johannestaas/catscan",
    packages=['catscan'],
    package_dir={'catscan': 'catscan'},
    long_description=read('README.rst'),
    classifiers=[
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        ('License :: OSI Approved :: GNU General Public License v3 or later '
         '(GPLv3+)'),
        'Environment :: Console',
        'Environment :: X11 Applications :: Qt',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
    ],
    install_requires=[
        'colorama', 'filemagic',
    ],
    entry_points={
        'console_scripts': [
            'catscan=catscan.scan:main',
            'catscan-install=catscan.install:main',
        ],
    },
    zip_safe=False,
)
