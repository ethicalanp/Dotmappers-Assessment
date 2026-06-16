import sys
import subprocess
import time

def main():
    print("=" * 60)
    print("Starting PDF QA Engine System...")
    print("   - Backend API:  http://localhost:8000")
    print("   - Frontend UI:  http://localhost:8501")
    print("=" * 60)
    
    # Launch uvicorn and streamlit using the current python executable to guarantee correct env
    api_cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    ui_cmd = [sys.executable, "-m", "streamlit", "run", "app/ui.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
    
    try:
        api_proc = subprocess.Popen(api_cmd)
        ui_proc = subprocess.Popen(ui_cmd)
        
        print("\nBoth servers started! Press Ctrl+C in this terminal to stop them.")
        
        while True:
            # Poll status of processes
            api_exit = api_proc.poll()
            ui_exit = ui_proc.poll()
            
            if api_exit is not None:
                print(f"\nBackend API stopped (code {api_exit}). Stopping UI...")
                ui_proc.terminate()
                break
                
            if ui_exit is not None:
                print(f"\nFrontend UI stopped (code {ui_exit}). Stopping API...")
                api_proc.terminate()
                break
                
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down servers gracefully...")
        api_proc.terminate()
        ui_proc.terminate()
        
        # Wait for processes to exit
        api_proc.wait()
        ui_proc.wait()
        print("Done. Goodbye!")
        
if __name__ == "__main__":
    main()
