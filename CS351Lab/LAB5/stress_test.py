import urllib.request
import threading
import sys
import time

def stress(url, duration):
    end_time = time.time() + duration
    requests_made = 0
    errors = 0
    
    while time.time() < end_time:
        try:
            urllib.request.urlopen(url, timeout=2)
            requests_made += 1
        except Exception:
            errors += 1
            
    print(f"Thread finished. Requests: {requests_made}, Errors: {errors}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python stress_test.py <url>")
        sys.exit(1)
        
    url = sys.argv[1]
    duration = 300  # 5 minutes
    num_threads = 50
    
    print(f"Starting stress test on {url} with {num_threads} threads for {duration} seconds...")
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=stress, args=(url, duration))
        t.daemon = True
        t.start()
        threads.append(t)
        
    try:
        while any(t.is_alive() for t in threads):
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStress test stopped by user.")
        
    print("Test complete.")

if __name__ == "__main__":
    main()
