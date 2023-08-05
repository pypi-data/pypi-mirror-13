import mock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.template import Context, Template
from django.utils import unittest

from .models import Example, NullableExample
from .utils import FakeCrocodocRequestMixin, TEST_DOC_DATA, TEST_DOC_NAME


class TestCrocoField(FakeCrocodocRequestMixin, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create sample data and store it on the class."""
        super(TestCrocoField, cls).setUpClass()
        example = Example.objects.create(
            name='Test item',
            document=SimpleUploadedFile(TEST_DOC_NAME, TEST_DOC_DATA),
        )
        # Reload the object from the database in order to ensure it's the correct type.
        # Example.objects.create() returns a SimpleUploadedFile for some reason.
        cls.instance = Example.objects.get(id=example.id)

    def render(self, tmpl):
        tmplout = "{% load croco_tags %}{% autoescape off %}"
        tmplout += tmpl
        tmplout += "{% endautoescape %}"
        return Template(tmplout).render(Context({'obj': self.instance}))

    def assertContains(self, test_value, expected_set):
        # That assert method does not exist in Py2.6
        msg = "%s does not contain %s" % (test_value, expected_set)
        self.assert_(test_value not in expected_set, msg)

    def test_document_empty(self):
        # Ensure document can be empty
        instance = Example.objects.create(name='Test empty')
        self.assertEqual(instance.document, '')

    def test_document_null(self):
        # Ensure document can be null
        instance = NullableExample.objects.create(name='Test empty')
        self.assertEqual(instance.document, None)

    def test_document_name(self):
        # Ensure document has correct name
        self.assertEqual(self.instance.document.name, TEST_DOC_NAME)

    def test_document_size(self):
        # Ensure correct size
        self.assertEqual(self.instance.document.size, 679)
        self.assertEqual(self.instance.document.size_human, u'679\xa0bytes')

    def test_document_type(self):
        # Ensure correct file type
        self.assertEqual(self.instance.document.type, 'pdf')

    def test_document_uuid(self):
        # Ensure correct length of UUID
        # UUID is 32 long chars, but there is 36 including dash chars
        uuid = self.instance.document.uuid
        self.assertEqual(len(uuid), 36)

    def test_document_url(self):
        # Ensure correct URL was returned for `url`
        url = self.instance.document.url
        expected_url = reverse(
            'croco_document_url',
            kwargs={'uuid': self.instance.document.uuid},
        )
        self.assertEqual(url, expected_url)

    def test_document_content_url(self):
        # Ensure correct URL for `content_url`
        content_url = self.instance.document.content_url
        expected_url = reverse(
            'croco_document_content_url',
            kwargs={'uuid': self.instance.document.uuid},
        )
        self.assertEqual(content_url, expected_url)

    def test_document_download(self):
        # Ensure correct URL for `download_document`
        document_url = self.instance.document.download_document
        expected_url = reverse(
            'croco_document_download',
            kwargs={'uuid': self.instance.document.uuid},
        )
        self.assertEqual(document_url, expected_url)

    def test_document_thumbnail_custom_field(self):
        # get filename with correct path
        uuid = self.instance.document.uuid
        filename = self.instance.my_thumbnail.field.upload_to + uuid
        # thumbnail should not exist yet
        self.assertFalse(self.instance.my_thumbnail.storage.exists(filename + '.png'))
        # create thumbnail
        with mock.patch.object(
            self.instance.my_thumbnail.storage,
            'url',
            return_value='http://testserver/image.png',
        ):
            self.instance.document.thumbnail
        # ensure it is saved in custom thumbnail field
        self.assertTrue(self.instance.my_thumbnail.storage.exists(filename + '.png'))

    def test_thumbnail_download(self):
        # Ensure correct URL for `download_thumbnail`
        thumbnail_url = self.instance.document.download_thumbnail
        expected_url = reverse(
            'croco_thumbnail_download',
            kwargs={'uuid': self.instance.document.uuid},
        )
        self.assertEqual(thumbnail_url, expected_url)

    def test_text_download(self):
        # Ensure correct URL for `download_text`
        text_url = self.instance.document.download_text
        expected_url = reverse(
            'croco_text_download',
            kwargs={'uuid': self.instance.document.uuid},
        )
        self.assertEqual(text_url, expected_url)
