from django.conf.urls import url

from .views import demo_view
urlpatterns = [
    url(r'^', demo_view)
]
