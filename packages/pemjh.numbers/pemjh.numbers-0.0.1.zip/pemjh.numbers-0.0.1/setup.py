""" Setup file for install and test. Taken from:
https://pythonhosted.org/an_example_pypi_project/setuptools.html
for pytest:
https://pytest.org/latest/goodpractises.html
for tox:
https://testrun.org/tox/latest/example/basic.html#
integration-with-setuptools-distribute-test-commands"""

import os
from setuptools import setup
from setuptools import find_packages
from setuptools.command.test import test as TestCommand


def read(fname):
    """ Open a local file and return as string.
    Used for populating descriptions and arguments from file. """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


class Tox(TestCommand):
    """ Hook into running Tox for testing. """
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def __init__(self, dist):
        TestCommand.__init__(self, dist)
        self.tox_args = None
        self.test_args = []
        self.test_suite = True

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        import virtualenv
        from os.path import dirname

        ve_path = dirname(virtualenv.__file__)
        try:
            os.environ['PYTHONPATH'] += ';{0}'.format(ve_path)
        except:
            os.environ['PYTHONPATH'] = ve_path

        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        else:
            args = []
        tox.cmdline(args=args)


def main():
    """ Run the setup. """
    setup(
        name="pemjh.numbers",
        version="0.0.1",
        author="Matthew Hussey",
        author_email="matthew.hussey@googlemail.com",
        description=("Numeric helper functions for Project Euler Challenges."),
        license="None, private use by myself only",
        keywords="python",
        url="none.non",
        packages=find_packages(where='src'),
        package_data={},
        package_dir={'': 'src'},
        install_requires=[],
        long_description=read("README"),
        classifiers=[
            "Development Status :: 1 - Planning"],
        tests_require=['tox'],
        cmdclass={"test": Tox},
    )

if __name__ == "__main__":
    main()
