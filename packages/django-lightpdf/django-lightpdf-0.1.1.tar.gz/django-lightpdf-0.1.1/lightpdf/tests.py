from django.test import RequestFactory, TestCase
from django.views.generic import TemplateView

from lightpdf.mixins import PdfGeneratorMixin


class PdfView(PdfGeneratorMixin, TemplateView):
    template_name = 'blah.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_pdf_response()

    def render_to_string(self):
        return '<p>blah</p>'


class PdfGeneratorMixinTestCase(TestCase):

    factory = RequestFactory()

    def tearDown(self):
        PdfView.pdf_name = None

    def test_pdf_name_not_specified(self):
        request = self.factory.get('/rand')
        view = PdfView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, 'We had some errors while generating PDF')
        self.assertEqual(response['content-type'], 'text/html; charset=utf-8')

    def test_pdf_ok(self):
        request = self.factory.get('/rand')
        PdfView.pdf_name = 'blah'
        view = PdfView.as_view()
        response = view(request)
        self.assertEqual(response['content-type'], 'application/pdf')
