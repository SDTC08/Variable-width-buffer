# Variable Width Buffer Plugin para QGIS

Plugin de QGIS para generar buffers dinámicos alrededor de conductos de redes hidráulicas basados en sus dimensiones (ancho/diámetro).

## Características

- ✅ Genera buffers dinámicos basados en las dimensiones reales de cada conducto
- ✅ Detecta automáticamente si el conducto es circular o rectangular
- ✅ Soporta dimensiones en milímetros o metros
- ✅ Calcula el radio del buffer como mitad del ancho/diámetro
- ✅ Factor de ajuste del buffer (multiplicador)
- ✅ Añade campos con información de tipo de sección, dimensiones, longitud y área
- ✅ Integrado en el panel de Processing de QGIS

## Instalación

### Método 1: Instalación Manual

1. Descarga el plugin (carpeta `conduit_buffer_plugin`)
2. Copia la carpeta completa a tu directorio de plugins de QGIS:
   - **Windows**: `C:\Users\[usuario]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`

3. Abre QGIS
4. Ve a **Complementos → Administrar e instalar complementos**
5. En la pestaña **Instalados**, busca "Variable Width Buffer"
6. Activa el plugin marcando la casilla

### Método 2: Instalación desde ZIP

1. Comprime la carpeta `conduit_buffer_plugin` en un archivo ZIP
2. En QGIS, ve a **Complementos → Administrar e instalar complementos**
3. Selecciona **Instalar desde ZIP**
4. Selecciona el archivo ZIP descargado
5. Haz clic en **Instalar complemento**

## Uso

### Desde el Panel de Processing

1. Abre el **Panel de Processing** (Procesado → Caja de herramientas)
2. Busca **"Conduit Buffer"** o **"Buffer Dinámico de Conductos"**
3. Expande el grupo **Hidráulica**
4. Doble clic en **Buffer Dinámico de Conductos**

### Parámetros

- **Capa de conductos**: Selecciona tu capa de líneas con los conductos
- **Campo de ancho**: Campo que contiene el ancho del conducto
- **Campo de alto/diámetro**: Campo que contiene la altura o diámetro
- **Unidad de las dimensiones**: Selecciona si tus datos están en milímetros o metros
- **Factor de buffer**: Multiplicador para ajustar el tamaño (1.0 = tamaño normal)
- **Buffers de salida**: Especifica dónde guardar el resultado

### Ejemplo

Si tienes conductos de InfoWorks con:
- `condwidth` = 1800 (mm)
- `condheight` = 600 (mm)

El plugin generará un buffer rectangular con radio de 900mm (0.9m) del ancho.

Si el conducto es circular con:
- `condwidth` = 600 (mm)
- `condheight` = 600 (mm)

El plugin generará un buffer circular con radio de 300mm (0.3m).

## Campos de Salida

El plugin añade los siguientes campos a la capa de salida:

- `TIPO_SECC`: Tipo de sección ("Circular" o "Rectangular")
- `ANCHO_MM`: Ancho en milímetros
- `ALTO_MM`: Alto/diámetro en milímetros
- `DIM_M`: Dimensión principal en metros
- `BUFFER_M`: Radio del buffer aplicado en metros
- `LONG_M`: Longitud del conducto en metros
- `AREA_M2`: Área del buffer en metros cuadrados
- `DESCRIPCION`: Descripción legible (ej: "Ø 600 mm" o "1800 x 600 mm")

## Casos de Uso

- Visualización de redes de alcantarillado
- Análisis de redes de agua potable
- Planificación de excavaciones
- Cálculo de áreas de afectación
- Modelado hidráulico de redes de drenaje

## Requisitos

- QGIS 3.0 o superior
- Python 3.6 o superior

## Autor

**Michel Cueva & DTC**  
**EPA - Escuela Peruana del Agua**
- Empresa especializada en geomática, modelado hidráulico y diseño CAD
- Lima, Perú

## Licencia

Este plugin es de código abierto y está disponible bajo licencia GPL v3.

## Soporte

Para reportar problemas o solicitar nuevas características, por favor contacta a epacursos@epa-edu.com

## Changelog

### Versión 1.0 (2026-01-27)
- Primera versión pública
- Generación de buffers dinámicos
- Detección automática de tipo de sección
- Soporte para mm y metros
- Factor de ajuste de buffer
- Campos calculados de estadísticas
