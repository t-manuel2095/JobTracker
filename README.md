# JobTracker - Complete Job Application Manager

A full-stack web application for tracking and managing job applications throughout your job search journey. Built with **Django REST Framework** backend and **Vanilla HTML/CSS/JavaScript** frontend.

**Live Demo:** Coming soon  
**Status:** ✅ Fully Functional (Days 1-7 Complete)

---

## 📋 Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Prerequisites](#prerequisites)
5. [Backend Setup](#backend-setup)
6. [Frontend Setup](#frontend-setup)
7. [Environment Variables](#environment-variables)
8. [Database Setup](#database-setup)
9. [Running the Application](#running-the-application)
10. [API Endpoints](#api-endpoints)
11. [API Examples](#api-examples)
12. [Troubleshooting](#troubleshooting)

---

## ✨ Features

### Core Features
- 🔐 **User Authentication** - Secure JWT-based authentication with registration
- 📋 **Job Application Tracking** - Add, edit, delete job applications
- 🏢 **Application Details** - Company, role, status, applied date, notes
- 🔄 **Status Management** - Track application through pipeline (Applied → Interview → Offer → Rejected)
- 📊 **Status History** - Automatic logging of status changes with timestamps
- 🔍 **Search & Filter** - Find jobs by company name or filter by status
- 📈 **Analytics Dashboard** - Statistics on application success rate and status breakdown
- 🎯 **Responsive Design** - Works on desktop, tablet, and mobile devices

### Advanced Features
- 📅 **Status Timeline** - Visual history of status changes for each application
- 🔐 **User Isolation** - Users only see and manage their own applications
- ⚡ **Real-time Feedback** - Alert notifications for all user actions
- 📱 **Mobile-First Design** - Optimized for all screen sizes

---

## 🛠 Tech Stack

### Backend
- **Framework**: Django 4.2
- **API**: Django REST Framework 3.16
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: SQLite (development) / PostgreSQL (production)
- **CORS**: django-cors-headers
- **Testing**: Python unittest (112 tests)

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Responsive design with CSS Grid & Flexbox
- **JavaScript**: Vanilla ES6+ (no frameworks)
- **API Communication**: Fetch API
- **Storage**: localStorage for JWT tokens

### Development Tools
- **Dependency Management**: Pipenv
- **Version Control**: Git
- **Testing**: Django test runner
- **Code Quality**: Django system checks

---

## 📁 Project Structure

```
JobTracker/
├── backend/
│   ├── JobTracker/                 # Django project folder
│   │   ├── settings.py            # Django configuration
│   │   ├── urls.py                # Main URL routing
│   │   ├── wsgi.py                # WSGI configuration
│   │   └── asgi.py                # ASGI configuration
│   │
│   ├── jobs/                       # Main app
│   │   ├── migrations/            # Database migrations
│   │   ├── tests/                 # Comprehensive test suite (112 tests)
│   │   │   ├── test_api.py       # 44 API integration tests
│   │   │   ├── test_models.py    # 23 model unit tests
│   │   │   ├── test_serializers.py # 20 serializer tests
│   │   │   └── test_permissions.py # 25 permission tests
│   │   ├── models.py              # JobApplication, StatusHistory models
│   │   ├── serializers.py         # REST serializers
│   │   ├── views.py               # ViewSets and API views
│   │   ├── permissions.py         # IsOwner permission class
│   │   ├── urls.py                # App URL routing
│   │   └── admin.py               # Admin configuration
│   │
│   ├── users/                      # User app
│   │   └── (standard Django user app)
│   │
│   ├── manage.py                   # Django management script
│   ├── Pipfile                     # Dependency management
│   ├── Pipfile.lock                # Locked dependencies
│   └── requirements.txt            # Alternative pip requirements
│
├── frontend/
│   ├── index.html                  # Main entry point
│   ├── css/
│   │   └── style.css              # Complete styling (responsive)
│   ├── js/
│   │   ├── api.js                 # API client wrapper
│   │   ├── auth.js                # Authentication management
│   │   ├── dashboard.js           # Main application logic
│   │   ├── analytics.js           # Analytics display
│   │   └── main.js                # App initialization
│   └── README.md                   # Frontend documentation
│
└── README.md                        # This file
```

---

## 📋 Prerequisites

- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **Pipenv** - `pip install pipenv`
- **Git** - [Download](https://git-scm.com/)
- **Web Browser** - Chrome, Firefox, Safari, or Edge
- **Text Editor/IDE** - VS Code, PyCharm, etc.

---

## 🚀 Backend Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/JobTracker.git
cd JobTracker
```

### Step 2: Install Dependencies

```bash
# Navigate to backend
cd JobTracker

# Install dependencies using pipenv
pipenv install

# Activate the virtual environment
pipenv shell
```

### Step 3: Create Environment File

Create a `.env` file in the `JobTracker` directory:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:8001,http://127.0.0.1:8001
```

### Step 4: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser (Admin)

```bash
python manage.py createsuperuser
# Follow prompts for username, email, password
```

### Step 6: Collect Static Files (Optional)

```bash
python manage.py collectstatic --noinput
```

---

## 🎨 Frontend Setup

### Step 1: Navigate to Frontend

```bash
# From project root
cd frontend
```

### Step 2: No Installation Needed!

Vanilla HTML/CSS/JavaScript requires no build tools or dependencies. Just serve the files:

```bash
# Python 3
python -m http.server 8001

# Or Node.js
npx http-server -p 8001

# Or Python 2
python -m SimpleHTTPServer 8001
```

### Step 3: Open in Browser

Visit: **`http://localhost:8001`**

---

## 🔧 Environment Variables

### Backend (.env file)

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | True | Debug mode (set to False in production) |
| `SECRET_KEY` | - | Django secret key (generate a secure one) |
| `ALLOWED_HOSTS` | localhost | Comma-separated allowed hosts |
| `DATABASE_URL` | sqlite:///db.sqlite3 | Database connection string |
| `CORS_ALLOWED_ORIGINS` | http://localhost:8001 | Allowed frontend origins |

### Frontend (api.js)

Update the API base URL in `frontend/js/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

If your backend is on a different host/port, change accordingly:

```javascript
const API_BASE_URL = 'http://your-backend-host:8000/api';
```

---

## 🗄️ Database Setup

### Initial Setup

```bash
# Create initial migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

### Access Admin Panel

1. Run Django server: `python manage.py runserver`
2. Visit: `http://localhost:8000/admin/`
3. Login with superuser credentials
4. Manage jobs, users, and status history

### Reset Database (Development Only)

```bash
# Delete existing database
rm db.sqlite3

# Recreate
python manage.py migrate
python manage.py createsuperuser
```

---

## ▶️ Running the Application

### Terminal 1: Start Backend

```bash
cd JobTracker
pipenv shell
python manage.py runserver
```

**Backend running at:** `http://localhost:8000`  
**Admin panel at:** `http://localhost:8000/admin/`

### Terminal 2: Start Frontend

```bash
cd frontend
python -m http.server 8001
```

**Frontend running at:** `http://localhost:8001`

### Testing

```bash
# Run all 112 tests
python manage.py test jobs --verbosity=2

# Run specific test class
python manage.py test jobs.tests.test_api.JobApplicationCRUDTests

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test jobs
coverage report
```

---

## 📡 API Endpoints

### Authentication Endpoints

**Register New User**
```
POST /auth/users/
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123!"
}

Response: 201 Created
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com"
}
```

**Login (Get JWT Token)**
```
POST /auth/jwt/create/
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePassword123!"
}

Response: 200 OK
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Job Application Endpoints

**List All Jobs (with filters)**
```
GET /jobs/?status=applied&search=Google&ordering=-applied_date
Authorization: Bearer {access_token}

Response: 200 OK
[
  {
    "id": 1,
    "user": 1,
    "company": "Google",
    "role": "Software Engineer",
    "status": "interview",
    "applied_date": "2026-04-01",
    "notes": "Great company",
    "created_at": "2026-04-17T10:30:00Z"
  },
  ...
]
```

**Create Job Application**
```
POST /jobs/
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "company": "Microsoft",
  "role": "Senior Developer",
  "status": "applied",
  "applied_date": "2026-04-17",
  "notes": "Applied via LinkedIn"
}

Response: 201 Created
```

**Get Single Job**
```
GET /jobs/{id}/
Authorization: Bearer {access_token}

Response: 200 OK
{
  "id": 1,
  "company": "Google",
  ...
}
```

**Update Job**
```
PATCH /jobs/{id}/
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "status": "interview",
  "notes": "Phone screen scheduled for 2pm"
}

Response: 200 OK
```

**Delete Job**
```
DELETE /jobs/{id}/
Authorization: Bearer {access_token}

Response: 204 No Content
```

### Status History Endpoints

**List Status Changes for a Job**
```
GET /jobs/{id}/history/
Authorization: Bearer {access_token}

Response: 200 OK
[
  {
    "id": 1,
    "job": 1,
    "old_status": "applied",
    "new_status": "interview",
    "changed_at": "2026-04-17T14:30:00Z"
  },
  ...
]
```

**Get Formatted Status Timeline**
```
GET /jobs/{id}/status_timeline/
Authorization: Bearer {access_token}

Response: 200 OK
{
  "job_id": 1,
  "company": "Google",
  "timeline": [
    {
      "date": "2026-04-17T14:30:00Z",
      "from_status": "applied",
      "to_status": "interview",
      "label": "Applied → Interview"
    },
    ...
  ]
}
```

### Analytics Endpoints

**Get Statistics Summary**
```
GET /stats/stats/
Authorization: Bearer {access_token}

Response: 200 OK
{
  "total_applications": 10,
  "status_breakdown": {
    "applied": 4,
    "interview": 3,
    "offer": 2,
    "rejected": 1
  },
  "status_percentages": {
    "applied": 40.0,
    "interview": 30.0,
    "offer": 20.0,
    "rejected": 10.0
  },
  "offers": 2,
  "rejections": 1,
  "interviews": 3,
  "success_rate_percentage": 20.0,
  "rejection_rate_percentage": 10.0
}
```

**Get Detailed Statistics**
```
GET /stats/detailed_stats/
Authorization: Bearer {access_token}

Response: 200 OK
{
  "total_applications": 10,
  "status_breakdown": { ... },
  "status_percentages": { ... },
  "applications_by_month": [
    {
      "month": "2026-03",
      "applications": 3
    },
    ...
  ],
  "average_days_to_interview": 15.5,
  "average_days_to_offer": 28.3,
  "success_rate_percentage": 20.0,
  "rejection_rate_percentage": 10.0
}
```

---

## 🧪 API Examples

### Using cURL

**Login and Get Token**
```bash
curl -X POST http://localhost:8000/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","password":"password123"}'
```

**Create Job Application**
```bash
TOKEN="your_access_token_here"

curl -X POST http://localhost:8000/api/jobs/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "company": "Google",
    "role": "Software Engineer",
    "status": "applied",
    "applied_date": "2026-04-17",
    "notes": "Applied via company website"
  }'
```

**List All Jobs**
```bash
curl -X GET http://localhost:8000/api/jobs/ \
  -H "Authorization: Bearer $TOKEN"
```

**Get Analytics**
```bash
curl -X GET http://localhost:8000/api/stats/stats/ \
  -H "Authorization: Bearer $TOKEN"
```

### Using JavaScript (Fetch API)

```javascript
// Get token
const authResponse = await fetch('http://localhost:8000/auth/jwt/create/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'john_doe',
    password: 'password123'
  })
});
const { access } = await authResponse.json();

// Create job
const jobResponse = await fetch('http://localhost:8000/api/jobs/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access}`
  },
  body: JSON.stringify({
    company: 'Google',
    role: 'Software Engineer',
    status: 'applied',
    applied_date: '2026-04-17'
  })
});
```

### Using Postman

1. **Create a Collection** called "JobTracker API"
2. **Add Environment Variables:**
   - `base_url`: http://localhost:8000
   - `token`: (populate after login)

3. **Create Requests:**

   **POST: Login**
   - URL: `{{base_url}}/auth/jwt/create/`
   - Body (JSON): `{"username":"john_doe","password":"password123"}`
   - Post-request Script: `pm.environment.set("token", pm.response.json().access);`

   **POST: Create Job**
   - URL: `{{base_url}}/api/jobs/`
   - Headers: `Authorization: Bearer {{token}}`
   - Body (JSON): Job creation payload

   **GET: List Jobs**
   - URL: `{{base_url}}/api/jobs/`
   - Headers: `Authorization: Bearer {{token}}`

---

## 🔍 Troubleshooting

### Backend Issues

#### Error: "ModuleNotFoundError: No module named 'django'"
**Solution:**
```bash
pipenv install
pipenv shell
```

#### Error: "Traceback (most recent call last): ... IntegrityError"
**Solution:** Run migrations
```bash
python manage.py migrate
```

#### Error: "CORS header 'Access-Control-Allow-Origin' missing"
**Solution:** Check `.env` file has correct `CORS_ALLOWED_ORIGINS`:
```env
CORS_ALLOWED_ORIGINS=http://localhost:8001,http://127.0.0.1:8001
```

#### Port 8000 Already in Use
**Solution:**
```bash
# Kill existing process
# Windows:
netstat -ano | findstr :8000
taskkill /PID {PID} /F

# macOS/Linux:
lsof -i :8000
kill -9 {PID}

# Or use different port:
python manage.py runserver 8080
```

### Frontend Issues

#### "Failed to load jobs" Error
**Solution:** 
- Verify backend is running: `http://localhost:8000/`
- Check browser console for errors (F12)
- Ensure API URL is correct in `frontend/js/api.js`

#### Login Not Working
**Solution:**
1. Check backend server is running
2. Verify credentials are correct
3. Open browser console (F12) → Network tab → check login request for errors
4. Check `.env` file has DEBUG=True

#### Port 8001 Already in Use
**Solution:**
```bash
# Use different port
python -m http.server 8002
# Visit http://localhost:8002
```

#### Blank Page or No CSS/JS Loading
**Solution:**
1. Hard refresh browser: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
2. Clear cache: DevTools → Application → Cache Storage → Clear all
3. Check Network tab (F12) to see if files are 404

### Database Issues

#### Error: "SQLite database is locked"
**Solution:**
```bash
# Restart Django
python manage.py runserver
```

#### Lost Admin Access
**Solution:** Create new superuser
```bash
python manage.py createsuperuser
```

#### Need Fresh Database
```bash
# Delete existing database
rm db.sqlite3  # macOS/Linux
del db.sqlite3 # Windows

# Recreate
python manage.py migrate
python manage.py createsuperuser
```

---

## 📊 Project Statistics

- **Backend Tests:** 112 (all passing)
  - API Integration Tests: 44
  - Model Tests: 23
  - Serializer Tests: 20
  - Permission Tests: 25
- **API Endpoints:** 10+
- **Frontend Pages:** 6 (Login, Register, Dashboard, Add Job, Edit Job, Analytics)
- **Code Lines:** ~2,500+ (backend), ~1,500+ (frontend)

---

## 🎓 Learning Resources

### Django REST Framework
- [DRF Documentation](https://www.django-rest-framework.org/)
- [JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/)

### Testing
- [Django Testing](https://docs.djangoproject.com/en/4.2/topics/testing/)
- [DRF Testing](https://www.django-rest-framework.org/api-guide/testing/)

### Frontend
- [Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [localStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)

---

## 📝 License

MIT - Feel free to use, modify, and distribute!

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section above

---

**Last Updated:** April 17, 2026  
**Status:** ✅ Production Ready
