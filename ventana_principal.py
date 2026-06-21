
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTableView, QHeaderView, QPushButton, QTableWidget, QLineEdit
) 
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont
from PySide6.QtCore import Qt, QPropertyAnimation
from datetime import datetime
import os
import json

from delegates import ButtonDelegate
from ventana_control_caja import VentanaControlCaja
from dialog_empresa import DialogEmpresa

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
        self.mostrar_empresas("ACTIVO")

    def mostrar_finalizado(self):
        self.label_contenido.setText("Vista: Finalizado")
        self.mostrar_empresas("FINALIZADO")

    # =====================
    # VISTA EMPRESAS
    # =====================
    def mostrar_empresas(self, filtro_estado=None):
        # limpiar contenido anterior
        for i in reversed(range(self.contenido_layout.count())):
            widget_to_remove = self.contenido_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

        # Título
        titulo = QLabel("Empresas")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.contenido_layout.addWidget(titulo)

        # boton agregar
        btn_agregar = QPushButton("+ Nueva Empresa")
        btn_agregar.clicked.connect(self.abrir_dialog_empresa)
        self.contenido_layout.addWidget(btn_agregar)
        
        # boton de busqieda
        self.txt_busqueda = QLineEdit()
        self.txt_busqueda.setPlaceholderText("Buscar empresa...")
        self.txt_busqueda.textChanged.connect(self.buscar_empresa)
        self.contenido_layout.addWidget(self.txt_busqueda)
        self.contenido_layout.addSpacing(15)

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
        
        self.cargar_empresas(filtro_estado)

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

    def abrir_dialog_empresa(self):
        dialog = DialogEmpresa(self)
        
        if dialog.exec():
            nombre = dialog.txt_nombre.text().strip()
            if not nombre:
                return
            
            saldo = dialog.txt_saldo.text().strip()
            if not saldo:
                saldo = "0.00"
            
            # crear archivo json
            if self.crear_empresa(nombre, saldo):
                # mostrar empresa creada
                self.actualizar_tabla_empresas()
                # Abrir control de caja
                self.ventana = VentanaControlCaja(nombre, saldo)
                self.ventana.show()
            
            self.tabla_empresas.viewport().update()
            
            print("Empresa:", nombre)
            print("Saldo:", saldo)
            
    def crear_empresa(self, nombre, saldo):
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        
        datos = {
            "nombre": nombre,
            "fecha_creacion": fecha_actual,
            "fecha_finalizacion": "",
            "estado": "ACTIVO",
            "saldo_inicial": saldo,
            "observaciones": "",
            "filas": []
        }
        
        os.makedirs("datos", exist_ok=True)

        nombre_archivo = f"datos/{nombre}.json"
        
        if os.path.exists(nombre_archivo):
            print("La empresa ya existe")
            return False
        
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
        print("Empresa creada:", nombre_archivo)
        return True
        
    def cargar_empresas(self, filtro_estado=None):
        carpeta = "datos"

        if not os.path.exists(carpeta):
            return

        for archivo in os.listdir(carpeta):
            if not archivo.endswith(".json"):
                continue
            
            ruta = os.path.join(carpeta, archivo)
            
            with open(ruta, "r", encoding="utf-8") as f:
                print("Leyendo:", archivo)
                datos = json.load(f)
                
            datos.setdefault("nombre", archivo.replace(".json", ""))
            datos.setdefault("fecha_creacion", "")
            datos.setdefault("fecha_finalizacion", "")
            datos.setdefault("estado", "ACTIVO")
            
            if filtro_estado and datos["estado"] != filtro_estado:
                continue
            
            print("Archivo:", archivo)
            print(datos)
            
            fila = [
                QStandardItem(datos["nombre"]),
                QStandardItem(datos["fecha_creacion"]),
                QStandardItem(datos["estado"]),
                QStandardItem()
            ]

            for item in fila[:-1]:
                item.setEditable(False)

            self.model.appendRow(fila)

    def actualizar_tabla_empresas(self):
        self.model.removeRows(0, self.model.rowCount())
        print("Antes:", self.model.rowCount())
        self.cargar_empresas()  
        print("Después:", self.model.rowCount())
        
    def buscar_empresa(self, texto = ""):
        texto = texto.lower()
        
        for fila in range(self.model.rowCount()):
            nombre = self.model.item(fila, 0).text().lower()
            
            ocultar = texto not in nombre
            
            self.tabla_empresas.setRowHidden(fila, ocultar)