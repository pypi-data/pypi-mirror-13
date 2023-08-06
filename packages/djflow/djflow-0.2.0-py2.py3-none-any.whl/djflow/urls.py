from django.conf.urls import *
from django.conf import settings
from apptools.forms import DefaultAppStartForm
from apptools.views import DefaultAppModel

urlpatterns = patterns('django.contrib.auth.views',
    (r'^.*/logout/$', 'logout'),
    (r'^.*/accounts/login/$', 'login', {'template_name':'djflow/login.html'}),
    (r'^apptools/', include('djflow.apptools.urls')),
    (r'^graph/', include('djflow.graphics.urls')),
)

urlpatterns += patterns('djflow.workflow.views',
    (r'^$', 'index'),
    (r'^process/dot/(?P<id>.*)$','process_dot'),
    (r'^cron/$','cron'),
)

urlpatterns += patterns('djflow.apptools.views',
    (r'^default_app/(?P<id>.*)/$', 'default_app'),
    (r'^start/(?P<app_label>.*)/(?P<model_name>.*)/$', 'start_application'),
    (r'^start_proto/(?P<process_name>.*)/$', 'start_application',
        {'form_class':DefaultAppStartForm,
         'redirect':'../../',
         'template':'djflow/start_proto.html'}),
)

urlpatterns += patterns('djflow.runtime.views',
    (r'^otherswork/$',                 'otherswork'),
    (r'^otherswork/instancehistory/$', 'instancehistory'),
    (r'^myrequests/$',                 'myrequests'),
    (r'^myrequests/instancehistory/$', 'instancehistory'),
    (r'^mywork/$',                     'mywork'),
    (r'^mywork/activate/(?P<id>.*)/$', 'activate'),
    (r'^mywork/complete/(?P<id>.*)/$', 'complete'),
)

