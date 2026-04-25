from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton, QHeaderView, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtGui import QTextDocument
from datetime import datetime
import os

class VistaReporte(QDialog):
    def __init__(self, datos, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Reporte Final")
        self.resize(800, 600)
        
        layout = QVBoxLayout()
        
        titulo_resumen = QLabel("RESUMEN FINANCIERO")
        titulo_resumen.setStyleSheet("""
        font-size: 14px;
        font-weight: bold;
        margin-top: 10px;
        """)
        layout.addWidget(titulo_resumen)
        
        titulo_resumen.setAlignment(Qt.AlignCenter)
        
        linea = QLabel("────────────────────────")
        layout.addWidget(linea)
        
        # empresa
        lbl_empresa = QLabel(f"Empresa: {datos['empresa']}")
        layout.addWidget(lbl_empresa)
        
        # resumen
        resumen = datos["resumen"]
        
        lbl_resumen = QLabel(
            f"Saldo inicial: {resumen['saldo_inicial']}\n"
            f"{resumen['ingresos']}\n"
            f"{resumen['egresos']}\n"
            f"{resumen['saldo_total']}"
        )
        
        lbl_resumen.setStyleSheet("""
        font-family: Consolas;
        font-size: 12px;
        """)
        
        lbl_resumen.setWordWrap(True)
        lbl_resumen.setAlignment(Qt.AlignLeft)
        
        layout.addWidget(lbl_resumen)
        
        # Observaciones
        lbl_obs = QLabel("Observaciones:")
        layout.addWidget(lbl_obs)

        txt_obs = QTextEdit()
        txt_obs.setPlainText(datos["observaciones"])
        txt_obs.setReadOnly(True)
        txt_obs.setFixedHeight(50)

        layout.addWidget(txt_obs)

        self.setLayout(layout)
        
        # tabla
        tabla = QTableWidget()
        tabla.setRowCount(len(datos["tabla"]))
        tabla.setColumnCount(len(datos["tabla"][0]) if datos["tabla"] else 0)
        
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        tabla.setSelectionMode(QTableWidget.NoSelection)
        tabla.verticalHeader().setVisible(False)
        
        tabla.setHorizontalHeaderLabels([
            "Fecha", "Concepto", "Ingreso", "Egreso", "Saldo"
        ])
        
        for i, fila in enumerate(datos["tabla"]):
            for j, valor in enumerate(fila):
                tabla.setItem(i, j, QTableWidgetItem(valor))
        layout.addWidget(tabla)
        
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
        
        layout.addLayout(botones)
        
        btn_pdf.clicked.connect(self.exportar_pdf)
        
        self.setLayout(layout)
        
        self.datos = datos 
        
        btn_cerrar.clicked.connect(self.close)
        
    def exportar_pdf(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF", "", "PDF Files (*.pdf)"
        )
        
        if not ruta.endswith(".pdf"):
            ruta += ".pdf"
        
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(ruta)
        
        # contenido em texto
        contenido = self.generar_contenido()
        
        doc = QTextDocument()
        doc.setHtml(contenido)
        doc.print_(printer)
        
    def generar_contenido(self):
        with open("templates/reporte.html", "r", encoding="utf-8") as f:
            html = f.read()
            
        fecha = datetime.now().strftime("%d/%m/%Y")
        numero = self.generar_nro_reporte()
        resumen = self.datos["resumen"]
        
        filas_html = ""
        for fila in self.datos["tabla"]:
            filas_html += "<tr>"
            for valor in fila:
                filas_html += f"<td>{valor}</td>"
            # filas_html += "<tr>"

        # reemplazar los datos
        html = html.replace("{{empresa}}", self.datos["empresa"])
        html = html.replace("{{fecha}}", fecha)
        html = html.replace("{{numero}}", numero)
        html = html.replace("{{saldo_inicial}}", resumen["saldo_inicial"])
        html = html.replace("{{ingresos}}", resumen["ingresos"])
        html = html.replace("{{egresos}}", resumen["egresos"])
        html = html.replace("{{saldo_total}}", resumen["saldo_total"])
        html = html.replace("{{observaciones}}", self.datos["observaciones"])
        html = html.replace("{{filas}}", filas_html)
        
        return html
    
    def generar_nro_reporte(self):
        ruta = "datos/reportes_contador.txt"
        
        if not os.path.exists(ruta):
            with open(ruta, "w") as f:
                f.write("1")
            return "0001"
        
        with open(ruta, "r+") as f:
            numero = int(f.read())
            f.seek(0)
            f.write(str(numero + 1))
        return str(numero).zfill(4)