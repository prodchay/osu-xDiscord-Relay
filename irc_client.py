import socket
import threading
import time
from os import getenv

from dotenv import load_dotenv

load_dotenv()


class IRCClient(threading.Thread):
    def __init__(self, host: str = "irc.ppy.sh", port: int = 6667):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.sock = None
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.connected = threading.Event()
        self.username = getenv("IRC_USERNAME")
        self.password = getenv("IRC_PASSWORD")
        self.reconnect_delay = 1

    def close_socket(self):
        if self.sock is not None:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.sock.close()
            self.sock = None
        self.connected.clear()

    def _send_raw(self, payload: str):
        if self.sock is None:
            raise OSError("IRC socket is not connected")
        self.sock.sendall(payload.encode("utf-8"))

    def _read_data(self):
        if self.sock is None:
            return None

        try:
            self.sock.settimeout(1.0)
            data = self.sock.recv(4096)
        except TimeoutError:
            return None
        except OSError:
            self.close_socket()
            raise

        if not data:
            self.close_socket()
            return None

        return data.decode("utf-8", errors="ignore")

    def connect(self):
        if not self.username:
            raise RuntimeError("IRC_USERNAME is not set")
        if not self.password:
            raise RuntimeError("IRC_PASSWORD is not set")

        self.close_socket()
        self.sock = socket.create_connection((self.host, self.port), timeout=15)
        self.sock.settimeout(1.0)

        self._send_raw(f"PASS {self.password}\r\n")
        self._send_raw(f"NICK {self.username}\r\n")
        self._send_raw(f"USER {self.username} 0 * :{self.username}\r\n")

        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            data = self._read_data()
            if not data:
                continue
            if " 001 " in data:
                self.connected.set()
                self.reconnect_delay = 1
                return

        self.close_socket()
        raise TimeoutError("Timed out waiting for IRC welcome message")

    def run(self):
        backoff = 1

        while not self.stop_event.is_set():
            try:
                if self.sock is None or not self.connected.is_set():
                    self.connect()

                data = self._read_data()
                if data:
                    for line in data.splitlines():
                        if not line:
                            continue

                        if line.startswith("PING"):
                            self._send_raw(f"PONG {line.split()[1]}\r\n")
                        if " 001 " in line:
                            self.connected.set()

                if self.connected.is_set():
                    backoff = 1

            except (OSError, TimeoutError, RuntimeError) as exc:
                print(f"IRC connection lost: {exc}")
                self.close_socket()
                if self.stop_event.wait(backoff):
                    break
                backoff = min(backoff * 2, 30)

        self.close_socket()

    def stop(self):
        self.stop_event.set()
        self.close_socket()

    def send_message(self, sender, beatmap_details, target: str, beatmap_link: str):
        if self.stop_event.is_set():
            return 1

        if self.sock is None or not self.connected.is_set():
            try:
                self.connect()
            except (OSError, RuntimeError, TimeoutError) as exc:
                print(f"IRC reconnect failed: {exc}")
                return 1

        message = f"PRIVMSG {target} :[{sender}] {beatmap_details} - {beatmap_link}\r\n"

        try:
            with self.lock:
                print(f"Sending map to {target}: {beatmap_link}")
                self._send_raw(message)
            return 0
        except OSError:
            self.close_socket()
            return 1
