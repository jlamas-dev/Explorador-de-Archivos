"""
Punto de entrada de la aplicación Explorador de Archivos.
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow
from ui.styles import GLOBAL_STYLE


def main() -> None:
    # Habilitar escalado HiDPI (importante en Windows 10/11)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Explorador de Archivos")
    app.setOrganizationName("PyQtExplorer")
    app.setStyle("Fusion")
    app.setStyleSheet(GLOBAL_STYLE)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()