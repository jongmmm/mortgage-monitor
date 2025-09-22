#!/usr/bin/env python3
"""
Mortgage Monitor Dashboard - Main Entry Point

This script provides a simple entry point that uses the refactored architecture.
For development and testing, you can still run this directly.
For production, consider using the app module directly.
"""

import sys
import os

# Add src to Python path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mortgage_monitor.app import main

if __name__ == "__main__":
    main()
