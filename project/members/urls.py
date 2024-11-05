from django.urls import path
from . import views
from .views import addinventors, addcorp, addrecipients,  addactivities, addPA, members, matters, fip_reports, merges, toolbox, addRelatedMatter
#from django.contrib import admin
# from .views import mergeEmailButton
from .views import testview

urlpatterns = [
    path('', members, name='members'),
    path('matters/', matters, name='matters'),
    path('merge_inventors/', addinventors, name = 'merge_inventors'),
    path('merge_recipients/', addrecipients, name = 'merge_recipients'),
    path('merge_corp/', addcorp, name = 'merge_corp'),
    #path('merge_SA/', addSA, name = 'merge_SA'),
    path('test/', testview, name='test'),
    path('merge_activities/', addactivities, name = 'merge_activities'),
    path('merge_PA/', addPA, name = 'merge_PA'),
    path('merge_RM/', addRelatedMatter, name = 'merge_RM'),

    path('fip-reports/', fip_reports, name='fip_reports'),
    path('merges/', merges, name='merges'),
    path('toolbox/', toolbox, name='toolbox'),
    
    #path('admin/', admin.site.urls),
]