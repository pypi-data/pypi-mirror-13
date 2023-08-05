from models import Article
from django.views.generic import DetailView
from django.views.generic.list import ListView


class ArticleDetailView(DetailView):

    model = Article
    template_name = "test_app/article_detail.html"


class ArticleListView(ListView):

    model = Article
    template_name = "test_app/article_list.html"

    def get_context_data(self, **kwargs):
        context = super(ArticleListView, self).get_context_data(**kwargs)
        return context
