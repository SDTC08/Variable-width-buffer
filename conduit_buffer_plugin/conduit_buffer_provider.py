"""
Processing Provider for Conduit Buffer Plugin
"""

from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon
import os

from .conduit_buffer_algorithm import ConduitBufferAlgorithm


class ConduitBufferProvider(QgsProcessingProvider):
    """Processing Provider for Conduit Dynamic Buffer"""

    def __init__(self):
        QgsProcessingProvider.__init__(self)

    def loadAlgorithms(self):
        """Load all algorithms belonging to this provider."""
        self.addAlgorithm(ConduitBufferAlgorithm())

    def id(self):
        """Return the unique provider id"""
        return 'conduitbuffer'

    def name(self):
        """Return the provider name"""
        return 'Conduit Buffer'

    def longName(self):
        """Return the full provider name"""
        return 'Conduit Dynamic Buffer'

    def icon(self):
        """Return the provider icon"""
        return QgsProcessingProvider.icon(self)
