"""A small, local-network TCP port checker for a cybersecurity lab.

Uses Python's standard library only. Run against your own computer or
private lab devices that you have permission to assess.
"""

import argparse
import ipaddress
import socket

# Try the local demo port plus some common services.
COMMON_PORTS = {
    22: "SSH",
    80: "HTTP",
    443: "HTTPS",
    445: "SMB",
    3389: "Remote Desktop (RDP)",
    8006: "Proxmox web UI",
    8765: "Local test server",
    32400: "Plex",
}


def local_ipv4(value):
    """Allow only IPv4 loopback and private-network addresses."""
    try:
        address = ipaddress.IPv4Address(value)
    except ipaddress.AddressValueError as exc:
        raise argparse.ArgumentTypeError("Enter an IPv4 address, e.g. 127.0.0.1") from exc

    private_ranges = (
        ipaddress.IPv4Network("10.0.0.0/8"),
        ipaddress.IPv4Network("172.16.0.0/12"),
        ipaddress.IPv4Network("192.168.0.0/16"),
        ipaddress.IPv4Network("127.0.0.0/8"),
    )
    if not any(address in network for network in private_ranges):
        raise argparse.ArgumentTypeError("Only loopback or private lab IPv4 addresses are allowed")
    return str(address)


def port_number(value):
    """Reject invalid TCP port numbers."""
    try:
        port = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Port must be an integer") from exc
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("Port must be between 1 and 65535")
    return port


def check_port(host, port, timeout=0.5):
    """Return True if a TCP connection to this port succeeds."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
            connection.settimeout(timeout)
            return connection.connect_ex((host, port)) == 0
    except OSError:
        return False


def main():
    parser = argparse.ArgumentParser(description="Check a few TCP ports on your own private lab devices")
    parser.add_argument("target", nargs="?", type=local_ipv4, default="127.0.0.1",
                        help="private IPv4 address (default: 127.0.0.1)")
    parser.add_argument("--ports", nargs="+", type=port_number,
                        help="specific TCP ports to check; defaults to common services")
    args = parser.parse_args()

    ports = args.ports if args.ports is not None else list(COMMON_PORTS)
    print(f"Checking {len(ports)} TCP port(s) on {args.target}...\n")
    open_ports = []
    for port in ports:
        service = COMMON_PORTS.get(port, "Unknown service")
        is_open = check_port(args.target, port)
        status = "OPEN" if is_open else "closed / filtered"
        print(f"{port:>5}  {service:<23} {status}")
        if is_open:
            open_ports.append(port)

    print(f"\nFound {len(open_ports)} open TCP port(s).")
    print("Note: An open port is not automatically a vulnerability.")
    print("A non-response can mean closed, filtered, or unreachable.")


if __name__ == "__main__":
    main()
