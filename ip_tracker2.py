#!/usr/bin/env python3
import requests
import os
import socket
import threading
import time
from rich.console import Console
from rich.panel import Panel

from math import radians, cos, sin, asin, sqrt
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
console = Console()

# Colors for terminal output


class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[0;37m'
    BOLD = '\033[1m'
    NC = '\033[0m'


def clear_screen():
    os.system('clear')


def get_ip_info(ip):
    try:
        # Get comprehensive IP info
        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        data = response.json()

        # Get additional timezone info
        try:
            tz_response = requests.get(
                f"http://worldtimeapi.org/api/ip/{ip}", timeout=5)
            tz_data = tz_response.json()
            data['local_time'] = tz_data.get('datetime', 'N/A')
            data['timezone_offset'] = tz_data.get('utc_offset', 'N/A')
        except:
            data['local_time'] = 'N/A'
            data['timezone_offset'] = 'N/A'

        # Get weather info if available
        try:
            if 'loc' in data:
                coords = data['loc'].split(',')
                weather_response = requests.get(
                    f"https://api.open-meteo.com/v1/forecast?latitude={coords[0]}&longitude={coords[1]}&current_weather=true", timeout=5)
                weather_data = weather_response.json()
                data['temperature'] = weather_data.get(
                    'current_weather', {}).get('temperature', 'N/A')
                data['weather_code'] = weather_data.get(
                    'current_weather', {}).get('weathercode', 'N/A')
        except:
            data['temperature'] = 'N/A'
            data['weather_code'] = 'N/A'

# Distance from you
        my_ip_data = requests.get("https://ipinfo.io/json").json()

        my_loc = my_ip_data.get("loc", "0,0").split(",")
        target_loc = data.get("loc", "0,0").split(",")

        distance = calculate_distance(
            float(my_loc[0]),
            float(my_loc[1]),
            float(target_loc[0]),
            float(target_loc[1])
        )

        data["distance"] = f"{distance} km"

        return data
    except Exception as e:
        return None


def get_maps_link(location):
    try:
        lat, lon = location.split(",")
        return f"https://www.google.com/maps?q={lat},{lon}"
    except:
        return "N/A"

def get_flag(country_code):
    try:
        return ''.join(chr(127397 + ord(c)) for c in country_code.upper())
    except:
        return "🏳️"

def display_info(ip_data, title):
    clear_screen()

    # Country + Flag
    country_code = ip_data.get('country', 'N/A')
    flag = get_flag(country_code)

    # Location
    location = ip_data.get('loc', 'N/A')

    # Google Maps Link
    try:
        lat, lon = location.split(',')
        maps_link = f"https://www.google.com/maps?q={lat},{lon}"
    except:
        maps_link = "N/A"

    # Header
    print(f"""{Colors.CYAN}
╔══════════════════════════════════════════════════════╗
║              IP TRACKER BY THE UNSEEN               ║
╚══════════════════════════════════════════════════════╝
{Colors.NC}""")

    # Main Info
    print(f"{Colors.YELLOW}╔═══ BASIC INFORMATION ═══╗{Colors.NC}")

    print(f"{Colors.GREEN}{'IP Address':<18}:{Colors.WHITE} {ip_data.get('ip', 'N/A')}")
    print(f"{Colors.GREEN}{'Hostname':<18}:{Colors.WHITE} {ip_data.get('hostname', 'N/A')}")
    print(f"{Colors.GREEN}{'City':<18}:{Colors.WHITE} {ip_data.get('city', 'N/A')}")
    print(f"{Colors.GREEN}{'Region':<18}:{Colors.WHITE} {ip_data.get('region', 'N/A')}")
    print(f"{Colors.GREEN}{'Country':<18}:{Colors.WHITE} {flag} {country_code}")
    print(f"{Colors.GREEN}{'Postal Code':<18}:{Colors.WHITE} {ip_data.get('postal', 'N/A')}")
    print(f"Distance From You: {ip_data.get('distance', 'N/A')}")

    # Geo Info
    print(f"\n{Colors.YELLOW}╔═══ GEO LOCATION ═══╗{Colors.NC}")

    print(f"{Colors.GREEN}{'Coordinates':<18}:{Colors.WHITE} {location}")
    print(f"{Colors.GREEN}{'Google Maps':<18}:{Colors.WHITE} {maps_link}")

    # Network Info
    print(f"\n{Colors.YELLOW}╔═══ NETWORK INFORMATION ═══╗{Colors.NC}")

    print(f"{Colors.GREEN}{'ISP':<18}:{Colors.WHITE} {ip_data.get('org', 'N/A')}")
    print(f"{Colors.GREEN}{'Timezone':<18}:{Colors.WHITE} {ip_data.get('timezone', 'N/A')}")

    # Local Info
    print(f"\n{Colors.YELLOW}╔═══ LOCAL INFORMATION ═══╗{Colors.NC}")

    print(f"{Colors.GREEN}{'Temperature':<18}:{Colors.WHITE} {ip_data.get('temperature', 'N/A')}°C")
    print(f"{Colors.GREEN}{'Local Time':<18}:{Colors.WHITE} {ip_data.get('local_time', 'N/A')}")
    print(f"{Colors.GREEN}{'UTC Offset':<18}:{Colors.WHITE} {ip_data.get('timezone_offset', 'N/A')}")

    # Security Info
    print(f"\n{Colors.YELLOW}╔═══ SECURITY INFORMATION ═══╗{Colors.NC}")

    print(f"{Colors.GREEN}{'VPN/Proxy':<18}:{Colors.WHITE} Unknown")
    print(f"{Colors.GREEN}{'Threat Level':<18}:{Colors.WHITE} Unknown")

    # Footer
    print(f"\n{Colors.CYAN}══════════════════════════════════════════════════════{Colors.NC}")
    print(f"{Colors.BOLD}Created by THE UNSEEN{Colors.NC}")
    print(f"{Colors.CYAN}══════════════════════════════════════════════════════{Colors.NC}")


def stress_test():
    clear_screen()
    print(f"{Colors.YELLOW}Enter target IP address:{Colors.NC}")
    target_ip = input(">> ").strip()

    if not target_ip:
        print(f"{Colors.RED}Please enter an IP address{Colors.NC}")
        input(f"{Colors.YELLOW}Press Enter to continue...{Colors.NC}")
        return

    # Basic IP validation
    parts = target_ip.split('.')
    if len(parts) != 4 or not all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
        print(f"{Colors.RED}Invalid IP address format{Colors.NC}")
        input(f"{Colors.YELLOW}Press Enter to continue...{Colors.NC}")
        return

    print(f"{Colors.YELLOW}Enter number of packets (default 100):{Colors.NC}")
    try:
        packets = int(input(">> ") or "100")
    except:
        packets = 100

    print(f"{Colors.YELLOW}Enter number of threads (default 50):{Colors.NC}")
    try:
        threads = int(input(">> ") or "50")
    except:
        threads = 50

    print(f"{Colors.YELLOW}Starting stress test... Press Ctrl+C to stop{Colors.NC}")
    print(f"{Colors.RED}WARNING: This is for educational purposes only{Colors.NC}")

    sent = 0
    failed = 0

    def send_packet():
        nonlocal sent, failed
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((target_ip, 80))
            if result == 0:
                sent += 1
            else:
                failed += 1
            sock.close()
        except:
            failed += 1

    try:
        start_time = time.time()
        for i in range(packets):
            t = threading.Thread(target=send_packet)
            t.start()

            # Limit active threads
            if i % threads == 0:
                time.sleep(0.1)
                print(
                    f"{Colors.CYAN}Sent: {sent} | Failed: {failed} | Total: {i+1}/{packets}{Colors.NC}")

        # Wait for all threads to complete
        time.sleep(2)
        end_time = time.time()

        print(
            f"\n{Colors.GREEN}Stress test completed in {end_time - start_time:.2f} seconds{Colors.NC}")
        print(f"Sent: {sent} | Failed: {failed} | Total: {packets}")
        print(f"Success Rate: {(sent/packets)*100:.2f}%")
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Stress test stopped by user{Colors.NC}")

    input(f"{Colors.YELLOW}\nPress Enter to continue...{Colors.NC}")


def track_my_ip():
    clear_screen()
    print(f"{Colors.YELLOW}Getting your IP address...{Colors.NC}")
    try:
        my_ip = requests.get('https://ifconfig.me', timeout=5).text.strip()
        ip_data = get_ip_info(my_ip)
        if ip_data:
            display_info(ip_data, "YOUR IP DETAILS")
        else:
            print(f"{Colors.RED}Failed to get IP information{Colors.NC}")
    except Exception as e:
        print(f"{Colors.RED}Error: {str(e)}{Colors.NC}")
    input(f"{Colors.YELLOW}\nPress Enter to continue...{Colors.NC}")


def track_target_ip():
    clear_screen()
    print(f"{Colors.YELLOW}Enter target IP address:{Colors.NC}")
    target_ip = input(">> ").strip()

    if not target_ip:
        print(f"{Colors.RED}Please enter an IP address{Colors.NC}")
        input(f"{Colors.YELLOW}Press Enter to continue...{Colors.NC}")
        return

    # Basic IP validation
    parts = target_ip.split('.')
    if len(parts) != 4 or not all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
        print(f"{Colors.RED}Invalid IP address format{Colors.NC}")
        input(f"{Colors.YELLOW}Press Enter to continue...{Colors.NC}")
        return

    ip_data = get_ip_info(target_ip)
    if ip_data:
        display_info(ip_data, "TARGET IP DETAILS")
    else:
        print(f"{Colors.RED}Failed to get IP information{Colors.NC}")
    input(f"{Colors.YELLOW}\nPress Enter to continue...{Colors.NC}")

def banner():
    console.print(
        Panel.fit(
            "[bold cyan]IP Intelligence Dashboard[/bold cyan]\n[dim]created by THE UNSEEN[/dim]",
            border_style="cyan"
        )
    )

def loading(text="Loading", times=3):
    for i in range(times):
        print(f"{Colors.CYAN}{text}{'.' * (i+1)}{Colors.NC}", end="\r")
        time.sleep(0.4)

    print(" " * 60, end="\r")

from rich.table import Table

def compare_ips(ip_list):
    table = Table(title="IP Comparison Dashboard", show_lines=True)

    table.add_column("IP", style="cyan")
    table.add_column("City", style="white")
    table.add_column("Country", style="green")
    table.add_column("ISP", style="magenta")
    table.add_column("Location", style="yellow")

    for ip in ip_list:
        data = get_ip_info(ip)

        if not data:
            continue

        table.add_row(
            data.get("ip", "N/A"),
            data.get("city", "N/A"),
            data.get("country", "N/A"),
            data.get("org", "N/A"),
            data.get("loc", "N/A")
        )

    console.print(table)

def unseen_logo():
    try:
        path = "/sdcard/Download/ascii-art.txt"

        with open(path, "r", encoding="utf-8") as file:
            logo = file.read()

        console.print(f"[cyan]{logo}[/cyan]")

    except FileNotFoundError:
        console.print("[red]ascii-art.txt not found in Downloads[/red]")

def calculate_distance(lat1, lon1, lat2, lon2):
    # Earth radius in KM
    R = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * asin(sqrt(a))

    return round(R * c, 2)

def main():
    while True:
        clear_screen()

        # Show logo
        unseen_logo()

        # Header
        console.print(
            Panel.fit(
                "[bold cyan]IP Intelligence Dashboard[/bold cyan]\n"
                "[white]created by THE UNSEEN[/white]",
                border_style="cyan"
            )
        )

        # Status bar
        console.print(
            "[green]APIs:[/green] ONLINE   |   "
            "[cyan]Mode:[/cyan] LIVE   |   "
            "[yellow]Reports:[/yellow] ENABLED\n"
        )

        # Main menu table
        menu = Table(
            title="MAIN MENU",
            box=box.ROUNDED,
            border_style="cyan"
        )

        menu.add_column("Option", style="green", justify="center")
        menu.add_column("Feature", style="white")

        menu.add_row("1", "Track My IP")
        menu.add_row("2", "Track Target IP")
        menu.add_row("3", "Stress Test (Local Only)")
        menu.add_row("4", "Compare Multiple IPs")
        menu.add_row("0", "Exit")

        console.print(menu)

        # User input
        choice = input("\n>> Select option: ").strip()

        # Processing effect
        console.print("\n[cyan]Processing request...[/cyan]\n")

        # Menu actions
        if choice == "1":
            track_my_ip()

        elif choice == "2":
            track_target_ip()

        elif choice == "3":
            stress_test()

        elif choice == "4":
            ips = input("Enter IPs (comma separated): ")
            ip_list = [ip.strip() for ip in ips.split(",")]

            compare_ips(ip_list)

            input("\nPress Enter to continue...")

        elif choice == "0":
            console.print("[red]Shutting down...[/red]")
            break

        else:
            console.print("[red]Invalid option[/red]")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
