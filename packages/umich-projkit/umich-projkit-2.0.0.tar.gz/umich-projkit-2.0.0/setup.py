"""Install the `projkit` module."""
from setuptools import setup

setup(
    name="umich-projkit",
    version="2.0.0",
    author="Waleed Khan",
    author_email="wkhan@umich.edu",
    description=("Automatically grade projects for your CS course. "
                 "Written for University of Michigan's EECS 281 -- "
                 "Data Structures and Algorithms."),
    url="https://gitlab.eecs.umich.edu/eecs281/projkit",

    packages=["projkit"],
    entry_points="""
    [console_scripts]
    projkit=projkit.commands:cli
    """,

    install_requires=[],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)
