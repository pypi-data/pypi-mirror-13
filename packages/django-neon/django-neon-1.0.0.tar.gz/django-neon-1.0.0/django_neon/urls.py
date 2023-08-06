"""
django-neon url-configuration

To use django-neon include this file in the url-patterns of the project.
Here is an example how the configuration can look like (in production
you may want to rename 'admin/' and should use https):

    from django_neon.views import HomePageView

    urlpatterns = [
        url(r'^admin/', include(admin.site.urls)),
        url(r'^page/', include('django_neon.urls')),
        url(r'^$',
            HomePageView.as_view(),
            name='neonhome'),
    ]

"""


from django.conf.urls import url
from .views import PageView


urlpatterns = [
    url(r'^(?P<pk>\d+)/(?P<slug>[\w-]+)/$',
        PageView.as_view(),
        name='neonpage'),
]
