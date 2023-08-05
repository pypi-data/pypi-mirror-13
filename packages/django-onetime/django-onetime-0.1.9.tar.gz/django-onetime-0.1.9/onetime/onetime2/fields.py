import ast
import sys
import importlib
import uuid

from django.db import models


class UUIDField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 64)
        kwargs['blank'] = True
        models.CharField.__init__(self, *args, **kwargs)

    def pre_save(self, model_instance, is_new):
        if is_new:
            value = str(uuid.uuid4())
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(models.CharField, self).pre_save(model_instance, is_new)


class CallableField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def get_prep_value(self, value):
        """
        Generate the string representation of the callable.
        """
        module_name = value.__module__
        for k, v in sys.modules[module_name].__dict__.iteritems():
            if v is value:
                callable_name = k
                break
        else:
            callable_name = getattr(value, 'func_name', None)
            if callable_name is None:
                callable_name = getattr(value, '__name__', None)
                if callable_name is None:
                    raise ValueError("Cannot determine callable name for object %r" % value)
        return '.'.join((module_name, callable_name))

    def to_python(self, value):
        """
        Retrieve the callable object from the string value.
        """
        if callable(value):
            return value

        if not value:
            return value

        module_name, callable_name = value.rsplit('.', 1)
        module = sys.modules.get(module_name)
        if module is None:
            module = importlib.import_module(module_name)
            # raise ImportError("Cannot find module %s in sys.modules" % module_name)
        callback = getattr(module, callable_name, None)
        if callback is None:
            raise ImportError("Cannot find callable %s in module %s" % (callable_name, module_name))
        if not callable(callback):
            raise TypeError("%r is not callable." % callback)
        return callback


class PythonLiteralField(models.TextField):
    """
    Stores basic Python primitives to the DB.

    Can store numbers, strings, booleans, tuples, lists, dicts.
    """
    __metaclass__ = models.SubfieldBase

    def get_prep_value(self, value):
        return repr(value)

    def to_python(self, value):
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value
            #  raise ValueError("Stored literals cannot contain complex types.  Could not evaluate: %r" % (value,))

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], [
        "^onetime\.fields\.UUIDField",
        "^onetime\.fields\.CallableField",
        "^onetime\.fields\.PythonLiteralField"
    ])
except ImportError:
    pass
