#via https://stackoverflow.com/a/1057534
from os.path import dirname, basename, isfile
from os.path import abspath, expanduser, splitext
import glob
from .asd import read_asd
from .sed import read_sed
from .sig import read_sig
from .pico import read_pico
from .txt_asd1 import read_txt_asd1
from .txt_asd2 import read_txt_asd2

modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

SUPPORTED_TEXT_READERS = {
        '.0': read_txt_asd1,
        '.a': read_txt_asd2,
}

SUPPORTED_READERS = {
        '.asd': read_asd,
        '.sig': read_sig,
        '.sed': read_sed,
        '.pico': read_pico,
        '.light': read_pico,
        '.dark': read_pico,
        '.txt': SUPPORTED_TEXT_READERS,
}


def select_reader(d, filepath):
    """
    Some data files may have two extensions. The extensions will be checked in
    turns. This requires a nested dictionary to store the mappings between the
    extensions and readers.
    The example of a data file with two extensions are text files such as
    ".asd.txt". Thus the mappings for text readers are in a dict within the dict
    for non-text readers. Please see SUPPORTED_READERS and
    SUPPORTED_TEXT_READERS dicts.
    This function loop over available extensions in a dict and compare to the
    detected extension. This function also calls itself when it located a dict.
    Each time the function is called it expects a valid filepath and pop off
    the extension from the filepath to compare with the available extensions.
    """
    filepath, ext = splitext(filepath)
    for k, v in d.items():
        if k in ext:
            if isinstance(v, dict):
                reader = select_reader(v, filepath)
            else:
                reader = v
            return reader

    raise KeyError("No reader found for extension " + ext)


def read(filepath, read_data=True, read_metadata=True, verbose=False):
    """Calls a reader function based on the extension of the passed filename.
        .asd: read_asd
        .txt: various text readers
        .sig: read_sig
        .sed: read_sed
        .pico: read_pico
    """
    reader = select_reader(SUPPORTED_READERS, filepath)

    return reader(abspath(expanduser(filepath)), read_data,
                  read_metadata, verbose)
