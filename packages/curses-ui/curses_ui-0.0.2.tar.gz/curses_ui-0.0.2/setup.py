"""
curses_ui
"""

from setuptools import setup, find_packages

setup(
    name='curses_ui',
    version='0.0.2',
    author='Jordon Scott',
    author_email='jordon@novatek.com.au',
    packages=find_packages(exclude=["tests.*", "tests"]),
    scripts=[],
    url='https://github.com/jordonsc/python-curses-ui',
    license='MIT',
    description='Curses UI with native window management and keyboard support',
    setup_requires=[
    ],
    install_requires=[
    ],
)
