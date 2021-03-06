#!/usr/bin/env python
"""Make changes to Mac OSX system based on wireless network.

This script allows you to confiugure changes to a Max OSX system
based on the SSID of the wireless network your system is connected to.
It currently supports setting the default printer as well as executing
a arbitrary command.

This script works by using launchd to watch the file
/Library/Preferences/SystemConfiguration/com.apple.aurport.preferences.plist
and /var/run/resolve.conf, which change when the local network
configuration changes.

Many ideas taken from work by Onne Gorter <o.gorter@gmail.com> at:
http://tech.inhelsinki.nl/locationchanger/

Installation Directions

1) Install this script somewhere as a executable file.

2) Create ~/Library/LaunchAgents/networkwatcher.plist file using the
tempalte below. Do not include the "--begin template--" and
"--end template--" strings. Replace "*PATH*" with the path to where
you installed this script.

--begin template--
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN"
	"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key>
	<string>vwelch.com.networkwatcher</string>
	<key>ProgramArgumants</key>
	<array>
	  <string>*PATH*/networkwatcher</string>
	</array>
	<key>WatchPaths</key>
	<array>
	        <string>/Library/Preferences/SystemConfiguration/com.apple.airport.preferences.plist</string>
		<string>/var/run/resolv.conf</string>
	</array>
</dict>
</plist>
--end template--

3) Create ~/.networkwatcher configuration file. This file should contain
one or more SSIDs in brackets. Each SSID should be followed by one or more
of the following statements:

  location=location name
       Set the network location.

  printer=name of printer
       This sets the default printer when the system is connected to
       the given SSID. Printer names can be found in
       /etc/cups/printers.conf

  cmd=command to pass to shell
       This executes the given command when the system is connected to
       the given SSID.

Here is an example .networkwatcher configuration:  

[NCSA]
printer=bw2010pub.ncsa.uiuc.edu
location=Work

[Home]
printer=PSC 1600 series
location=Home

4) Load the networkwatch.plist configuration into launchd using the
following command. This only needs to be done once.

launchctl load ~/Library/LaunchAgents/networkwatcher.plist

5) That's it. Everytime you change your wireless network, networkwatcher
should be run by launchd. It will log it's actions to
/tmp/networkwatcher.log so you can keep track of what it is doing.
"""

__author__ = "Von Welch <vwelch@ncsa.uiuc.edu>"
__date__ = "$Date$"
__version__ = "$Revision$"

######################################################################
#
# Configuration
#

binaries = {
    "airport" : "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/A/Resources/airport",
    "ifconfig" : "ifconfig",
    "lpoptions" : "lpoptions",
    "scselect" : "scselect"
    }

ethernetIF = "en0"
airportIF = "en1"

######################################################################

def getNetworkParams():
    """Return a dictionary of network parameters. Values include:

ssid     Current SSID
bssid    Current Base Station ID
"""
    from subprocess import Popen, PIPE

    networkParams = {}

    airportCmd = "%s -I " % binaries["airport"]

    debug("Running %s" % airportCmd)
    pipe = Popen(airportCmd, shell=True, stdout=PIPE).stdout

    while True:
	line = pipe.readline()
	if len(line) == 0:
	    break
	components = line.split()
	if components[0] == "SSID:":
	    networkParams["ssid"] = components[1]
	    continue
	if components[0] == "BSSID:":
	    networkParams["bssid"] = components[1]
	    continue

    pipe.close()

    # Query interface, which one depends on wether we're using the airport
    # or not
    if networkParams.has_key("SSID"):
	interface = airportIF
    else:
	interface = ethernetIF
    
    ifconfigCmd = "%s %s" % (binaries["ifconfig"], interface)
    debug("Running %s" % ifconfigCmd)
    pipe = Popen(ifconfigCmd, shell=True, stdout=PIPE).stdout

    while True:
	line = pipe.readline()
	if len(line) == 0:
	    break
	components = line.split()
	if components[0] == "inet":
	    networkParams["IPaddress"] = components[1]

    pipe.close()

    return networkParams

######################################################################

def executeCmd(cmd):
    from subprocess import Popen, PIPE, STDOUT

    fromCmd = Popen(cmd, shell=True, stdout=PIPE,
		    stderr=STDOUT, close_fds=True).stdout

    while True:
	line = fromCmd.readline()
	if len(line) == 0:
	    break
	debug(line)

    fromCmd.close()

######################################################################
#
# Logging functions
#

def debug(msg):
    """Log a debugging message."""
    import logging

    logger = logging.getLogger()
    logger.debug(msg)

def log(msg):
    """Log a message."""
    import logging

    logger = logging.getLogger()
    logger.info(msg)

######################################################################

def errorExit(msg):
    """Log error message and exit."""
    import sys
    import logging

    logger = logging.getLogger()
    logger.error(msg)

    sys.exit(1)

######################################################################

def getConfig(configFilename=None):
    """Read our configuration. If configFilename is None, then ~/.networkwatcher
    is read."""

    import ConfigParser
    import os.path

    configFileName = os.path.expanduser("~/.networkwatcher")
    try:
	os.stat(configFileName)
    except OSError, e:
	errorExit("Could not read configuration file: %s" % e)

    config = ConfigParser.SafeConfigParser()
    try:
	config.read(configFileName)
    except Exception, e:
	errorExit("Error parsing configuration file: %s" % e)

    return config

######################################################################

def initLogging(filename, debug=False):
    """Initialize logging."""
    import logging, logging.handlers

    logger = logging.getLogger()

    if debug:
	logger.setLevel(logging.DEBUG)
    else:
	logger.setLevel(logging.INFO)

    handler = logging.FileHandler(filename)
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info("networkwatcher running.")


######################################################################

if __name__ == "__main__":

    import sys
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-d", "--debug", action="store_true", dest="debug",
		      default=False, help="turn on debugging")
    (options, args) = parser.parse_args()

    #
    # Get our configuration
    #
    config = getConfig()

    #
    # Set up logging
    #

    initLogging("/tmp/networkwatcher.log", debug = options.debug)

    #
    # Determine current network parameters
    #

    networkParams = getNetworkParams()

    if networkParams.has_key("ssid"):
	log("SSID is %s" % networkParams["ssid"])
    log("IP is %s" % networkParams["IPaddress"])

    #
    # Find the section of the configuration file that corresponds to
    # current network
    #

    networks = config.sections()

    section = None

    if (networkParams.has_key("ssid") and
	networks.count(networkParams["ssid"])):
	section = networkParams["ssid"]

    if section is None:
	log("No relevant network section found. Exiting.")
	sys.exit(0)

    #
    # Parse and act-on configuration file section
    #

    try:
	cmd = config.get(section, "cmd")
    except:
	# No cmd parameter
	pass
    else:
	log("Executing %s" % cmd)
	executeCmd(cmd)

    try:
	printer = config.get(section, "printer")
    except:
	# No printer parameter
	pass
    else:
	log("Setting default printer to %s" % printer)
	# Need to convert a bunch of characters to underscores
	printer = printer.replace(" ", "_")
	printer = printer.replace(".", "_")
	cmd = "%s -d %s" % (binaries["lpoptions"], printer)
	debug("Running command %s" % cmd)
	executeCmd(cmd)

    try:
	location = config.get(section, "location")
    except:
	# No location specified
	pass
    else:
	log("Setting location to %s" % location)
	cmd = "%s %s" % (binaries["scselect"], location)
	debug("Running command %s" % cmd)
	executeCmd(cmd)

    log("networkwatcher done.")
    sys.exit(0)
