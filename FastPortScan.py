#!/usr/bin/env python3

import argparse
import socket
import sys
import signal
from colorama import Fore, Style, init
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Initialize colorama
init(autoreset=True)

# Global variables
open_ports = []
executor = None  # Thread pool executor
progress = None  # Progress bar
exit_flag = False  # Flag to indicate termination

# Function to handle Ctrl + C (Graceful Exit)
def handle_exit(signum, frame):
    global exit_flag
    print(f"\n{Fore.RED}Ctrl + C detected! Stopping scan gracefully... Please wait.")
    exit_flag = True  # Signal threads to stop

# Function to send SYN packet (Stealth Mode)
def stealth_scan(ip, port):
    if exit_flag:
        return None

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        if result == 0:
            open_ports.append(port)
            tqdm.write(f"{Fore.GREEN}port {port} - open")  
        sock.close()
    except socket.error:
        pass
    finally:
        progress.update(1)

# Function to scan a single port (Normal Mode)
def scan_port(ip, port):
    if exit_flag:
        return None

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        if result == 0:
            open_ports.append(port)
            tqdm.write(f"{Fore.GREEN}port {port} - open")  
        sock.close()
    except socket.error:
        pass
    finally:
        progress.update(1)

# Function to handle scanning with a thread pool
def scan_ports(ip, start_port, end_port, stealth):
    global progress, executor
    total_ports = end_port - start_port + 1

    with tqdm(total=total_ports, desc="Scanning Ports", ncols=100, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{percentage:3.0f}%]") as progress:
        with ThreadPoolExecutor(max_workers=100) as executor:
            scan_function = stealth_scan if stealth else scan_port
            future_to_port = {executor.submit(scan_function, ip, port): port for port in range(start_port, end_port + 1)}

            for future in as_completed(future_to_port):
                if exit_flag:
                    break  

    return open_ports

# Function to display the banner
def display_banner():
    print(Fore.CYAN + """
    ============================================
          Welcome to the Fast Port Scanner
		    by @kra1t
    ============================================
    """)

# Main function
def main():
    global exit_flag

    # Setup argument parsing
    parser = argparse.ArgumentParser(description="Scan ports on a given IP address.")
    parser.add_argument("-ip", "--ip", required=True, help="IP address to scan")
    parser.add_argument("--starting", type=int, default=1, help="Starting port (default: 1)")
    parser.add_argument("--ending", type=int, default=65535, help="Ending port (default: 65535)")
    parser.add_argument("--stealth", action="store_true", help="Enable stealth mode (SYN scan)")

    args = parser.parse_args()

    # Display banner
    display_banner()

    # Get IP and port range
    ip = args.ip
    start_port = args.starting
    end_port = args.ending
    stealth = args.stealth

    # Validate port range
    if start_port < 1 or end_port > 65535 or start_port > end_port:
        print(f"{Fore.RED}Invalid port range! Ensure 1 <= start <= end <= 65535.")
        sys.exit(1)

    # Handle Ctrl + C gracefully
    signal.signal(signal.SIGINT, handle_exit)

    # Start scanning
    mode_text = "Stealth SYN Scan" if stealth else "Normal Scan"
    print(f"{Fore.YELLOW}Starting {mode_text} on {ip} from port {start_port} to port {end_port}...\n")
    found_ports = scan_ports(ip, start_port, end_port, stealth)

    # Display final result
    if exit_flag:
        print(f"\n{Fore.YELLOW}Scan stopped by user! Showing results so far...")

    if found_ports:
        print(f"\n{Fore.GREEN}Open ports found: {','.join(map(str, found_ports))}")
    else:
        print(f"{Fore.RED}No open ports found.")

if __name__ == "__main__":
    main()
#Krait's Work
