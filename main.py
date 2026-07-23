from interfaz import VentanaPrincipal
from inventario import Inventario
from caja import Caja


def main():
    """Inicializa la aplicación y la interfaz gráfica."""
    inventario = Inventario()
    caja = Caja(inventario)
    app = VentanaPrincipal(inventario, caja)
    app.mainloop()


if __name__ == "__main__":
    main()