import inspect
import traceback

import shutil
import os
import sys
import logging
import pprint
import hashlib
import datetime
import webbrowser
import configparser

# https://github.com/mitsuhiko/click
import click


log = logging.getLogger(__name__)

CONFIG_FILENAME="PyHardLinkBackup.ini"
DEAFULT_CONFIG_FILENAME="config_defaults.ini"


def strftime(value):
    # Just test the formatter
    datetime.datetime.now().strftime(value)
    return value

def commalist(value):
    values = [v.strip() for v in value.split(",")] # split and strip
    values = [v for v in values if v!=""] # remove empty strings
    return tuple(values)

def int8(value):
    return int(value, 8)

def hashname(value):
    # test if exist
    hashlib.new(value)
    return value

def expand_abs_path(value):
    return os.path.normpath(os.path.abspath(os.path.expanduser(value)))


INI_CONVERTER_DICT = {
    "database_name": expand_abs_path,
    "enable_auto_login": bool,

    "backup_path": expand_abs_path,
    "sub_dir_formatter": strftime,

    "skip_dirs": commalist,
    "skip_files": commalist,

    "logging_level": None,
    "default_new_path_mode": int8,
    "hash_name": hashname,
    "chunk_size": int,
}



def get_dict_from_ini(filepath):
    log.debug("Read config %r" % filepath)
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(filepath)
    config={}
    for section in parser.sections():
        config.update(
            dict(parser.items(section))
        )
    log.debug("readed config:")
    log.debug(pprint.pformat(config))
    return config


def get_user_ini_filepath():
    return os.path.join(os.path.expanduser("~"), CONFIG_FILENAME)


def get_ini_search_paths():
    search_paths=[
        os.path.join(os.getcwd(), CONFIG_FILENAME),
        get_user_ini_filepath()
    ]
    log.debug("Search paths: %r" % search_paths)
    return search_paths


def get_ini_filepath():
    search_paths=get_ini_search_paths()
    for filepath in search_paths:
        if os.path.isfile(filepath):
            return filepath


def edit_ini(ini_filepath=None):
    """
    Open the .ini file with the operating system’s associated editor.
    """
    if ini_filepath==None:
        ini_filepath = get_ini_filepath()

    try:
        click.edit(filename=ini_filepath)
    except click.exceptions.ClickException as err:
        print("Click err: %s" % err)
        webbrowser.open(ini_filepath)





class PyHardLinkBackupConfig(object):
    ini_filepath=None
    _config=None

    def __init__(self, ini_converter_dict):
        super(PyHardLinkBackupConfig, self).__init__()
        self.ini_converter_dict = ini_converter_dict
        self._config = self._read_config()

    def __getattr__(self, item):
        if self._config is None:
            raise AttributeError(item)

        try:
            return self._config[item]
        except KeyError:
            raise AttributeError("%s missing in %r" % (item.upper(), self.ini_filepath))

    def __repr__(self):
        return "%r with %r" % (self.ini_filepath, self._config)

    def open_editor(self):
        edit_ini(self.ini_filepath)

    def _read_and_convert(self, filepath, all_values):
        """
        if all_values==True: the readed ini file must contain all values
        """
        d = get_dict_from_ini(filepath)
        result = {}
        for key, func in self.ini_converter_dict.items():
            if not all_values and key not in d:
                continue

            try:
                value = d[key]
            except KeyError as err:
                traceback.print_exc()
                print("_"*79)
                print("ERROR: %r is missing in your config!" % err)
                print("Debug .ini config:")
                print(pprint.pformat(self))
                print("\n")
                if click.confirm("Open the editor?"):
                    self.open_editor()
                sys.exit(-1)

            if func:
                try:
                    value = func(value)
                except (KeyError, ValueError) as err:
                    edit_ini(self.ini_filepath)
                    raise Exception("%s - .ini file: %r" % (err, self.ini_filepath))

            result[key] = value
        return result

    def _read_config(self):
        """
        returns the config as a dict.
        """       
        default_config_filepath = os.path.join(
            os.path.dirname(__file__), DEAFULT_CONFIG_FILENAME
        )
        log.debug("Read defaults from: %r" % default_config_filepath)
        if not os.path.isfile(default_config_filepath):
            raise RuntimeError(
                "Internal error: Can't locate the default .ini file here: %r" % default_config_filepath
            )
        config = self._read_and_convert(default_config_filepath, all_values=True)
        log.debug("Defaults: %s", pprint.pformat(config))
    
        self.ini_filepath = get_ini_filepath()
        if not self.ini_filepath:
            # No .ini file made by user found
            # -> Create one into user home
            self.ini_filepath = get_user_ini_filepath()
            shutil.copyfile(default_config_filepath,self.ini_filepath)
            print("\n*************************************************************")
            print("Default config file was created into your home:")
            print("\t%s" % self.ini_filepath)
            print("Change it for your needs ;)")
            print("*************************************************************\n")
        else:
            print("\nread user configuration from:")
            print("\t%s\n" % self.ini_filepath)
            config.update(
                self._read_and_convert(self.ini_filepath, all_values=False)
            )
            log.debug("RawConfig changed to: %s", pprint.pformat(config))

        return config


phlb_config=PyHardLinkBackupConfig(INI_CONVERTER_DICT)


if __name__ == '__main__':
    import sys
    sys.stdout = sys.stderr # work-a-round for PyCharm to sync output
    logging.basicConfig(level=logging.DEBUG)

    phlb_config=PyHardLinkBackupConfig(INI_CONVERTER_DICT)

    print("INI filepath: %r" % phlb_config.ini_filepath)
    pprint.pprint(phlb_config)

    print()
    for k in phlb_config._config.keys():
        print(k, getattr(phlb_config, k))

    try:
        phlb_config.doesntexist
    except AttributeError:
        print("OK")
    else:
        print("ERROR!")