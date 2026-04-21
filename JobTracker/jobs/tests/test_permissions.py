from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from ..models import JobApplication
from ..permissions import IsOwner


class IsOwnerPermissionTests(APITestCase):
    """Test IsOwner permission class"""
    
    def setUp(self):
        """Create test users and jobs"""
        self.client = APIClient()
        self.user1 = User.objects.create_user('user1', 'user1@test.com', 'password123')
        self.user2 = User.objects.create_user('user2', 'user2@test.com', 'password123')
        
        self.job_user1 = JobApplication.objects.create(
            user=self.user1,
            company='Google',
            role='SWE',
            status='applied',
            applied_date='2026-04-01'
        )
        self.job_user2 = JobApplication.objects.create(
            user=self.user2,
            company='Microsoft',
            role='DevOps',
            status='applied',
            applied_date='2026-04-02'
        )
    
    def test_owner_can_access_own_job(self):
        """Test that owner can access their own job"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(f'/api/jobs/{self.job_user1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company'], 'Google')
    
    def test_owner_cannot_access_other_users_job(self):
        """Test that user cannot access another user's job"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get(f'/api/jobs/{self.job_user2.id}/')
        
        # Returns 404 because job is filtered out by get_queryset()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_owner_can_modify_own_job(self):
        """Test that owner can modify their own job"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.patch(
            f'/api/jobs/{self.job_user1.id}/',
            {'company': 'Amazon'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company'], 'Amazon')
    
    def test_owner_cannot_modify_other_users_job(self):
        """Test that user cannot modify another user's job"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.patch(
            f'/api/jobs/{self.job_user2.id}/',
            {'company': 'Hacked'}
        )
        
        # Returns 404 because job is filtered out by get_queryset()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify job wasn't modified
        self.job_user2.refresh_from_db()
        self.assertEqual(self.job_user2.company, 'Microsoft')
    
    def test_owner_can_delete_own_job(self):
        """Test that owner can delete their own job"""
        self.client.force_authenticate(user=self.user1)
        job_id = self.job_user1.id
        
        response = self.client.delete(f'/api/jobs/{job_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(JobApplication.objects.filter(id=job_id).exists())
    
    def test_owner_cannot_delete_other_users_job(self):
        """Test that user cannot delete another user's job"""
        self.client.force_authenticate(user=self.user1)
        job_id = self.job_user2.id
        
        response = self.client.delete(f'/api/jobs/{job_id}/')
        
        # Returns 404 because job is filtered out by get_queryset()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify job still exists
        self.assertTrue(JobApplication.objects.filter(id=job_id).exists())
    
    def test_permission_class_has_object_permission_method(self):
        """Test IsOwner permission class has proper method"""
        from ..permissions import IsOwner
        
        permission = IsOwner()
        self.assertTrue(hasattr(permission, 'has_object_permission'))
    
    def test_permission_allows_owner(self):
        """Test permission check allows owner"""
        from ..permissions import IsOwner
        from unittest.mock import Mock
        
        permission = IsOwner()
        
        # Create mock request with user1
        request = Mock()
        request.user = self.user1
        
        # Check permission for user1's job
        result = permission.has_object_permission(request, None, self.job_user1)
        
        self.assertTrue(result)
    
    def test_permission_denies_non_owner(self):
        """Test permission check denies non-owner"""
        from ..permissions import IsOwner
        from unittest.mock import Mock
        
        permission = IsOwner()
        
        # Create mock request with user1
        request = Mock()
        request.user = self.user1
        
        # Check permission for user2's job
        result = permission.has_object_permission(request, None, self.job_user2)
        
        self.assertFalse(result)


class UserDataIsolationTests(APITestCase):
    """Test that users cannot access other users' data"""
    
    def setUp(self):
        """Create test users and jobs"""
        self.client = APIClient()
        self.user1 = User.objects.create_user('user1', 'user1@test.com', 'password123')
        self.user2 = User.objects.create_user('user2', 'user2@test.com', 'password123')
        
        # Create multiple jobs for user1
        self.job1_user1 = JobApplication.objects.create(
            user=self.user1, company='Google', role='SWE',
            status='applied', applied_date='2026-04-01'
        )
        self.job2_user1 = JobApplication.objects.create(
            user=self.user1, company='Amazon', role='DevOps',
            status='applied', applied_date='2026-04-02'
        )
        
        # Create jobs for user2
        self.job1_user2 = JobApplication.objects.create(
            user=self.user2, company='Microsoft', role='Backend',
            status='applied', applied_date='2026-04-03'
        )
    
    def test_user_list_only_shows_own_jobs(self):
        """Test that list endpoint only shows user's own jobs"""
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.get('/api/jobs/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only user1's jobs
        
        job_ids = [job['id'] for job in response.data]
        self.assertIn(self.job1_user1.id, job_ids)
        self.assertIn(self.job2_user1.id, job_ids)
        self.assertNotIn(self.job1_user2.id, job_ids)
    
    def test_user2_list_only_shows_own_jobs(self):
        """Test that user2 only sees their own jobs"""
        self.client.force_authenticate(user=self.user2)
        
        response = self.client.get('/api/jobs/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only user2's jobs
        
        job_ids = [job['id'] for job in response.data]
        self.assertIn(self.job1_user2.id, job_ids)
        self.assertNotIn(self.job1_user1.id, job_ids)
        self.assertNotIn(self.job2_user1.id, job_ids)
    
    def test_user_cannot_see_other_users_stats(self):
        """Test that stats are user-specific"""
        # Create stats for user1
        self.client.force_authenticate(user=self.user1)
        response1 = self.client.get('/api/stats/stats/')
        user1_stats = response1.data['total_applications']
        
        # Create stats for user2
        self.client.force_authenticate(user=self.user2)
        response2 = self.client.get('/api/stats/stats/')
        user2_stats = response2.data['total_applications']
        
        # Verify different stats
        self.assertEqual(user1_stats, 2)
        self.assertEqual(user2_stats, 1)
    
    def test_data_modification_isolated_by_user(self):
        """Test that modifications don't affect other users"""
        # User1 modifies their job
        self.client.force_authenticate(user=self.user1)
        self.client.patch(
            f'/api/jobs/{self.job1_user1.id}/',
            {'status': 'interview'}
        )
        
        # Verify user2's jobs are unchanged
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f'/api/jobs/{self.job1_user2.id}/')
        
        self.assertEqual(response.data['status'], 'applied')  # Unchanged


class UnauthenticatedAccessTests(APITestCase):
    """Test that unauthenticated users cannot access protected endpoints"""
    
    def test_unauthenticated_cannot_list_jobs(self):
        """Test unauthenticated access to job list denied"""
        response = self.client.get('/api/jobs/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_cannot_create_job(self):
        """Test unauthenticated user cannot create job"""
        data = {
            'company': 'Google',
            'role': 'SWE',
            'status': 'applied',
            'applied_date': '2026-04-01'
        }
        response = self.client.post('/api/jobs/', data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_cannot_access_stats(self):
        """Test unauthenticated access to stats denied"""
        response = self.client.get('/api/stats/stats/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_cannot_access_detailed_stats(self):
        """Test unauthenticated access to detailed stats denied"""
        response = self.client.get('/api/stats/detailed_stats/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_cannot_access_job_detail(self):
        """Test unauthenticated access to job detail denied"""
        user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        job = JobApplication.objects.create(
            user=user, company='Google', role='SWE',
            status='applied', applied_date='2026-04-01'
        )
        
        response = self.client.get(f'/api/jobs/{job.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_cannot_update_job(self):
        """Test unauthenticated user cannot update job"""
        user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        job = JobApplication.objects.create(
            user=user, company='Google', role='SWE',
            status='applied', applied_date='2026-04-01'
        )
        
        response = self.client.patch(f'/api/jobs/{job.id}/', {'company': 'Amazon'})
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_cannot_delete_job(self):
        """Test unauthenticated user cannot delete job"""
        user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        job = JobApplication.objects.create(
            user=user, company='Google', role='SWE',
            status='applied', applied_date='2026-04-01'
        )
        
        response = self.client.delete(f'/api/jobs/{job.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_cannot_access_history(self):
        """Test unauthenticated access to job history denied"""
        user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        job = JobApplication.objects.create(
            user=user, company='Google', role='SWE',
            status='applied', applied_date='2026-04-01'
        )
        
        response = self.client.get(f'/api/jobs/{job.id}/history/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_cannot_access_timeline(self):
        """Test unauthenticated access to status timeline denied"""
        user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        job = JobApplication.objects.create(
            user=user, company='Google', role='SWE',
            status='applied', applied_date='2026-04-01'
        )
        
        response = self.client.get(f'/api/jobs/{job.id}/status_timeline/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticationRequiredTests(APITestCase):
    """Test authentication requirements across all endpoints"""
    
    def setUp(self):
        """Create test user"""
        self.authenticated_user = User.objects.create_user(
            'testuser', 'test@test.com', 'password123'
        )
    
    def test_authenticated_user_has_access(self):
        """Test that authenticated user can access protected endpoints"""
        self.client.force_authenticate(user=self.authenticated_user)
        
        response = self.client.get('/api/jobs/')
        
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_authentication_persists_across_requests(self):
        """Test authentication persists for multiple requests"""
        self.client.force_authenticate(user=self.authenticated_user)
        
        # First request
        response1 = self.client.get('/api/jobs/')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Second request should still be authenticated
        response2 = self.client.get('/api/stats/stats/')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
    
    def test_logout_removes_access(self):
        """Test that removing authentication removes access"""
        # First authenticate
        self.client.force_authenticate(user=self.authenticated_user)
        response1 = self.client.get('/api/jobs/')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Then force_authenticate with None to logout
        self.client.force_authenticate(user=None)
        response2 = self.client.get('/api/jobs/')
        self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)
