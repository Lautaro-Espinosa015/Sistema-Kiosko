"""Módulo que coordina las ventas del día: valida stock, lo descuenta,
guarda cada venta (con su forma de pago) y calcula los totales."""

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

    def registrar_venta(self, codigo: int, cantidad: float, forma_pago: str) -> Venta:
        """
        Registra una venta:
        1) busca el producto por código,
        2) valida que haya stock suficiente,
        3) descuenta el stock,
        4) guarda la venta (con su forma de pago) y la devuelve.
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
            categoria=producto.categoria,
            tipo=producto.tipo,
            cantidad=cantidad,
            precio_unitario=producto.precio,
            costo_unitario=producto.costo,
            forma_pago=forma_pago,
        )
        self._ventas.append(venta)
        return venta

    def agregar_venta_existente(self, venta: Venta) -> None:
        """
        Agrega una venta ya validada anteriormente (por ejemplo, al cargar
        el historial del día desde el Excel), sin volver a descontar stock.
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
    # En caja.py, dentro de class Caja:

    def limpiar_ventas(self) -> None:
        """Vacía la lista de ventas de la caja activa sin tocar el inventario."""
        self._ventas.clear()

    def total_por_forma_pago(self) -> dict[str, float]:
        """Total vendido, agrupado por forma de pago (ej: Efectivo, Transferencia)."""
        totales: dict[str, float] = {}
        for venta in self._ventas:
            totales[venta.forma_pago] = totales.get(venta.forma_pago, 0.0) + venta.total
        return totales
    