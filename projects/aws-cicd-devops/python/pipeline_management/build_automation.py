#!/usr/bin/env python3
"""
AWS CodeBuild automation for build processes.

This module provides comprehensive build automation capabilities including
project creation, build execution, monitoring, and optimization.
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


class BuildAutomation:
    """
    AWS CodeBuild automation for build processes.
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize BuildAutomation with AWS clients."""
        self.region = region
        self.codebuild_client = boto3.client('codebuild', region_name=region)
        self.s3_client = boto3.client('s3', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        self.logs_client = boto3.client('logs', region_name=region)
        
    def create_build_project(self, project_name: str, build_config: Dict[str, Any]) -> Optional[str]:
        """Create CodeBuild project with comprehensive configuration."""
        try:
            # Validate build configuration
            self._validate_build_config(build_config)
            
            # Create IAM role if not exists
            role_arn = self._create_build_role(project_name)
            
            # Create CloudWatch log group
            log_group_name = f"/aws/codebuild/{project_name}"
            self._create_log_group(log_group_name)
            
            # Build project configuration
            project_config = {
                'name': project_name,
                'description': build_config.get('description', f"Build project for {project_name}"),
                'source': self._build_source_config(build_config),
                'artifacts': self._build_artifacts_config(build_config),
                'environment': self._build_environment_config(build_config),
                'serviceRole': role_arn,
                'timeoutInMinutes': build_config.get('timeout_minutes', 60),
                'queuedTimeoutInMinutes': build_config.get('queued_timeout_minutes', 480),
                'logsConfig': {
                    'cloudWatchLogs': {
                        'status': 'ENABLED',
                        'groupName': log_group_name
                    }
                }
            }
            
            # Add tags
            if 'tags' in build_config:
                project_config['tags'] = [
                    {'key': k, 'value': v} for k, v in build_config['tags'].items()
                ]
            
            response = self.codebuild_client.create_project(**project_config)
            
            logger.info(f"Build project {project_name} created successfully")
            return response['project']['name']
            
        except Exception as e:
            logger.error(f"Error creating build project: {str(e)}")
            return None
    
    def _validate_build_config(self, config: Dict[str, Any]) -> None:
        """Validate build configuration."""
        required_fields = ['source_type']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
    
    def _create_build_role(self, project_name: str) -> str:
        """Create IAM role for CodeBuild."""
        role_name = f"{project_name}-build-role"
        
        try:
            # Check if role exists
            self.iam_client.get_role(RoleName=role_name)
            logger.info(f"Build role {role_name} already exists")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
            
        except self.iam_client.exceptions.NoSuchEntityException:
            # Create role
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "codebuild.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                Description=f"IAM role for {project_name} CodeBuild"
            )
            
            # Attach policies
            policies = [
                "arn:aws:iam::aws:policy/AWSCodeBuildDeveloperAccess",
                "arn:aws:iam::aws:policy/AmazonS3FullAccess",
                "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnlyAccess",
                "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
            ]
            
            for policy_arn in policies:
                self.iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            logger.info(f"Created build role: {role_name}")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
    
    def _create_log_group(self, log_group_name: str) -> None:
        """Create CloudWatch log group."""
        try:
            self.logs_client.create_log_group(logGroupName=log_group_name)
            logger.info(f"Created log group: {log_group_name}")
        except self.logs_client.exceptions.ResourceAlreadyExistsException:
            logger.info(f"Log group {log_group_name} already exists")
        except Exception as e:
            logger.error(f"Error creating log group: {str(e)}")
    
    def _build_source_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build source configuration."""
        source_type = config['source_type']
        
        if source_type == 'CODECOMMIT':
            return {
                'type': 'CODECOMMIT',
                'location': config.get('repository_url'),
                'buildspec': config.get('buildspec_file', 'buildspec.yml')
            }
        elif source_type == 'CODEPIPELINE':
            return {
                'type': 'CODEPIPELINE',
                'buildspec': config.get('buildspec_file', 'buildspec.yml')
            }
        elif source_type == 'GITHUB':
            return {
                'type': 'GITHUB',
                'location': config.get('repository_url'),
                'buildspec': config.get('buildspec_file', 'buildspec.yml'),
                'auth': {
                    'type': 'OAUTH',
                    'resource': config.get('github_token')
                }
            }
        elif source_type == 'S3':
            return {
                'type': 'S3',
                'location': config.get('s3_location'),
                'buildspec': config.get('buildspec_file', 'buildspec.yml')
            }
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
    
    def _build_artifacts_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build artifacts configuration."""
        artifacts_type = config.get('artifacts_type', 'CODEPIPELINE')
        
        if artifacts_type == 'CODEPIPELINE':
            return {
                'type': 'CODEPIPELINE'
            }
        elif artifacts_type == 'S3':
            return {
                'type': 'S3',
                'location': config.get('artifacts_location'),
                'path': config.get('artifacts_path', ''),
                'name': config.get('artifacts_name', 'build-artifacts'),
                'packaging': config.get('artifacts_packaging', 'ZIP')
            }
        elif artifacts_type == 'NO_ARTIFACTS':
            return {
                'type': 'NO_ARTIFACTS'
            }
        else:
            raise ValueError(f"Unsupported artifacts type: {artifacts_type}")
    
    def _build_environment_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build environment configuration."""
        environment_config = {
            'type': config.get('environment_type', 'LINUX_CONTAINER'),
            'image': config.get('image', 'aws/codebuild/amazonlinux2-x86_64-standard:3.0'),
            'computeType': config.get('compute_type', 'BUILD_GENERAL1_SMALL'),
            'privilegedMode': config.get('privileged_mode', False),
            'imagePullCredentialsType': 'CODEBUILD'
        }
        
        # Add environment variables
        if 'environment_variables' in config:
            environment_config['environmentVariables'] = [
                {
                    'name': name,
                    'value': str(value),
                    'type': 'PLAINTEXT'
                } for name, value in config['environment_variables'].items()
            ]
        
        # Add VPC configuration
        if 'vpc_config' in config:
            environment_config['vpcConfig'] = config['vpc_config']
        
        return environment_config
    
    def start_build(self, project_name: str, build_config: Dict[str, Any] = None) -> Optional[str]:
        """Start CodeBuild project build."""
        try:
            build_params = {
                'projectName': project_name
            }
            
            if build_config:
                # Add environment variables override
                if 'environment_variables' in build_config:
                    build_params['environmentVariablesOverride'] = [
                        {
                            'name': name,
                            'value': str(value),
                            'type': 'PLAINTEXT'
                        } for name, value in build_config['environment_variables'].items()
                    ]
                
                # Add source version
                if 'source_version' in build_config:
                    build_params['sourceVersion'] = build_config['source_version']
            
            response = self.codebuild_client.start_build(**build_params)
            
            build_id = response['build']['id']
            logger.info(f"Build started: {build_id}")
            return build_id
            
        except Exception as e:
            logger.error(f"Error starting build: {str(e)}")
            return None
    
    def get_build_status(self, build_id: str) -> Dict[str, Any]:
        """Get build status."""
        try:
            response = self.codebuild_client.batch_get_builds(ids=[build_id])
            
            if response['builds']:
                build = response['builds'][0]
                return {
                    'build_id': build['id'],
                    'status': build['buildStatus'],
                    'phase': build['currentPhase'],
                    'start_time': build.get('startTime'),
                    'end_time': build.get('endTime'),
                    'duration': build.get('duration'),
                    'logs': build.get('logs', {}).get('deepLink'),
                    'environment': build.get('environment'),
                    'source': build.get('source'),
                    'artifacts': build.get('artifacts')
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting build status: {str(e)}")
            return {}
    
    def list_builds(self, project_name: str = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """List builds for a project."""
        try:
            params = {'maxResults': max_results}
            if project_name:
                params['projectName'] = project_name
            
            response = self.codebuild_client.list_builds(**params)
            
            if not response['ids']:
                return []
            
            # Get detailed build information
            builds_response = self.codebuild_client.batch_get_builds(ids=response['ids'])
            
            builds = []
            for build in builds_response['builds']:
                builds.append({
                    'build_id': build['id'],
                    'project_name': build['projectName'],
                    'status': build['buildStatus'],
                    'phase': build['currentPhase'],
                    'start_time': build.get('startTime'),
                    'end_time': build.get('endTime'),
                    'duration': build.get('duration')
                })
            
            return builds
            
        except Exception as e:
            logger.error(f"Error listing builds: {str(e)}")
            return []
    
    def get_build_logs(self, build_id: str) -> str:
        """Get build logs."""
        try:
            response = self.codebuild_client.batch_get_builds(ids=[build_id])
            
            if response['builds']:
                build = response['builds'][0]
                logs_info = build.get('logs', {})
                
                if 'groupName' in logs_info and 'streamName' in logs_info:
                    # Get logs from CloudWatch
                    log_group = logs_info['groupName']
                    log_stream = logs_info['streamName']
                    
                    logs_response = self.logs_client.get_log_events(
                        logGroupName=log_group,
                        logStreamName=log_stream
                    )
                    
                    log_events = logs_response.get('events', [])
                    logs = '\n'.join([event['message'] for event in log_events])
                    
                    return logs
            
            return ""
            
        except Exception as e:
            logger.error(f"Error getting build logs: {str(e)}")
            return ""
    
    def stop_build(self, build_id: str) -> bool:
        """Stop build."""
        try:
            self.codebuild_client.stop_build(id=build_id)
            logger.info(f"Build {build_id} stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping build: {str(e)}")
            return False
    
    def delete_project(self, project_name: str) -> bool:
        """Delete build project."""
        try:
            self.codebuild_client.delete_project(name=project_name)
            logger.info(f"Build project {project_name} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting build project: {str(e)}")
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
    """Main function for testing BuildAutomation."""
    # Example usage
    build_automation = BuildAutomation()
    
    # Example build configuration
    build_config = {
        'source_type': 'CODEPIPELINE',
        'artifacts_type': 'CODEPIPELINE',
        'environment_type': 'LINUX_CONTAINER',
        'image': 'aws/codebuild/amazonlinux2-x86_64-standard:3.0',
        'compute_type': 'BUILD_GENERAL1_SMALL',
        'timeout_minutes': 60,
        'description': 'Example build project',
        'environment_variables': {
            'NODE_ENV': 'production',
            'BUILD_ENV': 'ci'
        },
        'tags': {
            'Environment': 'production',
            'Project': 'my-project'
        }
    }
    
    # Create build project
    project_name = build_automation.create_build_project('my-build-project', build_config)
    if project_name:
        print(f"Build project created: {project_name}")
        
        # Start build
        build_id = build_automation.start_build(project_name)
        if build_id:
            print(f"Build started: {build_id}")
            
            # Monitor build
            import time
            while True:
                status = build_automation.get_build_status(build_id)
                print(f"Build status: {status.get('status')} - Phase: {status.get('phase')}")
                
                if status.get('status') in ['SUCCEEDED', 'FAILED', 'STOPPED']:
                    break
                
                time.sleep(30)


if __name__ == "__main__":
    main()