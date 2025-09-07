# Camera Proctoring Troubleshooting Guide

This guide helps diagnose and resolve issues with the camera proctoring system in CodeBuzz.

## Common Issues and Solutions

### 1. Camera Not Accessible

**Symptoms:**
- "Camera access denied" message
- "No camera found" error
- Camera permission prompt not appearing

**Solutions:**
1. Check browser permissions:
   - Chrome: Settings → Privacy and security → Site Settings → Camera
   - Firefox: Preferences → Privacy & Security → Permissions → Camera
   - Safari: Preferences → Websites → Camera

2. Ensure no other applications are using the camera

3. Try refreshing the page or restarting the browser

4. Check if the website is being served over HTTPS (required for camera access)

### 2. Proctoring Not Starting Automatically

**Symptoms:**
- Manual start button appears
- Proctoring status shows "Inactive"
- Console shows "Proctoring not required" message

**Solutions:**
1. Verify contest settings:
   - Check if `requires_proctoring` is enabled for the contest
   - Ensure the contest is currently running

2. Check session state:
   - Clear browser cache and cookies
   - Ensure you're logged in as a participant

3. Look for JavaScript errors in the browser console

### 3. Face Detection Not Working

**Symptoms:**
- "No face detected" warnings
- Frequent violations
- Proctoring status shows warnings

**Solutions:**
1. Lighting conditions:
   - Ensure adequate lighting
   - Avoid backlighting (e.g., sitting with window behind you)

2. Camera positioning:
   - Position camera at eye level
   - Keep face centered in frame
   - Maintain appropriate distance (arm's length)

3. Background:
   - Use a plain background when possible
   - Avoid cluttered or busy backgrounds

## Technical Debugging Steps

### 1. Check Browser Console

Open the browser's developer tools (F12) and check the Console tab for any error messages related to:
- Camera access failures
- JavaScript exceptions
- Network errors with proctoring endpoints

### 2. Verify Computer Vision Libraries

Run the test script to verify libraries are properly installed:
```bash
python test_cv.py
```

Expected output:
```
Testing computer vision library imports...
==================================================
NumPy version: 1.26.4
NumPy import successful
OpenCV version: 4.11.0
OpenCV import successful
MediaPipe version: 0.10.21
MediaPipe import successful
==================================================
All tests passed! Computer vision libraries are ready.
```

### 3. Check Proctoring Endpoints

Verify the proctoring endpoints are accessible:
- `/contests/{contest_id}/proctoring/start/`
- `/contests/{contest_id}/proctoring/monitor/`
- `/contests/{contest_id}/proctoring/status/`

### 4. Database Session Check

Ensure the ProctoringSession is properly created:
```bash
python manage.py shell
```

```python
from hackIDE.models import ProctoringSession
# Check if sessions exist for your user and contest
sessions = ProctoringSession.objects.filter(user__username='your_username')
print(sessions)
```

## Code Fixes

### 1. Update JavaScript Error Handling

The proctoring system has been enhanced with better error handling and fallback mechanisms.

### 2. Improve Camera Stream Management

The GlobalCameraManager now has improved stream persistence and recovery mechanisms.

### 3. Enhanced Debugging Information

Added more detailed console logging to help diagnose issues.

## Browser Compatibility

The proctoring system works best with:
- Chrome (latest version)
- Firefox (latest version)
- Edge (latest version)

Safari has known issues with camera access in some configurations.

## Network Requirements

- Stable internet connection
- No content blockers or ad blockers that might interfere with camera access
- Proper CORS configuration for API endpoints

## Advanced Troubleshooting

### 1. Manual Camera Test

Navigate to `/camera-test/` to test camera access independently of the proctoring system.

### 2. Check Media Devices

In browser console:
```javascript
navigator.mediaDevices.enumerateDevices().then(devices => {
    console.log('Available media devices:', devices);
});
```

### 3. Verify SSL/TLS

Camera access requires a secure context (HTTPS or localhost). Ensure your deployment uses HTTPS.

## Contact Support

If issues persist after trying all troubleshooting steps:
1. Provide browser console output
2. Include steps to reproduce the issue
3. Specify browser and operating system versions
4. Attach any relevant screenshots