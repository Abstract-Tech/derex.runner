from collections import namedtuple
import os
import pkg_resources
from typing import List, Dict, Callable, Union
import pluggy
from derex.runner import config
from derex.runner import plugin_spec
from derex.runner import hookimpl
from derex.runner.utils import asbool


def setup_plugin_manager():
    plugin_manager = pluggy.PluginManager("derex.runner")
    plugin_manager.add_hookspecs(plugin_spec)
    plugin_manager.load_setuptools_entrypoints("derex.runner")
    plugin_manager.register(config.BaseOpenEdX)
    plugin_manager.register(config.LocalOpenEdX)
    plugin_manager.register(config.BaseServices)
    return plugin_manager


# Used internally by `Registry` for each item in its sorted list.
# Provides an easier to read API when editing the code later.
# For example, `item.name` is more clear than `item[0]`.
_PriorityItem = namedtuple("PriorityItem", ["name", "priority"])


class Registry(object):
    """
    Stolen from Python-Markdown/utils.py
    A priority sorted registry.
    A `Registry` instance provides two public methods to alter the data of the
    registry: `register` and `deregister`. Use `register` to add items and
    `deregister` to remove items. See each method for specifics.
    When registering an item, a "name" and a "priority" must be provided. All
    items are automatically sorted by "priority" from highest to lowest. The
    "name" is used to remove ("deregister") and get items.
    A `Registry` instance it like a list (which maintains order) when reading
    data. You may iterate over the items, get an item and get a count (length)
    of all items. You may also check that the registry contains an item.
    When getting an item you may use either the index of the item or the
    string-based "name". For example:
        registry = Registry()
        registry.register(SomeItem(), 'itemname', 20)
        # Get the item by index
        item = registry[0]
        # Get the item by name
        item = registry['itemname']
    When checking that the registry contains an item, you may use either the
    string-based "name", or a reference to the actual item. For example:
        someitem = SomeItem()
        registry.register(someitem, 'itemname', 20)
        # Contains the name
        assert 'itemname' in registry
        # Contains the item instance
        assert someitem in registry
    The method `get_index_for_name` is also available to obtain the index of
    an item using that item's assigned "name".
    """

    def __init__(self):
        self._data = {}
        self._priority = []
        self._is_sorted = False

    def __contains__(self, item):
        if isinstance(item, str):
            # Check if an item exists by this name.
            return item in self._data.keys()
        # Check if this instance exists.
        return item in self._data.values()

    def __iter__(self):
        self._sort()
        return iter([self._data[k] for k, p in self._priority])

    def __getitem__(self, key):
        self._sort()
        if isinstance(key, slice):
            data = Registry()
            for k, p in self._priority[key]:
                data.register(self._data[k], k, p)
            return data
        if isinstance(key, int):
            return self._data[self._priority[key].name]
        return self._data[key]

    def __len__(self):
        return len(self._priority)

    def __repr__(self):
        return "<{0}({1})>".format(self.__class__.__name__, list(self))

    def get_index_for_name(self, name):
        """
        Return the index of the given name.
        """
        if name in self:
            self._sort()
            return self._priority.index(
                [x for x in self._priority if x.name == name][0]
            )
        raise ValueError('No item named "{0}" exists.'.format(name))

    def register(self, item, name, priority):
        """
        Add an item to the registry with the given name and priority.
        Parameters:
        * `item`: The item being registered.
        * `name`: A string used to reference the item.
        * `priority`: An integer or float used to sort against all items.
        If an item is registered with a "name" which already exists, the
        existing item is replaced with the new item. Tread carefully as the
        old item is lost with no way to recover it. The new item will be
        sorted according to its priority and will **not** retain the position
        of the old item.
        """
        if name in self:
            # Remove existing item of same name first
            self.deregister(name)
        self._is_sorted = False
        self._data[name] = item
        self._priority.append(_PriorityItem(name, priority))

    def deregister(self, name, strict=True):
        """
        Remove an item from the registry.
        Set `strict=False` to fail silently.
        """
        try:
            index = self.get_index_for_name(name)
            del self._priority[index]
            del self._data[name]
        except ValueError:
            if strict:
                raise

    def _sort(self):
        """
        Sort the registry by priority from highest to lowest.
        This method is called internally and should never be explicitly called.
        """
        if not self._is_sorted:
            self._priority.sort(key=lambda item: item.priority, reverse=True)
            self._is_sorted = True

    def add(self, key, value, location):
        """ Register a key by location. """
        if len(self) == 0:
            # This is the first item. Set priority to 50.
            priority = 50
        elif location == "_begin":
            self._sort()
            # Set priority 5 greater than highest existing priority
            priority = self._priority[0].priority + 5
        elif location == "_end":
            self._sort()
            # Set priority 5 less than lowest existing priority
            priority = self._priority[-1].priority - 5
        elif location.startswith("<") or location.startswith(">"):
            # Set priority halfway between existing priorities.
            i = self.get_index_for_name(location[1:])
            if location.startswith("<"):
                after = self._priority[i].priority
                if i > 0:
                    before = self._priority[i - 1].priority
                else:
                    # Location is first item`
                    before = after + 10
            else:
                # location.startswith('>')
                before = self._priority[i].priority
                if i < len(self) - 1:
                    after = self._priority[i + 1].priority
                else:
                    # location is last item
                    after = before - 10
            priority = before - ((before - after) / 2)
        else:
            raise ValueError(
                'Not a valid location: "%s". Location key '
                'must start with a ">" or "<".' % location
            )
        self.register(value, key, priority)
