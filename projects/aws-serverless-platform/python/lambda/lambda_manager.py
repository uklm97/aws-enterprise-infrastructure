#!/usr/bin/env python3
"""
AWS Lambda Manager
Comprehensive Lambda function management with deployment, monitoring, and optimization
"""

import boto3
import json
import zipfile
import os
import time
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError


class LambdaManager:
    """Manage AWS Lambda functions with comprehensive features"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=region)
        self.logs_client = boto3.client('logs', region_name=region)
        
    def create_function(self, function_config: Dict[str, Any]) -> Optional[str]:
        """Create a new Lambda function"""
        try:
            response = self.lambda_client.create_function(
                FunctionName=function_config['FunctionName'],
                Runtime=function_config.get('Runtime', 'python3.9'),
                Role=function_config['Role'],
                Handler=function_config.get('Handler', 'index.handler'),
                Code=function_config['Code'],
                Description=function_config.get('Description', ''),
                Timeout=function_config.get('Timeout', 3),
                MemorySize=function_config.get('MemorySize', 128),
                Environment=function_config.get('Environment', {}),
                VpcConfig=function_config.get('VpcConfig', {}),
                DeadLetterConfig=function_config.get('DeadLetterConfig', {}),
                TracingConfig=function_config.get('TracingConfig', {}),
                Tags=function_config.get('Tags', {})
            )
            return response['FunctionArn']
        except ClientError as e:
            print(f"Error creating function: {e}")
            return None
    
    def update_function_code(self, function_name: str, code_config: Dict[str, Any]) -> bool:
        """Update Lambda function code"""
        try:
            self.lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=code_config.get('ZipFile'),
                S3Bucket=code_config.get('S3Bucket'),
                S3Key=code_config.get('S3Key'),
                S3ObjectVersion=code_config.get('S3ObjectVersion'),
                Publish=code_config.get('Publish', False)
            )
            return True
        except ClientError as e:
            print(f"Error updating function code: {e}")
            return False
    
    def update_function_configuration(self, function_name: str, config: Dict[str, Any]) -> bool:
        """Update Lambda function configuration"""
        try:
            self.lambda_client.update_function_configuration(
                FunctionName=function_name,
                Role=config.get('Role'),
                Handler=config.get('Handler'),
                Description=config.get('Description'),
                Timeout=config.get('Timeout'),
                MemorySize=config.get('MemorySize'),
                Environment=config.get('Environment'),
                VpcConfig=config.get('VpcConfig'),
                DeadLetterConfig=config.get('DeadLetterConfig'),
                TracingConfig=config.get('TracingConfig')
            )
            return True
        except ClientError as e:
            print(f"Error updating function configuration: {e}")
            return False
    
    def invoke_function(self, function_name: str, payload: Dict[str, Any] = None, 
                       invocation_type: str = 'RequestResponse') -> Dict[str, Any]:
        """Invoke a Lambda function"""
        try:
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                InvocationType=invocation_type,
                Payload=json.dumps(payload) if payload else '{}'
            )
            
            result = {
                'StatusCode': response['StatusCode'],
                'Payload': json.loads(response['Payload'].read()),
                'ExecutedVersion': response.get('ExecutedVersion'),
                'LogResult': response.get('LogResult')
            }
            
            if 'LogResult' in response:
                result['Logs'] = self._decode_logs(response['LogResult'])
            
            return result
        except ClientError as e:
            print(f"Error invoking function: {e}")
            return {'StatusCode': 500, 'Payload': {'error': str(e)}}
    
    def create_deployment_package(self, source_dir: str, output_path: str) -> bool:
        """Create a deployment package (ZIP file) for Lambda"""
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        if file.endswith('.py') or file.endswith('.json'):
                            file_path = os.path.join(root, file)
                            arc_path = os.path.relpath(file_path, source_dir)
                            zip_file.write(file_path, arc_path)
            return True
        except Exception as e:
            print(f"Error creating deployment package: {e}")
            return False
    
    def create_lambda_role(self, role_name: str, policies: List[str] = None) -> Optional[str]:
        """Create IAM role for Lambda function"""
        try:
            # Default Lambda execution policy
            lambda_policy = {
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
                            "Principal": {"Service": "lambda.amazonaws.com"},
                            "Action": "sts:AssumeRole"
                        }
                    ]
                }),
                Description=f"IAM role for Lambda function {role_name}"
            )
            
            role_arn = response['Role']['Arn']
            
            # Attach basic execution policy
            self.iam_client.put_role_policy(
                RoleName=role_name,
                PolicyName='LambdaBasicExecution',
                PolicyDocument=json.dumps(lambda_policy)
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
            print(f"Error creating Lambda role: {e}")
            return None
    
    def create_event_source_mapping(self, function_name: str, event_source_config: Dict[str, Any]) -> bool:
        """Create event source mapping for Lambda"""
        try:
            self.lambda_client.create_event_source_mapping(
                EventSourceArn=event_source_config['EventSourceArn'],
                FunctionName=function_name,
                Enabled=event_source_config.get('Enabled', True),
                BatchSize=event_source_config.get('BatchSize', 10),
                StartingPosition=event_source_config.get('StartingPosition', 'LATEST'),
                MaximumBatchingWindowInSeconds=event_source_config.get('MaximumBatchingWindowInSeconds', 0)
            )
            return True
        except ClientError as e:
            print(f"Error creating event source mapping: {e}")
            return False
    
    def create_alias(self, function_name: str, alias_name: str, version: str = '$LATEST') -> bool:
        """Create function alias"""
        try:
            self.lambda_client.create_alias(
                FunctionName=function_name,
                Name=alias_name,
                FunctionVersion=version,
                Description=f"Alias {alias_name} for function {function_name}"
            )
            return True
        except ClientError as e:
            print(f"Error creating alias: {e}")
            return False
    
    def get_function_metrics(self, function_name: str, days: int = 7) -> Dict[str, Any]:
        """Get CloudWatch metrics for Lambda function"""
        try:
            end_time = time.time()
            start_time = end_time - (days * 24 * 60 * 60)
            
            metrics = {}
            
            # Get invocations
            invocations = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/Lambda',
                MetricName='Invocations',
                Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
                StartTime=time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(start_time)),
                EndTime=time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(end_time)),
                Period=3600,
                Statistics=['Sum']
            )
            metrics['Invocations'] = invocations['Datapoints']
            
            # Get errors
            errors = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/Lambda',
                MetricName='Errors',
                Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
                StartTime=time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(start_time)),
                EndTime=time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(end_time)),
                Period=3600,
                Statistics=['Sum']
            )
            metrics['Errors'] = errors['Datapoints']
            
            # Get duration
            duration = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/Lambda',
                MetricName='Duration',
                Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
                StartTime=time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(start_time)),
                EndTime=time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(end_time)),
                Period=3600,
                Statistics=['Average', 'Maximum']
            )
            metrics['Duration'] = duration['Datapoints']
            
            return metrics
        except ClientError as e:
            print(f"Error getting function metrics: {e}")
            return {}
    
    def get_function_logs(self, function_name: str, log_group_name: str = None) -> List[Dict[str, Any]]:
        """Get CloudWatch logs for Lambda function"""
        try:
            if not log_group_name:
                log_group_name = f"/aws/lambda/{function_name}"
            
            response = self.logs_client.describe_log_streams(
                logGroupName=log_group_name,
                orderBy='LastEventTime',
                descending=True,
                limit=10
            )
            
            logs = []
            for stream in response['logStreams']:
                log_events = self.logs_client.get_log_events(
                    logGroupName=log_group_name,
                    logStreamName=stream['logStreamName'],
                    limit=100
                )
                
                for event in log_events['events']:
                    logs.append({
                        'timestamp': event['timestamp'],
                        'message': event['message'],
                        'logStreamName': stream['logStreamName']
                    })
            
            return logs
        except ClientError as e:
            print(f"Error getting function logs: {e}")
            return []
    
    def optimize_function(self, function_name: str) -> Dict[str, Any]:
        """Analyze and provide optimization recommendations"""
        try:
            # Get function configuration
            function_config = self.lambda_client.get_function(FunctionName=function_name)
            config = function_config['Configuration']
            
            # Get metrics
            metrics = self.get_function_metrics(function_name)
            
            recommendations = []
            
            # Memory optimization
            current_memory = config['MemorySize']
            if current_memory < 1024:
                recommendations.append({
                    'type': 'memory',
                    'current': current_memory,
                    'recommended': 1024,
                    'reason': 'Increase memory for better performance'
                })
            
            # Timeout optimization
            current_timeout = config['Timeout']
            if current_timeout < 30:
                recommendations.append({
                    'type': 'timeout',
                    'current': current_timeout,
                    'recommended': 30,
                    'reason': 'Increase timeout to prevent early termination'
                })
            
            # Error rate analysis
            if metrics.get('Errors'):
                error_count = sum(point['Sum'] for point in metrics['Errors'])
                invocation_count = sum(point['Sum'] for point in metrics.get('Invocations', []))
                if invocation_count > 0:
                    error_rate = (error_count / invocation_count) * 100
                    if error_rate > 5:
                        recommendations.append({
                            'type': 'error_rate',
                            'current': f"{error_rate:.2f}%",
                            'recommended': '< 5%',
                            'reason': 'High error rate detected'
                        })
            
            return {
                'function_name': function_name,
                'current_config': {
                    'memory': current_memory,
                    'timeout': current_timeout,
                    'runtime': config['Runtime']
                },
                'recommendations': recommendations
            }
        except ClientError as e:
            print(f"Error optimizing function: {e}")
            return {}
    
    def delete_function(self, function_name: str) -> bool:
        """Delete Lambda function"""
        try:
            self.lambda_client.delete_function(FunctionName=function_name)
            return True
        except ClientError as e:
            print(f"Error deleting function: {e}")
            return False
    
    def list_functions(self, max_items: int = 50) -> List[Dict[str, Any]]:
        """List all Lambda functions"""
        try:
            response = self.lambda_client.list_functions(MaxItems=max_items)
            return response['Functions']
        except ClientError as e:
            print(f"Error listing functions: {e}")
            return []
    
    def _decode_logs(self, log_result: str) -> str:
        """Decode base64 encoded logs"""
        import base64
        try:
            return base64.b64decode(log_result).decode('utf-8')
        except Exception:
            return log_result


# Example usage and testing
if __name__ == "__main__":
    # Initialize Lambda manager
    lambda_manager = LambdaManager()
    
    # Example function configuration
    function_config = {
        'FunctionName': 'test-function',
        'Runtime': 'python3.9',
        'Role': 'arn:aws:iam::123456789012:role/lambda-execution-role',
        'Handler': 'index.handler',
        'Code': {
            'ZipFile': b'def handler(event, context): return {"statusCode": 200, "body": "Hello World"}'
        },
        'Description': 'Test Lambda function',
        'Timeout': 30,
        'MemorySize': 256
    }
    
    # Create function
    function_arn = lambda_manager.create_function(function_config)
    if function_arn:
        print(f"Function created: {function_arn}")
        
        # Invoke function
        result = lambda_manager.invoke_function('test-function', {'test': 'data'})
        print(f"Invocation result: {result}")
        
        # Get metrics
        metrics = lambda_manager.get_function_metrics('test-function')
        print(f"Function metrics: {metrics}")
        
        # Optimize function
        optimization = lambda_manager.optimize_function('test-function')
        print(f"Optimization recommendations: {optimization}")