#!/usr/bin/env python3
"""
AWS SageMaker Manager
Comprehensive SageMaker management with training, deployment, and MLOps capabilities
"""

import boto3
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from botocore.exceptions import ClientError
import pandas as pd
import numpy as np


class SageMakerManager:
    """Comprehensive AWS SageMaker management and MLOps"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.sagemaker_client = boto3.client('sagemaker', region_name=region)
        self.s3_client = boto3.client('s3', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=region)
        self.ecr_client = boto3.client('ecr', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.api_gateway_client = boto3.client('apigateway', region_name=region)
        
    def create_training_job(self, job_config: Dict[str, Any]) -> Optional[str]:
        """Create SageMaker training job"""
        try:
            response = self.sagemaker_client.create_training_job(
                TrainingJobName=job_config['TrainingJobName'],
                RoleArn=job_config['RoleArn'],
                AlgorithmSpecification=job_config['AlgorithmSpecification'],
                InputDataConfig=job_config.get('InputDataConfig', []),
                OutputDataConfig=job_config['OutputDataConfig'],
                ResourceConfig=job_config['ResourceConfig'],
                StoppingCondition=job_config.get('StoppingCondition', {}),
                VpcConfig=job_config.get('VpcConfig', {}),
                Tags=job_config.get('Tags', []),
                EnableNetworkIsolation=job_config.get('EnableNetworkIsolation', False),
                EnableInterContainerTrafficEncryption=job_config.get('EnableInterContainerTrafficEncryption', False),
                EnableManagedSpotTraining=job_config.get('EnableManagedSpotTraining', False),
                CheckpointConfig=job_config.get('CheckpointConfig', {}),
                DebugHookConfig=job_config.get('DebugHookConfig', {}),
                DebugRuleConfigurations=job_config.get('DebugRuleConfigurations', []),
                TensorBoardOutputConfig=job_config.get('TensorBoardOutputConfig', {}),
                ExperimentConfig=job_config.get('ExperimentConfig', {}),
                ProfilerConfig=job_config.get('ProfilerConfig', {}),
                ProfilerRuleConfigurations=job_config.get('ProfilerRuleConfigurations', [])
            )
            return response['TrainingJobArn']
        except ClientError as e:
            print(f"Error creating training job: {e}")
            return None
    
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
    
    def create_model(self, model_config: Dict[str, Any]) -> Optional[str]:
        """Create SageMaker model"""
        try:
            response = self.sagemaker_client.create_model(
                ModelName=model_config['ModelName'],
                PrimaryContainer=model_config.get('PrimaryContainer', {}),
                Containers=model_config.get('Containers', []),
                ExecutionRoleArn=model_config['ExecutionRoleArn'],
                Tags=model_config.get('Tags', []),
                VpcConfig=model_config.get('VpcConfig', {}),
                EnableNetworkIsolation=model_config.get('EnableNetworkIsolation', False),
                InferenceExecutionConfig=model_config.get('InferenceExecutionConfig', {})
            )
            return response['ModelArn']
        except ClientError as e:
            print(f"Error creating model: {e}")
            return None
    
    def create_endpoint_config(self, endpoint_config: Dict[str, Any]) -> Optional[str]:
        """Create endpoint configuration"""
        try:
            response = self.sagemaker_client.create_endpoint_config(
                EndpointConfigName=endpoint_config['EndpointConfigName'],
                ProductionVariants=endpoint_config['ProductionVariants'],
                DataCaptureConfig=endpoint_config.get('DataCaptureConfig', {}),
                Tags=endpoint_config.get('Tags', []),
                KmsKeyId=endpoint_config.get('KmsKeyId'),
                AsyncInferenceConfig=endpoint_config.get('AsyncInferenceConfig', {}),
                ExplainerConfig=endpoint_config.get('ExplainerConfig', {}),
                ShadowProductionVariants=endpoint_config.get('ShadowProductionVariants', [])
            )
            return response['EndpointConfigArn']
        except ClientError as e:
            print(f"Error creating endpoint config: {e}")
            return None
    
    def create_endpoint(self, endpoint_name: str, endpoint_config_name: str, 
                       tags: List[Dict[str, str]] = None) -> Optional[str]:
        """Create SageMaker endpoint"""
        try:
            response = self.sagemaker_client.create_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=endpoint_config_name,
                Tags=tags or []
            )
            return response['EndpointArn']
        except ClientError as e:
            print(f"Error creating endpoint: {e}")
            return None
    
    def create_batch_transform_job(self, transform_config: Dict[str, Any]) -> Optional[str]:
        """Create batch transform job"""
        try:
            response = self.sagemaker_client.create_transform_job(
                TransformJobName=transform_config['TransformJobName'],
                ModelName=transform_config['ModelName'],
                MaxConcurrentTransforms=transform_config.get('MaxConcurrentTransforms', 1),
                MaxPayloadInMB=transform_config.get('MaxPayloadInMB', 6),
                BatchStrategy=transform_config.get('BatchStrategy', 'MultiRecord'),
                Environment=transform_config.get('Environment', {}),
                TransformInput=transform_config['TransformInput'],
                TransformOutput=transform_config['TransformOutput'],
                TransformResources=transform_config['TransformResources'],
                DataProcessing=transform_config.get('DataProcessing', {}),
                Tags=transform_config.get('Tags', []),
                ExperimentConfig=transform_config.get('ExperimentConfig', {})
            )
            return response['TransformJobArn']
        except ClientError as e:
            print(f"Error creating batch transform job: {e}")
            return None
    
    def create_processing_job(self, processing_config: Dict[str, Any]) -> Optional[str]:
        """Create SageMaker processing job"""
        try:
            response = self.sagemaker_client.create_processing_job(
                ProcessingJobName=processing_config['ProcessingJobName'],
                RoleArn=processing_config['RoleArn'],
                AppSpecification=processing_config['AppSpecification'],
                ProcessingInputs=processing_config.get('ProcessingInputs', []),
                ProcessingOutputConfig=processing_config.get('ProcessingOutputConfig', {}),
                ProcessingResources=processing_config['ProcessingResources'],
                StoppingCondition=processing_config.get('StoppingCondition', {}),
                Environment=processing_config.get('Environment', {}),
                NetworkConfig=processing_config.get('NetworkConfig', {}),
                Tags=processing_config.get('Tags', []),
                ExperimentConfig=processing_config.get('ExperimentConfig', {}),
                MonitoringScheduleConfig=processing_config.get('MonitoringScheduleConfig', {})
            )
            return response['ProcessingJobArn']
        except ClientError as e:
            print(f"Error creating processing job: {e}")
            return None
    
    def create_model_package_group(self, group_name: str, description: str = None,
                                 tags: List[Dict[str, str]] = None) -> Optional[str]:
        """Create model package group"""
        try:
            response = self.sagemaker_client.create_model_package_group(
                ModelPackageGroupName=group_name,
                ModelPackageGroupDescription=description or f"Model package group for {group_name}",
                Tags=tags or []
            )
            return response['ModelPackageGroupArn']
        except ClientError as e:
            print(f"Error creating model package group: {e}")
            return None
    
    def create_model_package(self, package_config: Dict[str, Any]) -> Optional[str]:
        """Create model package"""
        try:
            response = self.sagemaker_client.create_model_package(
                ModelPackageName=package_config.get('ModelPackageName'),
                ModelPackageGroupName=package_config.get('ModelPackageGroupName'),
                ModelPackageDescription=package_config.get('ModelPackageDescription', ''),
                InferenceSpecification=package_config.get('InferenceSpecification', {}),
                ValidationSpecification=package_config.get('ValidationSpecification', {}),
                SourceAlgorithmSpecification=package_config.get('SourceAlgorithmSpecification', {}),
                CertifyForMarketplace=package_config.get('CertifyForMarketplace', False),
                ModelApprovalStatus=package_config.get('ModelApprovalStatus', 'PendingManualApproval'),
                MetadataProperties=package_config.get('MetadataProperties', {}),
                ModelMetrics=package_config.get('ModelMetrics', {}),
                ClientToken=package_config.get('ClientToken'),
                CustomerMetadataProperties=package_config.get('CustomerMetadataProperties', {}),
                DriftCheckBaselines=package_config.get('DriftCheckBaselines', {}),
                Domain=package_config.get('Domain'),
                Task=package_config.get('Task'),
                SamplePayloadUrl=package_config.get('SamplePayloadUrl'),
                Tags=package_config.get('Tags', [])
            )
            return response['ModelPackageArn']
        except ClientError as e:
            print(f"Error creating model package: {e}")
            return None
    
    def create_pipeline(self, pipeline_config: Dict[str, Any]) -> Optional[str]:
        """Create SageMaker pipeline"""
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
            print(f"Error creating pipeline: {e}")
            return None
    
    def create_experiment(self, experiment_name: str, display_name: str = None,
                         description: str = None, tags: List[Dict[str, str]] = None) -> Optional[str]:
        """Create SageMaker experiment"""
        try:
            response = self.sagemaker_client.create_experiment(
                ExperimentName=experiment_name,
                DisplayName=display_name or experiment_name,
                Description=description or f"Experiment: {experiment_name}",
                Tags=tags or []
            )
            return response['ExperimentArn']
        except ClientError as e:
            print(f"Error creating experiment: {e}")
            return None
    
    def create_trial(self, trial_name: str, experiment_name: str,
                    display_name: str = None, tags: List[Dict[str, str]] = None) -> Optional[str]:
        """Create trial within experiment"""
        try:
            response = self.sagemaker_client.create_trial(
                TrialName=trial_name,
                ExperimentName=experiment_name,
                DisplayName=display_name or trial_name,
                Tags=tags or []
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
    
    def create_monitoring_schedule(self, schedule_config: Dict[str, Any]) -> Optional[str]:
        """Create model monitoring schedule"""
        try:
            response = self.sagemaker_client.create_monitoring_schedule(
                MonitoringScheduleName=schedule_config['MonitoringScheduleName'],
                MonitoringScheduleConfig=schedule_config['MonitoringScheduleConfig'],
                Tags=schedule_config.get('Tags', [])
            )
            return response['MonitoringScheduleArn']
        except ClientError as e:
            print(f"Error creating monitoring schedule: {e}")
            return None
    
    def create_data_quality_job_definition(self, job_definition: Dict[str, Any]) -> Optional[str]:
        """Create data quality job definition"""
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
        """Create model quality job definition"""
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
        """Create bias job definition"""
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
        """Create explainability job definition"""
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
    
    def get_training_job(self, job_name: str) -> Optional[Dict[str, Any]]:
        """Get training job details"""
        try:
            response = self.sagemaker_client.describe_training_job(
                TrainingJobName=job_name
            )
            return response
        except ClientError as e:
            print(f"Error getting training job: {e}")
            return None
    
    def get_model(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get model details"""
        try:
            response = self.sagemaker_client.describe_model(
                ModelName=model_name
            )
            return response
        except ClientError as e:
            print(f"Error getting model: {e}")
            return None
    
    def get_endpoint(self, endpoint_name: str) -> Optional[Dict[str, Any]]:
        """Get endpoint details"""
        try:
            response = self.sagemaker_client.describe_endpoint(
                EndpointName=endpoint_name
            )
            return response
        except ClientError as e:
            print(f"Error getting endpoint: {e}")
            return None
    
    def list_training_jobs(self, status_equals: str = None, 
                          created_after: datetime = None,
                          created_before: datetime = None) -> List[Dict[str, Any]]:
        """List training jobs"""
        try:
            kwargs = {}
            if status_equals:
                kwargs['StatusEquals'] = status_equals
            if created_after:
                kwargs['CreationTimeAfter'] = created_after
            if created_before:
                kwargs['CreationTimeBefore'] = created_before
            
            response = self.sagemaker_client.list_training_jobs(**kwargs)
            return response['TrainingJobSummaries']
        except ClientError as e:
            print(f"Error listing training jobs: {e}")
            return []
    
    def list_models(self, name_contains: str = None) -> List[Dict[str, Any]]:
        """List models"""
        try:
            kwargs = {}
            if name_contains:
                kwargs['NameContains'] = name_contains
            
            response = self.sagemaker_client.list_models(**kwargs)
            return response['Models']
        except ClientError as e:
            print(f"Error listing models: {e}")
            return []
    
    def list_endpoints(self, status_equals: str = None) -> List[Dict[str, Any]]:
        """List endpoints"""
        try:
            kwargs = {}
            if status_equals:
                kwargs['StatusEquals'] = status_equals
            
            response = self.sagemaker_client.list_endpoints(**kwargs)
            return response['Endpoints']
        except ClientError as e:
            print(f"Error listing endpoints: {e}")
            return []
    
    def invoke_endpoint(self, endpoint_name: str, body: str, 
                       content_type: str = 'application/json') -> Optional[Dict[str, Any]]:
        """Invoke SageMaker endpoint"""
        try:
            response = self.sagemaker_client.invoke_endpoint(
                EndpointName=endpoint_name,
                Body=body,
                ContentType=content_type
            )
            return {
                'Body': response['Body'].read().decode('utf-8'),
                'ContentType': response.get('ContentType'),
                'InvokedProductionVariant': response.get('InvokedProductionVariant')
            }
        except ClientError as e:
            print(f"Error invoking endpoint: {e}")
            return None
    
    def delete_endpoint(self, endpoint_name: str) -> bool:
        """Delete SageMaker endpoint"""
        try:
            self.sagemaker_client.delete_endpoint(EndpointName=endpoint_name)
            return True
        except ClientError as e:
            print(f"Error deleting endpoint: {e}")
            return False
    
    def delete_model(self, model_name: str) -> bool:
        """Delete SageMaker model"""
        try:
            self.sagemaker_client.delete_model(ModelName=model_name)
            return True
        except ClientError as e:
            print(f"Error deleting model: {e}")
            return False
    
    def stop_training_job(self, job_name: str) -> bool:
        """Stop training job"""
        try:
            self.sagemaker_client.stop_training_job(TrainingJobName=job_name)
            return True
        except ClientError as e:
            print(f"Error stopping training job: {e}")
            return False
    
    def get_training_job_metrics(self, job_name: str) -> Dict[str, Any]:
        """Get training job metrics from CloudWatch"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=24)
            
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/SageMaker',
                MetricName='TrainingJobStatus',
                Dimensions=[
                    {
                        'Name': 'TrainingJobName',
                        'Value': job_name
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Average']
            )
            
            return {
                'metrics': response['Datapoints'],
                'job_name': job_name,
                'period': {'start': start_time.isoformat(), 'end': end_time.isoformat()}
            }
        except Exception as e:
            print(f"Error getting training job metrics: {e}")
            return {}
    
    def get_endpoint_metrics(self, endpoint_name: str) -> Dict[str, Any]:
        """Get endpoint metrics from CloudWatch"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=24)
            
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/SageMaker',
                MetricName='Invocations',
                Dimensions=[
                    {
                        'Name': 'EndpointName',
                        'Value': endpoint_name
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum', 'Average']
            )
            
            return {
                'metrics': response['Datapoints'],
                'endpoint_name': endpoint_name,
                'period': {'start': start_time.isoformat(), 'end': end_time.isoformat()}
            }
        except Exception as e:
            print(f"Error getting endpoint metrics: {e}")
            return {}
    
    def create_sagemaker_role(self, role_name: str, 
                            policies: List[str] = None) -> Optional[str]:
        """Create IAM role for SageMaker"""
        try:
            if not policies:
                policies = [
                    'arn:aws:iam::aws:policy/AmazonSageMakerFullAccess',
                    'arn:aws:iam::aws:policy/AmazonS3FullAccess',
                    'arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess'
                ]
            
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "sagemaker.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                Description=f"SageMaker execution role for {role_name}"
            )
            
            role_arn = response['Role']['Arn']
            
            # Attach policies
            for policy_arn in policies:
                self.iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            return role_arn
        except ClientError as e:
            print(f"Error creating SageMaker role: {e}")
            return None
    
    def create_experiment_tracking_dashboard(self, experiment_name: str) -> Dict[str, Any]:
        """Create experiment tracking dashboard data"""
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
    
    def create_mlops_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create MLOps workflow configuration"""
        try:
            workflow = {
                'name': workflow_config['name'],
                'description': workflow_config.get('description', ''),
                'stages': workflow_config.get('stages', []),
                'triggers': workflow_config.get('triggers', []),
                'notifications': workflow_config.get('notifications', []),
                'created_at': datetime.now().isoformat()
            }
            
            # Add common MLOps stages if not provided
            if not workflow['stages']:
                workflow['stages'] = [
                    {
                        'name': 'data_validation',
                        'type': 'processing',
                        'description': 'Validate and preprocess data'
                    },
                    {
                        'name': 'model_training',
                        'type': 'training',
                        'description': 'Train ML model'
                    },
                    {
                        'name': 'model_evaluation',
                        'type': 'processing',
                        'description': 'Evaluate model performance'
                    },
                    {
                        'name': 'model_validation',
                        'type': 'validation',
                        'description': 'Validate model quality'
                    },
                    {
                        'name': 'model_deployment',
                        'type': 'deployment',
                        'description': 'Deploy model to endpoint'
                    },
                    {
                        'name': 'model_monitoring',
                        'type': 'monitoring',
                        'description': 'Monitor model performance'
                    }
                ]
            
            return workflow
        except Exception as e:
            print(f"Error creating MLOps workflow: {e}")
            return {}


# Example usage and testing
if __name__ == "__main__":
    # Initialize SageMaker manager
    sagemaker_manager = SageMakerManager()
    
    # Create SageMaker role
    role_arn = sagemaker_manager.create_sagemaker_role("ml-platform-role")
    print(f"Created SageMaker role: {role_arn}")
    
    # Create experiment
    experiment_arn = sagemaker_manager.create_experiment(
        experiment_name="ml-experiment-1",
        display_name="ML Experiment 1",
        description="First ML experiment"
    )
    print(f"Created experiment: {experiment_arn}")
    
    # Create model package group
    group_arn = sagemaker_manager.create_model_package_group(
        group_name="ml-models",
        description="ML model package group"
    )
    print(f"Created model package group: {group_arn}")
    
    # List existing training jobs
    training_jobs = sagemaker_manager.list_training_jobs()
    print(f"Found {len(training_jobs)} training jobs")
    
    # List existing models
    models = sagemaker_manager.list_models()
    print(f"Found {len(models)} models")
    
    # List existing endpoints
    endpoints = sagemaker_manager.list_endpoints()
    print(f"Found {len(endpoints)} endpoints")
    
    # Create MLOps workflow
    workflow = sagemaker_manager.create_mlops_workflow({
        'name': 'ml-pipeline-1',
        'description': 'Complete ML pipeline'
    })
    print(f"Created MLOps workflow: {workflow['name']}")