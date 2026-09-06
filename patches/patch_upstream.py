from pathlib import Path

main = Path("upstream/app/src/main/java/com/joyconmerge/MainActivity.java")
s = main.read_text(encoding="utf-8")

# Refresh the UI when the Shizuku binder arrives/dies.
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
        raise RuntimeError("Could not locate Shizuku listener registration")
    s = s.replace(old, new, 1)

old = '''    protected void onResume() {\n        super.onResume();\n        updateShizukuBanner();\n    }\n'''
new = '''    protected void onResume() {\n        super.onResume();\n        updateShizukuBanner();\n        shizukuBanner.postDelayed(this::updateShizukuBanner, 500);\n        shizukuBanner.postDelayed(this::updateShizukuBanner, 1500);\n    }\n'''
if new not in s:
    if old not in s:
        raise RuntimeError("Could not locate onResume")
    s = s.replace(old, new, 1)

old = "        Shizuku.removeRequestPermissionResultListener(shizukuPermResult);\n"
new = "        Shizuku.removeRequestPermissionResultListener(shizukuPermResult);\n        Shizuku.removeBinderReceivedListener(shizukuBinderReceivedListener);\n        Shizuku.removeBinderDeadListener(shizukuBinderDeadListener);\n"
if new not in s:
    if old not in s:
        raise RuntimeError("Could not locate onDestroy cleanup")
    s = s.replace(old, new, 1)

# Replace the anonymous /dev/input/eventXX manual selectors with readable
# "device name — path" labels while keeping the real path separately.
old_fn = '''    private void updatePathSpinners(List<String> paths) {\n        eventPaths.clear();\n        eventPaths.addAll(paths);\n        List<String> labels = new ArrayList<>(paths);\n        if (labels.isEmpty()) {\n            Toast.makeText(this, "Tidak ada Joy-Con event device ditemukan", Toast.LENGTH_LONG).show();\n            return;\n        }\n        ArrayAdapter<String> adL = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, new ArrayList<>(labels));\n        adL.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);\n        spLeftPath.setAdapter(adL);\n        ArrayAdapter<String> adR = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, new ArrayList<>(labels));\n        adR.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);\n        spRightPath.setAdapter(adR);\n        for (int i = 0; i < labels.size(); i++) {\n            if (labels.get(i).toLowerCase().contains("left")) { spLeftPath.setSelection(i); break; }\n        }\n        for (int i = labels.size()-1; i >= 0; i--) {\n            if (labels.get(i).toLowerCase().contains("right")) { spRightPath.setSelection(i); break; }\n        }\n        Toast.makeText(this, "✓ " + paths.size() + " device. Pilih L dan R, lalu Start.", Toast.LENGTH_LONG).show();\n    }\n'''
new_fn = '''    private void updatePathSpinners(List<String> entries) {\n        eventPaths.clear();\n        List<String> labels = new ArrayList<>();\n        for (String entry : entries) {\n            String[] parts = entry.split("\\\\|", 2);\n            String path = parts[0].trim();\n            String name = parts.length > 1 ? parts[1].trim() : "";\n            if (path.isEmpty()) continue;\n            eventPaths.add(path);\n            labels.add(name.isEmpty() ? path : name + " — " + path);\n        }\n        if (labels.isEmpty()) {\n            Toast.makeText(this, "No input devices were found", Toast.LENGTH_LONG).show();\n            return;\n        }\n        ArrayAdapter<String> adL = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, new ArrayList<>(labels));\n        adL.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);\n        spLeftPath.setAdapter(adL);\n        ArrayAdapter<String> adR = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, new ArrayList<>(labels));\n        adR.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);\n        spRightPath.setAdapter(adR);\n\n        for (int i = 0; i < labels.size(); i++) {\n            String l = labels.get(i).toLowerCase();\n            if (l.contains("left joy-con") || l.contains("joy-con (l)") || l.contains("joy-con l") ||\n                l.contains("joycon (l)") || l.contains("joycon l")) {\n                spLeftPath.setSelection(i);\n                break;\n            }\n        }\n        for (int i = labels.size()-1; i >= 0; i--) {\n            String l = labels.get(i).toLowerCase();\n            if (l.contains("right joy-con") || l.contains("joy-con (r)") || l.contains("joy-con r") ||\n                l.contains("joycon (r)") || l.contains("joycon r")) {\n                spRightPath.setSelection(i);\n                break;\n            }\n        }\n        Toast.makeText(this, "✓ " + labels.size() + " input devices found. Joy-Con names are now shown in the lists.", Toast.LENGTH_LONG).show();\n    }\n'''
if new_fn not in s:
    if old_fn not in s:
        raise RuntimeError("Could not locate updatePathSpinners")
    s = s.replace(old_fn, new_fn, 1)

translations = {
    "Shizuku granted! Bisa mulai merge.": "Shizuku permission granted! You can start merging.",
    "⚠ Shizuku belum berjalan. Install & aktifkan Shizuku terlebih dulu.": "⚠ Shizuku is not connected yet. Make sure Shizuku is running.",
    "⚠ Izin Shizuku belum diberikan. Tap untuk mengizinkan.": "⚠ Shizuku permission has not been granted. Tap to allow.",
    "Shizuku terlalu lama, upgrade ke v11+": "Shizuku is too old. Please update to v11 or newer.",
    "Shizuku tidak berjalan": "Shizuku is not connected",
    "Berikan izin Shizuku dulu!": "Grant Shizuku permission first!",
    "Service belum siap": "Service is not ready yet",
    "Scan dulu path-nya pakai tombol 🔍": "Scan devices first using the Scan Devices button",
    "Left dan Right path tidak boleh sama!": "Left and Right Joy-Cons cannot use the same device path!",
}
for src, dst in translations.items():
    s = s.replace(src, dst)
main.write_text(s, encoding="utf-8")

# Improve the backend scanner: preserve device names for the manual UI and
# recognise several common Linux/Android Joy-Con naming styles.
merge = Path("upstream/app/src/main/java/com/joyconmerge/MergeService.java")
ms = merge.read_text(encoding="utf-8")
ms = ms.replace(
    '            if (!result.allPaths.contains(path)) result.allPaths.add(path);',
    '            String display = name.isEmpty() ? path : path + "|" + name;\n            if (!result.allPaths.contains(display)) result.allPaths.add(display);',
    1
)
old_detect = '''            if (lname.contains("left joy-con") && result.autoLeft.isEmpty())\n                result.autoLeft = path;\n            else if (lname.contains("right joy-con") && result.autoRight.isEmpty())\n                result.autoRight = path;\n'''
new_detect = '''            boolean isLeft = lname.contains("left joy-con") || lname.contains("joy-con (l)") ||\n                    lname.contains("joy-con l") || lname.contains("joycon (l)") || lname.contains("joycon l");\n            boolean isRight = lname.contains("right joy-con") || lname.contains("joy-con (r)") ||\n                    lname.contains("joy-con r") || lname.contains("joycon (r)") || lname.contains("joycon r");\n            if (isLeft && result.autoLeft.isEmpty())\n                result.autoLeft = path;\n            else if (isRight && result.autoRight.isEmpty())\n                result.autoRight = path;\n'''
if new_detect not in ms:
    if old_detect not in ms:
        raise RuntimeError("Could not locate Joy-Con auto detection block")
    ms = ms.replace(old_detect, new_detect, 1)
ms = ms.replace("ERROR: Left Joy-Con not found — gunakan Manual Override", "ERROR: Left Joy-Con not found — use Manual Override")
ms = ms.replace("ERROR: Shizuku service not ready — coba lagi", "ERROR: Shizuku service not ready — try again")
merge.write_text(ms, encoding="utf-8")

# Required Shizuku provider.
manifest = Path("upstream/app/src/main/AndroidManifest.xml")
m = manifest.read_text(encoding="utf-8")
provider_block = '''\n        <!-- Required by Shizuku to deliver its Binder to this app. -->\n        <provider\n            android:name="rikka.shizuku.ShizukuProvider"\n            android:authorities="${applicationId}.shizuku"\n            android:enabled="true"\n            android:exported="true"\n            android:multiprocess="false"\n            android:permission="android.permission.INTERACT_ACROSS_USERS_FULL" />\n'''
if 'android:name="rikka.shizuku.ShizukuProvider"' not in m:
    insert_before = '\n    </application>'
    if insert_before not in m:
        raise RuntimeError("Could not locate </application> in manifest")
    m = m.replace(insert_before, provider_block + insert_before, 1)
manifest.write_text(m, encoding="utf-8")

# Distinct v4 build.
gradle = Path("upstream/app/build.gradle")
g = gradle.read_text(encoding="utf-8")
g = g.replace('versionCode 13', 'versionCode 16', 1)
g = g.replace('versionName "13.0-shizuku"', 'versionName "16.0-named-joycon-detection"', 1)
gradle.write_text(g, encoding="utf-8")

print("Applied v4: Shizuku fixes + named Joy-Con selectors + broader detection")
