#!/usr/bin/python3
import logging
import socket
import time
import sys
import os

from .settings import log


class WatchdogPing():

    def watchdog_period(self):
        """Return the time (in seconds) that we need to ping within."""
        val = os.environ.get("WATCHDOG_USEC", None)
        if not val:
            return None
        return int(val)/1000000  # (2)

    def notify_socket(self, clean_environment=False):
        """Return a tuple of address, socket. clean_environment removes the variables from env to prevent children 
           from inheriting it and doing something wrong."""
        _empty = None, None
        address = os.environ.get("NOTIFY_SOCKET", None)  # (3)
        log.info("address: %s" % address)
        if clean_environment:
            address = os.environ.pop("NOTIFY_SOCKET", None)
        if not address or len(address) == 1 or address[0] not in ("@", "/"):
            return _empty
        if address[0] == "@":
            address = "\0" + address[1:]
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM | socket.SOCK_CLOEXEC)  # (1)
        except AttributeError:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        if not address or not sock:  # (4)
            self.print_err("No notification socket, not launched via systemd?")
        log.debug(address)
        log.debug(sock)
        return address, sock

    def sd_message(self, address, sock, message):
        """Send a message to the systemd bus/socket. message is expected to be bytes."""
        if not (address and sock and message):
            return False
        assert isinstance(message, bytes)
        try:
            retval = sock.sendto(message, address)
        except socket.error:
            return False
        return (retval > 0)

    def watchdog_ping(self):
        """Helper function to send a watchdog ping."""
        self.notify = self.notify_socket()
        logging.basicConfig()
        log.setLevel(logging.DEBUG)
        self.systemd_status(*self.notify, status=b"Initializing")
        self.systemd_ready(*self.notify)
        message = b"WATCHDOG=1"
        # Pinging is done with sd_message(..), within the return value. sd_message sends the message with sock.
        return self.sd_message(*self.notify, message=message)

    def systemd_ready(self, address, sock):
        """Helper function to send a ready signal."""
        message = b"READY=1"
        log.debug("Signaling system ready")
        return self.sd_message(address, sock, message)

    def systemd_stop(address, sock):
        """Helper function to signal service stopping."""
        message = b"STOPPING=1"
        return self.sd_message(address, sock, message)

    def systemd_status(self, address, sock, status):
        """Helper function to update the service status."""
        message = ("STATUS=%s" % status).encode('utf8')
        return self.sd_message(address, sock, message)

    def print_err(self, msg):
        """Print an error message to STDERR and quit."""
        print(msg, file=sys.stderr)
        sys.exit(1)


ping = WatchdogPing().watchdog_ping  # (7)


# Original code is from Spindel, which is adjusted slightly here.
# (1) SOCK_CLOEXEC was added in Python 3.2 and requires Linux >= 2.6.27. It means "close this socket after fork/exec()
# (2) env multipliziert WATCHDOG_USEC mit 10^6, darum muss durch 10^6 dividiert werden.
# (3) Systemd address is also in the environment variables (NOTIFY_SOCKET).
# (4) Validate some in-data
# (5) Cut off a bit from the period to make the ping/Execution time work
# (6) Get our settings from the environment
# (7) For textual reference we have to assign the bound method to global variables, which can for example be used in
#     apscheduler's add_job textual reference parameter.
