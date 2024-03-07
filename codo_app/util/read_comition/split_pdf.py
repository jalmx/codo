from os import makedirs
from PyPDF2 import PdfReader


def _get_name_folder(name_file: str) -> str:
    """Get the name without extension fila

    Args:
        name_file (str): name from file pdf

    Returns:
        str: name clear
    """
    return name_file.replace(".pdf", "")


def _save_pdf(name: str, dist: str):
    pass


def _is_not_all(pdf: list) -> bool:
    factor = 0.85

    total = 0
    max_content = 0

    for page in pdf:
        content = len(page.extract_text().strip())
        total += content

        if max_content < content:
            max_content = content

    content_length = len(pdf[-1].extract_text().strip())
    last_count = content_length / max_content

    if last_count < factor:
        return True

    return False


def _is_one(pdf: list) -> bool:

    n_1 = len(pdf[0].extract_text().split())
    n_2 = len(pdf[1].extract_text().split())
    n_3 = len(pdf[2].extract_text().split())

    single = int((n_1 / n_2) - 1) - int((n_1 / n_3) - 1)

    if single == 0:
        return True
    else:
        return False


def _get_number_to_split(pdf: list) -> int:
    n_split = 1
    total_pages = len(pdf)

    if _is_not_all(pdf):
        total_pages -= 1

    if _is_one(pdf):
        return n_split
    else:
        return n_split + 1


def split(path_pdf: str, path_dist: str | None = None):
    pdf = PdfReader(path_pdf).pages

    folder_name = _get_name_folder(path_pdf)

    print(f"name folder: {folder_name}")

    _get_number_to_split(pdf)


if __name__ == "__main__":
    path_file = ["comision_1.pdf", "./comision_2.pdf", "./comision_3.pdf"]

    for p in path_file:
        split(p)
        print("----------------------")
        # break
