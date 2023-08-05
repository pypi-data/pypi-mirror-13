from __future__ import absolute_import
from bd2k.util import sync_memoize


class InnerClass( object ):
    """
    Note that this is EXPERIMENTAL code.

    A nested class (the inner class) decorated with this will have an additional attribute called
    'outer' referencing the instance of the nesting class (the outer class) that was used to
    create the inner class. The outer instance does not need to be passed to the inner class's
    constructor, it will be set magically. Shamelessly stolen from

    http://stackoverflow.com/questions/2278426/inner-classes-how-can-i-get-the-outer-class-object-at-construction-time#answer-2278595.

    with names made more descriptive (I hope) and added caching of the BoundInner classes.

    Caveat: Within the inner class, self.__class__ will not be the inner class but a dynamically
    created subclass thereof. It's name will be the same as that of the inner class,
    but its __module__ will be different. There will be one such dynamic subclass per inner class
    and instance of outer class, if that outer class instance created any instances of inner the
    class.

    >>> class Outer(object):
    ...     def new_inner(self):
    ...         # self is an instance of the outer class
    ...         inner = self.Inner()
    ...         # the inner instance's 'outer' attribute is set to the outer instance
    ...         assert inner.outer is self
    ...         return inner
    ...     @InnerClass
    ...     class Inner(object):
    ...         def get_outer(self):
    ...             return self.outer
    ...         @classmethod
    ...         def new_inner(cls):
    ...             return cls()
    >>> o = Outer()
    >>> i = o.new_inner()
    >>> i # doctest: +ELLIPSIS
    <bd2k.util.objects.Inner object at ...> bound to <bd2k.util.objects.Outer object at ...>

    >>> i.get_outer() # doctest: +ELLIPSIS
    <bd2k.util.objects.Outer object at ...>

    Now with inheritance for both inner and outer:

    >>> class DerivedOuter(Outer):
    ...     def new_inner(self):
    ...         return self.DerivedInner()
    ...     @InnerClass
    ...     class DerivedInner(Outer.Inner):
    ...         def get_outer(self):
    ...             assert super( DerivedOuter.DerivedInner, self ).get_outer() == self.outer
    ...             return self.outer
    >>> derived_outer = DerivedOuter()
    >>> derived_inner = derived_outer.new_inner()
    >>> derived_inner # doctest: +ELLIPSIS
    <bd2k.util.objects.DerivedInner object at ...> bound to <bd2k.util.objects.DerivedOuter object at ...>

    >>> derived_inner.get_outer() # doctest: +ELLIPSIS
    <bd2k.util.objects.DerivedOuter object at ...>

    Test a static references:
    >>> Outer.Inner
    <class 'bd2k.util.objects.Inner'>
    >>> DerivedOuter.Inner
    <class 'bd2k.util.objects.Inner'>
    >>> DerivedOuter.DerivedInner
    <class 'bd2k.util.objects.DerivedInner'>

    Can't decorate top-level classes. Unfortunately, this is detected when the instance is
    created, not when the class is defined.
    >>> @InnerClass
    ... class Foo(object):
    ...    pass
    >>> Foo()
    Traceback (most recent call last):
    ...
    RuntimeError: Inner classes must be nested in another class.

    All inner instances should refer to a single outer instance:
    >>> o = Outer()
    >>> o.new_inner().outer == o == o.new_inner().outer
    True

    All inner instances should be of the same class ...
    >>> o.new_inner().__class__ == o.new_inner().__class__
    True

    ... but that class isn't the inner class ...
    >>> o.new_inner().__class__ != Outer.Inner
    True

    ... but a subclass of the inner class.
    >>> isinstance( o.new_inner(), Outer.Inner )
    True

    Static and class methods, e.g. should work, too

    >>> o.Inner.new_inner().outer == o
    True
    """

    def __init__( self, inner_class ):
        super( InnerClass, self ).__init__( )
        self.inner_class = inner_class

    # noinspection PyUnusedLocal
    def __get__( self, instance, owner ):
        # No need to wrap a static reference, i.e one that is made via 'Outer.' rather than 'self.'
        if instance is None:
            return self.inner_class
        else:
            return self._bind( instance )

    @sync_memoize
    def _bind( self, _outer ):
        class BoundInner( self.inner_class ):
            outer = _outer

            def __repr__( self ):
                return "%s bound to %s" % (super( BoundInner, self ).__repr__( ), repr( _outer ))

        BoundInner.__name__ = self.inner_class.__name__
        return BoundInner

    def __call__( *args, **kwargs ):
        raise RuntimeError( "Inner classes must be nested in another class." )
