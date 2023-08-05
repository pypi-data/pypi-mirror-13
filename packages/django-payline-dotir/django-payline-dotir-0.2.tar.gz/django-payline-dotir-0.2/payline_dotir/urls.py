from django.conf.urls import patterns, include, url
import views


urlpatterns = patterns('views',
    url(r'^pay/$', 'pay_form', name='pay_form'),
    url(r'^gateway/$', 'gateway', name='gateway'),
    url(r'^result/$', 'result', name='result'),
)
