from django.conf.urls.defaults import url

from . import views

urlpatterns = [
    url(r'^transaction/(?P<tx_id>[0-9]+)$', views.transaction_view, name='compropago_transaction_state'),
    url(r'^webhook/$', views.web_hook_view, name='compropago_webhook'),
]
