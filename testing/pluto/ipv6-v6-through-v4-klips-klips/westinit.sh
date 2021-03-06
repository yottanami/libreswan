/testing/guestbin/swan-prep --46
# confirm that the network is alive
ping6 -n -c 4 -I 2001:db8:0:1::254 2001:db8:0:2::254
# make sure that clear text does not get through
ip6tables -A INPUT -i eth1 -s 2001:db8:0:2::254 -j DROP
# confirm with a ping
ping6 -n -c 4 -I 2001:db8:0:1::254 2001:db8:0:2::254
ipsec setup start
/testing/pluto/bin/wait-until-pluto-started
ipsec auto --add westnet-eastnet-6in4
echo "initdone"
