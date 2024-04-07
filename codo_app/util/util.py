from codo_app.util.log import *

from os import remove, path
import shutil

def delete_files(path_folder:str, path_pdf:str):
    """Delete all files from one commission, pdf file and folder content all pdf

    Args:
        path_folder (str): Path from folder with pdf files
        path_pdf (str): Path from pdf

    Returns:
        bool: Return True if delete everything
    """
    if path.exists(path_folder) and path.exists(path_folder) :
        shutil.rmtree(path_folder)
        remove(path_pdf)
        l(__name__, f"Delete pdf: {path_pdf}")
        l(__name__, f"Delete folder: {path_folder}")
        return True
    
    l(__name__, f"Can't delete file: {path_pdf}")
    l(__name__, f"Can't delete folder: {path_folder}")
    
    return False
