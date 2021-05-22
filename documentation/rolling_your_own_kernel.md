# Rolling your own kernel

> tutorial for rolling your own kernel

https://www.stephenwagner.com/2020/03/17/how-to-compile-linux-kernel-raspberry-pi-4-raspbian/

---

sudo emerge -av sys-devel/bc

---

## Instructions

> NEEDS FORMATTING

So you’ve got a shiny new Raspberry Pi 4 and you need to compile a fresh and custom Linux kernel on Raspbian. You might need some features, some kernel modules, or you just want to compile the latest version from source.

I’m doing various projects (and blog posts) and with one of the projects, I found I needed to compile and enable a kernel module that wasn’t built in to the latest Raspbian image for the Pi 4.

This guide is also great if you just want to learn how to compile the kernel yourself!
Instructions

You may find that this guide is slightly different that the guide on the Raspberry Pi website and other sites. I like to append a unique name to the kernel version so I don’t have to touch the existing kernels. This allows me to revert or run multiple different custom kernels and switch back and forth.

Please note: You must be using a 32-bit kernel (or the default Raspbian kernel) to compile a new 32-bit kernel. You will not be able to compile a new kernel (32-bit or 64-bit) if you have booted in to the 64-bit kernel using the “arm_64bit=1” switch in “config.txt”. I’ve tried to compile a 64-bit kernel on Raspbian, but have not yet been able to do so. I’ll update with a new post once I figure it out.

And don’t forget, this can take some time and is CPU intensive. I installed a fan to help cool the temperatures while compilling!
This guide will compile a 32-bit kernel.

    Install some packages required to building and compiling.

    apt install raspberrypi-kernel-headers build-essential bc git wget bison flex libssl-dev make libncurses-dev

    Create a directory for us to work in.

    mkdir kernel
    cd kernel

    Clone the latest kernel sources using GIT.

    git clone --depth=1 https://github.com/raspberrypi/linux

    Setup the kernel configuration for compiling.

    cd linux
    KERNEL=kernel7l
    make bcm2711_defconfig

    Make any changes you want to the kernel configuration and append a friendly local version name by using make menuconfig.

    make menuconfig


    To change the friendly name, navigate to “General Setup” and select/modify “Local Version – append to kernel release”.

    (-v7lstephen) Local version - append to kernel release

    Compile the kernel, modules, and device tree blobs.

    make -j4 zImage modules dtbs

    Install compiled modules.

    make modules_install

    Copy the kernel, modules, and other files to the boot filesystem.

    cp arch/arm/boot/dts/*.dtb /boot/
    cp arch/arm/boot/dts/overlays/*.dtb* /boot/overlays/
    cp arch/arm/boot/dts/overlays/README /boot/overlays/
    cp arch/arm/boot/zImage /boot/kernel-stephen.img

    Configure the PI to boot using the new kernel by modifying and adding the below line to “/boot/config.txt”.

    kernel=kernel-stephen.img

    Reboot!

Bam! You’re now using your shiny new Linux kernel on the Raspberry Pi 4!
To rescue a failed build or if the Pi won’t boot

If for some reason the Pi won’t boot, you can recover the previous kernel since we used a new name with the new kernel.

To rescue the image you’ll need another Linux computer that can read the Micro-SD card.

    Insert the Micro-SD Card in the computer.
    Mount the /boot/ filesystem on the Micro SD card to a local directory.
    Edit the “config.txt” file and remove the “kernel=kernel-name.img” line we made above, or alternatively comment it out by inserting a “#” before the line.

    #kernel=kernel-stephen.img

    Save the file.
    Unmount the partition.
    Insert in the Raspberry Pi and boot!

You should now be back up and running and should be able to try again!

Leave some feedback and let me know if it worked for you. In the future I’ll be doing another post on compiling a 64-bit kernel for the Raspberry Pi 4 on Raspbian.

---

## Commands(ONLY) to roll your own kernel

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

