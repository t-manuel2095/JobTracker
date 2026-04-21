from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework import serializers as drf_serializers
from ..models import JobApplication, StatusHistory
from ..serializers import (
    JobApplicationSerializer,
    StatusHistorySerializer,
    JobStatsSerializer,
    DetailedStatsSerializer
)


class JobApplicationSerializerTests(TestCase):
    """Test JobApplicationSerializer"""
    
    def setUp(self):
        """Create test user"""
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
    
    def test_serializer_valid_data(self):
        """Test serializer with valid data"""
        data = {
            'company': 'Google',
            'role': 'Software Engineer',
            'status': 'applied',
            'applied_date': '2026-04-01',
            'notes': 'Test notes'
        }
        serializer = JobApplicationSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
    
    def test_serializer_invalid_status(self):
        """Test serializer rejects invalid status"""
        data = {
            'company': 'Google',
            'role': 'Software Engineer',
            'status': 'invalid_status',
            'applied_date': '2026-04-01'
        }
        serializer = JobApplicationSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)
    
    def test_serializer_missing_required_fields(self):
        """Test serializer rejects missing required fields"""
        data = {
            'company': 'Google'
            # Missing required fields
        }
        serializer = JobApplicationSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('role', serializer.errors)
        self.assertIn('applied_date', serializer.errors)
    
    def test_serializer_read_only_fields(self):
        """Test serializer enforces read-only fields"""
        job = JobApplication.objects.create(
            user=self.user,
            company='Google',
            role='SWE',
            status='applied',
            applied_date='2026-04-01'
        )
        
        data = {
            'id': 999,
            'created_at': '2020-01-01T00:00:00Z',
            'user': 999,
            'company': 'Amazon'
        }
        
        serializer = JobApplicationSerializer(job, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        
        # Verify read-only fields weren't changed
        job.refresh_from_db()
        self.assertNotEqual(job.id, 999)
        self.assertNotEqual(job.user.id, 999)
        # Company should be updated
        self.assertEqual(job.company, 'Amazon')
    
    def test_serializer_update_method(self):
        """Test serializer update() method works"""
        job = JobApplication.objects.create(
            user=self.user,
            company='Google',
            role='SWE',
            status='applied',
            applied_date='2026-04-01'
        )
        
        data = {'company': 'Microsoft'}
        serializer = JobApplicationSerializer(job, data=data, partial=True)
        
        self.assertTrue(serializer.is_valid())
        updated_job = serializer.save()
        
        self.assertEqual(updated_job.company, 'Microsoft')
    
    def test_serializer_status_change_creates_history(self):
        """Test status change creates StatusHistory entry"""
        job = JobApplication.objects.create(
            user=self.user,
            company='Google',
            role='SWE',
            status='applied',
            applied_date='2026-04-01'
        )
        
        # No history yet
        self.assertEqual(StatusHistory.objects.filter(job=job).count(), 0)
        
        # Update status via serializer
        data = {'status': 'interview'}
        serializer = JobApplicationSerializer(job, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        
        # History should be created
        history = StatusHistory.objects.filter(job=job).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.old_status, 'applied')
        self.assertEqual(history.new_status, 'interview')
    
    def test_serializer_non_status_update_no_history(self):
        """Test non-status updates don't create history"""
        job = JobApplication.objects.create(
            user=self.user,
            company='Google',
            role='SWE',
            status='applied',
            applied_date='2026-04-01'
        )
        
        initial_count = StatusHistory.objects.filter(job=job).count()
        
        # Update notes (not status)
        data = {'notes': 'Updated notes'}
        serializer = JobApplicationSerializer(job, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        
        # No new history
        self.assertEqual(StatusHistory.objects.filter(job=job).count(), initial_count)
    
    def test_serializer_all_fields_present(self):
        """Test serializer includes all expected fields"""
        job = JobApplication.objects.create(
            user=self.user,
            company='Google',
            role='SWE',
            status='applied',
            applied_date='2026-04-01'
        )
        
        serializer = JobApplicationSerializer(job)
        expected_fields = {'id', 'user', 'company', 'role', 'status', 'applied_date', 'notes', 'created_at'}
        
        self.assertEqual(set(serializer.data.keys()), expected_fields)
    
    def test_serializer_partial_update(self):
        """Test partial update (PATCH)"""
        job = JobApplication.objects.create(
            user=self.user,
            company='Google',
            role='SWE',
            status='applied',
            applied_date='2026-04-01',
            notes='Original'
        )
        
        data = {'role': 'Senior SWE'}
        serializer = JobApplicationSerializer(job, data=data, partial=True)
        
        self.assertTrue(serializer.is_valid())
        updated_job = serializer.save()
        
        self.assertEqual(updated_job.role, 'Senior SWE')
        # Other fields unchanged
        self.assertEqual(updated_job.company, 'Google')
        self.assertEqual(updated_job.notes, 'Original')
    
    def test_serializer_full_update(self):
        """Test full update (PUT)"""
        job = JobApplication.objects.create(
            user=self.user,
            company='Google',
            role='SWE',
            status='applied',
            applied_date='2026-04-01'
        )
        
        data = {
            'company': 'Microsoft',
            'role': 'DevOps',
            'status': 'interview',
            'applied_date': '2026-04-02',
            'notes': 'Full update'
        }
        serializer = JobApplicationSerializer(job, data=data)
        
        self.assertTrue(serializer.is_valid())
        updated_job = serializer.save()
        
        self.assertEqual(updated_job.company, 'Microsoft')
        self.assertEqual(updated_job.role, 'DevOps')
        self.assertEqual(updated_job.status, 'interview')
        self.assertEqual(updated_job.notes, 'Full update')


class StatusHistorySerializerTests(TestCase):
    """Test StatusHistorySerializer"""
    
    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        self.job = JobApplication.objects.create(
            user=self.user,
            company='Google',
            role='SWE',
            status='applied',
            applied_date='2026-04-01'
        )
    
    def test_status_history_serializer_valid_data(self):
        """Test serializer with valid data"""
        history = StatusHistory.objects.create(
            job=self.job,
            old_status='applied',
            new_status='interview'
        )
        
        serializer = StatusHistorySerializer(history)
        
        self.assertEqual(serializer.data['old_status'], 'applied')
        self.assertEqual(serializer.data['new_status'], 'interview')
    
    def test_status_history_read_only_fields(self):
        """Test all fields are read-only"""
        history = StatusHistory.objects.create(
            job=self.job,
            old_status='applied',
            new_status='interview'
        )
        
        data = {
            'id': 999,
            'job': 999,
            'old_status': 'offer',
            'new_status': 'rejected',
            'changed_at': '2020-01-01T00:00:00Z'
        }
        
        serializer = StatusHistorySerializer(history, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        # Data shouldn't change (read-only)
        self.assertEqual(serializer.data['old_status'], 'applied')
        self.assertEqual(serializer.data['new_status'], 'interview')
    
    def test_status_history_contains_all_fields(self):
        """Test serializer includes all expected fields"""
        history = StatusHistory.objects.create(
            job=self.job,
            old_status='applied',
            new_status='interview'
        )
        
        serializer = StatusHistorySerializer(history)
        expected_fields = {'id', 'job', 'old_status', 'new_status', 'changed_at'}
        
        self.assertEqual(set(serializer.data.keys()), expected_fields)
    
    def test_status_history_serializer_for_list(self):
        """Test serializer works with multiple histories"""
        StatusHistory.objects.create(
            job=self.job, old_status='applied', new_status='interview'
        )
        StatusHistory.objects.create(
            job=self.job, old_status='interview', new_status='offer'
        )
        
        histories = StatusHistory.objects.all()
        serializer = StatusHistorySerializer(histories, many=True)
        
        self.assertEqual(len(serializer.data), 2)


class JobStatsSerializerTests(TestCase):
    """Test JobStatsSerializer"""
    
    def test_stats_serializer_valid_data(self):
        """Test serializer with valid stats data"""
        data = {
            'total_applications': 10,
            'status_breakdown': {
                'applied': 5,
                'interview': 3,
                'offer': 1,
                'rejected': 1
            },
            'status_percentages': {
                'applied': 50.0,
                'interview': 30.0,
                'offer': 10.0,
                'rejected': 10.0
            },
            'offers': 1,
            'rejections': 1,
            'interviews': 3,
            'success_rate_percentage': 10.0,
            'rejection_rate_percentage': 10.0
        }
        
        serializer = JobStatsSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_stats_serializer_invalid_data(self):
        """Test serializer rejects invalid data"""
        data = {
            'total_applications': 'not_a_number',
            'status_breakdown': {},
            'status_percentages': {},
            'offers': 1,
            'rejections': 1,
            'interviews': 3,
            'success_rate_percentage': 10.0,
            'rejection_rate_percentage': 10.0
        }
        
        serializer = JobStatsSerializer(data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_stats_serializer_contains_all_fields(self):
        """Test serializer includes all expected fields"""
        data = {
            'total_applications': 5,
            'status_breakdown': {'applied': 5, 'interview': 0, 'offer': 0, 'rejected': 0},
            'status_percentages': {'applied': 100.0, 'interview': 0.0, 'offer': 0.0, 'rejected': 0.0},
            'offers': 0,
            'rejections': 0,
            'interviews': 0,
            'success_rate_percentage': 0.0,
            'rejection_rate_percentage': 0.0
        }
        
        serializer = JobStatsSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        expected_fields = {
            'total_applications', 'status_breakdown', 'status_percentages',
            'offers', 'rejections', 'interviews', 'success_rate_percentage',
            'rejection_rate_percentage'
        }
        self.assertEqual(set(serializer.validated_data.keys()), expected_fields)


class DetailedStatsSerializerTests(TestCase):
    """Test DetailedStatsSerializer"""
    
    def test_detailed_stats_serializer_valid_data(self):
        """Test serializer with valid detailed stats data"""
        data = {
            'total_applications': 10,
            'status_breakdown': {
                'applied': 5, 'interview': 3, 'offer': 1, 'rejected': 1
            },
            'status_percentages': {
                'applied': 50.0, 'interview': 30.0, 'offer': 10.0, 'rejected': 10.0
            },
            'applications_by_month': [
                {'month': '2026-01', 'applications': 2},
                {'month': '2026-02', 'applications': 3},
            ],
            'average_days_to_interview': 15.5,
            'average_days_to_offer': 30.0,
            'success_rate_percentage': 10.0,
            'rejection_rate_percentage': 10.0
        }
        
        serializer = DetailedStatsSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_detailed_stats_serializer_invalid_average_days(self):
        """Test serializer rejects invalid average days"""
        data = {
            'total_applications': 10,
            'status_breakdown': {
                'applied': 5, 'interview': 3, 'offer': 1, 'rejected': 1
            },
            'status_percentages': {
                'applied': 50.0, 'interview': 30.0, 'offer': 10.0, 'rejected': 10.0
            },
            'applications_by_month': [],
            'average_days_to_interview': 'not_a_number',
            'average_days_to_offer': 30.0,
            'success_rate_percentage': 10.0,
            'rejection_rate_percentage': 10.0
        }
        
        serializer = DetailedStatsSerializer(data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_detailed_stats_serializer_contains_all_fields(self):
        """Test serializer includes all expected fields"""
        data = {
            'total_applications': 5,
            'status_breakdown': {'applied': 5, 'interview': 0, 'offer': 0, 'rejected': 0},
            'status_percentages': {'applied': 100.0, 'interview': 0.0, 'offer': 0.0, 'rejected': 0.0},
            'applications_by_month': [{'month': '2026-01', 'applications': 5}],
            'average_days_to_interview': 0.0,
            'average_days_to_offer': 0.0,
            'success_rate_percentage': 0.0,
            'rejection_rate_percentage': 0.0
        }
        
        serializer = DetailedStatsSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        expected_fields = {
            'total_applications', 'status_breakdown', 'status_percentages',
            'applications_by_month', 'average_days_to_interview',
            'average_days_to_offer', 'success_rate_percentage', 'rejection_rate_percentage'
        }
        self.assertEqual(set(serializer.validated_data.keys()), expected_fields)
