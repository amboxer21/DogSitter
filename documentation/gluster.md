DOCs:

https://docs.gluster.org/en/v3/Administrator%20Guide/Setting%20Up%20Volumes/


Gluster must be compiled without ipv6

```
localhost ~ # eix glusterfs
[?] sys-cluster/glusterfs
     Available versions:  (~)7.9(0/7)^t (~)8.3(0/8)^t (~)8.4(0/8)^t (~)9.0(0/9)^t {debug emacs +fuse +georeplication infiniband ipv6 libressl +libtirpc rsyslog static-libs +syslog test +xml PYTHON_SINGLE_TARGET="python3_7 python3_8 python3_9"}
     Installed versions:  9.1(0/9)^t(22:57:07 05/22/21)(fuse georeplication libtirpc rsyslog syslog xml -debug -emacs -ipv6 -static-libs -test PYTHON_SINGLE_TARGET="python3_7 -python3_8 -python3_9")
     Homepage:            https://www.gluster.org/ https://github.com/gluster/glusterfs/
     Description:         GlusterFS is a powerful network/cluster filesystem

localhost ~ #
```

All nodes must be running the same gluster version
