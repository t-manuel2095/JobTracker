from django.shortcuts import render
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions, serializers, status
from .permissions import IsOwner
from .models import JobApplication, StatusHistory
from . import serializers 
from datetime import datetime
from dateutil.relativedelta import relativedelta
        

class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all()
    serializer_class = serializers.JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    #Standard filtering options
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'company']
    search_fields = ['company', 'role']
    ordering_fields = ['applied_date', 'created_at']
    ordering = ['-applied_date']

    #Without this, the user won't be automatically assigned when creating a job.
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StatusHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.StatusHistorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        # job_application_pk comes from the nested router
        job_id = self.kwargs.get('job_application_pk')
        return StatusHistory.objects.filter(
            job_id=job_id,
            job__user=self.request.user
        )

class JobStatsViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    #return analytics and statistiics for users job application
    @action(detail=False, methods=['get'])
    def stats(self, request):
        user = request.user
        
        # Single optimized aggregate query
        stats_result = JobApplication.objects.filter(user=user).aggregate(
            total_apps=Count('id'),
            applied_count=Count('id', filter=Q(status='applied')),
            interview_count=Count('id', filter=Q(status='interview')),
            offer_count=Count('id', filter=Q(status='offer')),
            rejected_count=Count('id', filter=Q(status='rejected')),
        )
        
        # Extract values
        total = stats_result['total_apps']
        applied = stats_result['applied_count']
        interviews = stats_result['interview_count']
        offers = stats_result['offer_count']
        rejected = stats_result['rejected_count']
        
        # Calculate percentages
        applied_pct = (applied / total * 100) if total > 0 else 0
        interview_pct = (interviews / total * 100) if total > 0 else 0
        offer_pct = (offers / total * 100) if total > 0 else 0
        rejected_pct = (rejected / total * 100) if total > 0 else 0
        
        # Success and rejection rates
        success_rate = (offers / total * 100) if total > 0 else 0
        rejection_rate = (rejected / total * 100) if total > 0 else 0
        
        stats_data = {
            'total_applications': total,
            'status_breakdown': {
                'applied': applied,
                'interview': interviews,
                'offer': offers,
                'rejected': rejected,
            },
            'status_percentages': {
                'applied': round(applied_pct, 2),
                'interview': round(interview_pct, 2),
                'offer': round(offer_pct, 2),
                'rejected': round(rejected_pct, 2),
            },
            'offers': offers,
            'rejections': rejected,
            'interviews': interviews,
            'success_rate_percentage': round(success_rate, 2),
            'rejection_rate_percentage': round(rejection_rate, 2),
        }
        
        serializer = serializers.JobStatsSerializer(stats_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def detailed_stats(self, request):
        """Return detailed timeline-based statistics and trend analysis"""

        user = request.user
        jobs = JobApplication.objects.filter(user=user)
        
        # Basic aggregation
        total = jobs.count()
        offers = jobs.filter(status='offer').count()
        rejected = jobs.filter(status='rejected').count()
        success_rate = (offers / total * 100) if total > 0 else 0
        rejection_rate = (rejected / total * 100) if total > 0 else 0
        
        # Status breakdown
        status_breakdown = jobs.values('status').annotate(count=Count('id'))
        status_dict = {item['status']: item['count'] for item in status_breakdown}
        
        status_counts = {
            'applied': status_dict.get('applied', 0),
            'interview': status_dict.get('interview', 0),
            'offer': status_dict.get('offer', 0),
            'rejected': status_dict.get('rejected', 0),
        }
        
        # Calculate percentages
        status_percentages = {}
        for status, count in status_counts.items():
            pct = (count / total * 100) if total > 0 else 0
            status_percentages[status] = round(pct, 2)
        
        # Timeline - Applications by month (last 6 months)
        applications_by_month = []
        six_months_ago = datetime.now() - relativedelta(months=6)
        
        for i in range(6):
            month_start = six_months_ago + relativedelta(months=i)
            month_end = month_start + relativedelta(months=1)
            
            count = jobs.filter(
                applied_date__gte=month_start.date(),
                applied_date__lt=month_end.date()
            ).count()
            
            applications_by_month.append({
                'month': month_start.strftime('%Y-%m'),
                'applications': count
            })
        
        # Average days to interview/offer
        interview_times = []
        offer_times = []
        
        for job in jobs:
            first_interview = StatusHistory.objects.filter(
                job=job,
                new_status='interview'
            ).order_by('changed_at').first()
            
            if first_interview:
                days = (first_interview.changed_at.date() - job.applied_date).days
                interview_times.append(days)
            
            first_offer = StatusHistory.objects.filter(
                job=job,
                new_status='offer'
            ).order_by('changed_at').first()
            
            if first_offer:
                days = (first_offer.changed_at.date() - job.applied_date).days
                offer_times.append(days)
        
        avg_days_to_interview = sum(interview_times) / len(interview_times) if interview_times else 0
        avg_days_to_offer = sum(offer_times) / len(offer_times) if offer_times else 0
        
        # Build response
        stats_data = {
            'total_applications': total,
            'status_breakdown': status_counts,
            'status_percentages': status_percentages,
            'applications_by_month': applications_by_month,
            'average_days_to_interview': round(avg_days_to_interview, 2),
            'average_days_to_offer': round(avg_days_to_offer, 2),
            'success_rate_percentage': round(success_rate, 2),
            'rejection_rate_percentage': round(rejection_rate, 2),
        }
        
        serializer = serializers.DetailedStatsSerializer(stats_data)
        return Response(serializer.data)