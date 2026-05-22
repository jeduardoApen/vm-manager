from abc import ABC, abstractmethod
from typing import List
from models.virtual_machine import VirtualMachine


class IMainView(ABC):
    @abstractmethod
    def update_vm_list(self, vms: List[VirtualMachine]) -> None:
        pass

    @abstractmethod
    def show_error(self, message: str) -> None:
        pass

    @abstractmethod
    def show_info(self, message: str) -> None:
        pass

    @abstractmethod
    def show_confirm(self, message: str) -> bool:
        pass

    @abstractmethod
    def get_selected_vm_name(self) -> str:
        pass

    @abstractmethod
    def refresh_view(self) -> None:
        pass
