#!/usr/bin/env python3
"""
AWS CodeDeploy automation for deployment processes.

This module provides comprehensive deployment automation capabilities including
application creation, deployment group management, deployment execution, and monitoring.
"""

import boto3
import json
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeploymentManager:
    """
    AWS CodeDeploy automation for deployment processes.
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize DeploymentManager with AWS clients."""
        self.region = region
        self.codedeploy_client = boto3.client('codedeploy', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        self.ec2_client = boto3.client('ec2', region_name=region)
        self.autoscaling_client = boto3.client('autoscaling', region_name=region)
        self.elasticloadbalancing_client = boto3.client('elbv2', region_name=region)
        
    def create_application(self, application_name: str, application_config: Dict[str, Any]) -> Optional[str]:
        """Create CodeDeploy application."""
        try:
            # Validate application configuration
            self._validate_application_config(application_config)
            
            # Create IAM role if not exists
            role_arn = self._create_deployment_role(application_name)
            
            # Build application configuration
            app_config = {
                'applicationName': application_name,
                'computePlatform': application_config.get('compute_platform', 'Server'),
                'tags': [
                    {'key': k, 'value': v} for k, v in application_config.get('tags', {}).items()
                ]
            }
            
            response = self.codedeploy_client.create_application(**app_config)
            
            logger.info(f"Application {application_name} created successfully")
            return response['applicationId']
            
        except Exception as e:
            logger.error(f"Error creating application: {str(e)}")
            return None
    
    def _validate_application_config(self, config: Dict[str, Any]) -> None:
        """Validate application configuration."""
        required_fields = ['compute_platform']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
    
    def _create_deployment_role(self, application_name: str) -> str:
        """Create IAM role for CodeDeploy."""
        role_name = f"{application_name}-deployment-role"
        
        try:
            # Check if role exists
            self.iam_client.get_role(RoleName=role_name)
            logger.info(f"Deployment role {role_name} already exists")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
            
        except self.iam_client.exceptions.NoSuchEntityException:
            # Create role
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "codedeploy.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                Description=f"IAM role for {application_name} CodeDeploy"
            )
            
            # Attach policies
            policies = [
                "arn:aws:iam::aws:policy/AWSCodeDeployRole",
                "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
                "arn:aws:iam::aws:policy/AmazonEC2FullAccess",
                "arn:aws:iam::aws:policy/AWSCodeDeployRoleForECS"
            ]
            
            for policy_arn in policies:
                self.iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            logger.info(f"Created deployment role: {role_name}")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
    
    def create_deployment_group(self, application_name: str, deployment_group_name: str, 
                               group_config: Dict[str, Any]) -> Optional[str]:
        """Create deployment group."""
        try:
            # Validate deployment group configuration
            self._validate_deployment_group_config(group_config)
            
            # Build deployment group configuration
            dg_config = {
                'applicationName': application_name,
                'deploymentGroupName': deployment_group_name,
                'serviceRoleArn': group_config.get('service_role_arn', 
                                                 f"arn:aws:iam::{self._get_account_id()}:role/{application_name}-deployment-role"),
                'deploymentConfigName': group_config.get('deployment_config_name', 'CodeDeployDefault.OneAtATime'),
                'tags': [
                    {'key': k, 'value': v} for k, v in group_config.get('tags', {}).items()
                ]
            }
            
            # Add EC2 instances configuration
            if 'ec2_tag_filters' in group_config:
                dg_config['ec2TagFilters'] = group_config['ec2_tag_filters']
            elif 'ec2_instance_ids' in group_config:
                dg_config['ec2TagFilters'] = [
                    {
                        'type': 'KEY_AND_VALUE',
                        'key': 'Name',
                        'value': instance_id
                    } for instance_id in group_config['ec2_instance_ids']
                ]
            
            # Add Auto Scaling groups
            if 'auto_scaling_groups' in group_config:
                dg_config['autoScalingGroups'] = group_config['auto_scaling_groups']
            
            # Add load balancer configuration
            if 'load_balancer_info' in group_config:
                dg_config['loadBalancerInfo'] = group_config['load_balancer_info']
            
            # Add blue/green deployment configuration
            if 'blue_green_deployment_configuration' in group_config:
                dg_config['blueGreenDeploymentConfiguration'] = group_config['blue_green_deployment_configuration']
            
            # Add alarm configuration
            if 'alarm_configuration' in group_config:
                dg_config['alarmConfiguration'] = group_config['alarm_configuration']
            
            # Add auto rollback configuration
            if 'auto_rollback_configuration' in group_config:
                dg_config['autoRollbackConfiguration'] = group_config['auto_rollback_configuration']
            
            response = self.codedeploy_client.create_deployment_group(**dg_config)
            
            logger.info(f"Deployment group {deployment_group_name} created successfully")
            return response['deploymentGroupId']
            
        except Exception as e:
            logger.error(f"Error creating deployment group: {str(e)}")
            return None
    
    def _validate_deployment_group_config(self, config: Dict[str, Any]) -> None:
        """Validate deployment group configuration."""
        # At least one target type must be specified
        target_types = ['ec2_tag_filters', 'ec2_instance_ids', 'auto_scaling_groups']
        if not any(target_type in config for target_type in target_types):
            raise ValueError("At least one target type must be specified")
    
    def create_deployment(self, application_name: str, deployment_group_name: str, 
                         deployment_config: Dict[str, Any]) -> Optional[str]:
        """Create deployment."""
        try:
            # Validate deployment configuration
            self._validate_deployment_config(deployment_config)
            
            # Build deployment configuration
            deploy_config = {
                'applicationName': application_name,
                'deploymentGroupName': deployment_group_name,
                'revision': deployment_config['revision'],
                'deploymentConfigName': deployment_config.get('deployment_config_name', 'CodeDeployDefault.OneAtATime'),
                'description': deployment_config.get('description', f"Deployment for {application_name}"),
                'ignoreApplicationStopFailures': deployment_config.get('ignore_application_stop_failures', False)
            }
            
            # Add file exists behavior
            if 'file_exists_behavior' in deployment_config:
                deploy_config['fileExistsBehavior'] = deployment_config['file_exists_behavior']
            
            # Add update out dated instances only
            if 'update_outdated_instances_only' in deployment_config:
                deploy_config['updateOutdatedInstancesOnly'] = deployment_config['update_outdated_instances_only']
            
            response = self.codedeploy_client.create_deployment(**deploy_config)
            
            deployment_id = response['deploymentId']
            logger.info(f"Deployment {deployment_id} created successfully")
            return deployment_id
            
        except Exception as e:
            logger.error(f"Error creating deployment: {str(e)}")
            return None
    
    def _validate_deployment_config(self, config: Dict[str, Any]) -> None:
        """Validate deployment configuration."""
        required_fields = ['revision']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
    
    def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment status."""
        try:
            response = self.codedeploy_client.get_deployment(deploymentId=deployment_id)
            
            deployment = response['deploymentInfo']
            return {
                'deployment_id': deployment['deploymentId'],
                'application_name': deployment['applicationName'],
                'deployment_group_name': deployment['deploymentGroupName'],
                'status': deployment['status'],
                'status_message': deployment.get('statusMessage', ''),
                'create_time': deployment['createTime'],
                'start_time': deployment.get('startTime'),
                'complete_time': deployment.get('completeTime'),
                'deployment_config_name': deployment['deploymentConfigName'],
                'revision': deployment['revision']
            }
            
        except Exception as e:
            logger.error(f"Error getting deployment status: {str(e)}")
            return {}
    
    def list_deployments(self, application_name: str = None, deployment_group_name: str = None, 
                        max_results: int = 10) -> List[Dict[str, Any]]:
        """List deployments."""
        try:
            params = {'maxResults': max_results}
            if application_name:
                params['applicationName'] = application_name
            if deployment_group_name:
                params['deploymentGroupName'] = deployment_group_name
            
            response = self.codedeploy_client.list_deployments(**params)
            
            deployments = []
            for deployment_id in response['deployments']:
                status = self.get_deployment_status(deployment_id)
                if status:
                    deployments.append(status)
            
            return deployments
            
        except Exception as e:
            logger.error(f"Error listing deployments: {str(e)}")
            return []
    
    def stop_deployment(self, deployment_id: str) -> bool:
        """Stop deployment."""
        try:
            self.codedeploy_client.stop_deployment(deploymentId=deployment_id)
            logger.info(f"Deployment {deployment_id} stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping deployment: {str(e)}")
            return False
    
    def get_deployment_instances(self, deployment_id: str) -> List[Dict[str, Any]]:
        """Get deployment instances."""
        try:
            response = self.codedeploy_client.list_deployment_instances(deploymentId=deployment_id)
            
            instances = []
            for instance_id in response['instancesList']:
                instance_response = self.codedeploy_client.get_deployment_instance(
                    deploymentId=deployment_id,
                    instanceId=instance_id
                )
                
                instance_info = instance_response['instanceSummary']
                instances.append({
                    'instance_id': instance_id,
                    'status': instance_info['status'],
                    'last_updated_at': instance_info['lastUpdatedAt'],
                    'lifecycle_events': instance_info.get('lifecycleEvents', [])
                })
            
            return instances
            
        except Exception as e:
            logger.error(f"Error getting deployment instances: {str(e)}")
            return []
    
    def create_deployment_config(self, deployment_config_name: str, config: Dict[str, Any]) -> bool:
        """Create deployment configuration."""
        try:
            deployment_config = {
                'deploymentConfigName': deployment_config_name,
                'minimumHealthyHosts': config.get('minimum_healthy_hosts', {
                    'type': 'HOST_COUNT',
                    'value': 1
                })
            }
            
            # Add traffic routing configuration for blue/green
            if 'traffic_routing_config' in config:
                deployment_config['trafficRoutingConfig'] = config['traffic_routing_config']
            
            self.codedeploy_client.create_deployment_config(**deployment_config)
            
            logger.info(f"Deployment configuration {deployment_config_name} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating deployment configuration: {str(e)}")
            return False
    
    def delete_application(self, application_name: str) -> bool:
        """Delete application."""
        try:
            self.codedeploy_client.delete_application(applicationName=application_name)
            logger.info(f"Application {application_name} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting application: {str(e)}")
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
    """Main function for testing DeploymentManager."""
    # Example usage
    deployment_manager = DeploymentManager()
    
    # Example application configuration
    application_config = {
        'compute_platform': 'Server',
        'tags': {
            'Environment': 'production',
            'Project': 'my-project'
        }
    }
    
    # Create application
    app_id = deployment_manager.create_application('my-app', application_config)
    if app_id:
        print(f"Application created: {app_id}")
        
        # Example deployment group configuration
        group_config = {
            'ec2_tag_filters': [
                {
                    'type': 'KEY_AND_VALUE',
                    'key': 'Environment',
                    'value': 'production'
                }
            ],
            'deployment_config_name': 'CodeDeployDefault.OneAtATime',
            'auto_rollback_configuration': {
                'enabled': True,
                'events': ['DEPLOYMENT_FAILURE']
            },
            'alarm_configuration': {
                'enabled': True,
                'alarms': ['my-alarm']
            }
        }
        
        # Create deployment group
        dg_id = deployment_manager.create_deployment_group('my-app', 'my-deployment-group', group_config)
        if dg_id:
            print(f"Deployment group created: {dg_id}")
            
            # Example deployment configuration
            deployment_config = {
                'revision': {
                    'revisionType': 'S3',
                    's3Location': {
                        'bucket': 'my-deployment-bucket',
                        'key': 'my-app.zip',
                        'bundleType': 'zip'
                    }
                },
                'description': 'Production deployment',
                'file_exists_behavior': 'OVERWRITE'
            }
            
            # Create deployment
            deployment_id = deployment_manager.create_deployment('my-app', 'my-deployment-group', deployment_config)
            if deployment_id:
                print(f"Deployment created: {deployment_id}")
                
                # Monitor deployment
                import time
                while True:
                    status = deployment_manager.get_deployment_status(deployment_id)
                    print(f"Deployment status: {status.get('status')}")
                    
                    if status.get('status') in ['Succeeded', 'Failed', 'Stopped']:
                        break
                    
                    time.sleep(30)


if __name__ == "__main__":
    main()