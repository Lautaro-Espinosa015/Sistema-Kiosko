"""Módulo que define los datos del Producto y la Venta."""

from dataclasses import dataclass

# Tipos de producto posibles: por unidad (ej: alfajor, gaseosa)
# o por peso (ej: verdura, pan, fiambre). Define si el stock/cantidad
# se maneja como número entero o con decimales (kg).
TIPOS_PRODUCTO = ("Unidad", "Peso (Kg)")

# Formas de pago que acepta el kiosko al registrar una venta.
FORMAS_PAGO = ("Efectivo", "Transferencia")


@dataclass
class Producto:
    """Representa un producto dentro del sistema."""

    codigo: int
    nombre: str
    categoria: str
    tipo: str       # uno de TIPOS_PRODUCTO
    precio: float   # precio por unidad, o por kg si tipo == "Peso (Kg)"
    costo: float    # costo por unidad, o por kg
    stock: float    # cantidad de unidades, o kilos disponibles


@dataclass
class Venta:
    """Representa una operación de venta realizada."""

    codigo: int
    nombre: str
    categoria: str
    tipo: str        # copiado del producto, para saber si cantidad es entera o en kg
    cantidad: float
    precio_unitario: float
    costo_unitario: float
    forma_pago: str  # uno de FORMAS_PAGO

    @property
    def total(self) -> float:
        """Calcula el total devengado por la venta."""
        return self.precio_unitario * self.cantidad

    @property
    def ganancia(self) -> float:
        """Calcula la ganancia neta (Precio - Costo) * Cantidad."""
        return (self.precio_unitario - self.costo_unitario) * self.cantidad