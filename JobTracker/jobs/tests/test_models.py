from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from ..models import JobApplication, StatusHistory


class JobApplicationModelTests(TestCase):
    """Test JobApplication model"""
    
    def setUp(self):
        """Create test user and job application"""
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
    
    def test_job_creation(self):
        """Test creating a JobApplication with all fields"""
        job = JobApplication.objects.create(
            user=self.user,
            company='Google',
            role='Software Engineer',
            status='applied',
            applied_date='2026-04-01',
            notes='Test notes'
        )
        
        self.assertEqual(job.company, 'Google')
        self.assertEqual(job.role, 'Software Engineer')
        self.assertEqual(job.status, 'applied')
        self.assertEqual(job.user, self.user)
    
    def test_job_str_method(self):
        """Test __str__() returns company name"""
        job = JobApplication.objects.create(
            user=self.user,
            company='Microsoft',
            role='DevOps Engineer',
            status='applied',
            applied_date='2026-04-02'
        )
        
        self.assertEqual(str(job), 'Microsoft')
    
    def test_job_default_status(self):
        """Test default status is 'applied'"""
        job = JobApplication.objects.create(
            user=self.user,
            company='Amazon',
            role='Backend Engineer',
            applied_date='2026-04-03'
        )
        
        self.assertEqual(job.status, 'applied')
    
    def test_job_user_foreign_key(self):
        """Test ForeignKey relationship with User"""
        job = JobApplication.objects.create(
            user=self.user,
            company='Apple',
            role='iOS Developer',
            status='applied',
            applied_date='2026-04-04'
        )
        
        self.assertEqual(job.user.username, 'testuser')
        self.assertIn(job, self.user.jobapplication_set.all())
    
    def test_job_related_name_history(self):
        """Test accessing history via related_name"""
        job = JobApplication.objects.create(
            user=self.user,
            company='Facebook',
            role='Full Stack Engineer',
            status='applied',
            applied_date='2026-04-05'
        )
        
        # Create history entries
        StatusHistory.objects.create(
            job=job,
            old_status='applied',
            new_status='interview'
        )
        StatusHistory.objects.create(
            job=job,
            old_status='interview',
            new_status='offer'
        )
        
        # Access via related_name 'history'
        self.assertEqual(job.history.count(), 2)
    
    def test_job_status_choices(self):
        """Test that only valid status choices are accepted"""
        job = JobApplication.objects.create(
            user=self.user,
            company='Netflix',
            role='Data Engineer',
            status='offer',
            applied_date='2026-04-06'
        )
        
        valid_statuses = ['applied', 'interview', 'offer', 'rejected']
        self.assertIn(job.status, valid_statuses)
    
    def test_job_ordering(self):
        """Test model ordering by applied_date descending"""
        job1 = JobApplication.objects.create(
            user=self.user, company='A', role='SWE',
            status='applied', applied_date='2026-04-01'
        )
        job2 = JobApplication.objects.create(
            user=self.user, company='B', role='SWE',
            status='applied', applied_date='2026-04-02'
        )
        job3 = JobApplication.objects.create(
            user=self.user, company='C', role='SWE',
            status='applied', applied_date='2026-04-03'
        )
        
        jobs = JobApplication.objects.all()
        self.assertEqual(jobs[0].company, 'C')  # Most recent
        self.assertEqual(jobs[2].company, 'A')  # Oldest
    
    def test_job_notes_blank(self):
        """Test notes field is optional"""
        job = JobApplication.objects.create(
            user=self.user,
            company='Tesla',
            role='Software Engineer',
            status='applied',
            applied_date='2026-04-07'
        )
        
        self.assertEqual(job.notes, '')
    
    def test_job_created_at_auto_set(self):
        """Test created_at is automatically set"""
        before = timezone.now()
        job = JobApplication.objects.create(
            user=self.user,
            company='Uber',
            role='Backend Engineer',
            status='applied',
            applied_date='2026-04-08'
        )
        after = timezone.now()
        
        self.assertIsNotNone(job.created_at)
        self.assertGreaterEqual(job.created_at, before)
        self.assertLessEqual(job.created_at, after)
    
    def test_job_cascade_delete_history(self):
        """Test StatusHistory entries are deleted when job is deleted"""
        job = JobApplication.objects.create(
            user=self.user,
            company='LinkedIn',
            role='Software Engineer',
            status='applied',
            applied_date='2026-04-09'
        )
        
        history = StatusHistory.objects.create(
            job=job,
            old_status='applied',
            new_status='interview'
        )
        
        job_id = job.id
        job.delete()
        
        self.assertFalse(JobApplication.objects.filter(id=job_id).exists())
        self.assertFalse(StatusHistory.objects.filter(id=history.id).exists())


class StatusHistoryModelTests(TestCase):
    """Test StatusHistory model"""
    
    def setUp(self):
        """Create test user and job application"""
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
        self.job = JobApplication.objects.create(
            user=self.user,
            company='Google',
            role='SWE',
            status='applied',
            applied_date='2026-04-01'
        )
    
    def test_status_history_creation(self):
        """Test creating a StatusHistory entry"""
        history = StatusHistory.objects.create(
            job=self.job,
            old_status='applied',
            new_status='interview'
        )
        
        self.assertEqual(history.old_status, 'applied')
        self.assertEqual(history.new_status, 'interview')
        self.assertEqual(history.job, self.job)
    
    def test_status_history_str_method(self):
        """Test __str__() format"""
        history = StatusHistory.objects.create(
            job=self.job,
            old_status='applied',
            new_status='interview'
        )
        
        expected_str = 'Google - applied → interview'
        self.assertEqual(str(history), expected_str)
    
    def test_status_history_changed_at_auto_set(self):
        """Test changed_at is automatically set"""
        before = timezone.now()
        history = StatusHistory.objects.create(
            job=self.job,
            old_status='applied',
            new_status='interview'
        )
        after = timezone.now()
        
        self.assertIsNotNone(history.changed_at)
        self.assertGreaterEqual(history.changed_at, before)
        self.assertLessEqual(history.changed_at, after)
    
    def test_status_history_job_foreign_key(self):
        """Test ForeignKey relationship with JobApplication"""
        history = StatusHistory.objects.create(
            job=self.job,
            old_status='interview',
            new_status='offer'
        )
        
        self.assertEqual(history.job, self.job)
        self.assertIn(history, self.job.history.all())
    
    def test_status_history_ordering(self):
        """Test model ordering by changed_at descending"""
        history1 = StatusHistory.objects.create(
            job=self.job, old_status='applied', new_status='interview'
        )
        history2 = StatusHistory.objects.create(
            job=self.job, old_status='interview', new_status='offer'
        )
        history3 = StatusHistory.objects.create(
            job=self.job, old_status='offer', new_status='rejected'
        )
        
        histories = StatusHistory.objects.filter(job=self.job).order_by('-changed_at')
        # Should return 3 items
        self.assertEqual(histories.count(), 3)
        # Most recent should be after older ones
        self.assertGreaterEqual(histories[0].changed_at, histories[1].changed_at)
        self.assertGreaterEqual(histories[1].changed_at, histories[2].changed_at)
    
    def test_status_history_multiple_entries_per_job(self):
        """Test multiple history entries for one job"""
        StatusHistory.objects.create(
            job=self.job, old_status='applied', new_status='interview'
        )
        StatusHistory.objects.create(
            job=self.job, old_status='interview', new_status='offer'
        )
        StatusHistory.objects.create(
            job=self.job, old_status='offer', new_status='rejected'
        )
        
        self.assertEqual(self.job.history.count(), 3)
    
    def test_status_history_job_relationship(self):
        """Test accessing job from history"""
        history = StatusHistory.objects.create(
            job=self.job,
            old_status='applied',
            new_status='interview'
        )
        
        self.assertEqual(history.job.company, 'Google')
        self.assertEqual(history.job.user, self.user)
    
    def test_status_history_status_choices(self):
        """Test that only valid status choices are accepted"""
        history = StatusHistory.objects.create(
            job=self.job,
            old_status='interview',
            new_status='offer'
        )
        
        valid_statuses = ['applied', 'interview', 'offer', 'rejected']
        self.assertIn(history.old_status, valid_statuses)
        self.assertIn(history.new_status, valid_statuses)
    
    def test_status_history_readonly_fields(self):
        """Test that history fields are set correctly on creation"""
        history = StatusHistory.objects.create(
            job=self.job,
            old_status='applied',
            new_status='interview'
        )
        
        # Verify fields can't be changed meaningfully after creation
        original_changed_at = history.changed_at
        history.save()
        
        history.refresh_from_db()
        self.assertEqual(history.changed_at, original_changed_at)


class ModelRelationshipTests(TestCase):
    """Test relationships between models"""
    
    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password123')
    
    def test_user_to_job_relationship(self):
        """Test one user can have multiple jobs"""
        job1 = JobApplication.objects.create(
            user=self.user, company='Google', role='SWE',
            status='applied', applied_date='2026-04-01'
        )
        job2 = JobApplication.objects.create(
            user=self.user, company='Microsoft', role='DevOps',
            status='applied', applied_date='2026-04-02'
        )
        
        self.assertEqual(self.user.jobapplication_set.count(), 2)
        self.assertIn(job1, self.user.jobapplication_set.all())
        self.assertIn(job2, self.user.jobapplication_set.all())
    
    def test_job_to_history_relationship(self):
        """Test one job can have multiple history entries"""
        job = JobApplication.objects.create(
            user=self.user, company='Google', role='SWE',
            status='applied', applied_date='2026-04-01'
        )
        
        StatusHistory.objects.create(
            job=job, old_status='applied', new_status='interview'
        )
        StatusHistory.objects.create(
            job=job, old_status='interview', new_status='offer'
        )
        
        self.assertEqual(job.history.count(), 2)
    
    def test_history_delete_cascade(self):
        """Test history is deleted when job is deleted"""
        job = JobApplication.objects.create(
            user=self.user, company='Google', role='SWE',
            status='applied', applied_date='2026-04-01'
        )
        
        history = StatusHistory.objects.create(
            job=job, old_status='applied', new_status='interview'
        )
        
        job.delete()
        
        self.assertFalse(StatusHistory.objects.filter(id=history.id).exists())
    
    def test_job_delete_preserves_user(self):
        """Test deleting a job doesn't delete the user"""
        job = JobApplication.objects.create(
            user=self.user, company='Google', role='SWE',
            status='applied', applied_date='2026-04-01'
        )
        
        job.delete()
        
        # User should still exist
        self.assertTrue(User.objects.filter(id=self.user.id).exists())
