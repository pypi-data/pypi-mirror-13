import os

from pip.download import PipSession
from pip.req import parse_requirements
from pip.index import PackageFinder
from setuptools import setup, find_packages


version = '0.1.3'

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

root_dir = os.path.abspath(os.path.dirname(__file__))
requirements_path = os.path.join(root_dir, 'requirements.txt')

session = PipSession()
finder = PackageFinder([], [], session=session)
requirements = parse_requirements(requirements_path, finder, session=session)
install_requires = [r.name for r in requirements if r.match_markers()]

standard_exclude = ('*.py', '*.pyc', '*$py.class', '*~', '.*', '*.bak')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build',
                                './dist', 'EGG-INFO', '*.egg-info')

setup(
    name='django-randsense',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    license='BSD License',
    description='A Django app to create random sentences.',
    long_description=README,
    url='https://www.jameydeorio.com/',
    author='Jamey DeOrio',
    author_email='jdeorio@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
