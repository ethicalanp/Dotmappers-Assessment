import sys
import os
import subprocess
import signal
import time

def get_node_path():
    """Find npm.cmd on Windows regardless of PATH."""
    # Try to refresh PATH from environment
    machine_path = os.environ.get("PATH", "")
    user_path = ""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment") as k:
            machine_path, _ = winreg.QueryValueEx(k, "PATH")
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as k:
            try:
                user_path, _ = winreg.QueryValueEx(k, "PATH")
            except FileNotFoundError:
                pass
    except Exception:
        pass

    full_path = machine_path + os.pathsep + user_path
    os.environ["PATH"] = full_path

    # Common Node.js install locations
    candidates = [
        r"C:\Program Files\nodejs\npm.cmd",
        r"C:\Program Files (x86)\nodejs\npm.cmd",
        os.path.join(os.environ.get("APPDATA", ""), r"npm\npm.cmd"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c

    return "npm.cmd"  # fallback, hope it's in PATH

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(base_dir, "frontend")
    npm = get_node_path()

    print("=" * 60)
    print("  Support Ticket AI Dashboard")
    print("  FastAPI  -> http://localhost:8000")
    print("  React UI -> http://localhost:5173")
    print("=" * 60)

    processes = []

    try:
        # Start FastAPI backend
        api_proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app",
             "--host", "0.0.0.0", "--port", "8000"],
            cwd=base_dir
        )
        processes.append(api_proc)
        print("[1/2] FastAPI backend started (PID %d)" % api_proc.pid)

        # Give API a moment to start
        time.sleep(2)

        # Start React dev server
        react_proc = subprocess.Popen(
            [npm, "run", "dev"],
            cwd=frontend_dir,
            shell=False
        )
        processes.append(react_proc)
        print("[2/2] React frontend started  (PID %d)" % react_proc.pid)
        print()
        print("Both servers running. Open: http://localhost:5173")
        print("Press Ctrl+C to stop everything.")
        print("=" * 60)

        # Wait — if either process dies, stop both
        while True:
            for p in processes:
                if p.poll() is not None:
                    print("\nA server stopped unexpectedly. Shutting down...")
                    raise KeyboardInterrupt
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping all servers...")
        for p in processes:
            try:
                if sys.platform == "win32":
                    subprocess.call(["taskkill", "/F", "/T", "/PID", str(p.pid)],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    os.killpg(os.getpgid(p.pid), signal.SIGTERM)
            except Exception:
                p.terminate()
        print("All servers stopped.")

if __name__ == "__main__":
    main()
