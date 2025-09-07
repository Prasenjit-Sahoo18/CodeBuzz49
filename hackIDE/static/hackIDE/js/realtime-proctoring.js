/**
 * Real-time Proctoring System
 * Continuous camera monitoring with face detection for contest integrity
 */

// Check if required browser APIs are available
if (typeof navigator === 'undefined' || typeof window === 'undefined') {
    console.error('Required browser APIs not available');
}

class RealtimeProctoring {
    constructor(contestId, csrfToken) {
        // Validate inputs
        if (!contestId || !csrfToken) {
            throw new Error('Invalid parameters: contestId and csrfToken are required');
        }
        
        this.contestId = contestId;
        this.csrfToken = csrfToken;
        this.isActive = false;
        this.violationCount = 0;
        this.warningCount = 0;
        this.contestTerminated = false;
        
        // Camera and monitoring settings
        this.video = null;
        this.canvas = null;
        this.ctx = null;
        this.stream = null;
        this.monitoringInterval = null;
        this.checkInterval = 3000; // Check every 3 seconds
        
        // UI elements
        this.statusIndicator = null;
        this.warningModal = null;
        this.terminationModal = null;
        
        // Callbacks
        this.onWarning = null;
        this.onTermination = null;
        this.onStatusUpdate = null;
        
        this.init();
    }
    
    init() {
        this.createUI();
        this.setupEventListeners();
    }
    
    createUI() {
        // Create hidden video element for camera capture
        this.video = document.createElement('video');
        this.video.width = 320;
        this.video.height = 240;
        this.video.autoplay = true;
        this.video.playsInline = true;
        this.video.muted = true;  // Add muted to help with autoplay
        this.video.style.display = 'none';
        document.body.appendChild(this.video);
        
        // Create hidden canvas for image capture
        this.canvas = document.createElement('canvas');
        this.canvas.width = 320;
        this.canvas.height = 240;
        this.canvas.style.display = 'none';
        this.ctx = this.canvas.getContext('2d');
        document.body.appendChild(this.canvas);
        
        // Create status indicator
        this.createStatusIndicator();
        
        // Create warning modal
        this.createWarningModal();
        
        // Create termination modal
        this.createTerminationModal();
        
        // Create debug overlay (only in development)
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            this.createDebugOverlay();
        }
    }
    
    createStatusIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'proctoring-status';
        indicator.innerHTML = `
            <div class="proctoring-indicator">
                <div class="indicator-dot" id="proctoring-dot"></div>
                <span id="proctoring-text">Proctoring: Inactive</span>
            </div>
        `;
        // Fixed CSS with proper values
        indicator.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 10000; background: rgba(0, 0, 0, 0.8); color: white; padding: 10px 15px; border-radius: 20px; font-size: 12px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;';
        
        const style = document.createElement('style');
        style.textContent = '.proctoring-indicator { display: flex; align-items: center; } .proctoring-indicator > * { margin-right: 8px; } .proctoring-indicator > *:last-child { margin-right: 0; } .indicator-dot { width: 8px; height: 8px; border-radius: 50%; background: #dc3545; animation: pulse 2s infinite; } .indicator-dot.active { background: #28a745; } .indicator-dot.warning { background: #ffc107; } .indicator-dot.terminated { background: #dc3545; animation: none; } @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }';
        document.head.appendChild(style);
        document.body.appendChild(indicator);
        
        this.statusIndicator = indicator;
    }
    
    createWarningModal() {
        const modal = document.createElement('div');
        modal.id = 'warning-modal';
        modal.innerHTML = `
            <div class="modal fade" tabindex="-1" role="dialog">
                <div class="modal-dialog modal-dialog-centered" role="document">
                    <div class="modal-content border-warning">
                        <div class="modal-header bg-warning text-dark">
                            <h5 class="modal-title">⚠️ Proctoring Warning</h5>
                        </div>
                        <div class="modal-body">
                            <div class="alert alert-warning">
                                <p id="warning-message" class="mb-0"></p>
                            </div>
                            <div class="warning-details">
                                <p><strong>Warning Count:</strong> <span id="warning-count-display">0</span>/2</p>
                                <p class="mb-0"><strong>Note:</strong> After 2 warnings, your contest will be automatically terminated.</p>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-warning" data-bs-dismiss="modal">I Understand</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        this.warningModal = new bootstrap.Modal(modal.querySelector('.modal'));
    }
    
    createTerminationModal() {
        const modal = document.createElement('div');
        modal.id = 'termination-modal';
        modal.innerHTML = `
            <div class="modal fade" tabindex="-1" role="dialog" data-bs-backdrop="static" data-bs-keyboard="false">
                <div class="modal-dialog modal-dialog-centered" role="document">
                    <div class="modal-content border-danger">
                        <div class="modal-header bg-danger text-white">
                            <h5 class="modal-title">🚫 Contest Terminated</h5>
                        </div>
                        <div class="modal-body text-center">
                            <div class="alert alert-danger">
                                <h6>Your contest has been terminated due to multiple proctoring violations.</h6>
                                <p class="mb-0">You exceeded the maximum number of allowed warnings (2).</p>
                            </div>
                            <div class="mt-3">
                                <p><strong>Total Violations:</strong> <span id="final-violation-count">3</span></p>
                                <p><strong>Reason:</strong> Face detection violations</p>
                            </div>
                            <div class="mt-4">
                                <p class="text-muted">You will be redirected to the contest list shortly.</p>
                            </div>
                        </div>
                        <div class="modal-footer justify-content-center">
                            <button type="button" class="btn btn-danger" onclick="window.location.href='/contests/'">
                                Return to Contests
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        this.terminationModal = new bootstrap.Modal(modal.querySelector('.modal'));
    }
    
    createDebugOverlay() {
        const debugPanel = document.createElement('div');
        debugPanel.id = 'proctoring-debug';
        debugPanel.innerHTML = `
            <div style="
                position: fixed;
                bottom: 20px;
                left: 20px;
                background: rgba(0,0,0,0.9);
                color: white;
                padding: 15px;
                border-radius: 8px;
                font-family: monospace;
                font-size: 12px;
                z-index: 10002;
                min-width: 300px;
                max-height: 200px;
                overflow-y: auto;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <strong>🔧 Proctoring Debug</strong>
                    <button onclick="this.parentElement.parentElement.parentElement.style.display='none'" 
                            style="background: none; border: none; color: white; cursor: pointer; margin-left: 10px;">✕</button>
                </div>
                <div id="debug-info"></div>
                <div style="margin-top: 10px;">
                    <button onclick="window.proctoring && window.proctoring.start()" 
                            style="background: #28a745; border: none; color: white; padding: 5px 10px; border-radius: 4px; cursor: pointer; margin-right: 5px;">Start</button>
                    <button onclick="window.proctoring && window.proctoring.stop()" 
                            style="background: #dc3545; border: none; color: white; padding: 5px 10px; border-radius: 4px; cursor: pointer; margin-right: 5px;">Stop</button>
                    <button onclick="window.proctoring && window.proctoring.checkFace()" 
                            style="background: #007bff; border: none; color: white; padding: 5px 10px; border-radius: 4px; cursor: pointer;">Test Face Check</button>
                </div>
            </div>
        `;
        document.body.appendChild(debugPanel);
        
        // Update debug info periodically
        setInterval(() => {
            const debugInfo = document.getElementById('debug-info');
            if (debugInfo && this) {
                debugInfo.innerHTML = `
                    <div>Active: ${this.isActive}</div>
                    <div>Stream: ${this.stream ? 'Connected' : 'None'}</div>
                    <div>Video Ready: ${this.video ? this.video.readyState : 'No Video'}</div>
                    <div>Violations: ${this.violationCount}</div>
                    <div>Warnings: ${this.warningCount}</div>
                    <div>Terminated: ${this.contestTerminated}</div>
                `;
            }
        }, 1000);
        
        // Make proctoring instance available globally for debugging
        window.proctoring = this;
    }
    
    setupEventListeners() {
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && this.isActive) {
                console.log('Page hidden - proctoring continues in background');
            }
        });
        
        // Handle beforeunload to clean up
        window.addEventListener('beforeunload', () => {
            this.stop();
        });
    }
    
    async start() {
        if (this.isActive) {
            console.log('Proctoring already active');
            return true;
        }
        
        console.log('Starting real-time proctoring...');
        this.updateStatus('warning', 'Proctoring: Starting...');
        
        try {
            // Check if required browser APIs are available
            if (!navigator.mediaDevices) {
                throw new Error('Media devices API not available in this browser. Please use Chrome, Firefox, or Edge.');
            }
            
            if (!navigator.mediaDevices.getUserMedia) {
                throw new Error('Camera access not supported in this browser. Please use Chrome, Firefox, or Edge.');
            }
            
            // Log browser capabilities
            console.log('Browser media devices support:', !!navigator.mediaDevices);
            console.log('Browser media devices getUserMedia support:', !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia));
            
            // First priority: Use GlobalCameraManager if available
            if (window.contestCameraManager && window.contestCameraManager.isStreamActive()) {
                console.log('Using GlobalCameraManager stream for proctoring...');
                this.stream = window.contestCameraManager.getStream();
                this.video.srcObject = this.stream;
                
                // Mark our video element as proctoring active
                this.video.setAttribute('data-proctoring-active', 'true');
                this.video.setAttribute('data-global-managed', 'true');
                
                // Wait for video to be ready
                await new Promise(resolve => {
                    this.video.onloadedmetadata = () => {
                        console.log('Video metadata loaded from GlobalCameraManager stream');
                        resolve();
                    };
                    // If already loaded
                    if (this.video.readyState >= 2) {
                        resolve();
                    }
                });
                
                try {
                    await this.video.play();
                    console.log('Video is playing from GlobalCameraManager stream');
                } catch (playError) {
                    console.warn('Video autoplay failed, but continuing:', playError);
                }
            }
            // Second priority: Check for persistent camera stream from navigation
            else {
                const persistentVideo = document.querySelector('video[data-persistent="true"]');
                let streamFound = false;
                
                if (persistentVideo && persistentVideo.srcObject && persistentVideo.srcObject.active) {
                    console.log('Found persistent camera stream from navigation, using it...');
                    this.stream = persistentVideo.srcObject;
                    this.video.srcObject = this.stream;
                    
                    // Mark our video element as proctoring active
                    this.video.setAttribute('data-proctoring-active', 'true');
                    
                    // Clean up the persistent video element
                    setTimeout(() => {
                        if (persistentVideo && persistentVideo.parentNode) {
                            persistentVideo.remove();
                            console.log('Cleaned up persistent video element');
                        }
                    }, 1000);
                    
                    streamFound = true;
                }
                // Third priority: Check if camera is already active from initial verification
                else {
                    const existingVideo = document.querySelector('video[data-proctoring-active="true"]');
                    
                    // First priority: Check for marked video element with active stream
                    if (existingVideo && existingVideo.srcObject) {
                        console.log('Found existing proctoring video with stream, reusing...');
                        this.stream = existingVideo.srcObject;
                        this.video.srcObject = this.stream;
                        streamFound = true;
                    }
                    // Second priority: Check for any video element with stream on the page
                    else {
                        const allVideos = document.querySelectorAll('video');
                        for (let vid of allVideos) {
                            if (vid.srcObject && vid.srcObject.active) {
                                console.log('Found active video stream, reusing for proctoring...');
                                this.stream = vid.srcObject;
                                this.video.srcObject = this.stream;
                                // Mark this video as proctoring active
                                vid.setAttribute('data-proctoring-active', 'true');
                                streamFound = true;
                                break;
                            }
                }
                    }
                }
                
                if (streamFound) {
                    // Wait for video to be ready
                    await new Promise(resolve => {
                        this.video.onloadedmetadata = () => {
                            console.log('Video metadata loaded from existing stream');
                            resolve();
                        };
                        // If already loaded
                        if (this.video.readyState >= 2) {
                            resolve();
                        }
                    });
                    
                    try {
                        await this.video.play();
                        console.log('Video is playing from existing stream');
                    } catch (playError) {
                        console.warn('Video autoplay failed, but continuing:', playError);
                    }
                } else {
                    // Check if getUserMedia is supported
                    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                        throw new Error('Camera access is not supported in this browser. Please use Chrome, Firefox, or Edge.');
                    }
                    
                    console.log('Requesting new camera access...');
                    
                    // Request camera permission with more permissive constraints
                    this.stream = await navigator.mediaDevices.getUserMedia({
                        video: { 
                            facingMode: 'user',
                            width: { ideal: 320, min: 240 },
                            height: { ideal: 240, min: 180 }
                        },
                        audio: false
                    });
                    
                    console.log('Camera stream obtained:', this.stream);
                    
                    this.video.srcObject = this.stream;
                    
                    // Register with GlobalCameraManager if available
                    if (window.contestCameraManager) {
                        console.log('Registering new stream with GlobalCameraManager');
                        window.contestCameraManager.stream = this.stream;
                        window.contestCameraManager.isActive = true;
                        window.contestCameraManager.contestId = this.contestId;
                        window.contestCameraManager.attachToElement(this.video, true);
                        window.contestCameraManager.saveState();
                        
                        // Create hidden video for persistence
                        window.contestCameraManager.createHiddenVideo();
                    }
                    
                    // Wait for video to be ready with timeout
                    await Promise.race([
                        new Promise(resolve => {
                            this.video.onloadedmetadata = () => {
                                console.log('Video metadata loaded');
                                resolve();
                            };
                        }),
                        new Promise((_, reject) => {
                            setTimeout(() => reject(new Error('Video load timeout - camera may be blocked or in use')), 10000);
                        })
                    ]);
                    
                    // Ensure video is playing
                    try {
                        await this.video.play();
                        console.log('Video is playing');
                    } catch (playError) {
                        console.warn('Video autoplay failed, but continuing:', playError);
                    }
                }
            }
            
            // Validate that we have a working stream
            if (!this.stream || !this.stream.active) {
                throw new Error('Camera stream is not active. Please check camera permissions and try again.');
            }
            
            // Log stream details for debugging
            console.log('Stream details:', {
                active: this.stream.active,
                id: this.stream.id,
                tracks: this.stream.getTracks().map(track => ({
                    kind: track.kind,
                    readyState: track.readyState,
                    enabled: track.enabled
                }))
            });
            
            // Start proctoring on server
            console.log('Starting server-side proctoring...');
            const response = await fetch(`/contests/${this.contestId}/proctoring/start/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server error: ${response.status} - ${errorText}`);
            }
            
            const data = await response.json();
            console.log('Server response:', data);
            
            if (data.success) {
                this.isActive = true;
                this.startMonitoring();
                this.updateStatus('active', 'Proctoring: Active ✓');
                console.log('Real-time proctoring started successfully');
                
                // Show success message
                this.showTemporaryMessage('📹 Camera proctoring is now active', 'success');
                
                if (this.onStatusUpdate) {
                    this.onStatusUpdate('started');
                }
                
                return true;
            } else {
                throw new Error(data.message || 'Failed to start proctoring on server');
            }
            
        } catch (error) {
            console.error('Failed to start proctoring:', error);
            this.updateStatus('error', 'Proctoring: Error');
            
            let errorMessage = 'Failed to start camera proctoring. ';
            
            // Enhanced error handling with more specific messages
            if (error.name === 'NotAllowedError' || (error.message && error.message.includes('denied'))) {
                errorMessage += 'Camera access was denied. Please allow camera access and refresh the page.';
            } else if (error.name === 'NotFoundError' || (error.message && error.message.includes('found'))) {
                errorMessage += 'No camera found. Please connect a camera and refresh the page.';
            } else if (error.name === 'NotReadableError' || (error.message && error.message.includes('use'))) {
                errorMessage += 'Camera is already in use by another application.';
            } else if (error.message && error.message.includes('not supported')) {
                errorMessage += 'Your browser does not support camera access. Please use Chrome, Firefox, or Edge.';
            } else if (error.message && error.message.includes('timeout')) {
                errorMessage += 'Camera initialization timed out. Please check camera permissions and try again.';
            } else if (error.message) {
                errorMessage += error.message;
            } else {
                errorMessage += 'Unknown error occurred. Please check browser compatibility and camera permissions.';
            }
            
            this.showTemporaryMessage(errorMessage, 'error');
            
            // Don't throw the error, just log it and return false to indicate failure
            return false;
        }
    }
    
    stop() {
        if (!this.isActive) return;
        
        this.isActive = false;
        
        // Stop monitoring
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
        }
        
        // Only stop camera if we should actually stop it
        // Don't stop if it's managed by GlobalCameraManager unless explicitly stopping contest
        if (this.stream) {
            if (window.contestCameraManager && window.contestCameraManager.isStreamActive() && this.stream === window.contestCameraManager.getStream()) {
                console.log('Not stopping camera stream - managed by GlobalCameraManager');
                // Just remove our reference, but keep the stream active
                this.stream = null;
            } else {
                console.log('Stopping camera stream (not managed by GlobalCameraManager)');
                this.stream.getTracks().forEach(track => track.stop());
                this.stream = null;
            }
        }
        
        this.updateStatus('inactive', 'Proctoring: Stopped');
        console.log('Real-time proctoring stopped');
        
        if (this.onStatusUpdate) {
            this.onStatusUpdate('stopped');
        }
    }
    
    startMonitoring() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
        }
        
        console.log('Starting face monitoring with', this.checkInterval, 'ms interval');
        
        this.monitoringInterval = setInterval(() => {
            this.checkFace();
        }, this.checkInterval);
        
        // Also do an immediate check after a short delay to ensure video is ready
        setTimeout(() => {
            console.log('Performing initial face check...');
            this.checkFace();
        }, 2000);
    }
    
    async checkFace() {
        if (!this.isActive || !this.video || !this.ctx) {
            console.log('checkFace called but conditions not met:', {
                isActive: this.isActive,
                hasVideo: !!this.video,
                hasCtx: !!this.ctx
            });
            return;
        }
        
        try {
            // Check if video is ready and playing
            if (this.video.readyState < 2) {
                console.log('Video not ready for capture, readyState:', this.video.readyState);
                return;
            }
            
            // Capture current frame
            console.log('Capturing frame for face detection...');
            this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
            const dataUrl = this.canvas.toDataURL('image/jpeg', 0.8);
            
            // Verify we got valid image data
            if (!dataUrl || dataUrl === 'data:,') {
                console.error('Failed to capture valid image data');
                return;
            }
            
            // Send to server for face detection
            const formData = new FormData();
            formData.append('image', dataUrl);
            
            console.log('Sending frame for analysis...');
            const response = await fetch(`/contests/${this.contestId}/proctoring/monitor/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken
                },
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Face detection response:', data);
            
            if (data.contest_terminated) {
                this.handleTermination(data);
                return;
            }
            
            // Update status
            this.violationCount = data.violation_count || 0;
            this.warningCount = data.warning_count || 0;
            this.contestTerminated = data.contest_terminated || false;
            
            if (data.violation_added) {
                this.handleViolation(data);
            } else if (data.face_detected) {
                this.updateStatus('active', 'Proctoring: Face Detected ✓');
            } else {
                this.updateStatus('warning', 'Proctoring: No Face Detected');
            }
            
        } catch (error) {
            console.error('Face check failed:', error);
            this.updateStatus('error', 'Proctoring: Connection Error');
        }
    }
    
    handleViolation(data) {
        console.log('Proctoring violation detected:', data);
        
        if (data.contest_terminated) {
            this.handleTermination(data);
        } else {
            this.showWarning(data);
        }
        
        if (this.onWarning) {
            this.onWarning(data);
        }
    }
    
    showWarning(data) {
        const warningMessage = document.getElementById('warning-message');
        const warningCountDisplay = document.getElementById('warning-count-display');
        
        warningMessage.textContent = data.message || 'Face detection violation detected.';
        warningCountDisplay.textContent = data.warning_count;
        
        this.updateStatus('warning', `Warning ${data.warning_count}/2`);
        this.warningModal.show();
    }
    
    handleTermination(data) {
        console.log('Contest terminated:', data);
        
        this.contestTerminated = true;
        this.stop();
        
        // Update termination modal
        const finalViolationCount = document.getElementById('final-violation-count');
        finalViolationCount.textContent = data.violation_count || 3;
        
        this.updateStatus('terminated', 'Contest Terminated');
        this.terminationModal.show();
        
        // Auto-redirect after 10 seconds
        setTimeout(() => {
            window.location.href = '/contests/';
        }, 10000);
        
        if (this.onTermination) {
            this.onTermination(data);
        }
    }
    
    updateStatus(state, text) {
        const dot = document.getElementById('proctoring-dot');
        const statusText = document.getElementById('proctoring-text');
        
        if (dot && statusText) {
            dot.className = `indicator-dot ${state}`;
            statusText.textContent = text;
        }
    }
    
    async getStatus() {
        try {
            const response = await fetch(`/contests/${this.contestId}/proctoring/status/`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Failed to get proctoring status:', error);
            return null;
        }
    }
    
    // Public API methods
    setOnWarning(callback) {
        this.onWarning = callback;
    }
    
    setOnTermination(callback) {
        this.onTermination = callback;
    }
    
    setOnStatusUpdate(callback) {
        this.onStatusUpdate = callback;
    }
    
    isMonitoringActive() {
        return this.isActive;
    }
    
    getViolationCount() {
        return this.violationCount;
    }
    
    getWarningCount() {
        return this.warningCount;
    }
    
    isContestTerminated() {
        return this.contestTerminated;
    }
    
    // Get the current camera stream
    getStream() {
        return this.stream;
    }
    
    // Helper method to show temporary messages
    showTemporaryMessage(message, type = 'info') {
        // Remove any existing temporary message
        const existingMsg = document.getElementById('temp-proctoring-message');
        if (existingMsg) {
            existingMsg.remove();
        }
        
        // Create temporary message element
        const msgElement = document.createElement('div');
        msgElement.id = 'temp-proctoring-message';
        msgElement.style.cssText = `
            position: fixed;
            top: 70px;
            right: 20px;
            z-index: 10001;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 14px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        
        // Set colors based on type
        if (type === 'success') {
            msgElement.style.background = '#d4edda';
            msgElement.style.border = '1px solid #c3e6cb';
            msgElement.style.color = '#155724';
        } else if (type === 'error') {
            msgElement.style.background = '#f8d7da';
            msgElement.style.border = '1px solid #f5c6cb';
            msgElement.style.color = '#721c24';
        } else {
            msgElement.style.background = '#d1ecf1';
            msgElement.style.border = '1px solid #bee5eb';
            msgElement.style.color = '#0c5460';
        }
        
        msgElement.textContent = message;
        document.body.appendChild(msgElement);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (msgElement.parentNode) {
                msgElement.remove();
            }
        }, 5000);
    }
}

// Export for use in other scripts
window.RealtimeProctoring = RealtimeProctoring;