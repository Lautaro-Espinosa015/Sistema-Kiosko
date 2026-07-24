from tkinter import messagebox

import excel_datos
from caja import Caja
from interfaz import VentanaPrincipal
from inventario import Inventario

def main():
    """Inicializa la aplicación, carga el Excel (o crea uno nuevo) y abre la ventana."""
    inventario = Inventario()
    caja = Caja(inventario)
    app = VentanaPrincipal(inventario, caja)

    archivo_existia = excel_datos.cargar_datos(inventario, caja)
    app.refrescar_todo()

    if not archivo_existia:
        messagebox.showwarning(
            "Archivo no encontrado",
            f"No se encontró '{excel_datos.NOMBRE_ARCHIVO}' en esta carpeta.\n"
            "Se creó uno nuevo y vacío para empezar a cargar datos.",
        )

    app.mainloop()


if __name__ == "__main__":
    main()