import psutil
import time
import platform

# --- Configuration ---
# Host to ping periodically (e.g., Google DNS)
TARGET_HOST = "8.8.8.8"
# How often to run the main monitoring loop (in seconds)
INTERVAL = 5 
# Size of the send buffer for network I/O (optional, for precision)
BYTES_TO_READ = 1024

def get_system_info():
    """Gathers and prints general CPU and Memory usage."""
    print("\n" + "="*50)
    print("          SYSTEM RESOURCE MONITORING")
    print("="*50)
    
    # 1. CPU Usage
    cpu_percent = psutil.cpu_percent(interval=1)  # Measure over 1 second
    print(f"CPU Utilization: {cpu_percent:.2f}%")

    # 2. Memory Usage
    mem = psutil.virtual_memory()
    total_mem_gb = mem.total / (1024**3)
    used_mem_gb = mem.used / (1024**3)
    percent_mem = mem.percent
    print(f"Memory Usage: {used_mem_gb:.2f} GB / {total_mem_gb:.2f} GB ({percent_mem:.1f}%)")
    
    # 3. System Info
    print(f"Operating System: {platform.system()} {platform.release()}")


def get_network_io():
    """
    Gathers and prints cumulative network I/O statistics since boot.
    Note: For real-time bandwidth, you'd need to sample these values 
    over an interval, which is done in the main loop.
    """
    print("\n" + "="*50)
    print("          NETWORK I/O MONITORING")
    print("="*50)
    
    # Get byte counts since boot
    net_io = psutil.net_io_counters()
    
    print(f"Bytes Sent (Total): {net_io.bytes_sent / (1024**2):.2f} MB")
    print(f"Bytes Received (Total): {net_io.bytes_recv / (1024**2):.2f} MB")
    
    # On a real-time basis, we'd use psutil.net_io_counters(pernic=True) 
    # and sample the difference.


def check_ping(host: str, count: int = 4):
    """Pings a target host and reports latency."""
    print("\n" + "="*50)
    print(f"          PING CHECK ({host})")
    print("="*50)
    
    # Use subprocess for system 'ping' command for reliable cross-platform testing
    import subprocess
    
    # Determine the correct ping utility based on the OS
    if platform.system().lower() == "windows":
        ping_command = ['ping', '-n', str(count), host]
    else: # Linux/macOS
        ping_command = ['ping', '-c', str(count), host]

    try:
        result = subprocess.run(
            ping_command, 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        print("--- Ping Output ---")
        print(result.stdout)
        if result.returncode != 0 and "unknown host" not in result.stdout.lower():
            print("WARNING: Ping command returned a non-zero exit code.")

    except subprocess.TimeoutExpired:
        print(f"ERROR: Ping command timed out while contacting {host}.")
    except FileNotFoundError:
        print(f"ERROR: 'ping' command not found. Are you on a standard OS?")
    except Exception as e:
        print(f"An unexpected error occurred during ping: {e}")


def main_monitoring_loop():
    """The main loop that orchestrates all monitoring tasks."""
    print(f"\n*** Starting Network Monitor ***")
    print(f"Monitoring interval set to {INTERVAL} seconds. Press Ctrl+C to stop.")

    # ---------------------------------------------------------------------
    # PHASE 1: Initial Setup Readings (for delta calculation later)
    # ---------------------------------------------------------------------
    # Get initial network counters
    last_net_stats = psutil.net_io_counters()
    
    # Perform an initial system reading right away
    get_system_info()
    
    print("\n--- Starting Live Monitoring Loop (Press Ctrl+C to exit) ---")

    try:
        while True:
            # --- Real-time Network I/O Bandwidth Calculation ---
            # Calculate the difference since the last call
            time.sleep(1) # Wait 1 second for more accurate delta
            current_net_stats = psutil.net_io_counters()
            
            # Calculate the rate (bytes/second)
            bytes_sent_rate = (current_net_stats.bytes_sent - last_net_stats.bytes_sent) / 1.0
            bytes_recv_rate = (current_net_stats.bytes_recv - last_net_stats.bytes_recv) / 1.0
            
            # Update the display with real-time data
            print("\n" + "*"*60)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] LIVE BANDWIDTH:")
            print(f"  -> Transmitted: {(bytes_sent_rate / (1024*1024)):.2f} MB/sec")
            print(f"  <- Received:   {(bytes_recv_rate / (1024*1024)):.2f} MB/sec")
            print("*"*60)
            
            # Update stats for next iteration
            last_net_stats = current_net_stats
            
            # --- Periodically run other stability checks ---
            if time.time() % (INTERVAL * 2) < 1: # Crude way to run every X seconds
                 pass # We rely on timing above, but structure allows adding the checks below
                 
            if time.time() % (INTERVAL * 2) < 1 and time.time() % (INTERVAL * 2) > (INTERVAL * 2) - 0.5:
                # Run ping check every N intervals
                check_ping(TARGET_HOST, count=2)
            
            time.sleep(max(0, INTERVAL - 1)) # Adjust sleep time based on the 1 sec wait above

    except KeyboardInterrupt:
        print("\n\nMonitor stopped by user (Ctrl+C). Exiting gracefully.")
    except Exception as e:
        print(f"\nAn unexpected error occurred in the main loop: {e}")


if __name__ == "__main__":
    # Ensure 'psutil' is installed: pip install psutil
    try:
        main_monitoring_loop()
    except ImportError:
        print("\n=============================================================")
        print("ERROR: The 'psutil' library is required for this script.")
        print("Please install it using: pip install psutil")
        print("=============================================================\n")
