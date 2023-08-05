import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

DESCRIPTION = """
Frequently Asked Questions page made simple
"""

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='mezzanine-faq',
    version='0.2',
    packages=['mezzanine_faq'],
    include_package_data=True,
    license='BSD License',
    description=DESCRIPTION,
    long_description=README,
    url='https://github.com/fpytloun/mezzanine-faq',
    download_url='https://pypi.python.org/pypi/mezzanine-faq',
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
