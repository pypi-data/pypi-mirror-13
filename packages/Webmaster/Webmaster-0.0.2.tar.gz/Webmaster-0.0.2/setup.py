"""
Webmaster

Webmaster is a Flask based framework to help quickly develop web applications, by
adding structure to your views and templates.

Philosophy:

To create a framework that runs everywhere, regardless of the platform, by
providing cloud balh...

It made the following decisions for you: (of course you can change them)


It comes with pre-built components:


And it is still Flask.

http://pylot.io/
https://github.com/mardix/Webmaster

"""

import os
from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)

__about__ = {}
with open(os.path.join(base_dir, "webmaster", "__about__.py")) as f:
    exec(f.read(), __about__)

setup(
    name=__about__["title"],
    version=__about__["version"],
    license=__about__["license"],
    author=__about__["author"],
    author_email=__about__["email"],
    description=__about__["description"],
    url=__about__["uri"],
    long_description=__doc__,
    py_modules=['webmaster'],
    entry_points=dict(console_scripts=[
        'webcli=webmaster.cli:cli'
    ]),
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'Flask==0.10.1',
        'Flask-Assets==0.10',
        'flask-recaptcha==0.4.1',
        'flask-login==0.3.2',
        'flask-kvsession==0.6.1',
        'flask-s3==0.2.5',
        'flask-mail==0.9.0',
        'flask-cache==0.13.1',
        'flask-cloudy==0.13.1',
        'flask-seasurf==0.2.0',
        #'flask-babel==0.9',
        'Active-Alchemy==0.4.4',
        'Paginator==0.3.5',
        #'authomatic==0.1.0.post1',
        'six==1.9.0',
        'passlib==1.6.2',
        'bcrypt==1.1.1',
        'python-slugify==0.1.0',
        'humanize==0.5.1',
        'redis==2.9.1',
        'ses-mailer==0.13.0',
        'markdown==2.6.2',
        'inflection==0.3.1',
        'pyyaml==3.11',
        'click==5.1',
        'dicttoxml==1.6.6'
    ],
    keywords=['flask',
              'webmaster',
              'templates',
              'views',
              'classy',
              'framework',
              "mvc",
              "blueprint",
              "webmaster"],
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    zip_safe=False
)

