from io import BytesIO

import httpretty
from PIL import Image


def simple_png():
    """Create a 1x1 black png in memory and return a handle to it."""
    image_file = BytesIO()
    image = Image.new('RGBA', (1, 1))
    image.save(image_file, 'png')
    image_file.name = 'test.png'
    image_file.url = 'http://testserver' + image_file.name
    image_file._committed = True
    image_file.seek(0)
    return image_file


# simple 1-page pdf saying 'Hello, world!'
TEST_DOC_DATA = (  # Multiline string, not tuple.
    '%PDF-1.7\n\n1 0 obj  % entry point\n<<\n  /Type /Catalog\n  /Pages 2 0 '
    'R\n>>\nendobj\n\n2 0 obj\n<<\n  /Type /Pages\n  /MediaBox [ 0 0 200 200 '
    ']\n  /Count 1\n  /Kids [ 3 0 R ]\n>>\nendobj\n\n3 0 obj\n<<\n  /Type '
    '/Page\n  /Parent 2 0 R\n  /Resources <<\n    /Font <<\n      /F1 4 0 R \n'
    '    >>\n  >>\n  /Contents 5 0 R\n>>\nendobj\n\n4 0 obj\n<<\n  /Type '
    '/Font\n  /Subtype /Type1\n  /BaseFont /Times-Roman\n>>\nendobj\n\n5 0 obj'
    '  % page content\n<<\n  /Length 44\n>>\nstream\nBT\n70 50 TD\n/F1 12 '
    'Tf\n(Hello, world!) Tj\nET\nendstream\nendobj\n\nxref\n0 6\n0000000000 '
    '65535 f \n0000000010 00000 n \n0000000079 00000 n \n0000000173 00000 n '
    '\n0000000301 00000 n \n0000000380 00000 n \ntrailer\n<<\n  /Size 6\n  '
    '/Root 1 0 R\n>>\nstartxref\n492\n%%EOF\n'
)
TEST_DOC_NAME = 'test_doc_file.pdf'


class FakeCrocodocRequestMixin(object):
    @classmethod
    def setUpClass(cls):
        """
        Disables a HTTP requests on socket's level as we do not need
        to test external API services.
        """
        httpretty.enable()
        httpretty.register_uri(
            httpretty.POST,
            "https://crocodoc.com/api/v2/document/upload",
            body='{"uuid": "8e5b0721-26c4-11df-b354-002170de47d3"}',
        )
        httpretty.register_uri(
            httpretty.GET,
            "https://crocodoc.com/api/v2/download/thumbnail",
            body=simple_png().read(),
        )
        httpretty.register_uri(
            httpretty.GET,
            "https://crocodoc.com/api/v2/download/document",
            body=TEST_DOC_DATA,
        )
        httpretty.register_uri(
            httpretty.GET,
            "https://crocodoc.com/api/v2/document/status",
            body='[{"uuid": "8e5b0721-26c4-11df-b354-002170de47d3"}]',
        )
        super(FakeCrocodocRequestMixin, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        """Disable `httpretty` to avoid crocodoc upload to be monkey patched."""
        httpretty.disable()
        super(FakeCrocodocRequestMixin, cls).tearDownClass()
