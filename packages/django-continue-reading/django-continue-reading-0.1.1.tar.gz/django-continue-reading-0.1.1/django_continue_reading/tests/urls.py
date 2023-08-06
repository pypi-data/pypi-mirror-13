from django.conf.urls import url
from .views import post_detail

urlpatterns = [
    url(r'(?P<post>[-\w]+)/$', post_detail, name='post_detail'),
]
