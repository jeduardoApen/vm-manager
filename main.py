import sys
import os
import platform

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from views.main_window import MainWindow
from controllers.vm_controller import VMController
from interfaces.virtualization_service import IVirtualizationService


def create_service() -> IVirtualizationService:
    if "--libvirt" in sys.argv:
        from services.libvirt_service import LibvirtService
        return LibvirtService()

    if "--mock" in sys.argv:
        from services.mock_virt_service import MockVirtualizationService
        return MockVirtualizationService()

    if platform.system() == "Linux":
        try:
            from services.libvirt_service import LibvirtService
            svc = LibvirtService()
            return svc
        except (ImportError, ConnectionError):
            pass

    from services.qemu_service import QemuService
    return QemuService()


def main():
    service = create_service()
    view = MainWindow()
    VMController(view, service)
    view.run()


if __name__ == "__main__":
    main()
