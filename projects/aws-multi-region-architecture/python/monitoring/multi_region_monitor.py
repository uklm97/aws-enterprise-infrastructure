#!/usr/bin/env python3
"""
AWS Multi-Region Monitor
Comprehensive monitoring and alerting across multiple AWS regions
"""

import boto3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from botocore.exceptions import ClientError
import pandas as pd


class MultiRegionMonitor:
    """Comprehensive multi-region monitoring and alerting"""
    
    def __init__(self, primary_region: str = 'us-east-1', monitored_regions: List[str] = None):
        self.primary_region = primary_region
        self.monitored_regions = monitored_regions or [
            'us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1', 'ap-northeast-1'
        ]
        
        # Initialize clients for all regions
        self.cloudwatch_clients = {}
        self.sns_clients = {}
        self.route53_clients = {}
        self.ec2_clients = {}
        self.rds_clients = {}
        self.s3_clients = {}
        self.lambda_clients = {}
        self.elasticache_clients = {}
        
        for region in self.monitored_regions:
            self.cloudwatch_clients[region] = boto3.client('cloudwatch', region_name=region)
            self.sns_clients[region] = boto3.client('sns', region_name=region)
            self.route53_clients[region] = boto3.client('route53', region_name=region)
            self.ec2_clients[region] = boto3.client('ec2', region_name=region)
            self.rds_clients[region] = boto3.client('rds', region_name=region)
            self.s3_clients[region] = boto3.client('s3', region_name=region)
            self.lambda_clients[region] = boto3.client('lambda', region_name=region)
            self.elasticache_clients[region] = boto3.client('elasticache', region_name=region)
    
    def create_global_dashboard(self, dashboard_config: Dict[str, Any]) -> Dict[str, str]:
        """Create global monitoring dashboard"""
        try:
            dashboards = {}
            
            for region in self.monitored_regions:
                dashboard_body = {
                    "widgets": [
                        {
                            "type": "metric",
                            "x": 0,
                            "y": 0,
                            "width": 12,
                            "height": 6,
                            "properties": {
                                "metrics": [
                                    ["AWS/EC2", "CPUUtilization", "InstanceId", "i-1234567890abcdef0"],
                                    [".", "NetworkIn", ".", "."],
                                    [".", "NetworkOut", ".", "."]
                                ],
                                "view": "timeSeries",
                                "stacked": False,
                                "region": region,
                                "title": f"EC2 Metrics - {region}",
                                "period": 300
                            }
                        },
                        {
                            "type": "metric",
                            "x": 0,
                            "y": 6,
                            "width": 12,
                            "height": 6,
                            "properties": {
                                "metrics": [
                                    ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "mydb"],
                                    [".", "DatabaseConnections", ".", "."],
                                    [".", "FreeableMemory", ".", "."]
                                ],
                                "view": "timeSeries",
                                "stacked": False,
                                "region": region,
                                "title": f"RDS Metrics - {region}",
                                "period": 300
                            }
                        },
                        {
                            "type": "metric",
                            "x": 0,
                            "y": 12,
                            "width": 12,
                            "height": 6,
                            "properties": {
                                "metrics": [
                                    ["AWS/S3", "BucketSizeBytes", "BucketName", "my-bucket", "StorageType", "StandardStorage"],
                                    [".", "NumberOfObjects", ".", ".", ".", "."]
                                ],
                                "view": "timeSeries",
                                "stacked": False,
                                "region": region,
                                "title": f"S3 Metrics - {region}",
                                "period": 300
                            }
                        }
                    ]
                }
                
                response = self.cloudwatch_clients[region].put_dashboard(
                    DashboardName=f"multi-region-dashboard-{region}",
                    DashboardBody=json.dumps(dashboard_body)
                )
                
                dashboards[region] = f"multi-region-dashboard-{region}"
            
            return dashboards
        except Exception as e:
            print(f"Error creating global dashboard: {e}")
            return {}
    
    def setup_global_alarms(self, alarm_config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Setup global CloudWatch alarms"""
        try:
            alarms = {}
            
            for region in self.monitored_regions:
                region_alarms = []
                
                # EC2 CPU alarm
                cpu_alarm = self.cloudwatch_clients[region].put_metric_alarm(
                    AlarmName=f"high-cpu-{region}",
                    ComparisonOperator='GreaterThanThreshold',
                    EvaluationPeriods=2,
                    MetricName='CPUUtilization',
                    Namespace='AWS/EC2',
                    Period=300,
                    Statistic='Average',
                    Threshold=80.0,
                    ActionsEnabled=True,
                    AlarmActions=[alarm_config['sns_topic_arn']],
                    AlarmDescription=f'High CPU utilization in {region}',
                    Dimensions=[
                        {
                            'Name': 'InstanceId',
                            'Value': alarm_config.get('instance_id', 'i-*')
                        }
                    ]
                )
                region_alarms.append('high-cpu')
                
                # RDS CPU alarm
                rds_alarm = self.cloudwatch_clients[region].put_metric_alarm(
                    AlarmName=f"high-rds-cpu-{region}",
                    ComparisonOperator='GreaterThanThreshold',
                    EvaluationPeriods=2,
                    MetricName='CPUUtilization',
                    Namespace='AWS/RDS',
                    Period=300,
                    Statistic='Average',
                    Threshold=80.0,
                    ActionsEnabled=True,
                    AlarmActions=[alarm_config['sns_topic_arn']],
                    AlarmDescription=f'High RDS CPU utilization in {region}',
                    Dimensions=[
                        {
                            'Name': 'DBInstanceIdentifier',
                            'Value': alarm_config.get('db_instance_id', 'mydb')
                        }
                    ]
                )
                region_alarms.append('high-rds-cpu')
                
                # Lambda error alarm
                lambda_alarm = self.cloudwatch_clients[region].put_metric_alarm(
                    AlarmName=f"lambda-errors-{region}",
                    ComparisonOperator='GreaterThanThreshold',
                    EvaluationPeriods=1,
                    MetricName='Errors',
                    Namespace='AWS/Lambda',
                    Period=300,
                    Statistic='Sum',
                    Threshold=0.0,
                    ActionsEnabled=True,
                    AlarmActions=[alarm_config['sns_topic_arn']],
                    AlarmDescription=f'Lambda errors in {region}',
                    Dimensions=[
                        {
                            'Name': 'FunctionName',
                            'Value': alarm_config.get('lambda_function_name', 'my-function')
                        }
                    ]
                )
                region_alarms.append('lambda-errors')
                
                # S3 bucket size alarm
                s3_alarm = self.cloudwatch_clients[region].put_metric_alarm(
                    AlarmName=f"s3-bucket-size-{region}",
                    ComparisonOperator='GreaterThanThreshold',
                    EvaluationPeriods=1,
                    MetricName='BucketSizeBytes',
                    Namespace='AWS/S3',
                    Period=86400,
                    Statistic='Average',
                    Threshold=1000000000000,  # 1TB
                    ActionsEnabled=True,
                    AlarmActions=[alarm_config['sns_topic_arn']],
                    AlarmDescription=f'Large S3 bucket size in {region}',
                    Dimensions=[
                        {
                            'Name': 'BucketName',
                            'Value': alarm_config.get('bucket_name', 'my-bucket')
                        },
                        {
                            'Name': 'StorageType',
                            'Value': 'StandardStorage'
                        }
                    ]
                )
                region_alarms.append('s3-bucket-size')
                
                alarms[region] = region_alarms
            
            return alarms
        except Exception as e:
            print(f"Error setting up global alarms: {e}")
            return {}
    
    def setup_health_checks(self, health_check_config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Setup global health checks"""
        try:
            health_checks = {}
            
            for region in self.monitored_regions:
                region_health_checks = []
                
                # HTTP health check
                http_check = self.route53_clients[region].create_health_check(
                    CallerReference=f"http-check-{region}-{int(time.time())}",
                    HealthCheckConfig={
                        'Type': 'HTTP',
                        'ResourcePath': health_check_config.get('resource_path', '/health'),
                        'FullyQualifiedDomainName': health_check_config['fqdn'],
                        'Port': health_check_config.get('port', 80),
                        'RequestInterval': health_check_config.get('request_interval', 30),
                        'FailureThreshold': health_check_config.get('failure_threshold', 3),
                        'EnableSNI': health_check_config.get('enable_sni', True)
                    }
                )
                region_health_checks.append(http_check['HealthCheck']['Id'])
                
                # HTTPS health check
                https_check = self.route53_clients[region].create_health_check(
                    CallerReference=f"https-check-{region}-{int(time.time())}",
                    HealthCheckConfig={
                        'Type': 'HTTPS',
                        'ResourcePath': health_check_config.get('resource_path', '/health'),
                        'FullyQualifiedDomainName': health_check_config['fqdn'],
                        'Port': health_check_config.get('port', 443),
                        'RequestInterval': health_check_config.get('request_interval', 30),
                        'FailureThreshold': health_check_config.get('failure_threshold', 3),
                        'EnableSNI': health_check_config.get('enable_sni', True)
                    }
                )
                region_health_checks.append(https_check['HealthCheck']['Id'])
                
                # TCP health check
                tcp_check = self.route53_clients[region].create_health_check(
                    CallerReference=f"tcp-check-{region}-{int(time.time())}",
                    HealthCheckConfig={
                        'Type': 'TCP',
                        'FullyQualifiedDomainName': health_check_config['fqdn'],
                        'Port': health_check_config.get('port', 80),
                        'RequestInterval': health_check_config.get('request_interval', 30),
                        'FailureThreshold': health_check_config.get('failure_threshold', 3)
                    }
                )
                region_health_checks.append(tcp_check['HealthCheck']['Id'])
                
                health_checks[region] = region_health_checks
            
            return health_checks
        except Exception as e:
            print(f"Error setting up health checks: {e}")
            return {}
    
    def setup_cross_region_alerting(self, alerting_config: Dict[str, Any]) -> Dict[str, str]:
        """Setup cross-region alerting"""
        try:
            sns_topics = {}
            
            for region in self.monitored_regions:
                # Create SNS topic for each region
                response = self.sns_clients[region].create_topic(
                    Name=f"multi-region-alerts-{region}"
                )
                
                sns_topics[region] = response['TopicArn']
                
                # Subscribe to email notifications
                if alerting_config.get('email_subscriptions'):
                    for email in alerting_config['email_subscriptions']:
                        self.sns_clients[region].subscribe(
                            TopicArn=response['TopicArn'],
                            Protocol='email',
                            Endpoint=email
                        )
                
                # Subscribe to SMS notifications
                if alerting_config.get('sms_subscriptions'):
                    for phone in alerting_config['sms_subscriptions']:
                        self.sns_clients[region].subscribe(
                            TopicArn=response['TopicArn'],
                            Protocol='sms',
                            Endpoint=phone
                        )
            
            return sns_topics
        except Exception as e:
            print(f"Error setting up cross-region alerting: {e}")
            return {}
    
    def get_global_metrics(self, metric_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get global metrics across all regions"""
        try:
            global_metrics = {
                'regions': {},
                'summary': {},
                'last_updated': datetime.now().isoformat()
            }
            
            for region in self.monitored_regions:
                region_metrics = {
                    'region': region,
                    'ec2_metrics': self._get_ec2_metrics(region, metric_config),
                    'rds_metrics': self._get_rds_metrics(region, metric_config),
                    's3_metrics': self._get_s3_metrics(region, metric_config),
                    'lambda_metrics': self._get_lambda_metrics(region, metric_config),
                    'elasticache_metrics': self._get_elasticache_metrics(region, metric_config)
                }
                global_metrics['regions'][region] = region_metrics
            
            # Calculate summary metrics
            global_metrics['summary'] = self._calculate_summary_metrics(global_metrics['regions'])
            
            return global_metrics
        except Exception as e:
            print(f"Error getting global metrics: {e}")
            return {}
    
    def get_region_health_status(self) -> Dict[str, Any]:
        """Get health status for all regions"""
        try:
            health_status = {
                'regions': {},
                'overall_status': 'HEALTHY',
                'last_updated': datetime.now().isoformat()
            }
            
            for region in self.monitored_regions:
                region_health = {
                    'region': region,
                    'status': 'HEALTHY',
                    'services': {},
                    'issues': []
                }
                
                # Check EC2 health
                try:
                    instances = self.ec2_clients[region].describe_instances()
                    running_instances = sum(1 for reservation in instances['Reservations'] 
                                          for instance in reservation['Instances'] 
                                          if instance['State']['Name'] == 'running')
                    region_health['services']['ec2'] = {
                        'status': 'HEALTHY',
                        'running_instances': running_instances
                    }
                except Exception as e:
                    region_health['services']['ec2'] = {
                        'status': 'UNHEALTHY',
                        'error': str(e)
                    }
                    region_health['issues'].append(f"EC2 error: {str(e)}")
                
                # Check RDS health
                try:
                    instances = self.rds_clients[region].describe_db_instances()
                    available_instances = sum(1 for instance in instances['DBInstances'] 
                                           if instance['DBInstanceStatus'] == 'available')
                    region_health['services']['rds'] = {
                        'status': 'HEALTHY',
                        'available_instances': available_instances
                    }
                except Exception as e:
                    region_health['services']['rds'] = {
                        'status': 'UNHEALTHY',
                        'error': str(e)
                    }
                    region_health['issues'].append(f"RDS error: {str(e)}")
                
                # Check S3 health
                try:
                    buckets = self.s3_clients[region].list_buckets()
                    region_health['services']['s3'] = {
                        'status': 'HEALTHY',
                        'bucket_count': len(buckets['Buckets'])
                    }
                except Exception as e:
                    region_health['services']['s3'] = {
                        'status': 'UNHEALTHY',
                        'error': str(e)
                    }
                    region_health['issues'].append(f"S3 error: {str(e)}")
                
                # Check Lambda health
                try:
                    functions = self.lambda_clients[region].list_functions()
                    region_health['services']['lambda'] = {
                        'status': 'HEALTHY',
                        'function_count': len(functions['Functions'])
                    }
                except Exception as e:
                    region_health['services']['lambda'] = {
                        'status': 'UNHEALTHY',
                        'error': str(e)
                    }
                    region_health['issues'].append(f"Lambda error: {str(e)}")
                
                # Determine region status
                unhealthy_services = [service for service in region_health['services'].values() 
                                    if service['status'] == 'UNHEALTHY']
                region_health['status'] = 'UNHEALTHY' if unhealthy_services else 'HEALTHY'
                
                health_status['regions'][region] = region_health
            
            # Determine overall status
            unhealthy_regions = [region for region in health_status['regions'].values() 
                               if region['status'] == 'UNHEALTHY']
            health_status['overall_status'] = 'UNHEALTHY' if unhealthy_regions else 'HEALTHY'
            
            return health_status
        except Exception as e:
            print(f"Error getting region health status: {e}")
            return {}
    
    def create_incident_response_plan(self, incident_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create incident response plan for multi-region"""
        try:
            incident_plan = {
                'plan_id': f"incident-plan-{int(time.time())}",
                'plan_name': incident_config.get('plan_name', 'Multi-Region Incident Response'),
                'severity_levels': incident_config.get('severity_levels', [
                    'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
                ]),
                'response_procedures': {},
                'escalation_matrix': {},
                'communication_channels': {},
                'created_at': datetime.now().isoformat()
            }
            
            # Define response procedures for each severity level
            for severity in incident_plan['severity_levels']:
                incident_plan['response_procedures'][severity] = {
                    'response_time_minutes': incident_config.get(f'{severity.lower()}_response_time', 15),
                    'escalation_time_minutes': incident_config.get(f'{severity.lower()}_escalation_time', 30),
                    'procedures': [
                        f"Assess impact in {severity} incident",
                        f"Notify {severity} response team",
                        f"Execute {severity} recovery procedures",
                        f"Monitor {severity} incident resolution"
                    ]
                }
            
            # Define escalation matrix
            incident_plan['escalation_matrix'] = {
                'L1': {
                    'team': 'On-Call Engineer',
                    'response_time': 15,
                    'escalation_to': 'L2'
                },
                'L2': {
                    'team': 'Senior Engineer',
                    'response_time': 30,
                    'escalation_to': 'L3'
                },
                'L3': {
                    'team': 'Engineering Manager',
                    'response_time': 60,
                    'escalation_to': 'L4'
                },
                'L4': {
                    'team': 'Director of Engineering',
                    'response_time': 120,
                    'escalation_to': None
                }
            }
            
            # Define communication channels
            incident_plan['communication_channels'] = {
                'internal': incident_config.get('internal_channels', ['slack', 'email']),
                'external': incident_config.get('external_channels', ['status_page', 'twitter']),
                'customers': incident_config.get('customer_channels', ['email', 'in_app'])
            }
            
            return incident_plan
        except Exception as e:
            print(f"Error creating incident response plan: {e}")
            return {}
    
    def _get_ec2_metrics(self, region: str, metric_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get EC2 metrics for region"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
            
            response = self.cloudwatch_clients[region].get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[
                    {
                        'Name': 'InstanceId',
                        'Value': metric_config.get('instance_id', 'i-*')
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average', 'Maximum']
            )
            
            return {
                'cpu_utilization': response['Datapoints'],
                'region': region
            }
        except Exception as e:
            print(f"Error getting EC2 metrics for {region}: {e}")
            return {}
    
    def _get_rds_metrics(self, region: str, metric_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get RDS metrics for region"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
            
            response = self.cloudwatch_clients[region].get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName='CPUUtilization',
                Dimensions=[
                    {
                        'Name': 'DBInstanceIdentifier',
                        'Value': metric_config.get('db_instance_id', 'mydb')
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average', 'Maximum']
            )
            
            return {
                'cpu_utilization': response['Datapoints'],
                'region': region
            }
        except Exception as e:
            print(f"Error getting RDS metrics for {region}: {e}")
            return {}
    
    def _get_s3_metrics(self, region: str, metric_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get S3 metrics for region"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
            
            response = self.cloudwatch_clients[region].get_metric_statistics(
                Namespace='AWS/S3',
                MetricName='BucketSizeBytes',
                Dimensions=[
                    {
                        'Name': 'BucketName',
                        'Value': metric_config.get('bucket_name', 'my-bucket')
                    },
                    {
                        'Name': 'StorageType',
                        'Value': 'StandardStorage'
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average', 'Maximum']
            )
            
            return {
                'bucket_size': response['Datapoints'],
                'region': region
            }
        except Exception as e:
            print(f"Error getting S3 metrics for {region}: {e}")
            return {}
    
    def _get_lambda_metrics(self, region: str, metric_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get Lambda metrics for region"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
            
            response = self.cloudwatch_clients[region].get_metric_statistics(
                Namespace='AWS/Lambda',
                MetricName='Invocations',
                Dimensions=[
                    {
                        'Name': 'FunctionName',
                        'Value': metric_config.get('lambda_function_name', 'my-function')
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Sum', 'Average']
            )
            
            return {
                'invocations': response['Datapoints'],
                'region': region
            }
        except Exception as e:
            print(f"Error getting Lambda metrics for {region}: {e}")
            return {}
    
    def _get_elasticache_metrics(self, region: str, metric_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get ElastiCache metrics for region"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
            
            response = self.cloudwatch_clients[region].get_metric_statistics(
                Namespace='AWS/ElastiCache',
                MetricName='CPUUtilization',
                Dimensions=[
                    {
                        'Name': 'CacheClusterId',
                        'Value': metric_config.get('cache_cluster_id', 'my-cache')
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average', 'Maximum']
            )
            
            return {
                'cpu_utilization': response['Datapoints'],
                'region': region
            }
        except Exception as e:
            print(f"Error getting ElastiCache metrics for {region}: {e}")
            return {}
    
    def _calculate_summary_metrics(self, regions: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary metrics across all regions"""
        try:
            summary = {
                'total_regions': len(regions),
                'healthy_regions': 0,
                'unhealthy_regions': 0,
                'average_cpu_utilization': 0.0,
                'total_instances': 0,
                'total_databases': 0,
                'total_functions': 0
            }
            
            cpu_values = []
            for region_data in regions.values():
                if 'ec2_metrics' in region_data and region_data['ec2_metrics']:
                    cpu_data = region_data['ec2_metrics'].get('cpu_utilization', [])
                    if cpu_data:
                        avg_cpu = sum(point['Average'] for point in cpu_data) / len(cpu_data)
                        cpu_values.append(avg_cpu)
                
                if 'rds_metrics' in region_data and region_data['rds_metrics']:
                    summary['total_databases'] += 1
                
                if 'lambda_metrics' in region_data and region_data['lambda_metrics']:
                    summary['total_functions'] += 1
            
            if cpu_values:
                summary['average_cpu_utilization'] = sum(cpu_values) / len(cpu_values)
            
            return summary
        except Exception as e:
            print(f"Error calculating summary metrics: {e}")
            return {}


# Example usage and testing
if __name__ == "__main__":
    # Initialize multi-region monitor
    monitor = MultiRegionMonitor(
        primary_region='us-east-1',
        monitored_regions=['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
    )
    
    # Create global dashboard
    dashboard_config = {
        'dashboard_name': 'multi-region-dashboard',
        'regions': ['us-east-1', 'us-west-2', 'eu-west-1']
    }
    dashboards = monitor.create_global_dashboard(dashboard_config)
    print(f"Created dashboards for {len(dashboards)} regions")
    
    # Setup global alarms
    alarm_config = {
        'sns_topic_arn': 'arn:aws:sns:region:account:alerts',
        'instance_id': 'i-1234567890abcdef0',
        'db_instance_id': 'mydb',
        'lambda_function_name': 'my-function',
        'bucket_name': 'my-bucket'
    }
    alarms = monitor.setup_global_alarms(alarm_config)
    print(f"Created alarms for {len(alarms)} regions")
    
    # Setup health checks
    health_config = {
        'fqdn': 'example.com',
        'resource_path': '/health',
        'port': 80,
        'request_interval': 30,
        'failure_threshold': 3
    }
    health_checks = monitor.setup_health_checks(health_config)
    print(f"Created health checks for {len(health_checks)} regions")
    
    # Get global metrics
    metric_config = {
        'instance_id': 'i-1234567890abcdef0',
        'db_instance_id': 'mydb',
        'bucket_name': 'my-bucket',
        'lambda_function_name': 'my-function',
        'cache_cluster_id': 'my-cache'
    }
    metrics = monitor.get_global_metrics(metric_config)
    print(f"Retrieved metrics for {len(metrics['regions'])} regions")
    
    # Get region health status
    health_status = monitor.get_region_health_status()
    print(f"Overall health status: {health_status['overall_status']}")
    
    # Create incident response plan
    incident_config = {
        'plan_name': 'Multi-Region Incident Response',
        'critical_response_time': 5,
        'high_response_time': 15,
        'medium_response_time': 30,
        'low_response_time': 60
    }
    incident_plan = monitor.create_incident_response_plan(incident_config)
    print(f"Created incident response plan: {incident_plan['plan_id']}")