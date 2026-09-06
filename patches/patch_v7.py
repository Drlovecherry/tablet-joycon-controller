from pathlib import Path

# This patch is applied after patch_upstream.py (v6).

main = Path("upstream/app/src/main/java/com/joyconmerge/MainActivity.java")
s = main.read_text(encoding="utf-8")

# Do not offer Joy-Con IMU/sensor event nodes as controller choices.
s = s.replace(
    '            if (path.isEmpty()) continue;\n            eventPaths.add(path);',
    '            if (path.isEmpty()) continue;\n            if (name.toLowerCase().contains("imu")) continue;\n            eventPaths.add(path);',
    1
)

# Make the virtual output button names understandable without knowing Linux input jargon.
old_names = '''    private static final String[] BTN_NAMES = {\n        "BTN_SOUTH (B/Cross)", "BTN_EAST (A/Circle)", "BTN_NORTH (Y/Triangle)",\n        "BTN_WEST (X/Square)", "BTN_TL (L)", "BTN_TR (R)", "BTN_TL2 (ZL)", "BTN_TR2 (ZR)",\n        "BTN_SELECT (−)", "BTN_START (+)", "BTN_THUMBL (L3)", "BTN_THUMBR (R3)"\n    };'''
new_names = '''    private static final String[] BTN_NAMES = {\n        "B — bottom face button (BTN_SOUTH)",\n        "A — right face button (BTN_EAST)",\n        "Y — top face button (BTN_NORTH)",\n        "X — left face button (BTN_WEST)",\n        "L — left shoulder (BTN_TL)",\n        "R — right shoulder (BTN_TR)",\n        "ZL — left trigger (BTN_TL2)",\n        "ZR — right trigger (BTN_TR2)",\n        "− / Minus (BTN_SELECT)",\n        "+ / Plus (BTN_START)",\n        "L3 — press left stick (BTN_THUMBL)",\n        "R3 — press right stick (BTN_THUMBR)"\n    };'''
if old_names not in s:
    raise RuntimeError("Could not locate BTN_NAMES")
s = s.replace(old_names, new_names, 1)
main.write_text(s, encoding="utf-8")

# Auto detection must ignore IMU nodes too.
merge = Path("upstream/app/src/main/java/com/joyconmerge/MergeService.java")
ms = merge.read_text(encoding="utf-8")
old_joy = '            boolean joy = lname.contains("joy-con") || lname.contains("joycon");'
new_joy = '            boolean joy = (lname.contains("joy-con") || lname.contains("joycon")) && !lname.contains("imu");'
if old_joy not in ms:
    raise RuntimeError("Could not locate Joy-Con detection line")
ms = ms.replace(old_joy, new_joy, 1)
merge.write_text(ms, encoding="utf-8")

# Add an in-app legend on Remap and a usage note on Test.
layout = Path("upstream/app/src/main/res/layout/activity_main.xml")
x = layout.read_text(encoding="utf-8")

remap_anchor = '''        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="vertical" android:padding="16dp">\n            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="vertical" android:background="@drawable/card_bg" android:padding="12dp">\n                <TextView android:layout_width="match_parent" android:layout_height="wrap_content" android:text="Right Joy-Con Buttons"'''
remap_replacement = '''        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="vertical" android:padding="16dp">\n            <TextView\n                android:layout_width="match_parent"\n                android:layout_height="wrap_content"\n                android:background="@drawable/card_bg"\n                android:padding="12dp"\n                android:layout_marginBottom="12dp"\n                android:text="Button legend\nB = bottom • A = right • Y = top • X = left\nL / R = shoulder buttons • ZL / ZR = triggers\n+ / − = Plus / Minus • L3 / R3 = press the analogue stick\n\nBTN_… is Android/Linux's name for the virtual controller button."\n                android:textColor="#E0E0E0"\n                android:textSize="12sp" />\n            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="vertical" android:background="@drawable/card_bg" android:padding="12dp">\n                <TextView android:layout_width="match_parent" android:layout_height="wrap_content" android:text="Right Joy-Con Buttons"'''
if remap_anchor not in x:
    raise RuntimeError("Could not locate Remap tab anchor")
x = x.replace(remap_anchor, remap_replacement, 1)

test_anchor = '''    <LinearLayout android:id="@+id/tab_test" android:layout_width="match_parent" android:layout_height="match_parent" android:orientation="vertical" android:padding="16dp" android:visibility="gone">\n        <com.joyconmerge.GamepadView'''
test_replacement = '''    <LinearLayout android:id="@+id/tab_test" android:layout_width="match_parent" android:layout_height="match_parent" android:orientation="vertical" android:padding="16dp" android:visibility="gone">\n        <TextView\n            android:layout_width="match_parent"\n            android:layout_height="wrap_content"\n            android:background="@drawable/card_bg"\n            android:padding="10dp"\n            android:layout_marginBottom="8dp"\n            android:text="For the most reliable test, press START on the Status tab first. Before merging, Android sees the Left and Right Joy-Cons as separate devices, so this diagram may show only part of the controls."\n            android:textColor="#B0BEC5"\n            android:textSize="12sp" />\n        <com.joyconmerge.GamepadView'''
if test_anchor not in x:
    raise RuntimeError("Could not locate Test tab anchor")
x = x.replace(test_anchor, test_replacement, 1)
layout.write_text(x, encoding="utf-8")

# Distinct v7 version after the v6 patch has already bumped it to 18.
gradle = Path("upstream/app/build.gradle")
g = gradle.read_text(encoding="utf-8")
g = g.replace('versionCode 18', 'versionCode 19', 1)
g = g.replace('versionName "18.0-getevent-detection"', 'versionName "19.0-controller-ui-fix"', 1)
gradle.write_text(g, encoding="utf-8")

print("Applied v7: exclude IMU nodes + clearer remap legend + Test guidance")
