#from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name='mon_app'
urlpatterns=[
    #Monitoring Application
    path('', views.index, name='index'),
    path('index_content', views.index_content, name='index_content'),
    path('devices', views.devices, name='devices'),
    path('device/<str:device_name>', views.device, name='device'),
    path('device_content/<str:device_name>', views.device_content, name='device_content'),
    path('events', views.events, name='events'),
    path('events_content', views.events_content, name='events_content'),
    path('reports', views.reports, name='reports'),
    path('settings', views.settings, name='settings'),
]   

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
