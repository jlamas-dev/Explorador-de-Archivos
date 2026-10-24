"""
Panel lateral con unidades de disco y accesos rápidos.
"""
import os
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QWidget, QVBoxLayout


class Sidebar(QWidget):
    """Barra lateral que muestra unidades y accesos rápidos."""

    # Señal emitida cuando el usuario selecciona una ruta
    path_selected = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup_ui()
        self._populate_items()

    # ------------------------------------------------------------------ UI
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.list_widget = QListWidget()
        self.list_widget.setSpacing(0)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.setIconSize(self.list_widget.iconSize())

        layout.addWidget(self.list_widget)

    # ------------------------------------------------------------ Poblar
    def _populate_items(self) -> None:
        """Añade accesos rápidos y unidades de disco al listado."""
        # Accesos rápidos (Escritorio, Documentos, Descargas, Imágenes, Música)
        quick_access = [
            ("Escritorio", self._user_path("Desktop")),
            ("Documentos", self._user_path("Documents")),
            ("Descargas", self._user_path("Downloads")),
            ("Imágenes", self._user_path("Pictures")),
            ("Música", self._user_path("Music")),
        ]

        self._add_section_header("Accesos rápidos")
        for name, path in quick_access:
            if path and os.path.isdir(path):
                self._add_item(name, path, icon_char="📁")

        # Unidades de disco (Windows: C:\, D:\ ... / Otros SO: /)
        self._add_section_header("Este equipo")
        for drive in self._get_drives():
            label = drive.rstrip("\\") or drive
            self._add_item(label, drive, icon_char="💾")

    @staticmethod
    def _user_path(subfolder: str) -> Optional[str]:
        """Resuelve la ruta de una carpeta del usuario de forma segura."""
        try:
            home = Path.home()
            candidate = home / subfolder
            if candidate.exists():
                return str(candidate)
            # Algunos LTSC en inglés u otros idiomas -> comprobar en inglés
            english = {
                "Desktop": "Desktop",
                "Documents": "Documents",
                "Downloads": "Downloads",
                "Pictures": "Pictures",
                "Music": "Music",
            }
            alt = home / english.get(subfolder, subfolder)
            return str(alt) if alt.exists() else None
        except Exception:
            return None

    @staticmethod
    def _get_drives() -> list[str]:
        """Devuelve las unidades de disco disponibles."""
        drives: list[str] = []
        if os.name == "nt":
            # Windows
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    drives.append(drive)
        else:
            # Otros sistemas (para pruebas)
            drives.append("/")
        return drives

    # --------------------------------------------------- Helpers de items
    def _add_section_header(self, text: str) -> None:
        item = QListWidgetItem(text)
        item.setFlags(Qt.ItemFlag.NoItemFlags)  # No seleccionable
        font = item.font()
        font.setBold(True)
        font.setPointSize(font.pointSize() - 1)
        item.setFont(font)
        item.setForeground(Qt.GlobalColor.gray)
        self.list_widget.addItem(item)

    def _add_item(self, text: str, path: str, icon_char: str = "📁") -> None:
        item = QListWidgetItem(f"{icon_char}  {text}")
        item.setData(Qt.ItemDataRole.UserRole, path)
        item.setToolTip(path)
        self.list_widget.addItem(item)

    # ---------------------------------------------------------- Señales
    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            self.path_selected.emit(path)

    # ---------------------------------------------------------- API
    def clear_selection(self) -> None:
        self.list_widget.clearSelection()