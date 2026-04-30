from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView,
    QStyledItemDelegate, QStyle, QGridLayout, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from datetime import datetime
import os
import json

class VentanaControlCaja(QMainWindow):

    def __init__(self, empresa):
        super().__init__()
        
        self.empresa = empresa

        self.setWindowTitle(f"Control de Caja - {empresa}")
        self.resize(1000, 600)
        
        # =====================
        # WIDGET CENTRAL
        # =====================
        central = QWidget()
        self.setCentralWidget(central)

        layout_principal = QVBoxLayout()
        central.setLayout(layout_principal)

        # =====================
        # CONTENIDO DERECHO
        # =====================
        contenido = QWidget()
        contenido_layout = QVBoxLayout()
        contenido.setLayout(contenido_layout)
        
        # =====================
        # HEADER ARRIBA
        # =====================
        
        header = QHBoxLayout()
        
        self.btn_volver = QPushButton("Volver")
        self.btn_volver.setFixedWidth(80)
        self.btn_volver.clicked.connect(self.close)
        
        # Palanca de estado
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["ACTIVO", "FINALIZADO"])
        self.combo_estado.currentTextChanged.connect(self.cambiar_estado)
        self.combo_estado.setCurrentText("ACTIVO")
        
        # Boton Guardar
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setFixedWidth(80)
        self.btn_guardar.clicked.connect(self.guardar_datos)
        
        header.addWidget(self.btn_volver)
        header.addWidget(self.combo_estado)
        header.addWidget(self.btn_guardar)
        header.addStretch()
        
        contenido_layout.addLayout(header)

        # =====================
        # TITULO
        # =====================
        self.lbl_titulo = QLabel(f"CONTROL DE CAJA - {empresa}")
        self.lbl_titulo.setAlignment(Qt.AlignCenter)
        self.lbl_titulo.setStyleSheet("font-size:18px; font-weight:bold;")
        contenido_layout.addWidget(self.lbl_titulo)

        # =====================
        # BLOQUE DATOS GENERALES
        # =====================
        datos_widget = QWidget()
        datos_layout = QHBoxLayout()
        datos_widget.setLayout(datos_layout)

        col_izquierda = QVBoxLayout()
        col_derecha = QVBoxLayout()

        datos_layout.addLayout(col_izquierda)
        datos_layout.addStretch()
        datos_layout.addLayout(col_derecha)

        self.lbl_fecha_inicio = QLabel("Fecha inicio: ")
        self.lbl_fecha = QLabel("Periodo: 04/26")
        col_izquierda.addWidget(self.lbl_fecha)

        fila_saldo = QHBoxLayout()
        lbl_saldo = QLabel("Saldo Inicial:")
        self.input_saldo = QLineEdit("0.00")

        self.input_saldo.setFixedWidth(100)
        self.input_saldo.editingFinished.connect(self.colocar_saldo_inicial)

        fila_saldo.addWidget(lbl_saldo)
        fila_saldo.addWidget(self.input_saldo)
        fila_saldo.addStretch()

        self.lbl_ingresos = QLabel("Ingresos Totales: 0.00")
        self.lbl_egresos = QLabel("Egresos Totales: 0.00")
        self.lbl_saldo_total = QLabel("Saldo Total: 0.00")

        col_derecha.addLayout(fila_saldo)
        col_derecha.addWidget(self.lbl_ingresos)
        col_derecha.addWidget(self.lbl_egresos)
        col_derecha.addWidget(self.lbl_saldo_total)

        contenido_layout.addWidget(datos_widget)
        contenido_layout.addSpacing(10)

        # =====================
        # TABLA MOVIMIENTOS
        # =====================
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)

        self.tabla.setHorizontalHeaderLabels([
            "Fecha", "Concepto", "Ingreso", "Egreso", " Saldo "
        ])

        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)    # Fecha automatico
        header.setSectionResizeMode(1, QHeaderView.Stretch)             # Concepto
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)    # Ingreso
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)    # Egreso
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)    # Saldo

        self.tabla.setStyleSheet("""
            QTableWidget {
                gridline-color: #dcdcdc;
                selection-background-color: #e8f2ff;
                selection-color: black;
            }
            QHeaderView::section {
                font-weight: bold;
                background-color: #f2f2f2;
                border: 1px solid #dcdcdc;
                padding: 4px;
            }
            QTableWidget::item:focus {
                outline: none;
            }
        """)

        self.tabla.setEditTriggers(
            QAbstractItemView.DoubleClicked |
            QAbstractItemView.EditKeyPressed
        )

        self.tabla.setItemDelegate(SinCursorDelegate())
        self.tabla.setItemDelegateForColumn(4, NoEditableDelegate())

        # Empezar fila vacia
        self.tabla.setRowCount(1)
        self.fila_total = 1
        self.tabla.itemChanged.connect(self.verificar_nueva_fila)

        contenido_layout.addWidget(self.tabla)

        # =====================
        # TABLA TOTALES
        # =====================
        self.tabla_totales = QTableWidget()
        self.tabla_totales.setColumnCount(5)
        self.tabla_totales.setRowCount(1)

        self.tabla_totales.setHorizontalHeaderLabels([
            "", "TOTAL", "", "", ""
        ])

        for i in range(5):
            self.tabla_totales.setColumnWidth(i, self.tabla.columnWidth(i))

        # Oculta header
        self.tabla_totales.horizontalHeader().setVisible(False)
        self.tabla_totales.verticalHeader().setVisible(False)
        # Bloquea edicion
        self.tabla_totales.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # Estilo
        self.tabla_totales.setFixedHeight(40)
        self.tabla_totales.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabla_totales.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla_totales.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabla_totales.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabla_totales.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.tabla_totales.setStyleSheet("""
            QTableWidget {
                background-color: #f5f5f5;
                font-weight: bold;
                border-top: 1px solid #dcdcdc;
            }
        """)

        self.tabla_totales.setItem(0, 1, QTableWidgetItem("TOTAL"))
        self.tabla_totales.setItem(0, 2, QTableWidgetItem("S/ 0.00"))
        self.tabla_totales.setItem(0, 3, QTableWidgetItem("S/ 0.00"))
        self.tabla_totales.setItem(0, 4, QTableWidgetItem("S/ 0.00"))

        contenido_layout.addWidget(self.tabla_totales)

        for col in (2, 3, 4):
            item = self.tabla_totales.item(0, col)
            if item:
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.tabla.horizontalHeader().sectionResized.connect(
            lambda i, old, new:
            self.tabla_totales.setColumnWidth(i, new)
        )

        for i in range(5):
            self.tabla_totales.setColumnWidth(i, self.tabla.columnWidth(i))

        # cargar datos guardados
        self.cargar_datos()
        
        layout_principal.addWidget(contenido)

    def verificar_nueva_fila(self, item):
        fila = item.row()
        columna = item.column()
        
        if item.row() == self.fila_total:
            return

        self.tabla.blockSignals(True)

        if columna in (2, 3):
            ingreso_item = self.tabla.item(fila, 2)
            egreso_item = self.tabla.item(fila, 3)

            ingreso = self.convertir_a_float(
                ingreso_item.text() if ingreso_item else ""
            )

            egreso = self.convertir_a_float(
                egreso_item.text() if egreso_item else ""
            )

            # evitar ingreso y egreso al mismo tiempo
            if ingreso > 0 and egreso > 0:
                if columna == 2:
                    egreso = 0
                    self.tabla.setItem(fila, 3, QTableWidgetItem(""))
                else:
                    ingreso = 0
                    self.tabla.setItem(fila, 2, QTableWidgetItem(""))

            # formatear moneda
            if ingreso != 0:
                self.formatear_moneda(fila, 2, ingreso)

            if egreso != 0:
                self.formatear_moneda(fila, 3, egreso)

            # calcular saldo
            if fila != 0 and ingreso == 0 and egreso == 0:
                self.tabla.setItem(fila, 4, QTableWidgetItem(""))
            else:
                if fila == 0:
                    saldo_anterior = self.convertir_a_float(self.input_saldo.text())
                else:
                    saldo_item = self.tabla.item(fila - 1, 4)
                    saldo_anterior = self.convertir_a_float(
                        saldo_item.text() if saldo_item else ""
                    )

                saldo = saldo_anterior + ingreso - egreso
                saldo_item = QTableWidgetItem(f"S/ {saldo:.2f}")
                saldo_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tabla.setItem(fila, 4, saldo_item)

            self.recalcular_saldos()

        if columna in (1, 2, 3):
            fecha_item = self.tabla.item(fila, 0)
            if not fecha_item or fecha_item.text() == "":
                fecha = datetime.now().strftime("%d/%m/%Y")
                self.tabla.setItem(fila, 0, QTableWidgetItem(fecha))

        if fila == self.fila_total - 1:
            if item.text().strip() != "":
                self.tabla.insertRow(self.fila_total)
                self.fila_total += 1

        self.calcular_totales()
        self.tabla.blockSignals(False)
        
    def colocar_saldo_inicial(self):
        texto = self.input_saldo.text()

        saldo = self.convertir_a_float(texto)
        
        self.input_saldo.setText(f"S/ {saldo:.2f}")

        if self.tabla.rowCount() == 0:
            self.tabla.setRowCount(1)

        self.tabla.setItem(0, 1, QTableWidgetItem("Saldo inicial en caja"))
        self.tabla.setItem(0, 2, QTableWidgetItem(""))
        self.tabla.setItem(0, 3, QTableWidgetItem(""))

        item_saldo = QTableWidgetItem(f"S/ {saldo:.2f}")
        item_saldo.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.tabla.setItem(0, 4, item_saldo)
        
        self.recalcular_saldos()
        self.calcular_totales()
        
        for col in range(5) :
            item = self.tabla.item(0, col)
            if item :
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

    def recalcular_saldos(self):
        saldo_anterior = self.convertir_a_float(self.input_saldo.text())
        saldo_final = saldo_anterior

        for fila in range(1, self.tabla.rowCount()):
            ingreso_item = self.tabla.item(fila, 2)
            egreso_item = self.tabla.item(fila, 3)
            
            ingreso = self.convertir_a_float(
                ingreso_item.text() if ingreso_item else ""
            )
            egreso = self.convertir_a_float(
                egreso_item.text() if egreso_item else ""
            )

            if ingreso == 0 and egreso == 0:
                self.tabla.setItem(fila, 4, QTableWidgetItem(""))
                continue

            saldo = saldo_anterior + ingreso - egreso
            saldo_item = QTableWidgetItem(f"S/ {saldo:.2f}")
            saldo_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(fila, 4, saldo_item)

            saldo_anterior = saldo
            saldo_final = saldo
         
        self.lbl_saldo_total.setText(f"Saldo Total: S/ {saldo_final:.2f}")        

    def calcular_totales(self):
        total_ingresos = 0
        total_egresos = 0

        for fila in range(1, self.fila_total):
            ingreso_item = self.tabla.item(fila, 2)
            egreso_item = self.tabla.item(fila, 3)

            ingreso = self.convertir_a_float(
                ingreso_item.text() if ingreso_item else ""
            )
            egreso = self.convertir_a_float(
                egreso_item.text() if egreso_item else ""
            )

            total_ingresos += ingreso
            total_egresos += egreso

        saldo = total_ingresos - total_egresos

        item_ing = QTableWidgetItem(f"S/ {total_ingresos:.2f}")
        item_egr = QTableWidgetItem(f"S/ {total_egresos:.2f}")
        item_sal = QTableWidgetItem(f"S/ {saldo:.2f}")

        for item in (item_ing, item_egr, item_sal):
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.tabla_totales.setItem(0, 2, item_ing)
        self.tabla_totales.setItem(0, 3, item_egr)
        self.tabla_totales.setItem(0, 4, item_sal)

        for i in range(self.tabla.columnCount()):
            self.tabla_totales.setColumnWidth(i, self.tabla.columnWidth(i))
            
        # actualizar resumen superior
        self.lbl_ingresos.setText(f"Ingresos Totales: S/ {total_ingresos:.2f}")
        self.lbl_egresos.setText(f"Egresos Totales: S/ {total_egresos:.2f}")
        
    def cambiar_estado(self, estado):
        if estado == "FINALIZADO" :
            self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.input_saldo.setEnabled(False)
            self.combo_estado.setEnabled(False)
        elif estado == "ACTIVO":
            self.tabla.setEditTriggers(
                QAbstractItemView.DoubleClicked | 
                QAbstractItemView.EditKeyPressed |
                QAbstractItemView.AnyKeyPressed
            )
            self.input_saldo.setEnabled(True) 
            
    def guardar_datos(self):
        datos = {
            "estado" : self.combo_estado.currentText(),
            "saldo_inicial" : self.input_saldo.text(),
            "filas" : []     
        }
        
        for fila in range(self.tabla.rowCount()):
            fila_data = []
            for col in range(self.tabla.columnCount()):
                item = self.tabla.item(fila,col)
                fila_data.append(item.text() if item else "")
            datos["filas"].append(fila_data)
            
        nombre_archivo = f"{self.empresa}.json"
        
        with open(nombre_archivo, "w", encoding= "utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
            
        print("Guardando en:", nombre_archivo)
            
    def closeEvent(self, event):
       self.guardar_datos()
       event.accept()
       
    def cargar_datos(self) :
        nombre_archivo = f"{self.empresa}.json"
        
        if not os.path.exists(nombre_archivo):
            return
        
        with open(nombre_archivo, "r", encoding= "utf-8") as f:
            datos = json.load(f)
        
        # 🔥 BLOQUEAR EVENTOS
        self.tabla.blockSignals(True)
        
        self.combo_estado.setCurrentText(datos.get("estado", "ACTIVO"))
        self.input_saldo.setText(datos.get("saldo_inicial", "0.00"))
        
        self.tabla.setRowCount(0)
        
        for fila_data in datos["filas"]:
            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            
            for col, valor in enumerate(fila_data):
                if valor:
                    self.tabla.setItem(fila, col, QTableWidgetItem(valor))    
         
        self.fila_total = self.tabla.rowCount()
        
        # 🔥 VOLVER A ACTIVAR
        self.tabla.blockSignals(False)
        
        self.recalcular_saldos()
        self.calcular_totales()
                  
        print("Cargando desde:", nombre_archivo)
    
    
    def convertir_a_float(self, texto):
        if not texto:
            return 0.0
        
        try:
            return float(texto.replace("S/", "").replace(",", "").strip())
        except:
            return 0.0
        
    def formatear_moneda(self, fila, columna, valor):
        item = QTableWidgetItem(f"S/ {valor:.2f}")
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.tabla.blockSignals(True)
        self.tabla.setItem(fila, columna, item)
        self.tabla.blockSignals(False)

class SinCursorDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.state &= ~QStyle.State_HasFocus
        super().paint(painter, option, index)


class NoEditableDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        return None