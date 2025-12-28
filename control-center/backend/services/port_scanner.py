"""Port scanner service for detecting open ports and their processes."""
import psutil
from typing import List, Dict, Optional
from config import settings


class PortScanner:
    """Scanner for detecting open ports and associated processes."""

    @staticmethod
    def get_process_name(pid: int) -> Optional[str]:
        """Get process name from PID."""
        try:
            process = psutil.Process(pid)
            return process.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    @staticmethod
    def scan_ports() -> List[Dict]:
        """
        Scan ports in the configured range and return information about open ports.

        Returns:
            List of dictionaries containing port information.
        """
        open_ports = []

        try:
            # Get all network connections
            connections = psutil.net_connections(kind='inet')

            for conn in connections:
                # Check if connection has a local address
                if not conn.laddr:
                    continue

                port = conn.laddr.port

                # Filter by port range
                if settings.PORT_SCAN_START <= port <= settings.PORT_SCAN_END:
                    process_name = PortScanner.get_process_name(conn.pid) if conn.pid else None

                    port_info = {
                        "port": port,
                        "pid": conn.pid,
                        "process_name": process_name,
                        "status": conn.status,
                        "address": conn.laddr.ip
                    }

                    # Avoid duplicates
                    if not any(p["port"] == port and p["pid"] == conn.pid for p in open_ports):
                        open_ports.append(port_info)

            # Sort by port number
            open_ports.sort(key=lambda x: x["port"])

        except Exception as e:
            print(f"Error scanning ports: {e}")

        return open_ports

    @staticmethod
    def is_port_in_use(port: int) -> bool:
        """Check if a specific port is in use."""
        try:
            connections = psutil.net_connections(kind='inet')
            return any(conn.laddr and conn.laddr.port == port for conn in connections)
        except Exception:
            return False

    @staticmethod
    def get_port_info(port: int) -> Optional[Dict]:
        """Get information about a specific port."""
        try:
            connections = psutil.net_connections(kind='inet')
            for conn in connections:
                if conn.laddr and conn.laddr.port == port:
                    process_name = PortScanner.get_process_name(conn.pid) if conn.pid else None
                    return {
                        "port": port,
                        "pid": conn.pid,
                        "process_name": process_name,
                        "status": conn.status,
                        "address": conn.laddr.ip
                    }
        except Exception as e:
            print(f"Error getting port info: {e}")

        return None
