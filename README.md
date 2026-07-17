# NetPen

NetPen is an enterprise-grade tactical network security and penetration testing auditing framework built in Python. Designed for security professionals, network engineers, and academic researchers, it provides a comprehensive suite of security validation modules within a modern, highly optimized graphical user interface.

## System Architecture

The application is engineered with a strict separation of concerns, ensuring absolute thread-safety, real-time GUI responsiveness, and structured resource management.

*   **Asynchronous Processing Engine**: Background auditing tasks are entirely decoupled from the main thread using an isolated execution pipeline.
*   **Thread-Safe Event Queue**: Communication between packet craft operations and the visual dashboard is managed through a thread-safe message queue, eliminating standard GUI-blocking conditions.
*   **Stateful Lifecycle Management**: Implements clean termination hooks for scheduled tasks, threads, and packet interfaces to prevent resource leakage or orphan socket connections on application shutdown.

## Key Modules

### 1. CAM Table MAC Flooding (MAC Flood)
Floods local layer-2 switch topologies with randomized hardware source identifiers to test CAM table exhaustion thresholds. Includes optional address randomization (RandMAC).

### 2. TCP SYN Starvation (SYN Flood)
Performs automated, high-volume TCP synchronization frame transmissions to test host resource exhaustion, supporting spoofed source address mapping (RandIP).

### 3. ARP Cache Poisoning (ARP Spoof)
Intercepts local broadcast domains by mapping network gateway hardware addresses to target cache pointers, facilitating authorized Man-in-the-Middle (MitM) traffic analysis.

### 4. DNS Query Redirection (DNS Spoof)
Forges mapping parameters inside ongoing system query processes to safely evaluate redirection and hijacking vulnerabilities in testing environments.

## Installation

### Prerequisites

NetPen requires administrative privileges to interact directly with network interface cards for raw packet crafting.

*   **Operating System**: Linux (Ubuntu, Debian, Kali) or Windows (10/11)
*   **Packet Capture Engine**: 
    *   **Windows**: [Npcap](https://npcap.com/) (installed with the "API-compatible Mode" option selected)
    *   **Linux**: Native packet capture utilities (standard on most distributions)

### Deployment Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/FaresMohamed6/NetPen.git
   cd NetPen
   ```

2. Install system-level dependencies (Linux only):
   ```bash
   sudo apt update
   sudo apt install python3-pip libpcap-dev
   ```

3. Install Python library dependencies:
   ```bash
   pip install customtkinter scapy
   ```

## Usage

Since packet craft engines interface directly with layer-2/layer-3 sockets, the application must be executed with root or administrator privileges.

### Linux
```bash
sudo python3 NetPen_2.py
```

### Windows
1. Open PowerShell or Command Prompt as **Administrator**.
2. Run:
   ```cmd
   python NetPen_2.py
   ```

## Development and Architecture

*   **UI Framework**: CustomTkinter
*   **Packet Handling**: Scapy
*   **Concurrency**: Python Threading and Queue modules
*   **Design Paradigm**: Decoupled Model-View-Controller (MVC) architecture with customized styling sheets.

## Disclaimer

This software is developed strictly for educational purposes, defensive network auditing, and authorized security research in controlled laboratory environments. Executing packet injection or intercept operations against network targets without prior explicit written authorization is strictly illegal and subject to criminal prosecution. The developer assumes zero liability for misuse, damages, or legal consequences arising from the execution of this codebase.

## Developer Profile

*   **Name**: Fares Mohamed
*   **GitHub**: [FaresMohamed6](https://github.com/FaresMohamed6)
*   **LinkedIn**: [Fares Mohamed](https://www.linkedin.com/in/faresmohamed5)
*   **Telegram**: [Secure Channel](https://t.me/FaressMohamed11)
*   **WhatsApp**: [Direct Message](https://api.whatsapp.com/send/?phone=201033463740)
*   **X (Twitter)**: [FERSKA432007](https://x.com/FERSKA432007)