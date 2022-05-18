from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from rest_framework_swagger.views import get_swagger_view
from core import *
from core.views import LoginAPI
import pac.views as views

SCHEMA_VIEW = get_swagger_view(title='PAC Management API')

urlpatterns = [
    #url(r'^api/', include('pac.pre_costing.urls')),
    #url(r'^api/', include('pac.rrf.urls')),
    url(r'^api/', include('core.urls')),
    url(r'^schema/$', SCHEMA_VIEW),
    path("accounts/", include('rest_framework.urls')),

    path(
        'api/metadata/<int:user_id>/',
        views.get_metadata_pyodbc,
        name='metadata'
    ),

    path('api/login/',
         LoginAPI.as_view(),
         name='login'),

    path(
        'api/notification/batch-update/',
        views.NotificationBatchUpdateView.as_view(),
        name='notification-batch-update'
    ),
    path(
        'api/notification/<int:user_id>/',
        views.NotificationListView.as_view(),
        name='notification-list'
    ),
    path('api/rrf/<str:rrf_id>/comments/',
         views.comment_handler,
         name='comments'),
    path('api/rrf/<str:rrf_id>/comments/<str:comment_id>/',
         views.comment_handler,
         name='comments-id'),
    path('api/rrf/<str:rrf_id>/comments/<str:comment_id>/file/<str:file_name>',
         views.comment_file_handler,
         name='comment-file'),
    path('api/rrf/<str:rrf_id>/cost-override/',
         views.add_cost_override,
         name='cost-override'),

    path('api/rrf/<str:rrf_id>/comments/<str:comment_id>/replies',
         views.add_comment_reply,
         name='comment-replies'),

    path('api/account/<str:external_erp_id>',
         views.account_handler,
         name='account_handler'),

    path('api/account/',
         views.account_handler,
         name='account_handler'),

    # TODO remove before production
    path('api/sl/migrate',
         views.service_service_migration,
         name='service_service_migration')
]

urlpatterns += staticfiles_urlpatterns()
