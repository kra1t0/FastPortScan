#!/usr/bin/env python3

import argparse
import socket
import sys
import signal
from colorama import Fore, Style, init
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import errno
import time

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
# NOTE: The original script used plain connect_ex for "stealth"; we keep the same behavior
# to avoid adding raw-socket requirements or dropping functionality.
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
        # progress is a global tqdm object created in scan_ports
        try:
            progress.update(1)
        except Exception:
            pass

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
        try:
            progress.update(1)
        except Exception:
            pass

# Function to scan a single UDP port
# UDP scanning is best-effort: many UDP services do not reply to empty packets.
# This function treats a port as "open" only if we receive a response within the timeout.
# If no response is received we don't mark it open (this avoids false positives but can miss
# real UDP services that are silent).
def udp_scan_port(ip, port):
    if exit_flag:
        return None

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        # Send a small payload. Some services expect specific data; an empty packet may be ignored.
        try:
            sock.sendto(b"\x00", (ip, port))
        except OSError:
            # Could be unreachable immediately on some environments
            pass

        try:
            data, addr = sock.recvfrom(1024)
            # If recvfrom succeeded, we got a response -> consider port open
            open_ports.append(port)
            tqdm.write(f"{Fore.GREEN}port {port} - open")
        except socket.timeout:
            # No response; don't mark as open to avoid false positives.
            pass
        except OSError:
            # On some systems, receiving an ICMP 'port unreachable' can raise OSError
            # which we treat as closed/filtered; ignore it.
            pass
        finally:
            sock.close()
    except socket.error:
        pass
    finally:
        try:
            progress.update(1)
        except Exception:
            pass

# Function to handle scanning with a thread pool
def scan_ports(ip, start_port, end_port, stealth, udp):
    global progress, executor, open_ports
    total_ports = end_port - start_port + 1

    # Reset found ports list for each run
    open_ports = []

    with tqdm(total=total_ports, desc="Scanning Ports", ncols=100, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{percentage:3.0f}%]") as progress:
        with ThreadPoolExecutor(max_workers=100) as executor:
            if udp:
                scan_function = udp_scan_port
            else:
                scan_function = stealth_scan if stealth else scan_port

            future_to_port = {executor.submit(scan_function, ip, port): port for port in range(start_port, end_port + 1)}

            for future in as_completed(future_to_port):
                if exit_flag:
                    break

    # Remove duplicates and sort
    unique_sorted = sorted(set(open_ports))
    return unique_sorted

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
    # Accept both --UDP and --udp for convenience; dest is 'udp'
    parser.add_argument("--UDP", "--udp", action="store_true", dest="udp", help="Scan UDP ports instead of TCP")
    parser.add_argument("--stealth", action="store_true", help="Enable stealth mode (SYN scan) for TCP")

    args = parser.parse_args()

    # Display banner
    display_banner()

    # Get IP and port range
    ip = args.ip
    start_port = args.starting
    end_port = args.ending
    stealth = args.stealth
    udp = args.udp

    # Validate port range
    if start_port < 1 or end_port > 65535 or start_port > end_port:
        print(f"{Fore.RED}Invalid port range! Ensure 1 <= start <= end <= 65535.")
        sys.exit(1)

    # Handle Ctrl + C gracefully
    signal.signal(signal.SIGINT, handle_exit)

    # Start scanning
    if udp and stealth:
        # stealth mode isn't applicable to UDP in this script; warn the user but continue with UDP
        print(f"{Fore.YELLOW}Note: --stealth is for TCP scans only. Proceeding with UDP scan (stealth ignored).")

    mode_text = "UDP Scan" if udp else ("Stealth SYN Scan" if stealth else "Normal TCP Scan")
    print(f"{Fore.YELLOW}Starting {mode_text} on {ip} from port {start_port} to port {end_port}...\n")

    found_ports = scan_ports(ip, start_port, end_port, stealth, udp)

    # Display final result
    if exit_flag:
        print(f"\n{Fore.YELLOW}Scan stopped by user! Showing results so far...")

    if found_ports:
        print(f"\n{Fore.GREEN}Open ports found: {','.join(map(str, found_ports))}")
    else:
        print(f"{Fore.RED}No open ports found.")

if __name__ == "__main__":
    main()
#Krait's Work (udp support added)
