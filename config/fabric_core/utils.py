"""
   This file contains the helper functions for interacting with Microsoft Fabric 
   using fabric cli. 
"""
import sys, shutil
from pathlib import Path


"""
set_stdout_encoding_to_utf_8:
    This function sets the encoding for the standard output to utf-8.

    @params:
        None
    @return:
        None
"""

def set_stdout_encoding_to_utf_8() -> None:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.encoding = 'uft-8'


"""
get_fab_cli_executable_path:
    This function fetches the fabric executable. It checks whether program is run
    inside a virtual env or not and fetches respective path for fabric cli executable
    for Mac OS.

    @params:
        None
    @return:
        path to fabric cli executable: str
"""

def get_fab_cli_executable_path() -> str:
    if hasattr(sys, "prefix") and hasattr(sys, "base_prefix"):
        return str(Path(sys.prefix) / "bin" / "fab") if sys.prefix != sys.base_prefix else str(Path(sys.base_prefix) / "bin" / "fab")
    else:
        return shutil.which("fab") or "fab"
    



