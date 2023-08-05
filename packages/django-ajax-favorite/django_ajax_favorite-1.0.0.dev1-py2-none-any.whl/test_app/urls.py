from django.conf.urls import patterns, url
from views import ArticleDetailView, ArticleListView

urlpatterns = patterns(
    '',
    url(
        r'^article/list/(?P<pk>[0-9]+)/$',
        ArticleDetailView.as_view(), name='article-detail'),
    url(r'^$', ArticleListView.as_view(), name='article-list'),


)
