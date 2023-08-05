"""Install the `projkit` module."""
from setuptools import setup


def get_requirements(requirements_file):
    """Read requirements from a text file."""
    with open(requirements_file) as f:
        return [line.strip()
                for line in f.readlines()
                if not line.startswith("#")]


setup(
    name="umich-projkit",
    version="2.0.1",
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

    install_requires=get_requirements("requirements.txt"),
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)
