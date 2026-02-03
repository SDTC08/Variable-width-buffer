"""
Variable Width Buffer Plugin
"""

def classFactory(iface):
    from .conduit_buffer_plugin import ConduitBufferPlugin
    return ConduitBufferPlugin(iface)
