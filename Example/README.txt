# Example Data

This folder contains sample InfoWorks ICM conduit data for testing the plugin.

## Files

- **Conduit.shp** - Sample conduit network shapefile
- **Conduit.dbf** - Attribute data
- **Conduit.shx** - Shape index
- **Conduit.prj** - Projection information

## Usage

1. Open QGIS
2. Load the `Conduit.shp` layer
3. Open the **Variable-width-buffer** tool from Processing Toolbox → Hydraulics
4. Configure parameters:
   - **Input conduit layer**: Conduit
   - **Width field**: condwidth
   - **Dimension unit**: Millimeters (mm)
   - **Wall thickness**: 0.15 m
   - **Excavation width**: 0.5 m
   - **Export 3D DXF**: Enable if you need the 3DFACE export for Civil 3D
   - **Output folder for DXF**: Select the destination folder
5. Run the tool

The plugin will generate 4 output layers:
- Conduits (polygon buffers)
- Walls (wall polygons)
- Excavation (excavation buffers with hole)
- Total Width (complete solid polygon)

And optionally a DXF file (`conduits_3d.dxf`) with 3DFACE entities.

## DXF Export — Civil 3D Workflow

1. Open the exported `conduits_3d.dxf` in Civil 3D
2. **ConvertToSurface** - convert 3D faces to surfaces
3. **Thicken** - add thickness to create 3D Solid

## Data Source

Sample data from InfoWorks ICM Ultimate export.
Coordinate System: WGS 84 / UTM Zone 17S (EPSG:32717)

---
EPA - Escuela Peruana del Agua
epacursos@epa-edu.com
