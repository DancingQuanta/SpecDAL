#via https://stackoverflow.com/a/1057534
from os.path import dirname, basename, isfile 
from os.path import abspath, expanduser, splitext, join, split
import glob
from .asd import read_asd
from .sed import read_sed
from .sig import read_sig
from .pico import read_pico
from .txt_asd1 import read_txt_asd1
from .txt_asd2 import read_txt_asd2

modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

SUPPORTED_TEXT_READERS = {
        '.0': read_txt_asd1,
        '.a': read_txt_asd2,
}

def read_txt(filepath, read_data=True, read_metadata=True, verbose=False):
    """Calls a reader function based on the extension of the passed filename.
        .0**: read_txt_asd1
        .asd: read_txt_asd2
    """
    # Strip .txt
    filename = splitext(filepath)[0]
    # Get secondary ext and select first two characters
    ext = splitext(filename)[1][0:2]
    assert ext in SUPPORTED_TEXT_READERS
    reader = SUPPORTED_TEXT_READERS[ext]
    return reader(abspath(expanduser(filepath)), read_data,
                  read_metadata, verbose)

SUPPORTED_READERS = {
        '.asd':read_asd,
        '.txt': read_txt,
        '.sig':read_sig,
        '.sed':read_sed,
        '.pico':read_pico,
        '.light':read_pico,
        '.dark':read_pico,
}

def read(filepath, read_data=True, read_metadata=True, verbose=False):
    """Calls a reader function based on the extension of the passed filename.
        .asd: read_asd
        .txt: read_txt_asd
        .sig: read_sig
        .sed: read_sed
        .pico: read_pico
    """
    ext = splitext(filepath)[1]
    assert ext in SUPPORTED_READERS
    reader = SUPPORTED_READERS[ext]
    return reader(abspath(expanduser(filepath)), read_data,
                  read_metadata, verbose)
