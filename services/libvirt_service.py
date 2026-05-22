import uuid
from typing import List, Optional
from models.virtual_machine import VirtualMachine, VMStatus
from interfaces.virtualization_service import IVirtualizationService


class LibvirtService(IVirtualizationService):
    def __init__(self, uri: str = "qemu:///system"):
        self._uri = uri
        self._conn: Optional[object] = None
        self._connect()

    def _connect(self) -> None:
        import libvirt
        try:
            self._conn = libvirt.open(self._uri)
        except libvirt.libvirtError as e:
            self._conn = None

    def _ensure_connection(self) -> object:
        import libvirt
        if self._conn is None:
            self._connect()
        if self._conn is None:
            raise ConnectionError(
                f"No se pudo conectar al hipervisor: {self._uri}"
            )
        return self._conn

    @staticmethod
    def _parse_status(domain, status_code: int) -> VMStatus:
        import libvirt
        status_map = {
            libvirt.VIR_DOMAIN_RUNNING: VMStatus.RUNNING,
            libvirt.VIR_DOMAIN_SHUTOFF: VMStatus.SHUT_OFF,
            libvirt.VIR_DOMAIN_PAUSED: VMStatus.PAUSED,
        }
        return status_map.get(status_code, VMStatus.UNKNOWN)

    def list_vms(self) -> List[VirtualMachine]:
        conn = self._ensure_connection()
        domains = conn.listAllDomains(0)
        vms = []
        for dom in domains:
            name = dom.name()
            state, _ = dom.state()
            info = dom.info()
            vms.append(VirtualMachine(
                name=name,
                uuid=dom.UUIDString(),
                memory_mb=info[1] // 1024,
                vcpus=info[3],
                status=self._parse_status(dom, state),
            ))
        return vms

    def create_vm(self, vm: VirtualMachine, iso_path: str = "") -> VirtualMachine:
        conn = self._ensure_connection()
        import libvirt

        xml = self._build_domain_xml(vm, iso_path)
        try:
            dom = conn.createXML(xml, 0)
            vm.uuid = dom.UUIDString()
            vm.status = VMStatus.RUNNING
            return vm
        except libvirt.libvirtError as e:
            raise RuntimeError(f"Error al crear VM '{vm.name}': {e}")

    def start_vm(self, name: str) -> bool:
        conn = self._ensure_connection()
        try:
            dom = conn.lookupByName(name)
            dom.create()
            return True
        except Exception:
            return False

    def stop_vm(self, name: str) -> bool:
        conn = self._ensure_connection()
        try:
            dom = conn.lookupByName(name)
            dom.shutdown()
            return True
        except Exception:
            return False

    def restart_vm(self, name: str) -> bool:
        conn = self._ensure_connection()
        try:
            dom = conn.lookupByName(name)
            dom.reboot(0)
            return True
        except Exception:
            return False

    def delete_vm(self, name: str) -> bool:
        conn = self._ensure_connection()
        try:
            dom = conn.lookupByName(name)
            state, _ = dom.state()
            import libvirt
            if state == libvirt.VIR_DOMAIN_RUNNING:
                dom.destroy()
            dom.undefine()
            return True
        except Exception:
            return False

    def get_vm_status(self, name: str) -> str:
        conn = self._ensure_connection()
        try:
            dom = conn.lookupByName(name)
            state, _ = dom.state()
            return self._parse_status(dom, state).value
        except Exception:
            return VMStatus.UNKNOWN.value

    def _build_domain_xml(self, vm: VirtualMachine, iso_path: str) -> str:
        return f"""<domain type='kvm'>
  <name>{vm.name}</name>
  <uuid>{vm.uuid or uuid.uuid4()}</uuid>
  <memory unit='MiB'>{vm.memory_mb}</memory>
  <vcpu>{vm.vcpus}</vcpu>
  <os>
    <type arch='x86_64' machine='q35'>hvm</type>
    {'<boot dev=\'cdrom\'/>' if iso_path else '<boot dev=\'hd\'/>'}
  </os>
  <devices>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='/var/lib/libvirt/images/{vm.name}.qcow2'/>
      <target dev='vda' bus='virtio'/>
    </disk>
    {f'<disk type=\'file\' device=\'cdrom\'><source file=\'{iso_path}\'/><target dev=\'sda\' bus=\'sata\'/></disk>' if iso_path else ''}
    <interface type='network'>
      <source network='default'/>
      <model type='virtio'/>
    </interface>
    <graphics type='vnc' port='-1' autoport='yes'/>
  </devices>
</domain>"""
