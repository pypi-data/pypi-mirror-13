from django.template import Template, Context
from django.test import TestCase
from .models import TestPost


class TemplateTagsTest(TestCase):

    def test_continue_reading(self):
        TestPost(title="Test Post", body="Lorem ipsum dolor sit amet consectetur")
        template = Template("{% load continue_reading %}"
                            "{% continue_reading post 3 %}")
        context = Context({"post": TestPost})
        result = template.render(context)
        expected = '<div class="body-filter">\n    ' \
                   '<p id="truncated-post"><p></p></p>\n    ' \
                   '<a id="continue" href=""></a>\n' \
                   '</div>'
        self.assertEqual(result, expected)
