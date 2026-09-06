from pathlib import Path

main = Path("upstream/app/src/main/java/com/joyconmerge/MainActivity.java")
s = main.read_text(encoding="utf-8")

# MainActivity originally checks Shizuku only during onResume. On some newer
# Android/Shizuku combinations the binder arrives slightly later, leaving the
# UI stuck on "Shizuku not running" even though Shizuku is active. Listen for
# binder arrival/death and refresh the UI when either event happens.
marker = "    // ─── ServiceConnection ────────────────────────────────────────────────────\n"
listener_block = '''    // Refresh the UI as soon as the Shizuku binder becomes available.\n    private final Shizuku.OnBinderReceivedListener shizukuBinderReceivedListener =\n        () -> runOnUiThread(this::updateShizukuBanner);\n\n    private final Shizuku.OnBinderDeadListener shizukuBinderDeadListener =\n        () -> runOnUiThread(this::updateShizukuBanner);\n\n'''
if listener_block not in s:
    if marker not in s:
        raise RuntimeError("Could not locate ServiceConnection marker")
    s = s.replace(marker, listener_block + marker, 1)

old = "        Shizuku.addRequestPermissionResultListener(shizukuPermResult);\n"
new = "        Shizuku.addBinderReceivedListenerSticky(shizukuBinderReceivedListener);\n        Shizuku.addBinderDeadListener(shizukuBinderDeadListener);\n        Shizuku.addRequestPermissionResultListener(shizukuPermResult);\n"
if new not in s:
    if old not in s:
        raise RuntimeError("Could not locate Shizuku permission listener registration")
    s = s.replace(old, new, 1)

old = '''    protected void onResume() {\n        super.onResume();\n        updateShizukuBanner();\n    }\n'''
new = '''    protected void onResume() {\n        super.onResume();\n        updateShizukuBanner();\n        // A short delayed refresh covers devices where the binder is delivered\n        // just after Activity resume. The sticky listener above remains the\n        // authoritative update path.\n        shizukuBanner.postDelayed(this::updateShizukuBanner, 500);\n        shizukuBanner.postDelayed(this::updateShizukuBanner, 1500);\n    }\n'''
if new not in s:
    if old not in s:
        raise RuntimeError("Could not locate onResume")
    s = s.replace(old, new, 1)

old = "        Shizuku.removeRequestPermissionResultListener(shizukuPermResult);\n"
new = "        Shizuku.removeRequestPermissionResultListener(shizukuPermResult);\n        Shizuku.removeBinderReceivedListener(shizukuBinderReceivedListener);\n        Shizuku.removeBinderDeadListener(shizukuBinderDeadListener);\n"
if new not in s:
    if old not in s:
        raise RuntimeError("Could not locate onDestroy listener cleanup")
    s = s.replace(old, new, 1)

# Translate user-facing Shizuku messages.
translations = {
    "Shizuku granted! Bisa mulai merge.": "Shizuku permission granted! You can start merging.",
    "⚠ Shizuku belum berjalan. Install & aktifkan Shizuku terlebih dulu.": "⚠ Shizuku is not connected yet. Make sure Shizuku is running.",
    "⚠ Izin Shizuku belum diberikan. Tap untuk mengizinkan.": "⚠ Shizuku permission has not been granted. Tap to allow.",
    "Shizuku terlalu lama, upgrade ke v11+": "Shizuku is too old. Please update to v11 or newer.",
    "Shizuku tidak berjalan": "Shizuku is not connected",
}
for src, dst in translations.items():
    s = s.replace(src, dst)

main.write_text(s, encoding="utf-8")

# Give the patched build its own version number/name.
gradle = Path("upstream/app/build.gradle")
g = gradle.read_text(encoding="utf-8")
g = g.replace('versionCode 13', 'versionCode 14', 1)
g = g.replace('versionName "13.0-shizuku"', 'versionName "14.0-shizuku-binder-fix"', 1)
gradle.write_text(g, encoding="utf-8")

print("Applied Shizuku binder refresh + English UI patch")
