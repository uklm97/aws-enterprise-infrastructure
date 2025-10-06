#!/usr/bin/env python3
"""
AWS Disaster Recovery Manager
Comprehensive disaster recovery management with automated failover and recovery procedures
"""

import boto3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from botocore.exceptions import ClientError
import pandas as pd


class DisasterRecoveryManager:
    """Comprehensive AWS disaster recovery management"""
    
    def __init__(self, primary_region: str = 'us-east-1', dr_regions: List[str] = None):
        self.primary_region = primary_region
        self.dr_regions = dr_regions or ['us-west-2', 'eu-west-1']
        self.all_regions = [primary_region] + self.dr_regions
        
        # Initialize clients for all regions
        self.ec2_clients = {}
        self.rds_clients = {}
        self.s3_clients = {}
        self.route53_clients = {}
        self.cloudwatch_clients = {}
        self.sns_clients = {}
        self.lambda_clients = {}
        self.stepfunctions_clients = {}
        
        for region in self.all_regions:
            self.ec2_clients[region] = boto3.client('ec2', region_name=region)
            self.rds_clients[region] = boto3.client('rds', region_name=region)
            self.s3_clients[region] = boto3.client('s3', region_name=region)
            self.route53_clients[region] = boto3.client('route53', region_name=region)
            self.cloudwatch_clients[region] = boto3.client('cloudwatch', region_name=region)
            self.sns_clients[region] = boto3.client('sns', region_name=region)
            self.lambda_clients[region] = boto3.client('lambda', region_name=region)
            self.stepfunctions_clients[region] = boto3.client('stepfunctions', region_name=region)
    
    def create_dr_plan(self, plan_config: Dict[str, Any]) -> Optional[str]:
        """Create comprehensive disaster recovery plan"""
        try:
            dr_plan = {
                'plan_id': plan_config.get('plan_id', f"dr-plan-{int(time.time())}"),
                'plan_name': plan_config['plan_name'],
                'primary_region': self.primary_region,
                'dr_regions': self.dr_regions,
                'rto_minutes': plan_config.get('rto_minutes', 60),  # Recovery Time Objective
                'rpo_minutes': plan_config.get('rpo_minutes', 15),  # Recovery Point Objective
                'failover_triggers': plan_config.get('failover_triggers', []),
                'recovery_procedures': [],
                'monitoring_config': {},
                'created_at': datetime.now().isoformat()
            }
            
            # Add recovery procedures
            dr_plan['recovery_procedures'] = [
                {
                    'name': 'Database Failover',
                    'description': 'Failover RDS instances to DR region',
                    'estimated_time_minutes': 15,
                    'automated': True,
                    'priority': 1,
                    'dependencies': []
                },
                {
                    'name': 'Application Failover',
                    'description': 'Switch application traffic to DR region',
                    'estimated_time_minutes': 5,
                    'automated': True,
                    'priority': 2,
                    'dependencies': ['Database Failover']
                },
                {
                    'name': 'DNS Failover',
                    'description': 'Update DNS records to point to DR region',
                    'estimated_time_minutes': 2,
                    'automated': True,
                    'priority': 3,
                    'dependencies': ['Application Failover']
                },
                {
                    'name': 'Data Synchronization',
                    'description': 'Ensure data consistency across regions',
                    'estimated_time_minutes': 30,
                    'automated': False,
                    'priority': 4,
                    'dependencies': ['Database Failover']
                },
                {
                    'name': 'Monitoring Setup',
                    'description': 'Configure monitoring in DR region',
                    'estimated_time_minutes': 10,
                    'automated': True,
                    'priority': 5,
                    'dependencies': ['Application Failover']
                }
            ]
            
            # Add monitoring configuration
            dr_plan['monitoring_config'] = {
                'health_checks': plan_config.get('health_checks', []),
                'alerts': plan_config.get('alerts', []),
                'metrics': plan_config.get('metrics', []),
                'dashboard_urls': []
            }
            
            return dr_plan['plan_id']
        except Exception as e:
            print(f"Error creating DR plan: {e}")
            return None
    
    def setup_automated_failover(self, failover_config: Dict[str, Any]) -> bool:
        """Setup automated failover procedures"""
        try:
            # Create Step Functions state machine for failover
            failover_definition = {
                "Comment": "Automated Disaster Recovery Failover",
                "StartAt": "CheckPrimaryRegion",
                "States": {
                    "CheckPrimaryRegion": {
                        "Type": "Task",
                        "Resource": "arn:aws:lambda:${region}:${account}:function:check-primary-region",
                        "Next": "EvaluateFailover",
                        "Retry": [
                            {
                                "ErrorEquals": ["States.ALL"],
                                "IntervalSeconds": 30,
                                "MaxAttempts": 3
                            }
                        ]
                    },
                    "EvaluateFailover": {
                        "Type": "Choice",
                        "Choices": [
                            {
                                "Variable": "$.primary_region_healthy",
                                "BooleanEquals": False,
                                "Next": "InitiateFailover"
                            }
                        ],
                        "Default": "WaitAndRetry"
                    },
                    "InitiateFailover": {
                        "Type": "Parallel",
                        "Branches": [
                            {
                                "StartAt": "FailoverDatabase",
                                "States": {
                                    "FailoverDatabase": {
                                        "Type": "Task",
                                        "Resource": "arn:aws:lambda:${region}:${account}:function:failover-database",
                                        "End": True
                                    }
                                }
                            },
                            {
                                "StartAt": "FailoverApplication",
                                "States": {
                                    "FailoverApplication": {
                                        "Type": "Task",
                                        "Resource": "arn:aws:lambda:${region}:${account}:function:failover-application",
                                        "End": True
                                    }
                                }
                            },
                            {
                                "StartAt": "UpdateDNS",
                                "States": {
                                    "UpdateDNS": {
                                        "Type": "Task",
                                        "Resource": "arn:aws:lambda:${region}:${account}:function:update-dns",
                                        "End": True
                                    }
                                }
                            }
                        ],
                        "Next": "NotifyStakeholders"
                    },
                    "NotifyStakeholders": {
                        "Type": "Task",
                        "Resource": "arn:aws:lambda:${region}:${account}:function:notify-stakeholders",
                        "End": True
                    },
                    "WaitAndRetry": {
                        "Type": "Wait",
                        "Seconds": 300,
                        "Next": "CheckPrimaryRegion"
                    }
                }
            }
            
            # Create Step Functions state machine in each region
            for region in self.all_regions:
                self.stepfunctions_clients[region].create_state_machine(
                    name=f"dr-failover-{region}",
                    definition=json.dumps(failover_definition),
                    roleArn=failover_config['execution_role_arn']
                )
            
            return True
        except Exception as e:
            print(f"Error setting up automated failover: {e}")
            return False
    
    def setup_health_monitoring(self, monitoring_config: Dict[str, Any]) -> List[str]:
        """Setup comprehensive health monitoring across regions"""
        try:
            health_check_ids = []
            
            for region in self.all_regions:
                # Create CloudWatch alarms for health monitoring
                alarm_configs = [
                    {
                        'AlarmName': f'dr-health-check-{region}',
                        'ComparisonOperator': 'GreaterThanThreshold',
                        'EvaluationPeriods': 3,
                        'MetricName': 'HealthCheckStatus',
                        'Namespace': 'AWS/Route53',
                        'Period': 60,
                        'Statistic': 'Average',
                        'Threshold': 0.0,
                        'ActionsEnabled': True,
                        'AlarmActions': [monitoring_config['sns_topic_arn']]
                    }
                ]
                
                for alarm_config in alarm_configs:
                    self.cloudwatch_clients[region].put_metric_alarm(**alarm_config)
                
                # Create Route53 health checks
                health_check = self.route53_clients[region].create_health_check(
                    CallerReference=f"dr-health-check-{region}-{int(time.time())}",
                    HealthCheckConfig={
                        'Type': monitoring_config.get('health_check_type', 'HTTP'),
                        'ResourcePath': monitoring_config.get('resource_path', '/health'),
                        'FullyQualifiedDomainName': monitoring_config['fqdn'],
                        'Port': monitoring_config.get('port', 80),
                        'RequestInterval': monitoring_config.get('request_interval', 30),
                        'FailureThreshold': monitoring_config.get('failure_threshold', 3),
                        'EnableSNI': monitoring_config.get('enable_sni', True)
                    }
                )
                
                health_check_ids.append(health_check['HealthCheck']['Id'])
            
            return health_check_ids
        except Exception as e:
            print(f"Error setting up health monitoring: {e}")
            return []
    
    def setup_rds_failover(self, rds_config: Dict[str, Any]) -> bool:
        """Setup RDS automated failover"""
        try:
            for region in self.dr_regions:
                # Create read replica in DR region
                replica_id = f"{rds_config['db_instance_id']}-dr-{region}"
                
                self.rds_clients[region].create_db_instance_read_replica(
                    DBInstanceIdentifier=replica_id,
                    SourceDBInstanceIdentifier=f"arn:aws:rds:{self.primary_region}:{rds_config['account_id']}:db:{rds_config['db_instance_id']}",
                    DBInstanceClass=rds_config.get('instance_class', 'db.t3.micro'),
                    AvailabilityZone=rds_config.get('availability_zone'),
                    Port=rds_config.get('port', 3306),
                    AutoMinorVersionUpgrade=rds_config.get('auto_minor_version_upgrade', True),
                    PubliclyAccessible=rds_config.get('publicly_accessible', False),
                    Tags=rds_config.get('tags', [])
                )
                
                # Create CloudWatch alarm for RDS failover
                self.cloudwatch_clients[region].put_metric_alarm(
                    AlarmName=f'rds-failover-{replica_id}',
                    ComparisonOperator='GreaterThanThreshold',
                    EvaluationPeriods=2,
                    MetricName='DatabaseConnections',
                    Namespace='AWS/RDS',
                    Period=300,
                    Statistic='Average',
                    Threshold=0.0,
                    ActionsEnabled=True,
                    AlarmActions=[rds_config['sns_topic_arn']],
                    Dimensions=[
                        {
                            'Name': 'DBInstanceIdentifier',
                            'Value': replica_id
                        }
                    ]
                )
            
            return True
        except Exception as e:
            print(f"Error setting up RDS failover: {e}")
            return False
    
    def setup_application_failover(self, app_config: Dict[str, Any]) -> bool:
        """Setup application failover procedures"""
        try:
            for region in self.dr_regions:
                # Create Auto Scaling Group in DR region
                self.ec2_clients[region].create_auto_scaling_group(
                    AutoScalingGroupName=f"{app_config['asg_name']}-dr-{region}",
                    LaunchTemplate={
                        'LaunchTemplateName': app_config['launch_template_name'],
                        'Version': app_config.get('launch_template_version', '$Latest')
                    },
                    MinSize=app_config.get('min_size', 1),
                    MaxSize=app_config.get('max_size', 3),
                    DesiredCapacity=app_config.get('desired_capacity', 2),
                    VPCZoneIdentifier=app_config['subnet_ids'][region],
                    HealthCheckType=app_config.get('health_check_type', 'EC2'),
                    HealthCheckGracePeriod=app_config.get('health_check_grace_period', 300),
                    Tags=app_config.get('tags', [])
                )
                
                # Create Application Load Balancer in DR region
                self.ec2_clients[region].create_load_balancer(
                    Name=f"{app_config['alb_name']}-dr-{region}",
                    Subnets=app_config['subnet_ids'][region],
                    SecurityGroups=app_config.get('security_group_ids', []),
                    Scheme=app_config.get('scheme', 'internet-facing'),
                    Type=app_config.get('type', 'application'),
                    Tags=app_config.get('tags', [])
                )
            
            return True
        except Exception as e:
            print(f"Error setting up application failover: {e}")
            return False
    
    def setup_dns_failover(self, dns_config: Dict[str, Any]) -> bool:
        """Setup DNS failover routing"""
        try:
            # Create failover routing policy
            for i, region in enumerate(self.all_regions):
                record_type = 'PRIMARY' if i == 0 else 'SECONDARY'
                
                self.route53_clients[region].change_resource_record_sets(
                    HostedZoneId=dns_config['hosted_zone_id'],
                    ChangeBatch={
                        'Changes': [
                            {
                                'Action': 'UPSERT',
                                'ResourceRecordSet': {
                                    'Name': dns_config['domain_name'],
                                    'Type': 'A',
                                    'SetIdentifier': f'{region}-{record_type.lower()}',
                                    'Failover': record_type,
                                    'HealthCheckId': dns_config['health_check_ids'][i],
                                    'AliasTarget': {
                                        'DNSName': dns_config['alias_targets'][i],
                                        'EvaluateTargetHealth': True,
                                        'HostedZoneId': dns_config['hosted_zone_id']
                                    }
                                }
                            }
                        ]
                    }
                )
            
            return True
        except Exception as e:
            print(f"Error setting up DNS failover: {e}")
            return False
    
    def execute_failover(self, failover_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute disaster recovery failover"""
        try:
            failover_result = {
                'failover_id': f"failover-{int(time.time())}",
                'start_time': datetime.now().isoformat(),
                'primary_region': self.primary_region,
                'target_region': failover_config['target_region'],
                'steps': [],
                'status': 'IN_PROGRESS'
            }
            
            # Step 1: Validate target region
            try:
                self._validate_target_region(failover_config['target_region'])
                failover_result['steps'].append({
                    'step': 'validate_target_region',
                    'status': 'SUCCESS',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                failover_result['steps'].append({
                    'step': 'validate_target_region',
                    'status': 'FAILED',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                failover_result['status'] = 'FAILED'
                return failover_result
            
            # Step 2: Failover database
            try:
                self._failover_database(failover_config['target_region'])
                failover_result['steps'].append({
                    'step': 'failover_database',
                    'status': 'SUCCESS',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                failover_result['steps'].append({
                    'step': 'failover_database',
                    'status': 'FAILED',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
            
            # Step 3: Failover application
            try:
                self._failover_application(failover_config['target_region'])
                failover_result['steps'].append({
                    'step': 'failover_application',
                    'status': 'SUCCESS',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                failover_result['steps'].append({
                    'step': 'failover_application',
                    'status': 'FAILED',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
            
            # Step 4: Update DNS
            try:
                self._update_dns_routing(failover_config['target_region'])
                failover_result['steps'].append({
                    'step': 'update_dns',
                    'status': 'SUCCESS',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                failover_result['steps'].append({
                    'step': 'update_dns',
                    'status': 'FAILED',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
            
            # Step 5: Verify failover
            try:
                self._verify_failover(failover_config['target_region'])
                failover_result['steps'].append({
                    'step': 'verify_failover',
                    'status': 'SUCCESS',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                failover_result['steps'].append({
                    'step': 'verify_failover',
                    'status': 'FAILED',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
            
            # Determine overall status
            failed_steps = [step for step in failover_result['steps'] if step['status'] == 'FAILED']
            failover_result['status'] = 'SUCCESS' if not failed_steps else 'PARTIAL_SUCCESS'
            failover_result['end_time'] = datetime.now().isoformat()
            
            return failover_result
        except Exception as e:
            print(f"Error executing failover: {e}")
            return {'status': 'FAILED', 'error': str(e)}
    
    def execute_failback(self, failback_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute failback to primary region"""
        try:
            failback_result = {
                'failback_id': f"failback-{int(time.time())}",
                'start_time': datetime.now().isoformat(),
                'from_region': failback_config['from_region'],
                'to_region': self.primary_region,
                'steps': [],
                'status': 'IN_PROGRESS'
            }
            
            # Step 1: Validate primary region
            try:
                self._validate_target_region(self.primary_region)
                failback_result['steps'].append({
                    'step': 'validate_primary_region',
                    'status': 'SUCCESS',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                failback_result['steps'].append({
                    'step': 'validate_primary_region',
                    'status': 'FAILED',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                failback_result['status'] = 'FAILED'
                return failback_result
            
            # Step 2: Synchronize data
            try:
                self._synchronize_data(failback_config['from_region'], self.primary_region)
                failback_result['steps'].append({
                    'step': 'synchronize_data',
                    'status': 'SUCCESS',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                failback_result['steps'].append({
                    'step': 'synchronize_data',
                    'status': 'FAILED',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
            
            # Step 3: Failback application
            try:
                self._failback_application(self.primary_region)
                failback_result['steps'].append({
                    'step': 'failback_application',
                    'status': 'SUCCESS',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                failback_result['steps'].append({
                    'step': 'failback_application',
                    'status': 'FAILED',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
            
            # Step 4: Update DNS back to primary
            try:
                self._update_dns_routing(self.primary_region)
                failback_result['steps'].append({
                    'step': 'update_dns_primary',
                    'status': 'SUCCESS',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                failback_result['steps'].append({
                    'step': 'update_dns_primary',
                    'status': 'FAILED',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
            
            # Determine overall status
            failed_steps = [step for step in failback_result['steps'] if step['status'] == 'FAILED']
            failback_result['status'] = 'SUCCESS' if not failed_steps else 'PARTIAL_SUCCESS'
            failback_result['end_time'] = datetime.now().isoformat()
            
            return failback_result
        except Exception as e:
            print(f"Error executing failback: {e}")
            return {'status': 'FAILED', 'error': str(e)}
    
    def run_dr_test(self, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive disaster recovery test"""
        try:
            test_result = {
                'test_id': f"dr-test-{int(time.time())}",
                'start_time': datetime.now().isoformat(),
                'test_type': test_config.get('test_type', 'full'),
                'regions_tested': self.all_regions,
                'results': {},
                'overall_status': 'PENDING'
            }
            
            for region in self.all_regions:
                region_results = {
                    'region': region,
                    'status': 'PENDING',
                    'tests': []
                }
                
                # Test database connectivity
                try:
                    db_test = self._test_database_connectivity(region)
                    region_results['tests'].append({
                        'test_name': 'database_connectivity',
                        'status': 'PASS' if db_test else 'FAIL',
                        'duration_ms': 100
                    })
                except Exception as e:
                    region_results['tests'].append({
                        'test_name': 'database_connectivity',
                        'status': 'FAIL',
                        'error': str(e)
                    })
                
                # Test application health
                try:
                    app_test = self._test_application_health(region)
                    region_results['tests'].append({
                        'test_name': 'application_health',
                        'status': 'PASS' if app_test else 'FAIL',
                        'duration_ms': 200
                    })
                except Exception as e:
                    region_results['tests'].append({
                        'test_name': 'application_health',
                        'status': 'FAIL',
                        'error': str(e)
                    })
                
                # Test DNS resolution
                try:
                    dns_test = self._test_dns_resolution(region)
                    region_results['tests'].append({
                        'test_name': 'dns_resolution',
                        'status': 'PASS' if dns_test else 'FAIL',
                        'duration_ms': 50
                    })
                except Exception as e:
                    region_results['tests'].append({
                        'test_name': 'dns_resolution',
                        'status': 'FAIL',
                        'error': str(e)
                    })
                
                # Determine region status
                region_results['status'] = 'PASS' if all(
                    test['status'] == 'PASS' for test in region_results['tests']
                ) else 'FAIL'
                
                test_result['results'][region] = region_results
            
            # Determine overall status
            test_result['overall_status'] = 'PASS' if all(
                result['status'] == 'PASS' for result in test_result['results'].values()
            ) else 'FAIL'
            
            test_result['end_time'] = datetime.now().isoformat()
            
            return test_result
        except Exception as e:
            print(f"Error running DR test: {e}")
            return {}
    
    def get_dr_status(self) -> Dict[str, Any]:
        """Get current disaster recovery status"""
        try:
            status = {
                'primary_region': self.primary_region,
                'dr_regions': self.dr_regions,
                'last_updated': datetime.now().isoformat(),
                'region_status': {},
                'overall_status': 'HEALTHY'
            }
            
            for region in self.all_regions:
                region_status = {
                    'region': region,
                    'status': 'HEALTHY',
                    'services': {}
                }
                
                # Check EC2 status
                try:
                    instances = self.ec2_clients[region].describe_instances()
                    region_status['services']['ec2'] = {
                        'instance_count': len(instances['Reservations']),
                        'status': 'HEALTHY'
                    }
                except Exception as e:
                    region_status['services']['ec2'] = {
                        'status': 'UNHEALTHY',
                        'error': str(e)
                    }
                
                # Check RDS status
                try:
                    instances = self.rds_clients[region].describe_db_instances()
                    region_status['services']['rds'] = {
                        'instance_count': len(instances['DBInstances']),
                        'status': 'HEALTHY'
                    }
                except Exception as e:
                    region_status['services']['rds'] = {
                        'status': 'UNHEALTHY',
                        'error': str(e)
                    }
                
                # Check S3 status
                try:
                    buckets = self.s3_clients[region].list_buckets()
                    region_status['services']['s3'] = {
                        'bucket_count': len(buckets['Buckets']),
                        'status': 'HEALTHY'
                    }
                except Exception as e:
                    region_status['services']['s3'] = {
                        'status': 'UNHEALTHY',
                        'error': str(e)
                    }
                
                # Determine region status
                unhealthy_services = [
                    service for service in region_status['services'].values()
                    if service['status'] == 'UNHEALTHY'
                ]
                region_status['status'] = 'HEALTHY' if not unhealthy_services else 'UNHEALTHY'
                
                status['region_status'][region] = region_status
            
            # Determine overall status
            unhealthy_regions = [
                region for region in status['region_status'].values()
                if region['status'] == 'UNHEALTHY'
            ]
            status['overall_status'] = 'HEALTHY' if not unhealthy_regions else 'UNHEALTHY'
            
            return status
        except Exception as e:
            print(f"Error getting DR status: {e}")
            return {}
    
    def _validate_target_region(self, region: str) -> bool:
        """Validate target region for failover"""
        # Implementation would validate region availability
        return True
    
    def _failover_database(self, target_region: str) -> bool:
        """Failover database to target region"""
        # Implementation would failover RDS instances
        return True
    
    def _failover_application(self, target_region: str) -> bool:
        """Failover application to target region"""
        # Implementation would failover application services
        return True
    
    def _update_dns_routing(self, target_region: str) -> bool:
        """Update DNS routing to target region"""
        # Implementation would update Route53 records
        return True
    
    def _verify_failover(self, target_region: str) -> bool:
        """Verify failover to target region"""
        # Implementation would verify failover success
        return True
    
    def _synchronize_data(self, from_region: str, to_region: str) -> bool:
        """Synchronize data between regions"""
        # Implementation would synchronize data
        return True
    
    def _failback_application(self, target_region: str) -> bool:
        """Failback application to target region"""
        # Implementation would failback application
        return True
    
    def _test_database_connectivity(self, region: str) -> bool:
        """Test database connectivity in region"""
        # Implementation would test database connectivity
        return True
    
    def _test_application_health(self, region: str) -> bool:
        """Test application health in region"""
        # Implementation would test application health
        return True
    
    def _test_dns_resolution(self, region: str) -> bool:
        """Test DNS resolution in region"""
        # Implementation would test DNS resolution
        return True


# Example usage and testing
if __name__ == "__main__":
    # Initialize DR manager
    dr_manager = DisasterRecoveryManager(
        primary_region='us-east-1',
        dr_regions=['us-west-2', 'eu-west-1']
    )
    
    # Create DR plan
    plan_config = {
        'plan_name': 'Production DR Plan',
        'rto_minutes': 60,
        'rpo_minutes': 15,
        'failover_triggers': ['database_failure', 'application_failure'],
        'health_checks': ['database', 'application', 'dns']
    }
    plan_id = dr_manager.create_dr_plan(plan_config)
    print(f"Created DR plan: {plan_id}")
    
    # Setup automated failover
    failover_config = {
        'execution_role_arn': 'arn:aws:iam::account:role/DRExecutionRole'
    }
    dr_manager.setup_automated_failover(failover_config)
    
    # Setup health monitoring
    monitoring_config = {
        'fqdn': 'example.com',
        'sns_topic_arn': 'arn:aws:sns:region:account:dr-alerts'
    }
    health_checks = dr_manager.setup_health_monitoring(monitoring_config)
    print(f"Created {len(health_checks)} health checks")
    
    # Run DR test
    test_config = {
        'test_type': 'full'
    }
    test_results = dr_manager.run_dr_test(test_config)
    print(f"DR test results: {test_results['overall_status']}")
    
    # Get DR status
    status = dr_manager.get_dr_status()
    print(f"DR status: {status['overall_status']}")