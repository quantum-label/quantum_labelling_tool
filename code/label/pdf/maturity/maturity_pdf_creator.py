import os
from datetime import datetime

import code.label.label as label
from code.label.pdf.pdf_creator import PDFCreator
from webapp.models import Organization


class MaturityPDFCreator(PDFCreator):
    def __init__(self, organization: Organization):
        super().__init__()

        self.organization = organization

    def _get_templates_path(self):
        return os.path.dirname(os.path.abspath(__file__)) + '/templates'

    def _generate_data(self):
        """
        Generate the data for a maturity
        @return:
        """

        # TO FILL

        maturity_dictionary, score = label.compute_maturity_score(organization=self.organization)
        data = {
            'label': label.plot_maturity(self.organization, output_type='img'),
            'organization': self.organization,
            'score': score,
            'maturity_assessment': maturity_dictionary,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '0.1',
        }

        return data
