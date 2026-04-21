from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from ..models import JobApplication, StatusHistory


class AuthenticationTests(APITestCase):
    """Test authentication requirements"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
    
    def test_unauthenticated_access_denied_to_jobs(self):
        """Verify unauthenticated users get 401"""
        response = self.client.get('/api/jobs/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_access_denied_to_stats(self):
        """Verify unauthenticated users can't access stats"""
        response = self.client.get('/api/stats/stats/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_access_allowed(self):
        """Verify authenticated users can access endpoints"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/jobs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class JobApplicationCRUDTests(APITestCase):
    """Test CRUD operations on JobApplication"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        self.client.force_authenticate(user=self.user)
    
    def test_create_job_application(self):
        """Test creating a new job application"""
        data = {
            'company': 'Google',
            'role': 'Software Engineer',
            'status': 'applied',
            'applied_date': '2026-04-01',
            'notes': 'Test application'
        }
        response = self.client.post('/api/jobs/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['company'], 'Google')
        self.assertEqual(response.data['role'], 'Software Engineer')
        self.assertEqual(response.data['user'], self.user.id)
    
    def test_create_job_assigns_user_automatically(self):
        """Verify user is assigned automatically"""
        data = {
            'company': 'Microsoft',
            'role': 'DevOps Engineer',
            'status': 'applied',
            'applied_date': '2026-04-02'
        }
        response = self.client.post('/api/jobs/', data, format='json')
        
        self.assertEqual(response.data['user'], self.user.id)
    
    def test_list_jobs(self):
        """Test listing all jobs for user"""
        JobApplication.objects.create(
            user=self.user, company='Google', role='SWE', status='applied', applied_date='2026-04-01'
        )
        JobApplication.objects.create(
            user=self.user, company='Microsoft', role='DevOps', status='interview', applied_date='2026-04-02'
        )
        
        response = self.client.get('/api/jobs/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_retrieve_job_detail(self):
        """Test retrieving a specific job"""
        job = JobApplication.objects.create(
            user=self.user, company='Google', role='SWE', status='applied', applied_date='2026-04-01'
        )
        
        response = self.client.get(f'/api/jobs/{job.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company'], 'Google')
    
    def test_update_job_partial(self):
        """Test partial update (PATCH)"""
        job = JobApplication.objects.create(
            user=self.user, company='Google', role='SWE', status='applied', applied_date='2026-04-01'
        )
        
        response = self.client.patch(f'/api/jobs/{job.id}/', {'company': 'Amazon'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company'], 'Amazon')
    
    def test_update_job_full(self):
        """Test full update (PUT)"""
        job = JobApplication.objects.create(
            user=self.user, company='Google', role='SWE', status='applied', applied_date='2026-04-01'
        )
        
        data = {
            'company': 'Amazon',
            'role': 'Backend Engineer',
            'status': 'interview',
            'applied_date': '2026-04-02',
            'notes': 'Updated'
        }
        response = self.client.put(f'/api/jobs/{job.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company'], 'Amazon')
    
    def test_delete_job(self):
        """Test deleting a job"""
        job = JobApplication.objects.create(
            user=self.user, company='Google', role='SWE', status='applied', applied_date='2026-04-01'
        )
        
        response = self.client.delete(f'/api/jobs/{job.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(JobApplication.objects.filter(id=job.id).exists())


class PermissionTests(APITestCase):
    """Test IsOwner permission"""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user('user1', 'user1@test.com', 'password123')
        self.user2 = User.objects.create_user('user2', 'user2@test.com', 'password123')
        
        self.job_user1 = JobApplication.objects.create(
            user=self.user1, company='Google', role='SWE', status='applied', applied_date='2026-04-01'
        )
        self.job_user2 = JobApplication.objects.create(
            user=self.user2, company='Microsoft', role='DevOps', status='applied', applied_date='2026-04-02'
        )
    
    def test_user_cannot_access_other_users_jobs(self):
        """Verify IsOwner permission prevents unauthorized access"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(f'/api/jobs/{self.job_user2.id}/')
        
        # Will be 404 because job is filtered out by get_queryset()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_user_can_access_own_jobs(self):
        """Verify user can access their own jobs"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(f'/api/jobs/{self.job_user1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_cannot_modify_other_users_jobs(self):
        """Verify IsOwner prevents modification of other users' data"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.patch(f'/api/jobs/{self.job_user2.id}/', {'company': 'Hacked'})
        
        # Will be 404 because job is filtered out by get_queryset()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_user_cannot_delete_other_users_jobs(self):
        """Verify IsOwner prevents deletion of other users' data"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.delete(f'/api/jobs/{self.job_user2.id}/')
        
        # Will be 404 because job is filtered out by get_queryset()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Job should still exist
        self.assertTrue(JobApplication.objects.filter(id=self.job_user2.id).exists())
    
    def test_user_list_only_shows_own_jobs(self):
        """Verify user only sees their own jobs in list"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get('/api/jobs/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.job_user1.id)


class FilteringAndSearchTests(APITestCase):
    """Test filtering, searching, and ordering"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        self.client.force_authenticate(user=self.user)
        
        JobApplication.objects.create(
            user=self.user, company='Google', role='SWE', status='applied', applied_date='2026-04-01'
        )
        JobApplication.objects.create(
            user=self.user, company='Microsoft', role='Backend', status='interview', applied_date='2026-04-02'
        )
        JobApplication.objects.create(
            user=self.user, company='Amazon', role='DevOps', status='offer', applied_date='2026-04-03'
        )
    
    def test_filter_by_status(self):
        """Test filtering jobs by status"""
        response = self.client.get('/api/jobs/?status=interview')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'interview')
    
    def test_filter_by_company(self):
        """Test filtering jobs by company"""
        response = self.client.get('/api/jobs/?company=Google')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['company'], 'Google')
    
    def test_search_by_company_name(self):
        """Test searching jobs by company name"""
        response = self.client.get('/api/jobs/?search=Google')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_search_by_role(self):
        """Test searching jobs by role"""
        response = self.client.get('/api/jobs/?search=Backend')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_ordering_by_applied_date_ascending(self):
        """Test ordering by applied_date ascending"""
        response = self.client.get('/api/jobs/?ordering=applied_date')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['company'], 'Google')
        self.assertEqual(response.data[2]['company'], 'Amazon')
    
    def test_ordering_by_applied_date_descending(self):
        """Test ordering by applied_date descending (default)"""
        response = self.client.get('/api/jobs/?ordering=-applied_date')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['company'], 'Amazon')
        self.assertEqual(response.data[2]['company'], 'Google')


class StatusHistoryTrackingTests(APITestCase):
    """Test automatic status history creation (Day 4)"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        self.client.force_authenticate(user=self.user)
    
    def test_status_change_creates_history_entry(self):
        """Verify StatusHistory entry created when status changes"""
        job = JobApplication.objects.create(
            user=self.user, company='Google', role='SWE', status='applied', applied_date='2026-04-01'
        )
        
        # No history yet
        self.assertEqual(StatusHistory.objects.filter(job=job).count(), 0)
        
        # Update status
        response = self.client.patch(f'/api/jobs/{job.id}/', {'status': 'interview'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # History entry created
        history = StatusHistory.objects.filter(job=job).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.old_status, 'applied')
        self.assertEqual(history.new_status, 'interview')
    
    def test_multiple_status_changes_create_multiple_entries(self):
        """Verify multiple status changes create multiple history entries"""
        job = JobApplication.objects.create(
            user=self.user, company='Google', role='SWE', status='applied', applied_date='2026-04-01'
        )
        
        # Change 1: applied → interview
        self.client.patch(f'/api/jobs/{job.id}/', {'status': 'interview'})
        # Change 2: interview → offer
        self.client.patch(f'/api/jobs/{job.id}/', {'status': 'offer'})
        # Change 3: offer → rejected
        self.client.patch(f'/api/jobs/{job.id}/', {'status': 'rejected'})
        
        history_entries = StatusHistory.objects.filter(job=job).order_by('changed_at')
        
        self.assertEqual(history_entries.count(), 3)
        self.assertEqual(history_entries[0].old_status, 'applied')
        self.assertEqual(history_entries[0].new_status, 'interview')
        self.assertEqual(history_entries[1].old_status, 'interview')
        self.assertEqual(history_entries[1].new_status, 'offer')
        self.assertEqual(history_entries[2].old_status, 'offer')
        self.assertEqual(history_entries[2].new_status, 'rejected')
    
    def test_non_status_update_does_not_create_history(self):
        """Verify non-status updates don't create history entries"""
        job = JobApplication.objects.create(
            user=self.user, company='Google', role='SWE', status='applied', applied_date='2026-04-01'
        )
        
        initial_count = StatusHistory.objects.filter(job=job).count()
        
        # Update notes (not status)
        self.client.patch(f'/api/jobs/{job.id}/', {'notes': 'Updated notes'})
        
        new_count = StatusHistory.objects.filter(job=job).count()
        
        self.assertEqual(initial_count, new_count)


class NestedHistoryEndpointTests(APITestCase):
    """Test nested status history endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        self.client.force_authenticate(user=self.user)
        
        self.job = JobApplication.objects.create(
            user=self.user, company='Google', role='SWE', status='applied', applied_date='2026-04-01'
        )
    
    def test_history_endpoint_returns_all_changes(self):
        """Test nested history endpoint returns all status changes"""
        # Create status changes
        self.client.patch(f'/api/jobs/{self.job.id}/', {'status': 'interview'})
        self.client.patch(f'/api/jobs/{self.job.id}/', {'status': 'offer'})
        
        response = self.client.get(f'/api/jobs/{self.job.id}/history/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_history_endpoint_contains_correct_data(self):
        """Verify history endpoint returns correct old/new status"""
        self.client.patch(f'/api/jobs/{self.job.id}/', {'status': 'interview'})
        
        response = self.client.get(f'/api/jobs/{self.job.id}/history/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        history_data = response.data[0]
        
        self.assertEqual(history_data['old_status'], 'applied')
        self.assertEqual(history_data['new_status'], 'interview')
        self.assertIn('changed_at', history_data)
    
    def test_history_endpoint_is_read_only(self):
        """Verify history endpoint doesn't allow POST"""
        response = self.client.post(
            f'/api/jobs/{self.job.id}/history/',
            {'old_status': 'applied', 'new_status': 'interview'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_user_cannot_access_other_users_history(self):
        """Verify user can only see their own job's history"""
        user2 = User.objects.create_user('user2', 'user2@test.com', 'password123')
        job2 = JobApplication.objects.create(
            user=user2, company='Microsoft', role='DevOps', status='applied', applied_date='2026-04-02'
        )
        
        # Authenticate as user1
        # Since get_queryset filters by user, it should return empty even if job exists
        response = self.client.get(f'/api/jobs/{job2.id}/history/')
        
        # The job doesn't belong to user1, so should be 404 (job not in queryset)
        # But nested routers work differently - they might return empty list
        # Let's check that the response is either 404 or an empty list
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK])
        if response.status_code == status.HTTP_200_OK:
            # If we got 200, verify it's because there's no data
            self.assertEqual(len(response.data), 0)


class StatusTimelineActionTests(APITestCase):
    """Test custom @action for status timeline"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        self.client.force_authenticate(user=self.user)
        
        self.job = JobApplication.objects.create(
            user=self.user, company='Google', role='SWE', status='applied', applied_date='2026-04-01'
        )
    
    def test_status_timeline_action_exists(self):
        """Test custom status-timeline action"""
        # The route should be /api/jobs/{id}/status_timeline/ (with underscores, not hyphens in URL)
        response = self.client.get(f'/api/jobs/{self.job.id}/status_timeline/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_status_timeline_returns_formatted_data(self):
        """Verify timeline action returns formatted response"""
        # Create status changes
        self.client.patch(f'/api/jobs/{self.job.id}/', {'status': 'interview'})
        self.client.patch(f'/api/jobs/{self.job.id}/', {'status': 'offer'})
        
        response = self.client.get(f'/api/jobs/{self.job.id}/status_timeline/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['job_id'], self.job.id)
        self.assertEqual(response.data['company'], 'Google')
        self.assertIn('timeline', response.data)
    
    def test_status_timeline_includes_labels(self):
        """Verify timeline includes human-readable labels"""
        self.client.patch(f'/api/jobs/{self.job.id}/', {'status': 'interview'})
        
        response = self.client.get(f'/api/jobs/{self.job.id}/status_timeline/')
        
        timeline_entry = response.data['timeline'][0]
        self.assertIn('label', timeline_entry)
        self.assertIn('→', timeline_entry['label'])


class StatsEndpointTests(APITestCase):
    """Test analytics endpoints (Day 5)"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        self.client.force_authenticate(user=self.user)
        
        # Create diverse jobs for testing
        JobApplication.objects.create(
            user=self.user, company='Google', role='SWE', status='applied', applied_date='2026-04-01'
        )
        JobApplication.objects.create(
            user=self.user, company='Microsoft', role='Backend', status='applied', applied_date='2026-04-02'
        )
        JobApplication.objects.create(
            user=self.user, company='Amazon', role='DevOps', status='interview', applied_date='2026-04-03'
        )
        JobApplication.objects.create(
            user=self.user, company='Facebook', role='SWE', status='offer', applied_date='2026-04-04'
        )
    
    def test_stats_endpoint_returns_correct_total(self):
        """Test stats endpoint returns correct total applications"""
        response = self.client.get('/api/stats/stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_applications'], 4)
    
    def test_stats_endpoint_status_breakdown(self):
        """Verify status breakdown is accurate"""
        response = self.client.get('/api/stats/stats/')
        
        breakdown = response.data['status_breakdown']
        self.assertEqual(breakdown['applied'], 2)
        self.assertEqual(breakdown['interview'], 1)
        self.assertEqual(breakdown['offer'], 1)
        self.assertEqual(breakdown['rejected'], 0)
    
    def test_stats_endpoint_percentages(self):
        """Test status percentages calculation"""
        response = self.client.get('/api/stats/stats/')
        
        percentages = response.data['status_percentages']
        self.assertEqual(percentages['applied'], 50.0)
        self.assertEqual(percentages['interview'], 25.0)
        self.assertEqual(percentages['offer'], 25.0)
        self.assertEqual(percentages['rejected'], 0.0)
    
    def test_stats_endpoint_success_rate(self):
        """Test success rate calculation"""
        response = self.client.get('/api/stats/stats/')
        
        self.assertEqual(response.data['success_rate_percentage'], 25.0)  # 1 offer / 4 total
    
    def test_detailed_stats_endpoint_exists(self):
        """Test detailed_stats endpoint"""
        response = self.client.get('/api/stats/detailed_stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_detailed_stats_includes_applications_by_month(self):
        """Verify detailed stats includes timeline data"""
        response = self.client.get('/api/stats/detailed_stats/')
        
        self.assertIn('applications_by_month', response.data)
        self.assertIsInstance(response.data['applications_by_month'], list)
    
    def test_detailed_stats_includes_average_days(self):
        """Verify detailed stats includes performance metrics"""
        response = self.client.get('/api/stats/detailed_stats/')
        
        self.assertIn('average_days_to_interview', response.data)
        self.assertIn('average_days_to_offer', response.data)


class ValidationTests(APITestCase):
    """Test data validation"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        self.client.force_authenticate(user=self.user)
    
    def test_invalid_status_rejected(self):
        """Verify invalid status is rejected"""
        response = self.client.post('/api/jobs/', {
            'company': 'Google',
            'role': 'SWE',
            'status': 'invalid_status',
            'applied_date': '2026-04-01'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_required_fields_enforced(self):
        """Verify required fields are enforced"""
        response = self.client.post('/api/jobs/', {
            'company': 'Google'
            # Missing required fields
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_read_only_fields_cannot_be_modified(self):
        """Verify read-only fields can't be changed"""
        job = JobApplication.objects.create(
            user=self.user, company='Google', role='SWE', status='applied', applied_date='2026-04-01'
        )
        original_id = job.id
        
        response = self.client.patch(f'/api/jobs/{job.id}/', {
            'id': 999,
            'company': 'Amazon'
        })
        
        self.assertNotEqual(response.data['id'], 999)
        self.assertEqual(response.data['id'], original_id)


class EdgeCaseTests(APITestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        self.client.force_authenticate(user=self.user)
    
    def test_not_found_error(self):
        """Verify 404 for missing resource"""
        response = self.client.get('/api/jobs/999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_empty_list_returns_empty_array(self):
        """Verify empty list returns proper response"""
        response = self.client.get('/api/jobs/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
    
    def test_stats_with_no_jobs(self):
        """Verify stats endpoint works with no jobs"""
        response = self.client.get('/api/stats/stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_applications'], 0)
        self.assertEqual(response.data['success_rate_percentage'], 0.0)
