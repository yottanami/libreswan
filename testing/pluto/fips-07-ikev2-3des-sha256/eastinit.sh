/testing/guestbin/swan-prep
fipscheck
setenforce 0
ipsec setup start
/testing/pluto/bin/wait-until-pluto-started
ipsec auto --add westnet-eastnet-ikev2
echo "initdone"
