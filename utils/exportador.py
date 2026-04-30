from PySide6.QtPrintSupport import QPrinter
from PySide6.QtGui import QTextDocument, QFont
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from datetime import datetime
import os

class Exportador:
    @staticmethod
    def generar_html(datos):
        with open("templates/reporte.html", "r", encoding="utf-8") as f:
            html = f.read()
            
        fecha = datetime.now().strftime("%d/%m/%Y")
        numero = Exportador.generar_nro_reporte()
        resumen = datos["resumen"]
        
        filas_html = ""
        for fila in datos["tabla"]:
            filas_html += "<tr>"
            for valor in fila:
                filas_html += f"<td>{valor}</td>"
            filas_html += "</tr>"

        # reemplazar los datos
        html = html.replace("{{empresa}}", datos["empresa"])
        html = html.replace("{{fecha}}", fecha)
        html = html.replace("{{numero}}", numero)
        html = html.replace("{{saldo_inicial}}", resumen["saldo_inicial"])
        html = html.replace("{{ingresos}}", resumen["ingresos"])
        html = html.replace("{{egresos}}", resumen["egresos"])
        html = html.replace("{{saldo_total}}", resumen["saldo_total"])
        html = html.replace("{{observaciones}}", datos["observaciones"])
        html = html.replace("{{filas}}", filas_html)
        
        return html
    
    @staticmethod
    def exportar_pdf(html, ruta):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(ruta)
        
        doc = QTextDocument()
        doc.setDefaultFont(QFont("Arial", 12))
        doc.setHtml(html)

        doc.print_(printer)
    
    @staticmethod
    def generar_excel(datos, ruta):
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte"
        
        fecha = datetime.now().strftime("%d/%m/%Y")
        numero = Exportador.generar_nro_reporte()
        resumen = datos["resumen"]
        
        ws["A1"] = "REPORTE CONTROL DE CAJA"
        ws["A2"] = f"Empresa: {datos['empresa']}"
        ws["E1"] = "Fecha:"
        ws["F1"] = fecha
        ws["E2"] = "N°:"
        ws["F2"] = numero
        
        ws.merge_cells("A1:D1")
        
        ws["A4"] = "Resumen"
        ws["A5"] = "Saldo Inicial"
        ws["B5"] = resumen["saldo_inicial"]
        ws["C5"] = resumen["ingresos"]
        ws["D5"] = resumen["egresos"]
        ws["E5"] = resumen["saldo_total"]
        
        fila_inicio = 12

        headers = ["Fecha", "Concepto", "Ingreso", "Egreso", "Saldo"]

        for col, header in enumerate(headers, start=1):
            ws.cell(row=fila_inicio, column=col, value=header)
            
        for i, fila in enumerate(datos["tabla"], start=fila_inicio + 1):
            for j, valor in enumerate(fila, start=1):
                ws.cell(row=i, column=j, value=valor)
                
        wb.save(ruta)
             
            
    @staticmethod
    def generar_nro_reporte():
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