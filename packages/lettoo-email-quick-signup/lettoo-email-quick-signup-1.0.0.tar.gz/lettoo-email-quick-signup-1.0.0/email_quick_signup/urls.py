from django.views.generic import TemplateView
from django.conf.urls import patterns, url

from .views import RegisterView, VerifyEmailView

urlpatterns = patterns(
    '',
    url(r'^$', RegisterView.as_view(), name='email_quick_register'),
    url(r'^verify-email/$', VerifyEmailView.as_view(), name='email_quick_verify_email'),
)
