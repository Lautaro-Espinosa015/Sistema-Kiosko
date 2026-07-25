"""Módulo que contiene la interfaz gráfica con Tkinter."""

import tkinter as tk
from tkinter import messagebox, ttk, simpledialog

import excel_datos
from caja import Caja, StockInsuficiente
from inventario import Inventario
from modelos import FORMAS_PAGO, TIPOS_PRODUCTO


def _coincide_busqueda(nombre: str, texto_busqueda: str) -> bool:
    """True si 'texto_busqueda' aparece dentro de 'nombre' (sin importar mayúsculas)."""
    return texto_busqueda.strip().lower() in nombre.lower()


def _formato_cantidad(tipo: str, cantidad: float) -> str:
    """Muestra la cantidad como entero (unidades) o con 2 decimales + 'kg' (peso)."""
    if tipo == "Unidad":
        return str(int(cantidad))
    return f"{cantidad:.2f} kg"


class VentanaPrincipal(tk.Tk):
    """Ventana principal de la aplicación para gestión del kiosko."""

    def __init__(self, inventario: Inventario, caja: Caja):
        """Inicializa la ventana y sus componentes."""
        super().__init__()
        self.inventario = inventario
        self.caja = caja

        # Productos que cumplen el filtro de categoría/buscador de arriba
        # (el "pool" completo del que se arma el autocompletado).
        self._productos_disponibles = []
        # Subconjunto de ese pool que está mostrando el desplegable en
        # este momento, según lo que el usuario va escribiendo. Se usa
        # para saber a qué producto corresponde la opción elegida.
        self._productos_visibles_combo = []

        self.title("Kiosko")
        self.geometry("1600x768")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        tab_productos = tk.Frame(notebook)
        tab_ventas = tk.Frame(notebook)
        notebook.add(tab_productos, text="Productos")
        notebook.add(tab_ventas, text="Ventas")

        notebook.bind("<<NotebookTabChanged>>", self._on_cambio_pestania)

        self._crear_tab_productos(tab_productos)
        self._crear_tab_ventas(tab_ventas)
        self._crear_boton_guardar()

        self._refrescar_categorias_en_combos()

        self.protocol("WM_DELETE_WINDOW", self._on_cerrar_ventana)

    def refrescar_todo(self):
        """Actualiza tablas, combos y categorías. Se usa después de cargar el Excel."""
        self._refrescar_categorias_en_combos()
        self._refrescar_tabla_productos()
        self._refrescar_combo_productos()
        self._refrescar_tabla_ventas()

    # ==================================================================
    # GUARDADO EN EXCEL
    # ==================================================================
    def _crear_boton_guardar(self):
        boton = tk.Button(
            self,
            text=f"💾  GUARDAR EN EXCEL  ({excel_datos.NOMBRE_ARCHIVO})",
            command=self._on_guardar_excel,
            font=("", 13, "bold"),
            bg="#2e7d32",
            fg="white",
            activebackground="#256428",
            activeforeground="white",
            height=2,
        )
        boton.pack(side="bottom", fill="x", padx=10, pady=10)

    def _on_guardar_excel(self):
        excel_datos.guardar_datos(self.inventario, self.caja)
        messagebox.showinfo(
            "Guardado", f"Los datos se guardaron en '{excel_datos.NOMBRE_ARCHIVO}'."
        )

    def _on_cerrar_ventana(self):
        respuesta = messagebox.askyesnocancel(
            "Salir", "¿Querés guardar los datos en el Excel antes de salir?"
        )
        if respuesta is None:
            return
        if respuesta:
            excel_datos.guardar_datos(self.inventario, self.caja)
        self.destroy()

    # ==================================================================
    # CATEGORÍAS (compartidas por ambas pestañas)
    # ==================================================================
    def _refrescar_categorias_en_combos(self):
        """Actualiza las categorías disponibles en los combos de filtro y del formulario."""
        categorias = self.inventario.obtener_categorias()
        valores_filtro = ["Todas"] + categorias

        for combo in (self.combo_filtro_categoria_productos, self.combo_filtro_categoria_ventas):
            actual = combo.get()
            combo["values"] = valores_filtro
            combo.set(actual if actual in valores_filtro else "Todas")

        self.combo_categoria["values"] = categorias

    def _productos_filtrados(self, texto_busqueda: str, categoria: str):
        """Devuelve los productos que coinciden con el buscador y la categoría elegida."""
        productos = self.inventario.obtener_todos()
        if texto_busqueda:
            productos = [p for p in productos if _coincide_busqueda(p.nombre, texto_busqueda)]
        if categoria and categoria != "Todas":
            productos = [p for p in productos if p.categoria == categoria]
        return productos

    def _ventas_filtradas(self, texto_busqueda: str, categoria: str):
        """Devuelve las ventas del historial que coinciden con el buscador y la categoría."""
        ventas = self.caja.obtener_ventas()
        if texto_busqueda:
            ventas = [v for v in ventas if _coincide_busqueda(v.nombre, texto_busqueda)]
        if categoria and categoria != "Todas":
            ventas = [v for v in ventas if v.categoria == categoria]
        return ventas

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

        tk.Label(frame, text="Categoría:").grid(row=2, column=0, sticky="w")
        self.combo_categoria = ttk.Combobox(frame, width=27)
        self.combo_categoria.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(frame, text="Tipo:").grid(row=3, column=0, sticky="w")
        self.combo_tipo = ttk.Combobox(
            frame, width=27, state="readonly", values=TIPOS_PRODUCTO
        )
        self.combo_tipo.set(TIPOS_PRODUCTO[0])
        self.combo_tipo.grid(row=3, column=1, padx=5, pady=5)
        self.combo_tipo.bind("<<ComboboxSelected>>", self._on_cambio_tipo)

        tk.Label(frame, text="Precio de venta:").grid(row=4, column=0, sticky="w")
        self.entry_precio = tk.Entry(frame, width=30)
        self.entry_precio.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(frame, text="Costo:").grid(row=5, column=0, sticky="w")
        self.entry_costo = tk.Entry(frame, width=30)
        self.entry_costo.grid(row=5, column=1, padx=5, pady=5)

        tk.Label(frame, text="Stock:").grid(row=6, column=0, sticky="w")
        frame_stock = tk.Frame(frame)
        frame_stock.grid(row=6, column=1, sticky="w")
        self.entry_stock = tk.Entry(frame_stock, width=20)
        self.entry_stock.pack(side="left")
        self.label_ayuda_stock = tk.Label(frame_stock, text="(unidades, número entero)", fg="gray30")
        self.label_ayuda_stock.pack(side="left", padx=5)

        self.boton_guardar = tk.Button(
            frame, text="Agregar producto", command=self._on_guardar_producto
        )
        self.boton_guardar.grid(row=7, column=0, pady=10)

        self.boton_nuevo = tk.Button(
            frame, text="Nuevo producto", command=self._on_nuevo_producto
        )
        self.boton_nuevo.grid(row=7, column=1, pady=10)

        self.boton_eliminar = tk.Button(
            frame,
            text="Eliminar producto",
            command=self._on_eliminar_producto,
            bg="#c62828",
            fg="white",
            activebackground="#8e1b1b",
            activeforeground="white",
        )
        self.boton_eliminar.grid(row=8, column=0, columnspan=2, pady=(0, 10))

        tk.Label(
            contenedor,
            text="Tip: hacé clic en un producto de la tabla para editarlo "
                 "(por ejemplo, para reponer stock).",
            fg="gray30",
        ).pack(anchor="w", padx=10)

        # --- Buscador y filtro por categoría ---
        frame_filtros = tk.Frame(contenedor, padx=10)
        frame_filtros.pack(fill="x", pady=(5, 0))

        tk.Label(frame_filtros, text="Buscar:").pack(side="left")
        self.entry_buscar_productos = tk.Entry(frame_filtros, width=22)
        self.entry_buscar_productos.pack(side="left", padx=5)
        self.entry_buscar_productos.bind("<KeyRelease>", lambda e: self._refrescar_tabla_productos())

        tk.Label(frame_filtros, text="Categoría:").pack(side="left", padx=(15, 0))
        self.combo_filtro_categoria_productos = ttk.Combobox(frame_filtros, width=18, state="readonly")
        self.combo_filtro_categoria_productos.pack(side="left", padx=5)
        self.combo_filtro_categoria_productos.bind(
            "<<ComboboxSelected>>", lambda e: self._refrescar_tabla_productos()
        )

        columnas = ("codigo", "nombre", "categoria", "tipo", "precio", "costo", "stock")
        self.tabla_productos = ttk.Treeview(contenedor, columns=columnas, show="headings")
        self.tabla_productos.heading("codigo", text="Código")
        self.tabla_productos.heading("nombre", text="Producto")
        self.tabla_productos.heading("categoria", text="Categoría")
        self.tabla_productos.heading("tipo", text="Tipo")
        self.tabla_productos.heading("precio", text="Precio")
        self.tabla_productos.heading("costo", text="Costo")
        self.tabla_productos.heading("stock", text="Stock")
        self.tabla_productos.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabla_productos.bind("<<TreeviewSelect>>", self._on_seleccionar_producto)

    def _on_cambio_tipo(self, event):
        """Actualiza el texto de ayuda según se eligió 'Unidad' o 'Peso (Kg)'."""
        if self.combo_tipo.get() == "Unidad":
            self.label_ayuda_stock.config(text="(unidades, número entero)")
        else:
            self.label_ayuda_stock.config(text="(en kg, podés usar decimales, ej: 2.5)")

    def _on_guardar_producto(self):
        """
        Guarda el producto del formulario. Como 'agregar_producto' del
        inventario sobreescribe si el código ya existe, este mismo método
        sirve tanto para CREAR un producto nuevo como para ACTUALIZAR uno
        existente (por ejemplo, para reponer stock).
        """
        codigo_texto = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get().strip()
        categoria = self.combo_categoria.get().strip()
        tipo = self.combo_tipo.get().strip()
        precio_texto = self.entry_precio.get().strip()
        costo_texto = self.entry_costo.get().strip()
        stock_texto = self.entry_stock.get().strip()

        if not all([codigo_texto, nombre, categoria, tipo, precio_texto, costo_texto, stock_texto]):
            messagebox.showwarning(
                "Faltan datos",
                "Completá código, nombre, categoría, tipo, precio, costo y stock.",
            )
            return

        try:
            codigo = int(codigo_texto)
            precio = float(precio_texto)
            costo = float(costo_texto)
        except ValueError:
            messagebox.showerror("Error", "Código debe ser entero; precio y costo, números.")
            return

        try:
            if tipo == "Unidad":
                stock = float(int(stock_texto))
            else:
                stock = float(stock_texto)
        except ValueError:
            mensaje = (
                "El stock debe ser un número entero (es un producto por unidad)."
                if tipo == "Unidad"
                else "El stock debe ser un número, puede tener decimales (ej: 2.5)."
            )
            messagebox.showerror("Error", mensaje)
            return

        self.inventario.agregar_producto(codigo, nombre, categoria, tipo, precio, costo, stock)
        self._refrescar_categorias_en_combos()
        self._refrescar_tabla_productos()
        self._refrescar_combo_productos()
        self._on_nuevo_producto()

    def _on_seleccionar_producto(self, event):
        """
        Se dispara al hacer clic en una fila de la tabla de productos.
        Precarga sus datos en el formulario para editarlos rápido.
        """
        seleccion = self.tabla_productos.selection()
        if not seleccion:
            return

        valores = self.tabla_productos.item(seleccion[0], "values")
        codigo = int(valores[0])
        producto = self.inventario.obtener_producto_por_codigo(codigo)
        if producto is None:
            return

        self.entry_codigo.config(state="normal")
        self.entry_codigo.delete(0, tk.END)
        self.entry_codigo.insert(0, producto.codigo)
        self.entry_codigo.config(state="disabled")

        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, producto.nombre)

        self.combo_categoria.set(producto.categoria)
        self.combo_tipo.set(producto.tipo)
        self._on_cambio_tipo(None)

        self.entry_precio.delete(0, tk.END)
        self.entry_precio.insert(0, producto.precio)

        self.entry_costo.delete(0, tk.END)
        self.entry_costo.insert(0, producto.costo)

        self.entry_stock.delete(0, tk.END)
        if producto.tipo == "Unidad":
            self.entry_stock.insert(0, str(int(producto.stock)))
        else:
            self.entry_stock.insert(0, str(producto.stock))

        self.boton_guardar.config(text="Actualizar producto")

    def _on_eliminar_producto(self):
        """Elimina el producto cuyo código está en el formulario, con confirmación."""
        codigo_texto = self.entry_codigo.get().strip()
        if not codigo_texto:
            messagebox.showwarning(
                "Falta el código", "Seleccioná un producto de la tabla o ingresá su código."
            )
            return

        try:
            codigo = int(codigo_texto)
        except ValueError:
            messagebox.showerror("Error", "El código debe ser un número entero.")
            return

        if not self.inventario.existe(codigo):
            messagebox.showwarning("No encontrado", f"No existe ningún producto con código {codigo}.")
            return

        producto = self.inventario.obtener_producto_por_codigo(codigo)
        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Seguro que querés eliminar '{producto.nombre}' (código {codigo})?\n\n"
            "Esto solo borra el producto del inventario; las ventas ya "
            "registradas de ese producto NO se pierden.",
        )
        if not confirmar:
            return

        self.inventario.eliminar_producto(codigo)
        self._refrescar_categorias_en_combos()
        self._refrescar_tabla_productos()
        self._refrescar_combo_productos()
        self._on_nuevo_producto()

    def _on_nuevo_producto(self):
        """Limpia el formulario y lo deja listo para cargar un producto nuevo."""
        self.tabla_productos.selection_remove(self.tabla_productos.selection())

        self.entry_codigo.config(state="normal")
        self.entry_codigo.delete(0, tk.END)
        self.entry_nombre.delete(0, tk.END)
        self.combo_categoria.set("")
        self.combo_tipo.set(TIPOS_PRODUCTO[0])
        self._on_cambio_tipo(None)
        self.entry_precio.delete(0, tk.END)
        self.entry_costo.delete(0, tk.END)
        self.entry_stock.delete(0, tk.END)

        self.boton_guardar.config(text="Agregar producto")
        self.entry_codigo.focus()

    def _refrescar_tabla_productos(self):
        for fila in self.tabla_productos.get_children():
            self.tabla_productos.delete(fila)

        texto = self.entry_buscar_productos.get()
        categoria = self.combo_filtro_categoria_productos.get()
        for producto in self._productos_filtrados(texto, categoria):
            self.tabla_productos.insert(
                "", tk.END,
                values=(
                    producto.codigo,
                    producto.nombre,
                    producto.categoria,
                    producto.tipo,
                    f"${producto.precio:.2f}",
                    f"${producto.costo:.2f}",
                    _formato_cantidad(producto.tipo, producto.stock),
                ),
            )

    # ==================================================================
    # PESTAÑA: VENTAS
    # ==================================================================
    def _crear_tab_ventas(self, contenedor):
        frame_filtros = tk.Frame(contenedor, padx=10, pady=10)
        frame_filtros.pack(fill="x")

        tk.Label(frame_filtros, text="Buscar:").pack(side="left")
        self.entry_buscar_ventas = tk.Entry(frame_filtros, width=22)
        self.entry_buscar_ventas.pack(side="left", padx=5)
        self.entry_buscar_ventas.bind("<KeyRelease>", lambda e: self._on_filtro_ventas_cambiado())

        tk.Label(frame_filtros, text="Categoría:").pack(side="left", padx=(15, 0))
        self.combo_filtro_categoria_ventas = ttk.Combobox(frame_filtros, width=18, state="readonly")
        self.combo_filtro_categoria_ventas.pack(side="left", padx=5)
        self.combo_filtro_categoria_ventas.bind(
            "<<ComboboxSelected>>", lambda e: self._on_filtro_ventas_cambiado()
        )
        tk.Label(
            contenedor,
            text="El buscador y la categoría filtran tanto la lista para vender "
                 "como el historial de abajo.",
            fg="gray30",
        ).pack(anchor="w", padx=10)

        frame = tk.Frame(contenedor, padx=10, pady=10)
        frame.pack(fill="x")

        tk.Label(frame, text="Producto:").grid(row=0, column=0, sticky="w")
        self.combo_productos = ttk.Combobox(frame, width=38)
        self.combo_productos.grid(row=0, column=1, padx=5, pady=5)
        self.combo_productos.bind("<KeyRelease>", self._on_escribir_producto)

        tk.Label(frame, text="Cantidad:").grid(row=1, column=0, sticky="w")
        self.entry_cantidad = tk.Entry(frame, width=10)
        self.entry_cantidad.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        tk.Label(frame, text="Forma de pago:").grid(row=2, column=0, sticky="w")
        self.combo_forma_pago = ttk.Combobox(
            frame, width=15, state="readonly", values=FORMAS_PAGO
        )
        self.combo_forma_pago.set(FORMAS_PAGO[0])
        self.combo_forma_pago.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        boton = tk.Button(frame, text="Registrar venta", command=self._on_registrar_venta)
        boton.grid(row=3, column=0, columnspan=2, pady=10)

        columnas = ("codigo", "nombre", "categoria", "cantidad", "precio", "total", "ganancia", "pago")
        self.tabla_ventas = ttk.Treeview(contenedor, columns=columnas, show="headings")
        self.tabla_ventas.heading("codigo", text="Código")
        self.tabla_ventas.heading("nombre", text="Producto")
        self.tabla_ventas.heading("categoria", text="Categoría")
        self.tabla_ventas.heading("cantidad", text="Cant.")
        self.tabla_ventas.heading("precio", text="Precio unit.")
        self.tabla_ventas.heading("total", text="Total")
        self.tabla_ventas.heading("ganancia", text="Ganancia")
        self.tabla_ventas.heading("pago", text="Pago")
        self.tabla_ventas.pack(fill="both", expand=True, padx=10, pady=10)

        self.label_totales = tk.Label(
            contenedor, text="Vendido: $0.00   |   Ganancia: $0.00", font=("", 10, "bold")
        )
        self.label_totales.pack(pady=5)

        # NUEVO: Botón para cerrar período, ubicado abajo de los totales
        self.boton_cerrar_periodo = tk.Button(
            contenedor,
            text="🔄 Cerrar Semana/Mes y Reiniciar Ventas",
            command=self._on_cerrar_periodo,
            bg="#d32f2f",
            fg="white",
            font=("", 10, "bold")
        )
        self.boton_cerrar_periodo.pack(pady=10)

    def _on_cerrar_periodo(self):
        """Pide confirmación y archiva las ventas acumuladas."""
        etiqueta = simpledialog.askstring(
            "Archivar Ventas", 
            "Ingresá un nombre para identificar este período (ej: Semana_1_Agosto o Agosto_2026):"
        )
        if not etiqueta:
            return
        
        confirmar = messagebox.askyesno(
            "Confirmar Reinicio",
            f"Se guardará un resumen en 'kiosko_ventas_{etiqueta}_...xlsx' y se limpiarán las ventas activas.\n\n"
            "El stock de productos NO se modificará.\n¿Deseás continuar?"
        )
        if not confirmar:
            return
        
        archivo_creado = excel_datos.archivar_periodo_y_reiniciar(self.inventario, self.caja, etiqueta)
        self._refrescar_tabla_ventas()
        
        messagebox.showinfo(
            "Período Cerrado", 
            f"Se han reajustado las ventas a $0.00.\nSe generó la planilla de respaldo:\n{archivo_creado}"
        )

    def _on_cambio_pestania(self, event):
        self._refrescar_combo_productos()

    def _on_filtro_ventas_cambiado(self):
        """Se llama cuando cambia el buscador o el filtro de categoría en Ventas."""
        self._refrescar_combo_productos()
        self._refrescar_tabla_ventas()

    def _refrescar_combo_productos(self):
        """
        Recalcula el 'pool' de productos disponibles según el buscador
        y la categoría de arriba, y reinicia el desplegable con todos ellos.
        """
        texto = self.entry_buscar_ventas.get()
        categoria = self.combo_filtro_categoria_ventas.get()
        self._productos_disponibles = self._productos_filtrados(texto, categoria)
        self._actualizar_valores_combo(self._productos_disponibles)

    def _actualizar_valores_combo(self, productos):
        """Carga 'productos' como las opciones visibles del combobox de venta."""
        self._productos_visibles_combo = productos
        self.combo_productos["values"] = [
            f"{p.codigo} - {p.nombre} (stock: {_formato_cantidad(p.tipo, p.stock)})"
            for p in productos
        ]

    def _on_escribir_producto(self, event):
        """
        Se dispara con cada tecla en el campo Producto. Filtra las opciones
        del desplegable según lo que se va escribiendo, como un autocompletado,
        pero sin interrumpir ni sobrescribir la escritura del usuario.
        """
        # Ignoramos teclas de navegación para no interferir cuando el usuario las usa
        if event.keysym in ("Up", "Down", "Return", "Escape", "Tab", "Left", "Right"):
            return

        # 1. Guardamos el texto exacto que se está escribiendo y la posición del cursor
        texto_escrito = self.combo_productos.get()
        posicion_cursor = self.combo_productos.index(tk.INSERT)

        # 2. Filtramos la lista de productos
        if texto_escrito:
            coincidencias = [
                p for p in self._productos_disponibles
                if _coincide_busqueda(p.nombre, texto_escrito)
            ]
        else:
            coincidencias = self._productos_disponibles

        # 3. Actualizamos los valores internos del combobox
        self._actualizar_valores_combo(coincidencias)

        # 4. Restauramos el texto y el cursor (evita que el combobox borre lo que escribiste)
        self.combo_productos.set(texto_escrito)
        self.combo_productos.icursor(posicion_cursor)

        # Eliminamos la línea event_generate("<Down>") que causaba la superposición.
        # Ahora filtra silenciosamente. Para ver la lista filtrada, el usuario 
        # solo presiona la tecla "Flecha Abajo" cuando termine de escribir.

    def _on_registrar_venta(self):
        indice = self.combo_productos.current()
        if indice < 0:
            messagebox.showwarning("Falta el producto", "Elegí un producto de la lista.")
            return

        producto = self._productos_visibles_combo[indice]
        cantidad_texto = self.entry_cantidad.get().strip()
        if not cantidad_texto:
            messagebox.showwarning("Falta la cantidad", "Ingresá la cantidad vendida.")
            return

        try:
            if producto.tipo == "Unidad":
                cantidad = float(int(cantidad_texto))
            else:
                cantidad = float(cantidad_texto)
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            mensaje = (
                "La cantidad debe ser un número entero mayor a 0."
                if producto.tipo == "Unidad"
                else "La cantidad debe ser un número mayor a 0 (podés usar decimales, ej: 0.5)."
            )
            messagebox.showerror("Error", mensaje)
            return

        forma_pago = self.combo_forma_pago.get() or FORMAS_PAGO[0]

        try:
            self.caja.registrar_venta(producto.codigo, cantidad, forma_pago)
        except StockInsuficiente as error:
            messagebox.showerror("Stock insuficiente", str(error))
            return

        self._refrescar_tabla_ventas()
        self._refrescar_tabla_productos()
        self._refrescar_combo_productos()
        self.combo_productos.set("")
        self.entry_cantidad.delete(0, tk.END)

    def _refrescar_tabla_ventas(self):
        for fila in self.tabla_ventas.get_children():
            self.tabla_ventas.delete(fila)

        texto = self.entry_buscar_ventas.get()
        categoria = self.combo_filtro_categoria_ventas.get()
        for venta in self._ventas_filtradas(texto, categoria):
            self.tabla_ventas.insert(
                "", tk.END,
                values=(
                    venta.codigo,
                    venta.nombre,
                    venta.categoria,
                    _formato_cantidad(venta.tipo, venta.cantidad),
                    f"${venta.precio_unitario:.2f}",
                    f"${venta.total:.2f}",
                    f"${venta.ganancia:.2f}",
                    venta.forma_pago,
                ),
            )

        # Los totales siempre muestran el día completo, sin importar el filtro,
        # para que reflejen el cierre de caja real.
        self.label_totales.config(
            text=(
                f"Vendido (total del día): ${self.caja.total_vendido():.2f}   |   "
                f"Ganancia (total del día): ${self.caja.total_ganancia():.2f}"
            )
        )