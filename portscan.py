import socket
import sys
import time
import concurrent.futures

# Port szolgáltatásának lekérdezése
def get_service(port):
    try:
        return socket.getservbyport(port)
    except OSError:
        return "Ismeretlen"

# Port szkennelés egy adott portra
def scan_port(target_host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((target_host, port))
            if result == 0:
                service = get_service(port)    
                return (port, service)
            else:
                return None
    except Exception as e:
        return None

# Portok szkennelése párhuzamosan
def scan_ports(target_host, start_port, end_port, num_threads=50):
    open_ports = []
    total_ports = end_port - start_port + 1
    ports_scanned = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        port_range = range(start_port, end_port + 1)
        futures = {executor.submit(scan_port, target_host, port): port for port in port_range}
        for future in concurrent.futures.as_completed(futures):
            port = futures[future]
            ports_scanned += 1
            try:
                data = future.result()
                if data is not None:
                    open_ports.append(data)
            except Exception as e:
                pass
            percent_done = ports_scanned / total_ports * 100
            print(f"\r{percent_done:.2f}% kész", end='', flush=True)
    print()  # Új sor a kész szkennelési üzenet után
    return open_ports

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Használat: python port_scanner.py <célpont> <kezdő port> <végző port>")
        sys.exit()

    target = sys.argv[1]
    start_port = int(sys.argv[2])
    end_port = int(sys.argv[3])

    print(f"Port scan indítása {target}")
    start_time = time.time()

    # Párhuzamos portszkennelés indítása
    open_ports = scan_ports(target, start_port, end_port)

    end_time = time.time()
    scan_duration = end_time - start_time
    print(f"Port scan kész, eltelt idő: {scan_duration} másodperc")

    if open_ports:
        print("Nyitott portok:")
        for port, service in open_ports:
            print(f"{port} - {service} ")
    else:
        print("Nem található nyitott port.")
