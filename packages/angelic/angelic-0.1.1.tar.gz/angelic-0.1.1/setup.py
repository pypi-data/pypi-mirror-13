import os
from setuptools import setup

# angelic
# An API for daemonization

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "angelic",
    version = "0.1.1",
    description = "An API for daemonization",
    author = "Johan Nestaas",
    author_email = "johannestaas@gmail.com",
    license = "GPLv3+",
    keywords = "",
    url = "https://www.bitbucket.org/johannestaas/angelic",
    packages=['angelic'],
    package_dir={'angelic': 'angelic'},
    long_description=read('README.rst'),
    classifiers=[
        #'Development Status :: 1 - Planning',
        #'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        #'Development Status :: 6 - Mature',
        #'Development Status :: 7 - Inactive',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
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
        'confutil', 'tinylog',
    ],
    entry_points = {
        'console_scripts': [
            'angelic = angelic:main',
        ],
    },
    #package_data = {
        #'angelic': ['catalog/*.edb'],
    #},
    #include_package_data = True,
)
