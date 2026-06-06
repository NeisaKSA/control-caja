from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton, QHeaderView, QFileDialog, QDialog, QVBoxLayout,
    QHBoxLayout, QPushButton,
    QFileDialog, QTextBrowser, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtGui import QTextDocument, QFont, QColor
from datetime import datetime
import os
from utils.exportador import Exportador

class VistaReporte(QDialog):
    def __init__(self, datos, parent=None):
        super().__init__(parent)
        
        with open("styles/vista_reporte.qss", "r") as f:
            self.setStyleSheet(f.read())
        
        self.setWindowTitle("Reporte Final")
        self.resize(800, 600)
        
        layout = QVBoxLayout()
        
        contenedor = QVBoxLayout()
        contenedor.setContentsMargins(40, 30, 40, 30)
        contenedor.setSpacing(15)
        
        titulo_resumen = QLabel("RESUMEN FINANCIERO")
        titulo_resumen.setObjectName("tituloReporte")
        contenedor.addWidget(titulo_resumen)
        
        titulo_resumen.setAlignment(Qt.AlignCenter)
        
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setObjectName("lineaSeparador")
        contenedor.addWidget(linea)
        
        # empresa
        lbl_empresa = QLabel(f"Empresa: {datos['empresa']}")
        lbl_empresa.setObjectName("empresaLabel")
        contenedor.addWidget(lbl_empresa)
        
        # resumen
        resumen = datos["resumen"]
        
        lbl_resumen = QLabel(
            f"Saldo inicial: {resumen['saldo_inicial']}\n"
            f"{resumen['ingresos']}\n"
            f"{resumen['egresos']}\n"
            f"{resumen['saldo_total']}"
        )
        
        lbl_resumen.setWordWrap(True)
        lbl_resumen.setAlignment(Qt.AlignLeft)
        
        # CARD
        card_resumen = QFrame()
        card_resumen.setObjectName("cardResumen")
        
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)
        
        # contenedor.addWidget(lbl_resumen)
        card_layout.addWidget(lbl_empresa)
        card_layout.addWidget(lbl_resumen)
        
        card_resumen.setLayout(card_layout)

        contenedor.addWidget(card_resumen)
        
        # Observaciones
        lbl_obs = QLabel("Observaciones:")
        contenedor.addWidget(lbl_obs)

        txt_obs = QTextEdit()
        txt_obs.setPlainText(datos["observaciones"])
        txt_obs.setReadOnly(True)
        txt_obs.setFixedHeight(50)

        contenedor.addWidget(txt_obs)

        self.setLayout(layout)
        
        # tabla
        tabla_limpia = [
            fila for fila in datos["tabla"]
            if any(str(c).strip() != "" for c in fila)
        ]
        
        datos["tabla"] = tabla_limpia
        
        tabla = QTableWidget()
        tabla.setRowCount(len(tabla_limpia))
        tabla.setColumnCount(len(datos["tabla"][0]) if datos["tabla"] else 0)
        
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        tabla.setSelectionMode(QTableWidget.NoSelection)
        tabla.verticalHeader().setVisible(False)
        
        tabla.setHorizontalHeaderLabels([
            "Fecha", "Concepto", "Ingreso", "Egreso", "Saldo"
        ])
        
        for i, fila in enumerate(tabla_limpia):
            for j, valor in enumerate(fila):
                item = QTableWidgetItem(valor)
                
                if j == 2:
                    item.setBackground(QColor("#e8f5e9"))
                    
                if j == 3:
                    item.setBackground(QColor("#ffebee"))
                
                tabla.setItem(i, j, item)
        contenedor.addWidget(tabla)
        
        header = tabla.horizontalHeader()
        
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        # botones 
        botones = QHBoxLayout()
        
        btn_pdf = QPushButton("Exportar PDF")
        btn_excel = QPushButton("Exportar Excel")
        btn_cerrar = QPushButton("Cerrar")
        
        botones.addWidget(btn_pdf)
        botones.addWidget(btn_excel)
        botones.addWidget(btn_cerrar)
        
        layout.addLayout(contenedor)
        layout.addLayout(botones)
        
        btn_pdf.clicked.connect(self.exportar_pdf)
        btn_excel.clicked.connect(self.exportar_excel)
        
        self.setLayout(layout)
        
        self.datos = datos 
        
        btn_cerrar.clicked.connect(self.close)
        
    def exportar_pdf(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF", "", "PDF Files (*.pdf)"
        )
        
        if not ruta:
            return
        
        if not ruta.endswith(".pdf"):
            ruta += ".pdf"
            
        print("Ruta PDF:", ruta)
        
        html = Exportador.generar_html(self.datos)
        Exportador.exportar_pdf(html, ruta)
        
    def exportar_excel(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar Excel", "", "EXCEL Files (*.xlsx)"
        )
        
        if not ruta:
            return
        
        if not ruta.endswith(".xlsx"):
            ruta += ".xlsx"
        
        print("Ruta EXCEL:", ruta)
        
        Exportador.generar_excel(self.datos, ruta)
        
        