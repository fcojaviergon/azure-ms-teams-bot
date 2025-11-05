#!/usr/bin/env python
"""Convenience script to run the bot."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.api.app import main

if __name__ == "__main__":
    main()
