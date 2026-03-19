# Frontend Setup & Usage Guide

## Quick Start

### 1. Prerequisites
- A web browser (Chrome, Firefox, Safari, Edge)
- Backend API running on `http://localhost:5000`
- Python simple HTTP server (included in Python 3)

### 2. Start Frontend Server

**Option A: Using Python (Recommended)**
```bash
cd frontend
python -m http.server 8000
```

**Option B: Using Node.js (if available)**
```bash
cd frontend
npx http-server -p 8000
```

**Option C: Using PHP (if available)**
```bash
cd frontend
php -S localhost:8000
```

### 3. Access Application

Open your browser and navigate to:
```
http://localhost:8000
```

---

## Features

### 📁 File Upload
- **Drag & Drop:** Drag files directly onto the upload zone
- **Click to Browse:** Click the zone to open file picker
- **Supported Formats:** CSV, JSON, XLSX/XLS
- **File Size:** Up to 100MB
- **Async Processing:** Files processed in background

### ✅ Data Validation
- **Automatic Validation:** Analyze data quality
- **Issue Detection:** Identifies missing values, duplicates, type errors
- **Data Preview:** View first 10 rows of data
- **Statistics:** Get column count, record count, data issues

### 📊 Analytics Dashboard
- **Real-time Processing:** Track job progress with visual indicator
- **Job Status:** Monitor processing status (queued → processing → completed)
- **Statistics Cards:** Total records, columns, missing values, duplicates
- **Interactive Charts:**
  - Distribution histogram
  - Correlation matrix
  - Missing values analysis
  - Data quality score

### 📥 Results Management
- **Download Results:** Export processed data as CSV
- **View Insights:** See key findings from analysis
- **New Analysis:** Start fresh analysis with new file

### 🔧 System Status
- **API Health:** Monitor backend connection
- **Queue Workers:** See active processing workers
- **Storage Status:** Check storage availability

---

## API Integration

### Backend Connection
The frontend communicates with the Flask backend API at:
```
http://localhost:5000/api
```

### Main API Endpoints Used
| Endpoint | Purpose |
|----------|---------|
| `POST /upload` | Upload data files |
| `POST /validate` | Validate data quality |
| `POST /process` | Start async processing |
| `GET /async/job/{job_id}` | Check job status |
| `GET /results/{job_id}` | Get processing results |
| `GET /analytics/{job_id}` | Get analytics data |
| `GET /health` | Check API health |
| `GET /async/queue` | Get queue status |
| `GET /storage/stats` | Get storage info |

### API Configuration
To change the backend URL, edit `js/api.js`:
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

---

## File Structure

```
frontend/
├── index.html              # Main HTML file
├── css/
│   └── style.css          # All styling (responsive design)
├── js/
│   ├── api.js             # API client & HTTP requests
│   └── app.js             # Application logic & UI controller
└── README.md              # This file
```

### HTML (`index.html`)
- Navigation header with links
- Upload section with drag-drop
- Data preview section with table
- Dashboard section with charts
- API status footer

### CSS (`css/style.css`)
- Modern gradient colors and shadows
- Fully responsive design (mobile, tablet, desktop)
- Smooth animations and transitions
- Dark mode compatible
- 1000+ lines of polished styling

### JavaScript (`js/api.js`)
- RESTful API client wrapper
- All HTTP communication
- File upload handling
- Job polling mechanism
- Error handling
- Utility functions (file size formatting, validation)

### JavaScript (`js/app.js`)
- Application state management
- User interaction handlers
- DOM manipulation
- Chart.js integration
- Progress tracking
- Message display system

---

## Usage Workflow

### Step 1: Upload File
```
1. Click or drag file onto upload zone
2. Select CSV, JSON, or Excel file
3. Click "Validate Data" button
```

### Step 2: Validate Data
```
1. View validation report
2. See data quality metrics
3. Preview first 10 rows in table
4. Check for issues (missing values, duplicates)
```

### Step 3: Process Data
```
1. Click "Process & Analyze" button
2. Job sent to backend queue
3. Watch progress bar update in real-time
4. Processing status updates automatically
```

### Step 4: View Results
```
1. Dashboard shows statistics cards
2. Interactive charts visualize data
3. Key insights displayed
4. Download processed results as CSV
```

---

## UI Components

### Status Messages
- **Success (Green):** Data validated, processing complete
- **Error (Red):** Validation failed, processing failed
- **Info (Blue):** Processing status updates

### Progress Indicator
- Real-time progress bar
- Shows current percentage (0-100%)
- Updates every 2 seconds while processing
- Color gradient: blue → green

### Statistics Cards
- **Total Records:** Number of rows in dataset
- **Columns:** Number of data fields
- **Missing Values:** NULL/empty cell count
- **Duplicates:** Repeated row count

### Charts (Chart.js)
- Distribution histogram (numeric data)
- Correlation matrix (relationships)
- Missing values bar chart
- Data quality doughnut chart

### Responsive Design
- **Desktop (1200px+):** Full 2-column layout
- **Tablet (768px+):** Stacked single column
- **Mobile (<768px):** Optimized single column
- Touch-friendly button sizes
- Readable font sizes on all devices

---

## Configuration

### Customize API Base URL
Edit `js/api.js`:
```javascript
const API_BASE_URL = 'http://your-backend-url/api';
```

### Adjust Polling Interval
Edit `js/api.js`:
```javascript
const POLL_INTERVAL = 2000;  // 2 seconds between status checks
const POLL_TIMEOUT = 300000; // 5 minutes max polling duration
```

### Change Color Scheme
Edit `css/style.css`:
```css
:root {
    --primary-color: #3b82f6;      /* Blue */
    --secondary-color: #10b981;    /* Green */
    --danger-color: #ef4444;       /* Red */
    --dark-bg: #0f172a;
}
```

---

## Troubleshooting

### Issue: "Cannot connect to backend"
**Solution:**
1. Ensure backend is running: `python backend/app.py`
2. Backend should be on `http://localhost:5000`
3. Check browser console for CORS errors
4. Verify firewall isn't blocking port 5000

### Issue: "File upload fails with 413 error"
**Solution:**
- File is larger than backend's size limit (default 100MB)
- Reduce file size or increase `MAX_FILE_SIZE_MB` in backend config

### Issue: "Processing takes a long time"
**Solution:**
- Large datasets take longer to process
- Check queue status in footer
- Monitor storage usage
- Backend processes jobs sequentially in queue

### Issue: "Charts not displaying"
**Solution:**
1. Check browser console for JavaScript errors
2. Ensure Chart.js CDN is accessible
3. Verify analytics data is returned from backend
4. Try refreshing the page

### Issue: "CORS errors in console"
**Solution:**
1. Ensure backend has CORS enabled
2. Check backend `CORS_ORIGINS` setting
3. Frontend URL might need to be added to CORS whitelist

---

## Browser Support

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome | ✓ | Full support, recommended |
| Firefox | ✓ | Full support |
| Safari | ✓ | Full support |
| Edge | ✓ | Full support |
| IE 11 | ✗ | Not supported |

---

## Performance Tips

1. **Upload Files:**
   - Keep files under 50MB for fastest processing
   - CSV format processes faster than Excel

2. **Network:**
   - Ensure stable internet connection
   - Use 4G/WiFi, not cellular data

3. **Browser:**
   - Clear browser cache if charts lag
   - Use latest browser version
   - Close unnecessary tabs

4. **Backend:**
   - Monitor queue size in status footer
   - Process smaller files first
   - Check storage space availability

---

## Security Notes

1. **File Upload:**
   - Backend validates file types
   - Maximum file size enforced
   - Temporary files stored securely

2. **API Communication:**
   - Uses HTTP over CORS
   - Use HTTPS in production
   - Set appropriate CORS headers

3. **Data Privacy:**
   - Processed files stored in backend storage
   - Review backend data retention policies
   - Use VPN for sensitive data

---

## Development

### Adding New Features

1. **New UI Section:**
   - Add HTML in `index.html`
   - Add CSS in `css/style.css`
   - Add JavaScript in `js/app.js`

2. **New API Endpoint:**
   - Add function in `js/api.js`
   - Use pattern: `async function name() { return request(...) }`
   - Handle errors consistently

3. **New Chart:**
   - Add canvas element in HTML
   - Use `createChart()` in `js/app.js`
   - Follow Chart.js documentation

### Code Organization
- Keep HTML semantic and accessible
- CSS uses CSS variables for consistency
- JavaScript uses IIFE pattern for encapsulation
- All user-facing strings centralized for i18n

---

## Support & Troubleshooting

### Check Status
1. Open "System Status" section at bottom
2. Verify all services show green
3. Check queue workers are active
4. Monitor storage usage

### View Logs
- **Browser Console:** Press F12, go to Console tab
- **Backend Logs:** Check `logs/` directory
- **Storage:** Check `storage/` directory

### Contact Support
For issues:
1. Check browser console for errors
2. Check backend logs for failures
3. Verify API connectivity
4. Review troubleshooting section above

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | March 2026 | Initial release |

---

## License

This frontend application is part of the Advanced Data Processing & Analytics Platform.
For licensing terms, see LICENSE file in project root.

---

**Last Updated:** March 18, 2026
