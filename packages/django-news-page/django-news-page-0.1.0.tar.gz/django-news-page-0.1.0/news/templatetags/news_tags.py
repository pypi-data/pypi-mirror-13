from datetime import datetime
from django import template
from news.models import News

register = template.Library()


@register.inclusion_tag('news/news_widget.html')
def news_widget(num_latest=3):
    news_list = News.objects.filter(show=True).filter(date__lte=datetime.now()).order_by('-date')[:num_latest]
    return locals()

