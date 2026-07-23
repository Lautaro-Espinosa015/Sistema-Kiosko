import tkinter as tk
from tkinter import ttk, messagebox
from inventario import Inventario


class VentanaPrincipal(tk.Tk):
    """
    Es la ventana de la aplicación.
    Hereda de tk.Tk, así que ES la ventana en sí misma.
 
    Importante: esta clase NO decide cómo se guardan los productos,
    solo le pide a "self.inventario" que lo haga. Esa es la idea
    de separar la interfaz de la lógica.
    """
 
    def __init__(self, inventario: Inventario):
        super().__init__()
        self.inventario = inventario
 
        self.title("Kiosko - Paso 1: Cargar productos")
        self.geometry("520x420")
 
        self._crear_formulario()
        self._crear_tabla()
 
    # ------------------------------------------------------------------
    # Construcción de la interfaz (métodos "privados", por eso el guion bajo)
    # ------------------------------------------------------------------
    def _crear_formulario(self):
        frame = tk.Frame(self, padx=10, pady=10)
        frame.pack(fill="x")
 
        tk.Label(frame, text="Nombre del producto:").grid(row=0, column=0, sticky="w")
        self.entry_nombre = tk.Entry(frame, width=30)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5)
 
        tk.Label(frame, text="Precio:").grid(row=1, column=0, sticky="w")
        self.entry_precio = tk.Entry(frame, width=30)
        self.entry_precio.grid(row=1, column=1, padx=5, pady=5)
 
        tk.Label(frame, text="Stock inicial:").grid(row=2, column=0, sticky="w")
        self.entry_stock = tk.Entry(frame, width=30)
        self.entry_stock.grid(row=2, column=1, padx=5, pady=5)
 
        boton = tk.Button(frame, text="Agregar producto", command=self._on_agregar_producto)
        boton.grid(row=3, column=0, columnspan=2, pady=10)
 
    def _crear_tabla(self):
        columnas = ("nombre", "precio", "stock")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings")
        self.tabla.heading("nombre", text="Producto")
        self.tabla.heading("precio", text="Precio")
        self.tabla.heading("stock", text="Stock")
        self.tabla.pack(fill="both", expand=True, padx=10, pady=10)
 
    # ------------------------------------------------------------------
    # Manejadores de eventos (lo que pasa cuando el usuario interactúa)
    # ------------------------------------------------------------------
    def _on_agregar_producto(self):
        nombre = self.entry_nombre.get().strip()
        precio_texto = self.entry_precio.get().strip()
        stock_texto = self.entry_stock.get().strip()
 
        if not nombre or not precio_texto or not stock_texto:
            messagebox.showwarning("Faltan datos", "Completá nombre, precio y stock.")
            return
 
        try:
            precio = float(precio_texto)
            stock = int(stock_texto)
        except ValueError:
            messagebox.showerror("Error", "El precio y el stock tienen que ser números.")
            return
 
        # Acá la ventana NO guarda nada por su cuenta: le delega el trabajo al inventario.
        self.inventario.agregar_producto(nombre, precio, stock)
        self._refrescar_tabla()
 
        self.entry_nombre.delete(0, tk.END)
        self.entry_precio.delete(0, tk.END)
        self.entry_stock.delete(0, tk.END)
        self.entry_nombre.focus()
 
    def _refrescar_tabla(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for producto in self.inventario.obtener_todos():
            self.tabla.insert(
                "", tk.END,
                values=(producto.nombre, f"${producto.precio:.2f}", producto.stock)
            )
 