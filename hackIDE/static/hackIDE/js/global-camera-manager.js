/**
 * Global Camera Manager for Contest Proctoring
 * Ensures camera remains active throughout entire contest session
 */

// Check if required browser APIs are available
if (typeof navigator === 'undefined' || typeof window === 'undefined') {
    console.error('Required browser APIs not available');
}

class GlobalCameraManager {
    constructor() {
        this.stream = null;
        this.isActive = false;
        this.contestId = null;
        this.storageKey = 'contest_camera_state';
        this.streamKey = 'contest_camera_stream_id';
        this.videoElements = new Set();
        
        this.init();
    }
    
    init() {
        console.log('GlobalCameraManager: Initializing...');
        
        // Bind to window for global access
        window.contestCameraManager = this;
        
        // Restore state on page load
        this.restoreState();
        
        // Prevent camera loss on page unload
        this.setupUnloadPrevention();
        
        // Setup periodic state saving
        this.setupStatePersistence();
        
        // Setup beforeunload protection
        this.setupBeforeUnloadProtection();
    }
    
    async startCamera(contestId, forceNew = false) {
        console.log('GlobalCameraManager: Starting camera for contest', contestId);
        
        this.contestId = contestId;
        
        // Check if we already have an active stream
        if (this.stream && this.stream.active && !forceNew) {
            console.log('GlobalCameraManager: Using existing active stream');
            this.isActive = true;
            this.saveState();
            return this.stream;
        }
        
        // Try to restore from any existing video element
        if (!forceNew) {
            const existingStream = this.findExistingStream();
            if (existingStream) {
                console.log('GlobalCameraManager: Found existing stream, adopting it');
                this.stream = existingStream;
                this.isActive = true;
                this.saveState();
                return this.stream;
            }
        }
        
        try {
            // Check if getUserMedia is supported
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('Camera access is not supported in this browser. Please use Chrome, Firefox, or Edge.');
            }
            
            // Request new camera access with more detailed constraints
            console.log('GlobalCameraManager: Requesting new camera access');
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: { 
                    facingMode: 'user',
                    width: { ideal: 320, min: 240 },
                    height: { ideal: 240, min: 180 }
                },
                audio: false
            });
            
            this.isActive = true;
            this.saveState();
            
            console.log('GlobalCameraManager: Camera started successfully');
            return this.stream;
            
        } catch (error) {
            console.error('GlobalCameraManager: Failed to start camera:', error);
            
            // Provide more specific error messages
            let errorMessage = 'Failed to access camera. ';
            
            if (error.name === 'NotAllowedError' || (error.message && error.message.includes('denied'))) {
                errorMessage += 'Please allow camera access in your browser settings and refresh the page.';
            } else if (error.name === 'NotFoundError' || (error.message && error.message.includes('found'))) {
                errorMessage += 'No camera detected. Please connect a camera and try again.';
            } else if (error.name === 'NotReadableError' || (error.message && error.message.includes('use'))) {
                errorMessage += 'Camera is already in use by another application.';
            } else if (error.message && error.message.includes('not supported')) {
                errorMessage += 'Your browser does not support camera access. Please use Chrome, Firefox, or Edge.';
            } else if (error.message) {
                errorMessage += error.message;
            } else {
                errorMessage += 'Unknown error occurred.';
            }
            
            // Show error to user
            this.showErrorMessage(errorMessage);
            
            this.isActive = false;
            this.saveState();
            throw error;
        }
    }
    
    findExistingStream() {
        // Look for any video element with an active stream
        const videos = document.querySelectorAll('video');
        for (const video of videos) {
            if (video.srcObject && video.srcObject.active) {
                console.log('GlobalCameraManager: Found existing video stream');
                return video.srcObject;
            }
        }
        
        // Check our tracked video elements
        for (const video of this.videoElements) {
            if (video && video.srcObject && video.srcObject.active) {
                console.log('GlobalCameraManager: Found tracked video stream');
                return video.srcObject;
            }
        }
        
        return null;
    }
    
    attachToElement(videoElement, markAsProctoring = true) {
        if (!this.stream || !this.stream.active) {
            console.warn('GlobalCameraManager: No active stream to attach');
            return false;
        }
        
        console.log('GlobalCameraManager: Attaching stream to video element');
        videoElement.srcObject = this.stream;
        
        if (markAsProctoring) {
            videoElement.setAttribute('data-proctoring-active', 'true');
            videoElement.setAttribute('data-global-managed', 'true');
        }
        
        // Track this video element
        this.videoElements.add(videoElement);
        
        // Remove from tracking when element is removed
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.removedNodes.forEach((node) => {
                    if (node === videoElement) {
                        this.videoElements.delete(videoElement);
                        observer.disconnect();
                    }
                });
            });
        });
        
        if (videoElement.parentNode) {
            observer.observe(videoElement.parentNode, { childList: true });
        }
        
        return true;
    }
    
    createHiddenVideo() {
        console.log('GlobalCameraManager: Creating hidden video element');
        
        const video = document.createElement('video');
        video.id = 'global-camera-stream-' + Date.now();
        video.width = 320;
        video.height = 240;
        video.autoplay = true;
        video.playsInline = true;
        video.muted = true;
        // Fixed CSS with proper negative values
        video.style.cssText = 'position: fixed !important; top: -9999px !important; left: -9999px !important; width: 1px !important; height: 1px !important; z-index: -9999 !important; opacity: 0 !important; pointer-events: none !important;';
        video.setAttribute('data-global-camera', 'true');
        video.setAttribute('data-proctoring-active', 'true');
        
        document.body.appendChild(video);
        
        this.attachToElement(video, false);
        
        // Ensure video plays
        video.play().catch(e => {
            console.warn('GlobalCameraManager: Hidden video autoplay failed:', e);
        });
        
        return video;
    }
    
    saveState() {
        const state = {
            isActive: this.isActive,
            contestId: this.contestId,
            timestamp: Date.now(),
            streamActive: this.stream && this.stream.active
        };
        
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(state));
            sessionStorage.setItem(this.storageKey, JSON.stringify(state));
            console.log('GlobalCameraManager: State saved', state);
        } catch (e) {
            console.warn('GlobalCameraManager: Failed to save state:', e);
        }
    }
    
    restoreState() {
        try {
            // Try session storage first, then local storage
            let stateStr = sessionStorage.getItem(this.storageKey) || localStorage.getItem(this.storageKey);
            
            if (!stateStr) {
                console.log('GlobalCameraManager: No saved state found');
                return false;
            }
            
            const state = JSON.parse(stateStr);
            console.log('GlobalCameraManager: Restoring state', state);
            
            // Check if state is recent (within 5 minutes)
            const isRecent = state.timestamp && (Date.now() - state.timestamp) < 300000;
            
            if (state.isActive && isRecent) {
                this.isActive = state.isActive;
                this.contestId = state.contestId;
                
                // Try to find and adopt existing stream
                const existingStream = this.findExistingStream();
                if (existingStream) {
                    this.stream = existingStream;
                    console.log('GlobalCameraManager: State restored with existing stream');
                    return true;
                }
            }
            
            console.log('GlobalCameraManager: State expired or no stream found');
            return false;
        } catch (e) {
            console.warn('GlobalCameraManager: Failed to restore state:', e);
            return false;
        }
    }
    
    setupUnloadPrevention() {
        // Prevent stream destruction on page unload
        window.addEventListener('beforeunload', (e) => {
            if (this.isActive && this.stream) {
                console.log('GlobalCameraManager: Page unloading, preserving stream');
                
                // Create or update hidden video to maintain stream
                const existingHidden = document.querySelector('video[data-global-camera="true"]');
                if (!existingHidden) {
                    this.createHiddenVideo();
                }
                
                // Save state
                this.saveState();
                
                // Don't show confirmation dialog, just preserve state
                return undefined;
            }
        });
        
        // Handle visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                console.log('GlobalCameraManager: Page hidden, ensuring stream persistence');
                if (this.isActive && this.stream) {
                    this.saveState();
                    
                    // Ensure we have a hidden video element
                    const hiddenVideo = document.querySelector('video[data-global-camera="true"]');
                    if (!hiddenVideo) {
                        this.createHiddenVideo();
                    }
                }
            } else {
                console.log('GlobalCameraManager: Page visible, checking stream status');
                this.restoreState();
            }
        });
    }
    
    setupStatePersistence() {
        // Save state every 5 seconds
        setInterval(() => {
            if (this.isActive) {
                this.saveState();
            }
        }, 5000);
    }
    
    setupBeforeUnloadProtection() {
        // Override window.location changes to preserve stream
        const originalAssign = window.location.assign;
        const originalReplace = window.location.replace;
        
        window.location.assign = (url) => {
            this.prepareForNavigation();
            return originalAssign.call(window.location, url);
        };
        
        window.location.replace = (url) => {
            this.prepareForNavigation();
            return originalReplace.call(window.location, url);
        };
        
        // Override href setter
        let originalHref = window.location.href;
        Object.defineProperty(window.location, 'href', {
            get: () => originalHref,
            set: (url) => {
                this.prepareForNavigation();
                originalHref = url;
                window.location.assign(url);
            }
        });
    }
    
    prepareForNavigation() {
        if (this.isActive && this.stream) {
            console.log('GlobalCameraManager: Preparing for navigation');
            
            // Ensure hidden video exists
            let hiddenVideo = document.querySelector('video[data-global-camera="true"]');
            if (!hiddenVideo) {
                hiddenVideo = this.createHiddenVideo();
            }
            
            // Update state
            this.saveState();
            
            // Mark navigation time
            sessionStorage.setItem('camera_navigation_time', Date.now().toString());
        }
    }
    
    stop() {
        console.log('GlobalCameraManager: Stopping camera');
        
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        this.isActive = false;
        this.contestId = null;
        
        // Clean up hidden videos
        const hiddenVideos = document.querySelectorAll('video[data-global-camera="true"]');
        hiddenVideos.forEach(video => video.remove());
        
        // Clear state
        try {
            localStorage.removeItem(this.storageKey);
            sessionStorage.removeItem(this.storageKey);
        } catch (e) {
            console.warn('GlobalCameraManager: Failed to clear state:', e);
        }
        
        console.log('GlobalCameraManager: Camera stopped');
    }
    
    // Method to stop camera only on final submission
    stopForFinalSubmission() {
        console.log('GlobalCameraManager: Stopping camera for final submission');
        this.stop();
        
        // Also stop any active proctoring
        if (window.proctoring && window.proctoring.isMonitoringActive()) {
            window.proctoring.stop();
        }
        
        // Clear all camera-related session storage
        try {
            sessionStorage.removeItem('cameraVerified');
            sessionStorage.removeItem('cameraStreamActive');
            sessionStorage.removeItem('navigationTime');
            sessionStorage.removeItem('contestId');
        } catch (e) {
            console.warn('GlobalCameraManager: Failed to clear session storage:', e);
        }
        
        console.log('GlobalCameraManager: Final submission cleanup complete');
    }
    
    getStream() {
        return this.stream;
    }
    
    isStreamActive() {
        return this.isActive && this.stream && this.stream.active;
    }
    
    getStatus() {
        return {
            isActive: this.isActive,
            hasStream: !!this.stream,
            streamActive: this.stream && this.stream.active,
            contestId: this.contestId,
            videoElements: this.videoElements.size
        };
    }
    
    showErrorMessage(message) {
        // Create or update error message element
        let errorElement = document.getElementById('global-camera-error');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.id = 'global-camera-error';
            errorElement.style.cssText = `
                position: fixed;
                top: 60px;
                right: 20px;
                z-index: 10001;
                background: #dc3545;
                color: white;
                padding: 15px;
                border-radius: 5px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                font-size: 14px;
                max-width: 300px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            `;
            document.body.appendChild(errorElement);
        }
        
        errorElement.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <strong>Camera Error:</strong>
                    <p style="margin: 5px 0 0 0; font-size: 13px;">${message}</p>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" style="
                    background: none;
                    border: none;
                    color: white;
                    font-size: 18px;
                    cursor: pointer;
                    padding: 0;
                    margin-left: 10px;
                ">&times;</button>
            </div>
        `;
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            if (errorElement && errorElement.parentElement) {
                errorElement.remove();
            }
        }, 10000);
    }
}

// Initialize global camera manager
window.contestCameraManager = new GlobalCameraManager();

console.log('GlobalCameraManager: Loaded and initialized');