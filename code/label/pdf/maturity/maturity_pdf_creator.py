import os

from code.label.pdf.pdf_creator import PDFCreator


class MaturityPDFCreator(PDFCreator):
    def __init__(self):
        super().__init__()

    def _get_templates_path(self):
        return os.path.dirname(os.path.abspath(__file__)) + '/templates'

    def _generate_data(self):
        """
        Generate the data for a maturity
        @return:
        """

        # TO FILL

        data = {

        }

        return data
