from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton, QHeaderView, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtGui import QTextDocument

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
        
        if not ruta:
            return
        
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(ruta)
        
        # contenido em texto
        contenido = self.generar_contenido()
        
        doc = QTextDocument()
        doc.setHtml(contenido)
        doc.print(printer)
        
    def generar_contenido(self):
        resumen = self.datos["resumen"]

        html = f"""
        <h1>REPORTE CONTROL DE CAJA</h1>
        <h3>Empresa: {self.datos['empresa']}</h3>

        <hr>

        <h3>Resumen</h3>
        <p>{resumen['saldo_inicial']}<br>
        {resumen['ingresos']}<br>
        {resumen['egresos']}<br>
        {resumen['saldo_total']}</p>

        <h3>Observaciones</h3>
        <p>{self.datos['observaciones']}</p>

        <h3>Movimientos</h3>
        <table border="1" cellspacing="0" cellpadding="4">
            <tr>
                <th>Fecha</th>
                <th>Concepto</th>
                <th>Ingreso</th>
                <th>Egreso</th>
                <th>Saldo</th>
            </tr>
        """

        for fila in self.datos["tabla"]:
            html += "<tr>"
            for valor in fila:
                html += f"<td>{valor}</td>"
            html += "</tr>"

        html += "</table>"

        return html