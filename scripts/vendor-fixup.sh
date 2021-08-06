#!/bin/bash

mkdir /var/lib/lxc/waydroid/tmp_vendor
mount /var/lib/lxc/waydroid/anbox_${1}_vendor.img /var/lib/lxc/waydroid/tmp_vendor

SKU=`getprop ro.boot.product.hardware.sku`
cp -p /vendor/etc/permissions/android.hardware.nfc.* /var/lib/lxc/waydroid/tmp_vendor/etc/permissions/
cp -p /vendor/etc/permissions/android.hardware.consumerir.xml /var/lib/lxc/waydroid/tmp_vendor/etc/permissions/
cp -p /odm/etc/permissions/android.hardware.nfc.* /var/lib/lxc/waydroid/tmp_vendor/etc/permissions/
cp -p /odm/etc/permissions/android.hardware.consumerir.xml /var/lib/lxc/waydroid/tmp_vendor/etc/permissions/
if [ ! -z $SKU ]; then
    cp -p /odm/etc/permissions/sku_${SKU}/android.hardware.nfc.* /var/lib/lxc/waydroid/tmp_vendor/etc/permissions/
    cp -p /odm/etc/permissions/sku_${SKU}/android.hardware.consumerir.xml /var/lib/lxc/waydroid/tmp_vendor/etc/permissions/
fi
if [ -f /vendor/lib/libladder.so ] && [ ! -f /var/lib/lxc/waydroid/tmp_vendor/lib/libladder.so ]; then
    cd /var/lib/lxc/waydroid/tmp_vendor/lib
    wget https://github.com/GS290-dev/gigaset_gs290_dump/raw/full_k63v2_64_bsp-user-10-QP1A.190711.020-1597810494-release-keys/vendor/lib/libladder.so
    cd ../../..
fi
if [ -f /vendor/lib64/libladder.so ] && [ ! -f /var/lib/lxc/waydroid/tmp_vendor/lib64/libladder.so ]; then
    cd /var/lib/lxc/waydroid/tmp_vendor/lib64
    wget https://github.com/GS290-dev/gigaset_gs290_dump/raw/full_k63v2_64_bsp-user-10-QP1A.190711.020-1597810494-release-keys/vendor/lib64/libladder.so
    cd ../../..
fi
if [ -f /vendor/lib64/libmpvr.so ] && [ ! -f /var/lib/lxc/waydroid/tmp_vendor/lib64/libmpvr.so ]; then
    cp /vendor/lib64/libmpvr.so /var/lib/lxc/waydroid/tmp_vendor/lib64/
fi
if [ -f /vendor/lib/libmpvr.so ] && [ ! -f /var/lib/lxc/waydroid/tmp_vendor/lib/libmpvr.so ]; then
    cp /vendor/lib/libmpvr.so /var/lib/lxc/waydroid/tmp_vendor/lib/
fi
sed -i "s/-service/-service --desktop_file_hint=unity8.desktop/" /var/lib/lxc/waydroid/tmp_vendor/etc/init/android.hardware.graphics.composer@2.1-service.rc
umount /var/lib/lxc/waydroid/tmp_vendor
rm -rf /var/lib/lxc/waydroid/tmp_vendor
