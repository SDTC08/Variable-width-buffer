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
3. Open the **Dynamic Conduit Buffer** tool from Processing Toolbox
4. Configure parameters:
   - **Input conduit layer**: Conduit
   - **Width field**: condwidth
   - **Dimension unit**: Millimeters (mm)
   - **Wall thickness**: 0.15 m
   - **Excavation width**: 0.5 m
5. Run the tool

The plugin will generate 4 output layers:
- Conduits (polygon buffers)
- Walls (wall polygons)
- Excavation (excavation buffers with hole)
- Total Width (complete solid polygon)

## Data Source

Sample data from InfoWorks ICM Ultimate export.
Coordinate System: WGS 84 / UTM Zone 17S (EPSG:32717)
