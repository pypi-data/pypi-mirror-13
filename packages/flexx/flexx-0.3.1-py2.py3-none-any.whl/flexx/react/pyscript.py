"""
Implementation of flexx.react in JS via PyScript.
"""

import json

from ..pyscript import py2js as py2js_, undefined
from ..pyscript.parser2 import get_class_definition

from .signals import Signal, SourceSignal

Object = Date = None  # fool pyflake

reprs = json.dumps


def py2js(*args, **kwargs):
    kwargs['inline_stdlib'] = False
    return py2js_(*args, **kwargs)


class HasSignalsJS:
    """ An implementation of the HasSignals class in PyScript. It has
    some boilerplate code to create signal objects in JavaScript, but
    otherwise shares most of the code with the Python signal classes
    by transpiling their methods via PyScript. This ensures that the
    Python and JS implementation of this reactive programming system
    have the same API and behave the same.
    
    The Python version of this class has a ``JSCODE`` attribute that
    contains the auto-generated JavaScript for this class.
    """
    __signals__ = []
    
    def __init__(self):
        self._create_signals()
        self.connect_signals(False)
    
    def _signal_changed(self, signal):
        pass  # can be overloaded in subclasses
    
    def connect_signals(self, raise_on_fail=True):
        success = True
        for name in self.__signals__:
            if name in self.__props__:
                continue
            s = self[name]
            if s.not_connected:
                connected = s.connect(raise_on_fail)  # dont combine with next line
                success = success and connected
        return success 
    
    def _create_property(self, obj, name, private_name, initial):
        def getter():
            return obj[private_name]
        def setter():
            raise ValueError(name + ' is not settable')
        obj[private_name] = initial
        opts = {'enumerable': True, 'configurable': True,  # i.e. overloadable
                'get': getter, 'set': setter}
        Object.defineProperty(obj, name, opts)
    
    def _create_signals(self):
        self.__props__ = []  # todo: get rid of this?
        for name in self.__signals__:
            func = self['_' + name + '_func']
            func._name = name
            creator = self['_create_' + func._signal_type]
            signal = creator(func, func._upstream)
            signal.flags = func.flags
            signal.signal_type = func._signal_type
            self._create_property(self, name, '_' + name + '_signal', signal)
    
    def _create_PySignal(self, func, upstream, selff):  # proxy for Model
        return self._create_SourceSignal(func, upstream, selff)
    
    def _create_PyInputSignal(self, func, upstream, selff):  # proxy for Model
        return self._create_InputSignal(func, upstream, selff)
        
    def _create_SourceSignal(self, func, upstream, selff):
        
        selff = self._create_Signal(func, upstream, selff)
        
        SourceSignal__update_value_from_py  # noqa
        SourceSignal__set_from_py  # noqa
        
        return selff
    
    def _create_InputSignal(self, func, upstream):
        
        def selff(*args):
            if not len(args):
                return selff._get_value()
            elif len(args) == 1:
                return selff._set(args[0])
            else:
                raise ValueError('Setting input signal %r requires exactly '
                                 'one argument.' % selff._name)
        
        return self._create_SourceSignal(func, upstream, selff)
    
    def _create_LazySignal(self, func, upstream, selff=None):
        selff = self._create_Signal(func, upstream, selff)
        selff._active = False
        return selff
    
    def _create_Signal(self, func, upstream, selff=None):
        # We create the selff function which then serves as the signal object
        # that we populate with attributres, properties and functions.
        obj = self
        
        if selff is None:
            def selff(*args):
                if not len(args):
                    return selff._get_value()
                else:
                    raise RuntimeError('Can only set signal values of InputSignal '
                                       'objects, which signal %r is not.' % selff._name)
        
        # Create public attributes
        self._create_property(selff, 'value', '_value', undefined)
        self._create_property(selff, 'last_value', '_last_value', undefined)
        self._create_property(selff, 'timestamp', '_timestamp', 0)
        self._create_property(selff, 'last_timestamp', '_last_timestamp', 0)
        self._create_property(selff, 'not_connected', '_not_connected', 
                              'No connection attempt yet.')
        #self._create_property(selff, 'name', '_name', func.name)  already is a property
        selff._name = func._name
        
        # Create private attributes
        selff._IS_SIGNAL = True
        selff._active = True
        selff._func = func
        selff._status = 3
        selff._count = 0
        selff._self = obj  # note: not a weakref...
        selff._upstream_given = upstream
        selff._upstream = []
        selff._downstream = []
        selff._upstream_reconnect = []
        selff._downstream_reconnect = []
        
        # Functions that we re-use from the Python implementation of signals
        BaseSignal_connect_from_py  # noqa
        BaseSignal_disconnect_from_py  # noqa
        BaseSignal__subscribe_from_py  # noqa
        BaseSignal__unsubscribe_from_py  # noqa
        BaseSignal__get_value_from_py  # noqa
        BaseSignal__update_value_from_py  # noqa
        BaseSignal__set_status_from_py  # noqa
        BaseSignal__seek_signal_from_py  # noqa
        
        # Some functions need JS specifics
        
        def _resolve_signals():
            selff._upstream = []
            selff._upstream_reconnect = []
            
            for fullname in selff._upstream_given:
                nameparts = fullname.split('.')
                # Obtain first part of path from the frame that we have
                ob = obj[nameparts[0]]
                msg = selff._seek_signal(fullname, nameparts[1:], ob)
                if msg:
                    selff._upstream = []
                    return msg
            
            return False  # no error
        
        def _save_update():
            """
            try {
                selff();
            } catch(err) {
                if (err instanceof Error && err.name === "SignalValueError") {
                } else {throw err;}
            }
            """
        
        def _set_value(value):
            if value is undefined:
                selff._status = 3 if (selff._count == 0) else 0
                return  # new tick, but no update of value
            selff._last_value = selff._value
            selff._value = value
            selff._last_timestamp = selff._timestamp
            selff._count += 1
            selff._timestamp = Date().getTime() / 1000
            selff._status = 0
            obj._signal_changed(selff)
        
        def _call_func(*args):
            return func.apply(obj, args)
        
        # Put functions that we defined here on the signal
        selff._resolve_signals = _resolve_signals
        selff._save_update = _save_update
        selff._set_value = _set_value
        selff._call_func = _call_func
        
        return selff


def patch_HasSignals(jscode):
    """ Insert code from the Python implementation of signals.
    """
    for signal_type, cls in [('BaseSignal', Signal), ('SourceSignal', SourceSignal)]:
        for name in ('connect', 'disconnect', '_subscribe', '_unsubscribe', '_set',
                     '_get_value', '_update_value', '_set_status', '_seek_signal'):
            if name in cls.__dict__:
                code = py2js(cls.__dict__[name], 'selff.' + name, indent=1,
                             docstrings=False)
                template = '%s_%s_from_py;' % (signal_type, name)
                jscode = jscode.replace(template, code.lstrip())
    assert 'from_py' not in jscode
    return jscode

HasSignalsJS.JSCODE = patch_HasSignals(py2js(HasSignalsJS))


def create_js_signals_class(cls, cls_name, base_class='HasSignals.prototype'):
    """ Create the JS equivalent of a subclass of the HasSignals class.
    
    Given a Python class with signals attached to it, this creates the
    code for the JS version of this class. Apart from converting the
    signals, it also supports class constants that are int/float/str,
    or a tuple/list thereof.
    """
    
    assert cls_name != 'HasSignals'  # we need this special class above instead
    
    signals = []
    total_code = []
    funcs_code = []  # functions and signals go below class constants
    err = ('Objects on JS HasSignals classes can only be int, float, str, '
           'or a list/tuple thereof. Not %s -> %r.')
    
    total_code.extend(get_class_definition(cls_name, base_class))
    prefix = '' if cls_name.count('.') else 'var '
    total_code[0] = prefix + total_code[0]
    
    for name, val in sorted(cls.__dict__.items()):
        name = name.replace('_JS__', '_%s__' % cls_name.split('.')[-1])  # fix mangling
        if isinstance(val, Signal):
            signals.append(name)
            funcname = '_' + name + '_func'
            # Add function def
            code = py2js(val._func, cls_name + '.prototype.' + funcname)
            code = code.replace('super()', base_class)  # fix super
            funcs_code.append(code)
            # Mark to not bind the func
            t = '%s.prototype.%s.nobind = true;\n'
            funcs_code.append(t % (cls_name, funcname))
            # Add upstream signal names to the function object
            t = '%s.prototype.%s._upstream = %s;\n'
            funcs_code.append(t % (cls_name, funcname, reprs(val._upstream_given)))
            # Add type of signal too
            t = '%s.prototype.%s._signal_type = %s;\n'
            signal_type = val.__class__.__name__
            funcs_code.append(t % (cls_name, funcname, reprs(signal_type)))
            # Add flags
            t = '%s.prototype.%s.flags = JSON.parse(%s);\n'
            funcs_code.append(t % (cls_name, funcname, reprs(json.dumps(val.flags))))
        elif callable(val):
            code = py2js(val, cls_name + '.prototype.' + name)
            code = code.replace('super()', base_class)  # fix super
            funcs_code.append(code)
        elif name.startswith('__'):
            pass  # we create our own __signals__ list
        else:
            try:
                serialized = json.dumps(val)
            except Exception as err:  # pragma: no cover
                raise ValueError('Attributes on JS HasSignals class must be '
                                 'JSON compatible.\n%s' % str(err))
            total_code.append('%s.prototype.%s = JSON.parse(%s)' %
                              (cls_name, name, reprs(serialized)))
    
    # Insert __signals__ that we found
    if base_class in ('Object', 'HasSignals.prototype'):
        t = '%s.prototype.__signals__ = %s.sort();'
        total_code.append(t % (cls_name, reprs(signals)))
    else:
        t = '%s.prototype.__signals__ = %s.__signals__.concat(%s).sort();'
        total_code.append(t % (cls_name, base_class, reprs(signals)))
    
    total_code.extend(funcs_code)
    return '\n'.join(total_code)
