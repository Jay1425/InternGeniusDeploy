"""
ML Module for InternGenius

This module contains all machine learning functionality including:
1. Drop-out Prediction System
2. Internship Recommendation Engine  
3. Risk Assessment Algorithms
4. Data Processing Pipelines

Separate from the main Flask application for better modularity.
"""

import os
import sys

# Add the parent directory to the path so we can import from the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .dropout_predictor import DropoutPredictor
from .recommendation_engine import RecommendationEngine
from .risk_assessor import RiskAssessor
from .data_processor import DataProcessor

__all__ = ['DropoutPredictor', 'RecommendationEngine', 'RiskAssessor', 'DataProcessor']

# Version info
__version__ = '1.0.0'
__author__ = 'InternGenius ML Team'
