import logging

import pdfkit

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.template.loader import render_to_string

from lightpdf.settings import LIGHTPDF_PDFKIT_OPTIONS, LIGHTPDF_LOGGING_CONFIG


logging.config.dictConfig(LIGHTPDF_LOGGING_CONFIG)
logger = logging.getLogger(__name__)


class PdfGeneratorMixin(object):
    pdf_name = None

    def get_pdf_name(self):
        if self.pdf_name is None:
            raise ImproperlyConfigured(
                "PdfGeneratorMixin requires either a definition of "
                "'pdf_name' or an implementation of 'get_pdf_name()'")

    def render_to_string(self):
        return render_to_string(self.template_name, self.get_context_data())

    def render_to_pdf(self):
        return pdfkit.from_string(self.render_to_string(), False, options=LIGHTPDF_PDFKIT_OPTIONS)

    def render_to_pdf_response(self):
        try:
            pdf_name = self.get_pdf_name()
            pdf = self.render_to_pdf()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'filename="%s.pdf"'.format(pdf_name)
        except Exception as e:
            logger.error(e)
            response = HttpResponse('We had some errors while generating PDF')
        return response
