# Tablet Joy-Con Controller

Build helper for the open-source **Joy-Con Merge — Shizuku Edition** project by Faraw4y.

This repository does not contain Nintendo keys, firmware, ROMs, or proprietary game content. It simply builds the upstream Android controller-merging app so a paired Left + Right Joy-Con can be exposed as one virtual controller on Android via Shizuku, without root.

Upstream project: https://github.com/Faraw4y/joycon-merge

## Build

The GitHub Actions workflow checks out the upstream Joy-Con Merge source at a pinned commit, installs the required Android build tools, builds the release APK, and uploads it as a workflow artifact named `JoyConMerge-APK`.

## Tablet setup after installing

1. Install Shizuku from Google Play.
2. Start Shizuku using Android Wireless Debugging.
3. Install the APK produced by the workflow.
4. Pair both Joy-Cons to Android over Bluetooth.
5. Open Joy-Con Merge and grant Shizuku permission.
6. Tap **Start** to merge the pair into one virtual controller.
