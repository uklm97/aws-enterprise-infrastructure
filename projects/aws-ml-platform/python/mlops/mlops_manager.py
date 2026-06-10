#!/usr/bin/env python3
"""
AWS MLOps Manager
Comprehensive MLOps management with CI/CD, model versioning, monitoring, and deployment automation
"""

import boto3
import json
import time
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from botocore.exceptions import ClientError
import pandas as pd
import git


class MLOpsManager:
    """Comprehensive MLOps management and automation"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.sagemaker_client = boto3.client('sagemaker', region_name=region)
        self.codebuild_client = boto3.client('codebuild', region_name=region)
        self.codepipeline_client = boto3.client('codepipeline', region_name=region)
        self.codedeploy_client = boto3.client('codedeploy', region_name=region)
        self.ecr_client = boto3.client('ecr', region_name=region)
        self.s3_client = boto3.client('s3', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=region)
        self.eventbridge_client = boto3.client('events', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        
    def create_ml_pipeline(self, pipeline_config: Dict[str, Any]) -> Optional[str]:
        """Create SageMaker ML pipeline"""
        try:
            response = self.sagemaker_client.create_pipeline(
                PipelineName=pipeline_config['PipelineName'],
                PipelineDisplayName=pipeline_config.get('PipelineDisplayName'),
                PipelineDefinition=pipeline_config['PipelineDefinition'],
                PipelineDescription=pipeline_config.get('PipelineDescription', ''),
                ClientRequestToken=pipeline_config.get('ClientRequestToken'),
                Tags=pipeline_config.get('Tags', [])
            )
            return response['PipelineArn']
        except ClientError as e:
            print(f"Error creating ML pipeline: {e}")
            return None
    
    def create_codebuild_project(self, project_config: Dict[str, Any]) -> Optional[str]:
        """Create CodeBuild project for ML CI/CD"""
        try:
            response = self.codebuild_client.create_project(
                name=project_config['name'],
                description=project_config.get('description', ''),
                source=project_config['source'],
                artifacts=project_config['artifacts'],
                environment=project_config['environment'],
                serviceRole=project_config['serviceRole'],
                timeoutInMinutes=project_config.get('timeoutInMinutes', 60),
                queuedTimeoutInMinutes=project_config.get('queuedTimeoutInMinutes', 480),
                cache=project_config.get('cache', {}),
                tags=project_config.get('tags', []),
                vpcConfig=project_config.get('vpcConfig', {}),
                badgeEnabled=project_config.get('badgeEnabled', False),
                logsConfig=project_config.get('logsConfig', {}),
                fileSystemLocations=project_config.get('fileSystemLocations', []),
                buildBatchConfig=project_config.get('buildBatchConfig', {})
            )
            return response['project']['arn']
        except ClientError as e:
            print(f"Error creating CodeBuild project: {e}")
            return None
    
    def create_codepipeline(self, pipeline_config: Dict[str, Any]) -> Optional[str]:
        """Create CodePipeline for ML CI/CD"""
        try:
            response = self.codepipeline_client.create_pipeline(
                pipeline=pipeline_config
            )
            return response['pipeline']['arn']
        except ClientError as e:
            print(f"Error creating CodePipeline: {e}")
            return None
    
    def create_model_registry(self, registry_config: Dict[str, Any]) -> Optional[str]:
        """Create model registry/package group"""
        try:
            response = self.sagemaker_client.create_model_package_group(
                ModelPackageGroupName=registry_config['ModelPackageGroupName'],
                ModelPackageGroupDescription=registry_config.get('ModelPackageGroupDescription', ''),
                Tags=registry_config.get('Tags', [])
            )
            return response['ModelPackageGroupArn']
        except ClientError as e:
            print(f"Error creating model registry: {e}")
            return None
    
    def register_model(self, model_config: Dict[str, Any]) -> Optional[str]:
        """Register model in model registry"""
        try:
            response = self.sagemaker_client.create_model_package(
                ModelPackageName=model_config.get('ModelPackageName'),
                ModelPackageGroupName=model_config.get('ModelPackageGroupName'),
                ModelPackageDescription=model_config.get('ModelPackageDescription', ''),
                InferenceSpecification=model_config.get('InferenceSpecification', {}),
                ValidationSpecification=model_config.get('ValidationSpecification', {}),
                SourceAlgorithmSpecification=model_config.get('SourceAlgorithmSpecification', {}),
                CertifyForMarketplace=model_config.get('CertifyForMarketplace', False),
                ModelApprovalStatus=model_config.get('ModelApprovalStatus', 'PendingManualApproval'),
                MetadataProperties=model_config.get('MetadataProperties', {}),
                ModelMetrics=model_config.get('ModelMetrics', {}),
                ClientToken=model_config.get('ClientToken'),
                CustomerMetadataProperties=model_config.get('CustomerMetadataProperties', {}),
                DriftCheckBaselines=model_config.get('DriftCheckBaselines', {}),
                Domain=model_config.get('Domain'),
                Task=model_config.get('Task'),
                SamplePayloadUrl=model_config.get('SamplePayloadUrl'),
                Tags=model_config.get('Tags', [])
            )
            return response['ModelPackageArn']
        except ClientError as e:
            print(f"Error registering model: {e}")
            return None
    
    def create_model_monitoring_schedule(self, monitoring_config: Dict[str, Any]) -> Optional[str]:
        """Create model monitoring schedule"""
        try:
            response = self.sagemaker_client.create_monitoring_schedule(
                MonitoringScheduleName=monitoring_config['MonitoringScheduleName'],
                MonitoringScheduleConfig=monitoring_config['MonitoringScheduleConfig'],
                Tags=monitoring_config.get('Tags', [])
            )
            return response['MonitoringScheduleArn']
        except ClientError as e:
            print(f"Error creating monitoring schedule: {e}")
            return None
    
    def create_data_quality_job_definition(self, job_definition: Dict[str, Any]) -> Optional[str]:
        """Create data quality monitoring job definition"""
        try:
            response = self.sagemaker_client.create_data_quality_job_definition(
                JobDefinitionName=job_definition['JobDefinitionName'],
                DataQualityBaselineConfig=job_definition.get('DataQualityBaselineConfig', {}),
                DataQualityAppSpecification=job_definition['DataQualityAppSpecification'],
                DataQualityJobInput=job_definition['DataQualityJobInput'],
                DataQualityJobOutputConfig=job_definition['DataQualityJobOutputConfig'],
                JobResources=job_definition['JobResources'],
                NetworkConfig=job_definition.get('NetworkConfig', {}),
                RoleArn=job_definition['RoleArn'],
                StoppingCondition=job_definition.get('StoppingCondition', {}),
                Tags=job_definition.get('Tags', [])
            )
            return response['JobDefinitionArn']
        except ClientError as e:
            print(f"Error creating data quality job definition: {e}")
            return None
    
    def create_model_quality_job_definition(self, job_definition: Dict[str, Any]) -> Optional[str]:
        """Create model quality monitoring job definition"""
        try:
            response = self.sagemaker_client.create_model_quality_job_definition(
                JobDefinitionName=job_definition['JobDefinitionName'],
                ModelQualityBaselineConfig=job_definition.get('ModelQualityBaselineConfig', {}),
                ModelQualityAppSpecification=job_definition['ModelQualityAppSpecification'],
                ModelQualityJobInput=job_definition['ModelQualityJobInput'],
                ModelQualityJobOutputConfig=job_definition['ModelQualityJobOutputConfig'],
                JobResources=job_definition['JobResources'],
                NetworkConfig=job_definition.get('NetworkConfig', {}),
                RoleArn=job_definition['RoleArn'],
                StoppingCondition=job_definition.get('StoppingCondition', {}),
                Tags=job_definition.get('Tags', [])
            )
            return response['JobDefinitionArn']
        except ClientError as e:
            print(f"Error creating model quality job definition: {e}")
            return None
    
    def create_bias_job_definition(self, job_definition: Dict[str, Any]) -> Optional[str]:
        """Create bias monitoring job definition"""
        try:
            response = self.sagemaker_client.create_model_bias_job_definition(
                JobDefinitionName=job_definition['JobDefinitionName'],
                ModelBiasBaselineConfig=job_definition.get('ModelBiasBaselineConfig', {}),
                ModelBiasAppSpecification=job_definition['ModelBiasAppSpecification'],
                ModelBiasJobInput=job_definition['ModelBiasJobInput'],
                ModelBiasJobOutputConfig=job_definition['ModelBiasJobOutputConfig'],
                JobResources=job_definition['JobResources'],
                NetworkConfig=job_definition.get('NetworkConfig', {}),
                RoleArn=job_definition['RoleArn'],
                StoppingCondition=job_definition.get('StoppingCondition', {}),
                Tags=job_definition.get('Tags', [])
            )
            return response['JobDefinitionArn']
        except ClientError as e:
            print(f"Error creating bias job definition: {e}")
            return None
    
    def create_explainability_job_definition(self, job_definition: Dict[str, Any]) -> Optional[str]:
        """Create explainability monitoring job definition"""
        try:
            response = self.sagemaker_client.create_model_explainability_job_definition(
                JobDefinitionName=job_definition['JobDefinitionName'],
                ModelExplainabilityBaselineConfig=job_definition.get('ModelExplainabilityBaselineConfig', {}),
                ModelExplainabilityAppSpecification=job_definition['ModelExplainabilityAppSpecification'],
                ModelExplainabilityJobInput=job_definition['ModelExplainabilityJobInput'],
                ModelExplainabilityJobOutputConfig=job_definition['ModelExplainabilityJobOutputConfig'],
                JobResources=job_definition['JobResources'],
                NetworkConfig=job_definition.get('NetworkConfig', {}),
                RoleArn=job_definition['RoleArn'],
                StoppingCondition=job_definition.get('StoppingCondition', {}),
                Tags=job_definition.get('Tags', [])
            )
            return response['JobDefinitionArn']
        except ClientError as e:
            print(f"Error creating explainability job definition: {e}")
            return None
    
    def create_experiment_tracking(self, experiment_config: Dict[str, Any]) -> Optional[str]:
        """Create experiment tracking setup"""
        try:
            # Create experiment
            experiment_response = self.sagemaker_client.create_experiment(
                ExperimentName=experiment_config['ExperimentName'],
                DisplayName=experiment_config.get('DisplayName'),
                Description=experiment_config.get('Description', ''),
                Tags=experiment_config.get('Tags', [])
            )
            
            experiment_arn = experiment_response['ExperimentArn']
            
            # Create trial if specified
            if 'TrialName' in experiment_config:
                trial_response = self.sagemaker_client.create_trial(
                    TrialName=experiment_config['TrialName'],
                    ExperimentName=experiment_config['ExperimentName'],
                    DisplayName=experiment_config.get('TrialDisplayName'),
                    Tags=experiment_config.get('TrialTags', [])
                )
                return {
                    'experiment_arn': experiment_arn,
                    'trial_arn': trial_response['TrialArn']
                }
            
            return {'experiment_arn': experiment_arn}
        except ClientError as e:
            print(f"Error creating experiment tracking: {e}")
            return None
    
    def create_ml_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create ML workflow configuration"""
        try:
            workflow = {
                'name': workflow_config['name'],
                'description': workflow_config.get('description', ''),
                'stages': workflow_config.get('stages', []),
                'triggers': workflow_config.get('triggers', []),
                'notifications': workflow_config.get('notifications', []),
                'created_at': datetime.now().isoformat()
            }
            
            # Add default ML workflow stages if not provided
            if not workflow['stages']:
                workflow['stages'] = [
                    {
                        'name': 'data_ingestion',
                        'type': 'processing',
                        'description': 'Ingest and validate data',
                        'dependencies': []
                    },
                    {
                        'name': 'data_preprocessing',
                        'type': 'processing',
                        'description': 'Clean and preprocess data',
                        'dependencies': ['data_ingestion']
                    },
                    {
                        'name': 'feature_engineering',
                        'type': 'processing',
                        'description': 'Create and select features',
                        'dependencies': ['data_preprocessing']
                    },
                    {
                        'name': 'model_training',
                        'type': 'training',
                        'description': 'Train ML model',
                        'dependencies': ['feature_engineering']
                    },
                    {
                        'name': 'model_evaluation',
                        'type': 'processing',
                        'description': 'Evaluate model performance',
                        'dependencies': ['model_training']
                    },
                    {
                        'name': 'model_validation',
                        'type': 'validation',
                        'description': 'Validate model quality',
                        'dependencies': ['model_evaluation']
                    },
                    {
                        'name': 'model_registration',
                        'type': 'registration',
                        'description': 'Register model in registry',
                        'dependencies': ['model_validation']
                    },
                    {
                        'name': 'model_deployment',
                        'type': 'deployment',
                        'description': 'Deploy model to endpoint',
                        'dependencies': ['model_registration']
                    },
                    {
                        'name': 'model_monitoring',
                        'type': 'monitoring',
                        'description': 'Monitor model performance',
                        'dependencies': ['model_deployment']
                    }
                ]
            
            return workflow
        except Exception as e:
            print(f"Error creating ML workflow: {e}")
            return {}
    
    def create_ci_cd_pipeline(self, pipeline_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create CI/CD pipeline for ML"""
        try:
            pipeline = {
                'name': pipeline_config['name'],
                'description': pipeline_config.get('description', ''),
                'stages': [],
                'triggers': pipeline_config.get('triggers', []),
                'notifications': pipeline_config.get('notifications', []),
                'created_at': datetime.now().isoformat()
            }
            
            # Add CI/CD stages
            pipeline['stages'] = [
                {
                    'name': 'source',
                    'type': 'source',
                    'description': 'Source code checkout',
                    'provider': pipeline_config.get('source_provider', 'GitHub'),
                    'configuration': pipeline_config.get('source_config', {})
                },
                {
                    'name': 'build',
                    'type': 'build',
                    'description': 'Build and test code',
                    'provider': 'CodeBuild',
                    'configuration': pipeline_config.get('build_config', {})
                },
                {
                    'name': 'data_validation',
                    'type': 'validation',
                    'description': 'Validate data quality',
                    'provider': 'SageMaker',
                    'configuration': pipeline_config.get('data_validation_config', {})
                },
                {
                    'name': 'model_training',
                    'type': 'training',
                    'description': 'Train ML model',
                    'provider': 'SageMaker',
                    'configuration': pipeline_config.get('training_config', {})
                },
                {
                    'name': 'model_evaluation',
                    'type': 'evaluation',
                    'description': 'Evaluate model performance',
                    'provider': 'SageMaker',
                    'configuration': pipeline_config.get('evaluation_config', {})
                },
                {
                    'name': 'model_approval',
                    'type': 'approval',
                    'description': 'Manual model approval',
                    'provider': 'Manual',
                    'configuration': pipeline_config.get('approval_config', {})
                },
                {
                    'name': 'model_deployment',
                    'type': 'deployment',
                    'description': 'Deploy model to endpoint',
                    'provider': 'SageMaker',
                    'configuration': pipeline_config.get('deployment_config', {})
                },
                {
                    'name': 'post_deployment_testing',
                    'type': 'testing',
                    'description': 'Test deployed model',
                    'provider': 'Lambda',
                    'configuration': pipeline_config.get('testing_config', {})
                }
            ]
            
            return pipeline
        except Exception as e:
            print(f"Error creating CI/CD pipeline: {e}")
            return {}
    
    def create_model_versioning_system(self, versioning_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create model versioning system"""
        try:
            versioning_system = {
                'name': versioning_config['name'],
                'description': versioning_config.get('description', ''),
                'versioning_strategy': versioning_config.get('versioning_strategy', 'semantic'),
                'retention_policy': versioning_config.get('retention_policy', {}),
                'approval_workflow': versioning_config.get('approval_workflow', {}),
                'created_at': datetime.now().isoformat()
            }
            
            # Add default versioning strategy
            if versioning_system['versioning_strategy'] == 'semantic':
                versioning_system['versioning_rules'] = {
                    'major': 'Breaking changes or significant model architecture changes',
                    'minor': 'New features or improvements with backward compatibility',
                    'patch': 'Bug fixes or minor improvements'
                }
            
            # Add default retention policy
            if not versioning_system['retention_policy']:
                versioning_system['retention_policy'] = {
                    'keep_latest': 10,
                    'keep_stable': 5,
                    'keep_failed': 3,
                    'cleanup_after_days': 90
                }
            
            return versioning_system
        except Exception as e:
            print(f"Error creating model versioning system: {e}")
            return {}
    
    def create_ml_monitoring_dashboard(self, monitoring_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create ML monitoring dashboard"""
        try:
            dashboard = {
                'name': monitoring_config['name'],
                'description': monitoring_config.get('description', ''),
                'metrics': monitoring_config.get('metrics', []),
                'alerts': monitoring_config.get('alerts', []),
                'created_at': datetime.now().isoformat()
            }
            
            # Add default monitoring metrics
            if not dashboard['metrics']:
                dashboard['metrics'] = [
                    {
                        'name': 'model_accuracy',
                        'type': 'performance',
                        'description': 'Model accuracy over time',
                        'threshold': 0.8,
                        'alert_enabled': True
                    },
                    {
                        'name': 'prediction_latency',
                        'type': 'performance',
                        'description': 'Prediction latency in milliseconds',
                        'threshold': 1000,
                        'alert_enabled': True
                    },
                    {
                        'name': 'data_drift',
                        'type': 'data_quality',
                        'description': 'Data drift detection',
                        'threshold': 0.1,
                        'alert_enabled': True
                    },
                    {
                        'name': 'model_bias',
                        'type': 'fairness',
                        'description': 'Model bias detection',
                        'threshold': 0.05,
                        'alert_enabled': True
                    },
                    {
                        'name': 'endpoint_health',
                        'type': 'infrastructure',
                        'description': 'Endpoint health status',
                        'threshold': 0.95,
                        'alert_enabled': True
                    }
                ]
            
            # Add default alerts
            if not dashboard['alerts']:
                dashboard['alerts'] = [
                    {
                        'name': 'accuracy_drop',
                        'description': 'Model accuracy drops below threshold',
                        'condition': 'model_accuracy < 0.8',
                        'severity': 'high',
                        'notification_channels': ['email', 'slack']
                    },
                    {
                        'name': 'high_latency',
                        'description': 'Prediction latency exceeds threshold',
                        'condition': 'prediction_latency > 1000',
                        'severity': 'medium',
                        'notification_channels': ['email']
                    },
                    {
                        'name': 'data_drift_detected',
                        'description': 'Significant data drift detected',
                        'condition': 'data_drift > 0.1',
                        'severity': 'high',
                        'notification_channels': ['email', 'slack']
                    }
                ]
            
            return dashboard
        except Exception as e:
            print(f"Error creating ML monitoring dashboard: {e}")
            return {}
    
    def create_ml_governance_framework(self, governance_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create ML governance framework"""
        try:
            governance = {
                'name': governance_config['name'],
                'description': governance_config.get('description', ''),
                'policies': governance_config.get('policies', []),
                'approval_workflows': governance_config.get('approval_workflows', []),
                'compliance_checks': governance_config.get('compliance_checks', []),
                'created_at': datetime.now().isoformat()
            }
            
            # Add default governance policies
            if not governance['policies']:
                governance['policies'] = [
                    {
                        'name': 'model_approval_policy',
                        'description': 'Model approval requirements',
                        'rules': [
                            'All models must pass accuracy threshold',
                            'All models must pass bias checks',
                            'All models must have documentation',
                            'All models must pass security review'
                        ]
                    },
                    {
                        'name': 'data_privacy_policy',
                        'description': 'Data privacy requirements',
                        'rules': [
                            'No PII in training data',
                            'Data encryption at rest and in transit',
                            'Access logging enabled',
                            'Data retention policies enforced'
                        ]
                    },
                    {
                        'name': 'model_deployment_policy',
                        'description': 'Model deployment requirements',
                        'rules': [
                            'A/B testing required for new models',
                            'Rollback plan must be documented',
                            'Monitoring must be enabled',
                            'Performance baselines must be established'
                        ]
                    }
                ]
            
            # Add default approval workflows
            if not governance['approval_workflows']:
                governance['approval_workflows'] = [
                    {
                        'name': 'model_approval_workflow',
                        'description': 'Model approval process',
                        'stages': [
                            {
                                'name': 'technical_review',
                                'approvers': ['data_scientist', 'ml_engineer'],
                                'requirements': ['accuracy_threshold', 'bias_checks']
                            },
                            {
                                'name': 'business_review',
                                'approvers': ['product_manager', 'business_stakeholder'],
                                'requirements': ['business_impact_assessment']
                            },
                            {
                                'name': 'security_review',
                                'approvers': ['security_team'],
                                'requirements': ['security_scan', 'vulnerability_assessment']
                            }
                        ]
                    }
                ]
            
            return governance
        except Exception as e:
            print(f"Error creating ML governance framework: {e}")
            return {}
    
    def create_ml_automation_workflow(self, automation_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create ML automation workflow"""
        try:
            workflow = {
                'name': automation_config['name'],
                'description': automation_config.get('description', ''),
                'triggers': automation_config.get('triggers', []),
                'actions': automation_config.get('actions', []),
                'conditions': automation_config.get('conditions', []),
                'created_at': datetime.now().isoformat()
            }
            
            # Add default automation triggers
            if not workflow['triggers']:
                workflow['triggers'] = [
                    {
                        'name': 'data_updated',
                        'type': 's3_event',
                        'description': 'Trigger when new data is uploaded',
                        'configuration': {
                            'bucket': 'ml-data-bucket',
                            'prefix': 'training-data/',
                            'suffix': '.csv'
                        }
                    },
                    {
                        'name': 'model_performance_degraded',
                        'type': 'cloudwatch_alarm',
                        'description': 'Trigger when model performance drops',
                        'configuration': {
                            'alarm_name': 'model-accuracy-alarm',
                            'threshold': 0.8
                        }
                    },
                    {
                        'name': 'scheduled_retraining',
                        'type': 'schedule',
                        'description': 'Trigger scheduled model retraining',
                        'configuration': {
                            'schedule_expression': 'cron(0 2 * * ? *)'  # Daily at 2 AM
                        }
                    }
                ]
            
            # Add default automation actions
            if not workflow['actions']:
                workflow['actions'] = [
                    {
                        'name': 'start_training',
                        'type': 'sagemaker_training',
                        'description': 'Start model training job',
                        'configuration': {
                            'training_job_name': 'auto-retrain-{timestamp}',
                            'role_arn': 'arn:aws:iam::account:role/SageMakerExecutionRole'
                        }
                    },
                    {
                        'name': 'evaluate_model',
                        'type': 'sagemaker_processing',
                        'description': 'Evaluate model performance',
                        'configuration': {
                            'processing_job_name': 'model-evaluation-{timestamp}',
                            'role_arn': 'arn:aws:iam::account:role/SageMakerExecutionRole'
                        }
                    },
                    {
                        'name': 'deploy_model',
                        'type': 'sagemaker_deployment',
                        'description': 'Deploy model to endpoint',
                        'configuration': {
                            'endpoint_name': 'ml-endpoint',
                            'instance_type': 'ml.m5.large'
                        }
                    },
                    {
                        'name': 'send_notification',
                        'type': 'sns_notification',
                        'description': 'Send notification about workflow status',
                        'configuration': {
                            'topic_arn': 'arn:aws:sns:region:account:ml-notifications',
                            'message': 'ML workflow completed successfully'
                        }
                    }
                ]
            
            return workflow
        except Exception as e:
            print(f"Error creating ML automation workflow: {e}")
            return {}
    
    def get_ml_metrics(self, metric_names: List[str], 
                      start_time: datetime = None,
                      end_time: datetime = None) -> Dict[str, Any]:
        """Get ML metrics from CloudWatch"""
        try:
            if not start_time:
                start_time = datetime.now() - timedelta(hours=24)
            if not end_time:
                end_time = datetime.now()
            
            metrics_data = {}
            
            for metric_name in metric_names:
                response = self.cloudwatch_client.get_metric_statistics(
                    Namespace='AWS/SageMaker',
                    MetricName=metric_name,
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=3600,
                    Statistics=['Sum', 'Average', 'Maximum']
                )
                
                metrics_data[metric_name] = {
                    'datapoints': response['Datapoints'],
                    'period': {'start': start_time.isoformat(), 'end': end_time.isoformat()}
                }
            
            return metrics_data
        except Exception as e:
            print(f"Error getting ML metrics: {e}")
            return {}
    
    def create_ml_ops_dashboard(self, dashboard_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive MLOps dashboard"""
        try:
            dashboard = {
                'name': dashboard_config['name'],
                'description': dashboard_config.get('description', ''),
                'sections': dashboard_config.get('sections', []),
                'created_at': datetime.now().isoformat()
            }
            
            # Add default dashboard sections
            if not dashboard['sections']:
                dashboard['sections'] = [
                    {
                        'name': 'model_performance',
                        'title': 'Model Performance',
                        'metrics': ['accuracy', 'precision', 'recall', 'f1_score'],
                        'charts': ['line_chart', 'bar_chart']
                    },
                    {
                        'name': 'data_quality',
                        'title': 'Data Quality',
                        'metrics': ['data_drift', 'missing_values', 'outliers'],
                        'charts': ['histogram', 'box_plot']
                    },
                    {
                        'name': 'model_bias',
                        'title': 'Model Bias',
                        'metrics': ['demographic_parity', 'equalized_odds'],
                        'charts': ['bar_chart', 'heatmap']
                    },
                    {
                        'name': 'infrastructure',
                        'title': 'Infrastructure',
                        'metrics': ['cpu_utilization', 'memory_utilization', 'latency'],
                        'charts': ['line_chart', 'gauge']
                    },
                    {
                        'name': 'deployment_status',
                        'title': 'Deployment Status',
                        'metrics': ['deployment_success_rate', 'rollback_count'],
                        'charts': ['status_indicator', 'timeline']
                    }
                ]
            
            return dashboard
        except Exception as e:
            print(f"Error creating MLOps dashboard: {e}")
            return {}


# Example usage and testing
if __name__ == "__main__":
    # Initialize MLOps manager
    mlops_manager = MLOpsManager()
    
    # Create ML workflow
    workflow = mlops_manager.create_ml_workflow({
        'name': 'ml-pipeline-1',
        'description': 'Complete ML pipeline with MLOps'
    })
    print(f"Created ML workflow: {workflow['name']}")
    
    # Create CI/CD pipeline
    ci_cd_pipeline = mlops_manager.create_ci_cd_pipeline({
        'name': 'ml-ci-cd-pipeline',
        'description': 'CI/CD pipeline for ML models'
    })
    print(f"Created CI/CD pipeline: {ci_cd_pipeline['name']}")
    
    # Create model versioning system
    versioning = mlops_manager.create_model_versioning_system({
        'name': 'model-versioning',
        'description': 'Semantic versioning for ML models'
    })
    print(f"Created model versioning system: {versioning['name']}")
    
    # Create ML monitoring dashboard
    monitoring = mlops_manager.create_ml_monitoring_dashboard({
        'name': 'ml-monitoring',
        'description': 'Comprehensive ML monitoring'
    })
    print(f"Created ML monitoring dashboard: {monitoring['name']}")
    
    # Create ML governance framework
    governance = mlops_manager.create_ml_governance_framework({
        'name': 'ml-governance',
        'description': 'ML governance and compliance framework'
    })
    print(f"Created ML governance framework: {governance['name']}")
    
    # Create ML automation workflow
    automation = mlops_manager.create_ml_automation_workflow({
        'name': 'ml-automation',
        'description': 'Automated ML workflows'
    })
    print(f"Created ML automation workflow: {automation['name']}")
    
    # Create MLOps dashboard
    dashboard = mlops_manager.create_ml_ops_dashboard({
        'name': 'mlops-dashboard',
        'description': 'Comprehensive MLOps dashboard'
    })
    print(f"Created MLOps dashboard: {dashboard['name']}")
    
    # Get ML metrics
    metrics = mlops_manager.get_ml_metrics(['TrainingJobStatus', 'Invocations'])
    print(f"Retrieved metrics for {len(metrics)} metric types")