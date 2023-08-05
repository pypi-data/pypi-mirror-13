from django.conf.urls import patterns, url
from views import FavAlterView


urlpatterns = patterns(
    '',
    url(
        r'^alter/fav/$',
        FavAlterView.as_view(), name='fav-alter'),

)
