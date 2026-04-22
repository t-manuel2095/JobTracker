# JobTracker Frontend

A clean, vanilla HTML/CSS/JavaScript frontend for the JobTracker API.

## Features

- 🔐 **Authentication**: Register and login with JWT tokens
- 📋 **Dashboard**: View all your job applications in a responsive list
- ➕ **Add Jobs**: Create new job application records
- ✏️ **Edit Jobs**: Update existing job applications
- 🗑️ **Delete Jobs**: Remove job applications
- 🔍 **Search & Filter**: Find jobs by company or filter by status
- 📊 **Status Timeline**: View the history of status changes for each job
- 📈 **Analytics**: See statistics about your applications

## Getting Started

### Prerequisites

- Django backend running on `http://localhost:8000`
- Python backend with proper CORS configuration

### Setup

1. **No build required!** Just open `index.html` in a web browser

```bash
# Simple HTTP server (Python 3)
python -m http.server 8001
```

Then visit: `http://localhost:8001`

### Environment Configuration

The frontend uses the following API endpoint:
- **API Base URL**: `http://localhost:8000/api`

If your backend is running on a different host/port, edit `frontend/js/api.js`:

```javascript
const API_BASE_URL = 'http://your-backend-host:port/api';
```

## Project Structure

```
frontend/
├── index.html          # Main entry point
├── css/
│   └── style.css       # All styling (responsive design)
├── js/
│   ├── api.js          # API communication layer
│   ├── auth.js         # Authentication management
│   ├── dashboard.js    # Main application logic
│   ├── analytics.js    # Analytics display
│   └── main.js         # Initialization
└── README.md           # This file
```

## How It Works

### Authentication Flow

1. User registers with username, email, password
2. Backend creates user and returns confirmation
3. User is auto-logged in with JWT token
4. Token stored in `localStorage`
5. All API requests include token in `Authorization` header

### Job Management

1. **Add**: Fill form → POST to `/api/jobs/`
2. **View**: Jobs displayed in list with status badges
3. **Edit**: Click edit → PATCH to `/api/jobs/{id}/`
4. **Delete**: Confirm deletion → DELETE `/api/jobs/{id}/`
5. **History**: Click "History" → displays timeline of status changes

### Analytics

Dashboard shows:
- Total applications count
- Success rate percentage
- Rejection rate percentage
- Breakdown by status (applied, interview, offer, rejected)

## Features in Detail

### Authentication

- **Login Form**: Username + Password
- **Register Form**: Username + Email + Password
- **Token Storage**: Stored in localStorage as `auth_token`
- **Auto-logout**: Invalid token redirects to login

### Dashboard

- **Responsive Design**: Works on desktop, tablet, mobile
- **Search**: Real-time search by company name
- **Filter**: Dropdown to filter by status
- **Sort**: Applied date sorting
- **Status Badges**: Color-coded status indicators
- **Quick Actions**: Edit, View History, Delete buttons

### Status History

- **Timeline View**: Chronological list of status changes
- **Formatted Display**: Shows "Applied → Interview" transitions
- **Timestamps**: Each change has a timestamp

### Analytics

- **Summary Cards**: Key metrics at a glance
- **Status Distribution**: See breakdown of all statuses
- **Percentages**: View success and rejection rates

## Styling

All styling is in `css/style.css` with:
- CSS variables for easy theme customization
- Mobile-first responsive design
- Smooth transitions and hover effects
- Accessible color contrast

### Color Scheme

- **Primary**: Blue (#007bff)
- **Success**: Green (#28a745)
- **Danger**: Red (#dc3545)
- **Warning**: Orange (#ffc107)
- **Dark**: Charcoal (#343a40)

## API Integration

### Authentication Endpoints

- `POST /auth/users/` - Register
- `POST /auth/jwt/create/` - Login

### Job Endpoints

- `GET /jobs/` - List jobs (with filters)
- `POST /jobs/` - Create job
- `GET /jobs/{id}/` - Get single job
- `PATCH /jobs/{id}/` - Update job
- `DELETE /jobs/{id}/` - Delete job

### History Endpoints

- `GET /jobs/{id}/history/` - List status changes
- `GET /jobs/{id}/status_timeline/` - Formatted timeline

### Analytics Endpoints

- `GET /stats/stats/` - Stats summary
- `GET /stats/detailed_stats/` - Detailed analytics

## Troubleshooting

### Issue: "Failed to load jobs" error

**Solution**: Ensure backend is running on `http://localhost:8000` and CORS is configured to allow requests from your frontend URL.

### Issue: Login not working

**Solution**: 
1. Check backend is running
2. Verify credentials are correct
3. Check browser console for error messages

### Issue: Frontend shows blank page

**Solution**:
1. Check browser console for JavaScript errors
2. Ensure all `.js` files are loading (Network tab)
3. Clear browser cache and refresh

## Browser Compatibility

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- IE11: ⚠️ Requires polyfills

## Future Enhancements

- [ ] Dark mode toggle
- [ ] Export statistics to CSV
- [ ] Calendar view for applications
- [ ] Email notifications
- [ ] Notes editor with formatting
- [ ] Salary tracking
- [ ] Interview notes
- [ ] Company ratings

## License

MIT - Feel free to use and modify!
