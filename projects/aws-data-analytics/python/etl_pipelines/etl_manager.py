#!/usr/bin/env python3
"""
AWS ETL Pipeline Manager for data processing.

This module provides comprehensive ETL pipeline management capabilities including
Glue job management, Step Functions workflows, and data transformation.
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


class ETLPipelineManager:
    """
    AWS ETL Pipeline Manager for data processing.
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize ETLPipelineManager with AWS clients."""
        self.region = region
        self.glue_client = boto3.client('glue', region_name=region)
        self.stepfunctions_client = boto3.client('stepfunctions', region_name=region)
        self.s3_client = boto3.client('s3', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        
    def create_glue_job(self, job_name: str, job_config: Dict[str, Any]) -> Optional[str]:
        """Create Glue ETL job."""
        try:
            # Validate job configuration
            self._validate_job_config(job_config)
            
            # Create IAM role if not exists
            role_arn = self._create_glue_role(job_name)
            
            # Build job parameters
            job_params = {
                'Name': job_name,
                'Role': role_arn,
                'Command': {
                    'Name': job_config.get('command_name', 'glueetl'),
                    'ScriptLocation': job_config['script_location'],
                    'PythonVersion': job_config.get('python_version', '3')
                },
                'DefaultArguments': job_config.get('default_arguments', {}),
                'MaxCapacity': job_config.get('max_capacity', 2.0),
                'WorkerType': job_config.get('worker_type', 'Standard'),
                'NumberOfWorkers': job_config.get('number_of_workers', 2),
                'Timeout': job_config.get('timeout', 2880),
                'MaxRetries': job_config.get('max_retries', 0),
                'Description': job_config.get('description', f'ETL job for {job_name}'),
                'Tags': job_config.get('tags', {})
            }
            
            # Add connections if specified
            if 'connections' in job_config:
                job_params['Connections'] = {'Connections': job_config['connections']}
            
            # Add glue version if specified
            if 'glue_version' in job_config:
                job_params['GlueVersion'] = job_config['glue_version']
            
            response = self.glue_client.create_job(**job_params)
            
            logger.info(f"Glue job {job_name} created successfully")
            return response['Name']
            
        except Exception as e:
            logger.error(f"Error creating Glue job: {str(e)}")
            return None
    
    def _validate_job_config(self, config: Dict[str, Any]) -> None:
        """Validate job configuration."""
        required_fields = ['script_location']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
    
    def _create_glue_role(self, job_name: str) -> str:
        """Create IAM role for Glue job."""
        role_name = f"{job_name}-glue-role"
        
        try:
            # Check if role exists
            self.iam_client.get_role(RoleName=role_name)
            logger.info(f"Glue role {role_name} already exists")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
            
        except self.iam_client.exceptions.NoSuchEntityException:
            # Create role
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "glue.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                Description=f"IAM role for {job_name} Glue job"
            )
            
            # Attach policies
            policies = [
                "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole",
                "arn:aws:iam::aws:policy/AmazonS3FullAccess"
            ]
            
            for policy_arn in policies:
                self.iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            logger.info(f"Created Glue role: {role_name}")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
    
    def start_glue_job(self, job_name: str, job_run_config: Dict[str, Any] = None) -> Optional[str]:
        """Start Glue job run."""
        try:
            run_params = {
                'JobName': job_name
            }
            
            if job_run_config:
                if 'arguments' in job_run_config:
                    run_params['Arguments'] = job_run_config['arguments']
                if 'allocated_capacity' in job_run_config:
                    run_params['AllocatedCapacity'] = job_run_config['allocated_capacity']
                if 'worker_type' in job_run_config:
                    run_params['WorkerType'] = job_run_config['worker_type']
                if 'number_of_workers' in job_run_config:
                    run_params['NumberOfWorkers'] = job_run_config['number_of_workers']
                if 'timeout' in job_run_config:
                    run_params['Timeout'] = job_run_config['timeout']
            
            response = self.glue_client.start_job_run(**run_params)
            
            job_run_id = response['JobRunId']
            logger.info(f"Glue job run started: {job_run_id}")
            return job_run_id
            
        except Exception as e:
            logger.error(f"Error starting Glue job: {str(e)}")
            return None
    
    def get_job_run_status(self, job_name: str, job_run_id: str) -> Dict[str, Any]:
        """Get Glue job run status."""
        try:
            response = self.glue_client.get_job_run(
                JobName=job_name,
                RunId=job_run_id
            )
            
            job_run = response['JobRun']
            return {
                'job_name': job_run['JobName'],
                'job_run_id': job_run['Id'],
                'job_run_state': job_run['JobRunState'],
                'started_on': job_run.get('StartedOn'),
                'completed_on': job_run.get('CompletedOn'),
                'execution_time': job_run.get('ExecutionTime'),
                'allocated_capacity': job_run.get('AllocatedCapacity'),
                'worker_type': job_run.get('WorkerType'),
                'number_of_workers': job_run.get('NumberOfWorkers'),
                'error_message': job_run.get('ErrorMessage'),
                'predecessor_runs': job_run.get('PredecessorRuns', [])
            }
            
        except Exception as e:
            logger.error(f"Error getting job run status: {str(e)}")
            return {}
    
    def create_step_function(self, state_machine_name: str, definition: Dict[str, Any]) -> Optional[str]:
        """Create Step Functions state machine."""
        try:
            # Validate definition
            self._validate_state_machine_definition(definition)
            
            # Create IAM role for Step Functions
            role_arn = self._create_step_functions_role(state_machine_name)
            
            # Create state machine
            response = self.stepfunctions_client.create_state_machine(
                name=state_machine_name,
                definition=json.dumps(definition),
                roleArn=role_arn,
                tags=[
                    {'key': 'Project', 'value': 'aws-data-analytics'},
                    {'key': 'Environment', 'value': 'production'}
                ]
            )
            
            state_machine_arn = response['stateMachineArn']
            logger.info(f"Step Functions state machine {state_machine_name} created successfully")
            return state_machine_arn
            
        except Exception as e:
            logger.error(f"Error creating Step Functions state machine: {str(e)}")
            return None
    
    def _validate_state_machine_definition(self, definition: Dict[str, Any]) -> None:
        """Validate state machine definition."""
        required_fields = ['Comment', 'StartAt', 'States']
        for field in required_fields:
            if field not in definition:
                raise ValueError(f"Missing required field in state machine definition: {field}")
    
    def _create_step_functions_role(self, state_machine_name: str) -> str:
        """Create IAM role for Step Functions."""
        role_name = f"{state_machine_name}-stepfunctions-role"
        
        try:
            # Check if role exists
            self.iam_client.get_role(RoleName=role_name)
            logger.info(f"Step Functions role {role_name} already exists")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
            
        except self.iam_client.exceptions.NoSuchEntityException:
            # Create role
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "states.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                Description=f"IAM role for {state_machine_name} Step Functions"
            )
            
            # Attach policies
            policies = [
                "arn:aws:iam::aws:policy/service-role/AWSStepFunctionsFullAccess"
            ]
            
            for policy_arn in policies:
                self.iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            logger.info(f"Created Step Functions role: {role_name}")
            return f"arn:aws:iam::{self._get_account_id()}:role/{role_name}"
    
    def start_step_function_execution(self, state_machine_arn: str, input_data: Dict[str, Any] = None) -> Optional[str]:
        """Start Step Functions execution."""
        try:
            execution_params = {
                'stateMachineArn': state_machine_arn
            }
            
            if input_data:
                execution_params['input'] = json.dumps(input_data)
            
            response = self.stepfunctions_client.start_execution(**execution_params)
            
            execution_arn = response['executionArn']
            logger.info(f"Step Functions execution started: {execution_arn}")
            return execution_arn
            
        except Exception as e:
            logger.error(f"Error starting Step Functions execution: {str(e)}")
            return None
    
    def get_execution_status(self, execution_arn: str) -> Dict[str, Any]:
        """Get Step Functions execution status."""
        try:
            response = self.stepfunctions_client.describe_execution(
                executionArn=execution_arn
            )
            
            return {
                'execution_arn': response['executionArn'],
                'state_machine_arn': response['stateMachineArn'],
                'status': response['status'],
                'start_date': response['startDate'],
                'stop_date': response.get('stopDate'),
                'input': response.get('input'),
                'output': response.get('output'),
                'error': response.get('error'),
                'cause': response.get('cause')
            }
            
        except Exception as e:
            logger.error(f"Error getting execution status: {str(e)}")
            return {}
    
    def create_etl_workflow(self, workflow_name: str, workflow_config: Dict[str, Any]) -> bool:
        """Create complete ETL workflow."""
        try:
            # Create Glue jobs
            glue_jobs = workflow_config.get('glue_jobs', [])
            job_arns = []
            
            for job_config in glue_jobs:
                job_name = f"{workflow_name}-{job_config['name']}"
                job_arn = self.create_glue_job(job_name, job_config)
                if job_arn:
                    job_arns.append(f"arn:aws:glue:{self.region}:{self._get_account_id()}:job/{job_name}")
            
            # Create Step Functions definition
            state_machine_definition = self._build_etl_state_machine(workflow_name, job_arns, workflow_config)
            
            # Create Step Functions state machine
            state_machine_arn = self.create_step_function(f"{workflow_name}-workflow", state_machine_definition)
            
            if state_machine_arn:
                logger.info(f"ETL workflow {workflow_name} created successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error creating ETL workflow: {str(e)}")
            return False
    
    def _build_etl_state_machine(self, workflow_name: str, job_arns: List[str], config: Dict[str, Any]) -> Dict[str, Any]:
        """Build ETL state machine definition."""
        states = {}
        
        # Add Glue job states
        for i, job_arn in enumerate(job_arns):
            job_name = f"job_{i+1}"
            states[job_name] = {
                "Type": "Task",
                "Resource": "arn:aws:states:::glue:startJobRun.sync",
                "Parameters": {
                    "JobName": job_arn.split('/')[-1]
                },
                "Next": f"job_{i+2}" if i < len(job_arns) - 1 else "Success"
            }
        
        # Add success state
        states["Success"] = {
            "Type": "Succeed"
        }
        
        # Add error handling
        states["Error"] = {
            "Type": "Fail",
            "Cause": "ETL workflow failed"
        }
        
        return {
            "Comment": f"ETL workflow for {workflow_name}",
            "StartAt": "job_1",
            "States": states
        }
    
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
    """Main function for testing ETLPipelineManager."""
    # Example usage
    etl_manager = ETLPipelineManager()
    
    # Example Glue job configuration
    job_config = {
        'script_location': 's3://my-bucket/scripts/etl_script.py',
        'command_name': 'glueetl',
        'python_version': '3',
        'max_capacity': 2.0,
        'worker_type': 'Standard',
        'number_of_workers': 2,
        'timeout': 2880,
        'default_arguments': {
            '--job-language': 'python',
            '--job-bookmark-option': 'job-bookmark-enable'
        },
        'description': 'Sample ETL job',
        'tags': {
            'Environment': 'production',
            'Project': 'data-analytics'
        }
    }
    
    # Create Glue job
    job_name = etl_manager.create_glue_job('sample-etl-job', job_config)
    if job_name:
        print(f"Glue job created: {job_name}")
        
        # Start job run
        job_run_id = etl_manager.start_glue_job(job_name)
        if job_run_id:
            print(f"Job run started: {job_run_id}")
            
            # Monitor job run
            import time
            while True:
                status = etl_manager.get_job_run_status(job_name, job_run_id)
                print(f"Job run status: {status.get('job_run_state')}")
                
                if status.get('job_run_state') in ['SUCCEEDED', 'FAILED', 'STOPPED']:
                    break
                
                time.sleep(30)


if __name__ == "__main__":
    main()