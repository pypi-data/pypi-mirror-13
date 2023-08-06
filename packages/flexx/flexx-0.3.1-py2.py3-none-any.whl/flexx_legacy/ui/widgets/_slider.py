# -*- coding: utf-8 -*-
"""

Simple example:

.. UIExample:: 50

    s = ui.Slider(min=10, max=20, value=12)


Interactive example:

.. UIExample:: 100

    from flexx import app, ui, react
    
    class Example(ui.Widget):
    
        def init(self):
            with ui.HBox():
                self.slider = ui.Slider(flex=0, min=1, max=20, step=1)
                self.label = ui.Label(flex=1)
        
        class JS:
            @react.connect('slider.value')
            def _change_label(self, value):
                self.label.text('x'.repeat(value))
"""

from __future__ import print_function, absolute_import, with_statement, unicode_literals, division

from ...pyscript import undefined, window
from ... import react
from . import Widget


#todo: implement this in a way so it looks/behaves the same everywhere.

class Slider(Widget):
    """ An input widget to select a value in a certain range (aka HTML
    range input).
    """
    
    CSS = ".flx-Slider {min-height: 30px;}"
    
    @react.input
    def value(v=0):
        """ The current slider value (settable)."""
        return float(v)
    
    @react.input
    def step(v=0.01):
        """ The step size for the slider."""
        return float(v)
    
    @react.input
    def min(v=0):
        """ The minimal slider value."""
        return float(v)
    
    @react.input
    def max(v=1):
        """ The maximum slider value."""
        return float(v)
    
    class JS(object):
    
        def _create_node(self):
            self.p = window.phosphor.createWidget('input')
            self.p.node.type = 'range'
            f = lambda ev: self.user_value._set(self.node.value)
            self.p.node.addEventListener('input', f, False)
            #if IE10:
            #   this.node.addEventListener('change', f, False)
            
        @react.source
        def user_value(self, v):
            """ The slider value set by the user (updates on user interaction). """
            if v is not undefined:
                v = float(v)
                self.value(v)
            return v
        
        @react.connect('value')
        def _value_changed(self, value):
            self.node.value = value
        
        @react.connect('step')
        def _step_changed(self, step):
            self.node.step= step
        
        @react.connect('min')
        def _min_changed(self, min_value):
            self.node.min = min_value
        
        @react.connect('max')
        def _max_changed(self, max_value):
            self.node.max = max_value
