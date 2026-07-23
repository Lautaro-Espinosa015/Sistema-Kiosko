"""Módulo que contiene la interfaz gráfica con Tkinter."""

import tkinter as tk
from tkinter import messagebox, ttk
from inventario import Inventario


class VentanaPrincipal(tk.Tk):
    """Ventana principal de la aplicación para gestión del kiosko."""

    def __init__(self, inventario: Inventario):
        """Inicializa la ventana y sus componentes."""
        super().__init__()
        self.inventario = inventario

        self.title("Kiosko - Paso 1: Cargar productos")
        self.geometry("520x450")

        self.entry_codigo = None
        self.entry_nombre = None
        self.entry_precio = None
        self.entry_stock = None
        self.tabla = None

        self._crear_formulario()
        self._crear_tabla()

    def _crear_formulario(self):
        """Crea los campos de texto y botones del formulario."""
        frame = tk.Frame(self, padx=10, pady=10)
        frame.pack(fill="x")

        # Fila 0: Código
        tk.Label(frame, text="Código del producto:").grid(
            row=0, column=0, sticky="w"
        )
        self.entry_codigo = tk.Entry(frame, width=30)
        self.entry_codigo.grid(row=0, column=1, padx=5, pady=5)

        # Fila 1: Nombre
        tk.Label(frame, text="Nombre del producto:").grid(
            row=1, column=0, sticky="w"
        )
        self.entry_nombre = tk.Entry(frame, width=30)
        self.entry_nombre.grid(row=1, column=1, padx=5, pady=5)

        # Fila 2: Precio
        tk.Label(frame, text="Precio:").grid(row=2, column=0, sticky="w")
        self.entry_precio = tk.Entry(frame, width=30)
        self.entry_precio.grid(row=2, column=1, padx=5, pady=5)

        # Fila 3: Stock
        tk.Label(frame, text="Stock inicial:").grid(row=3, column=0, sticky="w")
        self.entry_stock = tk.Entry(frame, width=30)
        self.entry_stock.grid(row=3, column=1, padx=5, pady=5)

        # Fila 4: Botón
        boton = tk.Button(
            frame, text="Agregar producto", command=self._on_agregar_producto
        )
        boton.grid(row=4, column=0, columnspan=2, pady=10)

    def _crear_tabla(self):
        """Inicializa la tabla donde se muestran los productos."""
        columnas = ("codigo", "nombre", "precio", "stock")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings")
        self.tabla.heading("codigo", text="Código")
        self.tabla.heading("nombre", text="Producto")
        self.tabla.heading("precio", text="Precio")
        self.tabla.heading("stock", text="Stock")
        self.tabla.pack(fill="both", expand=True, padx=10, pady=10)

    def _on_agregar_producto(self):
        """Maneja el evento de agregar un producto al presionar el botón."""
        codigo_texto = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get().strip()
        precio_texto = self.entry_precio.get().strip()
        stock_texto = self.entry_stock.get().strip()

        if not codigo_texto or not nombre or not precio_texto or not stock_texto:
            messagebox.showwarning(
                "Faltan datos", "Completá código, nombre, precio y stock."
            )
            return

        try:
            codigo = int(codigo_texto)
            precio = float(precio_texto)
            stock = int(stock_texto)
        except ValueError:
            messagebox.showerror(
                "Error", "El código y el stock deben ser enteros, y el precio un número."
            )
            return

        # Le pasamos el 'codigo' como primer argumento al inventario
        self.inventario.agregar_producto(codigo, nombre, precio, stock)
        self._refrescar_tabla()

        # Limpiamos los campos
        self.entry_codigo.delete(0, tk.END)
        self.entry_nombre.delete(0, tk.END)
        self.entry_precio.delete(0, tk.END)
        self.entry_stock.delete(0, tk.END)
        self.entry_codigo.focus()

    def _refrescar_tabla(self):
        """Limpia y vuelve a cargar los datos en la tabla."""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for producto in self.inventario.obtener_todos():
            self.tabla.insert(
                "",
                tk.END,
                values=(
                    producto.codigo,
                    producto.nombre,
                    f"${producto.precio:.2f}",
                    producto.stock,
                ),
            )