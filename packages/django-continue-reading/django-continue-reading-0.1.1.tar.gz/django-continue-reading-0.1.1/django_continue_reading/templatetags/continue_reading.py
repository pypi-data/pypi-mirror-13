from django import template
import re


register = template.Library()


@register.inclusion_tag('django_continue_reading/templatetags/continue_reading.html')
def continue_reading(post=None, word_limit=None):
    words_in_body = re.split(r'[^0-9A-Za-z]+', str(post.body))
    word_count = len(words_in_body)
    if word_count > word_limit:
        new_body = ' '.join(words_in_body[:word_limit]) + '...'
        return {'new_body': new_body, 'post_url': post.get_absolute_url,
                'link_text': 'continue reading'}
    else:
        return {'new_body': post.body, 'post_url': '', 'link_text': ''}
