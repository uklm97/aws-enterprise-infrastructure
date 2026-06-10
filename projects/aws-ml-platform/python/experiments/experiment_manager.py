#!/usr/bin/env python3
"""
AWS ML Experiment Manager
Comprehensive experiment tracking, hyperparameter tuning, and model comparison
"""

import boto3
import json
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from botocore.exceptions import ClientError
import matplotlib.pyplot as plt
import seaborn as sns


class ExperimentManager:
    """Comprehensive ML experiment tracking and management"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.sagemaker_client = boto3.client('sagemaker', region_name=region)
        self.s3_client = boto3.client('s3', region_name=region)
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        
    def create_experiment(self, experiment_config: Dict[str, Any]) -> Optional[str]:
        """Create SageMaker experiment"""
        try:
            response = self.sagemaker_client.create_experiment(
                ExperimentName=experiment_config['ExperimentName'],
                DisplayName=experiment_config.get('DisplayName'),
                Description=experiment_config.get('Description', ''),
                Tags=experiment_config.get('Tags', [])
            )
            return response['ExperimentArn']
        except ClientError as e:
            print(f"Error creating experiment: {e}")
            return None
    
    def create_trial(self, trial_config: Dict[str, Any]) -> Optional[str]:
        """Create trial within experiment"""
        try:
            response = self.sagemaker_client.create_trial(
                TrialName=trial_config['TrialName'],
                ExperimentName=trial_config['ExperimentName'],
                DisplayName=trial_config.get('DisplayName'),
                Tags=trial_config.get('Tags', [])
            )
            return response['TrialArn']
        except ClientError as e:
            print(f"Error creating trial: {e}")
            return None
    
    def create_trial_component(self, component_config: Dict[str, Any]) -> Optional[str]:
        """Create trial component"""
        try:
            response = self.sagemaker_client.create_trial_component(
                TrialComponentName=component_config['TrialComponentName'],
                DisplayName=component_config.get('DisplayName'),
                Status=component_config.get('Status', {}),
                StartTime=component_config.get('StartTime'),
                EndTime=component_config.get('EndTime'),
                Parameters=component_config.get('Parameters', {}),
                InputArtifacts=component_config.get('InputArtifacts', {}),
                OutputArtifacts=component_config.get('OutputArtifacts', {}),
                MetadataProperties=component_config.get('MetadataProperties', {}),
                Tags=component_config.get('Tags', [])
            )
            return response['TrialComponentArn']
        except ClientError as e:
            print(f"Error creating trial component: {e}")
            return None
    
    def associate_trial_component(self, trial_name: str, trial_component_name: str) -> bool:
        """Associate trial component with trial"""
        try:
            self.sagemaker_client.associate_trial_component(
                TrialName=trial_name,
                TrialComponentName=trial_component_name
            )
            return True
        except ClientError as e:
            print(f"Error associating trial component: {e}")
            return False
    
    def create_hyperparameter_tuning_job(self, tuning_config: Dict[str, Any]) -> Optional[str]:
        """Create hyperparameter tuning job"""
        try:
            response = self.sagemaker_client.create_hyper_parameter_tuning_job(
                HyperParameterTuningJobName=tuning_config['HyperParameterTuningJobName'],
                HyperParameterTuningJobConfig=tuning_config['HyperParameterTuningJobConfig'],
                TrainingJobDefinition=tuning_config['TrainingJobDefinition'],
                TrainingJobDefinitions=tuning_config.get('TrainingJobDefinitions', []),
                WarmStartConfig=tuning_config.get('WarmStartConfig', {}),
                Tags=tuning_config.get('Tags', []),
                Autotune=tuning_config.get('Autotune', {})
            )
            return response['HyperParameterTuningJobArn']
        except ClientError as e:
            print(f"Error creating hyperparameter tuning job: {e}")
            return None
    
    def get_hyperparameter_tuning_job(self, job_name: str) -> Optional[Dict[str, Any]]:
        """Get hyperparameter tuning job details"""
        try:
            response = self.sagemaker_client.describe_hyper_parameter_tuning_job(
                HyperParameterTuningJobName=job_name
            )
            return response
        except ClientError as e:
            print(f"Error getting hyperparameter tuning job: {e}")
            return None
    
    def list_training_jobs_for_tuning(self, tuning_job_name: str) -> List[Dict[str, Any]]:
        """List training jobs for hyperparameter tuning job"""
        try:
            response = self.sagemaker_client.list_training_jobs_for_hyper_parameter_tuning_job(
                HyperParameterTuningJobName=tuning_job_name
            )
            return response['TrainingJobSummaries']
        except ClientError as e:
            print(f"Error listing training jobs for tuning: {e}")
            return []
    
    def get_best_training_job(self, tuning_job_name: str) -> Optional[Dict[str, Any]]:
        """Get best training job from hyperparameter tuning"""
        try:
            tuning_job = self.get_hyperparameter_tuning_job(tuning_job_name)
            if not tuning_job:
                return None
            
            best_training_job = tuning_job.get('BestTrainingJob', {})
            if best_training_job:
                return best_training_job
            
            # If no best training job, get the one with highest objective metric
            training_jobs = self.list_training_jobs_for_tuning(tuning_job_name)
            if not training_jobs:
                return None
            
            # Sort by final objective metric value
            objective_metric_name = tuning_job['HyperParameterTuningJobConfig']['HyperParameterTuningJobObjective']['MetricName']
            best_job = max(training_jobs, key=lambda x: x.get('FinalHyperParameterTuningJobObjectiveMetric', {}).get('Value', 0))
            
            return best_job
        except Exception as e:
            print(f"Error getting best training job: {e}")
            return None
    
    def create_experiment_tracking_dashboard(self, experiment_name: str) -> Dict[str, Any]:
        """Create experiment tracking dashboard"""
        try:
            # Get experiment details
            experiment = self.sagemaker_client.describe_experiment(
                ExperimentName=experiment_name
            )
            
            # Get trials
            trials_response = self.sagemaker_client.list_trials(
                ExperimentName=experiment_name
            )
            
            trials_data = []
            for trial in trials_response['TrialSummaries']:
                trial_details = self.sagemaker_client.describe_trial(
                    TrialName=trial['TrialName']
                )
                
                # Get trial components
                components_response = self.sagemaker_client.list_trial_components(
                    TrialName=trial['TrialName']
                )
                
                trial_data = {
                    'trial_name': trial['TrialName'],
                    'trial_arn': trial['TrialArn'],
                    'creation_time': trial['CreationTime'],
                    'last_modified_time': trial['LastModifiedTime'],
                    'components': components_response['TrialComponentSummaries']
                }
                trials_data.append(trial_data)
            
            return {
                'experiment': experiment,
                'trials': trials_data,
                'total_trials': len(trials_data),
                'created_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error creating experiment tracking dashboard: {e}")
            return {}
    
    def compare_experiments(self, experiment_names: List[str]) -> Dict[str, Any]:
        """Compare multiple experiments"""
        try:
            comparison_data = {
                'experiments': [],
                'comparison_metrics': [],
                'created_at': datetime.now().isoformat()
            }
            
            for exp_name in experiment_names:
                exp_data = self.create_experiment_tracking_dashboard(exp_name)
                comparison_data['experiments'].append(exp_data)
            
            # Extract common metrics for comparison
            all_metrics = set()
            for exp in comparison_data['experiments']:
                for trial in exp['trials']:
                    for component in trial['components']:
                        if 'Parameters' in component:
                            all_metrics.update(component['Parameters'].keys())
            
            comparison_data['comparison_metrics'] = list(all_metrics)
            
            return comparison_data
        except Exception as e:
            print(f"Error comparing experiments: {e}")
            return {}
    
    def create_hyperparameter_analysis(self, tuning_job_name: str) -> Dict[str, Any]:
        """Create hyperparameter analysis"""
        try:
            tuning_job = self.get_hyperparameter_tuning_job(tuning_job_name)
            if not tuning_job:
                return {}
            
            training_jobs = self.list_training_jobs_for_tuning(tuning_job_name)
            
            # Extract hyperparameters and metrics
            analysis_data = {
                'tuning_job_name': tuning_job_name,
                'total_training_jobs': len(training_jobs),
                'hyperparameters': {},
                'metrics': {},
                'best_job': None,
                'created_at': datetime.now().isoformat()
            }
            
            # Get objective metric name
            objective_metric = tuning_job['HyperParameterTuningJobConfig']['HyperParameterTuningJobObjective']['MetricName']
            
            # Analyze each training job
            for job in training_jobs:
                job_name = job['TrainingJobName']
                job_status = job['TrainingJobStatus']
                
                if job_status == 'Completed':
                    # Get hyperparameters
                    hyperparams = job.get('HyperParameters', {})
                    for param_name, param_value in hyperparams.items():
                        if param_name not in analysis_data['hyperparameters']:
                            analysis_data['hyperparameters'][param_name] = []
                        analysis_data['hyperparameters'][param_name].append(param_value)
                    
                    # Get final metric value
                    final_metric = job.get('FinalHyperParameterTuningJobObjectiveMetric', {})
                    if final_metric:
                        metric_value = final_metric.get('Value', 0)
                        if objective_metric not in analysis_data['metrics']:
                            analysis_data['metrics'][objective_metric] = []
                        analysis_data['metrics'][objective_metric].append(metric_value)
            
            # Find best job
            best_job = self.get_best_training_job(tuning_job_name)
            if best_job:
                analysis_data['best_job'] = {
                    'job_name': best_job['TrainingJobName'],
                    'hyperparameters': best_job.get('HyperParameters', {}),
                    'final_metric': best_job.get('FinalHyperParameterTuningJobObjectiveMetric', {})
                }
            
            return analysis_data
        except Exception as e:
            print(f"Error creating hyperparameter analysis: {e}")
            return {}
    
    def create_hyperparameter_visualization(self, tuning_job_name: str, 
                                          output_path: str = None) -> Dict[str, Any]:
        """Create hyperparameter visualization"""
        try:
            analysis = self.create_hyperparameter_analysis(tuning_job_name)
            if not analysis or not analysis['hyperparameters']:
                return {}
            
            # Create visualizations
            visualizations = {}
            
            # 1. Hyperparameter distribution
            for param_name, param_values in analysis['hyperparameters'].items():
                if param_values:
                    plt.figure(figsize=(10, 6))
                    
                    # Convert to numeric if possible
                    numeric_values = []
                    for val in param_values:
                        try:
                            numeric_values.append(float(val))
                        except (ValueError, TypeError):
                            break
                    
                    if numeric_values:
                        plt.hist(numeric_values, bins=20, alpha=0.7)
                        plt.title(f'Distribution of {param_name}')
                        plt.xlabel(param_name)
                        plt.ylabel('Frequency')
                        
                        if output_path:
                            plt.savefig(f"{output_path}/{param_name}_distribution.png")
                        visualizations[f'{param_name}_distribution'] = f"{param_name}_distribution.png"
                        plt.close()
            
            # 2. Hyperparameter vs Performance
            objective_metric = list(analysis['metrics'].keys())[0] if analysis['metrics'] else None
            if objective_metric and analysis['metrics'][objective_metric]:
                metric_values = analysis['metrics'][objective_metric]
                
                for param_name, param_values in analysis['hyperparameters'].items():
                    if len(param_values) == len(metric_values):
                        plt.figure(figsize=(10, 6))
                        
                        # Convert to numeric if possible
                        numeric_params = []
                        for val in param_values:
                            try:
                                numeric_params.append(float(val))
                            except (ValueError, TypeError):
                                break
                        
                        if numeric_params and len(numeric_params) == len(metric_values):
                            plt.scatter(numeric_params, metric_values, alpha=0.7)
                            plt.title(f'{param_name} vs {objective_metric}')
                            plt.xlabel(param_name)
                            plt.ylabel(objective_metric)
                            
                            if output_path:
                                plt.savefig(f"{output_path}/{param_name}_vs_{objective_metric}.png")
                            visualizations[f'{param_name}_vs_{objective_metric}'] = f"{param_name}_vs_{objective_metric}.png"
                            plt.close()
            
            return {
                'tuning_job_name': tuning_job_name,
                'visualizations': visualizations,
                'created_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error creating hyperparameter visualization: {e}")
            return {}
    
    def create_experiment_summary(self, experiment_name: str) -> Dict[str, Any]:
        """Create experiment summary"""
        try:
            dashboard = self.create_experiment_tracking_dashboard(experiment_name)
            if not dashboard:
                return {}
            
            summary = {
                'experiment_name': experiment_name,
                'total_trials': dashboard['total_trials'],
                'experiment_arn': dashboard['experiment']['ExperimentArn'],
                'creation_time': dashboard['experiment']['CreationTime'],
                'last_modified_time': dashboard['experiment']['LastModifiedTime'],
                'trial_summaries': [],
                'created_at': datetime.now().isoformat()
            }
            
            # Summarize each trial
            for trial in dashboard['trials']:
                trial_summary = {
                    'trial_name': trial['trial_name'],
                    'trial_arn': trial['trial_arn'],
                    'creation_time': trial['creation_time'],
                    'last_modified_time': trial['last_modified_time'],
                    'component_count': len(trial['components']),
                    'components': []
                }
                
                # Summarize components
                for component in trial['components']:
                    component_summary = {
                        'component_name': component['TrialComponentName'],
                        'component_arn': component['TrialComponentArn'],
                        'creation_time': component['CreationTime'],
                        'last_modified_time': component['LastModifiedTime']
                    }
                    trial_summary['components'].append(component_summary)
                
                summary['trial_summaries'].append(trial_summary)
            
            return summary
        except Exception as e:
            print(f"Error creating experiment summary: {e}")
            return {}
    
    def create_model_comparison_report(self, model_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create model comparison report"""
        try:
            comparison_report = {
                'models': [],
                'comparison_metrics': [],
                'recommendations': [],
                'created_at': datetime.now().isoformat()
            }
            
            # Analyze each model configuration
            for model_config in model_configs:
                model_analysis = {
                    'model_name': model_config.get('model_name', 'Unknown'),
                    'model_type': model_config.get('model_type', 'Unknown'),
                    'performance_metrics': model_config.get('performance_metrics', {}),
                    'hyperparameters': model_config.get('hyperparameters', {}),
                    'training_time': model_config.get('training_time', 0),
                    'inference_time': model_config.get('inference_time', 0),
                    'model_size': model_config.get('model_size', 0),
                    'accuracy': model_config.get('accuracy', 0),
                    'precision': model_config.get('precision', 0),
                    'recall': model_config.get('recall', 0),
                    'f1_score': model_config.get('f1_score', 0)
                }
                comparison_report['models'].append(model_analysis)
            
            # Extract common metrics
            all_metrics = set()
            for model in comparison_report['models']:
                all_metrics.update(model['performance_metrics'].keys())
                all_metrics.update(['accuracy', 'precision', 'recall', 'f1_score'])
            
            comparison_report['comparison_metrics'] = list(all_metrics)
            
            # Generate recommendations
            if comparison_report['models']:
                # Find best model by accuracy
                best_model = max(comparison_report['models'], key=lambda x: x['accuracy'])
                comparison_report['recommendations'].append({
                    'type': 'best_accuracy',
                    'model': best_model['model_name'],
                    'accuracy': best_model['accuracy'],
                    'reason': 'Highest accuracy among all models'
                })
                
                # Find fastest model
                fastest_model = min(comparison_report['models'], key=lambda x: x['inference_time'])
                comparison_report['recommendations'].append({
                    'type': 'fastest_inference',
                    'model': fastest_model['model_name'],
                    'inference_time': fastest_model['inference_time'],
                    'reason': 'Fastest inference time'
                })
                
                # Find smallest model
                smallest_model = min(comparison_report['models'], key=lambda x: x['model_size'])
                comparison_report['recommendations'].append({
                    'type': 'smallest_model',
                    'model': smallest_model['model_name'],
                    'model_size': smallest_model['model_size'],
                    'reason': 'Smallest model size'
                })
            
            return comparison_report
        except Exception as e:
            print(f"Error creating model comparison report: {e}")
            return {}
    
    def create_ab_testing_framework(self, ab_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create A/B testing framework for ML models"""
        try:
            ab_framework = {
                'name': ab_config['name'],
                'description': ab_config.get('description', ''),
                'models': ab_config.get('models', []),
                'traffic_allocation': ab_config.get('traffic_allocation', {}),
                'success_metrics': ab_config.get('success_metrics', []),
                'test_duration': ab_config.get('test_duration', 7),  # days
                'min_sample_size': ab_config.get('min_sample_size', 1000),
                'statistical_significance': ab_config.get('statistical_significance', 0.95),
                'created_at': datetime.now().isoformat()
            }
            
            # Add default success metrics if not provided
            if not ab_framework['success_metrics']:
                ab_framework['success_metrics'] = [
                    'accuracy',
                    'precision',
                    'recall',
                    'f1_score',
                    'inference_latency',
                    'throughput'
                ]
            
            # Add default traffic allocation if not provided
            if not ab_framework['traffic_allocation']:
                ab_framework['traffic_allocation'] = {
                    'model_a': 0.5,
                    'model_b': 0.5
                }
            
            return ab_framework
        except Exception as e:
            print(f"Error creating A/B testing framework: {e}")
            return {}
    
    def create_experiment_automation(self, automation_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create experiment automation workflow"""
        try:
            automation = {
                'name': automation_config['name'],
                'description': automation_config.get('description', ''),
                'triggers': automation_config.get('triggers', []),
                'actions': automation_config.get('actions', []),
                'conditions': automation_config.get('conditions', []),
                'created_at': datetime.now().isoformat()
            }
            
            # Add default automation triggers
            if not automation['triggers']:
                automation['triggers'] = [
                    {
                        'name': 'new_data_available',
                        'type': 's3_event',
                        'description': 'Trigger when new training data is available',
                        'configuration': {
                            'bucket': 'ml-training-data',
                            'prefix': 'new-data/',
                            'suffix': '.csv'
                        }
                    },
                    {
                        'name': 'model_performance_degraded',
                        'type': 'cloudwatch_alarm',
                        'description': 'Trigger when model performance drops',
                        'configuration': {
                            'alarm_name': 'model-performance-alarm',
                            'threshold': 0.8
                        }
                    },
                    {
                        'name': 'scheduled_experiment',
                        'type': 'schedule',
                        'description': 'Trigger scheduled experiments',
                        'configuration': {
                            'schedule_expression': 'cron(0 2 * * ? *)'  # Daily at 2 AM
                        }
                    }
                ]
            
            # Add default automation actions
            if not automation['actions']:
                automation['actions'] = [
                    {
                        'name': 'start_hyperparameter_tuning',
                        'type': 'sagemaker_tuning',
                        'description': 'Start hyperparameter tuning job',
                        'configuration': {
                            'tuning_job_name': 'auto-tuning-{timestamp}',
                            'max_jobs': 10,
                            'max_parallel_jobs': 2
                        }
                    },
                    {
                        'name': 'evaluate_models',
                        'type': 'sagemaker_processing',
                        'description': 'Evaluate model performance',
                        'configuration': {
                            'processing_job_name': 'model-evaluation-{timestamp}',
                            'role_arn': 'arn:aws:iam::account:role/SageMakerExecutionRole'
                        }
                    },
                    {
                        'name': 'deploy_best_model',
                        'type': 'sagemaker_deployment',
                        'description': 'Deploy best performing model',
                        'configuration': {
                            'endpoint_name': 'ml-endpoint',
                            'instance_type': 'ml.m5.large'
                        }
                    },
                    {
                        'name': 'send_experiment_notification',
                        'type': 'sns_notification',
                        'description': 'Send experiment results notification',
                        'configuration': {
                            'topic_arn': 'arn:aws:sns:region:account:ml-experiments',
                            'message': 'Experiment completed successfully'
                        }
                    }
                ]
            
            return automation
        except Exception as e:
            print(f"Error creating experiment automation: {e}")
            return {}
    
    def get_experiment_metrics(self, experiment_name: str) -> Dict[str, Any]:
        """Get experiment metrics from CloudWatch"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=7)
            
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/SageMaker',
                MetricName='TrainingJobStatus',
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum', 'Average']
            )
            
            return {
                'experiment_name': experiment_name,
                'metrics': response['Datapoints'],
                'period': {'start': start_time.isoformat(), 'end': end_time.isoformat()}
            }
        except Exception as e:
            print(f"Error getting experiment metrics: {e}")
            return {}


# Example usage and testing
if __name__ == "__main__":
    # Initialize experiment manager
    exp_manager = ExperimentManager()
    
    # Create experiment
    experiment_arn = exp_manager.create_experiment({
        'ExperimentName': 'ml-experiment-1',
        'DisplayName': 'ML Experiment 1',
        'Description': 'First ML experiment'
    })
    print(f"Created experiment: {experiment_arn}")
    
    # Create trial
    trial_arn = exp_manager.create_trial({
        'TrialName': 'trial-1',
        'ExperimentName': 'ml-experiment-1',
        'DisplayName': 'Trial 1'
    })
    print(f"Created trial: {trial_arn}")
    
    # Create experiment tracking dashboard
    dashboard = exp_manager.create_experiment_tracking_dashboard('ml-experiment-1')
    print(f"Created dashboard with {dashboard.get('total_trials', 0)} trials")
    
    # Create model comparison report
    model_configs = [
        {
            'model_name': 'Random Forest',
            'model_type': 'ensemble',
            'accuracy': 0.85,
            'precision': 0.82,
            'recall': 0.88,
            'f1_score': 0.85,
            'inference_time': 50,
            'model_size': 10
        },
        {
            'model_name': 'XGBoost',
            'model_type': 'gradient_boosting',
            'accuracy': 0.87,
            'precision': 0.85,
            'recall': 0.89,
            'f1_score': 0.87,
            'inference_time': 30,
            'model_size': 15
        }
    ]
    
    comparison_report = exp_manager.create_model_comparison_report(model_configs)
    print(f"Created comparison report with {len(comparison_report['models'])} models")
    
    # Create A/B testing framework
    ab_framework = exp_manager.create_ab_testing_framework({
        'name': 'model-ab-test',
        'description': 'A/B test for model comparison'
    })
    print(f"Created A/B testing framework: {ab_framework['name']}")
    
    # Create experiment automation
    automation = exp_manager.create_experiment_automation({
        'name': 'experiment-automation',
        'description': 'Automated experiment workflows'
    })
    print(f"Created experiment automation: {automation['name']}")
    
    # Get experiment metrics
    metrics = exp_manager.get_experiment_metrics('ml-experiment-1')
    print(f"Retrieved metrics for experiment")