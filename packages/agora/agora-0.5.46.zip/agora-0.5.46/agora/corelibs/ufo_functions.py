###############################################################################
#
#   Agora Portfolio & Risk Management System
#
#   Copyright 2015 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

from onyx.database.ufo_base import BaseField
from onyx.database.ufo_archivable import Archivable
from onyx.depgraph.graph_api import GraphNodeVt, GetVal

import types

__all__ = [
    "enforce_archivable_entitlements",
    "RetainedFactory",
    "InheritAsProperty",
    "DiscardInheritedAttribute",
]


# -----------------------------------------------------------------------------
def enforce_archivable_entitlements(cls):
    """
    Decorator used to enforce compliance with Archivable entitlements.

    See Database->ArchivedOverwritable
    """
    if not issubclass(cls, Archivable):
        raise ValueError("enforce_archivable_entitlements can "
                         "only be applied to a subclass of Archivable")

    # -------------------------------------------------------------------------
    # override set_dated to enforce compliance with ArchivedOverwritable
    def set_dated(self, attr, date, value):
        overwrite = GetVal("Database", "ArchivedOverwritable")
        self.set_dated_raw(attr, date, value, overwrite)

    # --- rename original set_dated and replace it with a new version
    cls.set_dated_raw = cls.set_dated
    cls.set_dated = set_dated

    return cls


###############################################################################
class MktIndirectionFactory(object):
    """
    ValueType factory that implements a descriptor protocol used for market
    data indirection.

    THIS DECORATOR CAN ONLY BE APPLIED TO METHODS OF A SUBCLASS OF Archivable.

    Typical use is as follows:

        @MktIndirectionFactory(FloatField)
        def MarketizedVt(self, graph): pass

    MarketizedVt is created as a Property ValueType that fetches archived data
    by accessing the corresponding dated record. Consistency with the field
    type is enforced.

    NB: the dated record is fetched referencing the MktDataDate VT of the
        Database object.
    """
    # -------------------------------------------------------------------------
    def __init__(self, field_type):
        if not issubclass(field_type, BaseField):
            raise ValueError("field_type must be an instance of a "
                             "class derived from BaseField. Got {0!s} "
                             "instead".format(field_type.__class__))

        self.field = field_type()

    # -------------------------------------------------------------------------
    def __call__(self, func):
        vt_name = func.__name__

        # --- descriptor protocol: getter
        def getter(instance, graph):
            _, value = instance.get_dated(vt_name,
                                          graph("Database", "MktDataDate"),
                                          graph("Database", "ForceStrict"))
            return value

        getter.__name__ = vt_name

        # --- create a property descriptor ValueType and add the appropriate
        #     field attribute to it
        descriptor = GraphNodeVt("Property")(getter)
        descriptor.field = self.field

        return descriptor


###############################################################################
class RetainedFactory(object):
    """
    Description:
        ValueType factory that implements a descriptor protocol used to
        represent pseudo-attribute VTs, i.e. VTs that can be set but are not
        persisted in database.
    Inputs:
        default - if None use the VT function to calculate the current value,
                  otherwise use default.

    Typical use cases are:
    1) for the implementation of retained properties (such as Spot) where the
       typical syntax is as follows:

           @RetainedFactory()
           def Spot(self, graph):
               ...

    2) for in the implementation of edit screens where the typical
       syntax is as follows:

            @RetainedFactory(default=...)
            def MyVt(self, graph): pass
    """
    # -------------------------------------------------------------------------
    def __init__(self, default=None):
        self.value = default

    # -------------------------------------------------------------------------
    def __call__(self, func):
        def getter(instance, graph):
            if self.value is None:
                return func(instance, graph)
            else:
                return self.value

        def setter(instance, graph, value):
            self.value = value

        # --- return a settable descriptor ValueType
        return GraphNodeVt("Settable", getter, setter)(func)


# -----------------------------------------------------------------------------
class InheritAsProperty(object):
    """
    Description:
        Class decorator
    Inputs:
        attrs      - a list of stored attributes of the super-class that are
                     to be replaced by Property value types.
        value_type - a pointer to the instance of the ufo class from which we
                     are inheriting stored attributes as properties
    """
    template = ("def template(self, graph):\n"
                "    return graph(graph(self, '{0:s}'), '{1:s}')")

    # -------------------------------------------------------------------------
    def __init__(self, attrs, value_type):
        self.attrs = attrs
        self.value_type = value_type

    # -------------------------------------------------------------------------
    def __call__(self, cls):
        for attr in self.attrs:
            # --- discard from set of StoredAttrs attributes (discard does
            #     nothing if cls doesn't have such attribute)
            cls._json_fields.discard(attr)
            cls.StoredAttrs.discard(attr)

            # --- create Property-ValueType
            mod = types.ModuleType("__templates")
            exec(self.template.format(self.value_type, attr), mod.__dict__)
            func = types.FunctionType(mod.template.__code__, {}, name=attr)
            setattr(cls, attr, GraphNodeVt("Property")(func))

        return cls


# -----------------------------------------------------------------------------
class DiscardInheritedAttribute(object):
    """
    Description:
        Class decorator
    Inputs:
        attrs - a list of stored attributes of the super-class that are
                to be discarded.
    """
    # -------------------------------------------------------------------------
    def __init__(self, attrs):
        self.attrs = attrs

    # -------------------------------------------------------------------------
    def __call__(self, cls):
        for attr in self.attrs:
            # --- discard from set of StoredAttrs attributes (discard does
            #     nothing if cls doesn't have such attribute)
            cls._json_fields.discard(attr)
            cls.StoredAttrs.discard(attr)

        return cls
