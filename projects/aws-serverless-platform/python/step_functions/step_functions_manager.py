#!/usr/bin/env python3
"""
AWS Step Functions Manager
Comprehensive Step Functions management with state machines, executions, and monitoring
"""

import boto3
import json
import time
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError


class StepFunctionsManager:
    """Manage AWS Step Functions with comprehensive features"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.stepfunctions_client = boto3.client('stepfunctions', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=region)
        self.logs_client = boto3.client('logs', region_name=region)
        
    def create_state_machine(self, state_machine_config: Dict[str, Any]) -> Optional[str]:
        """Create Step Functions state machine"""
        try:
            response = self.stepfunctions_client.create_state_machine(
                name=state_machine_config['name'],
                definition=json.dumps(state_machine_config['definition']),
                roleArn=state_machine_config['roleArn'],
                type=state_machine_config.get('type', 'STANDARD'),
                loggingConfiguration=state_machine_config.get('loggingConfiguration', {}),
                tags=state_machine_config.get('tags', [])
            )
            return response['stateMachineArn']
        except ClientError as e:
            print(f"Error creating state machine: {e}")
            return None
    
    def update_state_machine(self, state_machine_arn: str, 
                            definition: Dict[str, Any], role_arn: str = None) -> bool:
        """Update state machine definition"""
        try:
            update_params = {
                'stateMachineArn': state_machine_arn,
                'definition': json.dumps(definition)
            }
            
            if role_arn:
                update_params['roleArn'] = role_arn
            
            self.stepfunctions_client.update_state_machine(**update_params)
            return True
        except ClientError as e:
            print(f"Error updating state machine: {e}")
            return False
    
    def start_execution(self, state_machine_arn: str, name: str = None,
                       input_data: Dict[str, Any] = None) -> Optional[str]:
        """Start state machine execution"""
        try:
            execution_params = {
                'stateMachineArn': state_machine_arn
            }
            
            if name:
                execution_params['name'] = name
            
            if input_data:
                execution_params['input'] = json.dumps(input_data)
            
            response = self.stepfunctions_client.start_execution(**execution_params)
            return response['executionArn']
        except ClientError as e:
            print(f"Error starting execution: {e}")
            return None
    
    def stop_execution(self, execution_arn: str, cause: str = None, error: str = None) -> bool:
        """Stop state machine execution"""
        try:
            stop_params = {
                'executionArn': execution_arn
            }
            
            if cause:
                stop_params['cause'] = cause
            
            if error:
                stop_params['error'] = error
            
            self.stepfunctions_client.stop_execution(**stop_params)
            return True
        except ClientError as e:
            print(f"Error stopping execution: {e}")
            return False
    
    def get_execution_status(self, execution_arn: str) -> Dict[str, Any]:
        """Get execution status and details"""
        try:
            response = self.stepfunctions_client.describe_execution(
                executionArn=execution_arn
            )
            
            return {
                'executionArn': response['executionArn'],
                'stateMachineArn': response['stateMachineArn'],
                'name': response['name'],
                'status': response['status'],
                'startDate': response['startDate'],
                'stopDate': response.get('stopDate'),
                'input': response.get('input'),
                'output': response.get('output'),
                'error': response.get('error'),
                'cause': response.get('cause')
            }
        except ClientError as e:
            print(f"Error getting execution status: {e}")
            return {}
    
    def list_executions(self, state_machine_arn: str = None, status_filter: str = None,
                       max_results: int = 100) -> List[Dict[str, Any]]:
        """List executions"""
        try:
            list_params = {}
            
            if state_machine_arn:
                list_params['stateMachineArn'] = state_machine_arn
            
            if status_filter:
                list_params['statusFilter'] = status_filter
            
            if max_results:
                list_params['maxResults'] = max_results
            
            response = self.stepfunctions_client.list_executions(**list_params)
            return response['executions']
        except ClientError as e:
            print(f"Error listing executions: {e}")
            return []
    
    def get_execution_history(self, execution_arn: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Get execution history"""
        try:
            response = self.stepfunctions_client.get_execution_history(
                executionArn=execution_arn,
                maxResults=max_results
            )
            return response['events']
        except ClientError as e:
            print(f"Error getting execution history: {e}")
            return []
    
    def create_express_state_machine(self, state_machine_config: Dict[str, Any]) -> Optional[str]:
        """Create Express state machine"""
        try:
            response = self.stepfunctions_client.create_state_machine(
                name=state_machine_config['name'],
                definition=json.dumps(state_machine_config['definition']),
                roleArn=state_machine_config['roleArn'],
                type='EXPRESS',
                loggingConfiguration=state_machine_config.get('loggingConfiguration', {}),
                tags=state_machine_config.get('tags', [])
            )
            return response['stateMachineArn']
        except ClientError as e:
            print(f"Error creating Express state machine: {e}")
            return None
    
    def start_sync_execution(self, state_machine_arn: str, name: str = None,
                            input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Start synchronous execution (Express only)"""
        try:
            execution_params = {
                'stateMachineArn': state_machine_arn
            }
            
            if name:
                execution_params['name'] = name
            
            if input_data:
                execution_params['input'] = json.dumps(input_data)
            
            response = self.stepfunctions_client.start_sync_execution(**execution_params)
            
            return {
                'executionArn': response['executionArn'],
                'stateMachineArn': response['stateMachineArn'],
                'name': response['name'],
                'status': response['status'],
                'startDate': response['startDate'],
                'stopDate': response['stopDate'],
                'input': response['input'],
                'output': response['output'],
                'billingDetails': response.get('billingDetails', {}),
                'error': response.get('error'),
                'cause': response.get('cause')
            }
        except ClientError as e:
            print(f"Error starting sync execution: {e}")
            return {}
    
    def create_activity(self, activity_config: Dict[str, Any]) -> Optional[str]:
        """Create activity"""
        try:
            response = self.stepfunctions_client.create_activity(
                name=activity_config['name'],
                tags=activity_config.get('tags', [])
            )
            return response['activityArn']
        except ClientError as e:
            print(f"Error creating activity: {e}")
            return None
    
    def get_activity_task(self, activity_arn: str, worker_name: str = None) -> Dict[str, Any]:
        """Get activity task"""
        try:
            get_task_params = {
                'activityArn': activity_arn
            }
            
            if worker_name:
                get_task_params['workerName'] = worker_name
            
            response = self.stepfunctions_client.get_activity_task(**get_task_params)
            
            if 'taskToken' in response:
                return {
                    'taskToken': response['taskToken'],
                    'input': response['input']
                }
            return {}
        except ClientError as e:
            print(f"Error getting activity task: {e}")
            return {}
    
    def send_task_success(self, task_token: str, output: Dict[str, Any]) -> bool:
        """Send task success"""
        try:
            self.stepfunctions_client.send_task_success(
                taskToken=task_token,
                output=json.dumps(output)
            )
            return True
        except ClientError as e:
            print(f"Error sending task success: {e}")
            return False
    
    def send_task_failure(self, task_token: str, error: str = None, cause: str = None) -> bool:
        """Send task failure"""
        try:
            failure_params = {
                'taskToken': task_token
            }
            
            if error:
                failure_params['error'] = error
            
            if cause:
                failure_params['cause'] = cause
            
            self.stepfunctions_client.send_task_failure(**failure_params)
            return True
        except ClientError as e:
            print(f"Error sending task failure: {e}")
            return False
    
    def send_task_heartbeat(self, task_token: str) -> bool:
        """Send task heartbeat"""
        try:
            self.stepfunctions_client.send_task_heartbeat(
                taskToken=task_token
            )
            return True
        except ClientError as e:
            print(f"Error sending task heartbeat: {e}")
            return False
    
    def create_state_machine_role(self, role_name: str, policies: List[str] = None) -> Optional[str]:
        """Create IAM role for Step Functions"""
        try:
            # Default Step Functions execution policy
            stepfunctions_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents"
                        ],
                        "Resource": "arn:aws:logs:*:*:*"
                    }
                ]
            }
            
            # Create role
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"Service": "states.amazonaws.com"},
                            "Action": "sts:AssumeRole"
                        }
                    ]
                }),
                Description=f"IAM role for Step Functions {role_name}"
            )
            
            role_arn = response['Role']['Arn']
            
            # Attach basic execution policy
            self.iam_client.put_role_policy(
                RoleName=role_name,
                PolicyName='StepFunctionsBasicExecution',
                PolicyDocument=json.dumps(stepfunctions_policy)
            )
            
            # Attach additional policies
            if policies:
                for i, policy in enumerate(policies):
                    self.iam_client.put_role_policy(
                        RoleName=role_name,
                        PolicyName=f'CustomPolicy{i+1}',
                        PolicyDocument=policy
                    )
            
            return role_arn
        except ClientError as e:
            print(f"Error creating Step Functions role: {e}")
            return None
    
    def get_state_machine_metrics(self, state_machine_arn: str, days: int = 7) -> Dict[str, Any]:
        """Get state machine CloudWatch metrics"""
        try:
            import time
            from datetime import datetime, timedelta
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            metrics = {}
            
            # Get executions started
            executions_started = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/States',
                MetricName='ExecutionsStarted',
                Dimensions=[
                    {'Name': 'StateMachineArn', 'Value': state_machine_arn}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            metrics['ExecutionsStarted'] = executions_started['Datapoints']
            
            # Get executions succeeded
            executions_succeeded = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/States',
                MetricName='ExecutionsSucceeded',
                Dimensions=[
                    {'Name': 'StateMachineArn', 'Value': state_machine_arn}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            metrics['ExecutionsSucceeded'] = executions_succeeded['Datapoints']
            
            # Get executions failed
            executions_failed = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/States',
                MetricName='ExecutionsFailed',
                Dimensions=[
                    {'Name': 'StateMachineArn', 'Value': state_machine_arn}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            metrics['ExecutionsFailed'] = executions_failed['Datapoints']
            
            # Get execution time
            execution_time = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/States',
                MetricName='ExecutionTime',
                Dimensions=[
                    {'Name': 'StateMachineArn', 'Value': state_machine_arn}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Average', 'Maximum']
            )
            metrics['ExecutionTime'] = execution_time['Datapoints']
            
            return metrics
        except ClientError as e:
            print(f"Error getting state machine metrics: {e}")
            return {}
    
    def create_cloudwatch_dashboard(self, dashboard_name: str, 
                                   state_machine_arns: List[str]) -> bool:
        """Create CloudWatch dashboard for Step Functions"""
        try:
            dashboard_body = {
                "widgets": []
            }
            
            for i, state_machine_arn in enumerate(state_machine_arns):
                # Executions widget
                executions_widget = {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            ["AWS/States", "ExecutionsStarted", "StateMachineArn", state_machine_arn],
                            [".", "ExecutionsSucceeded", ".", "."],
                            [".", "ExecutionsFailed", ".", "."]
                        ],
                        "period": 300,
                        "stat": "Sum",
                        "region": self.region,
                        "title": f"Executions - {state_machine_arn.split('/')[-1]}",
                        "yAxis": {
                            "left": {
                                "min": 0
                            }
                        }
                    }
                }
                
                # Execution time widget
                execution_time_widget = {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            ["AWS/States", "ExecutionTime", "StateMachineArn", state_machine_arn]
                        ],
                        "period": 300,
                        "stat": "Average",
                        "region": self.region,
                        "title": f"Execution Time - {state_machine_arn.split('/')[-1]}",
                        "yAxis": {
                            "left": {
                                "min": 0
                            }
                        }
                    }
                }
                
                dashboard_body["widgets"].extend([executions_widget, execution_time_widget])
            
            self.cloudwatch_client.put_dashboard(
                DashboardName=dashboard_name,
                DashboardBody=json.dumps(dashboard_body)
            )
            return True
        except ClientError as e:
            print(f"Error creating CloudWatch dashboard: {e}")
            return False
    
    def delete_state_machine(self, state_machine_arn: str) -> bool:
        """Delete state machine"""
        try:
            self.stepfunctions_client.delete_state_machine(
                stateMachineArn=state_machine_arn
            )
            return True
        except ClientError as e:
            print(f"Error deleting state machine: {e}")
            return False
    
    def list_state_machines(self) -> List[Dict[str, Any]]:
        """List all state machines"""
        try:
            response = self.stepfunctions_client.list_state_machines()
            return response['stateMachines']
        except ClientError as e:
            print(f"Error listing state machines: {e}")
            return []


# Example usage and testing
if __name__ == "__main__":
    # Initialize Step Functions manager
    stepfunctions_manager = StepFunctionsManager()
    
    # Example state machine definition
    state_machine_definition = {
        "Comment": "A simple example state machine",
        "StartAt": "HelloWorld",
        "States": {
            "HelloWorld": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:us-east-1:123456789012:function:HelloWorld",
                "End": True
            }
        }
    }
    
    # Example state machine configuration
    state_machine_config = {
        'name': 'test-state-machine',
        'definition': state_machine_definition,
        'roleArn': 'arn:aws:iam::123456789012:role/StepFunctionsExecutionRole',
        'type': 'STANDARD'
    }
    
    # Create state machine
    state_machine_arn = stepfunctions_manager.create_state_machine(state_machine_config)
    if state_machine_arn:
        print(f"State machine created: {state_machine_arn}")
        
        # Start execution
        execution_arn = stepfunctions_manager.start_execution(
            state_machine_arn, 
            'test-execution',
            {'input': 'test data'}
        )
        if execution_arn:
            print(f"Execution started: {execution_arn}")
            
            # Get execution status
            status = stepfunctions_manager.get_execution_status(execution_arn)
            print(f"Execution status: {status}")
            
            # Get metrics
            metrics = stepfunctions_manager.get_state_machine_metrics(state_machine_arn)
            print(f"State machine metrics: {metrics}")