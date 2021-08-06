#!/bin/bash

WAYDROID_PATH=/var/lib/lxc/waydroid

. /usr/share/waydroid/generate-props.sh

if [ -f "${WAYDROID_PATH}/anbox.prop" ]; then
    exit 0
fi

echo "${GRALLOC_PROP}" >> ${WAYDROID_PATH}/anbox.prop
echo "${EGL_PROP}" >> ${WAYDROID_PATH}/anbox.prop
echo "${MEDIA_PROFILES_PROP}" >> ${WAYDROID_PATH}/anbox.prop
echo "${CCODEC_PROP}" >> ${WAYDROID_PATH}/anbox.prop
echo "${EXT_LIB_PROP}" >> ${WAYDROID_PATH}/anbox.prop
echo "${VULKAN_PROP}" >> ${WAYDROID_PATH}/anbox.prop
echo "${DPI_PROP}" >> ${WAYDROID_PATH}/anbox.prop
echo "${GLES_VER_PROP}" >> ${WAYDROID_PATH}/anbox.prop
echo "${XDG_PROP}" >> ${WAYDROID_PATH}/anbox.prop
echo "${WAYLAND_DISP_PROP}" >> ${WAYDROID_PATH}/anbox.prop
echo "${PULSE_PROP}" >> ${WAYDROID_PATH}/anbox.prop

# TODO: Drop this
echo "anbox.active_apps=full" >> ${WAYDROID_PATH}/anbox.prop
