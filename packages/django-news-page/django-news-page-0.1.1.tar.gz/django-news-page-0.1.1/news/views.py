from django.views import generic
from news.models import News


class NewsList(generic.ListView):
    model = News
    context_object_name = 'news_list'
    template_name = 'news/news_list.html'


class NewsPage(generic.DetailView):
    model = News
    context_object_name = 'news_entry'
    template_name = 'news/news_page.html'