# Rolling your own kernel

> linux kernel clone url
 
git clone --depth=1 https://github.com/raspberrypi/linux

> tutorial for rolling your own kernel

https://www.stephenwagner.com/2020/03/17/how-to-compile-linux-kernel-raspberry-pi-4-raspbian/

---

**Commands to roll your own kernel**

```javascript
apt install raspberrypi-kernel-headers build-essential bc git wget bison flex libssl-dev make libncurses-dev
mkdir kernel
cd kernel
git clone --depth=1 https://github.com/raspberrypi/linux
cd linux
KERNEL=kernel7l
make bcm2711_defconfig
make menuconfig
# To change the friendly name, navigate to “General Setup” and select/modify “Local Version – append to kernel release”.
make -j4 zImage modules dtbs
make modules_install
cp arch/arm/boot/dts/*.dtb /boot/
cp arch/arm/boot/dts/overlays/*.dtb* /boot/overlays/
cp arch/arm/boot/dts/overlays/README /boot/overlays/
cp arch/arm/boot/zImage /boot/kernel-stephen.img
# Configure the PI to boot using the new kernel by modifying and adding the below line to “/boot/config.txt”.
kernel=kernel-stephen.img
```

