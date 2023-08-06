# django-lightpdf

[![Build Status](https://travis-ci.org/claudiutopriceanu/django-lightpdf.svg?branch=master)](https://travis-ci.org/claudiutopriceanu/django-lightpdf)


Installation
------------

``django-lightpdf`` depends on pdfkit and wkthmltopdf (v0.12.2.1 recommended).

    sudo apt-get update
    sudo apt-get install -y xorg xfonts-75dpi
    wget http://download.gna.org/wkhtmltopdf/0.12/0.12.2.1/wkhtmltox-0.12.2.1_linux-wheezy-amd64.deb
    sudo dpkg -i wkhtmltox-0.12.2.1_linux-wheezy-amd64.deb

    pip install pdfkit==0.5.0 django-lightpdf


Configuration
-------------

We need to hook ``django-lightpdf`` into our project.

1. Put ``lightpdf`` into your ``INSTALLED_APPS`` in settings module::

    ```  
    INSTALLED_APPS = (
     ...
     'lightpdf',
    )
    ```

2. To control logging behaviour, add a ``LIGHTPDF_LOGGING_CONFIG`` dictionary to your settings file following ``logging.config.dictConfig`` schema.

3. Put a ``lightpdf`` formatter into your LOGGING['formatters'] or the default value will be used.

    ```
    DEFAULT_LOGGING_FORMATTER = {
        'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
    }
    ```

4. Put a ``lightpdf`` handler into your LOGGING['handlers'] or the default value will be used.

    ```
    DEFAULT_LOGGING_HANDLER = {
        'level': 'INFO',
        'class': 'logging.StreamHandler',
        'formatter': 'lightpdf'
    }
    ```

5. Put a ``lightpdf`` handler into your LOGGING['loggers'] or the default value will be used.

    ```
    DEFAULT_LOGGER = {
        'handlers': ['lightpdf'],
        'level': 'INFO',
    }
    ```

6. Add a ``LIGHTPDF_PDFKIT_OPTIONS`` dictionary that will be used as kwargs for ``pdfkit.from_string()`` or the default values will be used.

    ```
    PDFKIT_OPTIONS = {
        'page-size': 'Letter',
        'margin-top': '1.2in',
        'margin-right': '0.75in',
        'margin-bottom': '1.2in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None,
        'quiet': '',
    }
    ```


Usage
-----
    ```
    from django.views.generic import TemplateView
    from lightpdf.mixins import PdfGeneratorMixin


    class PdfView(PdfGeneratorMixin, TemplateView):
        template_name = 'blah.html'
        pdf_name = 'superblah'

        def get(self, request, *args, **kwargs):
            return self.render_to_pdf_response()
    ```

