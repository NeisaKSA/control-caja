from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout
)

class DialogEmpresa(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Nueva Empresa")
        
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Nombre empresa"))
        self.txt_nombre = QLineEdit()
        layout.addWidget(self.txt_nombre)
        
        layout.addWidget(QLabel("Saldo inicial"))
        self.txt_saldo = QLineEdit()
        self.txt_saldo.setPlaceholderText("0.00")
        layout.addWidget(self.txt_saldo)
        
        botones = QHBoxLayout()
        btn_crear = QPushButton("Crear")
        btn_cancelar = QPushButton("Cancelar")
        
        botones.addWidget(btn_crear)
        botones.addWidget(btn_cancelar)
        
        layout.addLayout(botones)

        self.setLayout(layout)

        btn_crear.clicked.connect(self.accept)
        btn_cancelar.clicked.connect(self.reject)