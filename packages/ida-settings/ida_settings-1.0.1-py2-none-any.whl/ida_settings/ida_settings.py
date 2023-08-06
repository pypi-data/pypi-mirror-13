"""
ida_settings provides a mechanism for settings and fetching
configration values for IDAPython scripts and plugins.
Configurations are namespaced by plugin name,
and scoped to the global system, current user,
working directory, or current IDB file. Configurations
can be exported and imported using an .ini-style intermediate
representation.

Example fetching a configuration value:

    settings = IDASettings("MSDN-doc")
    if settings["verbosity"] == "high":
        ...

Example setting a global configuration value:

    settings = IDASettings("MSDN-doc")
    settings.system["verbosity"] = "high"

Example setting a working directory configuration value:

    settings = IDASettings("MSDN-doc")
    settings.directory["verbosity"] = "high"

Use the properties "system", "user", "directory" and "idb"
to scope configuration accesses and mutations to the global
system, current user, working directory, or current IDB file.

Plugins that write settings should pick the appropriate
scope for their settings. Plugins that read settings should
fetch them from the default scope. This allows for precedence
of scopes, such as the current IDB over system-wide configuration.
For example:

    settings = IDASettings("MSDN-doc")
    # when writing, use a scope:
    settings.user["verbosity"] = "high"
    
    # when reading, use the default scope:
    settings["verbosity"] --> "high"

Generally, treat a settings instance like a dictionary. For example:

    settings = IDASettings("MSDN-doc")
    "verbosity" in settings.user --> False
    settings.user["verbosity"] = "high"
    settings.user["verbosity"] --> "high"
    settings.user.keys()       --> ["verbosity"]
    settings.user.values()     --> ["high"]
    settings.user.items()      --> [("verbosity", "high')]

The value of a particular settings entry must be a JSON-encodable
value. For example, these are fine:

    settings = IDASettings("MSDN-doc")
    settings.user["verbosity"] = "high"
    settings.user["count"] = 1
    settings.user["percentage"] = 0.75
    settings.user["filenames"] = ["a.txt", "b.txt"]
    settings.user["aliases"] = {"bp": "breakpoint", "g": "go"}

and this is not:

    settings.user["object"] = hashlib.md5()      # this is not JSON-encodable

To export the current effective settings, use the `export_settings`
function. For example:

    settings = IDASettings("MSDN-doc")
    export_settings(settings, "/home/user/desktop/current.ini")

To import existing settings into a settings instance, such as
the open IDB, use the `import_settings` function. For example:

    settings = IDASettings("MSDN-doc")
    import_settings(settings.idb, "/home/user/desktop/current.ini")

Enumerate the plugin names for the various levels using the
IDASettings class properties:

    IDASettings.get_system_plugin_names()     --> ["plugin-1", "plugin-2"]
    IDASettings.get_user_plugin_names()       --> ["plugin-3", "plugin-4"]
    IDASettings.get_directory_plugin_names()  --> ["plugin-5", "plugin-6"]
    IDASettings.get_idb_plugin_names()        --> ["plugin-7", "plugin-8"]

This module is a single file that you can include in IDAPython
plugin module or scripts.

It depends on ida-netnode, which you can download here: 
https://github.com/williballenthin/ida-netnode

This project is licensed under the Apache 2.0 license.

Author: Willi Ballenthin <william.ballenthin@fireeye.com>
"""
import os
import re
import sys
import abc
import json
import logging
import datetime
import unittest
import contextlib

try:
    import idc
    import idaapi
    import netnode
except ImportError:
    pass


# we'll use a function here to avoid polluting our global variable namespace.
def import_qtcore():
    """
    This nasty piece of code is here to force the loading of IDA's
     Qt bindings.
    Without it, Python attempts to load PySide from the site-packages
     directory, and failing, as it does not play nicely with IDA.

    via: github.com/tmr232/Cute
    """
    has_ida = False
    try:
        # if we're running under IDA,
        # then we'll use IDA's Qt bindings
        import idaapi
        has_ida = True
    except ImportError:
        # not running under IDA,
        # so use default Qt installation
        has_ida = False

    if has_ida:
        old_path = sys.path[:]
        try:
            ida_python_path = os.path.dirname(idaapi.__file__)
            sys.path.insert(0, ida_python_path)
            if idaapi.IDA_SDK_VERSION >= 690:
                from PyQt5 import QtCore
                return QtCore
            else:
                from PySide import QtCore
                return QtCore
        finally:
            sys.path = old_path
    else:
        try:
            from PyQt5 import QtCore
            return QtCore
        except ImportError:
            pass

        try:
            from PySide import QtCore
            return QtCore
        except ImportError:
            pass

        raise ImportError("No module named PySide or PyQt")


QtCore = import_qtcore()

CONFIG_FILE_NANE = ".ida-settings.ini"
IDA_SETTINGS_ORGANIZATION = "IDAPython"
IDA_SETTINGS_APPLICATION = "IDA-Settings"

g_logger = logging.getLogger("ida-settings")


# enforce methods required by settings providers
class IDASettingsInterface:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_value(self, key):
        """
        Fetch the settings value with the given key, or raise KeyError.

        type key: basestring
        rtype value: Union[basestring, int, float, List, Dict]
        """
        raise NotImplemented

    @abc.abstractmethod
    def set_value(self, key, value):
        """
        Set the settings value with the given key.

        type key: basestring
        type value: Union[basestring, int, float, List, Dict]
        """
        raise NotImplemented

    @abc.abstractmethod
    def del_value(self, key):
        """
        Remove the settings value with the given key.
        Does not raise an error if the key does not already exist.

        type key: basestring
        """
        raise NotImplemented

    @abc.abstractmethod
    def get_keys(self):
        """
        Fetch an iterable of the settings keys, which are strings.

        rtype: Iterable[basestring]
        """
        raise NotImplemented

    @abc.abstractmethod
    def clear(self):
        """
        Delete all settings for this settings instance.

        rtype: None
        """
        raise NotImplemented


def validate(s):
    # the slash character is used by QSettings to denote a subgroup
    # we want to have a single nested structure of settings
    if "/" in s:
        return False
    if "\\" in s:
        # QSettings automatically translates '\' to '/'
        return False
    return True


# provide base constructor args required by settings providers
class IDASettingsBase(IDASettingsInterface):
    def __init__(self, plugin_name):
        super(IDASettingsBase, self).__init__()
        if not validate(plugin_name):
            raise RuntimeError("invalid plugin name")
        self._plugin_name = plugin_name


# allow IDASettings to look like dicts
class DictMixin:
    def __getitem__(self, key):
        if not isinstance(key, basestring):
            raise TypeError("key must be a string")
        return self.get_value(key)

    def __setitem__(self, key, value):
        if not isinstance(key, basestring):
            raise TypeError("key must be a string")
        return self.set_value(key, value)

    def __delitem__(self, key):
        if not isinstance(key, basestring):
            raise TypeError("key must be a string")
        return self.del_value(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        try:
            if self[key] is not None:
                return True
            return False
        except KeyError:
            return False

    def iterkeys(self):
        return self.get_keys()

    def keys(self):
        return [k for k in self.iterkeys()]

    def itervalues(self):
        for k in self.iterkeys():
            yield self[k]

    def values(self):
        return [v for v in self.itervalues()]

    def iteritems(self):
        for k in self.iterkeys():
            yield k, self[k]

    def items(self):
        return [(k, v) for k, v in self.iteritems()]


MARKER_KEY = "__meta/permission_check"


def has_qsettings_write_permission(settings):
    value = datetime.datetime.now().isoformat("T")
    settings.setValue(MARKER_KEY, value)
    settings.sync()
    # there's a race here, if another thread/process also
    # performs the same check at the same time
    if settings.status() != QtCore.QSettings.NoError:
        return False
    if settings.value(MARKER_KEY) != value:
        return False
    settings.remove(MARKER_KEY)
    settings.sync()
    return True


class PermissionError(IOError):
    def __init__(self):
        super(PermissionError, self).__init__("Unable to write to QSettings")


class QSettingsIDASettings(IDASettingsInterface):
    """
    An IDASettings implementation that uses an existing QSettings
     instance to persist the keys and values.
    """

    def __init__(self, qsettings):
        super(QSettingsIDASettings, self).__init__()
        self._settings = qsettings
        self._has_perms = None

    def _check_perms(self):
        if self._has_perms is None:
            self._has_perms = has_qsettings_write_permission(self._settings)
        if not self._has_perms:
            raise PermissionError()

    def get_value(self, key):
        v = self._settings.value(key)
        if v is None:
            raise KeyError("key not found")
        return json.loads(v)

    def set_value(self, key, value):
        self._check_perms()
        self._settings.setValue(key, json.dumps(value))

    def del_value(self, key):
        self._check_perms()
        return self._settings.remove(key)

    def get_keys(self):
        for k in self._settings.allKeys():
            yield k

    def clear(self):
        self._check_perms()
        # Qt: the empty string removes all entries in the current group
        self._settings.remove("")


class SystemIDASettings(IDASettingsBase, DictMixin):
    """
    An IDASettings implementation that persists keys and values in the
     system scope using a QSettings instance.
    """

    def __init__(self, plugin_name, *args, **kwargs):
        super(SystemIDASettings, self).__init__(plugin_name, *args, **kwargs)
        s = QtCore.QSettings(QtCore.QSettings.SystemScope,
                             IDA_SETTINGS_ORGANIZATION,
                             IDA_SETTINGS_APPLICATION)
        s.beginGroup(self._plugin_name)
        self._qsettings = QSettingsIDASettings(s)

    def get_value(self, key):
        return self._qsettings.get_value(key)

    def set_value(self, key, value):
        return self._qsettings.set_value(key, value)

    def del_value(self, key):
        return self._qsettings.del_value(key)

    def get_keys(self):
        return self._qsettings.get_keys()

    def clear(self):
        return self._qsettings.clear()


class UserIDASettings(IDASettingsBase, DictMixin):
    """
    An IDASettings implementation that persists keys and values in the
     user scope using a QSettings instance.
    """

    def __init__(self, plugin_name, *args, **kwargs):
        super(UserIDASettings, self).__init__(plugin_name, *args, **kwargs)
        s = QtCore.QSettings(QtCore.QSettings.UserScope,
                             IDA_SETTINGS_ORGANIZATION,
                             IDA_SETTINGS_APPLICATION)
        s.beginGroup(self._plugin_name)
        self._qsettings = QSettingsIDASettings(s)

    def get_value(self, key):
        return self._qsettings.get_value(key)

    def set_value(self, key, value):
        return self._qsettings.set_value(key, value)

    def del_value(self, key):
        return self._qsettings.del_value(key)

    def get_keys(self):
        return self._qsettings.get_keys()

    def clear(self):
        return self._qsettings.clear()


def get_directory_config_path(directory=None):
    if directory is None:
        directory = os.path.dirname(idc.GetIdbPath())
    config_path = os.path.join(directory, CONFIG_FILE_NANE)
    return config_path


class DirectoryIDASettings(IDASettingsBase, DictMixin):
    """
    An IDASettings implementation that persists keys and values in the
     directory scope using a QSettings instance.
    """

    def __init__(self, plugin_name, *args, **kwargs):
        config_directory = kwargs.pop("directory")
        super(DirectoryIDASettings, self).__init__(plugin_name, *args, **kwargs)
        config_path = get_directory_config_path(config_directory)
        s = QtCore.QSettings(config_path, QtCore.QSettings.IniFormat)
        s.beginGroup(self._plugin_name)
        self._qsettings = QSettingsIDASettings(s)

    def get_value(self, key):
        return self._qsettings.get_value(key)

    def set_value(self, key, value):
        return self._qsettings.set_value(key, value)

    def del_value(self, key):
        return self._qsettings.del_value(key)

    def get_keys(self):
        return self._qsettings.get_keys()

    def clear(self):
        return self._qsettings.clear()


def get_meta_netnode():
    """
    Get the netnode used to store settings metadata in the current IDB.
    Note that this implicitly uses the open IDB via the idc iterface.
    """
    node_name = "$ {org:s}.{application:s}".format(
        org=IDA_SETTINGS_ORGANIZATION,
        application=IDA_SETTINGS_APPLICATION)
    return netnode.Netnode(node_name)


PLUGIN_NAMES_KEY = "plugin_names"


def get_netnode_plugin_names():
    """
    Get a iterable of the plugin names registered in the current IDB.
    Note that this implicitly uses the open IDB via the idc iterface.
    """
    try:
        return json.loads(get_meta_netnode()[PLUGIN_NAMES_KEY])
    except KeyError:
        # TODO: there may be other exception types to catch here
        return []


def add_netnode_plugin_name(plugin_name):
    """
    Add the given plugin name to the list of plugin names registered in
      the current IDB.
    Note that this implicitly uses the open IDB via the idc iterface.
    """
    current_names = set(get_netnode_plugin_names())
    if plugin_name in current_names:
        return

    current_names.add(plugin_name)

    get_meta_netnode()[PLUGIN_NAMES_KEY] = json.dumps(list(current_names))


def del_netnode_plugin_name(plugin_name):
    """
    Remove the given plugin name to the list of plugin names registered in
      the current IDB.
    Note that this implicitly uses the open IDB via the idc iterface.
    """
    current_names = set(get_netnode_plugin_names())
    if plugin_name not in current_names:
        return

    try:
        current_names.remove(plugin_name)
    except KeyError:
        return

    get_meta_netnode()[PLUGIN_NAMES_KEY] = json.dumps(list(current_names))


class IDBIDASettings(IDASettingsBase, DictMixin):
    """
    An IDASettings implementation that persists keys and values in the
     current IDB database.
    """

    @property
    def _netnode(self):
        node_name = "$ {org:s}.{application:s}.{plugin_name:s}".format(
            org=IDA_SETTINGS_ORGANIZATION,
            application=IDA_SETTINGS_APPLICATION,
            plugin_name=self._plugin_name)
        return netnode.Netnode(node_name)

    def get_value(self, key):
        if not isinstance(key, basestring):
            raise TypeError("key must be a string")

        try:
            v = self._netnode[key]
        except TypeError:
            raise KeyError("key not found")
        if v is None:
            raise KeyError("key not found")

        return json.loads(v)

    def set_value(self, key, value):
        if not isinstance(key, basestring):
            raise TypeError("key must be a string")

        self._netnode[key] = json.dumps(value)
        add_netnode_plugin_name(self._plugin_name)

    def del_value(self, key):
        if not isinstance(key, basestring):
            raise TypeError("key must be a string")

        try:
            del self._netnode[key]
        except KeyError:
            pass

    def get_keys(self):
        return self._netnode.iterkeys()

    def clear(self):
        for k in self.get_keys():
            self.del_value(k)
        self._netnode.kill()
        del_netnode_plugin_name(self._plugin_name)


def ensure_ida_loaded():
    try:
        import idc
        import idaapi
    except ImportError:
        raise EnvironmentError("Must be running in IDA to access IDB or directory settings")


class IDASettings(object):
    def __init__(self, plugin_name, directory=None):
        super(IDASettings, self).__init__()
        if not validate(plugin_name):
            raise RuntimeError("invalid plugin name")
        self._plugin_name = plugin_name
        self._config_directory = directory

    @property
    def idb(self):
        """
        Fetch the IDASettings instance for the curren plugin with IDB scope.
        
        rtype: IDASettingsInterface
        """
        ensure_ida_loaded()
        return IDBIDASettings(self._plugin_name)

    @property
    def directory(self):
        """
        Fetch the IDASettings instance for the curren plugin with directory scope.
        
        rtype: IDASettingsInterface
        """
        if self._config_directory is None:
            ensure_ida_loaded()
        return DirectoryIDASettings(self._plugin_name, directory=self._config_directory)

    @property
    def user(self):
        """
        Fetch the IDASettings instance for the curren plugin with user scope.
        
        rtype: IDASettingsInterface
        """
        return UserIDASettings(self._plugin_name)

    @property
    def system(self):
        """
        Fetch the IDASettings instance for the curren plugin with system scope.
        
        rtype: IDASettingsInterface
        """
        return SystemIDASettings(self._plugin_name)

    def get_value(self, key):
        """
        Fetch the settings value with the highest precedence for the given
         key, or raise KeyError.
        Precedence:
          - IDB scope
          - directory scope
          - user scope
          - system scope

        type key: basestring
        rtype value: Union[basestring, int, float, List, Dict]
        """
        try:
            return self.idb.get_value(key)
        except (KeyError, EnvironmentError):
            pass
        try:
            return self.directory.get_value(key)
        except (KeyError, EnvironmentError):
            pass
        try:
            return self.user.get_value(key)
        except KeyError:
            pass
        try:
            return self.system.get_value(key)
        except KeyError:
            pass

        raise KeyError("key not found")

    def iterkeys(self):
        """
        Enumerate the keys found at any scope for the current plugin.
        
        rtype: Generator[str]
        """
        visited_keys = set()
        try:
            for key in self.idb.iterkeys():
                if key not in visited_keys:
                    yield key
                    visited_keys.add(key)
        except (PermissionError, EnvironmentError):
            pass

        try:
            for key in self.directory.iterkeys():
                if key not in visited_keys:
                    yield key
                    visited_keys.add(key)
        except (PermissionError, EnvironmentError):
            pass

        try:
            for key in self.user.iterkeys():
                if key not in visited_keys:
                    yield key
                    visited_keys.add(key)
        except (PermissionError, EnvironmentError):
            pass

        try:
            for key in self.system.iterkeys():
                if key not in visited_keys:
                    yield key
                    visited_keys.add(key)
        except (PermissionError, EnvironmentError):
            pass

    def keys(self):
        """
        Enumerate the keys found at any scope for the current plugin.
        
        rtype: Generator[str]
        """

        return list(self.iterkeys())

    def itervalues(self):
        """
        Enumerate the values found at any scope for the current plugin.
        
        rtype: Generator[jsonable]
        """

        for key in self.iterkeys():
            yield self[key]

    def values(self):
        """
        Enumerate the values found at any scope for the current plugin.
        
        rtype: Sequence[jsonable]
        """

        return list(self.itervalues())

    def iteritems(self):
        """
        Enumerate the (key, value) pairs found at any scope for the current plugin.
        
        rtype: Sequence[Tuple[str, jsonable]]
        """
        for key in self.iterkeys():
            yield (key, self[key])

    def items(self):
        """
        Enumerate the (key, value) pairs found at any scope for the current plugin.
        
        rtype: Sequence[Tuple[str, jsonable]]
        """
        return list(self.iteritems())

    def __getitem__(self, key):
        return self.get_value(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        try:
            if self[key] is not None:
                return True
            return False
        except KeyError:
            return False

    @staticmethod
    def get_system_plugin_names():
        """
        Get the names of all plugins at the system scope.
        As this is a static method, you can call the directly on IDASettings:

            import ida_settings
            print( ida_settings.IDASettings.get_system_plugin_names() )
        
        rtype: Sequence[str]
        """
        return QtCore.QSettings(QtCore.QSettings.SystemScope,
                                IDA_SETTINGS_ORGANIZATION,
                                IDA_SETTINGS_APPLICATION).childGroups()[:]

    @staticmethod
    def get_user_plugin_names():
        """
        Get the names of all plugins at the user scope.
        As this is a static method, you can call the directly on IDASettings:

            import ida_settings
            print( ida_settings.IDASettings.get_user_plugin_names() )
        
        rtype: Sequence[str]
        """
        return QtCore.QSettings(QtCore.QSettings.UserScope,
                                IDA_SETTINGS_ORGANIZATION,
                                IDA_SETTINGS_APPLICATION).childGroups()[:]

    @staticmethod
    def get_directory_plugin_names(config_directory=None):
        """
        Get the names of all plugins at the directory scope.
        Provide a config directory path to use this method outside of IDA.
        As this is a static method, you can call the directly on IDASettings:

            import ida_settings
            print( ida_settings.IDASettings.get_directory_plugin_names("/tmp/ida/1/") )
        
        type config_directory: str
        rtype: Sequence[str]
        """
        ensure_ida_loaded()
        return QtCore.QSettings(get_directory_config_path(directory=config_directory),
                                QtCore.QSettings.IniFormat).childGroups()[:]

    @staticmethod
    def get_idb_plugin_names():
        """
        Get the names of all plugins at the IDB scope.
        Cannot be used outside of IDA.
        As this is a static method, you can call the directly on IDASettings:

            import ida_settings
            print( ida_settings.IDASettings.get_idb_plugin_names() )
        
        rtype: Sequence[str]
        """
        ensure_ida_loaded()
        return get_netnode_plugin_names()


def import_settings(settings, config_path):
    """
    Import settings from the given file system path to given settings instance.
    
    type settings: IDASettingsInterface
    type config_path: str
    """
    other = QtCore.QSettings(config_path, QtCore.QSettings.IniFormat)
    for k in other.allKeys():
        settings[k] = other.value(k)


def export_settings(settings, config_path):
    """
    Export the given settings instance to the given file system path.
    
    type settings: IDASettingsInterface
    type config_path: str
    """
    other = QtCore.QSettings(config_path, QtCore.QSettings.IniFormat)
    for k, v in settings.iteritems():
        other.setValue(k, v)


#######################################################################################
#
# Test Cases
#  run this file as an IDAPython script to invoke the tests.
#
#######################################################################################


PLUGIN_1 = "plugin1"
PLUGIN_2 = "plugin2"
KEY_1 = "key_1"
KEY_2 = "key_2"
VALUE_1 = bytes("hello")
VALUE_2 = bytes("goodbye")
VALUE_INT = 69
VALUE_FLOAT = 69.69
VALUE_LIST = ["a", "b", "c"]
VALUE_DICT = {"a": 1, "b": "2", "c": 3.0}


class TestSync(unittest.TestCase):
    """
    Demonstrate that creating new instances of the settings objects shows the same data.
    """

    def test_system(self):
        try:
            # this may fail if the user is not running as admin
            IDASettings(PLUGIN_1).system.set_value(KEY_1, VALUE_1)
            self.assertEqual(IDASettings(PLUGIN_1).system.get_value(KEY_1), VALUE_1)
        except PermissionError:
            g_logger.warn("swallowing PermissionError during testing")

    def test_user(self):
        try:
            IDASettings(PLUGIN_1).user.set_value(KEY_1, VALUE_1)
            self.assertEqual(IDASettings(PLUGIN_1).user.get_value(KEY_1), VALUE_1)
        except PermissionError:
            g_logger.warn("swallowing PermissionError during testing")

    def test_directory(self):
        try:
            IDASettings(PLUGIN_1).directory.set_value(KEY_1, VALUE_1)
            self.assertEqual(IDASettings(PLUGIN_1).directory.get_value(KEY_1), VALUE_1)
        except PermissionError:
            g_logger.warn("swallowing PermissionError during testing")

    def test_idb(self):
        try:
            IDASettings(PLUGIN_1).idb.set_value(KEY_1, VALUE_1)
            self.assertEqual(IDASettings(PLUGIN_1).idb.get_value(KEY_1), VALUE_1)
        except PermissionError:
            g_logger.warn("swallowing PermissionError during testing")


@contextlib.contextmanager
def clearing(settings):
    settings.clear()
    try:
        yield
    finally:
        settings.clear()


class TestSettingsMixin(object):
    """
    A mixin that adds standard tests test cases with:
      - self.settings, an IDASettingsInterface implementor
    """

    def test_set(self):
        try:
            with clearing(self.settings):
                # simple set
                self.settings.set_value(KEY_1, VALUE_1)
                self.assertEqual(self.settings.get_value(KEY_1), VALUE_1)
                # overwrite
                self.settings.set_value(KEY_1, VALUE_2)
                self.assertEqual(self.settings.get_value(KEY_1), VALUE_2)
        except PermissionError:
            g_logger.warn("swallowing PermissionError during testing")

    def test_del(self):
        try:
            with clearing(self.settings):
                self.settings.set_value(KEY_1, VALUE_1)
                self.settings.del_value(KEY_1)
                with self.assertRaises(KeyError):
                    self.settings.get_value(KEY_1)
        except PermissionError:
            g_logger.warn("swallowing PermissionError during testing")

    def test_keys(self):
        try:
            with clearing(self.settings):
                self.settings.del_value(KEY_1)
                self.settings.del_value(KEY_2)
                self.settings.set_value(KEY_1, VALUE_1)
                self.assertEqual(list(self.settings.get_keys()), [KEY_1])
                self.settings.set_value(KEY_2, VALUE_2)
                self.assertEqual(list(self.settings.get_keys()), [KEY_1, KEY_2])
        except PermissionError:
            g_logger.warn("swallowing PermissionError during testing")

    def test_dict(self):
        try:
            with clearing(self.settings):
                self.assertFalse(KEY_1 in self.settings)
                self.settings[KEY_1] = VALUE_1
                self.assertEquals(self.settings[KEY_1], VALUE_1)
                self.settings[KEY_2] = VALUE_2
                self.assertEquals(self.settings[KEY_2], VALUE_2)
                self.assertEquals(self.settings.keys(), [KEY_1, KEY_2])
                self.assertEquals(self.settings.values(), [VALUE_1, VALUE_2])
                del self.settings[KEY_1]
                self.assertEquals(self.settings.keys(), [KEY_2])
        except PermissionError:
            g_logger.warn("swallowing PermissionError during testing")

    def test_types(self):
        try:
            with clearing(self.settings):
                for v in [VALUE_INT, VALUE_FLOAT, VALUE_LIST, VALUE_DICT]:
                    self.settings.set_value(KEY_1, v)
                    self.assertEquals(self.settings[KEY_1], v)
        except PermissionError:
            g_logger.warn("swallowing PermissionError during testing")

    def test_large_values(self):
        large_value_1 = "".join(VALUE_1 * 1000)
        large_value_2 = "".join(VALUE_2 * 1000)
        try:
            with clearing(self.settings):
                # simple set
                self.settings.set_value(KEY_1, large_value_1)
                self.assertEqual(self.settings.get_value(KEY_1), large_value_1)
                # overwrite
                self.settings.set_value(KEY_1, large_value_2)
                self.assertEqual(self.settings.get_value(KEY_1), large_value_2)
        except PermissionError:
            g_logger.warn("swallowing PermissionError during testing")


class TestSystemSettings(unittest.TestCase, TestSettingsMixin):
    def setUp(self):
        self.settings = IDASettings(PLUGIN_1).system


class TestUserSettings(unittest.TestCase, TestSettingsMixin):
    def setUp(self):
        self.settings = IDASettings(PLUGIN_1).user


class TestDirectorySettings(unittest.TestCase, TestSettingsMixin):
    def setUp(self):
        self.settings = IDASettings(PLUGIN_1).directory


class TestIdbSettings(unittest.TestCase, TestSettingsMixin):
    def setUp(self):
        self.settings = IDASettings(PLUGIN_1).idb


class TestUserAndSystemSettings(unittest.TestCase):
    def setUp(self):
        self.system = IDASettings(PLUGIN_1).system
        self.user = IDASettings(PLUGIN_1).user

    def test_system_fallback(self):
        """
        QSettings instances with scope "user" automatically fall back to
         scope "system" if the key doesn't exist.
        """
        try:
            with clearing(self.system):
                with clearing(self.user):
                    self.system.set_value(KEY_1, VALUE_1)
                    self.assertEqual(self.user.get_value(KEY_1), VALUE_1)
        except PermissionError:
            g_logger.warn("swallowing PermissionError during testing")


class TestSettingsPrecendence(unittest.TestCase):
    def setUp(self):
        self.system = IDASettings(PLUGIN_1).system
        self.user = IDASettings(PLUGIN_1).user
        self.directory = IDASettings(PLUGIN_1).directory
        self.idb = IDASettings(PLUGIN_1).idb
        self.mux = IDASettings(PLUGIN_1)

    def test_user_gt_system(self):
        try:
            with clearing(self.system):
                with clearing(self.user):
                    self.system.set_value(KEY_1, VALUE_1)
                    self.user.set_value(KEY_1, VALUE_2)
                    self.assertEqual(self.mux.get_value(KEY_1), VALUE_2)
        except PermissionError:
            g_logger.warn("swallowing PermissionError during testing")

    def test_directory_gt_user(self):
        try:
            with clearing(self.user):
                with clearing(self.directory):
                    self.user.set_value(KEY_1, VALUE_1)
                    self.directory.set_value(KEY_1, VALUE_2)
                    self.assertEqual(self.mux.get_value(KEY_1), VALUE_2)
        except PermissionError:
            g_logger.warn("swallowing PermissionError during testing")

    def test_idb_gt_directory(self):
        try:
            with clearing(self.directory):
                with clearing(self.idb):
                    self.directory.set_value(KEY_1, VALUE_1)
                    self.idb.set_value(KEY_1, VALUE_2)
                    self.assertEqual(self.mux.get_value(KEY_1), VALUE_2)
        except PermissionError:
            g_logger.warn("swallowing PermissionError during testing")


class TestPluginNamesAccessors(unittest.TestCase):
    def test_system_plugin_names(self):
        try:
            self.assertEqual(set(IDASettings.get_system_plugin_names()),
                            set([]))

            s1 = IDASettings(PLUGIN_1).system
            with clearing(s1):
                s1[KEY_1] = VALUE_1
                self.assertEqual(set(IDASettings.get_system_plugin_names()),
                                set([PLUGIN_1]))

                s2 = IDASettings(PLUGIN_2).system
                with clearing(s2):
                    s2[KEY_1] = VALUE_1
                    self.assertEqual(set(IDASettings.get_system_plugin_names()),
                                    set([PLUGIN_1, PLUGIN_2]))

            self.assertEqual(set(IDASettings.get_system_plugin_names()), set([]))
        except PermissionError:
            g_logger.warn("swallowing PermissionError during testing")

    def test_user_plugin_names(self):
        try:
            self.assertEqual(set(IDASettings.get_user_plugin_names()),
                            set([]))

            s1 = IDASettings(PLUGIN_1).user
            with clearing(s1):
                s1[KEY_1] = VALUE_1
                self.assertEqual(set(IDASettings.get_user_plugin_names()),
                                set([PLUGIN_1]))

                s2 = IDASettings(PLUGIN_2).user
                with clearing(s2):
                    s2[KEY_1] = VALUE_1
                    self.assertEqual(set(IDASettings.get_user_plugin_names()),
                                    set([PLUGIN_1, PLUGIN_2]))

            self.assertEqual(set(IDASettings.get_user_plugin_names()), set([]))
        except PermissionError:
            g_logger.warn("swallowing PermissionError during testing")

    def test_directory_plugin_names(self):
        try:
            self.assertEqual(set(IDASettings.get_directory_plugin_names()),
                            set([]))

            s1 = IDASettings(PLUGIN_1).directory
            with clearing(s1):
                s1[KEY_1] = VALUE_1
                self.assertEqual(set(IDASettings.get_directory_plugin_names()),
                                set([PLUGIN_1]))

                s2 = IDASettings(PLUGIN_2).directory
                with clearing(s2):
                    s2[KEY_1] = VALUE_1
                    self.assertEqual(set(IDASettings.get_directory_plugin_names()),
                                    set([PLUGIN_1, PLUGIN_2]))

            self.assertEqual(set(IDASettings.get_directory_plugin_names()),
                            set([]))
        except PermissionError:
            g_logger.warn("swallowing PermissionError during testing")

    def test_idb_plugin_names(self):
        try:
            self.assertEqual(set(IDASettings.get_idb_plugin_names()),
                            set([]))

            s1 = IDASettings(PLUGIN_1).idb
            with clearing(s1):
                s1[KEY_1] = VALUE_1
                self.assertEqual(set(IDASettings.get_idb_plugin_names()),
                                set([PLUGIN_1]))

                s2 = IDASettings(PLUGIN_2).idb
                with clearing(s2):
                    s2[KEY_1] = VALUE_1
                    self.assertEqual(set(IDASettings.get_idb_plugin_names()),
                                    set([PLUGIN_1, PLUGIN_2]))

            self.assertEqual(set(IDASettings.get_idb_plugin_names()),
                            set([]))
        except PermissionError:
            g_logger.warn("swallowing PermissionError during testing")


def main():
    try:
        unittest.main()
    except SystemExit:
        pass


if __name__ == "__main__":
    main()
