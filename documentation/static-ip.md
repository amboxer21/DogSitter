This networking guide presumes that the user has correctly configured the system and has determined the hardware's network interface name(s). The network interface name is produced based on the bus location of the network card(s) in the system. Because of this there is potential for interface name variants including: eno0, ens1, wlan0, enp1s0, etc. Each system may have a slightly different interface name. The following content presumes the name of the interface to configured is eth0, although any of the aforementioned names will work.

To get started configuring the network card, tell the Gentoo RC system about it. This is done by creating a symbolic link from net.lo to net.eth0 (or whatever the network interface name is on the system) in /etc/init.d.
```javascript
root #cd /etc/init.d
root #ln -s net.lo net.eth0
```

Gentoo's RC system now knows about that interface. It also needs to know how to configure the new interface. All the network interfaces are configured in /etc/conf.d/net file. Below is a sample configuration for DHCP and static addresses.
FILE `/etc/conf.d/net` Example network configuration

```
# For DHCP

config_eth0="dhcp"
  
# For static IP using CIDR notation
config_eth0="192.168.0.7/24"
routes_eth0="default via 192.168.0.1"
dns_servers_eth0="192.168.0.1 8.8.8.8"
  
# For static IP using netmask notation
config_eth0="192.168.0.7 netmask 255.255.255.0"
routes_eth0="default via 192.168.0.1"
dns_servers_eth0="192.168.0.1 8.8.8.8"
```

**Note:**

If no configuration is mentioned for an interface then DHCP is assumed.

**Note:**

CIDR stands for Classless InterDomain Routing. Originally, IPv4 addresses were classified as A, B, or C. The early classification system did not envision the massive popularity of the Internet, and is in danger of running out of new unique addresses. CIDR is an addressing scheme that allows one IP address to designate many IP addresses. A CIDR IP address looks like a normal IP address except that it ends with a slash followed by a number; for example, 192.168.0.0/16. CIDR is described in RFC 1519.

Now that the interface is configured, we can start and stop it using the following commands:
```
root #/etc/init.d/net.eth0 start
root #/etc/init.d/net.eth0 stop
```
**Iportant:**
When troubleshooting networking, take a look at /var/log/rc.log. Unless the rc_logger variable is set to NO in /etc/rc.conf, information on the boot activity will be stored in that log file.

Now that the network interface has been successfully stopped and started, the next step is to have it started when Gentoo boots. Here is how to do this.:
```
root #rc-update add net.eth0 default
root #rc
```

**Note:**

The last rc command instructs Gentoo to start any scripts in the current runlevel that have not yet been started.
