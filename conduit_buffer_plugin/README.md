# Variable-width-buffer Plugin for QGIS

QGIS plugin to generate dynamic buffers around hydraulic network conduits based on their dimensions (width/diameter). It also allows you to export 3D faces for Civil 3D.

## Features

- ✅ Generates dynamic buffers based on the real dimensions of each conduit
- ✅ Automatically detects if the conduit is circular or rectangular
- ✅ Supports dimensions in millimeters or meters
- ✅ Calculates buffer radius as half the width/diameter
- ✅ Generates wall and excavation polygons with configurable widths
- ✅ Optional 3D DXF export with 3DFACE entities for Civil 3D
- ✅ Integrated in the QGIS Processing panel

## Installation

### Method 1: Manual Installation

1. Download the plugin folder (`conduit_buffer_plugin`)
2. Copy the full folder to your QGIS plugins directory:
   - **Windows**: `C:\Users\[username]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
3. Open QGIS
4. Go to **Plugins → Manage and Install Plugins**
5. In the **Installed** tab, find "Variable-width-buffer"
6. Enable the plugin by checking the box

### Method 2: Install from ZIP

1. Compress the `conduit_buffer_plugin` folder into a ZIP file
2. In QGIS, go to **Plugins → Manage and Install Plugins**
3. Select **Install from ZIP**
4. Select the downloaded ZIP file
5. Click **Install plugin**

## Usage

### From the Processing Panel

1. Open the **Processing Toolbox** (Processing → Toolbox)
2. Expand the **Hydraulics** group
3. Double click on **Variable Width Buffer**

### Parameters

- **Input conduit layer**: Select your line layer with the conduits
- **Width field (condwidth)**: Field that contains the conduit width
- **Dimension unit**: Select whether your data is in millimeters or meters
- **Wall thickness**: Wall thickness in meters (default: 0.15 m)
- **Excavation width**: Excavation width in meters (default: 0.5 m)
- **Export 3D DXF**: Enable to export 3DFACE entities for Civil 3D
- **Output folder for DXF**: Select the destination folder for the DXF file

### Example

If you have InfoWorks conduits with:
- `condwidth` = 600 mm, `condheight` = 600 mm → **Circular**, buffer radius = 300 mm (0.3 m)
- `condwidth` = 1800 mm, `condheight` = 600 mm → **Rectangular**, buffer radius = 900 mm (0.9 m)

## Output Layers

The plugin generates 4 output layers:

| Layer | Description | Fields |
|-------|-------------|--------|
| **Conduits** | Polygon buffers around each conduit | id, tipo_secc, ancho_mm, alto_mm, diam_mm, longitud_m |
| **Walls** | Wall polygons from conduit edge outward | id, espesor_m |
| **Excavation** | Excavation buffers with hole | id, ancho_m |
| **Total Width** | Complete solid polygon (no hole) | id, ancho_total_m |

And optionally a DXF file (`conduits_3d.dxf`) with 3DFACE entities.

## DXF Export — Civil 3D Workflow

1. Open the exported `conduits_3d.dxf` in Civil 3D
2. **ConvertToSurface** - convert 3D faces to surfaces
3. **Thicken** - add thickness to create 3D Solid

The DXF contains two layers:
- `CONDUITS_CIRCULAR` (color: red) - circular conduits as 16-segment cylinders
- `CONDUITS_RECTANGULAR` (color: green) - rectangular conduits as triangulated boxes

Z coordinates are interpolated along each conduit using `us_invert` and `ds_invert` values.

## Use Cases

- Visualization of sewage networks
- Water supply network analysis
- Excavation planning
- Impact area calculation
- Hydraulic modeling of drainage networks

## Requirements

- QGIS 3.0 or higher
- Python 3.6 or higher

## Author

**Michel Cueva & DTC**  
**EPA - Escuela Peruana del Agua**
epacursos@epa-edu.com

## License

This plugin is open source and available under the GPL v3 license.

## Support

To report issues or request new features, please contact epacursos@epa-edu.com

## Changelog

### Version 2.0 (2026-02-03)
- Added 3D DXF export with 3DFACE entities
- Added wall and excavation polygon outputs
- Added ConvertToSurface → Thicken workflow for Civil 3D
- Native DXF R12 writing (no external dependencies)

### Version 1.0 (2026-01-27)
- First public version
- Dynamic buffer generation
- Automatic section type detection
- Support for mm and meters
