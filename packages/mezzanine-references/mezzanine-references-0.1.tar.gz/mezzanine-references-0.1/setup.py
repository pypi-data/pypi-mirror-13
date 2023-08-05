import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

DESCRIPTION = """
Customer references as homepage slideshow
"""

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='mezzanine-references',
    version='0.1',
    packages=['mezzanine_references'],
    include_package_data=True,
    license='BSD License',
    description=DESCRIPTION,
    long_description=README,
    url='https://github.com/fpytloun/mezzanine-references',
    download_url='https://pypi.python.org/pypi/mezzanine-references',
    author='Filip Pytloun',
    author_email='filip@pytloun.cz',
    requires=['mezzanine'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
