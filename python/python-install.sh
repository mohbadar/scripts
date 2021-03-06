#!/bin/bash
#
# Install python, helper utilities and frequently used modules

######################################################################
#
# Constants

PIP=pip

######################################################################
#
# Get OS name

uname=$(uname)

######################################################################
#
# Functons

install_module() {
  for module in $* ; do
    echo "Installing module ${module}"
    ${PIP} install ${module} || exit 1
  done
}

######################################################################
#
# Start by doing OS-specific python, pip and swig install

echo "Installing python"
case ${uname} in
  Darwin)
    brew install python
    # Above installs pip
    ;;

  *)
    echo "Don't know how to install python on ${uname}"
    exit 1
    ;;
esac

echo "Installing pip"

case ${uname} in
  Darwin)
    # XXX Should already be installed
    ;;

  *)
    echo "Don't know how to install pip on ${uname}"
    exit 1
    ;;
esac

echo "Installing swig"

case ${uname} in
  Darwin)
    brew install swig
    ;;

  *)
    echo "Don't know how to install swig on ${uname}"
    exit 1
    ;;
esac

######################################################################

echo "Installing virtualenv and virtualenvwrapper"
install_module virtualenv virtualenvwrapper

######################################################################
#
# Installing ipython and notebook

echo "Installing iPython"
install_module ipython readline

echo "Install iPython Notebook"

# http://ipython.org/ipython-doc/stable/interactive/notebook.html
install_module pyzmq tornado Jinja2

######################################################################

echo "Installing modules I have found useful"

# Graphical debugger
# https://pypi.python.org/pypi/pudb
install_module pudb

# Cliff - framework for CLI programs with sub-commands.
# https://cliff.readthedocs.org/
install_module cliff

# pyCLI - framework for simple CLI programs without sub-commands
# http://pythonhosted.org/pyCLI/
install_module pyCLI

# ProgressBar - CLI progress bar
# https://code.google.com/p/python-progressbar/
install_module progressbar

######################################################################

echo "Installing modules that look useful"

# Subprocess interace
# http://amoffat.github.io/sh/
install_module sh

# Contexter - a better contextlib
# https://bitbucket.org/defnull/contexter
install_module contexter

# docopt - commandline interface description language
# http://docopt.org/
install_module docopt

# mock - mocking and testing library
# http://www.voidspace.org.uk/python/mock/
install_module mock

# requests - HTTP for humans
# http://www.python-requests.org/
install_module requests

# path.py - wrapper for os,path
# https://pypi.python.org/pypi/path.py
install_module path.py

# watchdog - library and shell utilities to monitor file system events.
# http://pythonhosted.org/watchdog/
install_module watchdog

# dateutil - provides powerful extensions to the standard datetime module
# http://labix.org/python-dateutil
install_module python-dateutil

# structlog - structured logging
# http://www.structlog.org/
install_module structlog

# BeautifulSoup - HTML/XML parsing
# http://www.crummy.com/software/BeautifulSoup/
install_module beautifulsoup4

# CommonRegex - Find all times, dates, links, phone numbers, emails, ip
# addresses, prices, hex colors, and credit card numbers in a string.
# https://github.com/madisonmay/CommonRegex
install_module commonregex
######################################################################
#
# Modules to try

# Faker is a Python package that generates fake data for you.
# https://github.com/joke2k/faker

######################################################################

echo "Success."
exit 0

