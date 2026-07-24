"""
Módulo que se encarga de TODO lo relacionado al archivo Excel:
leerlo al iniciar la app y escribirlo al guardar.

Ni Inventario ni Caja saben que el Excel existe: este módulo
las "traduce" a filas de una planilla y viceversa. Si el día de
mañana quisieran guardar en otro formato (por ejemplo, una base
de datos), alcanzaría con reemplazar este archivo.
"""

import os

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font

from caja import Caja
from inventario import Inventario
from modelos import Venta

NOMBRE_ARCHIVO = "kiosko_datos.xlsx"

COLUMNAS_PRODUCTOS = ["Código", "Nombre", "Precio", "Costo", "Stock"]
COLUMNAS_VENTAS = [
    "Código", "Nombre", "Cantidad", "Precio unitario",
    "Costo unitario", "Total", "Ganancia",
]
COLUMNAS_RESUMEN = ["Concepto", "Valor"]


def cargar_datos(inventario: Inventario, caja: Caja) -> bool:
    """
    Carga productos y ventas del Excel hacia el inventario y la caja.

    Devuelve True si el archivo ya existía, o False si no existía
    y se creó uno nuevo (vacío) en su lugar.
    """
    if not os.path.exists(NOMBRE_ARCHIVO):
        _crear_archivo_vacio()
        return False

    libro = load_workbook(NOMBRE_ARCHIVO, data_only=True)

    if "Productos" in libro.sheetnames:
        hoja = libro["Productos"]
        for fila in hoja.iter_rows(min_row=2, values_only=True):
            if fila[0] is None:
                continue
            codigo, nombre, precio, costo, stock = fila
            inventario.agregar_producto(
                int(codigo), str(nombre), float(precio), float(costo), int(stock)
            )

    if "Ventas" in libro.sheetnames:
        hoja = libro["Ventas"]
        for fila in hoja.iter_rows(min_row=2, values_only=True):
            if fila[0] is None:
                continue
            codigo, nombre, cantidad, precio_unitario, costo_unitario = fila[:5]
            venta = Venta(
                codigo=int(codigo),
                nombre=str(nombre),
                cantidad=int(cantidad),
                precio_unitario=float(precio_unitario),
                costo_unitario=float(costo_unitario),
            )
            caja.agregar_venta_existente(venta)

    return True


def guardar_datos(inventario: Inventario, caja: Caja) -> None:
    """Guarda el estado actual (productos y ventas) en el Excel, pisando lo anterior."""
    libro = Workbook()

    hoja_productos = libro.active
    hoja_productos.title = "Productos"
    _escribir_encabezado(hoja_productos, COLUMNAS_PRODUCTOS)
    for producto in inventario.obtener_todos():
        hoja_productos.append(
            [producto.codigo, producto.nombre, producto.precio, producto.costo, producto.stock]
        )

    hoja_ventas = libro.create_sheet("Ventas")
    _escribir_encabezado(hoja_ventas, COLUMNAS_VENTAS)
    for venta in caja.obtener_ventas():
        hoja_ventas.append([
            venta.codigo, venta.nombre, venta.cantidad,
            venta.precio_unitario, venta.costo_unitario,
            venta.total, venta.ganancia,
        ])

    hoja_resumen = libro.create_sheet("Resumen")
    _escribir_encabezado(hoja_resumen, COLUMNAS_RESUMEN)
    hoja_resumen.append(["Cantidad de ventas", caja.cantidad_operaciones()])
    hoja_resumen.append(["Total vendido", caja.total_vendido()])
    hoja_resumen.append(["Ganancia total", caja.total_ganancia()])

    for hoja in (hoja_productos, hoja_ventas, hoja_resumen):
        _autoajustar_columnas(hoja)

    libro.save(NOMBRE_ARCHIVO)


def _crear_archivo_vacio() -> None:
    """Crea kiosko_datos.xlsx con las hojas y encabezados, sin filas de datos."""
    libro = Workbook()

    hoja_productos = libro.active
    hoja_productos.title = "Productos"
    _escribir_encabezado(hoja_productos, COLUMNAS_PRODUCTOS)

    hoja_ventas = libro.create_sheet("Ventas")
    _escribir_encabezado(hoja_ventas, COLUMNAS_VENTAS)

    hoja_resumen = libro.create_sheet("Resumen")
    _escribir_encabezado(hoja_resumen, COLUMNAS_RESUMEN)

    libro.save(NOMBRE_ARCHIVO)


def _escribir_encabezado(hoja, columnas: list[str]) -> None:
    for indice, titulo in enumerate(columnas, start=1):
        celda = hoja.cell(row=1, column=indice, value=titulo)
        celda.font = Font(bold=True)


def _autoajustar_columnas(hoja) -> None:
    """Ensancha cada columna según el contenido más largo, para que se lea bien."""
    for columna in hoja.columns:
        letra = columna[0].column_letter
        largo_max = max((len(str(c.value)) for c in columna if c.value is not None), default=8)
        hoja.column_dimensions[letra].width = largo_max + 2