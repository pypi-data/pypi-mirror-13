from zope.schema.interfaces import IObject, ICollection
from plone.registry.recordsproxy import RecordsProxy

_marker = object()

class ComplexRecordsProxy(RecordsProxy):

    def __getattr__(self, name):
        reg = self.__registry__
        if name not in self.__schema__:
            raise AttributeError(name)
        field = self.__schema__.get(name)
        if IObject.providedBy(field):
            iface = field.schema
            collection = reg.collectionOfInterface(
                            iface,
                            check=False,
                            factory=ComplexRecordsProxy)
            if collection.has_key(name):
                value = collection[name]
            else:
                value = _marker
        elif ICollection.providedBy(field) and \
                IObject.providedBy(field.value_type):
            iface = field.value_type.schema
            coll_prefix = iface.__identifier__ + '.' + name
            collection = reg.collectionOfInterface(
                            iface,
                            check=False,
                            prefix=coll_prefix,
                            factory=ComplexRecordsProxy)
            value = collection.values()
            if not value:
                value = _marker
        else:
            value = reg.get(self.__prefix__ + name, _marker)
        if value is _marker:
            value = self.__schema__[name].missing_value
        return value

    def __setattr__(self, name, value):
        if name in self.__schema__:
            reg = self.__registry__
            field = self.__schema__.get(name)
            if IObject.providedBy(field):
                iface = field.schema
                collection = reg.collectionOfInterface(
                                iface,
                                check=False,
                                factory=ComplexRecordsProxy)
                collection[name] = value
            elif ICollection.providedBy(field) and \
                    IObject.providedBy(field.value_type):
                iface = field.value_type.schema
                # All tuple items are stored as records under
                # the coll_prefix prefix:
                coll_prefix = iface.__identifier__ + '.' + name
                collection = reg.collectionOfInterface(
                                iface,
                                check=False,
                                prefix=coll_prefix,
                                factory=ComplexRecordsProxy)
                # Clear collection before adding/updating in case of deletes.
                collection.clear()
                for idx, val in enumerate(value):
                    # val is our obj created by the z3cform factory
                    collection['r' + str(idx)] = val
            else:
                full_name = self.__prefix__ + name
                if full_name not in reg:
                    raise AttributeError(name)
                reg[full_name] = value
        else:
            self.__dict__[name] = value
