import os
from setuptools import setup

# tasque
# Command-line task handler
from tasque import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="tasque",
    version=__version__,
    description="Command-line task handler",
    author="Johan Nestaas",
    author_email="johannestaas@gmail.com",
    license="GPLv3+",
    keywords="",
    url="https://www.bitbucket.org/johannestaas/tasque",
    packages=['tasque'],
    package_dir={'tasque': 'tasque'},
    long_description=read('README.rst'),
    classifiers=[
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        (
            'License :: OSI Approved :: GNU General Public License v3 or later '
            '(GPLv3+)'
        ),
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
        'terminaltables', 'colorama', 'confutil', 'shellify', 'pyyaml',
        'requests', 'requests_oauthlib',
    ],
    entry_points={
        'console_scripts': [
            # 'tasque=tasque:main',
            'tasque-shell=tasque.shell:main',
            'tasque-install=tasque:install_config',
        ],
    },
    zip_safe=False,
    # package_data={
    # 'tasque': ['catalog/*.edb'],
    # },
    # include_package_data=True,
)
