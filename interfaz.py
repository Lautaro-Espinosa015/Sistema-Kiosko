"""Módulo que contiene la interfaz gráfica con Tkinter."""

import tkinter as tk
from tkinter import messagebox, ttk

from caja import Caja, StockInsuficiente
from inventario import Inventario


class VentanaPrincipal(tk.Tk):
    """Ventana principal de la aplicación para gestión del kiosko."""

    def __init__(self, inventario: Inventario, caja: Caja):
        """Inicializa la ventana y sus componentes."""
        super().__init__()
        self.inventario = inventario
        self.caja = caja

        # Lista auxiliar: guarda, en orden, los productos que aparecen
        # en el combobox de la pestaña Ventas. La usamos para traducir
        # "qué opción eligió el usuario" -> "qué producto es".
        self._productos_combo = []

        self.title("Kiosko")
        self.geometry("1366x768")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        tab_productos = tk.Frame(notebook)
        tab_ventas = tk.Frame(notebook)
        notebook.add(tab_productos, text="Productos")
        notebook.add(tab_ventas, text="Ventas")

        # Cuando el usuario hace clic en la pestaña "Ventas", refrescamos
        # el combobox por si se cargaron productos nuevos mientras tanto.
        notebook.bind("<<NotebookTabChanged>>", self._on_cambio_pestania)

        self._crear_tab_productos(tab_productos)
        self._crear_tab_ventas(tab_ventas)

    # ==================================================================
    # PESTAÑA: PRODUCTOS
    # ==================================================================
    def _crear_tab_productos(self, contenedor):
        frame = tk.Frame(contenedor, padx=10, pady=10)
        frame.pack(fill="x")

        tk.Label(frame, text="Código:").grid(row=0, column=0, sticky="w")
        self.entry_codigo = tk.Entry(frame, width=30)
        self.entry_codigo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Nombre:").grid(row=1, column=0, sticky="w")
        self.entry_nombre = tk.Entry(frame, width=30)
        self.entry_nombre.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="Precio de venta:").grid(row=2, column=0, sticky="w")
        self.entry_precio = tk.Entry(frame, width=30)
        self.entry_precio.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(frame, text="Costo:").grid(row=3, column=0, sticky="w")
        self.entry_costo = tk.Entry(frame, width=30)
        self.entry_costo.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(frame, text="Stock inicial:").grid(row=4, column=0, sticky="w")
        self.entry_stock = tk.Entry(frame, width=30)
        self.entry_stock.grid(row=4, column=1, padx=5, pady=5)

        boton = tk.Button(frame, text="Agregar producto", command=self._on_agregar_producto)
        boton.grid(row=5, column=0, columnspan=2, pady=10)

        columnas = ("codigo", "nombre", "precio", "costo", "stock")
        self.tabla_productos = ttk.Treeview(contenedor, columns=columnas, show="headings")
        self.tabla_productos.heading("codigo", text="Código")
        self.tabla_productos.heading("nombre", text="Producto")
        self.tabla_productos.heading("precio", text="Precio")
        self.tabla_productos.heading("costo", text="Costo")
        self.tabla_productos.heading("stock", text="Stock")
        self.tabla_productos.pack(fill="both", expand=True, padx=10, pady=10)

    def _on_agregar_producto(self):
        """Maneja el evento de agregar un producto al presionar el botón."""
        codigo_texto = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get().strip()
        precio_texto = self.entry_precio.get().strip()
        costo_texto = self.entry_costo.get().strip()
        stock_texto = self.entry_stock.get().strip()

        if not all([codigo_texto, nombre, precio_texto, costo_texto, stock_texto]):
            messagebox.showwarning(
                "Faltan datos", "Completá código, nombre, precio, costo y stock."
            )
            return

        try:
            codigo = int(codigo_texto)
            precio = float(precio_texto)
            costo = float(costo_texto)
            stock = int(stock_texto)
        except ValueError:
            messagebox.showerror(
                "Error",
                "Código y stock deben ser enteros; precio y costo, números.",
            )
            return

        self.inventario.agregar_producto(codigo, nombre, precio, costo, stock)
        self._refrescar_tabla_productos()
        self._refrescar_combo_productos()

        self.entry_codigo.delete(0, tk.END)
        self.entry_nombre.delete(0, tk.END)
        self.entry_precio.delete(0, tk.END)
        self.entry_costo.delete(0, tk.END)
        self.entry_stock.delete(0, tk.END)
        self.entry_codigo.focus()

    def _refrescar_tabla_productos(self):
        for fila in self.tabla_productos.get_children():
            self.tabla_productos.delete(fila)
        for producto in self.inventario.obtener_todos():
            self.tabla_productos.insert(
                "", tk.END,
                values=(
                    producto.codigo,
                    producto.nombre,
                    f"${producto.precio:.2f}",
                    f"${producto.costo:.2f}",
                    producto.stock,
                ),
            )

    # ==================================================================
    # PESTAÑA: VENTAS
    # ==================================================================
    def _crear_tab_ventas(self, contenedor):
        frame = tk.Frame(contenedor, padx=10, pady=10)
        frame.pack(fill="x")

        tk.Label(frame, text="Producto:").grid(row=0, column=0, sticky="w")
        self.combo_productos = ttk.Combobox(frame, width=35, state="readonly")
        self.combo_productos.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Cantidad:").grid(row=1, column=0, sticky="w")
        self.entry_cantidad = tk.Entry(frame, width=10)
        self.entry_cantidad.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        boton = tk.Button(frame, text="Registrar venta", command=self._on_registrar_venta)
        boton.grid(row=2, column=0, columnspan=2, pady=10)

        columnas = ("codigo", "nombre", "cantidad", "precio", "total", "ganancia")
        self.tabla_ventas = ttk.Treeview(contenedor, columns=columnas, show="headings")
        self.tabla_ventas.heading("codigo", text="Código")
        self.tabla_ventas.heading("nombre", text="Producto")
        self.tabla_ventas.heading("cantidad", text="Cant.")
        self.tabla_ventas.heading("precio", text="Precio unit.")
        self.tabla_ventas.heading("total", text="Total")
        self.tabla_ventas.heading("ganancia", text="Ganancia")
        self.tabla_ventas.pack(fill="both", expand=True, padx=10, pady=10)

        self.label_totales = tk.Label(
            contenedor, text="Vendido: $0.00   |   Ganancia: $0.00", font=("", 10, "bold")
        )
        self.label_totales.pack(pady=5)

    def _on_cambio_pestania(self, event):
        self._refrescar_combo_productos()

    def _refrescar_combo_productos(self):
        """Vuelve a armar la lista del combobox con los productos actuales."""
        self._productos_combo = self.inventario.obtener_todos()
        self.combo_productos["values"] = [
            f"{p.codigo} - {p.nombre} (stock: {p.stock})" for p in self._productos_combo
        ]

    def _on_registrar_venta(self):
        indice = self.combo_productos.current()
        if indice < 0:
            messagebox.showwarning("Falta el producto", "Elegí un producto de la lista.")
            return

        cantidad_texto = self.entry_cantidad.get().strip()
        if not cantidad_texto:
            messagebox.showwarning("Falta la cantidad", "Ingresá la cantidad vendida.")
            return

        try:
            cantidad = int(cantidad_texto)
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero mayor a 0.")
            return

        producto = self._productos_combo[indice]

        try:
            self.caja.registrar_venta(producto.codigo, cantidad)
        except StockInsuficiente as error:
            messagebox.showerror("Stock insuficiente", str(error))
            return

        self._refrescar_tabla_ventas()
        self._refrescar_tabla_productos()
        self._refrescar_combo_productos()
        self.entry_cantidad.delete(0, tk.END)

    def _refrescar_tabla_ventas(self):
        for fila in self.tabla_ventas.get_children():
            self.tabla_ventas.delete(fila)
        for venta in self.caja.obtener_ventas():
            self.tabla_ventas.insert(
                "", tk.END,
                values=(
                    venta.codigo,
                    venta.nombre,
                    venta.cantidad,
                    f"${venta.precio_unitario:.2f}",
                    f"${venta.total:.2f}",
                    f"${venta.ganancia:.2f}",
                ),
            )
        self.label_totales.config(
            text=(
                f"Vendido: ${self.caja.total_vendido():.2f}   |   "
                f"Ganancia: ${self.caja.total_ganancia():.2f}"
            )
        )