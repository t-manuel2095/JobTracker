from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import JobApplicationViewSet, StatusHistoryViewSet, JobStatsViewSet

router = DefaultRouter()
router.register(r'jobs', JobApplicationViewSet, basename='job-application')
router.register(r'stats', JobStatsViewSet, basename='job-stats')

# Nested router - StatusHistory nested under jobs
jobs_router = routers.NestedDefaultRouter(router, r'jobs', lookup='job_application')
jobs_router.register(r'history', StatusHistoryViewSet, basename='job-status-history')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(jobs_router.urls)),
]