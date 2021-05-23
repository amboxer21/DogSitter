>create a symlink to a newly created file net.eth0 in /etc/init.d
``
ln -s /etc/init.d/net.lo /etc/init.d/net.eth0
``

> create file in /etc/conf.d called net
```
# For DHCP
#config_eth0="dhcp"

# For static IP using CIDR notation
config_eth0="192.168.1.217/24"
routes_eth0="default via 192.168.1.1"
dns_servers_eth0="192.168.1.1 8.8.4.4 8.8.8.8"
```

Wkiki is [here](https://wiki.gentoo.org/wiki/Handbook:X86/Full/Networking) @ `https://wiki.gentoo.org/wiki/Handbook:X86/Full/Networking`
