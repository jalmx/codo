from PyPDF2 import PdfReader


class ReadPDF:

    def __init__(self, path_pdf:str|None=None):
        self.path_pdf = path_pdf

    def _get_foliate(self, line: str) -> str | None:
        token = "Oficio número"
        if len(line.strip()):
            position = line.find(token)
            if position != -1:
                foliate = (
                    line[position + len(token) :].replace(" ", "").replace(".", "")
                )
                return foliate

        return None

    def _get_name_person(self, content: list):
        token = "Coatzacoalcos".upper()

        for i in range(len(content)):
            if content[i].upper().startswith(token):
                count = 1
                while True:
                    if len(content[i + count].strip()):
                        return content[i + count]
                        break
                    count += 1

    def get_data(self, path_pdf: str = None):
        path_pdf = path_pdf or self.path_pdf

        pdf = PdfReader(path_pdf)
        data = []
        for page in pdf.pages:
            information = {}
            content = page.extract_text().split("\n")

            for line in content:
                if self._get_foliate(line):
                    information["foliate"] = self._get_foliate(line)

            name = self._get_name_person(content)

            if name:
                information["name"] = name.strip()
                data.append(information)

        return data


if __name__ == "__main__":
    path_file = ["comision_1.pdf", "./comision_2.pdf", "./comision_3.pdf"]

    datas = ReadPDF(path_file[1]).get_data()
    print(datas)