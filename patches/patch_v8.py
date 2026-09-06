from pathlib import Path

# Applied after v6 + v7 patches. Android blocks the Shizuku shell UID from
# executing a binary copied into the app's private /data/user/0/.../files dir.
# Extract the bundled executable from the APK *inside the Shizuku UserService*
# to /data/local/tmp instead, where shell-owned executables are expected to run.

user = Path("upstream/app/src/main/java/com/joyconmerge/UserService.java")
us = user.read_text(encoding="utf-8")

old_fields = '''    private Process mergeProcess = null;\n    private DataOutputStream procStdin = null;\n    private final LinkedBlockingQueue<String> statusQueue = new LinkedBlockingQueue<>(200);\n    private volatile boolean running = false;\n'''
new_fields = '''    private Process mergeProcess = null;\n    private DataOutputStream procStdin = null;\n    private final LinkedBlockingQueue<String> statusQueue = new LinkedBlockingQueue<>(200);\n    private volatile boolean running = false;\n    private Context appContext = null;\n'''
if old_fields not in us:
    raise RuntimeError("Could not locate UserService fields")
us = us.replace(old_fields, new_fields, 1)

old_ctor = '''    // Context disuntikkan oleh Shizuku saat konstruksi\n    public UserService(Context context) {\n        // Context di sini adalah context app kita — dibutuhkan untuk getFilesDir()\n    }\n\n    // Constructor tanpa arg juga dibutuhkan oleh Shizuku\n    public UserService() {}\n'''
new_ctor = '''    // Shizuku API v13+ supplies a package Context. Keep it so the shell-side\n    // process can read our APK assets without trying to enter app-private data.\n    public UserService(Context context) {\n        this.appContext = context;\n    }\n\n    // Older Shizuku fallback. Our current setup uses v13+, but keep this for\n    // compatibility and report a clear error if asset extraction is attempted.\n    public UserService() {}\n'''
if old_ctor not in us:
    raise RuntimeError("Could not locate UserService constructors")
us = us.replace(old_ctor, new_ctor, 1)

old_start = '''        try {\n            // Pastikan binary executable\n            File binary = new File(args[0]);\n            if (!binary.canExecute()) {\n                binary.setExecutable(true, false);\n            }\n\n            ProcessBuilder pb = new ProcessBuilder(args);\n            pb.redirectErrorStream(false);\n            mergeProcess = pb.start();\n'''
new_start = '''        try {\n            // Do NOT execute args[0] from /data/user/0/<package>/files.\n            // On modern Android the Shizuku shell process is denied traversal/exec\n            // there even if the file mode contains +x. Instead, extract the same\n            // APK asset as shell into /data/local/tmp and execute that copy.\n            String[] execArgs = args.clone();\n            File binary = prepareShellBinary();\n            execArgs[0] = binary.getAbsolutePath();\n\n            ProcessBuilder pb = new ProcessBuilder(execArgs);\n            pb.redirectErrorStream(false);\n            mergeProcess = pb.start();\n'''
if old_start not in us:
    raise RuntimeError("Could not locate UserService.startMerge launch block")
us = us.replace(old_start, new_start, 1)

stop_marker = '''    // ─────────────────────────────────────────────────────────────────────────\n    // stopMerge\n    // ─────────────────────────────────────────────────────────────────────────\n'''
helper = '''    /**\n     * Extract the native helper from our APK while already running as the\n     * Shizuku shell UID. /data/local/tmp is writable/executable by shell and is\n     * the standard location used for adb shell helper binaries.\n     */\n    private File prepareShellBinary() throws IOException {\n        if (appContext == null) {\n            throw new IOException("Shizuku did not provide app Context; cannot read bundled native helper");\n        }\n\n        String abi = android.os.Build.SUPPORTED_ABIS.length > 0\n                ? android.os.Build.SUPPORTED_ABIS[0] : "arm64-v8a";\n        if (!abi.equals("arm64-v8a") && !abi.equals("armeabi-v7a")) abi = "arm64-v8a";\n        String assetName = "uinput_setup_" + abi;\n        File binary = new File("/data/local/tmp",\n                "joyconmerge_uinput_setup_" + abi.replace('-', '_'));\n        File tmp = new File(binary.getAbsolutePath() + ".tmp");\n\n        if (tmp.exists()) tmp.delete();\n        try (java.io.InputStream in = appContext.getAssets().open(assetName);\n             FileOutputStream out = new FileOutputStream(tmp, false)) {\n            byte[] buf = new byte[8192];\n            int n;\n            while ((n = in.read(buf)) > 0) out.write(buf, 0, n);\n            out.flush();\n        }\n\n        if (binary.exists() && !binary.delete()) {\n            throw new IOException("Could not replace old shell helper: " + binary);\n        }\n        if (!tmp.renameTo(binary)) {\n            throw new IOException("Could not install shell helper into /data/local/tmp");\n        }\n\n        // File#setExecutable is normally sufficient because this process is UID\n        // shell. Run Android's chmod as a second, explicit safeguard.\n        binary.setReadable(true, false);\n        binary.setWritable(true, true);\n        binary.setExecutable(true, false);\n        try {\n            Process chmod = new ProcessBuilder("/system/bin/chmod", "755",\n                    binary.getAbsolutePath()).start();\n            int rc = chmod.waitFor();\n            if (rc != 0) throw new IOException("chmod returned " + rc);\n        } catch (InterruptedException e) {\n            Thread.currentThread().interrupt();\n            throw new IOException("Interrupted while preparing native helper", e);\n        }\n\n        if (!binary.canExecute()) {\n            throw new IOException("Native helper is still not executable at " + binary);\n        }\n        return binary;\n    }\n\n'''
if stop_marker not in us:
    raise RuntimeError("Could not locate stopMerge marker")
us = us.replace(stop_marker, helper + stop_marker, 1)
user.write_text(us, encoding="utf-8")

# Distinct v8 version. v7 has already changed 18 -> 19.
gradle = Path("upstream/app/build.gradle")
g = gradle.read_text(encoding="utf-8")
g = g.replace('versionCode 19', 'versionCode 20', 1)
g = g.replace('versionName "19.0-controller-ui-fix"', 'versionName "20.0-shell-exec-fix"', 1)
gradle.write_text(g, encoding="utf-8")

print("Applied v8: execute uinput helper from shell-owned /data/local/tmp")
