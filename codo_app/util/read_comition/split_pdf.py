from os import makedirs
from os.path import join, basename
from PyPDF2 import PdfReader, PdfWriter
from uuid import uuid4


def _get_name_folder(name_file: str) -> str:
    """Get the name without extension fila

    Args:
        name_file (str): name from file pdf

    Returns:
        str: name clear
    """
    return basename(name_file).replace(".pdf", "")


def _save_pdf(path_pdf: str, path_dist: str, split: int):
    """Save all pdf files in a folder

    Args:
        path_pdf (str): Path pdf file with all commissions
        path_dist (str): Destination to save all commissions
        split (int): count of pages for each file
    """
    
    pdf = PdfReader(path_pdf).pages
    count = 0
    total_pages = len(pdf)

    if _is_not_all(pdf):
        total_pages -= 1
    

    while total_pages > count:
        count_inside = 0
        writer = PdfWriter()
        print(f"saving pdf {count}")

        while count_inside < split:
            writer.add_page(pdf[count])
            count_inside += 1
            count += 1

        with open(
            join(path_dist, f"{_get_name_folder(path_pdf)}_{uuid4()}.pdf"), mode="wb"
        ) as f:
            writer.write(f)


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
   

    if _is_one(pdf):
        return n_split
    else:
        return n_split + 1


def split(path_pdf: str, path_dist: str | None = None):
    pdf = PdfReader(path_pdf).pages

    folder_name = path_dist or _get_name_folder(path_pdf)

    print(f"name folder: {folder_name}")

    c = _get_number_to_split(pdf)

    makedirs(folder_name, exist_ok=True)

    _save_pdf(path_pdf, path_dist=folder_name, split=c)


if __name__ == "__main__":
    path_file = [
        "comision_1.pdf",
        "comision_2.pdf",
        "comision_3.pdf",
        "comision_4.pdf",
        "comision_5.pdf",
        "comision_6.pdf",
    ]

    for p in path_file:
        split(p)
        print("----------------------")
