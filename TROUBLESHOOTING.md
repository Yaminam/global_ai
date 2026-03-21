# Troubleshooting Guide

## "Process & Analyze" Not Working

### Check Browser Console
1. Open browser DevTools: `F12`
2. Go to **Console** tab
3. Look for error messages
4. Share these errors for debugging

### Common Issues

#### Issue: File Upload Fails
**Symptom:** Upload button doesn't respond
**Solution:**
- Check file size (max 100MB)
- Try different file format (CSV, JSON, Excel)
- Clear browser cache (Ctrl+Shift+Delete)
- Check browser console for errors

#### Issue: "Process" Button Doesn't Work
**Symptom:** File uploads but "Process & Analyze" has no effect
**Solution:**
- Refresh the page after upload
- Wait 2-3 seconds after file uploads before clicking Process
- Check that API is actually running
- Open browser DevTools → Network tab → click Process
  - Look for XHR request to `/api/process`
  - Check response (should show success: true)

#### Issue: Server Errors (500)
**Symptom:** Processing fails with "server error"
**Solution:**
1. Check Render logs: Dashboard → global_ai → Logs
2. Look for lines starting with "ERROR:" or "DEBUG:"
3. These will show exact problem

### Local Testing
```bash
# Start backend with debug output
python -m flask --app run_backend run --debug

# In another terminal, test API
curl -X POST http://localhost:5000/api/validate \
  -H "Content-Type: application/json" \
  -d '{"file_path": "./storage/uploads/test.csv"}'
```

### On Render
1. Go to dashboard.render.com
2. Click on "global_ai" service
3. Go to **Logs** tab
4. Upload file and click Process
5. Look for error messages in logs

## Getting Help

Include:
- Browser console errors (F12)
- Render logs (last 50 lines)
- Screenshot of what's happening
- File name and format you're uploading
