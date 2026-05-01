"""Power backend — systemd / logind"""
import subprocess


def _run(cmd: list):
    try:
        subprocess.run(cmd, timeout=5)
    except Exception:
        pass


def suspend():
    _run(["systemctl", "suspend"])


def reboot():
    _run(["systemctl", "reboot"])


def shutdown():
    _run(["systemctl", "poweroff"])


def hibernate():
    _run(["systemctl", "hibernate"])


def lock_screen():
    _run(["loginctl", "lock-session"])


def get_inhibitors() -> list:
    try:
        r = subprocess.run(
            ["systemd-inhibit", "--list", "--no-legend"],
            capture_output=True, text=True, timeout=5
        )
        return r.stdout.strip().splitlines()
    except Exception:
        return []
