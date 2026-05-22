from abc import ABC, abstractmethod
from typing import List
from models.virtual_machine import VirtualMachine


class IVirtualizationService(ABC):
    @abstractmethod
    def list_vms(self) -> List[VirtualMachine]:
        pass

    @abstractmethod
    def create_vm(self, vm: VirtualMachine, iso_path: str = "") -> VirtualMachine:
        pass

    @abstractmethod
    def start_vm(self, name: str) -> bool:
        pass

    @abstractmethod
    def stop_vm(self, name: str) -> bool:
        pass

    @abstractmethod
    def restart_vm(self, name: str) -> bool:
        pass

    @abstractmethod
    def delete_vm(self, name: str) -> bool:
        pass

    @abstractmethod
    def get_vm_status(self, name: str) -> str:
        pass
