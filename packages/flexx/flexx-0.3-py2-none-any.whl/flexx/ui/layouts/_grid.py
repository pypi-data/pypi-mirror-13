# -*- coding: utf-8 -*-
"""
The GridPanel is deprecated for the time being.

"""
from __future__ import print_function, absolute_import, with_statement, unicode_literals, division

"""
.. UIExample:: 250
    
    from flexx import ui
    
    class Example(ui.Widget):
        def init(self):
            with ui.GridPanel(spacing=12):
                with ui.GridPanel(pos=(0, 0)):
                    # Show min-width in action
                    self.a = ui.Widget(style='background:#a00;', pos=(0, 0), flex=1)
                    self.b = ui.Widget(style='background:#0a0;', pos=(1, 0))
                    self.c = ui.Widget(style='background:#00a; min-width:50px; ' +
                                       'min-height:50px;', pos=(1, 1))
                with ui.GridPanel(pos=(1, 0)):
                    # Show max-width in action
                    self.a = ui.Widget(style='background:#a00;', pos=(0, 0))
                    self.b = ui.Widget(style='background:#0a0;', pos=(1, 0))
                    self.c = ui.Widget(style='background:#00a; max-width:50px; ' +
                                       'max-height:50px', pos=(1, 1))
                with ui.GridPanel(pos=(0, 1)):
                    # Flex
                    self.a = ui.Widget(style='background:#a00;', pos=(0, 0), flex=1)
                    self.b = ui.Widget(style='background:#0a0;', pos=(1, 0), flex=1)
                    self.c = ui.Widget(style='background:#00a;', pos=(1, 1), flex=2)
                with ui.GridPanel(pos=(1, 1)):
                    # Base size
                    self.a = ui.Widget(style='background:#a00;', pos=(0, 0))
                    self.b = ui.Widget(style='background:#0a0;', pos=(1, 0))
                    self.c = ui.Widget(style='background:#00a;', pos=(1, 1),
                                       size=(100, 100))
"""

from ... import react
from ...pyscript import window, Infinity
from . import Layout
from ._form import BaseTableLayout


class GridPanel(Layout):
    """ A panel which lays out its children in a grid. 
    
    NOTE: the GridPanel is temporarily deprecated until the Phosphorjs
    GridPanel is fixed.
    
    The "pos" signal of each child represents its integer position/index
    in the grid.
    
    For each column and each row, it looks at its children and selects
    the maximum flex, min-size and base-size, and the minimum max-size.
    If all flex factors are zero, all columns/rows become of equal size
    (subject to size limits).
    """
    
    def init(self):
        raise NotImplementedError('The GridPanel is (temporarily) deprecated.')
    
    @react.input
    def spacing(v=5):
        """ The space between two child elements. """
        return float(v)
    
    # todo: allow specifying flex, minSize etc. using an array of dicts?
    # @react.input
    # def col_specs(v=None):
    #     """ The specification for the columns. If None, uses the 
    #     """
    #     return v
    
    class JS(object):
        
        def _init(self):
            super(JS, self)._init()
            
            that = self
            class LayoutNotifier(object):
                def filterMessage(handler, msg):
                    if msg._type == 'layout-request':
                        that._child_limits_changed()
                    return False
            window.phosphor.messaging.installMessageFilter(self.p, LayoutNotifier())
        
        def _create_node(self):
            self.p = window.phosphor.gridpanel.GridPanel()
        
        @react.connect('children.*.pos', 'children.*.flex', 'children.*.size')
        def __update_positions(self):
            self._child_limits_changed()
        
        def _child_limits_changed(self):
            # Set position of all children and get how large our grid is
            max_row, max_col = 0, 0
            for child in self.children():
                x, y = child.pos()
                window.phosphor.gridpanel.GridPanel.setColumn(child.p, x)
                window.phosphor.gridpanel.GridPanel.setRow(child.p, y)
                max_col = max(max_col, x)
                max_row = max(max_row, y)
            
            # Collect specs from all children
            colSpecs = [{'stretch': 0, 'minSize': 0, 'maxSize': Infinity,
                         'sizeBasis': 0} for i in xrange(max_col+1)]
            rowSpecs = [{'stretch': 0, 'minSize': 0, 'maxSize': Infinity,
                         'sizeBasis': 0} for i in xrange(max_row+1)]
            for child in self.children():
                x, y = child.pos()
                limits = child.p.sizeLimits
                colSpecs[x].minSize = max(colSpecs[x].minSize, limits.minWidth)
                colSpecs[x].maxSize = min(colSpecs[x].maxSize, limits.maxWidth)
                colSpecs[x].sizeBasis = max(colSpecs[x].sizeBasis, child.size()[0])
                colSpecs[x].stretch = max(colSpecs[x].stretch, child.flex()[0])
                
                rowSpecs[y].minSize = max(rowSpecs[y].minSize, limits.minHeight)
                rowSpecs[y].maxSize = min(rowSpecs[y].maxSize, limits.maxHeight)
                rowSpecs[y].sizeBasis = max(rowSpecs[y].sizeBasis, child.size()[1])
                rowSpecs[y].stretch = max(rowSpecs[y].stretch, child.flex()[1])
            
            # Assign
            self.p._columnSpecs = colSpecs
            self.p._rowSpecs = rowSpecs
            Spec = window.phosphor.gridpanel.Spec
            self.p.columnSpecs = [Spec(i) for i in colSpecs]
            self.p.rowSpecs = [Spec(i) for i in rowSpecs]
        
        @react.connect('spacing')
        def __spacing_changed(self, spacing):
            self.p.rowSpacing = spacing
            self.p.columnSpacing = spacing


class GridLayout(BaseTableLayout):  # note the othe GridLayout!
    """ Not implemented yet. 
    """
    def init(self):
        raise NotImplementedError()
