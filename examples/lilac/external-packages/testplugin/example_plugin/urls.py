from .views import example
from django.conf.urls import url


urlpatterns = [url(r"^example_view$", example, name="example-view")]
