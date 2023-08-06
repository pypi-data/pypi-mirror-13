"""
Base class for objects that live in both Python and JS.
This basically implements the syncing of signals.
"""

import weakref
import logging
import json

from .. import react
from ..react.hassignals import HasSignalsMeta, with_metaclass, new_type
from ..react.pyscript import create_js_signals_class, HasSignalsJS
from ..pyscript import py2js, js_rename, window

from .serialize import serializer

reprs = json.dumps

model_classes = []
def get_model_classes():
    """ Get a list of all known Model subclasses.
    """
    return [c for c in HasSignalsMeta.CLASSES if issubclass(c, Model)]


def get_instance_by_id(id):
    """ Get instance of Model class corresponding to the given id,
    or None if it does not exist.
    """
    return Model._instances.get(id, None)


class JSSignal(react.SourceSignal):
    """ A signal that represents a proxy to a signal in JavaScript.
    """
    
    def __init__(self, func_or_name, upstream=[], frame=None, ob=None, doc=None):
        
        def func(v):
            return v
        if doc is not None:
            func.__doc__ = doc
        
        if isinstance(func_or_name, str):
            func.__name__ = func_or_name
        else:
            func.__name__ = func_or_name.__name__
        
        self._linked = False
        react.SourceSignal.__init__(self, func, [], ob=ob)
    
    def _subscribe(self, *args):
        react.SourceSignal._subscribe(self, *args)
        if not self._linked:
            self._self._link_js_signal(self.name)
    
    def _unsubscribe(self, *args):
        react.SourceSignal._unsubscribe(self, *args)
        if self._linked and not self._downstream:
            self._self._link_js_signal(self.name, False)


class PySignal(react.SourceSignal):
    """ A signal in JS that represents a proxy to a signal in Python.
    """
    
    def __init__(self, name):
        
        def func(v):
            return v
        func._name = name
        react.SourceSignal.__init__(self, func, [])


class PyInputSignal(PySignal):
    """ A signal in JS that represents an input signal in Python. On
    the JS side, this can be used as an input too, although there is
    no validation in this case.
    """
    pass


class ModelMeta(HasSignalsMeta):
    """ Meta class for Model
    Set up proxy signals in Py/JS.
    """
 
    def __init__(cls, name, bases, dct):
        HasSignalsMeta.__init__(cls, name, bases, dct)
        
        OK_MAGICS = '__init__', '__json__', '__from_json__'
        
        # Create proxy signals on cls for each signal on JS
        if 'JS' in cls.__dict__:
            for name, val in cls.JS.__dict__.items():
                if isinstance(val, react.Signal) and not isinstance(val, PySignal):
                    if not hasattr(cls, name):
                        cls.__signals__.append(name)
                        setattr(cls, name, JSSignal(name, doc=val._func.__doc__))
                    elif isinstance(getattr(cls, name), (JSSignal, react.InputSignal)):
                        pass  # ok, overloading on JS side, or an input signal
                    else:
                        logging.warn('JS signal %r not proxied, '
                                     'as it would hide a Py attribute.' % name)
        
        # Implicit inheritance for JS "sub"-class
        jsbases = [getattr(b, 'JS') for b in cls.__bases__ if hasattr(b, 'JS')]
        JS = new_type('JS', tuple(jsbases), {})
        for c in (cls, ):  # cls.__bases__ + (cls, ):
            if 'JS' in c.__dict__:
                if '__init__' in c.JS.__dict__:
                    JS.__init__ = c.JS.__init__
                for name, val in c.JS.__dict__.items():
                    if not name.startswith('__'):
                        setattr(JS, name, val)
                    elif name in OK_MAGICS:
                        setattr(JS, name, val)
        cls.JS = JS
        
        # Create proxy signals on cls.JS for each signal on cls
        for name, val in cls.__dict__.items():
            if isinstance(val, react.Signal) and not isinstance(val, JSSignal):
                if not hasattr(cls.JS, name):
                    if isinstance(val, react.InputSignal):
                        setattr(cls.JS, name, PyInputSignal(name))
                    else:
                        setattr(cls.JS, name, PySignal(name))
                elif isinstance(getattr(cls.JS, name), (PySignal, react.InputSignal)):
                    pass  # ok, overloaded signal on JS side
                else:
                    logging.warn('Py signal %r not proxied, '
                                 'as it would hide a JS attribute.' % name)
        
        # Set JS and CSS for this class
        cls.JS.CODE = cls._get_js()
        cls.CSS = cls.__dict__.get('CSS', '')
    
    def _get_js(cls):
        """ Get source code for this class.
        """
        cls_name = 'flexx.classes.' + cls.__name__
        base_class = 'flexx.classes.%s.prototype' % cls.mro()[1].__name__
        code = []
        # Add JS version of HasSignals when this is the Model class
        if cls.mro()[1] is react.HasSignals:
            c = py2js(serializer.__class__, 'flexx.Serializer', inline_stdlib=False)
            code.append(c)
            code.append('flexx.serializer = new flexx.Serializer();')
            c = js_rename(HasSignalsJS.JSCODE, 'HasSignalsJS',
                          'flexx.classes.HasSignals')
            code.append(c)
        # Add this class
        code.append(create_js_signals_class(cls.JS, cls_name, base_class))
        code[-1] += '%s.prototype._class_name = "%s";\n' % (cls_name, cls.__name__)
        if cls.mro()[1] is react.HasSignals:
            code.append('flexx.serializer.add_reviver("Flexx-Model",'
                        ' flexx.classes.Model.prototype.__from_json__);\n')
        return '\n'.join(code)


class Model(with_metaclass(ModelMeta, react.HasSignals)):
    """ Subclass of HasSignals representing Python-JavaScript object models
    
    Each instance of this class has a corresponding object in
    JavaScript, and their signals are synced both ways. Signals defined
    in Python can be connected to from JS, and vice versa.
    
    The JS version of this class is defined by the contained ``JS``
    class. One can define methods, signals, and (json serializable)
    constants on the JS class.
    
    Parameters:
        session (Session, None): the session object that connects this
            instance to a JS client.
        is_app (bool): whether this object is the main app object. Set
            by Flexx internally. Not used by the Model class, but can
            be used by subclasses.
        kwargs: initial signal values (see HasSignals).
    
    Notes:
        This class provides the base object for all widget classes in
        ``flexx.ui``. However, one can also create subclasses that have
        nothing to do with user interfaces or DOM elements. You could e.g.
        use it to calculate pi on nodejs.
    
    Example:
    
        .. code-block:: py
        
            class MyModel(Model):
                
                def a_python_method(self):
                ...
                
                class JS:
                    
                    FOO = [1, 2, 3]
                    
                    def a_js_method(this):
                        ...
    """
    
    # Keep track of all instances, so we can easily collect al JS/CSS
    _instances = weakref.WeakValueDictionary()
    
    # Count instances to give each instance a unique id
    _counter = 0
    
    # CSS for this class (no css in the base class)
    CSS = ""
    
    def __json__(self):
        return {'__type__': 'Flexx-Model', 'id': self.id}
    
    @staticmethod
    def __from_json__(dct):
        return get_instance_by_id(dct['id'])
    
    def __init__(self, session=None, is_app=False, **kwargs):
        
        # Param "is_app" is not used, but we "take" the argument so it
        # is not mistaken for a signal value.
        
        # Set id and register this instance
        Model._counter += 1
        self._id = self.__class__.__name__ + str(Model._counter)
        Model._instances[self._id] = self
        
        # Flag to implement eventual synchronicity
        self._seid_from_js = 0
        
        # Init session
        if session is None:
            from .session import manager
            session = manager.get_default_session()
        self._session = session
        
        self._session.register_model_class(self.__class__)
        
        # Instantiate JavaScript version of this class
        clsname = 'flexx.classes.' + self.__class__.__name__
        cmd = 'flexx.instances.%s = new %s(%s);' % (self._id, clsname, reprs(self._id))
        self._session._exec(cmd)
        
        self._init()
        
        # Init signals - signals will be connected updated, causing updates
        # on the JS side.
        react.HasSignals.__init__(self, **kwargs)
    
    def _init(self):
        """ Can be overloaded when creating a custom class.
        """
        pass
    
    @property
    def id(self):
        """ The unique id of this Model instance. """
        return self._id
    
    @property
    def session(self):
        """ The session object that connects us to the runtime.
        """
        return self._session
    
    def __setattr__(self, name, value):
        # Sync attributes that are Model instances
        react.HasSignals.__setattr__(self, name, value)
        if isinstance(value, Model):
            txt = serializer.saves(value)
            cmd = 'flexx.instances.%s.%s = flexx.serializer.loads(%s);' % (
                self._id, name, reprs(txt))
            self._session._exec(cmd)
    
    def _set_signal_from_js(self, name, text, esid):
        """ Notes on synchronizing:
        - Py and JS both send updates when a signal changes.
        - JS does not send an update for signal updates received from Py.
        - Py does, to allow eventual synchronicity. Read on.
        - JS sends updates with a nonzero esid (eventual synchronicity
          id) and marks the corresponding signal with the same id.
        - Py sends an update with the esid that it got from JS, or 0
          if the signal originates from Py.
        - When JS receives an update from Py, it checks whether the
          seid is 0 (the signal originates from Py) or if the signal
          seid is 0 (the signal was updated from py since we last
          updated it from JS). If either is 0, it updates the signal
          value, and sets the signal esid to 0.
        """
        signal = getattr(self, name)
        value = serializer.loads(text)
        self._seid_from_js = esid  # to send back to js
        # if isinstance(signal, react.InputSignal) and signal.value == value:
        # #if name in ('parent', 'children') and signal.value == value:
        #     pass  # input signal already has this value
        # else:
        signal._set(value)
    
    def _signal_changed(self, signal):
        # Set esid to 0 if it originates from Py, or to what we got from JS
        esid = self._seid_from_js
        self._seid_from_js = 0
        if not isinstance(signal, JSSignal) and not signal.flags.get('nosync', False):
            #txt = json.dumps(signal.value)
            txt = serializer.saves(signal.value)
            cmd = 'flexx.instances.%s._set_signal_from_py(%s, %s, %s);' % (
                self._id, reprs(signal.name), reprs(txt), reprs(esid))
            self._session._exec(cmd)
    
    def _link_js_signal(self, name, link=True):
        """ Make a link between a JS signal and its proxy in Python.
        This is done when a proxy signal is used as input for a signal
        in Python.
        """
        # if self._session is None:
        #     self._initial_signal_links.discart(name)
        #     if link:
        #         self._initial_signal_links.add(name)
        # else:
        link = 'true' if link else 'false'
        cmd = 'flexx.instances.%s._link_js_signal(%s, %s);' % (self._id,
                                                               reprs(name), link)
        self._session._exec(cmd)
    
    def call_js(self, call):
        cmd = 'flexx.instances.%s.%s;' % (self._id, call)
        self._session._exec(cmd)
    
    
    class JS:
        
        def __json__(self):
            return {'__type__': 'Flexx-Model', 'id': self.id}
        
        def __from_json__(dct):
            return window.flexx.instances[dct.id]
        
        def __init__(self, id):
            # Set id alias. In most browsers this shows up as the first element
            # of the object, which makes it easy to identify objects while
            # debugging. This attribute should *not* be used.
            self.__id = self._id = self.id = id
            
            self._linked_signals = {}  # use a list as a set
            
            # Call _init now. This gives subclasses a chance to init at a time
            # when the id is set, but *before* the signals are connected.
            self._init()
            
            # Call HasSignals __init__, signals will be created and connected.
            # Act signals relying on JS signals will fire. 
            # Act signals relying on Py signals will fire later.
            super().__init__()
        
        def _init(self):
            pass
        
        def _set_signal_from_py(self, name, text, esid):
            value = window.flexx.serializer.loads(text)
            signal = self[name]
            if esid == 0 or signal._esid == 0:
                self._signal_emit_lock = True  # do not send back to py
                signal._set(value)
                signal._esid = 0  # mark signal as updated from py
        
        def _signal_changed(self, signal):
            if window.flexx.ws is None:  # we could be exported or in an nbviewer
                return
            if self._signal_emit_lock:
                self._signal_emit_lock = False
                return
            signal._esid = signal._count  # mark signal as just updated by us
            # todo: what signals do we sync? all but private signals? or only linked?
            # signals like `text` should always sync, signals like a 100Hz
            # timer not, mouse_pos maybe neither unless linked against
            if signal.flags.nosync:
                return
            if signal.signal_type != 'PySignal' and not signal._name.startswith('_'):
                #txt = JSON.stringify(signal.value)
                txt = window.flexx.serializer.saves(signal.value)
                window.flexx.ws.send('SIGNAL ' + [self.id, signal._esid,
                                                  signal._name, txt].join(' '))
        
        def _link_js_signal(self, name, link):
            if link:
                self._linked_signals[name] = True
                signal = self[name]
                if signal._timestamp > 1:
                    self._signal_changed(self[name])
            elif self._linked_signals[name]:
                del self._linked_signals[name]

# Make model objects de-serializable
serializer.add_reviver('Flexx-Model', Model.__from_json__)
