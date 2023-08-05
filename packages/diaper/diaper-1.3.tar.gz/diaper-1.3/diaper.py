"""
Diaper pattern
==============

Returns:
    Result of the function call if no exception is raised.
    Otherwise it returns None.

Usage::

    import diaper

    # call it directly
    diaper(function, *function_args, **function_kwargs)

    # as a context manager
    with diaper:
        do_terrible_things_here()

    # see if the diaper caught anything:
    with diaper:
        raise Exception
    assert diaper.smelly

    # diapers are automatically changed on use
    with diaper:
        pass
    assert not diaper.smelly

    # diapers can be manually changed and (somehow) soiled
    diaper.soil()
    assert diaper.smelly

    diaper.change()
    assert not diaper.smelly

    # diapers can be manipulated in the context with `as`
    with diaper as nappy:
        # But, of course, this serves no useful purpose
        # Since you can just as easily manipulate diaper
        assert nappy is diaper
        if something_smells_funny:
            nappy.soil()
    assert diaper.smelly and nappy.smelly

Note:

    diapers are thread-safe

"""

import sys
from threading import local
from types import ModuleType


class Diaper(ModuleType):
    def __init__(self, *args, **kwargs):
        self._threadlocal = local()
        self.change()
        super(Diaper, self).__init__(*args, **kwargs)

    def __call__(self, f, *args, **kwargs):
        self.change()
        try:
            return f(*args, **kwargs)
        except:
            self.soil()

    def __enter__(self):
        # Entering the context puts on a new diaper
        self.change()
        # Return the diaper if (for whatever reason?) someone wants to use `with ... as`
        return self

    def __exit__(self, exctype, excinst, exctb):
        if exctype is not None:
            self.soil()
        return True

    # The diaper interface!
    def change(self):
        """Indicate that this diaper is clean, and therefore not smelly."""
        self.smelly = False

    def soil(self):
        """Indicate that this diaper is dirty, and therefore smelly."""
        self.smelly = True

    def _get_smell(self):
        try:
            return self._threadlocal.smelly
        except AttributeError:
            # smelly is initialized by the importing thread, so it's possible
            # that a thread has access to the diaper but smelly hasn't been
            # set in the threadlocal store. In that case, this thread's diaper
            # is clean, since it hasn't yet been soiled or changed in the
            # calling thread. "Initialize" the diaper and return.
            self.change()
            return self._threadlocal.smelly

    def _set_smell(self, smelliness):
        self._threadlocal.smelly = bool(smelliness)

    #: A smelly diaper is a dirty diaper
    smelly = property(_get_smell, _set_smell)

# Well, the diaper pattern's already pretty shitty,
# let's go ahead and just do some module impersonation
sys.modules[__name__] = Diaper(__name__, __doc__)
