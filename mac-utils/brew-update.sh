#!/bin/sh
# Update brew and all brew packages
# Kudos: http://www.commandlinefu.com/commands/view/4831/update-all-packages-installed-via-homebrew

set -e  # Exit on any error
errors=0
echo "Updating brew..."
brew update
echo "Updating packages..."
outdated=$(brew outdated --quiet)
if test -n "${outdated}" ; then
  brew upgrade ${outdated} || errors=$(($errors+1))
else
  echo "No packages need updating."
fi
if test ${errors} -gt 0 ; then
  echo "${errors} errors encountered."
  exit 1
fi
echo "Removing older versions of packages..."
brew cleanup
echo "Success."
exit 0

