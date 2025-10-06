#!/usr/bin/env python3
"""
AWS CodePipeline Manager for CI/CD automation.

This module provides comprehensive pipeline management capabilities including
pipeline creation, execution, monitoring, and automation.
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


class PipelineManager:
    """
    AWS CodePipeline Manager for CI/CD automation.
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize PipelineManager with AWS clients."""
        self.region = region
        self.codepipeline_client = boto3.client('codepipeline', region_name=region)
        self.codebuild_client = boto3.client('codebuild', region_name=region)
        self.codedeploy_client = boto3.client('codedeploy', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        self.s3_client = boto3.client('s3', region_name=region)
        
    def create_pipeline(self, pipeline_name: str, pipeline_config: Dict[str, Any]) -> Optional[str]:
        """Create CodePipeline with comprehensive configuration."""
        try:
            # Validate pipeline configuration
            self._validate_pipeline_config(pipeline_config)
            
            # Create S3 bucket for artifacts if not exists
            artifact_bucket = self._create_artifact_bucket(pipeline_name)
            
            # Create IAM roles if not exist
            pipeline_role_arn = self._create_pipeline_role(pipeline_name)
            build_role_arn = self._create_build_role(pipeline_name)
            
            # Build pipeline structure
            pipeline_structure = {
                'name': pipeline_name,
                'roleArn': pipeline_role_arn,
                'stages': self._build_pipeline_stages(pipeline_config, build_role_arn),
                'artifactStore': {
                    'type': 'S3',
                    'location': artifact_bucket
                }
            }
            
            # Add tags
            if 'tags' in pipeline_config:
                pipeline_structure['tags'] = pipeline_config['tags']
            
            response = self.codepipeline_client.create_pipeline(
                pipeline=pipeline_structure
            )
            
            logger.info(f"Pipeline {pipeline_name} created successfully")
            return response['pipeline']['name']
            
        except Exception as e:
            logger.error(f"Error creating pipeline: {str(e)}")
            return None
    
    def _validate_pipeline_config(self, config: Dict[str, Any]) -> None:
        """Validate pipeline configuration."""
        required_fields = ['repository_name', 'branch_name']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
    
    def _create_artifact_bucket(self, pipeline_name: str) -> str:
        """Create S3 bucket for pipeline artifacts."""
        bucket_name = f"{pipeline_name}-artifacts-{int(time.time())}"
        
        try:
            self.s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': self.region} if self.region != 'us-east-1' else None
            )
            
            # Enable versioning
            self.s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            
            # Set lifecycle policy
            lifecycle_policy = {
                'Rules': [{
                    'ID': 'DeleteOldArtifacts',
                    'Status': 'Enabled',
                    'Expiration': {'Days': 30}
                }]
            }
            
            self.s3_client.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration=lifecycle_policy
            )
            
            logger.info(f"Created artifact bucket: {bucket_name}")
            return bucket_name
            
        except Exception as e:
            logger.error(f"Error creating artifact bucket: {str(e)}")
            raise
    
    def _create_pipeline_role(self, pipeline_name: str) -> str:
        """Create IAM role for CodePipeline."""
        role_name = f"{pipeline_name}-pipeline-role"
        
        try:
            # Check if role exists
            self.iam_client.get_role(RoleName=role_name)
            logger.info(f"Pipeline role {role_name} already exists")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
            
        except self.iam_client.exceptions.NoSuchEntityException:
            # Create role
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "codepipeline.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                Description=f"IAM role for {pipeline_name} CodePipeline"
            )
            
            # Attach policies
            policies = [
                "arn:aws:iam::aws:policy/AWSCodePipelineServiceRole",
                "arn:aws:iam::aws:policy/AmazonS3FullAccess",
                "arn:aws:iam::aws:policy/AWSCodeCommitFullAccess",
                "arn:aws:iam::aws:policy/AWSCodeBuildDeveloperAccess",
                "arn:aws:iam::aws:policy/AWSCodeDeployDeployerAccess"
            ]
            
            for policy_arn in policies:
                self.iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            logger.info(f"Created pipeline role: {role_name}")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
    
    def _create_build_role(self, pipeline_name: str) -> str:
        """Create IAM role for CodeBuild."""
        role_name = f"{pipeline_name}-build-role"
        
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
                Description=f"IAM role for {pipeline_name} CodeBuild"
            )
            
            # Attach policies
            policies = [
                "arn:aws:iam::aws:policy/AWSCodeBuildDeveloperAccess",
                "arn:aws:iam::aws:policy/AmazonS3FullAccess",
                "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnlyAccess"
            ]
            
            for policy_arn in policies:
                self.iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            logger.info(f"Created build role: {role_name}")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
    
    def _build_pipeline_stages(self, config: Dict[str, Any], build_role_arn: str) -> List[Dict[str, Any]]:
        """Build pipeline stages from configuration."""
        stages = []
        
        # Source stage
        source_stage = {
            'name': 'Source',
            'actions': [{
                'name': 'Source',
                'actionTypeId': {
                    'category': 'Source',
                    'owner': 'AWS',
                    'provider': config.get('source_provider', 'CodeCommit'),
                    'version': '1'
                },
                'configuration': {
                    'RepositoryName': config['repository_name'],
                    'BranchName': config['branch_name']
                },
                'outputArtifacts': [{'name': 'SourceCode'}]
            }]
        }
        
        # Add source-specific configuration
        if config.get('source_provider') == 'GitHub':
            source_stage['actions'][0]['configuration'].update({
                'Owner': config.get('github_owner'),
                'Repo': config.get('github_repo'),
                'OAuthToken': config.get('github_token')
            })
        
        stages.append(source_stage)
        
        # Build stage
        if config.get('build_enabled', True):
            build_stage = {
                'name': 'Build',
                'actions': [{
                    'name': 'Build',
                    'actionTypeId': {
                        'category': 'Build',
                        'owner': 'AWS',
                        'provider': 'CodeBuild',
                        'version': '1'
                    },
                    'configuration': {
                        'ProjectName': f"{config['repository_name']}-build"
                    },
                    'inputArtifacts': [{'name': 'SourceCode'}],
                    'outputArtifacts': [{'name': 'BuildOutput'}]
                }]
            }
            stages.append(build_stage)
        
        # Test stage
        if config.get('test_enabled', True):
            test_stage = {
                'name': 'Test',
                'actions': [{
                    'name': 'Test',
                    'actionTypeId': {
                        'category': 'Test',
                        'owner': 'AWS',
                        'provider': 'CodeBuild',
                        'version': '1'
                    },
                    'configuration': {
                        'ProjectName': f"{config['repository_name']}-test"
                    },
                    'inputArtifacts': [{'name': 'BuildOutput'}],
                    'outputArtifacts': [{'name': 'TestOutput'}]
                }]
            }
            stages.append(test_stage)
        
        # Deploy stage
        if config.get('deploy_enabled', True):
            deploy_stage = {
                'name': 'Deploy',
                'actions': [{
                    'name': 'Deploy',
                    'actionTypeId': {
                        'category': 'Deploy',
                        'owner': 'AWS',
                        'provider': config.get('deploy_provider', 'CodeDeploy'),
                        'version': '1'
                    },
                    'configuration': {
                        'ApplicationName': config.get('application_name', f"{config['repository_name']}-app"),
                        'DeploymentGroupName': config.get('deployment_group_name', f"{config['repository_name']}-deployment-group")
                    },
                    'inputArtifacts': [{'name': 'BuildOutput'}]
                }]
            }
            stages.append(deploy_stage)
        
        return stages
    
    def start_pipeline_execution(self, pipeline_name: str) -> Optional[str]:
        """Start pipeline execution."""
        try:
            response = self.codepipeline_client.start_pipeline_execution(
                name=pipeline_name
            )
            
            execution_id = response['pipelineExecutionId']
            logger.info(f"Pipeline execution started: {execution_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"Error starting pipeline execution: {str(e)}")
            return None
    
    def get_pipeline_status(self, pipeline_name: str) -> Dict[str, Any]:
        """Get pipeline execution status."""
        try:
            response = self.codepipeline_client.get_pipeline_state(
                name=pipeline_name
            )
            
            return {
                'pipeline_name': response['pipelineName'],
                'stage_states': response['stageStates'],
                'updated': response['updated']
            }
            
        except Exception as e:
            logger.error(f"Error getting pipeline status: {str(e)}")
            return {}
    
    def get_pipeline_execution_history(self, pipeline_name: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get pipeline execution history."""
        try:
            response = self.codepipeline_client.list_pipeline_executions(
                pipelineName=pipeline_name,
                maxResults=max_results
            )
            
            executions = []
            for execution in response['pipelineExecutionSummaries']:
                executions.append({
                    'execution_id': execution['pipelineExecutionId'],
                    'status': execution['status'],
                    'start_time': execution['startTime'],
                    'last_update_time': execution['lastUpdateTime']
                })
            
            return executions
            
        except Exception as e:
            logger.error(f"Error getting pipeline execution history: {str(e)}")
            return []
    
    def delete_pipeline(self, pipeline_name: str) -> bool:
        """Delete pipeline."""
        try:
            self.codepipeline_client.delete_pipeline(name=pipeline_name)
            logger.info(f"Pipeline {pipeline_name} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting pipeline: {str(e)}")
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
    """Main function for testing PipelineManager."""
    # Example usage
    pipeline_manager = PipelineManager()
    
    # Example pipeline configuration
    pipeline_config = {
        'repository_name': 'my-app-repo',
        'branch_name': 'main',
        'source_provider': 'CodeCommit',
        'build_enabled': True,
        'test_enabled': True,
        'deploy_enabled': True,
        'application_name': 'my-app',
        'deployment_group_name': 'my-app-deployment-group',
        'tags': {
            'Environment': 'production',
            'Project': 'my-project'
        }
    }
    
    # Create pipeline
    pipeline_name = pipeline_manager.create_pipeline('my-cicd-pipeline', pipeline_config)
    if pipeline_name:
        print(f"Pipeline created: {pipeline_name}")
        
        # Start execution
        execution_id = pipeline_manager.start_pipeline_execution(pipeline_name)
        if execution_id:
            print(f"Pipeline execution started: {execution_id}")
        
        # Get status
        status = pipeline_manager.get_pipeline_status(pipeline_name)
        print(f"Pipeline status: {json.dumps(status, indent=2, default=str)}")


if __name__ == "__main__":
    main()