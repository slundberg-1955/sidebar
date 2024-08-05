from django.urls import path
from . import views
from .views import mergeDocButton
from .views import addinventors, addcorp, addrecipients, addSA, addactivities
# from .views import mergeEmailButton
from .views import testview

urlpatterns = [
    path('', views.members),
    path('merge_doc/', mergeDocButton, name = 'merge_doc'),
    path('merge_inventors/', addinventors, name = 'merge_inventors'),
    path('merge_recipients/', addrecipients, name = 'merge_recipients'),
    path('merge_corp/', addcorp, name = 'merge_corp'),
    path('merge_SA/', addSA, name = 'merge_SA'),
    path('test/', testview, name='test'),
    path('merge_activities/', addactivities, name = 'merge_activities'),
]