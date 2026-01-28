"""
Conduit Buffer Algorithm
Generates conduit buffers with walls and excavation
"""

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingException,
                       QgsFeature,
                       QgsFields,
                       QgsField,
                       QgsWkbTypes,
                       QgsFeatureSink)


class ConduitBufferAlgorithm(QgsProcessingAlgorithm):
    """Generates conduit buffers with walls and excavation"""

    # Parameters
    INPUT = 'INPUT'
    WIDTH_FIELD = 'WIDTH_FIELD'
    DIMENSION_UNIT = 'DIMENSION_UNIT'
    WALL_THICKNESS = 'WALL_THICKNESS'
    EXCAVATION_WIDTH = 'EXCAVATION_WIDTH'
    
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
        return self.tr('Dynamic Conduit Buffer')

    def group(self):
        return self.tr('Hydraulics')

    def groupId(self):
        return 'hydraulics'
    
    def shortHelpString(self):
        return self.tr("""
        Dynamic buffers for InfoWorks ICM conduits.
        
        Generates:
        - Conduit polygons (buffer based on width)
        - Wall polygons (from conduit edge outward)
        - Excavation polygons (from conduit edge outward)
        
        Author: Michel Cueva & DTC
        Escuela Peruana del Agua (EPA)
        """)

    def initAlgorithm(self, config=None):
        """Define algorithm parameters"""
        
        # Input layer
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input conduit layer'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        # Width field
        self.addParameter(
            QgsProcessingParameterField(
                self.WIDTH_FIELD,
                self.tr('Width field (select: condwidth)'),
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric
            )
        )

        # Dimension unit
        self.addParameter(
            QgsProcessingParameterEnum(
                self.DIMENSION_UNIT,
                self.tr('Dimension unit'),
                options=[self.tr('Millimeters (mm)'), self.tr('Meters (m)')],
                defaultValue=0
            )
        )

        # Wall thickness
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

        # Excavation width
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

        # Output: Conduits
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_CONDUITS,
                self.tr('Output conduits')
            )
        )

        # Output: Walls
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_WALLS,
                self.tr('Output walls')
            )
        )

        # Output: Excavation
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_EXCAVATION,
                self.tr('Output excavation')
            )
        )

        # Output: Total width
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_TOTAL,
                self.tr('Output total width')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """Execute the algorithm"""
        
        source = self.parameterAsSource(parameters, self.INPUT, context)
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        width_field = self.parameterAsString(parameters, self.WIDTH_FIELD, context)
        dimension_unit = self.parameterAsEnum(parameters, self.DIMENSION_UNIT, context)
        wall_thickness = self.parameterAsDouble(parameters, self.WALL_THICKNESS, context)
        excavation_width = self.parameterAsDouble(parameters, self.EXCAVATION_WIDTH, context)

        # Get condheight field if exists
        field_names = [f.name() for f in source.fields()]
        height_field = None
        for fname in ['condheight', 'height', 'alto']:
            if fname in field_names:
                height_field = fname
                break

        feedback.pushInfo(f'Width field: {width_field}')
        if height_field:
            feedback.pushInfo(f'Height field: {height_field} (auto-detected)')
        feedback.pushInfo(f'Wall thickness: {wall_thickness}m')
        feedback.pushInfo(f'Excavation width: {excavation_width}m')
        
        # Conversion factor to meters
        conversion_factor = 0.001 if dimension_unit == 0 else 1.0

        # ===== PREPARE FIELDS FOR CONDUITS =====
        conduit_fields = QgsFields()
        conduit_fields.append(QgsField('id', QVariant.String, len=50))
        conduit_fields.append(QgsField('tipo_secc', QVariant.String, len=20))
        conduit_fields.append(QgsField('ancho_mm', QVariant.Double))
        conduit_fields.append(QgsField('alto_mm', QVariant.Double))
        conduit_fields.append(QgsField('diam_mm', QVariant.Double))
        conduit_fields.append(QgsField('longitud_m', QVariant.Double))

        (sink_conduits, dest_id_conduits) = self.parameterAsSink(
            parameters,
            self.OUTPUT_CONDUITS,
            context,
            conduit_fields,
            QgsWkbTypes.Polygon,
            source.sourceCrs()
        )

        # ===== PREPARE FIELDS FOR WALLS =====
        wall_fields = QgsFields()
        wall_fields.append(QgsField('id', QVariant.String, len=50))
        wall_fields.append(QgsField('espesor_m', QVariant.Double))
        
        (sink_walls, dest_id_walls) = self.parameterAsSink(
            parameters,
            self.OUTPUT_WALLS,
            context,
            wall_fields,
            QgsWkbTypes.Polygon,
            source.sourceCrs()
        )

        # ===== PREPARE FIELDS FOR EXCAVATION =====
        excavation_fields = QgsFields()
        excavation_fields.append(QgsField('id', QVariant.String, len=50))
        excavation_fields.append(QgsField('ancho_m', QVariant.Double))
        
        (sink_excavation, dest_id_excavation) = self.parameterAsSink(
            parameters,
            self.OUTPUT_EXCAVATION,
            context,
            excavation_fields,
            QgsWkbTypes.Polygon,
            source.sourceCrs()
        )

        # ===== PREPARE FIELDS FOR TOTAL WIDTH =====
        total_fields = QgsFields()
        total_fields.append(QgsField('id', QVariant.String, len=50))
        total_fields.append(QgsField('ancho_total_m', QVariant.Double))
        
        (sink_total, dest_id_total) = self.parameterAsSink(
            parameters,
            self.OUTPUT_TOTAL,
            context,
            total_fields,
            QgsWkbTypes.Polygon,
            source.sourceCrs()
        )

        # ===== PROCESS FEATURES =====
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()

        for current, feature in enumerate(features):
            if feedback.isCanceled():
                break

            # Get ID
            conduit_id = str(feature.id())
            if 'id' in field_names:
                conduit_id = str(feature['id'])

            # Get width
            width = feature[width_field]
            if width is None:
                feedback.reportError(f'Feature {conduit_id}: null width, skipping...')
                continue

            # Get height if exists
            height = None
            if height_field:
                height = feature[height_field]

            # Convert to mm
            width_mm = width if dimension_unit == 0 else width * 1000
            height_mm = height if (height is not None and dimension_unit == 0) else (height * 1000 if height else None)

            # Determine section type
            if height_mm and abs(width_mm - height_mm) < 1:
                tipo_seccion = 'Circular'
                ancho_mm = None
                alto_mm = None
                diam_mm = height_mm
            else:
                tipo_seccion = 'Rectangular'
                ancho_mm = width_mm
                alto_mm = height_mm
                diam_mm = None

            # Get geometry
            geom = feature.geometry()
            longitud_m = geom.length()

            # Conduit radius in meters (width/2)
            conduit_radius_m = (width_mm * conversion_factor) / 2.0

            # ===== 1. CREATE CONDUIT BUFFER =====
            conduit_buffer = geom.buffer(conduit_radius_m, 25)
            
            conduit_feature = QgsFeature()
            conduit_feature.setGeometry(conduit_buffer)
            conduit_feature.setAttributes([
                conduit_id,
                tipo_seccion,
                ancho_mm,
                alto_mm,
                diam_mm,
                longitud_m
            ])
            sink_conduits.addFeature(conduit_feature, QgsFeatureSink.FastInsert)

            # ===== 2. CREATE WALLS (from conduit edge outward) =====
            wall_outer_buffer = geom.buffer(conduit_radius_m + wall_thickness, 25)
            wall_geom = wall_outer_buffer.difference(conduit_buffer)
            
            if not wall_geom.isEmpty():
                wall_feature = QgsFeature()
                wall_feature.setGeometry(wall_geom)
                wall_feature.setAttributes([conduit_id, wall_thickness])
                sink_walls.addFeature(wall_feature, QgsFeatureSink.FastInsert)

            # ===== 3. CREATE EXCAVATION (from conduit edge outward) =====
            excavation_outer_buffer = geom.buffer(conduit_radius_m + excavation_width, 25)
            excavation_geom = excavation_outer_buffer.difference(conduit_buffer)
            
            if not excavation_geom.isEmpty():
                excavation_feature = QgsFeature()
                excavation_feature.setGeometry(excavation_geom)
                excavation_feature.setAttributes([conduit_id, excavation_width])
                sink_excavation.addFeature(excavation_feature, QgsFeatureSink.FastInsert)

            # ===== 4. CREATE TOTAL WIDTH (solid polygon - no hole) =====
            total_width = conduit_radius_m + excavation_width
            total_buffer = geom.buffer(total_width, 25)
            
            if not total_buffer.isEmpty():
                total_feature = QgsFeature()
                total_feature.setGeometry(total_buffer)
                total_feature.setAttributes([conduit_id, total_width * 2])  # diameter
                sink_total.addFeature(total_feature, QgsFeatureSink.FastInsert)

            feedback.setProgress(int(current * total))

        # Return results
        return {
            self.OUTPUT_CONDUITS: dest_id_conduits,
            self.OUTPUT_WALLS: dest_id_walls,
            self.OUTPUT_EXCAVATION: dest_id_excavation,
            self.OUTPUT_TOTAL: dest_id_total
        }
