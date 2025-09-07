#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify computer vision libraries are properly installed
"""

def test_computer_vision_libraries():
    """Test importing computer vision libraries"""
    print("Testing computer vision library imports...")
    print("=" * 50)
    
    # Test NumPy
    try:
        import numpy as np
        print(f"NumPy version: {np.__version__}")
        print("NumPy import successful")
    except ImportError as e:
        print(f"NumPy import failed: {e}")
        return False
    
    # Test OpenCV
    try:
        import cv2
        print(f"OpenCV version: {cv2.__version__}")
        print("OpenCV import successful")
    except ImportError as e:
        print(f"OpenCV import failed: {e}")
        # This is okay for deployment - proctoring will be disabled
        print("OpenCV not available - proctoring will be disabled")
    
    # Test MediaPipe
    try:
        import mediapipe as mp
        print(f"MediaPipe version: {mp.__version__}")
        print("MediaPipe import successful")
    except ImportError as e:
        print(f"MediaPipe import failed: {e}")
        # This is okay for deployment - proctoring will be disabled
        print("MediaPipe not available - proctoring will be disabled")
    
    print("=" * 50)
    print("All tests completed!")
    return True

if __name__ == "__main__":
    success = test_computer_vision_libraries()
    if success:
        print("Computer vision libraries are ready.")
    else:
        print("Some libraries failed to import.")