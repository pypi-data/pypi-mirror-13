"""
Implements the data models used throughout the SDK.
"""
import json
from coralogix import CORALOGIX_ENCODING


class Serializable(object):
    "Provides a serialization interface to subclasses."

    def __init__(self, **kwargs):
        """
        Default implementation. Ignores missing attributes and doesn't set any extra attributes (i.e. attributes not in self.__serializable__).
        Can be overridden by subclasses.
        """
        for attr, field in self.__serializable__:
            if attr in kwargs:
                setattr(self, attr, kwargs.pop(attr))

    def serialize(self):
        field_values = {}
        for attr, field in self.__serializable__:
            if field:
                value = getattr(self, attr)
                if isinstance(value, Serializable):
                    value = value.serialize()

                field_values[field] = value
        return field_values

    def tojson(self):
        return json.dumps(self.serialize()).encode(CORALOGIX_ENCODING)

    @classmethod
    def deserialize(cls, fields):
        if not hasattr(cls, '__deserializable__'):
            cls.__deserializable__ = dict([(v, k) for v, k in cls.__serializable__])
            # cls.__deserializable__ = {v: k for k, v in cls.__serializable__}

        init_kwargs = dict([(cls.__deserializable__[field], value) for field, value in fields.items() if field in cls.__deserializable__])
        # init_kwargs = {cls.__deserializable__[field]: value for field, value in fields.items() if field in cls.__deserializable__}
        return cls(**init_kwargs)

    @classmethod
    def fromjson(cls, json_string):
        json_dict = json.loads(json_string.decode(CORALOGIX_ENCODING))
        return cls.deserialize(json_dict)
