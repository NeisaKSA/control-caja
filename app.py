from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QStyledItemDelegate, QStyleOptionViewItem, QStyle, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from datetime import datetime


class VentanaControlCaja(QMainWindow):

    def __init__(self, empresa):
        super().__init__()

        self.setWindowTitle(f"Control de Caja - {empresa}")
        self.resize(1000, 600)

        # =====================
        # WIDGET CENTRAL
        # =====================
        central = QWidget()
        self.setCentralWidget(central)

        layout_principal = QHBoxLayout()
        central.setLayout(layout_principal)

        # =====================
        # SIDEBAR
        # =====================
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout()

        self.btn_volver = QPushButton("Volver")
        sidebar_layout.addWidget(self.btn_volver)
        self.btn_volver.clicked.connect(self.close)

        sidebar_layout.addWidget(QPushButton("Resumen"))
        sidebar_layout.addWidget(QPushButton("Movimientos"))
        sidebar_layout.addWidget(QPushButton("Reportes"))
        sidebar_layout.addStretch()

        sidebar.setLayout(sidebar_layout)
        sidebar.setFixedWidth(200)

        # =====================
        # CONTENIDO DERECHO
        # =====================
        contenido = QWidget()
        contenido_layout = QVBoxLayout()
        contenido.setLayout(contenido_layout)

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

        # contenido_layout.addWidget(datos_widget) abajo

        col_izquierda = QVBoxLayout()
        col_derecha = QVBoxLayout()

        datos_layout.addLayout(col_izquierda)
        datos_layout.addStretch()   # 👈 empuja la derecha
        datos_layout.addLayout(col_derecha)

        # ---- IZQUIERDA
        self.lbl_fecha_inicio = QLabel("Fecha inicio: ")
        self.lbl_fecha = QLabel("Periodo: 04/26")

        col_izquierda.addWidget(self.lbl_fecha)

        # ---- DERECHA
        # Saldo inicial (editable)
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
        contenido_layout.addSpacing(10)  # 👈 espacio pequeño controlado
                
        # =====================
        # TABLA MOVIMIENTOS
        # =====================
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)

        self.tabla.setHorizontalHeaderLabels([
            "Fecha", "Concepto", "Ingreso", "Egreso", "Saldo"
        ])            

        # que las columnas ocupen todo el ancho
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Fecha auto
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Concepto grande
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Ingreso
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Egreso
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Saldo

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
        
        # empezar con una fila vacía
        self.tabla.setRowCount(1)
        
        self.fila_total = 1
        self.tabla.itemChanged.connect(self.verificar_nueva_fila)
        
        contenido_layout.addWidget(self.tabla)
        
        # =====================
        # TOTALES ABAJO
        # =====================
        self.tabla_totales = QTableWidget()
        self.tabla_totales.setColumnCount(5)
        self.tabla_totales.setRowCount(1)

        self.tabla_totales.setHorizontalHeaderLabels([
            "", "TOTAL", "", "", ""
        ])

        # copiar tamaños de columnas
        for i in range(5):
            self.tabla_totales.setColumnWidth(i, self.tabla.columnWidth(i))

        # ocultar header
        self.tabla_totales.horizontalHeader().setVisible(False)
        self.tabla_totales.verticalHeader().setVisible(False)

        # bloquear edición
        self.tabla_totales.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # estilo
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

        # valores iniciales
        self.tabla_totales.setItem(0, 1, QTableWidgetItem("TOTAL"))
        self.tabla_totales.setItem(0, 2, QTableWidgetItem("S/ 0.00"))
        self.tabla_totales.setItem(0, 3, QTableWidgetItem("S/ 0.00"))
        self.tabla_totales.setItem(0, 4, QTableWidgetItem("S/ 0.00"))

        contenido_layout.addWidget(self.tabla_totales)
        
        for col in (2,3,4):
            item = self.tabla_totales.item(0, col)
            if item:
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
        self.tabla.horizontalHeader().sectionResized.connect(
            lambda i, old, new:
                self.tabla_totales.setColumnWidth(i, new)
        )   
        
        for i in range(5):
            self.tabla_totales.setColumnWidth(i, self.tabla.columnWidth(i))
        # totales_widget = QWidget()
        # totales_layout = QGridLayout()
        # totales_widget.setLayout(totales_layout)
        
        # lbl_total = QLabel("TOTAL")
        # self.lbl_total_ingresos = QLabel("S/ 0.00")
        # self.lbl_total_egresos = QLabel("S/ 0.00")
        # self.lbl_total_saldo = QLabel("S/ 0.00")
        
        # # negrita
        # lbl_total.setStyleSheet("font-weight: bold;")
        # self.lbl_total_ingresos.setStyleSheet("font-weight: bold;")
        # self.lbl_total_egresos.setStyleSheet("font-weight: bold;")
        # self.lbl_total_saldo.setStyleSheet("font-weight: bold;")

        # # columnas vacías para alinear con la tabla
        # totales_layout.addWidget(QLabel(""), 0, 0)
        # totales_layout.addWidget(lbl_total, 0, 1)
        # totales_layout.addWidget(self.lbl_total_ingresos, 0, 2)
        # totales_layout.addWidget(self.lbl_total_egresos, 0, 3)
        # totales_layout.addWidget(self.lbl_total_saldo, 0, 4)

        # # hacer que todas las columnas tengan mismo ancho
        # totales_layout.setColumnStretch(0, 1)  # espacio fecha
        # totales_layout.setColumnStretch(1, 3)  # concepto más grande
        # totales_layout.setColumnStretch(2, 1)  # ingreso
        # totales_layout.setColumnStretch(3, 1)  # egreso
        # totales_layout.setColumnStretch(4, 1)  # saldo
                
        # contenido_layout.addWidget(totales_widget)
        
        # =====================
        # LAYOUT FINAL
        # =====================
        layout_principal.addWidget(sidebar)
        layout_principal.addWidget(contenido)
        
        # self.sincronizar_totales()
        
    def verificar_nueva_fila(self, item):
        fila = item.row()
        columna = item.column()

        if item.row() == self.fila_total:
            return

        self.tabla.blockSignals(True)

        # -------- CALCULAR SALDO --------
        if columna in (2, 3):
            try:
                ingreso_item = self.tabla.item(fila, 2)
                egreso_item = self.tabla.item(fila, 3)

                ingreso = float(ingreso_item.text()) if ingreso_item and ingreso_item.text() else 0
                egreso = float(egreso_item.text()) if egreso_item and egreso_item.text() else 0
                
                if ingreso == 0 and egreso == 0 :
                    self.tabla.setItem(fila, 4, QTableWidgetItem(""))
                else :
                    if fila == 0:
                        saldo_anterior = float(self.input_saldo.text())
                    else:
                        saldo_item = self.tabla.item(fila - 1, 4)
                        saldo_anterior = float(saldo_item.text()) if saldo_item and saldo_item.text() else 0

                    saldo = saldo_anterior + ingreso - egreso

                    self.tabla.setItem(fila, 4, QTableWidgetItem(f"{saldo:.2f}"))
                    
                # 🔥 recalcular todos los de abajo
                self.recalcular_saldos()

            except:
                pass
            
        if columna in (1,2,3):
            fecha_item = self.tabla.item(fila, 0)
            
            # solo si aún no tiene fecha
            if not fecha_item or fecha_item.text() == "":
                fecha = datetime.now().strftime("%d/%m/%Y")
                self.tabla.setItem(fila, 0, QTableWidgetItem(fecha))
                
        # -------- AGREGAR FILA --------
        if fila == self.fila_total - 1:
            if item.text().strip() != "":
                self.tabla.insertRow(self.fila_total)
                self.fila_total += 1

        self.calcular_totales()
        self.tabla.blockSignals(False)
        
        
        
    def colocar_saldo_inicial(self):
        texto = self.input_saldo.text()

        try:
            saldo = float(texto)
        except ValueError:
            return

        # asegurar que haya al menos una fila
        if self.tabla.rowCount() == 0:
            self.tabla.setRowCount(1)

        # concepto
        self.tabla.setItem(0, 1, QTableWidgetItem("Saldo inicial en caja"))

        # ingreso vacío
        self.tabla.setItem(0, 2, QTableWidgetItem(""))

        # egreso vacío
        self.tabla.setItem(0, 3, QTableWidgetItem(""))

        # saldo
        item_saldo = QTableWidgetItem(f"{saldo:.2f}")
        item_saldo.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.tabla.setItem(0, 4, item_saldo)

        self.tabla
        
    def recalcular_saldos(self):
        saldo_anterior = float(self.input_saldo.text())

        for fila in range(1, self.tabla.rowCount()):
            ingreso_item = self.tabla.item(fila, 2)
            egreso_item = self.tabla.item(fila, 3)

            ingreso = float(ingreso_item.text()) if ingreso_item and ingreso_item.text() else 0
            egreso = float(egreso_item.text()) if egreso_item and egreso_item.text() else 0

            # si fila vacía → limpiar saldo
            if ingreso == 0 and egreso == 0:
                self.tabla.setItem(fila, 4, QTableWidgetItem(""))
                continue

            saldo = saldo_anterior + ingreso - egreso
            self.tabla.setItem(fila, 4, QTableWidgetItem(f"{saldo:.2f}"))

            saldo_anterior = saldo
        
    def calcular_totales(self):
        total_ingresos = 0
        total_egresos = 0

        for fila in range(1, self.fila_total):
            ingreso_item = self.tabla.item(fila, 2)
            egreso_item = self.tabla.item(fila, 3)

            ingreso = float(ingreso_item.text()) if ingreso_item and ingreso_item.text() else 0
            egreso = float(egreso_item.text()) if egreso_item and egreso_item.text() else 0

            total_ingresos += ingreso
            total_egresos += egreso

        saldo = total_ingresos - total_egresos

        item_ing = QTableWidgetItem(f"S/ {total_ingresos:.2f}")
        item_egr = QTableWidgetItem(f"S/ {total_egresos:.2f}")
        item_sal = QTableWidgetItem(f"S/ {saldo:.2f}")

        # alineación derecha
        for item in (item_ing, item_egr, item_sal):
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.tabla_totales.setItem(0, 2, item_ing)
        self.tabla_totales.setItem(0, 3, item_egr)
        self.tabla_totales.setItem(0, 4, item_sal)

        # sincronizar ancho después de escribir
        for i in range(self.tabla.columnCount()):
            self.tabla_totales.setColumnWidth(i, self.tabla.columnWidth(i))
    # def sincronizar_totales(self):
    #     for i in range(self.tabla.columnCount()):
    #         self.tabla_totales.setColumnWidth(i, self.tabla.columnWidth(i))
        
class SinCursorDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.state &= ~QStyle.State_HasFocus
        super().paint(painter, option, index)
        
class NoEditableDelegate(QStyledItemDelegate) :
    def createEditor(self, parent, option, index):
        return None
