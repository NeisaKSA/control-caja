
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTableView, QHeaderView, QPushButton, QTableWidget
) 
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont
from PySide6.QtCore import Qt, QPropertyAnimation

from delegates import ButtonDelegate
from ventana_control_caja import VentanaControlCaja

class VentanaPrincipal(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sistema control de caja")
        self.resize(1000, 600)

        # =====================
        # WIDGET CENTRAL
        # =====================
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout_principal = QHBoxLayout()

        # =====================
        # SIDEBAR
        # =====================
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout()

        self.btn_empresas = QPushButton("Empresa")
        sidebar_layout.addWidget(self.btn_empresas)

        self.btn_estado = QPushButton("Estado")
        sidebar_layout.addWidget(self.btn_estado)

        # Submenú Estado
        self.estado_widget = QWidget()
        estado_layout = QVBoxLayout()

        self.btn_proceso = QPushButton("Proceso")
        self.btn_finalizado = QPushButton("Finalizado")

        estado_layout.addWidget(self.btn_proceso)
        estado_layout.addWidget(self.btn_finalizado)

        self.estado_widget.setLayout(estado_layout)
        self.estado_widget.setVisible(False)

        sidebar_layout.addWidget(self.estado_widget)

        sidebar_layout.addWidget(QPushButton("Configuracion"))
        sidebar_layout.addStretch()

        sidebar.setLayout(sidebar_layout)

        # =====================
        # CONTENIDO DERECHO
        # =====================
        self.contenido = QWidget()
        self.contenido_layout = QVBoxLayout()
        self.contenido.setLayout(self.contenido_layout)

        self.label_contenido = QLabel("Bienvenido")
        self.contenido_layout.addWidget(self.label_contenido)

        # =====================
        # ESTILOS
        # =====================
        sidebar.setStyleSheet("background-color: lightgray;")
        sidebar.setFixedWidth(200)
        estado_layout.setContentsMargins(15, 0, 0, 0)
        self.contenido.setStyleSheet("background-color: white;")

        # =====================
        # ANIMACIÓN
        # =====================
        self.animacion = QPropertyAnimation(self.estado_widget, b"maximumHeight")
        self.animacion.setDuration(200)

        # =====================
        # AGREGAR LAYOUT
        # =====================
        layout_principal.addWidget(sidebar, 1)
        layout_principal.addWidget(self.contenido, 4)

        central_widget.setLayout(layout_principal)

        # =====================
        # CONEXIONES
        # =====================
        self.btn_estado.clicked.connect(self.toggle_estado)
        self.btn_proceso.clicked.connect(self.mostrar_proceso)
        self.btn_finalizado.clicked.connect(self.mostrar_finalizado)
        self.btn_empresas.clicked.connect(self.mostrar_empresas)

        self.mostrar_empresas()

    # =====================
    # FUNCIONES SIDEBAR
    # =====================
    def toggle_estado(self):
        if self.estado_widget.maximumHeight() == 0:
            self.estado_widget.setVisible(True)
            self.animacion.setStartValue(0)
            self.animacion.setEndValue(60)
        else:
            self.animacion.setStartValue(self.estado_widget.height())
            self.animacion.setEndValue(0)

        self.animacion.start()

    def mostrar_proceso(self):
        self.label_contenido.setText("Vista: Proceso")

    def mostrar_finalizado(self):
        self.label_contenido.setText("Vista: Finalizado")

    # =====================
    # VISTA EMPRESAS
    # =====================
    def mostrar_empresas(self):
        # limpiar contenido anterior
        for i in reversed(range(self.contenido_layout.count())):
            widget_to_remove = self.contenido_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

        # Título
        titulo = QLabel("Empresas")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.contenido_layout.addWidget(titulo)

        # Modelo
        self.model = QStandardItemModel()
        headers = ["Empresa", "Fecha inicio", "Estado", "Acción"]
        self.model.setHorizontalHeaderLabels(headers)

        # header bold
        font_bold = QFont()
        font_bold.setBold(True)

        for col in range(len(headers)):
            self.model.setHeaderData(
                col, Qt.Horizontal, font_bold, Qt.FontRole
            )

        # Datos
        datos = [
            ("Empresa A", "2026-04-03", "Proceso"),
            ("Empresa B", "2026-04-01", "Terminada"),
        ]

        for empresa, fecha, estado in datos:
            fila = []

            for valor in [empresa, fecha, estado]:
                item = QStandardItem(valor)
                item.setEditable(False)
                fila.append(item)

            fila.append(QStandardItem())
            self.model.appendRow(fila)

        # Tabla
        self.tabla_empresas = QTableView()
        self.tabla_empresas.setModel(self.model)
        self.tabla_empresas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_empresas.verticalHeader().setVisible(False)
        self.tabla_empresas.setSelectionBehavior(QTableView.SelectRows)
        self.tabla_empresas.setEditTriggers(QTableView.NoEditTriggers)
        self.tabla_empresas.setFocusPolicy(Qt.NoFocus)
        self.tabla_empresas.setAlternatingRowColors(True)

        # Estilo
        self.tabla_empresas.setStyleSheet("""
            QTableView {
                border: none;
                selection-background-color: #a0c4ff;
            }
            QTableView::item {
                background-color: white;
                padding: 5px;
            }
            QTableView::item:hover {
                background-color: white;
            }
            QTableView::item:selected {
                background-color: #a0c4ff;
                color: black;
            }
        """)

        # Delegado botón
        self.button_delegate = ButtonDelegate()
        self.tabla_empresas.setItemDelegateForColumn(3, self.button_delegate)
        self.button_delegate.clicked.connect(self.abrir_empresa)

        self.contenido_layout.addWidget(self.tabla_empresas)

    # =====================
    # ABRIR EMPRESA
    # =====================
    def abrir_empresa(self, index):
        empresa = self.model.item(index.row(), 0).text()
        self.ventana = VentanaControlCaja(empresa)
        self.ventana.show()
        
    # =====================
    # ABRIR CONTROL DE CAJA
    # =====================
    def mostrar_control_caja(self, empresa):
        # limpiar contenido
        for i in reversed(range(self.contenido_layout.count())):
            widget = self.contenido_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # titulo
        titulo = QLabel(f"Control de Caja - {empresa}")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.contenido_layout.addWidget(titulo)

        # tabla editable
        self.tabla_caja = QTableWidget()
        self.tabla_caja.setColumnCount(5)
        self.tabla_caja.setHorizontalHeaderLabels([
            "Fecha",
            "Descripción",
            "Ingreso",
            "Gasto",
            "Total"
        ])

        self.tabla_caja.setRowCount(15)

        self.tabla_caja.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.contenido_layout.addWidget(self.tabla_caja)
