# Conduit Dynamic Buffer Plugin for QGIS

QGIS plugin for generating variable width buffers from hydraulic network conduits exported from InfoWorks ICM Ultimate.

![EPA Logo](conduit_buffer_plugin/icon.png)

## Features

- ✅ Generates variable width buffers based on actual conduit dimensions
- ✅ Automatically detects circular vs rectangular sections
- ✅ Supports dimensions in millimeters or meters
- ✅ Generates 4 output layers:
  - **Conduits**: Polygon buffers of the conduit
  - **Walls**: Wall polygons from conduit edge outward
  - **Excavation**: Excavation buffers from conduit edge (with hole)
  - **Total Width**: Complete solid polygon (no hole)
- ✅ Adds fields with section type, dimensions, length and area information
- ✅ Integrated into QGIS Processing panel

## Installation

### Method 1: Manual Installation

1. Download the plugin (`conduit_buffer_plugin` folder)
2. Copy the complete folder to your QGIS plugins directory:
   - **Windows**: `C:\Users\[username]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`

3. Open QGIS
4. Go to **Plugins → Manage and Install Plugins**
5. In the **Installed** tab, search for "Conduit Dynamic Buffer"
6. Activate the plugin by checking the box

### Method 2: Install from ZIP

1. Compress the `conduit_buffer_plugin` folder into a ZIP file
2. In QGIS, go to **Plugins → Manage and Install Plugins**
3. Select **Install from ZIP**
4. Select the downloaded ZIP file
5. Click **Install Plugin**

## Usage

### From Processing Panel

1. Open the **Processing Panel** (Processing → Toolbox)
2. Search for **"Conduit Buffer"** or **"Dynamic Conduit Buffer"**
3. Expand the **Hydraulics** group
4. Double click on **Dynamic Conduit Buffer**

### Parameters

- **Input conduit layer**: Select your line layer with conduits
- **Width field**: Field containing conduit width (select `condwidth`)
- **Dimension unit**: Select if your data is in millimeters or meters
- **Wall thickness**: Wall thickness in meters (default: 0.15m)
- **Excavation width**: Excavation width in meters (default: 0.5m)

### Example

If you have InfoWorks conduits with:
- `condwidth` = 1800 (mm)
- `condheight` = 600 (mm)

The plugin will generate:
- **Conduit**: 1.8m wide polygon
- **Walls**: 0.15m thick on each side
- **Excavation**: 0.5m wide from conduit edge
- **Total Width**: Complete solid polygon

If the conduit is circular with:
- `condwidth` = 600 (mm)
- `condheight` = 600 (mm)

The plugin will generate a circular buffer with 0.6m diameter.

## Output Fields

### Conduits Layer
- `id`: Conduit identifier
- `tipo_secc`: Section type ("Circular" or "Rectangular")
- `ancho_mm`: Width in millimeters
- `alto_mm`: Height in millimeters
- `diam_mm`: Diameter in millimeters (for circular sections)
- `longitud_m`: Length in meters

### Walls Layer
- `id`: Conduit identifier
- `espesor_m`: Wall thickness in meters

### Excavation Layer
- `id`: Conduit identifier
- `ancho_m`: Excavation width in meters

### Total Width Layer
- `id`: Conduit identifier
- `ancho_total_m`: Total width in meters

## Use Cases

- Sewer network visualization
- Drinking water network analysis
- Excavation planning
- Impact area calculation
- Hydraulic drainage network modeling

## Requirements

- QGIS 3.0 or higher
- Python 3.6 or higher
- InfoWorks ICM conduit shapefiles

## Author

**Michel Cueva & DTC**  
**Escuela Peruana del Agua (EPA)**  
Lima, Peru

## License

This plugin is open source and available under the MIT License.

## Support

To report issues or request new features, please contact epacursos@epa-edu.com or open an issue on this repository.

## Changelog

### Version 1.0 (2026-01-27)
- Initial public release
- Variable width buffer generation
- Automatic section type detection
- Support for mm and meters
- Wall generation
- Excavation buffer
- Total width output
- Calculated statistics fields
