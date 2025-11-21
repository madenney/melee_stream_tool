This document explains how to reinstall the obs-multi-rtmp plugin for the
Flatpak version of OBS Studio. Use this if you reset your system or forget
how the plugin files must be placed.

-------------------------------------------------------------------------------
FILES NEEDED
-------------------------------------------------------------------------------
From the plugin package (deb-ified folder), you need:

1. obs-multi-rtmp.so
   Located inside:
   ./usr/lib/x86_64-linux-gnu/obs-plugins/

2. The locale folder:
   ./usr/share/obs/obs-plugins/obs-multi-rtmp/

Both must be copied into the Flatpak OBS plugin directory.

-------------------------------------------------------------------------------
FLATPAK OBS PLUGIN LOCATION
-------------------------------------------------------------------------------
All plugins go here:

~/.var/app/com.obsproject.Studio/config/obs-studio/plugins/

This folder should contain:
- obs-multi-rtmp.so
- obs-multi-rtmp/   (folder)
    └── locale/
        └── *.ini files

-------------------------------------------------------------------------------
INSTALLING (COPYING FILES)
-------------------------------------------------------------------------------
From your extracted plugin directory, run:

cp PATH_TO_PLUGIN/usr/lib/x86_64-linux-gnu/obs-plugins/obs-multi-rtmp.so \
   ~/.var/app/com.obsproject.Studio/config/obs-studio/plugins/

cp -r PATH_TO_PLUGIN/usr/share/obs/obs-plugins/obs-multi-rtmp \
   ~/.var/app/com.obsproject.Studio/config/obs-studio/plugins/

Replace PATH_TO_PLUGIN with the actual folder name you extracted.

-------------------------------------------------------------------------------
VERIFY INSTALL
-------------------------------------------------------------------------------
Run:

tree ~/.var/app/com.obsproject.Studio/config/obs-studio/plugins

You should see:

plugins/
├── obs-multi-rtmp.so
└── obs-multi-rtmp/
    └── locale/
        ├── en-US.ini
        ├── etc...

-------------------------------------------------------------------------------
USING THE PLUGIN
-------------------------------------------------------------------------------
Restart OBS.

You should now see:
Tools → Multiple Outputs

If this appears, the install worked.

-------------------------------------------------------------------------------
NOTES
-------------------------------------------------------------------------------
- This guide is ONLY for the Flatpak version of OBS.
- System plugin directories DO NOT work with Flatpak.
- Reinstalling OBS or wiping configs just means re-copying these files.
