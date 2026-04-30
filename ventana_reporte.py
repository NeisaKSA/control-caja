from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel, QHBoxLayout
)

class VentanaReporte(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Observaciones Finales")
        
        layout = QVBoxLayout()
        
        label = QLabel("Observaciones Finales")
        layout.addWidget(label)
        
        self.texto = QTextEdit()
        layout.addWidget(self.texto)
        
        botones = QHBoxLayout()
        
        btn_cancelar = QPushButton("Cancelar")
        btn_guardar = QPushButton("Guardar")
        
        botones.addWidget(btn_cancelar)
        botones.addWidget(btn_guardar)
        
        layout.addLayout(botones)
        
        self.setLayout(layout)
        
        btn_cancelar.clicked.connect(self.reject)
        btn_guardar.clicked.connect(self.accept)

    def obtener_observaciones(self):
        return self.texto.toPlainText()