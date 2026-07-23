"""Módulo para el procesamiento de transacciones y cálculo de caja."""

from inventario import Inventario
from modelos import Venta


class StockInsuficiente(Exception):
    """Excepción para cuando no hay suficiente stock de un producto."""


class Caja:
    """Gestor de ventas y balance financiero."""

    def __init__(self, inventario: Inventario):
        """Inicializa la caja conectada a un inventario."""
        self.inventario = inventario
        self._ventas: list[Venta] = []

    def registrar_venta(self, codigo: int, cantidad: int) -> Venta:
        """Procesa una venta y descuenta el stock correspondiente."""
        # 1. Asignamos el producto devuelto a la variable
        producto = self.inventario.obtener_producto_por_codigo(codigo)

        # 2. Verificamos si existe y si hay stock
        if not producto:
            raise ValueError(f"No existe ningún producto con el código {codigo}.")

        if producto.stock < cantidad:
            raise StockInsuficiente(
                f"Stock insuficiente de '{producto.nombre}'. "
                f"Disponible: {producto.stock}, pedido: {cantidad}."
            )

        # 3. Descontamos stock y registramos la venta
        producto.stock -= cantidad
        venta = Venta(
            codigo=producto.codigo,
            nombre=producto.nombre,
            cantidad=cantidad,
            precio_unitario=producto.precio,
            costo_unitario=producto.costo,
        )
        self._ventas.append(venta)
        return venta

    def obtener_ventas(self) -> list[Venta]:
        """Devuelve el historial de ventas."""
        return list(self._ventas)

    def total_vendido(self) -> float:
        """Suma el dinero total acumulado por ventas."""
        return sum(venta.total for venta in self._ventas)

    def total_ganancia(self) -> float:
        """Suma el dinero neta ganado por ventas."""
        return sum(venta.ganancia for venta in self._ventas)

    def cantidad_operaciones(self) -> int:
        """Devuelve la cantidad total de transacciones hechas."""
        return len(self._ventas)