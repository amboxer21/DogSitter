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

creating capture volume 
```
gluster volume create capture replica 4 pi1:/export/capture pi2:/export/capture pi3:/export/capture pi4:/export/capture force
```

create logs volume 
```
gluster volume create logs replica 4 pi1:/export/logs pi2:/export/logs pi3:/export/logs pi4:/export/logs force
```

create the videos volume
```
gluster volume create videos replica 4 pi1:/export/videos pi2:/export/videos pi3:/export/videos pi4:/export/videos force
```

create the mail volume
```
sudo gluster vol create mail replica 4 transport tcp pi1:/export/mail pi2:/export/mail pi3:/export/mail pi4:/export/mail force
```

start the volumes 
```
gluste rvol start logs
gluste rvol start mail
gluste rvol start videos
gluste rvol start capture
```


```
All nodes must be running the same gluster version

localhost ~ # rc-uodate add glusterd
-bash: rc-uodate: command not found
localhost ~ # rc-update add glusterd
 * rc-update: glusterd already installed in runlevel `default'; skipping
localhost ~ # ls /var/gluster/
dogsitter  pi
localhost ~ # rm -r /var/gluster/pi
localhost ~ # rm -r /var/gluster/dogsitter
localhost ~ # aagluster volume create pi
-bash: aagluster: command not found
localhost ~ # gluster volume create glusterfs replica 4 transport tcp pi1:/export pi2:/export pi3:/export pi4:/export
volume create: glusterfs: failed: The brick pi4:/export is being created in the root partition. It is recommended that you don't use the system's root partition for storage backend. Or use 'force' at the end of the command if you want to override this behavior.
localhost ~ # gluster volume create glusterfs replica 4 transport tcp pi1:/export pi2:/export pi3:/export pi4:/export force
volume create: glusterfs: success: please start the volume to access data
localhost ~ # gluster volume list
glusterfs
localhost ~ # gluster volume start glusterfs
volume start: glusterfs: success
localhost ~ # gluster volume set gfs auth.allow 10.0.0.2,10.0.0.3,10.0.0.4
volume set: failed: Volume gfs does not exist
localhost ~ # gluster volume set glusterfs auth.allow 192.168.1.105,192.168.1.217,192.168.1.218,192.168.1.232
volume set: success
localhost ~ # gluster volume set glusterfs auth.allow 192.168.1.105,192.168.1.217,192.168.1.218,192.168.1.232,192.168.1.248
volume set: success
localhost ~ #
```
