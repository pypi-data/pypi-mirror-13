from setuptools import setup

import waechter

setup(
    packages=["waechter", ],
    name=waechter.__title__,
    version=waechter.__version__,
    author='Lukas Rist',
    author_email='glaslos@gmail.com',
    license='GPL 3',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
    ],
    url='https://github.com/glaslos/waechter',
    description='Job Scheduling Helper',
    test_suite='nose.collector',
    tests_require="nose",
    zip_safe=False,
    install_requires=open('requirements.txt').read().splitlines(),
)
