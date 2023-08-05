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


log = logging.getLogger("phlb.%s" % __name__)

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
    value=value.strip()
    if value==":memory:":
        return value
    return os.path.normpath(os.path.abspath(os.path.expanduser(value)))

def logging_level(value):
    level=getattr(logging, value)
    return level


INI_CONVERTER_DICT = {
    "database_name": expand_abs_path,
    "enable_auto_login": bool,

    "backup_path": expand_abs_path,
    "sub_dir_formatter": strftime,

    "skip_dirs": commalist,
    "skip_files": commalist,

    "logging_level": logging_level,
    "default_new_path_mode": int8,
    "hash_name": hashname,
    "chunk_size": int,
}



def get_dict_from_ini(filepath):
    log.debug("Read config '%s'" % filepath)
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
    log.debug("Search paths: '%s'" % search_paths)
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


def set_phlb_logger(level):
    phlb_logger = logging.getLogger("phlb")
    phlb_logger.setLevel(level=level)
    phlb_logger.handlers = []
    handler = logging.StreamHandler()
    phlb_logger.addHandler(handler)
    phlb_logger.info("Set log level: %i" % level)


class PyHardLinkBackupConfig(object):
    ini_filepath=None
    _config=None

    def __init__(self, ini_converter_dict):
        super(PyHardLinkBackupConfig, self).__init__()
        self.ini_converter_dict = ini_converter_dict

    def _load(self, force=False):
        if force or self._config is None:
            self._config = self._read_config()
            set_phlb_logger(level=self._config["logging_level"])

    def __getattr__(self, item):
        self._load()

        try:
            return self._config[item]
        except KeyError:
            raise AttributeError("%s missing in '%s'" % (item.upper(), self.ini_filepath))

    def __repr__(self):
        self._load()
        return "'%s' with '%s'" % (self.ini_filepath, self._config)

    def open_editor(self):
        self._load()
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
                    raise Exception("%s - .ini file: '%s'" % (err, self.ini_filepath))

            result[key] = value
        return result

    def _read_config(self):
        """
        returns the config as a dict.
        """       
        default_config_filepath = os.path.join(
            os.path.dirname(__file__), DEAFULT_CONFIG_FILENAME
        )
        log.debug("Read defaults from: '%s'" % default_config_filepath)
        if not os.path.isfile(default_config_filepath):
            raise RuntimeError(
                "Internal error: Can't locate the default .ini file here: '%s'" % default_config_filepath
            )
        config = self._read_and_convert(default_config_filepath, all_values=True)
        log.debug("Defaults: %s", pprint.pformat(config))
    
        self.ini_filepath = get_ini_filepath()
        if not self.ini_filepath:
            # No .ini file made by user found
            # -> Create one into user home
            self.ini_filepath = get_user_ini_filepath()

            # We don't use shutil.copyfile here, so the line endings will
            # be converted e.g. under windows from \n to \n\r
            with open(default_config_filepath, "r") as infile:
                with open(self.ini_filepath, "w") as outfile:
                    outfile.write(infile.read())

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

    def print_config(self):
        self._load()
        print("Debug config '%s':" % self.ini_filepath)
        pprint.pprint(self._config)

phlb_config=PyHardLinkBackupConfig(INI_CONVERTER_DICT)


if __name__ == '__main__':
    import sys
    sys.stdout = sys.stderr # work-a-round for PyCharm to sync output
    logging.basicConfig(level=logging.DEBUG)

    phlb_config=PyHardLinkBackupConfig(INI_CONVERTER_DICT)

    print("INI filepath: '%s'" % phlb_config.ini_filepath)
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