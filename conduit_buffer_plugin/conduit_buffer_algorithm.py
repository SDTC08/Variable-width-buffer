"""
Variable Width Buffer
Generates conduit buffers with walls, excavation and 3D DXF export
"""

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingException,
                       QgsFeature,
                       QgsFields,
                       QgsField,
                       QgsWkbTypes,
                       QgsFeatureSink)
import math
import os


class ConduitBufferAlgorithm(QgsProcessingAlgorithm):

    # Parameters
    INPUT = 'INPUT'
    WIDTH_FIELD = 'WIDTH_FIELD'
    DIMENSION_UNIT = 'DIMENSION_UNIT'
    WALL_THICKNESS = 'WALL_THICKNESS'
    EXCAVATION_WIDTH = 'EXCAVATION_WIDTH'
    EXPORT_DXF = 'EXPORT_DXF'
    DXF_FOLDER = 'DXF_FOLDER'

    # Outputs
    OUTPUT_CONDUITS = 'OUTPUT_CONDUITS'
    OUTPUT_WALLS = 'OUTPUT_WALLS'
    OUTPUT_EXCAVATION = 'OUTPUT_EXCAVATION'
    OUTPUT_TOTAL = 'OUTPUT_TOTAL'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ConduitBufferAlgorithm()

    def name(self):
        return 'conduitdynamicbuffer'

    def displayName(self):
        return self.tr('Variable Width Buffer')

    def group(self):
        return self.tr('Hydraulics')

    def groupId(self):
        return 'hydraulics'

    def shortHelpString(self):
        return self.tr("""
        VARIABLE WIDTH BUFFER

        Generates variable width buffers from conduits exported
        from InfoWorks ICM Ultimate. Manually select the field
        from which the buffer is created, including wall
        thicknesses and excavation width. It also allows you to
        create a 3D face.

        DXF Export (Civil 3D):
        1. Open the exported DXF
        2. ConvertToSurface - convert 3D faces to surfaces
        3. Thicken - add thickness to create 3D Solid

        EPA - Escuela Peruana del Agua
        epacursos@epa-edu.com
        """)

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input conduit layer'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.WIDTH_FIELD,
                self.tr('Width field (condwidth)'),
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.DIMENSION_UNIT,
                self.tr('Dimension unit'),
                options=[self.tr('Millimeters (mm)'), self.tr('Meters (m)')],
                defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.WALL_THICKNESS,
                self.tr('Wall thickness (meters)'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.15,
                minValue=0.01,
                maxValue=2.0
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.EXCAVATION_WIDTH,
                self.tr('Excavation width (meters)'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.5,
                minValue=0.1,
                maxValue=5.0
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.EXPORT_DXF,
                self.tr('Export 3D DXF (3DFACE for Civil 3D)'),
                defaultValue=False
            )
        )

        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.DXF_FOLDER,
                self.tr('Output folder for DXF')
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_CONDUITS,
                self.tr('Output conduits')
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_WALLS,
                self.tr('Output walls')
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_EXCAVATION,
                self.tr('Output excavation')
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_TOTAL,
                self.tr('Output total width')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        source = self.parameterAsSource(parameters, self.INPUT, context)
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        width_field = self.parameterAsString(parameters, self.WIDTH_FIELD, context)
        dimension_unit = self.parameterAsEnum(parameters, self.DIMENSION_UNIT, context)
        wall_thickness = self.parameterAsDouble(parameters, self.WALL_THICKNESS, context)
        excavation_width = self.parameterAsDouble(parameters, self.EXCAVATION_WIDTH, context)
        export_dxf = self.parameterAsBool(parameters, self.EXPORT_DXF, context)
        dxf_folder = self.parameterAsString(parameters, self.DXF_FOLDER, context)

        feedback.pushInfo(f'Width field: {width_field}')
        feedback.pushInfo(f'Wall thickness: {wall_thickness}m')
        feedback.pushInfo(f'Excavation width: {excavation_width}m')
        feedback.pushInfo(f'Export DXF: {export_dxf}')

        conversion_factor = 0.001 if dimension_unit == 0 else 1.0
        field_names = [f.name() for f in source.fields()]

        # Sinks
        conduit_fields = QgsFields()
        conduit_fields.append(QgsField('id', QVariant.String, len=50))
        conduit_fields.append(QgsField('tipo_secc', QVariant.String, len=20))
        conduit_fields.append(QgsField('ancho_mm', QVariant.Double))
        conduit_fields.append(QgsField('alto_mm', QVariant.Double))
        conduit_fields.append(QgsField('diam_mm', QVariant.Double))
        conduit_fields.append(QgsField('longitud_m', QVariant.Double))
        (sink_conduits, dest_id_conduits) = self.parameterAsSink(
            parameters, self.OUTPUT_CONDUITS, context,
            conduit_fields, QgsWkbTypes.Polygon, source.sourceCrs())

        wall_fields = QgsFields()
        wall_fields.append(QgsField('id', QVariant.String, len=50))
        wall_fields.append(QgsField('espesor_m', QVariant.Double))
        (sink_walls, dest_id_walls) = self.parameterAsSink(
            parameters, self.OUTPUT_WALLS, context,
            wall_fields, QgsWkbTypes.Polygon, source.sourceCrs())

        excavation_fields = QgsFields()
        excavation_fields.append(QgsField('id', QVariant.String, len=50))
        excavation_fields.append(QgsField('ancho_m', QVariant.Double))
        (sink_excavation, dest_id_excavation) = self.parameterAsSink(
            parameters, self.OUTPUT_EXCAVATION, context,
            excavation_fields, QgsWkbTypes.Polygon, source.sourceCrs())

        total_fields = QgsFields()
        total_fields.append(QgsField('id', QVariant.String, len=50))
        total_fields.append(QgsField('ancho_total_m', QVariant.Double))
        (sink_total, dest_id_total) = self.parameterAsSink(
            parameters, self.OUTPUT_TOTAL, context,
            total_fields, QgsWkbTypes.Polygon, source.sourceCrs())

        dxf_conduits = []
        total = 100.0 / source.featureCount() if source.featureCount() else 0

        for current, feature in enumerate(source.getFeatures()):
            if feedback.isCanceled():
                break

            conduit_id = str(feature['id']) if 'id' in field_names else str(feature.id())

            width = feature[width_field]
            if width is None:
                feedback.reportError(f'Feature {conduit_id}: null width, skipping...')
                continue

            width_mm = width if dimension_unit == 0 else width * 1000

            # condheight: solo para clasificar y para DXF
            condheight_mm = None
            if 'condheight' in field_names:
                ch = feature['condheight']
                if ch is not None:
                    condheight_mm = ch if dimension_unit == 0 else ch * 1000

            if condheight_mm and abs(width_mm - condheight_mm) < 1:
                tipo_seccion = 'Circular'
                ancho_mm, alto_mm, diam_mm = None, None, width_mm
            else:
                tipo_seccion = 'Rectangular'
                ancho_mm, alto_mm, diam_mm = width_mm, condheight_mm, None

            geom = feature.geometry()
            longitud_m = geom.length()
            conduit_radius_m = (width_mm * conversion_factor) / 2.0

            # 1. Conduit buffer
            conduit_buffer = geom.buffer(conduit_radius_m, 25)
            cf = QgsFeature()
            cf.setGeometry(conduit_buffer)
            cf.setAttributes([conduit_id, tipo_seccion, ancho_mm, alto_mm, diam_mm, longitud_m])
            sink_conduits.addFeature(cf, QgsFeatureSink.FastInsert)

            # 2. Walls
            wall_geom = geom.buffer(conduit_radius_m + wall_thickness, 25).difference(conduit_buffer)
            if not wall_geom.isEmpty():
                wf = QgsFeature()
                wf.setGeometry(wall_geom)
                wf.setAttributes([conduit_id, wall_thickness])
                sink_walls.addFeature(wf, QgsFeatureSink.FastInsert)

            # 3. Excavation
            exc_geom = geom.buffer(conduit_radius_m + excavation_width, 25).difference(conduit_buffer)
            if not exc_geom.isEmpty():
                ef = QgsFeature()
                ef.setGeometry(exc_geom)
                ef.setAttributes([conduit_id, excavation_width])
                sink_excavation.addFeature(ef, QgsFeatureSink.FastInsert)

            # 4. Total width
            total_width = conduit_radius_m + excavation_width
            total_buffer = geom.buffer(total_width, 25)
            if not total_buffer.isEmpty():
                tf = QgsFeature()
                tf.setGeometry(total_buffer)
                tf.setAttributes([conduit_id, total_width * 2])
                sink_total.addFeature(tf, QgsFeatureSink.FastInsert)

            # Store for DXF
            if export_dxf:
                us_invert = feature['us_invert'] if 'us_invert' in field_names else 0
                ds_invert = feature['ds_invert'] if 'ds_invert' in field_names else 0
                if geom.isMultipart():
                    for part in geom.asGeometryCollection():
                        coords = list(part.asPolyline())
                else:
                    coords = list(geom.asPolyline())

                dxf_conduits.append({
                    'id': conduit_id,
                    'tipo': tipo_seccion,
                    'width_mm': width_mm,
                    'height_mm': condheight_mm if condheight_mm else width_mm,
                    'us_invert': us_invert,
                    'ds_invert': ds_invert,
                    'coords': coords
                })

            feedback.setProgress(int(current * total))

        # Export DXF
        if export_dxf and dxf_conduits and dxf_folder:
            feedback.pushInfo('=' * 50)
            feedback.pushInfo('Exporting 3D DXF with 3DFACE...')
            try:
                dxf_path = os.path.join(dxf_folder, 'conduits_3d.dxf')
                self._export_3dface_dxf(dxf_conduits, dxf_path, feedback)
                feedback.pushInfo(f'✓ DXF: {dxf_path}')
                feedback.pushInfo('Civil 3D: ConvertToSurface → Thicken')
            except Exception as e:
                feedback.reportError(f'✗ DXF export error: {str(e)}')
            feedback.pushInfo('=' * 50)

        return {
            self.OUTPUT_CONDUITS: dest_id_conduits,
            self.OUTPUT_WALLS: dest_id_walls,
            self.OUTPUT_EXCAVATION: dest_id_excavation,
            self.OUTPUT_TOTAL: dest_id_total
        }

    # ── DXF export ────────────────────────────────────────────────────

    def _write_3dface(self, f, layer, pts, color):
        """Escribe una entidad 3DFACE. pts = 3 o 4 tuplas (x,y,z).
        Si son 3 puntos el 4to se repite como el 3ro (triángulo)."""
        if len(pts) == 3:
            pts = [pts[0], pts[1], pts[2], pts[2]]
        f.write("  0\n3DFACE\n")
        f.write(f"  8\n{layer}\n")
        f.write(f" 62\n{color}\n")
        for code, idx in [(10,0),(11,1),(12,2),(13,3)]:
            f.write(f" {code}\n{pts[idx][0]:.6f}\n")
            f.write(f" {code+10}\n{pts[idx][1]:.6f}\n")
            f.write(f" {code+20}\n{pts[idx][2]:.6f}\n")
        f.write(" 70\n0\n")

    def _export_3dface_dxf(self, conduits, output_path, feedback):
        """Export conduits as 3DFACE — DXF R12 nativo, sin dependencias."""

        circular_count = 0
        rectangular_count = 0

        with open(output_path, 'w') as f:
            # Header R12
            f.write("  0\nSECTION\n  2\nHEADER\n")
            f.write("  9\n$ACADVER\n  1\nAC1009\n")
            f.write("  0\nENDSEC\n")

            # Layers
            f.write("  0\nSECTION\n  2\nTABLES\n")
            f.write("  0\nTABLE\n  2\nLAYER\n 70\n2\n")
            f.write("  0\nLAYER\n  2\nCONDUITS_CIRCULAR\n 70\n0\n 62\n1\n  6\nCONTINUOUS\n")
            f.write("  0\nLAYER\n  2\nCONDUITS_RECTANGULAR\n 70\n0\n 62\n3\n  6\nCONTINUOUS\n")
            f.write("  0\nENDTAB\n")
            f.write("  0\nENDSEC\n")

            # Entities
            f.write("  0\nSECTION\n  2\nENTITIES\n")

            for conduit in conduits:
                width_m = conduit['width_mm'] / 1000.0
                height_m = conduit['height_mm'] / 1000.0
                us_invert = conduit['us_invert']
                ds_invert = conduit['ds_invert']
                coords = conduit['coords']
                is_circular = conduit['tipo'] == 'Circular'
                layer = 'CONDUITS_CIRCULAR' if is_circular else 'CONDUITS_RECTANGULAR'
                color = 1 if is_circular else 3

                # Distancias acumuladas para interpolación Z
                total_length_2d = 0
                cumulative_dist = [0]
                for i in range(len(coords) - 1):
                    d = math.sqrt((coords[i+1].x()-coords[i].x())**2 + (coords[i+1].y()-coords[i].y())**2)
                    total_length_2d += d
                    cumulative_dist.append(cumulative_dist[-1] + d)

                for i in range(len(coords) - 1):
                    x1, y1 = coords[i].x(), coords[i].y()
                    x2, y2 = coords[i+1].x(), coords[i+1].y()

                    ratio_s = cumulative_dist[i] / total_length_2d if total_length_2d > 0 else 0
                    ratio_e = cumulative_dist[i+1] / total_length_2d if total_length_2d > 0 else 0
                    z1 = us_invert + (ds_invert - us_invert) * ratio_s
                    z2 = us_invert + (ds_invert - us_invert) * ratio_e

                    dx, dy = x2 - x1, y2 - y1
                    seg_len = math.sqrt(dx**2 + dy**2)
                    if seg_len == 0:
                        continue
                    perp_x, perp_y = -dy / seg_len, dx / seg_len

                    if is_circular:
                        radius = width_m / 2
                        n = 16
                        s_pts, e_pts = [], []
                        for j in range(n):
                            a = 2 * math.pi * j / n
                            ca, sa = math.cos(a), math.sin(a)
                            s_pts.append((x1 + radius*perp_x*ca, y1 + radius*perp_y*ca, z1 + radius*sa))
                            e_pts.append((x2 + radius*perp_x*ca, y2 + radius*perp_y*ca, z2 + radius*sa))

                        # Laterales
                        for j in range(n):
                            jn = (j+1) % n
                            self._write_3dface(f, layer, [s_pts[j], s_pts[jn], e_pts[jn], e_pts[j]], color)
                        # Tapas (fan triangulation)
                        for j in range(1, n-1):
                            self._write_3dface(f, layer, [s_pts[0], s_pts[j], s_pts[j+1]], color)
                        for j in range(1, n-1):
                            self._write_3dface(f, layer, [e_pts[0], e_pts[j+1], e_pts[j]], color)
                        circular_count += 1

                    else:
                        hw, hh = width_m / 2, height_m / 2
                        v = [
                            (x1+perp_x*hw, y1+perp_y*hw, z1-hh),  # 0
                            (x1-perp_x*hw, y1-perp_y*hw, z1-hh),  # 1
                            (x1-perp_x*hw, y1-perp_y*hw, z1+hh),  # 2
                            (x1+perp_x*hw, y1+perp_y*hw, z1+hh),  # 3
                            (x2+perp_x*hw, y2+perp_y*hw, z2-hh),  # 4
                            (x2-perp_x*hw, y2-perp_y*hw, z2-hh),  # 5
                            (x2-perp_x*hw, y2-perp_y*hw, z2+hh),  # 6
                            (x2+perp_x*hw, y2+perp_y*hw, z2+hh),  # 7
                        ]
                        # 6 caras, cada una dividida en 2 triángulos
                        for t1, t2 in [
                            ([v[0],v[1],v[2]], [v[0],v[2],v[3]]),  # Start
                            ([v[4],v[6],v[5]], [v[4],v[7],v[6]]),  # End
                            ([v[0],v[4],v[5]], [v[0],v[5],v[1]]),  # Bottom
                            ([v[3],v[2],v[6]], [v[3],v[6],v[7]]),  # Top
                            ([v[0],v[3],v[7]], [v[0],v[7],v[4]]),  # Right
                            ([v[1],v[5],v[6]], [v[1],v[6],v[2]]),  # Left
                        ]:
                            self._write_3dface(f, layer, t1, color)
                            self._write_3dface(f, layer, t2, color)
                        rectangular_count += 1

            f.write("  0\nENDSEC\n")
            f.write("  0\nEOF\n")

        feedback.pushInfo(f'  Circular: {circular_count}')
        feedback.pushInfo(f'  Rectangular: {rectangular_count}')
