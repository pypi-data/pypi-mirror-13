"""View configuration helpers."""
import sys

from inspect import getmembers, getmro, isclass

from venusian import Categories
from venusian.advice import getFrameInfo
from venusian import ATTACH_ATTR, LIFTONLY_ATTR


def _create_child_view_config_from_parent_cb(cb, module_name, liftid, cscope, overrides):
    """Override view_config declarations from parent for the child.

    Inspect the given venusian decorator callback to see if it is view_config.. If it is view_config, then create equal entry with overridden settings.

    :return: (callback tuple, view_config Ωere overridden flag)
    """

    # Arguments look like:
    # (<function view_config.__call__.<locals>.callback at 0x101d7d268>, 'websauna.viewconfig.tests.testmodule', 'render None', 'class')


    # Check if we are view_config or previously nested @view_overrides
    if not (cb.__qualname__.startswith("view_config") or cb.__qualname__.startswith("_create_child_view_config_from_parent_cb")):
        return (cb, module_name, liftid, cscope), False

    # OK we are view_config, then pry the decorators parameters out from the closure. If this is not evil Python programming, I don't know what is.
    # Closure looks like (<cell at 0x101cfc948: AttachInfo object at 0x101db4518>, <cell at 0x101cfc888: dict object at 0x101da08c8>)

    if not len(cb.__closure__) == 2:
        # Doesn't look like what we are looking for
        return (cb, module_name, liftid, cscope), False

    # This is like:
    # {'route_name': 'parent', '_info': ('/Users/mikko/code/trees/websauna.viewconfig/websauna/viewconfig/tests/testmodule.py', 15, 'Parent', '@view_config(route_name="parent", renderer="foobar.html")'), 'renderer': 'foobar.html', 'attr': 'render'}
    info = cb.__closure__[0].cell_contents
    settings = cb.__closure__[1].cell_contents

    # Recreate the callback with new parameters
    settings = settings.copy()
    settings.update(overrides)

    # See pyramid.view.view_config
    def new_callback(context, name, ob):
        config = context.config.with_package(info.module)
        config.add_view(view=ob, **settings)

    return (new_callback, module_name, liftid, cscope), True


class view_overrides(object):
    """A class decorator which overrides chosen view_config arguments from the parent class.

    """
    def __init__(self, categories=None, **kwargs):
        self.categories = categories
        self.kwargs = kwargs

    def __call__(self, wrapped):
        # Shamefully stolen from venusian.lift

        if not isclass(wrapped):
            raise RuntimeError('"view_overrides" only works as a class decorator; you tried to use it against %r' % wrapped)

        frame = sys._getframe(1)
        scope, module, f_locals, f_globals, codeinfo = getFrameInfo(frame)
        module_name = getattr(module, '__name__', None)
        newcategories = Categories(wrapped)
        newcategories.lifted = True

        # Did we find any view_config decorators from the parents of wrapped class
        found = False

        for cls in getmro(wrapped):

            attached_categories = cls.__dict__.get(ATTACH_ATTR, None)
            if attached_categories is None:
                attached_categories = cls.__dict__.get(LIFTONLY_ATTR, None)

            if attached_categories is not None:

                for cname, category in attached_categories.items():
                    if cls is not wrapped:
                        if self.categories and not cname in self.categories:
                            continue
                    callbacks = newcategories.get(cname, [])
                    newcallbacks = []

                    for cb, _, liftid, cscope in category:
                        append = True
                        toappend = (cb, module_name, liftid, cscope)

                        if cscope == 'class':
                            for ncb, _, nliftid, nscope in callbacks:
                                if (nscope == 'class' and liftid == nliftid):
                                    append = False
                        if append:
                            toappend, _found = _create_child_view_config_from_parent_cb(*toappend, overrides=self.kwargs)
                            found = found or _found
                            newcallbacks.append(toappend)
                    newcategory = list(callbacks) + newcallbacks
                    newcategories[cname] = newcategory
                if attached_categories.lifted:
                    break
        if newcategories: # if it has any keys
            setattr(wrapped, ATTACH_ATTR, newcategories)

        if not found:
            raise RuntimeError('"view_overrides" could not find any @view_config decorators on the parent classes of %r' % wrapped)

        return wrapped