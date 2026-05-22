from interfaces.view_interface import IMainView
from interfaces.virtualization_service import IVirtualizationService
from models.virtual_machine import VirtualMachine


class VMController:
    def __init__(self, view: IMainView, service: IVirtualizationService):
        self._view = view
        self._service = service
        self._bind_events()

    def _bind_events(self) -> None:
        self._view.set_create_callback(self._handle_create)
        self._view.set_start_callback(self._handle_start)
        self._view.set_stop_callback(self._handle_stop)
        self._view.set_restart_callback(self._handle_restart)
        self._view.set_delete_callback(self._handle_delete)
        self._view.set_refresh_callback(self._handle_refresh)
        self._handle_refresh()

    def _handle_refresh(self) -> None:
        try:
            vms = self._service.list_vms()
            self._view.update_vm_list(vms)
        except Exception as e:
            self._view.show_error(f"Error al listar VMs: {e}")

    def _handle_create(self, vm: VirtualMachine, iso_path: str = "") -> None:
        try:
            self._service.create_vm(vm, iso_path)
            msg = f"Maquina virtual '{vm.name}' creada correctamente."
            if iso_path:
                msg += f"\nISO de instalacion: {iso_path}"
            self._view.show_info(msg)
            self._handle_refresh()
        except Exception as e:
            self._view.show_error(f"Error al crear VM: {e}")

    def _handle_start(self, name: str) -> None:
        try:
            if self._service.start_vm(name):
                svc_type = type(self._service).__name__
                if "Qemu" in svc_type:
                    msg = f"VM '{name}' iniciada.\n\nLa ventana grafica de QEMU se abrira automaticamente.\nSi no la ves, revisa la barra de tareas."
                else:
                    msg = (
                        f"VM '{name}' iniciada.\n\n"
                        f"Para ver la consola grafica:\n"
                        f"  virt-viewer {name}\n"
                        f"o conectar via VNC con virt-manager"
                    )
                self._view.show_info(msg)
            else:
                self._view.show_error(f"No se pudo iniciar '{name}'.")
            self._handle_refresh()
        except Exception as e:
            self._view.show_error(f"Error: {e}")

    def _handle_stop(self, name: str) -> None:
        try:
            if self._service.stop_vm(name):
                self._view.show_info(f"VM '{name}' detenida.")
            else:
                self._view.show_error(f"No se pudo detener '{name}'.")
            self._handle_refresh()
        except Exception as e:
            self._view.show_error(f"Error: {e}")

    def _handle_restart(self, name: str) -> None:
        if not self._view.show_confirm(f"Reiniciar VM '{name}'?"):
            return
        try:
            if self._service.restart_vm(name):
                self._view.show_info(f"VM '{name}' reiniciada.")
            else:
                self._view.show_error(f"No se pudo reiniciar '{name}'.")
            self._handle_refresh()
        except Exception as e:
            self._view.show_error(f"Error: {e}")

    def _handle_delete(self, name: str) -> None:
        if not self._view.show_confirm(
            f"Esta seguro de eliminar la VM '{name}'?\nEsta accion no se puede deshacer."):
            return
        try:
            if self._service.delete_vm(name):
                self._view.show_info(f"VM '{name}' eliminada.")
            else:
                self._view.show_error(f"No se pudo eliminar '{name}'.")
            self._handle_refresh()
        except Exception as e:
            self._view.show_error(f"Error: {e}")
