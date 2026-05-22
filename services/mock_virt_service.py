import uuid
from typing import Dict, List
from models.virtual_machine import VirtualMachine, VMStatus
from interfaces.virtualization_service import IVirtualizationService


class MockVirtualizationService(IVirtualizationService):
    def __init__(self):
        self._vms: Dict[str, VirtualMachine] = {}

    def list_vms(self) -> List[VirtualMachine]:
        return list(self._vms.values())

    def create_vm(self, vm: VirtualMachine, iso_path: str = "") -> VirtualMachine:
        vm.uuid = str(uuid.uuid4())
        vm.status = VMStatus.SHUT_OFF
        self._vms[vm.name] = vm
        return vm

    def start_vm(self, name: str) -> bool:
        vm = self._vms.get(name)
        if vm and vm.status != VMStatus.RUNNING:
            vm.status = VMStatus.RUNNING
            return True
        return False

    def stop_vm(self, name: str) -> bool:
        vm = self._vms.get(name)
        if vm and vm.status != VMStatus.SHUT_OFF:
            vm.status = VMStatus.SHUT_OFF
            return True
        return False

    def restart_vm(self, name: str) -> bool:
        vm = self._vms.get(name)
        if vm:
            vm.status = VMStatus.SHUT_OFF
            vm.status = VMStatus.RUNNING
            return True
        return False

    def delete_vm(self, name: str) -> bool:
        return self._vms.pop(name, None) is not None

    def get_vm_status(self, name: str) -> str:
        vm = self._vms.get(name)
        return vm.status.value if vm else VMStatus.UNKNOWN.value
