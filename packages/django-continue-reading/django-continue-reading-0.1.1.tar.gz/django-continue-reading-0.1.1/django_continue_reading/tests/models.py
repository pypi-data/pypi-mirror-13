from django.db import models
from django.core.urlresolvers import reverse


class TestPost(models.Model):

    title = models.CharField(max_length=250)
    body = models.TextField()

    def get_absolute_url(self):
        return reverse('blog:post_detail',
                       args=[self.title])

    def __str__(self):
        return self.title
