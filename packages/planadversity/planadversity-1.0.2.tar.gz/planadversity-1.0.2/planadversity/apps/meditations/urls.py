from django.conf.urls import url
from .views import MeditationListView, MeditationDetailView, MeditationListJSONView, \
                   HomepageView, ResponseListView, ResponseDetailView, ResponseCreateView


# custom views
urlpatterns = [
    url(r'^meditations.json',
        view=MeditationListJSONView.as_view(),
        name="meditation-list-json"),

    url(r'^meditations/(?P<slug>[-\w]+)/',
        view=MeditationDetailView.as_view(),
        name="meditation-detail"),

    #url(r'^meditations.csv',
    #    view=MeditationListCSVView.as_view(),
    #    name="meditation-list-csv"),

    url(r'^meditations/$',
        view=MeditationListView.as_view(),
        name="meditation-list"),

    url(r'^responses/create/$',
        view=ResponseCreateView.as_view(),
        name="response-create"),

    url(r'^responses/(?P<slug>[-\w\d]+)/',
        view=ResponseDetailView.as_view(),
        name="response-detail"),

    url(r'^responses/$',
        view=ResponseListView.as_view(),
        name="response-list"),

    url("^$",
        view=HomepageView.as_view(),
        name="homepage")]
