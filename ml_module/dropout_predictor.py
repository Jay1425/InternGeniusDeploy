"""
Dropout Prediction System for InternGenius

This module implements machine learning models to predict student dropout risk
based on academic performance, attendance, financial status, and behavioral patterns.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import logging
from datetime import datetime
import os

class DropoutPredictor:
    """
    Machine Learning model for predicting student dropout risk.
    
    Features considered:
    - Attendance percentage
    - Grade trends (improving/declining/stable)
    - Assessment scores
    - Fee payment status
    - Number of subject attempts/backlogs
    - Behavioral indicators (library usage, participation)
    """
    
    def __init__(self, model_path='models/'):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        self.model_version = "1.0.0"
        self.last_trained = None
        
        # Ensure model directory exists
        os.makedirs(model_path, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Try to load existing model
        self.load_model()
    
    def prepare_features(self, student_data):
        """
        Prepare features from raw student data for prediction.
        
        Args:
            student_data (dict): Student academic and behavioral data
            
        Returns:
            np.array: Processed features ready for prediction
        """
        features = {}
        
        # Attendance features
        attendance = student_data.get('attendance', {})
        features['attendance_percentage'] = attendance.get('percentage', 0)
        
        # Grade features
        grades = student_data.get('grades', {})
        features['current_cgpa'] = grades.get('cgpa', 0)
        features['grade_trend'] = self._encode_grade_trend(grades.get('trend', 'stable'))
        
        # Assessment features
        assessments = student_data.get('assessments', {})
        recent_scores = assessments.get('recent_scores', [])
        features['avg_recent_score'] = np.mean(recent_scores) if recent_scores else 0
        features['assignment_completion_rate'] = assessments.get('assignment_submissions', 0)
        
        # Financial features
        financial = student_data.get('financial', {})
        features['fee_status'] = self._encode_fee_status(financial.get('fee_status', 'paid'))
        features['outstanding_amount'] = financial.get('outstanding_amount', 0)
        
        # Academic history features
        academic_history = student_data.get('academic_history', {})
        features['total_backlogs'] = academic_history.get('backlogs', 0)
        features['course_changes'] = academic_history.get('course_changes', 0)
        
        # Calculate total subject attempts
        subject_attempts = academic_history.get('subject_attempts', {})
        features['total_subject_attempts'] = sum(subject_attempts.values()) if subject_attempts else 0
        
        # Behavioral features
        behavioral = student_data.get('behavioral', {})
        features['library_usage_hours'] = behavioral.get('library_usage', 0)
        features['extracurricular_count'] = len(behavioral.get('extracurricular_participation', []))
        features['counseling_sessions'] = behavioral.get('counseling_sessions', 0)
        
        # Convert to DataFrame for consistent processing
        df = pd.DataFrame([features])
        
        # Store feature names if not already stored
        if not self.feature_names:
            self.feature_names = df.columns.tolist()
        
        return df.values
    
    def _encode_grade_trend(self, trend):
        """Encode grade trend as numerical value."""
        trend_mapping = {'declining': 0, 'stable': 1, 'improving': 2}
        return trend_mapping.get(trend.lower(), 1)
    
    def _encode_fee_status(self, status):
        """Encode fee payment status as numerical value."""
        status_mapping = {'overdue': 0, 'pending': 1, 'paid': 2}
        return status_mapping.get(status.lower(), 2)
    
    def train(self, training_data):
        """
        Train the dropout prediction model.
        
        Args:
            training_data (list): List of student records with features and labels
            
        Returns:
            dict: Training results and metrics
        """
        try:
            # Prepare training data
            X_data = []
            y_data = []
            
            for record in training_data:
                features = self.prepare_features(record)
                X_data.append(features[0])
                
                # Determine dropout risk based on risk indicators
                risk_level = record.get('risk_indicators', {}).get('calculated_risk', 'low')
                y_data.append(self._encode_risk_level(risk_level))
            
            X = np.array(X_data)
            y = np.array(y_data)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train ensemble of models
            models = {
                'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
                'logistic_regression': LogisticRegression(random_state=42)
            }
            
            best_model = None
            best_score = 0
            model_results = {}
            
            for name, model in models.items():
                # Train model
                model.fit(X_train_scaled, y_train)
                
                # Evaluate model
                train_score = model.score(X_train_scaled, y_train)
                test_score = model.score(X_test_scaled, y_test)
                cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
                
                model_results[name] = {
                    'train_score': train_score,
                    'test_score': test_score,
                    'cv_mean': cv_scores.mean(),
                    'cv_std': cv_scores.std()
                }
                
                # Select best model based on cross-validation score
                if cv_scores.mean() > best_score:
                    best_score = cv_scores.mean()
                    best_model = model
            
            # Set the best model
            self.model = best_model
            self.last_trained = datetime.now()
            
            # Save model
            self.save_model()
            
            # Generate detailed metrics for the best model
            y_pred = best_model.predict(X_test_scaled)
            y_pred_proba = best_model.predict_proba(X_test_scaled)
            
            results = {
                'status': 'success',
                'model_type': type(best_model).__name__,
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'accuracy': best_model.score(X_test_scaled, y_test),
                'roc_auc': roc_auc_score(y_test, y_pred_proba, multi_class='ovr'),
                'classification_report': classification_report(y_test, y_pred),
                'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
                'model_comparison': model_results,
                'trained_at': self.last_trained.isoformat()
            }
            
            self.logger.info(f"Model training completed successfully. Accuracy: {results['accuracy']:.3f}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error during model training: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def predict(self, student_features):
        """
        Predict dropout risk for a student.
        
        Args:
            student_features (np.array): Processed student features
            
        Returns:
            dict: Prediction results with risk level and probability
        """
        if self.model is None:
            return {
                'error': 'Model not trained. Please train the model first.',
                'risk_level': 'unknown',
                'confidence': 0.0
            }
        
        try:
            # Scale features
            features_scaled = self.scaler.transform(student_features)
            
            # Get prediction and probabilities
            prediction = self.model.predict(features_scaled)[0]
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            # Convert prediction to risk level
            risk_levels = ['low', 'medium', 'high']
            risk_level = risk_levels[prediction]
            confidence = probabilities[prediction]
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(student_features[0])
            
            return {
                'risk_level': risk_level,
                'confidence': float(confidence),
                'probabilities': {
                    'low': float(probabilities[0]),
                    'medium': float(probabilities[1]),
                    'high': float(probabilities[2])
                },
                'risk_factors': risk_factors,
                'recommendations': self._generate_recommendations(risk_level, risk_factors)
            }
            
        except Exception as e:
            self.logger.error(f"Error during prediction: {str(e)}")
            return {
                'error': str(e),
                'risk_level': 'unknown',
                'confidence': 0.0
            }
    
    def _encode_risk_level(self, risk_level):
        """Encode risk level to numerical value."""
        level_mapping = {'low': 0, 'medium': 1, 'high': 2}
        return level_mapping.get(risk_level.lower(), 0)
    
    def _identify_risk_factors(self, features):
        """
        Identify specific risk factors based on feature values.
        
        Args:
            features (np.array): Student feature vector
            
        Returns:
            list: List of identified risk factors
        """
        risk_factors = []
        
        if len(features) >= len(self.feature_names):
            feature_dict = dict(zip(self.feature_names, features))
            
            # Check attendance
            if feature_dict.get('attendance_percentage', 100) < 60:
                risk_factors.append('Low attendance (< 60%)')
            
            # Check CGPA
            if feature_dict.get('current_cgpa', 10) < 6:
                risk_factors.append('Low CGPA (< 6.0)')
            
            # Check grade trend
            if feature_dict.get('grade_trend', 1) == 0:  # declining
                risk_factors.append('Declining grade trend')
            
            # Check backlogs
            if feature_dict.get('total_backlogs', 0) > 3:
                risk_factors.append('Multiple backlogs (> 3)')
            
            # Check fee status
            if feature_dict.get('fee_status', 2) == 0:  # overdue
                risk_factors.append('Overdue fee payments')
            
            # Check assignment completion
            if feature_dict.get('assignment_completion_rate', 100) < 50:
                risk_factors.append('Low assignment completion (< 50%)')
        
        return risk_factors
    
    def _generate_recommendations(self, risk_level, risk_factors):
        """
        Generate recommendations based on risk level and factors.
        
        Args:
            risk_level (str): Predicted risk level
            risk_factors (list): Identified risk factors
            
        Returns:
            list: List of recommendations
        """
        recommendations = []
        
        if risk_level == 'high':
            recommendations.append('Immediate counseling session required')
            recommendations.append('Contact parents/guardians')
            recommendations.append('Consider academic support programs')
        elif risk_level == 'medium':
            recommendations.append('Schedule mentoring session')
            recommendations.append('Monitor progress closely')
        
        # Specific recommendations based on risk factors
        for factor in risk_factors:
            if 'attendance' in factor.lower():
                recommendations.append('Improve class attendance')
            elif 'cgpa' in factor.lower() or 'grade' in factor.lower():
                recommendations.append('Academic tutoring recommended')
            elif 'backlogs' in factor.lower():
                recommendations.append('Focus on clearing backlogs')
            elif 'fee' in factor.lower():
                recommendations.append('Resolve fee payment issues')
            elif 'assignment' in factor.lower():
                recommendations.append('Improve assignment submission rate')
        
        return list(set(recommendations))  # Remove duplicates
    
    def save_model(self):
        """Save the trained model and preprocessing objects."""
        if self.model is not None:
            model_file = os.path.join(self.model_path, 'dropout_predictor.pkl')
            scaler_file = os.path.join(self.model_path, 'dropout_scaler.pkl')
            
            joblib.dump(self.model, model_file)
            joblib.dump(self.scaler, scaler_file)
            joblib.dump(self.feature_names, os.path.join(self.model_path, 'feature_names.pkl'))
            
            self.logger.info(f"Model saved to {model_file}")
    
    def load_model(self):
        """Load a previously trained model."""
        try:
            model_file = os.path.join(self.model_path, 'dropout_predictor.pkl')
            scaler_file = os.path.join(self.model_path, 'dropout_scaler.pkl')
            features_file = os.path.join(self.model_path, 'feature_names.pkl')
            
            if os.path.exists(model_file) and os.path.exists(scaler_file):
                self.model = joblib.load(model_file)
                self.scaler = joblib.load(scaler_file)
                
                if os.path.exists(features_file):
                    self.feature_names = joblib.load(features_file)
                
                self.logger.info("Model loaded successfully")
                return True
                
        except Exception as e:
            self.logger.warning(f"Could not load existing model: {str(e)}")
            
        return False
    
    def get_model_metrics(self):
        """Get current model performance metrics."""
        if self.model is None:
            return {'status': 'no_model', 'message': 'No trained model available'}
        
        return {
            'model_type': type(self.model).__name__,
            'model_version': self.model_version,
            'last_trained': self.last_trained.isoformat() if self.last_trained else None,
            'feature_count': len(self.feature_names),
            'feature_names': self.feature_names
        }
    
    def get_feature_importance(self):
        """Get feature importance scores if available."""
        if self.model is None or not hasattr(self.model, 'feature_importances_'):
            return None
        
        importance_dict = {}
        for i, importance in enumerate(self.model.feature_importances_):
            if i < len(self.feature_names):
                importance_dict[self.feature_names[i]] = float(importance)
        
        # Sort by importance
        sorted_importance = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        return sorted_importance
