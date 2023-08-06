import io
import os
from setuptools import setup


def get_path(*args):
    return os.path.join(os.path.dirname(__file__), *args)


def get_requirements(filename='requirements.txt'):
    with io.open(get_path(filename), 'rt', encoding='utf8') as fd:
        data = fd.read()
        lines = map(lambda s: s.strip(), data.splitlines())
    return [l for l in lines if l and not l.startswith('#')]


version = '0.0.8'

setup(
    name='pyipconnect',
    version=version,
    description='Utility to connect to Alliance Internet (India).',
    long_description="""Very simple python script for auto login to alliance web login""",
    url='http://github.com/eka/pyipconnect',
    author='Esteban (Eka) Feldman',
    author_email='esteban.feldman@gmail.com',
    license='MIT',
    packages=['pyipconnect'],
    scripts=['pyipconnect/bin/ipconnect'],
    zip_safe=False,
    install_requires=get_requirements()
)
