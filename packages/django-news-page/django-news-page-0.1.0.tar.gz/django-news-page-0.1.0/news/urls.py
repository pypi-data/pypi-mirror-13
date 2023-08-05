from django.conf.urls import url
from news.views import NewsPage, NewsList

urlpatterns = [
    url(r'^$', NewsList.as_view(), name='news-list'),
    url(r'^(?P<slug>.*)/$', NewsPage.as_view(), name='news-page'),
]
