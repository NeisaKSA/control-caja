import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QAbstractItemView
)
from PyQt5.QtCore import Qt

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Excel con PyQt5")
        self.resize(800, 400)

        layout = QVBoxLayout(self)
        self.tabla = QTableWidget(5, 4)
        self.tabla.setHorizontalHeaderLabels(["Concepto", "Ingreso", "Egreso", "Saldo"])

        # Solo permitir edición con doble clic
        self.tabla.setEditTriggers(QAbstractItemView.DoubleClicked)

        for row in range(5):
            concepto = QTableWidgetItem(f"Concepto {row+1}")
            concepto.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.tabla.setItem(row, 0, concepto)

            ingreso = QTableWidgetItem("0.00")
            ingreso.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            self.tabla.setItem(row, 1, ingreso)

            egreso = QTableWidgetItem("0.00")
            egreso.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            self.tabla.setItem(row, 2, egreso)

            saldo = QTableWidgetItem("0.00")
            saldo.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.tabla.setItem(row, 3, saldo)

        self.tabla.itemChanged.connect(self.recalcular_saldo)
        layout.addWidget(self.tabla)

    def recalcular_saldo(self, item):
        if item.column() in (1, 2):
            try:
                ingreso = float(self.tabla.item(item.row(), 1).text())
                egreso = float(self.tabla.item(item.row(), 2).text())
                if item.row() > 0:
                    saldo_anterior = float(self.tabla.item(item.row()-1, 3).text())
                else:
                    saldo_anterior = 0.0
                saldo = saldo_anterior + ingreso - egreso
                self.tabla.item(item.row(), 3).setText(f"{saldo:.2f}")
            except ValueError:
                pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MyApp()
    win.show()
    sys.exit(app.exec_())