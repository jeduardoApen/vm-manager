# VM Manager

Cliente de virtualizacion con interfaz grafica para gestionar maquinas virtuales. Permite crear, iniciar, detener, reiniciar y eliminar VMs usando QEMU (Windows/Linux) o libvirt (Linux).

## Requisitos

- Python 3.8 o superior
- Tkinter (incluido con Python en Windows)
- **Windows:** QEMU
- **Linux:** libvirt + QEMU/KVM, o solo QEMU

## Instalacion

### 1. Clonar el proyecto

```bash
git clone <url-del-repo>
cd vm_manager
```

### 2. Instalar dependencias

#### Windows

**Paso 1 - QEMU**

Descargar QEMU para Windows desde: https://www.qemu.org/download/#windows

Instalarlo en la ruta por defecto (`C:\Program Files\qemu\`). La aplicacion busca QEMU automaticamente en:
- `C:\Program Files\qemu\`
- `C:\Program Files (x86)\qemu\`

Si lo instalas en otra ruta, agregala al PATH de Windows:
1. Inicio → buscar "Variables de entorno" → Variables de entorno
2. Seleccionar `Path` en Variables del sistema → Editar
3. Nuevo → pegar la ruta (ej: `D:\qemu`)
4. Aceptar y reiniciar la terminal

**Paso 2 - Verificar QEMU**

```powershell
qemu-img --version
qemu-system-x86_64 --version
```

Ambos deben mostrar su version. Si no se reconocen, revisa el PATH o reinstala.

#### Linux

**Opcion A - QEMU (recomendado, misma experiencia que Windows)**

```bash
sudo apt install qemu-system-x86 qemu-utils   # Debian/Ubuntu
sudo dnf install qemu-kvm qemu-img             # Fedora
sudo pacman -S qemu-full                        # Arch
```

**Opcion B - libvirt (integracion nativa con hipervisor)**

```bash
sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients virt-manager virt-viewer
sudo usermod -aG libvirt $USER
# Cerrar sesion y volver a entrar para que apliquen los permisos

pip install libvirt-python
# Requiere libvirt-dev:
sudo apt install libvirt-dev pkg-config
```

### 3. Instalar dependencias Python

```bash
pip install -r requirements.txt
```

## Ejecucion

```bash
cd vm_manager
python main.py
```

### Opciones de ejecucion

| Comando | Descripcion |
|---------|-------------|
| `python main.py` | Auto-detecta: QEMU en Windows, libvirt en Linux |
| `python main.py --qemu` | Fuerza uso de QEMU |
| `python main.py --libvirt` | Fuerza uso de libvirt |
| `python main.py --mock` | Modo simulacion (pruebas sin virtualizacion real) |

## Uso

Al abrir la aplicacion veras:

```
┌──────────────────────────────────────────────────────────┐
│  VM Manager   Gestor de Maquinas Virtuales               │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┬──────────┬───────┬──────────┬────────────┐ │
│  │ Nombre   │ Estado   │ vCPUs │ Mem(MB)  │ UUID       │ │
│  ├──────────┼──────────┼───────┼──────────┼────────────┤ │
│  │ Ubuntu   │ Apagada  │   2   │  2048    │ abc123...  │ │
│  └──────────┴──────────┴───────┴──────────┴────────────┘ │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  [+ Crear] [▶ Iniciar] [■ Detener] [↺ Reiniciar]         │
│  [✕ Eliminar]                             [⟳ Refrescar]  │
└──────────────────────────────────────────────────────────┘
```

### Estados de VM (colores en la tabla)

| Color | Estado | Significado |
|-------|--------|-------------|
| Verde | En ejecucion | La VM esta corriendo |
| Rojo | Apagada | La VM esta detenida |
| Naranja | Pausada | La VM esta suspendida |

### Crear una VM

1. Clic en **+ Crear**
2. Completar los campos:
   - **Nombre:** identificador unico (ej: `Ubuntu-Server`)
   - **Memoria (MB):** RAM asignada (ej: `2048`)
   - **vCPUs:** nucleos virtuales (ej: `2`)
   - **Disco (GB):** tamaño del disco virtual (ej: `20`)
   - **Sistema Operativo:** etiqueta del SO (ej: `Ubuntu`)
   - **Imagen ISO:** (opcional) archivo `.iso` de instalacion. Clic en `...` para buscarlo en el disco
3. Clic en **Crear**

### Iniciar una VM

1. Seleccionar la VM en la tabla
2. Clic en **▶ Iniciar**
3. Con QEMU se abre automaticamente una ventana grafica. Si no aparece, revisa la barra de tareas
4. Seguir el instalador del SO dentro de la ventana de QEMU

### Detener / Reiniciar / Eliminar

Seleccionar la VM en la tabla y usar el boton correspondiente. Eliminar requiere confirmacion.

### Ver la pantalla de la VM

- **QEMU:** la ventana grafica se abre automaticamente al iniciar
- **libvirt:** usar `virt-viewer <nombre>` desde terminal, o abrir `virt-manager`

## Almacenamiento

Todas las VMs y discos se guardan en:

| SO | Ruta |
|----|------|
| Windows | `C:\Users\<usuario>\.vm_manager\` |
| Linux | `/home/<usuario>/.vm_manager/` |

Estructura:
```
~/.vm_manager/
├── vms.json          # Registro de VMs (nombres, config, PIDs)
└── images/
    ├── Ubuntu.qcow2   # Disco virtual
    └── Debian.qcow2   # Disco virtual
```

## Arquitectura

El proyecto sigue los principios **SOLID**:

```
vm_manager/
├── main.py                        # Punto de entrada
├── requirements.txt               # Dependencias Python
├── models/
│   └── virtual_machine.py         # Dataclass VirtualMachine + VMStatus (SRP)
├── interfaces/
│   ├── virtualization_service.py  # IVirtualizationService - abstraccion (ISP, DIP)
│   └── view_interface.py          # IMainView - abstraccion de vista (ISP, DIP)
├── services/
│   ├── qemu_service.py            # Implementacion QEMU (OCP, LSP)
│   ├── libvirt_service.py         # Implementacion libvirt (OCP, LSP)
│   └── mock_virt_service.py       # Implementacion simulada (OCP, LSP)
├── controllers/
│   └── vm_controller.py           # Orquestador vista-servicio (SRP)
└── views/
    └── main_window.py             # GUI Tkinter + dialogo creacion VM (SRP)
```

- **SRP** - Cada clase tiene una unica responsabilidad
- **OCP** - Nuevos backends de virtualizacion se agregan sin modificar vistas ni controladores
- **LSP** - QemuService, LibvirtService y MockVirtualizationService son intercambiables
- **ISP** - Interfaces especificas: `IVirtualizationService` e `IMainView`
- **DIP** - El controlador depende de abstracciones, no de implementaciones concretas

## Solucion de problemas

| Problema | Solucion |
|----------|----------|
| `QEMU no encontrado` | Instalar QEMU y verificar que este en el PATH |
| `Error al crear disco` | Verificar permisos de escritura en `~/.vm_manager/` |
| `La VM no inicia` | Revisar que la ISO exista y no este corrupta |
| `No se ve la ventana grafica` | Revisar la barra de tareas. En algunos sistemas la ventana puede abrirse minimizada |
| `libvirt error` | Verificar que el servicio libvirtd este corriendo: `sudo systemctl start libvirtd` |
