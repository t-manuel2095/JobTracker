# Job Tracker API Project Guide

## Goal
Build a secure REST API to track job applications, statuses, and progress over time.

## Tech Stack
- **Backend Framework:** Django
- **API Framework:** Django REST Framework (DRF)
- **Authentication:** Djoser + JWT Authentication
- **Database:** Microsoft SQL Server (MSSQL) with mssql-django backend
- **Environment Management:** Pipenv
- **Frontend:** (To be determined - React, Vue, or vanilla JS)

## Data Models

### JobApplication Model
The core model for storing job application data.

```python
class JobApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    applied_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### Status Choices
```python
STATUS_CHOICES = [
    ("applied", "Applied"),
    ("interview", "Interview"),
    ("offer", "Offer"),
    ("rejected", "Rejected"),
]
```

### StatusHistory Model
Tracks all status changes for audit and analytics purposes.

```python
class StatusHistory(models.Model):
    job = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name="history")
    old_status = models.CharField(max_length=50)
    new_status = models.CharField(max_length=50)
    changed_at = models.DateTimeField(auto_now_add=True)
```

## API Endpoints

### Authentication Endpoints
- `POST /auth/users/` - Register new user
- `POST /auth/jwt/create/` - Obtain JWT tokens
- `POST /auth/jwt/refresh/` - Refresh JWT token

### Job Application Endpoints

#### CRUD Operations
- `GET /api/jobs/` - List all job applications
- `POST /api/jobs/` - Create new job application
- `GET /api/jobs/{id}/` - Retrieve specific job application
- `PUT /api/jobs/{id}/` - Update job application
- `DELETE /api/jobs/{id}/` - Delete job application

#### Filtering & Search
- `GET /api/jobs/?status=interview` - Filter by status
- `GET /api/jobs/?company=google` - Filter by company
- `GET /api/jobs/?ordering=-applied_date` - Order by applied date (newest first)

#### Status History & Analytics
- `GET /api/jobs/{id}/history/` - Get status change history for a job
- `GET /api/jobs/stats/` - Get analytics data (e.g., total applications, status breakdown)

## Serializers

Using Django REST Framework serializers to handle data validation and conversion.

### JobApplication Serializer
Handles validation and serialization of job application data.

### StatusHistory Serializer
Serializes status change history records.

## Permissions

### IsOwner Permission Class
Ensures users can only access and modify their own job applications.

```python
class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
```

## Status Change Logic

When a job application status is updated, automatically create a status history record.

```python
def update(self, instance, validated_data):
    old_status = instance.status
    new_status = validated_data.get("status", old_status)
    if old_status != new_status:
        StatusHistory.objects.create(
            job=instance,
            old_status=old_status,
            new_status=new_status
        )
    return super().update(instance, validated_data)
```

## Development Timeline (7-Day Plan)

| Day | Focus | Tasks |
|-----|-------|-------|
| 1 | Setup & Auth | Initialize Django project, setup Pipenv, configure Djoser authentication |
| 2 | Models & Migrations | Create database models, run migrations, setup admin interface |
| 3 | CRUD & Permissions | Implement serializers, create viewsets, apply IsOwner permissions |
| 4 | Status History | Implement status change tracking, create history endpoints |
| 5 | Analytics | Build stats aggregation, create analytics endpoints |
| 6 | Testing | Write unit and integration tests |
| 7 | Polish & Docs | Frontend integration, comprehensive README, final documentation |

## Frontend Features

- User registration and login
- Dashboard displaying all job applications
- Add/edit/delete job applications
- Filter and search job applications by status, company
- Status change interface with history tracking
- Analytics dashboard showing application statistics
- Responsive design for mobile and desktop

## Environment Setup (Pipenv)

```bash
# Install dependencies using Pipenv
pipenv install django==4.2 djangorestframework djoser djangorestframework-simplejwt django-cors-headers python-decouple mssql-django pyodbc

# Install dev dependencies
pipenv install --dev pytest pytest-django factory-boy black flake8

# Activate virtual environment
pipenv shell
```
## Notes

- All endpoints require JWT authentication (except /auth/users/ for registration)
- Users can only access their own job applications
- Status changes are automatically logged to StatusHistory
- Timestamps are auto-managed (created_at, changed_at)

## IMPLEMENTATION STEPS

### Day 1: Project Setup & Authentication (COMPLETE)

**Objectives:** Initialize the Django project, configure Pipenv with MSSQL, and set up authentication with Djoser.

**Tasks:**

1. **Create Project Directory & Pipenv**
   x Create `/backend` directory for Django project
   x Initialize Pipenv: `pipenv --python 3.11`
   x Create `Pipfile` with dependencies

2. **Install Core Dependencies (with MSSQL)**
   ```
   pipenv install django==4.2 djangorestframework djoser djangorestframework-simplejwt django-cors-headers python-decouple mssql-django pyodbc
   pipenv install --dev pytest pytest-django factory-boy black flake8
   ```

3. **Set Up MSSQL Database**
   x **Option A (Docker):** Create and run `docker-compose.yml` with MSSQL service (see Database Configuration section)
   x **Option B (Local):** Install SQL Server Express, create database `JobTrackerDB`
   x Verify connection with test credentials

4. **Initialize Django Project**
   x `django-admin startproject config .`
   x `python manage.py startapp jobs`
   x `python manage.py startapp users`

5. **Configure Django Settings for MSSQL**
   x Create `.env` file with database credentials
   x Update `settings.py` with MSSQL database configuration (see Database Configuration section)
   x Add to `INSTALLED_APPS`: `rest_framework`, `djoser`, `corsheaders`, `jobs`, `users`
   x Configure `REST_FRAMEWORK` settings for JWT authentication
   x Add CORS headers configuration
   x Set up JWT token settings

6. **Create Djoser Endpoints**
   x Add Djoser URLs to `urls.py`
   x Test auth endpoints: `/auth/users/`, `/auth/jwt/create/`, `/auth/jwt/refresh/`

7. **Test Authentication & Database**
   x Create test user via API
   x Obtain JWT token
   x Test token refresh
   x Verify data is persisted in MSSQL

**Deliverables:** Working Django project with functional JWT authentication and MSSQL database connection

---

### Day 2: Database Models & Migrations (COMPLETE)

**Objectives:** Create data models and set up database schema.

**Tasks:**

1. **Create JobApplication Model** (`jobs/models.py`)
   x Define fields: user, company, role, status, applied_date, notes, created_at
   x Add STATUS_CHOICES
   x Add `__str__` method
   x Add Meta options (ordering, verbose_name)

2. **Create StatusHistory Model** (`jobs/models.py`)
   x Define fields: job (FK), old_status, new_status, changed_at
   x Add `__str__` method
   x Add Meta options

3. **Create Migrations**
   x `python manage.py makemigrations`
   x `python manage.py migrate`

4. **Set Up Django Admin**
   x Create `jobs/admin.py`
   x Register JobApplication and StatusHistory models

5. **Create Fixtures (Optional)**
   x Create sample data for testing
   x Load fixtures for development

6. **Database Verification**
   x Access Django admin interface
   x Verify models appear and can be created

**Deliverables:** Database schema created, models accessible in admin panel

---

### Day 3: Serializers, ViewSets & CRUD Operations(COMPLETE)

**Objectives:** Implement serializers and views for job application CRUD operations with permissions.

**Tasks:**

1. **Create Custom Permissions** (`jobs/permissions.py`)
   x Implement `IsOwner` permission class
   x Verify ownership before allowing modifications

2. **Create Serializers** (`jobs/serializers.py`)
   - `JobApplicationSerializer`:
     x Fields: id, user, company, role, status, applied_date, notes, created_at
     x Read-only fields: id, created_at, user
     x Custom validation methods
   - `StatusHistorySerializer`:
     x Fields: id, job, old_status, new_status, changed_at
     x Read-only fields (all)

3. **Create ViewSets** (`jobs/views.py`)
   - `JobApplicationViewSet`:
     x Queryset: filtered by current user
     x Serializer: JobApplicationSerializer
     x Permissions: IsAuthenticated, IsOwner
     x Actions: list, create, retrieve, update, destroy
     x Override `perform_create()` to set user
   
4. **Configure URLs** (`jobs/urls.py`)
   x Use `DefaultRouter` to register JobApplicationViewSet
   x Generate endpoints: GET, POST, PUT, DELETE

5. **Test CRUD Operations**
   x Create job application
   x List job applications
   x Retrieve specific job
   x Update job status
   x Delete job application
   x Verify permissions (user can't access other users' jobs)

6. **Add Filtering**
   x Install `django-filter`
   x Add `DjangoFilterBackend` to ViewSet
   x Add filterset_fields: status, company, ordering

**Deliverables:** All CRUD endpoints working with proper permissions and filtering

---

### Day 4: Status History Tracking & Endpoints(COMPLETE)

**Objectives:** Implement automatic status change logging and create status history endpoints.

**Tasks:**

1. **Create Status History Logic** (`jobs/serializers.py`)
   x Override `update()` method in JobApplicationSerializer
   x Detect status changes
   x Auto-create StatusHistory entries
   x Test status change tracking

2. **Create Status History ViewSet** (`jobs/views.py`)
   - `StatusHistoryViewSet`:
     X Queryset: filter by parent job's user
     X Serializer: StatusHistorySerializer
     X Read-only actions
     X Nested routing under JobApplication

3. **Configure Nested Routes** (`jobs/urls.py`)
   x Set up nested router for `/api/jobs/{id}/history/`
   x Make it read-only

4. **Create Custom Actions** (`jobs/views.py`)
   O Add `@action` decorator for `/api/jobs/{id}/status-timeline/`
   x Return formatted status history for frontend consumption

5. **Test Status Tracking**
   x Update a job's status multiple times
   x Verify StatusHistory entries created
   x Test history endpoint returns all changes
   x Verify old_status and new_status are correct

**Deliverables:** Status history endpoints working, automatic logging functional

---

### Day 5: Analytics Endpoints(COMPLETE)

**Objectives:** Build analytics and statistics endpoints for dashboard insights.

**Tasks:**

1. **Create Analytics ViewSet** (`jobs/views.py`)
   x `JobStatsViewSet`:
     x Endpoint: `/api/jobs/stats/`
     x Calculate: total applications, breakdown by status, success rate

2. **Implement Statistics Logic** (`jobs/serializers.py`)
   x Total applications count
   x Count by status (applied, interview, offer, rejected)
   x Status percentages

3. **Create Analytics Serializer** (`jobs/serializers.py`)
   x `JobStatsSerializer` - validate and return stats data

4. **Add Aggregation Queries**
   x Use Django ORM aggregation: `Count()`, `Avg()`, `Max()`, `Min()`
   x Optimize with `annotate()`
   x Filter by current user

5. **Create Detailed Stats Endpoint** (`jobs/views.py`)
   x Custom action for more granular stats
   x Timeline-based statistics
   x Trend analysis (applications over time)

6. **Test Analytics**
   x Create multiple job applications with different statuses
   x Call stats endpoint
   x Verify calculations are correct
   x Test with filtered date ranges

**Deliverables:** Analytics endpoints functional, stats calculated correctly

---

### Day 6: Testing(COMPLETE)

**Objectives:** Write comprehensive tests for all functionality.

**Tasks:**

1. **Set Up Testing Infrastructure** (`jobs/tests/`)
   - Create test files structure:
     - `test_models.py`
     - `test_serializers.py`
     - `test_views.py`
     - `test_permissions.py`
   - Configure `pytest.ini`

2. **Model Tests** (`test_models.py`)
   - Test model creation
   - Test model methods
   - Test model constraints
   - Test relationships

3. **Serializer Tests** (`test_serializers.py`)
   - Test valid data serialization
   - Test invalid data rejection
   - Test status change logic
   - Test read-only fields

4. **View/ViewSet Tests** (`test_views.py`)
   - Test CRUD endpoints with authentication
   - Test filtering and ordering
   - Test list and detail views
   - Test status history endpoints
   - Test analytics endpoints

5. **Permission Tests** (`test_permissions.py`)
   - Test IsOwner permission
   - Test user can't access other users' data
   - Test unauthenticated access denied

6. **Run Test Suite**
   - `pytest` or `python manage.py test`
   - Aim for 80%+ code coverage
   - Fix any failing tests

**Deliverables:** Comprehensive test suite with >80% coverage

---

### Day 7: Frontend Integration & Polish(COMPLETE)

**Objectives:** Create frontend interface and finalize documentation.

**Tasks:**

1. **Choose Frontend Approach**
   - Option A: Vanilla HTML/CSS/JavaScript
   - Option B: Create React SPA in `/frontend`
   - Option C: Vue.js

2. **Create Frontend Project Structure** (if not vanilla)
   - Initialize project (`npm create vite@latest`)
   - Install dependencies
   - Set up environment variables for API URL

3. **Implement Authentication UI**
   - Registration form
   - Login form
   - JWT token storage (localStorage)
   - Logout functionality
   - Protected routes/pages

4. **Build Main Dashboard**
   - Display all job applications in table/card format
   - Show columns: company, role, status, applied_date, actions
   - Responsive design

5. **Create CRUD Pages**
   - Add Job Application page (form)
   - Edit Job Application page
   - Delete confirmation modal
   - Form validation

6. **Implement Filtering & Search**
   - Filter by status (dropdown)
   - Search by company
   - Sort by date
   - URL parameters for shareable filters

7. **Add Status History View**
   - Modal/page showing history for a job
   - Timeline visualization
   - Show old_status → new_status transitions

8. **Build Analytics Dashboard**
   - Display stats from `/api/jobs/stats/`
   - Show charts/visualizations:
     - Pie chart of status breakdown
     - Total applications count
     - Recent applications list

9. **Create Comprehensive Documentation**
   - Update README.md with:
     - Project setup instructions
     - API endpoint documentation
     - Frontend setup and running instructions
     - Environment variables needed
     - Database setup steps
   - Add API examples (cURL, Postman, or API client)

10. **Deploy Locally**
    - Test full workflow end-to-end
    - Frontend → API communication
    - Authentication flow
    - All CRUD operations
    - Analytics display

11. **Polish & Optimization**
    - Add error handling and user feedback
    - Improve UI/UX
    - Optimize API queries (select_related, prefetch_related)
    - Add loading states
    - Cache frequently accessed data

**Deliverables:** Fully functional job tracker website with polished UI and complete documentation

---

## Summary Table: File Structure After Implementation

```
JobTracker/
├── backend/
│   ├── manage.py
│   ├── Pipfile
│   ├── Pipfile.lock
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── jobs/
│   │   ├── migrations/
│   │   ├── tests/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── permissions.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── apps.py
│   ├── users/
│   │   └── (Djoser handles this)
│   └── README.md
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   └── (or React/Vue project structure)
└── JOB_TRACKER_API_GUIDE.md
```

**Note:** This timeline is flexible. Adjust based on your pace and requirements.