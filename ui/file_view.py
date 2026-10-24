"""
Vista de archivos avanzada con selección múltiple y operaciones en lote.
"""
import os
import shutil
import zipfile
from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import (
    QDir,
    QModelIndex,
    Qt,
    pyqtSignal,
)
from PyQt6.QtGui import QAction, QFileSystemModel
from PyQt6.QtWidgets import (
    QInputDialog,
    QListView,
    QMenu,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)


class FileView(QWidget):
    """Widget que muestra contenido de carpetas con soporte de selección múltiple."""

    folder_entered = pyqtSignal(str)
    file_opened = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._current_path: str = QDir.homePath()
        
        # Portapapeles para múltiples rutas
        self._clipboard_paths: List[str] = []
        self._is_cut: bool = False

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.model = QFileSystemModel(self)
        self.model.setRootPath("")
        self.model.setFilter(
            QDir.Filter.AllDirs
            | QDir.Filter.Files
            | QDir.Filter.NoDotAndDotDot
        )
        self.model.setReadOnly(False)

        self.view = QListView()
        self.view.setModel(self.model)
        self.view.setViewMode(QListView.ViewMode.ListMode)
        self.view.setResizeMode(QListView.ResizeMode.Adjust)
        # Habilitar selección extendida (Shift / Ctrl + Clic)
        self.view.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.view.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self.view.doubleClicked.connect(self._on_double_click)
        self.view.customContextMenuRequested.connect(self._on_context_menu)

        layout.addWidget(self.view)

    def set_root_path(self, path: str) -> None:
        if not os.path.isdir(path):
            return
        self._current_path = path
        index = self.model.setRootPath(path)
        self.view.setRootIndex(index)

    def current_path(self) -> str:
        return self._current_path

    def _on_double_click(self, index: QModelIndex) -> None:
        if not index.isValid():
            return
        path = self.model.filePath(index)
        if self.model.isDir(index):
            self.folder_entered.emit(path)
        else:
            self.file_opened.emit(path)

    def _get_selected_paths(self) -> List[str]:
        """Obtiene las rutas únicas de todos los elementos seleccionados."""
        indexes = self.view.selectionModel().selectedIndexes()
        paths = set()
        for idx in indexes:
            if idx.isValid():
                paths.add(self.model.filePath(idx))
        return list(paths)

    def _on_context_menu(self, pos) -> None:
        menu = QMenu(self)
        selected_paths = self._get_selected_paths()

        if selected_paths:
            # Si hay elementos seleccionados
            if len(selected_paths) == 1:
                path = selected_paths[0]
                if os.path.isdir(path):
                    act_open = QAction("Abrir carpeta", self)
                    act_open.triggered.connect(lambda: self.folder_entered.emit(path))
                    menu.addAction(act_open)
                else:
                    act_open = QAction("Abrir archivo", self)
                    act_open.triggered.connect(lambda: self.file_opened.emit(path))
                    menu.addAction(act_open)
                
                act_rename = QAction("Cambiar nombre", self)
                act_rename.triggered.connect(lambda: self._rename_item(path))
                menu.addAction(act_rename)
                menu.addSeparator()

            act_copy = QAction(f"Copiar ({len(selected_paths)})" if len(selected_paths) > 1 else "Copiar", self)
            act_copy.triggered.connect(lambda: self._copy_items(selected_paths))
            menu.addAction(act_copy)

            act_cut = QAction(f"Cortar ({len(selected_paths)})" if len(selected_paths) > 1 else "Cortar", self)
            act_cut.triggered.connect(lambda: self._cut_items(selected_paths))
            menu.addAction(act_cut)

            act_delete = QAction(f"Eliminar ({len(selected_paths)})" if len(selected_paths) > 1 else "Eliminar", self)
            act_delete.triggered.connect(lambda: self._delete_items(selected_paths))
            menu.addAction(act_delete)
            
            menu.addSeparator()

        # Submenú "Nuevo"
        sub_new = menu.addMenu("Nuevo")
        
        act_new_folder = QAction("Carpeta", self)
        act_new_folder.triggered.connect(lambda: self._create_new_item("folder"))
        sub_new.addAction(act_new_folder)

        act_new_txt = QAction("Archivo de texto (.txt)", self)
        act_new_txt.triggered.connect(lambda: self._create_new_item("file", ".txt"))
        sub_new.addAction(act_new_txt)

        act_new_zip = QAction("Archivo comprimido (.zip)", self)
        act_new_zip.triggered.connect(lambda: self._create_new_item("zip", ".zip"))
        sub_new.addAction(act_new_zip)

        act_new_docx = QAction("Documento de Word (.docx)", self)
        act_new_docx.triggered.connect(lambda: self._create_new_item("file", ".docx"))
        sub_new.addAction(act_new_docx)

        act_new_xlsx = QAction("Hoja de cálculo de Excel (.xlsx)", self)
        act_new_xlsx.triggered.connect(lambda: self._create_new_item("file", ".xlsx"))
        sub_new.addAction(act_new_xlsx)

        act_new_pptx = QAction("Presentación de PowerPoint (.pptx)", self)
        act_new_pptx.triggered.connect(lambda: self._create_new_item("file", ".pptx"))
        sub_new.addAction(act_new_pptx)

        if self._clipboard_paths:
            act_paste = QAction(f"Pegar ({len(self._clipboard_paths)})", self)
            act_paste.triggered.connect(self._paste_items)
            menu.addAction(act_paste)

        menu.exec(self.view.viewport().mapToGlobal(pos))

    # --- Operaciones en Lote y Archivos ---

    def _create_new_item(self, item_type: str, ext: str = "") -> None:
        base_name = "Nueva carpeta" if item_type == "folder" else f"Nuevo_archivo{ext}"
        target_path = os.path.join(self._current_path, base_name)
        
        counter = 1
        while os.path.exists(target_path):
            name_part, ext_part = os.path.splitext(base_name)
            target_path = os.path.join(self._current_path, f"{name_part} ({counter}){ext_part}")
            counter += 1

        try:
            if item_type == "folder":
                os.mkdir(target_path)
            elif item_type == "zip":
                with zipfile.ZipFile(target_path, 'w') as zf:
                    pass
            else:
                Path(target_path).touch()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo crear el elemento:\n{str(e)}")

    def _rename_item(self, path: str) -> None:
        old_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(self, "Cambiar nombre", "Nuevo nombre:", text=old_name)
        if ok and new_name and new_name != old_name:
            parent_dir = os.path.dirname(path)
            new_path = os.path.join(parent_dir, new_name)
            try:
                os.rename(path, new_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo renombrar:\n{str(e)}")

    def _delete_items(self, paths: List[str]) -> None:
        count = len(paths)
        msg = f"¿Estás seguro de que deseas eliminar los {count} elementos seleccionados?" if count > 1 else f"¿Estás seguro de que deseas eliminar '{os.path.basename(paths[0])}'?"
        
        reply = QMessageBox.question(
            self, "Confirmar eliminación", msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            errors = []
            for path in paths:
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                except Exception as e:
                    errors.append(f"{os.path.basename(path)}: {str(e)}")
            
            if errors:
                QMessageBox.warning(self, "Aviso de eliminación", "Algunos elementos no pudieron ser eliminados:\n" + "\n".join(errors))

    def _copy_items(self, paths: List[str]) -> None:
        self._clipboard_paths = paths
        self._is_cut = False

    def _cut_items(self, paths: List[str]) -> None:
        self._clipboard_paths = paths
        self._is_cut = True

    def _paste_items(self) -> None:
        if not self._clipboard_paths:
            return

        errors = []
        for src_path in self._clipboard_paths:
            if not os.path.exists(src_path):
                continue
            
            dest_path = os.path.join(self._current_path, os.path.basename(src_path))
            try:
                if os.path.isdir(src_path):
                    if self._is_cut:
                        shutil.move(src_path, dest_path)
                    else:
                        shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                else:
                    if self._is_cut:
                        shutil.move(src_path, dest_path)
                    else:
                        shutil.copy2(src_path, dest_path)
            except Exception as e:
                errors.append(f"{os.path.basename(src_path)}: {str(e)}")

        if self._is_cut:
            self._clipboard_paths = []
            self._is_cut = False

        if errors:
            QMessageBox.warning(self, "Aviso de portapapeles", "Hubo problemas con algunos archivos al pegar:\n" + "\n".join(errors))