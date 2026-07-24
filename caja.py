"""Módulo que coordina las ventas del día: valida stock, lo descuenta,
guarda cada venta y calcula los totales (vendido y ganancia)."""

from inventario import Inventario
from modelos import Venta


class StockInsuficiente(Exception):
    """Se lanza cuando se intenta vender más cantidad de la que hay en stock."""
    pass


class Caja:
    """
    Representa la caja del kiosko durante el día.
    No guarda productos por su cuenta: usa el Inventario que le pasan.
    """

    def __init__(self, inventario: Inventario):
        self.inventario = inventario
        self._ventas: list[Venta] = []

    def registrar_venta(self, codigo: int, cantidad: int) -> Venta:
        """
        Registra una venta:
        1) busca el producto por código,
        2) valida que haya stock suficiente,
        3) descuenta el stock,
        4) guarda la venta y la devuelve.
        """
        if not self.inventario.existe(codigo):
            raise KeyError(f"No existe ningún producto con código {codigo}.")

        producto = self.inventario.obtener_producto_por_codigo(codigo)

        if producto.stock < cantidad:
            raise StockInsuficiente(
                f"Stock insuficiente de '{producto.nombre}'. "
                f"Disponible: {producto.stock}, pedido: {cantidad}."
            )

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

    def agregar_venta_existente(self, venta: Venta) -> None:
        """
        Agrega una venta que ya había sido validada anteriormente
        (por ejemplo, al cargar el historial del día desde el Excel).
        A diferencia de 'registrar_venta', NO vuelve a descontar stock,
        porque el stock guardado en el Excel ya refleja esa venta.
        """
        self._ventas.append(venta)

    def obtener_ventas(self) -> list[Venta]:
        """Devuelve todas las ventas registradas en el día."""
        return list(self._ventas)

    def total_vendido(self) -> float:
        """Suma de todo lo facturado en el día."""
        return sum(venta.total for venta in self._ventas)

    def total_ganancia(self) -> float:
        """Suma de toda la ganancia del día (ventas - costos)."""
        return sum(venta.ganancia for venta in self._ventas)

    def cantidad_operaciones(self) -> int:
        """Cuántas ventas se registraron en el día."""
        return len(self._ventas)