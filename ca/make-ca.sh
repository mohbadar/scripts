#!/bin/sh
######################################################################
#
# Make a new CA.
#
######################################################################

# Exit on any error
set -e

. include.sh

######################################################################
#
# Parse commandline options
#

if [ $# -gt 0 ]; then
  ca_name=$1
  shift
else
  ca_name="default"
fi

######################################################################
#
# Create CA directory
#

if [ ! -d ca ]; then
  mkdir ca
fi

ca_dir="ca/${ca_name}"

if [ -e $ca_dir ]; then
  echo "CA directory $ca_dir already exists."
  exit 1;
fi

echo "Creating CA directory $ca_dir and contents"
mkdir $ca_dir
mkdir ${ca_dir}/certs
touch ${ca_dir}/index.txt
echo "01" > $ca_dir/serial

######################################################################
#
# Copy in configuration file
#

echo "Creating CA configuration"

ca_config=$ca_dir/ca.cnf
ca_key=$ca_dir/key.pem
ca_cert=$ca_dir/cert.pem
pwd=`pwd`

sed_script=""
sed_script=${sed_script}"s\\Xdir\\${pwd}/${ca_dir}\\g;"
sed_script=${sed_script}"s\\Xca_name\\${ca_name}\\g;"
sed_script=${sed_script}"s\\Xca_key\\${pwd}/${ca_key}\\g;"

sed $sed_script ca.cnf.in > $ca_config

######################################################################
#
# Generate the key and cert
#

echo "Generating CA certificate"

# These variables are used in CA configuration
COMMON_NAME=${ca_name}
OU_NAME="CA"

${openssl} req -x509 -newkey rsa \
  -out ${ca_cert} \
  -keyout ${ca_key} \
  -days $lifetime \
  -config $ca_config \
  -nodes

######################################################################
#
# Ok generate the Globus-specific stuff. First ca cert file.
#

echo "Generating Globus-specific stuff"

ca_hash=`${openssl} x509 -in $ca_cert -hash -noout`

cp ${ca_cert} ${ca_dir}/${ca_hash}.0

ca_signing_policy=${ca_dir}/${ca_hash}.signing_policy
dn="/C=${COUNTRY_NAME}/O=${ORG_NAME}/OU=${OU_NAME}/CN=${COMMON_NAME}"
namespace="/C=${COUNTRY_NAME}/O=${ORG_NAME}/*"

sed_script=""
sed_script=${sed_script}"s\\Xdn\\${dn}\\g;"
sed_script=${sed_script}"s\\Xnamespace\\${namespace}\\g;"

sed $sed_script signing_policy.in > $ca_signing_policy

######################################################################
#
# Success
#

echo "Success."
exit 0

#
# End
#
######################################################################


