# FastPortScan

FastPortScan is a **high-speed, multithreaded** port scanner built with Python. It can perform **both normal and stealth (SYN) scans**, allowing you to efficiently identify open ports on a target machine. The tool is designed to be fast, customizable, and easy to use.

## ⚡ Features

✅ **Ultra-fast scanning** using multithreading  
✅ **Full TCP scan (Default mode)**  
✅ **Stealth SYN scan (`--stealth` mode)**  
✅ **Custom port range selection**  
✅ **Color-coded output using `colorama`**  
✅ **Progress bar with `tqdm`**  
✅ **Graceful exit on Ctrl+C, ensuring all findings are displayed**  
✅ **Lightweight & easy to use**  

## 🚀 Installation

Ensure you have Python 3 installed. Then, install the required dependencies:

```bash
pip install colorama tqdm
```

## 🔧 Usage

Run the tool with the desired options:

### **Basic Scan (Full TCP Handshake)**
```bash
python3 FastPortScan.py -ip <TARGET_IP>
```
This scans **all 65,535 ports** on the target.

### **Specify Port Range**
```bash
python3 FastPortScan.py -ip <TARGET_IP> --starting 1 --ending 1024
```
This scans only ports **1 to 1024**.

### **Stealth Mode (SYN Scan - Requires Root)**
```bash
sudo python3 FastPortScan.py -ip <TARGET_IP> --stealth
```
This sends **SYN packets** instead of a full TCP handshake, making the scan stealthier.

### **Example Output**
```
============================================
      Welcome to the Fast Port Scanner
============================================

Starting scan on 10.10.11.24 from port 1 to 65535...

port 53 - open
port 80 - open
port 443 - open
Scanning Ports:  50%|███████████████████▍  | 32634/65535 [ 50%]

Open ports found: 53, 80, 443
```

## 🛡️ Legal Disclaimer
This tool is intended for **educational purposes** and **authorized security testing only**. Unauthorized scanning of networks **without explicit permission** is illegal and unethical. The developer is **not responsible** for any misuse.

## 🤖 Author
**Janindu (Kra1t)**  
💀 Ethical Hacker & Cybersecurity Enthusiast  
📌 [LinkedIn](https://www.linkedin.com/in/janindu)  
📌 [GitHub](https://github.com/janindu)  

## 📜 License
This project is licensed under the **MIT License**.

