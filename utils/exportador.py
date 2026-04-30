from PySide6.QtPrintSupport import QPrinter
from PySide6.QtGui import QTextDocument, QFont
from openpyxl import load_workbook 
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
        wb = load_workbook("templates/reporte_base.xlsx")
        ws = wb.active
        ws.title = "Reporte"
        
        fecha = datetime.now().strftime("%d/%m/%Y")
        numero = Exportador.generar_nro_reporte()
        resumen = datos["resumen"]
        
        # 🔹 llenar datos fijos
        ws["C3"] = "REPORTE CONTROL DE CAJA"
        ws["C6"] = f"Empresa: {datos['empresa']}"
        ws["G3"] = fecha    # fecha de reporte
        ws["G4"] = numero   # nro de reporte
        
        # RESUMEN 
        ws["G6"] = Exportador.conversor_nro(resumen["saldo_inicial"])# lo demas se calcula
        
        ws["C12"] = datos["observaciones"]

        # 🔹 tabla
        fila_inicio = 15  # debajo del header
        
        
        for i, fila in enumerate(datos["tabla"], start=fila_inicio):
            ws[f"C{i}"] = fila[0]  # Fecha
            ws[f"D{i}"] = fila[1]  # Concepto
            ws[f"E{i}"] = Exportador.conversor_nro(fila[2])  # Ingreso
            ws[f"F{i}"] = Exportador.conversor_nro(fila[3])  # Egreso
            
        wb.save(ruta)
            
    def conversor_nro(valor):
        if not valor:
            return 0
        
        print("VALOR ORIGINAL:", valor)
        
        try:
            # limpiamos texto
            valor = str(valor)
            valor = valor.replace("S/", "")
            valor = valor.replace(",", "")
            valor = valor.strip()
            
            return float(valor)
        except:
            return 0
   
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