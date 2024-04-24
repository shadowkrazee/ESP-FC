import sys
sys.path.append('/lib')
import time
import routes

def main():
    # Initialize your devices and variables here
    # For example, setup GPIO pins or sensors
    print("Application started")

    # Main loop
    while True:
        # Put your main code here to run repeatedly
        print("Hello from main.py")
        
        # Sleep for a while to avoid flooding with messages
        time.sleep(5)

if __name__ == "__main__":
    main()
