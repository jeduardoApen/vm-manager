import json
import os
import platform
import signal
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from models.virtual_machine import VirtualMachine, VMStatus
from interfaces.virtualization_service import IVirtualizationService


def _qemu_exe(name: str) -> str:
    if platform.system() == "Windows":
        candidates = [
            f"C:\\Program Files\\qemu\\{name}.exe",
            f"C:\\Program Files (x86)\\qemu\\{name}.exe",
            name,
        ]
        for c in candidates:
            if "\\" not in c or os.path.exists(c):
                return c
    return name


QEMU_IMG = _qemu_exe("qemu-img")
QEMU_SYS = _qemu_exe("qemu-system-x86_64")


class QemuService(IVirtualizationService):
    def __init__(self, data_dir: str = ""):
        if not data_dir:
            data_dir = os.path.expanduser("~/.vm_manager")
        self._data_dir = Path(data_dir)
        self._images_dir = self._data_dir / "images"
        self._images_dir.mkdir(parents=True, exist_ok=True)
        self._registry_path = self._data_dir / "vms.json"
        self._registry: Dict[str, dict] = {}
        self._load_registry()

    def _load_registry(self) -> None:
        if self._registry_path.exists():
            try:
                self._registry = json.loads(self._registry_path.read_text())
            except (json.JSONDecodeError, OSError):
                self._registry = {}

    def _save_registry(self) -> None:
        self._registry_path.write_text(json.dumps(self._registry, indent=2))

    def _vm_disk_path(self, name: str) -> Path:
        return self._images_dir / f"{name}.qcow2"

    def _is_process_alive(self, pid: int) -> bool:
        if platform.system() == "Windows":
            try:
                handle = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}"],
                    capture_output=True, text=True, timeout=5
                )
                return str(pid) in handle.stdout
            except Exception:
                return False
        else:
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                return False

    def list_vms(self) -> List[VirtualMachine]:
        vms = []
        for name, entry in self._registry.items():
            status = VMStatus.SHUT_OFF
            if entry.get("pid") and self._is_process_alive(entry["pid"]):
                status = VMStatus.RUNNING
            vms.append(VirtualMachine(
                name=name,
                uuid=entry.get("uuid", ""),
                memory_mb=entry.get("memory_mb", 1024),
                vcpus=entry.get("vcpus", 1),
                disk_size_gb=entry.get("disk_size_gb", 10),
                os_variant=entry.get("os_variant", "generic"),
                status=status,
                description=entry.get("description", ""),
            ))
        return vms

    def create_vm(self, vm: VirtualMachine, iso_path: str = "") -> VirtualMachine:
        if vm.name in self._registry:
            raise ValueError(f"La VM '{vm.name}' ya existe.")

        vm.uuid = str(uuid.uuid4())

        try:
            subprocess.run(
                [QEMU_IMG, "create", "-f", "qcow2",
                 str(self._vm_disk_path(vm.name)), f"{vm.disk_size_gb}G"],
                capture_output=True, text=True, check=True, timeout=60,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Error al crear disco: {e.stderr}\n"
                f"Asegurese de que QEMU este instalado: https://www.qemu.org/download/"
            )
        except FileNotFoundError:
            raise RuntimeError(
                "QEMU no encontrado. Instale QEMU desde:\n"
                "  https://www.qemu.org/download/\n"
                "y asegurese de que qemu-img.exe este en el PATH."
            )

        vm.status = VMStatus.SHUT_OFF
        self._registry[vm.name] = {
            "uuid": vm.uuid,
            "memory_mb": vm.memory_mb,
            "vcpus": vm.vcpus,
            "disk_size_gb": vm.disk_size_gb,
            "os_variant": vm.os_variant,
            "description": vm.description,
            "iso_path": iso_path,
            "pid": None,
        }
        self._save_registry()
        return vm

    def start_vm(self, name: str) -> bool:
        entry = self._registry.get(name)
        if not entry:
            return False

        if entry.get("pid") and self._is_process_alive(entry["pid"]):
            return False

        args = [
            QEMU_SYS,
            "-name", name,
            "-m", str(entry["memory_mb"]),
            "-smp", str(entry["vcpus"]),
            "-drive", f"file={self._vm_disk_path(name)},format=qcow2,if=virtio",
            "-netdev", "user,id=net0",
            "-device", "virtio-net,netdev=net0",
            "-display", "gtk",
            "-vga", "virtio",
        ]

        iso = entry.get("iso_path", "")
        if iso and os.path.isfile(iso):
            args.extend(["-cdrom", iso, "-boot", "order=d"])

        try:
            proc = subprocess.Popen(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
            )
            entry["pid"] = proc.pid
            self._save_registry()
            return True
        except FileNotFoundError:
            raise RuntimeError(
                "QEMU no encontrado. Instale QEMU desde:\n"
                "  https://www.qemu.org/download/"
            )
        except Exception as e:
            raise RuntimeError(f"Error al iniciar VM '{name}': {e}")

    def stop_vm(self, name: str) -> bool:
        entry = self._registry.get(name)
        if not entry:
            return False

        pid = entry.get("pid")
        if not pid or not self._is_process_alive(pid):
            entry["pid"] = None
            self._save_registry()
            return True

        try:
            if platform.system() == "Windows":
                subprocess.run(["taskkill", "/PID", str(pid), "/F"],
                               capture_output=True, timeout=15)
            else:
                os.kill(pid, signal.SIGTERM)
            entry["pid"] = None
            self._save_registry()
            return True
        except Exception:
            return False

    def restart_vm(self, name: str) -> bool:
        self.stop_vm(name)
        import time
        time.sleep(1)
        return self.start_vm(name)

    def delete_vm(self, name: str) -> bool:
        entry = self._registry.pop(name, None)
        if entry is None:
            return False

        self.stop_vm(name)
        self._save_registry()

        disk = self._vm_disk_path(name)
        if disk.exists():
            disk.unlink()
        return True

    def get_vm_status(self, name: str) -> str:
        entry = self._registry.get(name)
        if not entry:
            return VMStatus.UNKNOWN.value
        if entry.get("pid") and self._is_process_alive(entry["pid"]):
            return VMStatus.RUNNING.value
        return VMStatus.SHUT_OFF.value
