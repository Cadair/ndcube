import weakref

__all__ = ["NDCubeLinkedDescriptor", "ParentCubeAccessor"]


class NDCubeLinkedDescriptor:
    """
    A descriptor which gives the property a reference to the cube to which it is attached.
    """

    def __init__(self, default_type):
        self._default_type = default_type
        self._property_name = None

    def __set_name__(self, owner, name):
        """
        This function is called when the class the descriptor is attached to is initialized.

        The *class* and not the instance.
        """
        # property name is the name of the attribute on the parent class
        # pointing at an instance of this descriptor.
        self._property_name = name
        # attribute name is the name of the attribute on the parent class where
        # the data is stored.
        self._attribute_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return None

        if getattr(obj, self._attribute_name, None) is None and self._default_type is not None:
            self.__set__(obj, self._default_type)

        return getattr(obj, self._attribute_name)

    def __set__(self, obj, value):
        if isinstance(value, self._default_type):
            value._ndcube = weakref.ref(obj)
        elif issubclass(value, self._default_type):
            value = value(ndcube=weakref.ref(obj))
        else:
            raise ValueError(
                f"Unable to set value for {self._property_name} it should "
                f"be an instance or subclass of {self._default_type}")

        setattr(obj, self._attribute_name, value)


class ParentCubeAccessor:
    """
    A mix-in class which resolves the weakref to a parent cube.
    """
    @property
    def _ndcube(self):
        """
        Resolves the weakref to the parent cube.
        """
        return getattr(self, "_ndcube_weakref", lambda: None)()

    @_ndcube.setter
    def _ndcube(self, value):
        if value is not None and not isinstance(value, weakref.ReferenceType):
            value = weakref.ref(value)

        if value is None:
            # A None must be a function to match the weakref
            value = lambda: None  # noqa: E731

        self._ndcube_weakref = value
