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

# Manual selector consumes entries in the form path|human readable name.
old_fn = '''    private void updatePathSpinners(List<String> paths) {\n        eventPaths.clear();\n        eventPaths.addAll(paths);\n        List<String> labels = new ArrayList<>(paths);\n        if (labels.isEmpty()) {\n            Toast.makeText(this, "Tidak ada Joy-Con event device ditemukan", Toast.LENGTH_LONG).show();\n            return;\n        }\n        ArrayAdapter<String> adL = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, new ArrayList<>(labels));\n        adL.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);\n        spLeftPath.setAdapter(adL);\n        ArrayAdapter<String> adR = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, new ArrayList<>(labels));\n        adR.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);\n        spRightPath.setAdapter(adR);\n        for (int i = 0; i < labels.size(); i++) {\n            if (labels.get(i).toLowerCase().contains("left")) { spLeftPath.setSelection(i); break; }\n        }\n        for (int i = labels.size()-1; i >= 0; i--) {\n            if (labels.get(i).toLowerCase().contains("right")) { spRightPath.setSelection(i); break; }\n        }\n        Toast.makeText(this, "✓ " + paths.size() + " device. Pilih L dan R, lalu Start.", Toast.LENGTH_LONG).show();\n    }\n'''
new_fn = '''    private void updatePathSpinners(List<String> entries) {\n        eventPaths.clear();\n        List<String> labels = new ArrayList<>();\n        for (String entry : entries) {\n            String[] parts = entry.split("\\\\|", 2);\n            String path = parts[0].trim();\n            String name = parts.length > 1 ? parts[1].trim() : "";\n            if (path.isEmpty()) continue;\n            eventPaths.add(path);\n            labels.add(name.isEmpty() ? path + " — [name unavailable]" : name + " — " + path);\n        }\n        if (labels.isEmpty()) {\n            Toast.makeText(this, "No input devices were found", Toast.LENGTH_LONG).show();\n            return;\n        }\n        ArrayAdapter<String> adL = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, new ArrayList<>(labels));\n        adL.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);\n        spLeftPath.setAdapter(adL);\n        ArrayAdapter<String> adR = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, new ArrayList<>(labels));\n        adR.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);\n        spRightPath.setAdapter(adR);\n\n        for (int i = 0; i < labels.size(); i++) {\n            String l = labels.get(i).toLowerCase();\n            if ((l.contains("joy-con") || l.contains("joycon")) &&\n                (l.contains("left") || l.contains("(l)") || l.contains(" l —"))) {\n                spLeftPath.setSelection(i);\n                break;\n            }\n        }\n        for (int i = labels.size()-1; i >= 0; i--) {\n            String l = labels.get(i).toLowerCase();\n            if ((l.contains("joy-con") || l.contains("joycon")) &&\n                (l.contains("right") || l.contains("(r)") || l.contains(" r —"))) {\n                spRightPath.setSelection(i);\n                break;\n            }\n        }\n        Toast.makeText(this, "✓ " + labels.size() + " input devices found", Toast.LENGTH_LONG).show();\n    }\n'''
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

# Backend scanner. Samsung hides names through both sysfs and proc on this tablet.
# The Shizuku UserService runs as shell UID, so ask Android's own getevent utility
# for the event-node/name mapping first. Fall back to /proc and finally /dev/input.
user = Path("upstream/app/src/main/java/com/joyconmerge/UserService.java")
us = user.read_text(encoding="utf-8")
old_scan = '''    @Override\n    public String scanDevices() {\n        StringBuilder sb = new StringBuilder();\n        File inputDir = new File("/dev/input");\n        File[] events = inputDir.listFiles();\n        if (events == null) return "";\n\n        for (File evFile : events) {\n            if (!evFile.getName().startsWith("event")) continue;\n            String path = evFile.getAbsolutePath();\n            String base = evFile.getName(); // e.g. "event3"\n            String namePath = "/sys/class/input/" + base + "/device/name";\n            String name = readSysFile(namePath).trim();\n            sb.append(path).append("|").append(name).append("\\n");\n        }\n        return sb.toString();\n    }\n'''
new_scan = '''    @Override\n    public String scanDevices() {\n        StringBuilder sb = new StringBuilder();\n        java.util.LinkedHashMap<String, String> found = new java.util.LinkedHashMap<>();\n\n        // Preferred source: Android's getevent tool, executed as the Shizuku shell UID.\n        try {\n            Process proc = new ProcessBuilder("/system/bin/getevent", "-lp")\n                    .redirectErrorStream(true).start();\n            try (BufferedReader br = new BufferedReader(\n                    new InputStreamReader(proc.getInputStream()))) {\n                String line;\n                String currentPath = null;\n                String currentName = "";\n                while ((line = br.readLine()) != null) {\n                    String t = line.trim();\n                    if (t.startsWith("add device")) {\n                        if (currentPath != null) found.put(currentPath, currentName);\n                        currentPath = null;\n                        currentName = "";\n                        int p = t.indexOf("/dev/input/event");\n                        if (p >= 0) currentPath = t.substring(p).trim();\n                    } else if (currentPath != null && t.startsWith("name:")) {\n                        currentName = t.substring("name:".length()).trim();\n                        if (currentName.startsWith("\\\"") && currentName.endsWith("\\\"") && currentName.length() >= 2)\n                            currentName = currentName.substring(1, currentName.length() - 1);\n                    }\n                }\n                if (currentPath != null) found.put(currentPath, currentName);\n            }\n            try { proc.waitFor(); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }\n        } catch (IOException ignored) {}\n\n        // Fallback: /proc/bus/input/devices.\n        if (found.isEmpty()) {\n            try (BufferedReader br = new BufferedReader(\n                    new InputStreamReader(new FileInputStream("/proc/bus/input/devices")))) {\n                String line;\n                String currentName = "";\n                while ((line = br.readLine()) != null) {\n                    line = line.trim();\n                    if (line.startsWith("N: Name=")) {\n                        currentName = line.substring("N: Name=".length()).trim();\n                        if (currentName.startsWith("\\\"") && currentName.endsWith("\\\"") && currentName.length() >= 2)\n                            currentName = currentName.substring(1, currentName.length() - 1);\n                    } else if (line.startsWith("H: Handlers=")) {\n                        String handlers = line.substring("H: Handlers=".length()).trim();\n                        for (String h : handlers.split("\\\\s+")) {\n                            if (h.matches("event\\\\d+")) found.put("/dev/input/" + h, currentName);\n                        }\n                    } else if (line.isEmpty()) {\n                        currentName = "";\n                    }\n                }\n            } catch (IOException ignored) {}\n        }\n\n        // Always add any event nodes not reported above.\n        File inputDir = new File("/dev/input");\n        File[] events = inputDir.listFiles();\n        if (events != null) {\n            java.util.Arrays.sort(events, (a,b) -> a.getName().compareTo(b.getName()));\n            for (File evFile : events) {\n                if (!evFile.getName().startsWith("event")) continue;\n                String path = evFile.getAbsolutePath();\n                if (!found.containsKey(path)) {\n                    String namePath = "/sys/class/input/" + evFile.getName() + "/device/name";\n                    found.put(path, readSysFile(namePath).trim());\n                }\n            }\n        }\n\n        for (java.util.Map.Entry<String, String> e : found.entrySet()) {\n            sb.append(e.getKey()).append("|").append(e.getValue() == null ? "" : e.getValue()).append("\\n");\n        }\n        return sb.toString();\n    }\n'''
if old_scan not in us:
    raise RuntimeError("Could not locate UserService.scanDevices")
us = us.replace(old_scan, new_scan, 1)
user.write_text(us, encoding="utf-8")

# MergeService preserves path|name entries for the UI and uses broader matching.
merge = Path("upstream/app/src/main/java/com/joyconmerge/MergeService.java")
ms = merge.read_text(encoding="utf-8")
ms = ms.replace(
    '            if (!result.allPaths.contains(path)) result.allPaths.add(path);',
    '            String display = name.isEmpty() ? path : path + "|" + name;\n            if (!result.allPaths.contains(display)) result.allPaths.add(display);',
    1
)
old_detect = '''            if (lname.contains("left joy-con") && result.autoLeft.isEmpty())\n                result.autoLeft = path;\n            else if (lname.contains("right joy-con") && result.autoRight.isEmpty())\n                result.autoRight = path;\n'''
new_detect = '''            boolean joy = lname.contains("joy-con") || lname.contains("joycon");\n            boolean isLeft = joy && (lname.contains("left") || lname.contains("(l)") ||\n                    lname.endsWith(" l") || lname.contains("joy-con l") || lname.contains("joycon l"));\n            boolean isRight = joy && (lname.contains("right") || lname.contains("(r)") ||\n                    lname.endsWith(" r") || lname.contains("joy-con r") || lname.contains("joycon r"));\n            if (isLeft && result.autoLeft.isEmpty())\n                result.autoLeft = path;\n            else if (isRight && result.autoRight.isEmpty())\n                result.autoRight = path;\n'''
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

# Distinct v6 build.
gradle = Path("upstream/app/build.gradle")
g = gradle.read_text(encoding="utf-8")
g = g.replace('versionCode 13', 'versionCode 18', 1)
g = g.replace('versionName "13.0-shizuku"', 'versionName "18.0-getevent-detection"', 1)
gradle.write_text(g, encoding="utf-8")

print("Applied v6: getevent device-name scanner + Shizuku fixes")
