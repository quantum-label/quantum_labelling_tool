import os
from abc import ABC, abstractmethod
from io import BytesIO

from django.db.models import Sum
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


class PDFCreator(ABC):
    def __init__(self):
        self.templates_path = self._get_templates_path()
        self.html_files = self._get_html_files()

    def _get_html_files(self):
        """Get all HTML files from the current directory."""
        return [file for file in os.listdir(self.templates_path) if file.endswith('.html')]

    def generate_pdf(self) -> BytesIO:
        """Generate a PDF with one page per HTML file."""
        buffer = BytesIO()

        if not self.html_files:
            print("No HTML files found in the current directory.")
            return buffer

        pdf_pages = []

        data = self._generate_data()

        env = Environment(loader=FileSystemLoader(self.templates_path))
        for html_file in sorted(self.html_files):
            template = env.get_template(f'{html_file}')
            filled_html = template.render(data)

            html = HTML(string=filled_html, base_url=self.templates_path)

            pdf_pages.append(
                html.render(
                    data=data
                )
            )

        # Combine all pages
        combined_pdf = pdf_pages[0]
        for pdf in pdf_pages[1:]:
            combined_pdf.pages.extend(pdf.pages)

        combined_pdf.write_pdf(buffer)

        # Go to beginning of buffer
        buffer.seek(0)

        return buffer

    @abstractmethod
    def _generate_data(self):
        """ Implement in child classes to generate PDF content """
        pass

    @abstractmethod
    def _get_templates_path(self):
        """ Returns the path of the templates """
        pass
