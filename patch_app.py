#!/usr/bin/env python3
"""
Patch for app.py to disable NIM subprocess launching in all-in-one container.
Services are managed by supervisor instead.
"""

import sys
from pathlib import Path

def patch_app_py():
    app_path = Path("/app/app.py")
    
    if not app_path.exists():
        print("app.py not found!")
        return False
    
    content = app_path.read_text()
    
    # Check if already patched
    if "ALLINONE_CONTAINER" in content:
        print("app.py already patched")
        return True
    
    # Find and replace the NIM startup functions
    original_llm_function = '''def _ensure_llm_nim_started():
    """Start the LLM NIM container in the background if it's not already healthy."""
    global _nim_bootstrap_started
    if _nim_bootstrap_started:
        return
    _nim_bootstrap_started = True

    health_url = f"{config.LLM_BASE_URL}/v1/health/ready"
    try:
        resp = requests.get(health_url, timeout=1.5)
        if resp.status_code == 200:
            print("LLM NIM already running")
            return
    except Exception:
        pass

    def _runner():
        global _nim_process
        try:
            script_path = Path(__file__).parent / "nim_llm" / "run_llama.py"
            print(f"Starting LLM NIM via {script_path}")
            popen_kwargs = {}
            if os.name == "nt":
                popen_kwargs["creationflags"] = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            else:
                popen_kwargs["start_new_session"] = True
            _nim_process = subprocess.Popen([sys.executable, str(script_path)], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, **popen_kwargs)
        except Exception as e:
            print(f"Failed to start LLM NIM: {e}")

    threading.Thread(target=_runner, daemon=True).start()'''
    
    patched_llm_function = '''def _ensure_llm_nim_started():
    """In all-in-one container, services are managed by supervisor."""
    # ALLINONE_CONTAINER: Services managed by supervisor, skip subprocess launch
    global _nim_bootstrap_started
    if _nim_bootstrap_started:
        return
    _nim_bootstrap_started = True
    
    # Just check if service is ready (supervisor already started it)
    health_url = f"{config.LLM_BASE_URL}/v1/health/ready"
    print("Waiting for LLM service (managed by supervisor)...")
    import time
    for i in range(60):  # Wait up to 60 seconds
        try:
            resp = requests.get(health_url, timeout=2)
            if resp.status_code == 200:
                print("LLM service is ready!")
                return
        except Exception:
            pass
        time.sleep(1)
    print("Warning: LLM service not responding after 60 seconds")'''
    
    original_trellis_function = '''def _ensure_trellis_nim_started():
    """Start the Trellis NIM container in the background if it's not already healthy."""
    global _trellis_bootstrap_started
    if _trellis_bootstrap_started:
        return
    _trellis_bootstrap_started = True

    health_url = f"{config.TRELLIS_BASE_URL}/health/ready"
    try:
        resp = requests.get(health_url, timeout=1.5)
        if resp.status_code == 200:
            print("Trellis NIM already running")
            return
    except Exception:
        pass

    def _runner():
        global _trellis_process
        try:
            script_path = Path(__file__).parent / "nim_trellis" / "run_trellis.py"
            print(f"Starting Trellis NIM via {script_path}")
            popen_kwargs = {}
            if os.name == "nt":
                popen_kwargs["creationflags"] = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            else:
                popen_kwargs["start_new_session"] = True
            _trellis_process = subprocess.Popen([sys.executable, str(script_path)], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, **popen_kwargs)
        except Exception as e:
            print(f"Failed to start Trellis NIM: {e}")

    threading.Thread(target=_runner, daemon=True).start()'''
    
    patched_trellis_function = '''def _ensure_trellis_nim_started():
    """In all-in-one container, services are managed by supervisor."""
    # ALLINONE_CONTAINER: Services managed by supervisor, skip subprocess launch
    global _trellis_bootstrap_started
    if _trellis_bootstrap_started:
        return
    _trellis_bootstrap_started = True
    
    # Just check if service is ready (supervisor already started it)
    health_url = f"{config.TRELLIS_BASE_URL}/health/ready"
    print("Waiting for TRELLIS service (managed by supervisor)...")
    import time
    for i in range(60):  # Wait up to 60 seconds
        try:
            resp = requests.get(health_url, timeout=2)
            if resp.status_code == 200:
                print("TRELLIS service is ready!")
                return
        except Exception:
            pass
        time.sleep(1)
    print("Warning: TRELLIS service not responding after 60 seconds")'''
    
    # Apply patches
    if original_llm_function in content:
        content = content.replace(original_llm_function, patched_llm_function)
        print("✓ Patched LLM NIM startup function")
    else:
        print("⚠ Could not find LLM NIM startup function to patch")
    
    if original_trellis_function in content:
        content = content.replace(original_trellis_function, patched_trellis_function)
        print("✓ Patched TRELLIS NIM startup function")
    else:
        print("⚠ Could not find TRELLIS NIM startup function to patch")
    
    # Write back
    app_path.write_text(content)
    print("✓ app.py patched successfully")
    return True

if __name__ == "__main__":
    success = patch_app_py()
    sys.exit(0 if success else 1)
