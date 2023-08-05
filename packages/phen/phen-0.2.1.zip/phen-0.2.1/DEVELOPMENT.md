# Phen Developement

The suggested way of setting up a development environment is through
virtualenv. Unpack the source distribution or clone the git repository,
then follow the instructions for your OS.

## GNU/Linux

For Debian-derived operating systems, you must install the development
dependencies as follow:

``` bash
apt-get install python-dev libgmp3-dev python-pip python-virtualenv \
                libxml2-dev libxslt-dev python-fontforge libffi-dev
```

Or if instead of using virtualenv you rather use system libraries:

``` bash
apt-get install python-lxml python-twisted python-crypto python-openssl \
                python-six python-gmpy python-vobject python-markdown \
                python-cryptography
```

## Windows

For Windows, use these installers:

* [Python 2.7](http://www.python.org/download/releases/2.7.5/)
* [pip](http://www.pip-installer.org/en/latest/installing.html)
* [PyCrypto](http://www.voidspace.org.uk/python/modules.shtml#pycrypto)
* [gmpy](http://code.google.com/p/gmpy/downloads/list)
* [py2exe](http://www.py2exe.org/)

Then add ";c:\Python27;c:\Python27\Scripts" to the path:

`Control Panel > System > Advanced > Environment > Path`

todo: update Windows dep list

## Setting up the development environment for Phen

Create the virtual environment:

``` bash
virtualenv env
cd env
source bin/activate # or on Windows: \path\to\env\Scripts\activate
```

After it's done, the required runtime libraries must be installed:

``` bash
cd /path/to/phen/
pip install -r requirements.txt
```
