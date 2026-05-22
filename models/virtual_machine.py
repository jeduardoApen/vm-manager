from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class VMStatus(Enum):
    RUNNING = "En ejecucion"
    SHUT_OFF = "Apagada"
    PAUSED = "Pausada"
    UNKNOWN = "Desconocida"


@dataclass
class VirtualMachine:
    name: str
    uuid: str = ""
    memory_mb: int = 1024
    vcpus: int = 1
    disk_size_gb: int = 10
    os_variant: str = "generic"
    status: VMStatus = VMStatus.UNKNOWN
    description: str = ""

    @property
    def memory_gb(self) -> float:
        return self.memory_mb / 1024
