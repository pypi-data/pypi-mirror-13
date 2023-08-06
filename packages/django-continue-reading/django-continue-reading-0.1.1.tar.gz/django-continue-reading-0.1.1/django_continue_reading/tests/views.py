from django.shortcuts import render


def post_detail(request, post):
    return render(request, '/post/detail.html', {'post': post})
