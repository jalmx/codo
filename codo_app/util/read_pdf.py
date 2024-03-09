from os import makedirs
from os.path import join, basename
from PyPDF2 import PdfReader, PdfWriter
from uuid import uuid4


class ReadDataPDF:

    def __init__(self, path_pdf: str | None = None):
        self.path_pdf = path_pdf

    def _get_foliate(self, content: str) -> str | None:

        token = "Oficio número"

        for line in content:
            if len(line.strip()):
                position = line.find(token)
                if position != -1:
                    foliate = (
                        line[position + len(token) :].replace(" ", "").replace(".", "")
                    )
                    return foliate

        return None

    def _get_name_person(self, content: list) -> str | None:
        token = "Coatzacoalcos".upper()

        for i in range(len(content)):
            if content[i].upper().startswith(token):
                count = 1
                while True:
                    if len(content[i + count].strip()):
                        return content[i + count].strip()
                        break
                    count += 1
        return None

    def get_data(self, path_pdf: str = None):
        path_pdf = path_pdf or self.path_pdf

        pdf = PdfReader(path_pdf)
        self.data = []
        for page in pdf.pages:
            information = {}
            content = page.extract_text().split("\n")

            # for line in content:
            #     if self._get_foliate(line):
            information["foliate"] = self._get_foliate(content) or ""

            name = self._get_name_person(content)

            if name:
                information["name"] = name
                self.data.append(information)

        return self.data

    def _get_name_folder(self, name_file: str) -> str:
        """Get the name without extension fila

        Args:
            name_file (str): name from file pdf

        Returns:
            str: name clear
        """
        return basename(name_file).replace(".pdf", "")

    def _is_not_all(self, pdf: list) -> bool:
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

    def _save_pdf(self, path_pdf: str, path_dist: str, split: int):
        """Save all pdf files in a folder

        Args:
            path_pdf (str): Path pdf file with all commissions
            path_dist (str): Destination to save all commissions
            split (int): count of pages for each file
        """

        pdf = PdfReader(path_pdf).pages
        count = 0
        total_pages = len(pdf)

        if self._is_not_all(pdf):
            total_pages -= 1

        information =[]
        

        while total_pages > count:
            count_inside = 0
            writer = PdfWriter()
            # print(f"saving pdf {count}")
            name = None
            foliate = None
            while count_inside < split:

                if not name:
                    content = pdf[count].extract_text().split("\n")
                    name = self._get_name_person(content).replace(" ", "_") or None
                    foliate = self._get_foliate(content).replace("/", "_") or None

                writer.add_page(pdf[count])
                count_inside += 1
                count += 1

            name = name if name else str(uuid4())
            foliate = foliate if foliate else ""

            # print(f" name person for document: {name } - {foliate}")
            path_to_save = join(
                path_dist, f"{self._get_name_folder(path_pdf)}_{name}_{foliate}.pdf"
            )

            # print(f"path to save: {path_to_save}")
            with open(path_to_save, mode="wb") as f:
                writer.write(f)

            information.append(
                {
                    "path_file": path_to_save,
                    "name":name,
                    "foliate": foliate
                }
            )
            
        return information
    

    def _is_one(self, pdf: list) -> bool:

        n_1 = len(pdf[0].extract_text().split())
        n_2 = len(pdf[1].extract_text().split())
        n_3 = len(pdf[2].extract_text().split())

        single = int((n_1 / n_2) - 1) - int((n_1 / n_3) - 1)

        if single == 0:
            return True
        else:
            return False

    def _get_number_to_split(self, pdf: list) -> int:
        n_split = 1

        if self._is_one(pdf):
            return n_split
        else:
            return n_split + 1

    def split(self, path_pdf: str | None = None, path_dist: str | None = None):
        path_pdf = path_pdf or self.path_pdf

        pdf = PdfReader(path_pdf).pages

        folder_name = path_dist or self._get_name_folder(path_pdf)

        # print(f"name folder: {folder_name}")

        c = self._get_number_to_split(pdf)

        makedirs(folder_name, exist_ok=True)

        return self._save_pdf(path_pdf, path_dist=folder_name, split=c)


if __name__ == "__main__":
    path_file = [
        "comision_6.pdf",
        "comision_1.pdf",
        "comision_2.pdf",
        "comision_3.pdf",
        "comision_4.pdf",
        "comision_5.pdf",
    ]

    for file in path_file:

        datas = ReadDataPDF(file)

        print(datas.get_data())
        print(datas.split())
        break
