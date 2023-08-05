from setuptools import setup

version = '0.0.4'
name = 'dioc'
short_description = '`dioc` is a package for DigitalOcean.'
long_description = """\
`dioc` is a package for DigitalOcean.
::
   # Set your token to "dioc.yml"
   $ cat << eof >> dioc.yml
!Setting
token: !!!set_your_token!!!
default_sshkey: sshkey
default_size: 512mb
default_region: sgp1
eof

   import dioc
   d = dioc.Droplet('test')
   c = dioc.ssh_client()
   c.exec_command('ls')
   d.destroy()

Requirements
------------
* Python 3
* paramiko
* pyyaml
* python-digitalocean

Features
--------
* nothing

Setup
-----
::

   $ pip install dioc
   or
   $ easy_install dioc

History
-------
0.0.1 (2015-12-27)
~~~~~~~~~~~~~~~~~~
* first release

"""

classifiers = [
   "Development Status :: 1 - Planning",
   "License :: OSI Approved :: Python Software Foundation License",
   "Programming Language :: Python",
   "Topic :: Software Development",
]

setup(
    name=name,
    version=version,
    description=short_description,
    long_description=long_description,
    classifiers=classifiers,
    py_modules=['dioc'],
    keywords=['dioc',],
    author='Saito Tsutomu',
    author_email='tsutomu@kke.co.jp',
    url='https://pypi.python.org/pypi/dioc',
    license='PSFL',
    install_requires=['paramiko', 'pyyaml', 'python-digitalocean', ],
)