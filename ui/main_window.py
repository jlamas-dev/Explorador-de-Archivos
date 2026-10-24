"""
Ventana principal con QTabWidget + barra de herramientas y barra lateral.
Cada pestaña encapsula su propio FileView y su propio historial.
"""
import os
from typing import Optional

from PyQt6.QtCore import QDir, Qt, QUrl, QSize
from PyQt6.QtGui import QAction, QDesktopServices, QIcon
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QToolBar,
    QLineEdit,
    QTabWidget,
    QSplitter,
    QToolButton,
    QFileIconProvider,
    QLabel,
    QMessageBox,
)

from .file_view import FileView
from .sidebar import Sidebar


# ------------------------------------------------------------------ Tab
class BrowserTab(QWidget):
    """Una pestaña individual con su propio FileView e historial de navegación."""

    def __init__(self, start_path: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._history: list[str] = []
        self._history_index: int = -1

        self.file_view = FileView(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.file_view)

        self.navigate_to(start_path)

    # ----------------------------------------------------------- Navegar
    def navigate_to(self, path: str, add_to_history: bool = True) -> None:
        if not os.path.isdir(path):
            return
        path = os.path.normpath(path)
        self.file_view.set_root_path(path)

        if add_to_history:
            # Si estamos en medio del historial, cortar la rama posterior
            if self._history_index < len(self._history) - 1:
                self._history = self._history[: self._history_index + 1]
            if not self._history or self._history[-1] != path:
                self._history.append(path)
            self._history_index = len(self._history) - 1

    def current_path(self) -> str:
        return self.file_view.current_path()

    # ---------------------------------------------------------- Historial
    def go_back(self) -> Optional[str]:
        if self._history_index > 0:
            self._history_index -= 1
            path = self._history[self._history_index]
            self.file_view.set_root_path(path)
            return path
        return None

    def go_forward(self) -> Optional[str]:
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            path = self._history[self._history_index]
            self.file_view.set_root_path(path)
            return path
        return None

    def can_go_back(self) -> bool:
        return self._history_index > 0

    def can_go_forward(self) -> bool:
        return self._history_index < len(self._history) - 1


# ------------------------------------------------------------- MainWindow
class MainWindow(QMainWindow):
    """Ventana principal del explorador de archivos."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Explorador de Archivos")
        self.resize(1200, 760)

        self._icon_provider = QFileIconProvider()

        self._setup_ui()
        self._setup_toolbar()
        self._setup_shortcuts()
        self._add_new_tab(QDir.homePath())

    # ------------------------------------------------------------- UI
    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Splitter horizontal: sidebar + tabs
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        self.sidebar = Sidebar()
        self.sidebar.setMinimumWidth(200)
        self.sidebar.setMaximumWidth(320)
        self.sidebar.path_selected.connect(self._navigate_active_tab)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)

        # Botón "+" para nueva pestaña
        new_tab_btn = QToolButton()
        new_tab_btn.setText("+")
        new_tab_btn.setToolTip("Nueva pestaña (Ctrl+T)")
        new_tab_btn.clicked.connect(lambda: self._add_new_tab(QDir.homePath()))
        self.tabs.setCornerWidget(new_tab_btn, Qt.Corner.TopRightCorner)

        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.tabs)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([240, 960])

        layout.addWidget(splitter)

    # ------------------------------------------------------ Toolbar
    def _setup_toolbar(self) -> None:
        toolbar = QToolBar("Navegación")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(18, 18))
        self.addToolBar(toolbar)

        # Botones Atrás / Adelante / Arriba
        self.act_back = QAction("←", self)
        self.act_back.setToolTip("Atrás (Alt+←)")
        self.act_back.triggered.connect(self._go_back)
        toolbar.addAction(self.act_back)

        self.act_forward = QAction("→", self)
        self.act_forward.setToolTip("Adelante (Alt+→)")
        self.act_forward.triggered.connect(self._go_forward)
        toolbar.addAction(self.act_forward)

        self.act_up = QAction("↑", self)
        self.act_up.setToolTip("Subir un nivel (Alt+↑)")
        self.act_up.triggered.connect(self._go_up)
        toolbar.addAction(self.act_up)

        toolbar.addSeparator()

        # Barra de direcciones
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Escribe una ruta y pulsa Enter...")
        self.address_bar.returnPressed.connect(self._on_address_enter)
        toolbar.addWidget(self.address_bar)

        # Botón refrescar
        self.act_refresh = QAction("⟳", self)
        self.act_refresh.setToolTip("Actualizar (F5)")
        self.act_refresh.triggered.connect(self._refresh_active_tab)
        toolbar.addAction(self.act_refresh)

    # ------------------------------------------------------ Atajos
    def _setup_shortcuts(self) -> None:
        from PyQt6.QtGui import QKeySequence, QShortcut

        QShortcut(QKeySequence("Alt+Left"), self, self._go_back)
        QShortcut(QKeySequence("Alt+Right"), self, self._go_forward)
        QShortcut(QKeySequence("Alt+Up"), self, self._go_up)
        QShortcut(QKeySequence("Ctrl+T"), self, lambda: self._add_new_tab(QDir.homePath()))
        QShortcut(QKeySequence("Ctrl+W"), self, lambda: self._close_tab(self.tabs.currentIndex()))
        QShortcut(QKeySequence("F5"), self, self._refresh_active_tab)
        QShortcut(QKeySequence("Ctrl+L"), self, self._focus_address_bar)

    # ------------------------------------------------------ Tabs API
    def _add_new_tab(self, path: str) -> None:
        if not os.path.isdir(path):
            path = QDir.homePath()

        tab = BrowserTab(path, self)
        tab.file_view.folder_entered.connect(self._on_folder_entered)
        tab.file_view.file_opened.connect(self._on_file_opened)

        # Nombre de la pestaña = nombre de la carpeta actual
        title = self._tab_title_for(path)
        index = self.tabs.addTab(tab, title)
        self.tabs.setCurrentIndex(index)
        self._sync_address_bar()

    def _close_tab(self, index: int) -> None:
        if index < 0:
            return
        widget = self.tabs.widget(index)
        self.tabs.removeTab(index)
        if widget is not None:
            widget.deleteLater()

        # Siempre mantener al menos una pestaña
        if self.tabs.count() == 0:
            self._add_new_tab(QDir.homePath())

    def _current_tab(self) -> Optional[BrowserTab]:
        widget = self.tabs.currentWidget()
        return widget if isinstance(widget, BrowserTab) else None

    @staticmethod
    def _tab_title_for(path: str) -> str:
        name = os.path.basename(os.path.normpath(path))
        return name if name else path

    # ------------------------------------------------ Eventos navegación
    def _on_folder_entered(self, path: str) -> None:
        tab = self._current_tab()
        if tab is None:
            return
        tab.navigate_to(path)
        self.tabs.setTabText(self.tabs.currentIndex(), self._tab_title_for(path))
        self._sync_address_bar()

    def _on_file_opened(self, path: str) -> None:
        """Abre archivos con el programa por defecto del sistema."""
        if os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def _navigate_active_tab(self, path: str) -> None:
        tab = self._current_tab()
        if tab is None:
            self._add_new_tab(path)
            return
        tab.navigate_to(path)
        self.tabs.setTabText(self.tabs.currentIndex(), self._tab_title_for(path))
        self._sync_address_bar()

    # ------------------------------------------------------- Toolbar ops
    def _go_back(self) -> None:
        tab = self._current_tab()
        if tab is None:
            return
        new_path = tab.go_back()
        if new_path:
            self.tabs.setTabText(self.tabs.currentIndex(), self._tab_title_for(new_path))
            self._sync_address_bar()

    def _go_forward(self) -> None:
        tab = self._current_tab()
        if tab is None:
            return
        new_path = tab.go_forward()
        if new_path:
            self.tabs.setTabText(self.tabs.currentIndex(), self._tab_title_for(new_path))
            self._sync_address_bar()

    def _go_up(self) -> None:
        tab = self._current_tab()
        if tab is None:
            return
        current = tab.current_path()
        parent = os.path.dirname(os.path.normpath(current))
        if parent and parent != current and os.path.isdir(parent):
            self._on_folder_entered(parent)

    def _refresh_active_tab(self) -> None:
        tab = self._current_tab()
        if tab is None:
            return
        # Forzar refresco del modelo
        tab.file_view.model.setRootPath("")
        tab.file_view.set_root_path(tab.current_path())

    def _on_address_enter(self) -> None:
        raw = self.address_bar.text().strip().strip('"')
        if not raw:
            return
        # Expandir variables de entorno y "~"
        path = os.path.expandvars(os.path.expanduser(raw))
        if os.path.isdir(path):
            self._on_folder_entered(path)
        elif os.path.isfile(path):
            self._on_file_opened(path)
        else:
            QMessageBox.warning(
                self, "Ruta no válida",
                f"La ruta no existe:\n{raw}"
            )

    def _focus_address_bar(self) -> None:
        self.address_bar.setFocus()
        self.address_bar.selectAll()

    # ------------------------------------------------ Sincronización UI
    def _on_tab_changed(self, index: int) -> None:
        self._sync_address_bar()

    def _sync_address_bar(self) -> None:
        tab = self._current_tab()
        if tab is None:
            self.address_bar.clear()
            return
        self.address_bar.setText(tab.current_path())

        # Actualizar estado de los botones atrás / adelante
        self.act_back.setEnabled(tab.can_go_back())
        self.act_forward.setEnabled(tab.can_go_forward())

        # Habilitar / deshabilitar "subir" (en la raíz no se puede subir)
        current = os.path.normpath(tab.current_path())
        parent = os.path.dirname(current)
        self.act_up.setEnabled(parent != current)