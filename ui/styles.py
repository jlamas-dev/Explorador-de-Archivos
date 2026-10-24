"""
Hoja de estilos QSS moderna (tonos grises elegantes estilo Windows 11).
"""

GLOBAL_STYLE = """
/* ---------- Ventana principal ---------- */
QMainWindow, QWidget {
    background-color: #f3f3f3;
    color: #1f1f1f;
    font-family: "Segoe UI", "Segoe UI Variable", Arial, sans-serif;
    font-size: 10pt;
}

/* ---------- Barra de herramientas ---------- */
QToolBar {
    background-color: #ffffff;
    border: none;
    border-bottom: 1px solid #e1e1e1;
    padding: 6px 8px;
    spacing: 6px;
}

QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 6px 10px;
    color: #1f1f1f;
    font-weight: 500;
}

QToolButton:hover {
    background-color: #f0f0f0;
    border: 1px solid #e1e1e1;
}

QToolButton:pressed {
    background-color: #e5e5e5;
}

QToolButton:disabled {
    color: #a0a0a0;
}

/* ---------- Barra de direcciones ---------- */
QLineEdit {
    background-color: #ffffff;
    border: 1px solid #d6d6d6;
    border-radius: 8px;
    padding: 6px 10px;
    selection-background-color: #0078d4;
    selection-color: #ffffff;
}

QLineEdit:focus {
    border: 1px solid #0078d4;
}

/* ---------- Pestañas ---------- */
QTabWidget::pane {
    border: none;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #ececec;
    color: #1f1f1f;
    padding: 8px 16px;
    margin-right: 3px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border: 1px solid #e1e1e1;
    border-bottom: none;
    min-width: 140px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    font-weight: 600;
    border-bottom: 1px solid #ffffff;
}

QTabBar::tab:hover:!selected {
    background-color: #e5e5e5;
}

QTabBar::close-button {
    image: none;
    subcontrol-position: right;
}

/* ---------- Panel lateral (Sidebar) ---------- */
QListWidget {
    background-color: #fafafa;
    border: none;
    border-right: 1px solid #e1e1e1;
    padding: 8px;
    outline: 0;
}

QListWidget::item {
    padding: 8px 10px;
    border-radius: 6px;
    margin: 2px 0;
}

QListWidget::item:hover {
    background-color: #efefef;
}

QListWidget::item:selected {
    background-color: #e0efff;
    color: #005a9e;
    font-weight: 600;
}

/* ---------- Vista de archivos ---------- */
QListView, QTableView, QTreeView {
    background-color: #ffffff;
    border: none;
    outline: 0;
    padding: 6px;
}

QListView::item, QTableView::item {
    padding: 6px;
    border-radius: 4px;
}

QListView::item:hover, QTableView::item:hover {
    background-color: #f0f6ff;
}

QListView::item:selected, QTableView::item:selected {
    background-color: #cfe4ff;
    color: #000000;
}

/* ---------- Cabeceras de tabla ---------- */
QHeaderView::section {
    background-color: #f7f7f7;
    border: none;
    border-bottom: 1px solid #e1e1e1;
    padding: 6px;
    font-weight: 600;
}

/* ---------- Scrollbars ---------- */
QScrollBar:vertical {
    background: transparent;
    width: 12px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #c8c8c8;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #a8a8a8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: transparent;
    height: 12px;
}

QScrollBar::handle:horizontal {
    background: #c8c8c8;
    border-radius: 6px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: #a8a8a8;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* ---------- Splitter ---------- */
QSplitter::handle {
    background-color: #e1e1e1;
    width: 1px;
}
"""