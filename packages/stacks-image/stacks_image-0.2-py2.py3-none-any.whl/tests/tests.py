from __future__ import unicode_literals
import json

from django.contrib.auth.models import User
from django.test import Client, TestCase

from stacks_image.models import StacksImageList


class StacksImageTestCase(TestCase):
    """The test suite for stacks-image."""

    fixtures = ['stacksimage.json']
    maxDiff = None

    def setUp(self):
        """Set up the test suite."""
        password = '12345'
        user = User.objects.create_user(
            username='test_user',
            email='user@test.com',
            password=password
        )
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        user_client = Client()
        user_login = user_client.login(
            username='test_user',
            password=password
        )
        self.assertTrue(user_login)
        self.user = user
        self.user_client = user_client
        self.imagelist = StacksImageList.objects.get()

    def test_instances(self):
        """Test the test StacksImageList instance."""
        self.assertEqual(
            self.imagelist.pk,
            1
        )
        self.assertEqual(
            self.imagelist.__str__(),
            'Test Image List'
        )
        self.assertEqual(
            self.imagelist.images.all()[0].__str__(),
            'Django Logo'
        )
        self.assertEqual(
            self.imagelist.stacksimagelistimage_set.all()[
                0
            ].__str__(),
            'Test Image List 1. Django Logo'
        )

    def test_list_serialization(self):
        """Test the StacksImageList textplusstuff serializer."""
        response = self.client.get(
            '/textplusstuff/stacks_image/'
            'stacksimagelist/detail/1/'
        )
        self.assertEqual(
            response.status_code,
            200
        )
        self.assertEqual(
            json.loads(response.content)['context'],
            {
                "name": "Test Image List",
                "display_title": "A test list of images",
                "extra_context": {},
                "images": [
                    {
                        "name": "Django Logo",
                        "display_title": "The Django Logo",
                        "extra_context": {},
                        "image": {
                            "full_size": (
                                "/media/stacks_image/django-logo-green.png"
                            )
                        },
                        "optional_content": {
                            "as_plaintext": (
                                "This is a picture of the django logo!\n"
                            ),
                            "as_html": (
                                "<p>This is a <em>picture</em> of the <strong>"
                                "django logo</strong>!</p>\n"
                            ),
                            "raw_text": (
                                "This is a _picture_ of the **django logo**!"
                            ),
                            "as_html_no_tokens": (
                                "<p>This is a <em>picture</em> of the <strong>"
                                "django logo</strong>!</p>\n"
                            ),
                            "as_markdown": (
                                "This is a _picture_ of the **django logo**!"
                            )
                        }
                    },
                    {
                        "name": "Django Pony",
                        "display_title": "",
                        "extra_context": {},
                        "image": {
                            "full_size": (
                                "/media/stacks_image/django-pony-pink.png"
                            )
                        },
                        "optional_content": {
                            "as_plaintext": (
                                "This is a picture of the django pony.\n"
                            ),
                            "as_html": (
                                "<p>This is a <em>picture</em> of the <strong>"
                                "django pony</strong>.</p>\n"
                            ),
                            "raw_text": (
                                "This is a _picture_ of the **django pony**."
                            ),
                            "as_html_no_tokens": (
                                "<p>This is a <em>picture</em> of the <strong>"
                                "django pony</strong>.</p>\n"
                            ),
                            "as_markdown": (
                                "This is a _picture_ of the **django pony**."
                            )
                        }
                    },
                    {
                        "name": "Python Logo",
                        "display_title": "",
                        "extra_context": {},
                        "image": {
                            "full_size": "/media/stacks_image/python-logo.png"
                        },
                        "optional_content": {
                            "as_plaintext": (
                                "This is a picture of the python logo.\n"
                            ),
                            "as_html": (
                                "<p>This is a <em>picture</em> of the <strong>"
                                "python logo</strong>.</p>\n"
                            ),
                            "raw_text": (
                                "This is a _picture_ of the **python logo**."
                            ),
                            "as_html_no_tokens": (
                                "<p>This is a <em>picture</em> of the <strong>"
                                "python logo</strong>.</p>\n"
                            ),
                            "as_markdown": (
                                "This is a _picture_ of the **python logo**."
                            )
                        }
                    }
                ]
            }
        )
