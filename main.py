import sys
from PySide6.QtWidgets import (
    QApplication
)
from ventana_principal import VentanaPrincipal

# =====================
# MAIN
# =====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())
    