"""Módulo que contiene la lógica de gestión del inventario."""

from modelos import Producto


class Inventario:
    """Clase para gestionar el conjunto de productos."""

    def __init__(self):
        """Inicializa el inventario con un diccionario vacío de productos."""
        self.productos: dict[str, Producto] = {}

    def agregar_producto(self, nombre: str, precio: float, stock: int) -> None:
        """Agrega un nuevo producto al inventario."""
        self.productos[nombre] = Producto(
            nombre=nombre, precio=precio, stock=stock
        )

    def existe(self, nombre: str) -> bool:
        """Verifica si un producto existe en el inventario."""
        return nombre in self.productos

    def obtener_productos(self, nombre: str) -> Producto:
        """Obtiene un producto por su nombre."""
        return self.productos[nombre]

    def obtener_todos(self) -> list[Producto]:
        """Devuelve una lista con todos los productos ordenados por nombre."""
        return sorted(self.productos.values(), key=lambda p: p.nombre)

    def nombres(self) -> list[str]:
        """Devuelve una lista con los nombres de todos los productos."""
        return list(self.productos.keys())