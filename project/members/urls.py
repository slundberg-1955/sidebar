from django.urls import path
from . import views
from .views import addinventors, health_check, addcorp, addrecipients,  addactivities, addPA, members, matters, fip_reports, merges, toolbox, addRelatedMatter, checkMatter, addSA, get_doc_names, addassignee, addPCTSA
#from django.contrib import admin
# from .views import mergeEmailButton
from .views import testview
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', members, name='members'),
    path('matters/', matters, name='matters'),
    path('merge_inventors/', addinventors, name = 'merge_inventors'),
    path('merge_recipients/', addrecipients, name = 'merge_recipients'),
    path('merge_corp/', addcorp, name = 'merge_corp'),
    path('merge_SA/', addSA, name = 'merge_SA'),
    path('test/', testview, name='test'),
    path('merge_activities/', addactivities, name = 'merge_activities'),
    path('merge_PA/', addPA, name = 'merge_PA'),
    path('merge_RM/', addRelatedMatter, name = 'merge_RM'),
    path('merge_chkmatter/', checkMatter, name = 'merge_chkmatter'),
    path('merge_activity_docs/', get_doc_names, name = 'merge_activity_docs'),
    path('merge_assignee/', addassignee, name = 'merge_assignee'),
    path('merge_PCTSA/', addPCTSA, name = 'merge_PCTSA'),
    path('merge_issfee/', views.fillissuefee, name='merge_issfee'),

    path('edit_template/', views.edit_template, name='edit_template'),
    path('download_template/', views.download_template, name='download_template'),
    path('upload_template/', views.upload_template, name='upload_template'),

    path('fip-reports/', fip_reports, name='fip_reports'),
    path('merges/', merges, name='merges'),
    path('toolbox/', toolbox, name='toolbox'),
    
    path('health/', health_check, name='health_check'),
    #path('admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)