"""Punto de entrada principal de la aplicación."""

from interfaz import VentanaPrincipal
from inventario import Inventario


def main():
    """Inicializa la aplicación y la interfaz gráfica."""
    inventario = Inventario()
    app = VentanaPrincipal(inventario)
    app.mainloop()


if __name__ == "__main__":
    main()