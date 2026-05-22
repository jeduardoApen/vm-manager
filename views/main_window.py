import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from typing import Callable, Dict, List, Optional

from interfaces.view_interface import IMainView
from models.virtual_machine import VirtualMachine, VMStatus


class MainWindow(IMainView):
    def __init__(self, title: str = "VM Manager - Gestion de Maquinas Virtuales"):
        self._root = tk.Tk()
        self._root.title(title)
        self._root.geometry("820x520")
        self._root.resizable(True, True)
        self._root.configure(bg="#1e1e2e")

        self._controller = None
        self._on_create_callback = None
        self._on_start_callback = None
        self._on_stop_callback = None
        self._on_restart_callback = None
        self._on_delete_callback = None
        self._on_refresh_callback = None

        self._build_ui()

    def set_controller(self, controller) -> None:
        self._controller = controller

    def set_create_callback(self, callback) -> None:
        self._on_create_callback = callback

    def set_start_callback(self, callback) -> None:
        self._on_start_callback = callback

    def set_stop_callback(self, callback) -> None:
        self._on_stop_callback = callback

    def set_restart_callback(self, callback) -> None:
        self._on_restart_callback = callback

    def set_delete_callback(self, callback) -> None:
        self._on_delete_callback = callback

    def set_refresh_callback(self, callback) -> None:
        self._on_refresh_callback = callback

    def _build_ui(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#2e2e3e",
                        foreground="#cdd6f4",
                        fieldbackground="#2e2e3e",
                        rowheight=30,
                        font=("Consolas", 10))
        style.configure("Treeview.Heading",
                        background="#45475a",
                        foreground="#cdd6f4",
                        font=("Consolas", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", "#585b70")])
        style.configure("TButton",
                        background="#45475a",
                        foreground="#cdd6f4",
                        font=("Consolas", 10, "bold"),
                        padding=8)
        style.map("TButton",
                  background=[("active", "#585b70")])
        style.configure("TFrame", background="#1e1e2e")

        header = tk.Frame(self._root, bg="#313244", height=50)
        header.pack(fill=tk.X, side=tk.TOP)
        tk.Label(header, text="VM Manager", bg="#313244", fg="#cdd6f4",
                 font=("Consolas", 18, "bold")).pack(side=tk.LEFT, padx=20, pady=8)
        tk.Label(header, text="Gestor de Maquinas Virtuales",
                 bg="#313244", fg="#a6adc8", font=("Consolas", 10)).pack(
                 side=tk.LEFT, padx=5, pady=14)

        self._tree_frame = tk.Frame(self._root, bg="#1e1e2e")
        self._tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("Nombre", "Estado", "vCPUs", "Memoria (MB)", "UUID")
        self._tree = ttk.Treeview(self._tree_frame, columns=columns, show="headings",
                                   selectmode="browse")
        widths = [150, 140, 80, 130, 280]
        for col, w in zip(columns, widths):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, anchor=tk.CENTER)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self._tree_frame, orient=tk.VERTICAL,
                                  command=self._tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.tag_configure("running", foreground="#a6e3a1")
        self._tree.tag_configure("shutoff", foreground="#f38ba8")
        self._tree.tag_configure("paused", foreground="#fab387")

        toolbar = tk.Frame(self._root, bg="#313244", height=44)
        toolbar.pack(fill=tk.X, side=tk.BOTTOM)

        btn_config = {"font": ("Consolas", 10, "bold"), "padx": 12, "pady": 4,
                      "bg": "#45475a", "fg": "#cdd6f4", "activebackground": "#585b70",
                      "activeforeground": "#cdd6f4", "relief": tk.FLAT, "cursor": "hand2"}

        tk.Button(toolbar, text="+ Crear", command=self._on_create,
                  **btn_config).pack(side=tk.LEFT, padx=6, pady=6)
        tk.Button(toolbar, text="▶ Iniciar", command=self._on_start,
                  **{**btn_config, "bg": "#40a02b"}).pack(side=tk.LEFT, padx=6)
        tk.Button(toolbar, text="■ Detener", command=self._on_stop,
                  **{**btn_config, "bg": "#e64553"}).pack(side=tk.LEFT, padx=6)
        tk.Button(toolbar, text="↺ Reiniciar", command=self._on_restart,
                  **{**btn_config, "bg": "#df8e1d"}).pack(side=tk.LEFT, padx=6)
        tk.Button(toolbar, text="✕ Eliminar", command=self._on_delete,
                  **{**btn_config, "bg": "#d20f39"}).pack(side=tk.LEFT, padx=6)
        tk.Button(toolbar, text="⟳ Refrescar", command=self._on_refresh,
                  **{**btn_config, "bg": "#1e66f5"}).pack(side=tk.RIGHT, padx=6)

    def _on_create(self) -> None:
        dialog = CreateVMDialog(self._root)
        result = dialog.show()
        if result and self._on_create_callback:
            self._on_create_callback(result["vm"], result["iso_path"])

    def _on_start(self) -> None:
        name = self.get_selected_vm_name()
        if name and self._on_start_callback:
            self._on_start_callback(name)

    def _on_stop(self) -> None:
        name = self.get_selected_vm_name()
        if name and self._on_stop_callback:
            self._on_stop_callback(name)

    def _on_restart(self) -> None:
        name = self.get_selected_vm_name()
        if name and self._on_restart_callback:
            self._on_restart_callback(name)

    def _on_delete(self) -> None:
        name = self.get_selected_vm_name()
        if name and self._on_delete_callback:
            self._on_delete_callback(name)

    def _on_refresh(self) -> None:
        if self._on_refresh_callback:
            self._on_refresh_callback()

    def update_vm_list(self, vms: List[VirtualMachine]) -> None:
        for item in self._tree.get_children():
            self._tree.delete(item)
        for vm in vms:
            tag = ""
            if vm.status == VMStatus.RUNNING:
                tag = "running"
            elif vm.status == VMStatus.SHUT_OFF:
                tag = "shutoff"
            elif vm.status == VMStatus.PAUSED:
                tag = "paused"
            self._tree.insert("", tk.END,
                              values=(vm.name, vm.status.value, vm.vcpus,
                                      vm.memory_mb, vm.uuid),
                              tags=(tag,))

    def show_error(self, message: str) -> None:
        messagebox.showerror("Error", message)

    def show_info(self, message: str) -> None:
        messagebox.showinfo("Informacion", message)

    def show_confirm(self, message: str) -> bool:
        return messagebox.askyesno("Confirmacion", message)

    def get_selected_vm_name(self) -> str:
        selection = self._tree.selection()
        if selection:
            return self._tree.item(selection[0], "values")[0]
        self.show_info("Seleccione una maquina virtual de la lista.")
        return ""

    def refresh_view(self) -> None:
        if self._on_refresh_callback:
            self._on_refresh_callback()

    def run(self) -> None:
        self._root.mainloop()

    def destroy(self) -> None:
        self._root.destroy()


class CreateVMDialog:
    def __init__(self, parent: tk.Tk):
        self._result: Optional[Dict] = None
        self._dialog = tk.Toplevel(parent)
        self._dialog.title("Crear Nueva Maquina Virtual")
        self._dialog.geometry("440x470")
        self._dialog.configure(bg="#1e1e2e")
        self._dialog.resizable(False, False)
        self._dialog.transient(parent)
        self._dialog.grab_set()

        self._name_var = tk.StringVar()
        self._memory_var = tk.StringVar(value="2048")
        self._vcpus_var = tk.StringVar(value="2")
        self._disk_var = tk.StringVar(value="20")
        self._os_var = tk.StringVar(value="Ubuntu")
        self._desc_var = tk.StringVar()
        self._iso_var = tk.StringVar()

        self._build_dialog()

    def _build_dialog(self) -> None:
        tk.Label(self._dialog, text="Nueva Maquina Virtual",
                 bg="#1e1e2e", fg="#cdd6f4",
                 font=("Consolas", 14, "bold")).pack(pady=12)

        frame = tk.Frame(self._dialog, bg="#1e1e2e")
        frame.pack(padx=20, fill=tk.BOTH, expand=True)

        lbl_style = {"bg": "#1e1e2e", "fg": "#a6adc8", "font": ("Consolas", 10),
                     "anchor": "w"}
        ent_style = {"font": ("Consolas", 10), "bg": "#313244", "fg": "#cdd6f4",
                     "insertbackground": "#cdd6f4", "relief": tk.FLAT}

        fields = [
            ("Nombre:", self._name_var),
            ("Memoria (MB):", self._memory_var),
            ("vCPUs:", self._vcpus_var),
            ("Disco (GB):", self._disk_var),
            ("Sistema Operativo:", self._os_var),
        ]
        for label_text, var in fields:
            row = tk.Frame(frame, bg="#1e1e2e")
            row.pack(fill=tk.X, pady=4)
            tk.Label(row, text=label_text, width=22, **lbl_style).pack(side=tk.LEFT)
            tk.Entry(row, textvariable=var, width=24, **ent_style).pack(side=tk.LEFT)

        iso_row = tk.Frame(frame, bg="#1e1e2e")
        iso_row.pack(fill=tk.X, pady=4)
        tk.Label(iso_row, text="Imagen ISO:", width=22, **lbl_style).pack(side=tk.LEFT)
        tk.Entry(iso_row, textvariable=self._iso_var, width=18, **ent_style).pack(side=tk.LEFT)
        tk.Button(iso_row, text="...", width=4, bg="#45475a", fg="#cdd6f4",
                  activebackground="#585b70", activeforeground="#cdd6f4",
                  relief=tk.FLAT, cursor="hand2", font=("Consolas", 10, "bold"),
                  command=self._browse_iso).pack(side=tk.LEFT, padx=2)

        tk.Label(frame, text="Descripcion:", bg="#1e1e2e", fg="#a6adc8",
                 font=("Consolas", 10), anchor="w").pack(fill=tk.X, pady=(8, 0))
        tk.Entry(frame, textvariable=self._desc_var, width=48, **ent_style).pack(
            fill=tk.X, pady=4)

        btn_frame = tk.Frame(self._dialog, bg="#313244", height=44)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 0))

        btn_conf = {"font": ("Consolas", 10, "bold"), "padx": 16, "pady": 5,
                    "relief": tk.FLAT, "cursor": "hand2"}
        tk.Button(btn_frame, text="Cancelar", bg="#45475a", fg="#cdd6f4",
                  activebackground="#585b70", activeforeground="#cdd6f4",
                  command=self._dialog.destroy, **btn_conf).pack(side=tk.RIGHT, padx=8, pady=6)
        tk.Button(btn_frame, text="Crear", bg="#40a02b", fg="#cdd6f4",
                  activebackground="#44b633", activeforeground="#cdd6f4",
                  command=self._on_create, **btn_conf).pack(side=tk.RIGHT, pady=6)

    def _browse_iso(self) -> None:
        path = filedialog.askopenfilename(
            title="Seleccionar imagen ISO",
            filetypes=[("Imagenes ISO", "*.iso"), ("Todos", "*.*")]
        )
        if path:
            self._iso_var.set(path)

    def _on_create(self) -> None:
        name = self._name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "El nombre de la VM es obligatorio.")
            return
        try:
            memory = int(self._memory_var.get())
            vcpus = int(self._vcpus_var.get())
            disk = int(self._disk_var.get())
        except ValueError:
            messagebox.showerror("Error", "Memoria, vCPUs y Disco deben ser numeros enteros.")
            return

        self._result = {
            "vm": VirtualMachine(
                name=name,
                memory_mb=memory,
                vcpus=vcpus,
                disk_size_gb=disk,
                os_variant=self._os_var.get(),
                description=self._desc_var.get(),
            ),
            "iso_path": self._iso_var.get(),
        }
        self._dialog.destroy()

    def show(self) -> Optional[Dict]:
        self._dialog.wait_window()
        return self._result
