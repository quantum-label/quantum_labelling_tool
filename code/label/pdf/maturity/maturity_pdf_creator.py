import os
from datetime import datetime

import code.label.label as label
from code.label.pdf.pdf_creator import PDFCreator
from webapp.models import MaturityAssessment


class MaturityPDFCreator(PDFCreator):
    def __init__(self, assessment: MaturityAssessment):
        super().__init__()

        self.assessment = assessment

    def _get_templates_path(self):
        return os.path.dirname(os.path.abspath(__file__)) + '/templates'

    def _generate_data(self):
        """
        Generate the data for a maturity
        @return:
        """

        maturity_dictionary, score = label.compute_maturity_score(assessment=self.assessment)
        data = {
            'label': label.plot_maturity(self.assessment, output_type='img'),
            'organization': self.assessment.organization,
            'assessment': self.assessment,
            'score': score,
            'maturity_assessment': maturity_dictionary,
            'date': self.assessment.date.strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
        }

        return data
