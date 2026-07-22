import threading
import subprocess
import time
import json
import os
import sys
from datetime import datetime, UTC


# =====================================================
# EXECUTION ENGINE THREAD
# =====================================================

def run_engine():
    """Запуск paper execution engine"""

    try:
        import execution_engine

        execution_engine.run()

    except Exception as e:
        print(f"❌ Engine crashed: {e}")


# =====================================================
# STREAMLIT PROCESS
# =====================================================

def run_dashboard():
    """Запуск Streamlit dashboard"""

    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "dashboard.py",
            "--server.headless=true"
        ]
    )


# =====================================================
# MAIN
# =====================================================

def main():

    print("🚀 SOL Pullback v4 - Unified Launcher")

    # Запускаем engine в фоне
    engine_thread = threading.Thread(
        target=run_engine,
        daemon=True
    )

    engine_thread.start()

    print("🧠 Execution engine started")

    # Даём engine инициализироваться
    time.sleep(2)

    # Запускаем dashboard
    dashboard_process = run_dashboard()

    print("📊 Dashboard started")
    print("🌐 Open: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop")

    try:
        # Держим main живым
        while True:
            time.sleep(1)

            # Если dashboard умер — выходим
            if dashboard_process.poll() is not None:
                print("⚠️ Dashboard stopped")
                break

    except KeyboardInterrupt:

        print("\\n⛔ Stopping system...")

        dashboard_process.terminate()

        try:
            dashboard_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            dashboard_process.kill()

        print("✅ System stopped")


if __name__ == "__main__":
    main()