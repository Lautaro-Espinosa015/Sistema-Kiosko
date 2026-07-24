"""Módulo que define los datos del Producto y la Venta."""

from dataclasses import dataclass


@dataclass
class Producto:
    """Representa un producto dentro del sistema."""

    codigo: int
    nombre: str
    precio: float
    costo: float
    stock: int


@dataclass
class Venta:
    """Representa una operación de venta realizada."""

    codigo: int
    nombre: str
    cantidad: int
    precio_unitario: float
    costo_unitario: float

    @property
    def total(self) -> float:
        """Calcula el total devengado por la venta."""
        return self.precio_unitario * self.cantidad

    @property
    def ganancia(self) -> float:
        """Calcula la ganancia neta (Precio - Costo) * Cantidad."""
        return (self.precio_unitario - self.costo_unitario) * self.cantidad