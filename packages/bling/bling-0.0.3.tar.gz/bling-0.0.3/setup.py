import setuptools

from setuptools.command.test import test as TestCommand
import sys

class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)
        

setuptools.setup(
    name="bling",
    version="0.0.3",
    url="https://github.com/ungood/bling",

    author="Jason Walker",
    author_email="ungood@onetrue.name",

    description="Bling is a simple languagee for controlling LED strips.",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[
        'colour',
        'pyparsing'
    ],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    
    tests_require=['tox'],
    cmdclass = {'test': Tox},
)
