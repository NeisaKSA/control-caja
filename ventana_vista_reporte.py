from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout

class VistaReporte(QDialog):
    def __init__(self, contenido, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Reporte Final")
        self.resize(700, 500)
        
        layout = QVBoxLayout()
        
        self.texto = QTextEdit()
        self.texto.setReadOnly(True)
        self.texto.setText(contenido)
        
        layout.addWidget(self.texto)
        
        botones = QHBoxLayout()
        
        btn_pdf = QPushButton("Exportar PDF")
        btn_excel = QPushButton("Exportar Excel")
        btn_cerrar = QPushButton("Cerrar")
        
        botones.addWidget(btn_pdf)
        botones.addWidget(btn_excel)
        botones.addWidget(btn_cerrar)
        
        layout.addLayout(botones)
        
        self.setLayout(layout)
        
        btn_cerrar.clicked.connect(self.close)