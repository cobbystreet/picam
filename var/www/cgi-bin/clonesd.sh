#!/bin/bash
#Run config.py (note the backticks). This returns the configuration as environment variables
eval `/var/www/cgi-bin/config.py`

echo "Copying Partition table"
dd if=/dev/mmcblk0 of=${CloneDev} bs=512 count=1 || ( echo "Can't copy Partition table" ; exit 1 )
echo "Rescanning Partition table"
partprobe ${CloneDev} || ( echo "Can't reload Partition table" ; exit 1 )
echo "Copying Boot Partition"
dd if=/dev/mmcblk0p1 of=${CloneDev}1 bs=1M || ( echo "Can't copy Boot Partition " && exit 1 )
echo "Copying Root Partition"
dd if=/dev/mmcblk0p2 of=${CloneDev}2 bs=1M  || ( echo "Can't copy Root Partition " && exit 1 )
echo "Mounting Root Partition"
mount -t ext4 ${CloneDev}2 /mnt || ( echo "Can't mount Root Partition" ; exit 1 )
echo "Modifying files"
echo ${CloneHost} >/mnt/etc/hostname
sed "s/ssid=.*/ssid=${CloneHost}/" /etc/hostapd/hostapd.conf >/mnt/etc/hostapd/hostapd.conf
sed "s/${HOSTNAME}/${CloneHost}/" /etc/hosts >/mnt/etc/hosts
echo "UnMounting Root Partition"
umount /mnt
echo "Done cloning"
