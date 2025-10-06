#!/usr/bin/env python3
"""
AWS SageMaker Manager for machine learning operations.

This module provides comprehensive SageMaker management capabilities including
notebook instances, training jobs, model deployment, and endpoint management.
"""

import boto3
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SageMakerManager:
    """
    AWS SageMaker Manager for machine learning operations.
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize SageMakerManager with AWS clients."""
        self.region = region
        self.sagemaker_client = boto3.client('sagemaker', region_name=region)
        self.s3_client = boto3.client('s3', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        
    def create_notebook_instance(self, instance_config: Dict[str, Any]) -> Optional[str]:
        """Create SageMaker notebook instance."""
        try:
            # Validate instance configuration
            self._validate_notebook_config(instance_config)
            
            # Create IAM role if not specified
            if 'role_arn' not in instance_config:
                instance_config['role_arn'] = self._create_sagemaker_role(instance_config['instance_name'])
            
            # Build instance parameters
            instance_params = {
                'NotebookInstanceName': instance_config['instance_name'],
                'InstanceType': instance_config['instance_type'],
                'RoleArn': instance_config['role_arn'],
                'VolumeSizeInGB': instance_config.get('volume_size', 20),
                'Tags': instance_config.get('tags', [])
            }
            
            # Add optional parameters
            if 'subnet_id' in instance_config:
                instance_params['SubnetId'] = instance_config['subnet_id']
            
            if 'security_group_ids' in instance_config:
                instance_params['SecurityGroupIds'] = instance_config['security_group_ids']
            
            if 'kms_key_id' in instance_config:
                instance_params['KmsKeyId'] = instance_config['kms_key_id']
            
            if 'lifecycle_config_name' in instance_config:
                instance_params['LifecycleConfigName'] = instance_config['lifecycle_config_name']
            
            # Create notebook instance
            response = self.sagemaker_client.create_notebook_instance(**instance_params)
            
            instance_name = response['NotebookInstanceName']
            logger.info(f"SageMaker notebook instance {instance_name} creation initiated")
            
            # Wait for instance to be ready if requested
            if instance_config.get('wait_for_ready', True):
                self._wait_for_notebook_ready(instance_name)
            
            return instance_name
            
        except Exception as e:
            logger.error(f"Error creating notebook instance: {str(e)}")
            return None
    
    def _validate_notebook_config(self, config: Dict[str, Any]) -> None:
        """Validate notebook instance configuration."""
        required_fields = ['instance_name', 'instance_type']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
    
    def _create_sagemaker_role(self, instance_name: str) -> str:
        """Create IAM role for SageMaker."""
        role_name = f"{instance_name}-sagemaker-role"
        
        try:
            # Check if role exists
            self.iam_client.get_role(RoleName=role_name)
            logger.info(f"SageMaker role {role_name} already exists")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
            
        except self.iam_client.exceptions.NoSuchEntityException:
            # Create role
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "sagemaker.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                Description=f"IAM role for {instance_name} SageMaker notebook"
            )
            
            # Attach policies
            policies = [
                "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
            ]
            
            for policy_arn in policies:
                self.iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            logger.info(f"Created SageMaker role: {role_name}")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
    
    def _wait_for_notebook_ready(self, instance_name: str, timeout: int = 1800) -> bool:
        """Wait for notebook instance to be ready."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.sagemaker_client.describe_notebook_instance(NotebookInstanceName=instance_name)
                status = response['NotebookInstanceStatus']
                
                if status == 'InService':
                    logger.info(f"Notebook instance {instance_name} is now ready")
                    return True
                elif status in ['Failed', 'Stopped']:
                    logger.error(f"Notebook instance {instance_name} is in {status} state")
                    return False
                
                logger.info(f"Waiting for notebook instance {instance_name} to be ready. Current status: {status}")
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error checking notebook instance status: {str(e)}")
                return False
        
        logger.error(f"Timeout waiting for notebook instance {instance_name} to be ready")
        return False
    
    def get_notebook_info(self, instance_name: str) -> Dict[str, Any]:
        """Get notebook instance information."""
        try:
            response = self.sagemaker_client.describe_notebook_instance(NotebookInstanceName=instance_name)
            
            return {
                'instance_name': response['NotebookInstanceName'],
                'instance_type': response['InstanceType'],
                'role_arn': response['RoleArn'],
                'status': response['NotebookInstanceStatus'],
                'creation_time': response['CreationTime'],
                'last_modified_time': response['LastModifiedTime'],
                'volume_size': response['VolumeSizeInGB'],
                'subnet_id': response.get('SubnetId'),
                'security_groups': response.get('SecurityGroups', []),
                'kms_key_id': response.get('KmsKeyId'),
                'lifecycle_config_name': response.get('LifecycleConfigName'),
                'url': response.get('Url')
            }
            
        except Exception as e:
            logger.error(f"Error getting notebook instance info: {str(e)}")
            return {}
    
    def start_notebook_instance(self, instance_name: str) -> bool:
        """Start notebook instance."""
        try:
            self.sagemaker_client.start_notebook_instance(NotebookInstanceName=instance_name)
            logger.info(f"Notebook instance {instance_name} start initiated")
            return True
            
        except Exception as e:
            logger.error(f"Error starting notebook instance: {str(e)}")
            return False
    
    def stop_notebook_instance(self, instance_name: str) -> bool:
        """Stop notebook instance."""
        try:
            self.sagemaker_client.stop_notebook_instance(NotebookInstanceName=instance_name)
            logger.info(f"Notebook instance {instance_name} stop initiated")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping notebook instance: {str(e)}")
            return False
    
    def create_training_job(self, job_config: Dict[str, Any]) -> Optional[str]:
        """Create SageMaker training job."""
        try:
            # Validate job configuration
            self._validate_training_job_config(job_config)
            
            # Create IAM role if not specified
            if 'role_arn' not in job_config:
                job_config['role_arn'] = self._create_training_role(job_config['job_name'])
            
            # Build training job parameters
            training_params = {
                'TrainingJobName': job_config['job_name'],
                'RoleArn': job_config['role_arn'],
                'AlgorithmSpecification': job_config['algorithm_specification'],
                'ResourceConfig': job_config['resource_config'],
                'OutputDataConfig': job_config['output_data_config'],
                'StoppingCondition': job_config['stopping_condition']
            }
            
            # Add optional parameters
            if 'input_data_config' in job_config:
                training_params['InputDataConfig'] = job_config['input_data_config']
            
            if 'hyperparameters' in job_config:
                training_params['HyperParameters'] = job_config['hyperparameters']
            
            if 'tags' in job_config:
                training_params['Tags'] = job_config['tags']
            
            # Create training job
            response = self.sagemaker_client.create_training_job(**training_params)
            
            job_name = response['TrainingJobArn'].split('/')[-1]
            logger.info(f"SageMaker training job {job_name} creation initiated")
            return job_name
            
        except Exception as e:
            logger.error(f"Error creating training job: {str(e)}")
            return None
    
    def _validate_training_job_config(self, config: Dict[str, Any]) -> None:
        """Validate training job configuration."""
        required_fields = ['job_name', 'algorithm_specification', 'resource_config', 
                          'output_data_config', 'stopping_condition']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
    
    def _create_training_role(self, job_name: str) -> str:
        """Create IAM role for training job."""
        role_name = f"{job_name}-training-role"
        
        try:
            # Check if role exists
            self.iam_client.get_role(RoleName=role_name)
            logger.info(f"Training role {role_name} already exists")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
            
        except self.iam_client.exceptions.NoSuchEntityException:
            # Create role
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "sagemaker.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                Description=f"IAM role for {job_name} training job"
            )
            
            # Attach policies
            policies = [
                "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
            ]
            
            for policy_arn in policies:
                self.iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            logger.info(f"Created training role: {role_name}")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
    
    def get_training_job_info(self, job_name: str) -> Dict[str, Any]:
        """Get training job information."""
        try:
            response = self.sagemaker_client.describe_training_job(TrainingJobName=job_name)
            
            return {
                'job_name': response['TrainingJobName'],
                'job_arn': response['TrainingJobArn'],
                'status': response['TrainingJobStatus'],
                'creation_time': response['CreationTime'],
                'training_start_time': response.get('TrainingStartTime'),
                'training_end_time': response.get('TrainingEndTime'),
                'role_arn': response['RoleArn'],
                'algorithm_specification': response['AlgorithmSpecification'],
                'resource_config': response['ResourceConfig'],
                'output_data_config': response['OutputDataConfig'],
                'stopping_condition': response['StoppingCondition'],
                'hyperparameters': response.get('HyperParameters', {}),
                'input_data_config': response.get('InputDataConfig', []),
                'model_artifacts': response.get('ModelArtifacts', {}),
                'final_metric_data': response.get('FinalMetricDataList', [])
            }
            
        except Exception as e:
            logger.error(f"Error getting training job info: {str(e)}")
            return {}
    
    def create_model(self, model_config: Dict[str, Any]) -> Optional[str]:
        """Create SageMaker model."""
        try:
            # Validate model configuration
            self._validate_model_config(model_config)
            
            # Create IAM role if not specified
            if 'execution_role_arn' not in model_config:
                model_config['execution_role_arn'] = self._create_model_role(model_config['model_name'])
            
            # Build model parameters
            model_params = {
                'ModelName': model_config['model_name'],
                'ExecutionRoleArn': model_config['execution_role_arn'],
                'PrimaryContainer': model_config['primary_container']
            }
            
            # Add optional parameters
            if 'vpc_config' in model_config:
                model_params['VpcConfig'] = model_config['vpc_config']
            
            if 'tags' in model_config:
                model_params['Tags'] = model_config['tags']
            
            # Create model
            response = self.sagemaker_client.create_model(**model_params)
            
            model_name = response['ModelArn'].split('/')[-1]
            logger.info(f"SageMaker model {model_name} created successfully")
            return model_name
            
        except Exception as e:
            logger.error(f"Error creating model: {str(e)}")
            return None
    
    def _validate_model_config(self, config: Dict[str, Any]) -> None:
        """Validate model configuration."""
        required_fields = ['model_name', 'primary_container']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
    
    def _create_model_role(self, model_name: str) -> str:
        """Create IAM role for model."""
        role_name = f"{model_name}-model-role"
        
        try:
            # Check if role exists
            self.iam_client.get_role(RoleName=role_name)
            logger.info(f"Model role {role_name} already exists")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
            
        except self.iam_client.exceptions.NoSuchEntityException:
            # Create role
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "sagemaker.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                Description=f"IAM role for {model_name} model"
            )
            
            # Attach policies
            policies = [
                "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
            ]
            
            for policy_arn in policies:
                self.iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            logger.info(f"Created model role: {role_name}")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
    
    def create_endpoint(self, endpoint_config: Dict[str, Any]) -> Optional[str]:
        """Create SageMaker endpoint."""
        try:
            # Validate endpoint configuration
            self._validate_endpoint_config(endpoint_config)
            
            # Build endpoint parameters
            endpoint_params = {
                'EndpointName': endpoint_config['endpoint_name'],
                'EndpointConfigName': endpoint_config['endpoint_config_name']
            }
            
            # Add optional parameters
            if 'tags' in endpoint_config:
                endpoint_params['Tags'] = endpoint_config['tags']
            
            # Create endpoint
            response = self.sagemaker_client.create_endpoint(**endpoint_params)
            
            endpoint_name = response['EndpointArn'].split('/')[-1]
            logger.info(f"SageMaker endpoint {endpoint_name} creation initiated")
            return endpoint_name
            
        except Exception as e:
            logger.error(f"Error creating endpoint: {str(e)}")
            return None
    
    def _validate_endpoint_config(self, config: Dict[str, Any]) -> None:
        """Validate endpoint configuration."""
        required_fields = ['endpoint_name', 'endpoint_config_name']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
    
    def list_notebook_instances(self) -> List[Dict[str, Any]]:
        """List all notebook instances."""
        try:
            response = self.sagemaker_client.list_notebook_instances()
            instances = []
            
            for instance in response['NotebookInstances']:
                instances.append({
                    'instance_name': instance['NotebookInstanceName'],
                    'instance_type': instance['InstanceType'],
                    'status': instance['NotebookInstanceStatus'],
                    'creation_time': instance['CreationTime'],
                    'url': instance.get('Url')
                })
            
            return instances
            
        except Exception as e:
            logger.error(f"Error listing notebook instances: {str(e)}")
            return []
    
    def delete_notebook_instance(self, instance_name: str) -> bool:
        """Delete notebook instance."""
        try:
            self.sagemaker_client.delete_notebook_instance(NotebookInstanceName=instance_name)
            logger.info(f"Notebook instance {instance_name} deletion initiated")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting notebook instance: {str(e)}")
            return False
    
    def _get_account_id(self) -> str:
        """Get AWS account ID."""
        try:
            sts_client = boto3.client('sts', region_name=self.region)
            response = sts_client.get_caller_identity()
            return response['Account']
        except Exception as e:
            logger.error(f"Error getting account ID: {str(e)}")
            return ""


def main():
    """Main function for testing SageMakerManager."""
    # Example usage
    sagemaker_manager = SageMakerManager()
    
    # Example notebook instance configuration
    notebook_config = {
        'instance_name': 'test-notebook',
        'instance_type': 'ml.t3.medium',
        'volume_size': 20,
        'tags': [
            {'Key': 'Environment', 'Value': 'test'},
            {'Key': 'Project', 'Value': 'data-analytics'}
        ]
    }
    
    # Create notebook instance
    instance_name = sagemaker_manager.create_notebook_instance(notebook_config)
    if instance_name:
        print(f"Notebook instance created: {instance_name}")
        
        # Get instance info
        info = sagemaker_manager.get_notebook_info(instance_name)
        print(f"Instance info: {info}")
        
        # List instances
        instances = sagemaker_manager.list_notebook_instances()
        print(f"All instances: {instances}")


if __name__ == "__main__":
    main()