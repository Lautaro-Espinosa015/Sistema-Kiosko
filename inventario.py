"""Módulo que contiene la lógica de gestión del inventario."""

from modelos import Producto


class Inventario:
    """Clase para gestionar el conjunto de productos."""

    def __init__(self):
        """Inicializa el inventario indexado por código."""
        self.productos: dict[int, Producto] = {}

    def agregar_producto(
        self,
        codigo: int,
        nombre: str,
        categoria: str,
        tipo: str,
        precio: float,
        costo: float,
        stock: float,
    ) -> None:
        """Agrega un nuevo producto (o actualiza uno existente con el mismo código)."""
        self.productos[codigo] = Producto(
            codigo=codigo,
            nombre=nombre,
            categoria=categoria,
            tipo=tipo,
            precio=precio,
            costo=costo,
            stock=stock,
        )

    def existe(self, codigo: int) -> bool:
        """Verifica si un producto existe por su código."""
        return codigo in self.productos

    def obtener_producto_por_codigo(self, codigo: int) -> Producto | None:
        """Obtiene un producto por su código."""
        return self.productos.get(codigo)

    def eliminar_producto(self, codigo: int) -> None:
        """Elimina un producto del inventario por su código, si existe."""
        if codigo in self.productos:
            del self.productos[codigo]

    def obtener_todos(self) -> list[Producto]:
        """Devuelve todos los productos ordenados por nombre."""
        return sorted(self.productos.values(), key=lambda p: p.nombre)

    def obtener_categorias(self) -> list[str]:
        """Devuelve las categorías cargadas (sin repetir), ordenadas alfabéticamente."""
        categorias = {p.categoria for p in self.productos.values() if p.categoria}
        return sorted(categorias)