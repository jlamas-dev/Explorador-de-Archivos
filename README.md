# 🚀 Modern File Explorer for Windows

Un explorador de archivos moderno, ligero y de código abierto desarrollado en **Python** y **PyQt6**, diseñado específicamente para ofrecer una experiencia fluida en **Windows 10/11** (incluyendo ediciones LTSC).

---

## ✨ Características Principales

* 🗂️ **Sistema de Pestañas:** Navega por múltiples carpetas simultáneamente en una misma ventana.
* ⚡ **Rendimiento Asíncrono:** Utiliza `QFileSystemModel` para una carga fluida sin congelamientos de la interfaz.
* 🛠️ **Operaciones Completas (CRUD):** 
  * Copiar, cortar y pegar elementos individuales o en **selección múltiple**.
  * Cambiar nombre de archivos y carpetas de forma sencilla.
  * Eliminar elementos con confirmación de seguridad.
* 📄 **Creación Rápida de Archivos:** Menú contextual integrado para crear al instante:
  * Nuevas carpetas
  * Archivos de texto (`.txt`)
  * Archivos comprimidos (`.zip`)
  * Documentos de Office (`.docx`, `.xlsx`, `.pptx`)
* 🎨 **Interfaz Moderna:** Estilo limpio adaptado con temas elegantes compatibles con el sistema.

---

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3.15
* **Framework GUI:** PyQt6
* **Empaquetado:** PyInstaller & Inno Setup Compiler (para el instalador `.exe`)
