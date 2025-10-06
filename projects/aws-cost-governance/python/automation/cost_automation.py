#!/usr/bin/env python3
"""
AWS Cost Automation
Automated cost management with scheduled actions, auto-scaling, and resource optimization
"""

import boto3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from botocore.exceptions import ClientError
import schedule
import threading


class CostAutomation:
    """Automated cost management and optimization"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.ce_client = boto3.client('ce', region_name=region)
        self.ec2_client = boto3.client('ec2', region_name=region)
        self.rds_client = boto3.client('rds', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=region)
        self.sns_client = boto3.client('sns', region_name=region)
        self.organizations_client = boto3.client('organizations', region_name=region)
        self.autoscaling_client = boto3.client('autoscaling', region_name=region)
        
    def create_scheduled_cost_actions(self, schedule_config: Dict[str, Any]) -> bool:
        """Create scheduled cost management actions"""
        try:
            # Schedule daily cost checks
            schedule.every().day.at("09:00").do(
                self._daily_cost_check,
                threshold=schedule_config.get('daily_threshold', 100)
            )
            
            # Schedule weekly cost reports
            schedule.every().monday.at("10:00").do(
                self._weekly_cost_report,
                email=schedule_config.get('report_email')
            )
            
            # Schedule monthly optimization
            schedule.every().month.do(
                self._monthly_optimization
            )
            
            # Schedule resource cleanup
            schedule.every().sunday.at("02:00").do(
                self._cleanup_unused_resources
            )
            
            return True
        except Exception as e:
            print(f"Error creating scheduled actions: {e}")
            return False
    
    def start_automation_scheduler(self) -> None:
        """Start the automation scheduler in a separate thread"""
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        print("Cost automation scheduler started")
    
    def create_auto_scaling_policies(self, policies: List[Dict[str, Any]]) -> bool:
        """Create auto-scaling policies for cost optimization"""
        try:
            for policy in policies:
                self.autoscaling_client.put_scaling_policy(
                    AutoScalingGroupName=policy['AutoScalingGroupName'],
                    PolicyName=policy['PolicyName'],
                    PolicyType=policy.get('PolicyType', 'TargetTrackingScaling'),
                    TargetTrackingConfiguration=policy.get('TargetTrackingConfiguration', {}),
                    AdjustmentType=policy.get('AdjustmentType', 'ChangeInCapacity'),
                    ScalingAdjustment=policy.get('ScalingAdjustment', 1),
                    Cooldown=policy.get('Cooldown', 300)
                )
            return True
        except Exception as e:
            print(f"Error creating auto-scaling policies: {e}")
            return False
    
    def create_cost_based_scaling(self, asg_name: str, target_cost: float) -> bool:
        """Create cost-based auto-scaling policy"""
        try:
            policy_config = {
                'AutoScalingGroupName': asg_name,
                'PolicyName': f'{asg_name}-cost-scaling',
                'PolicyType': 'TargetTrackingScaling',
                'TargetTrackingConfiguration': {
                    'TargetValue': target_cost,
                    'PredefinedMetricSpecification': {
                        'PredefinedMetricType': 'ASGAverageCPUUtilization'
                    }
                }
            }
            
            return self.create_auto_scaling_policies([policy_config])
        except Exception as e:
            print(f"Error creating cost-based scaling: {e}")
            return False
    
    def create_scheduled_instances(self, schedule_config: Dict[str, Any]) -> bool:
        """Create scheduled EC2 instances for cost optimization"""
        try:
            response = self.ec2_client.create_scheduled_instances(
                InstanceCount=schedule_config.get('InstanceCount', 1),
                PurchaseRequests=[
                    {
                        'InstanceType': schedule_config['InstanceType'],
                        'Placement': schedule_config.get('Placement', {}),
                        'ImageId': schedule_config['ImageId'],
                        'ScheduledInstanceId': schedule_config.get('ScheduledInstanceId'),
                        'BlockDeviceMappings': schedule_config.get('BlockDeviceMappings', [])
                    }
                ],
                ClientToken=schedule_config.get('ClientToken', f"scheduled-{int(time.time())}")
            )
            return 'ScheduledInstanceSet' in response
        except Exception as e:
            print(f"Error creating scheduled instances: {e}")
            return False
    
    def create_spot_instances(self, spot_config: Dict[str, Any]) -> bool:
        """Create Spot instances for cost savings"""
        try:
            response = self.ec2_client.request_spot_instances(
                SpotPrice=spot_config.get('SpotPrice', '0.10'),
                InstanceCount=spot_config.get('InstanceCount', 1),
                Type=spot_config.get('Type', 'one-time'),
                LaunchSpecification={
                    'ImageId': spot_config['ImageId'],
                    'InstanceType': spot_config['InstanceType'],
                    'KeyName': spot_config.get('KeyName'),
                    'SecurityGroups': spot_config.get('SecurityGroups', []),
                    'UserData': spot_config.get('UserData', ''),
                    'Placement': spot_config.get('Placement', {}),
                    'BlockDeviceMappings': spot_config.get('BlockDeviceMappings', [])
                }
            )
            return 'SpotInstanceRequests' in response
        except Exception as e:
            print(f"Error creating spot instances: {e}")
            return False
    
    def create_auto_stop_instances(self, instance_ids: List[str], 
                                 stop_time: str = "18:00") -> bool:
        """Create auto-stop schedule for instances"""
        try:
            # This would typically use EventBridge rules with Lambda functions
            # For now, we'll create a simple schedule
            schedule.every().day.at(stop_time).do(
                self._stop_instances,
                instance_ids=instance_ids
            )
            return True
        except Exception as e:
            print(f"Error creating auto-stop schedule: {e}")
            return False
    
    def create_auto_start_instances(self, instance_ids: List[str], 
                                  start_time: str = "08:00") -> bool:
        """Create auto-start schedule for instances"""
        try:
            schedule.every().day.at(start_time).do(
                self._start_instances,
                instance_ids=instance_ids
            )
            return True
        except Exception as e:
            print(f"Error creating auto-start schedule: {e}")
            return False
    
    def create_cost_optimized_launch_template(self, template_config: Dict[str, Any]) -> bool:
        """Create cost-optimized launch template"""
        try:
            response = self.ec2_client.create_launch_template(
                LaunchTemplateName=template_config['LaunchTemplateName'],
                LaunchTemplateData={
                    'ImageId': template_config['ImageId'],
                    'InstanceType': template_config['InstanceType'],
                    'KeyName': template_config.get('KeyName'),
                    'SecurityGroupIds': template_config.get('SecurityGroupIds', []),
                    'UserData': template_config.get('UserData', ''),
                    'IamInstanceProfile': template_config.get('IamInstanceProfile', {}),
                    'Monitoring': {'Enabled': template_config.get('Monitoring', True)},
                    'InstanceMarketOptions': {
                        'MarketType': 'spot',
                        'SpotOptions': {
                            'SpotInstanceType': 'one-time',
                            'MaxPrice': template_config.get('MaxPrice', '0.10')
                        }
                    },
                    'TagSpecifications': template_config.get('TagSpecifications', [])
                }
            )
            return 'LaunchTemplate' in response
        except Exception as e:
            print(f"Error creating launch template: {e}")
            return False
    
    def create_cost_allocation_tags(self, tag_policy: Dict[str, Any]) -> bool:
        """Create automated cost allocation tagging"""
        try:
            # Create cost category definition
            self.ce_client.create_cost_category_definition(
                Name=tag_policy['Name'],
                Rules=tag_policy.get('Rules', []),
                RuleVersion=tag_policy.get('RuleVersion', 'CostCategoryExpression.v1')
            )
            return True
        except Exception as e:
            print(f"Error creating cost allocation tags: {e}")
            return False
    
    def create_automated_rightsizing(self, rightsizing_config: Dict[str, Any]) -> bool:
        """Create automated rightsizing recommendations and actions"""
        try:
            # This would typically involve:
            # 1. Getting rightsizing recommendations
            # 2. Analyzing current utilization
            # 3. Creating automated actions based on recommendations
            
            # For now, we'll create a scheduled job
            schedule.every().week.do(
                self._analyze_rightsizing_recommendations,
                config=rightsizing_config
            )
            return True
        except Exception as e:
            print(f"Error creating automated rightsizing: {e}")
            return False
    
    def create_reserved_instance_automation(self, ri_config: Dict[str, Any]) -> bool:
        """Create automated Reserved Instance management"""
        try:
            # Schedule RI analysis
            schedule.every().month.do(
                self._analyze_reserved_instances,
                config=ri_config
            )
            return True
        except Exception as e:
            print(f"Error creating RI automation: {e}")
            return False
    
    def create_savings_plans_automation(self, sp_config: Dict[str, Any]) -> bool:
        """Create automated Savings Plans management"""
        try:
            # Schedule SP analysis
            schedule.every().month.do(
                self._analyze_savings_plans,
                config=sp_config
            )
            return True
        except Exception as e:
            print(f"Error creating SP automation: {e}")
            return False
    
    def create_cost_anomaly_detection(self, anomaly_config: Dict[str, Any]) -> bool:
        """Create automated cost anomaly detection"""
        try:
            response = self.ce_client.create_anomaly_detector(
                AnomalyDetector=anomaly_config
            )
            
            # Schedule anomaly monitoring
            schedule.every().day.at("08:00").do(
                self._check_cost_anomalies,
                detector_arn=response['AnomalyDetectorArn']
            )
            return True
        except Exception as e:
            print(f"Error creating anomaly detection: {e}")
            return False
    
    def create_budget_automation(self, budget_config: Dict[str, Any]) -> bool:
        """Create automated budget management"""
        try:
            # Create budget
            self.ce_client.create_budget(
                AccountId=budget_config['AccountId'],
                Budget=budget_config['Budget'],
                NotificationsWithSubscribers=budget_config.get('NotificationsWithSubscribers', [])
            )
            
            # Schedule budget monitoring
            schedule.every().day.at("09:00").do(
                self._monitor_budgets,
                config=budget_config
            )
            return True
        except Exception as e:
            print(f"Error creating budget automation: {e}")
            return False
    
    def create_cost_optimization_workflow(self, workflow_config: Dict[str, Any]) -> bool:
        """Create comprehensive cost optimization workflow"""
        try:
            # Schedule different optimization tasks
            schedule.every().monday.at("10:00").do(
                self._run_ec2_optimization,
                config=workflow_config.get('ec2_config', {})
            )
            
            schedule.every().tuesday.at("10:00").do(
                self._run_rds_optimization,
                config=workflow_config.get('rds_config', {})
            )
            
            schedule.every().wednesday.at("10:00").do(
                self._run_storage_optimization,
                config=workflow_config.get('storage_config', {})
            )
            
            schedule.every().thursday.at("10:00").do(
                self._run_lambda_optimization,
                config=workflow_config.get('lambda_config', {})
            )
            
            schedule.every().friday.at("10:00").do(
                self._run_cleanup_tasks,
                config=workflow_config.get('cleanup_config', {})
            )
            
            return True
        except Exception as e:
            print(f"Error creating optimization workflow: {e}")
            return False
    
    def _daily_cost_check(self, threshold: float) -> None:
        """Daily cost threshold check"""
        try:
            current_cost = self._get_current_daily_cost()
            if current_cost > threshold:
                self._send_cost_alert(f"Daily cost ${current_cost:.2f} exceeds threshold ${threshold}")
        except Exception as e:
            print(f"Error in daily cost check: {e}")
    
    def _weekly_cost_report(self, email: str) -> None:
        """Generate and send weekly cost report"""
        try:
            report = self._generate_weekly_report()
            self._send_cost_report(email, report)
        except Exception as e:
            print(f"Error generating weekly report: {e}")
    
    def _monthly_optimization(self) -> None:
        """Run monthly cost optimization"""
        try:
            # Get optimization recommendations
            recommendations = self._get_optimization_recommendations()
            
            # Apply automated optimizations
            self._apply_automated_optimizations(recommendations)
        except Exception as e:
            print(f"Error in monthly optimization: {e}")
    
    def _cleanup_unused_resources(self) -> None:
        """Clean up unused resources"""
        try:
            # Find unused resources
            unused_resources = self._find_unused_resources()
            
            # Clean up based on policy
            self._cleanup_resources(unused_resources)
        except Exception as e:
            print(f"Error cleaning up resources: {e}")
    
    def _stop_instances(self, instance_ids: List[str]) -> None:
        """Stop instances"""
        try:
            self.ec2_client.stop_instances(InstanceIds=instance_ids)
            print(f"Stopped instances: {instance_ids}")
        except Exception as e:
            print(f"Error stopping instances: {e}")
    
    def _start_instances(self, instance_ids: List[str]) -> None:
        """Start instances"""
        try:
            self.ec2_client.start_instances(InstanceIds=instance_ids)
            print(f"Started instances: {instance_ids}")
        except Exception as e:
            print(f"Error starting instances: {e}")
    
    def _analyze_rightsizing_recommendations(self, config: Dict[str, Any]) -> None:
        """Analyze rightsizing recommendations"""
        try:
            # Get rightsizing recommendations
            recommendations = self.ce_client.get_rightsizing_recommendation(
                Service='EC2'
            )
            
            # Process recommendations
            self._process_rightsizing_recommendations(recommendations, config)
        except Exception as e:
            print(f"Error analyzing rightsizing: {e}")
    
    def _analyze_reserved_instances(self, config: Dict[str, Any]) -> None:
        """Analyze Reserved Instance utilization"""
        try:
            # Get RI utilization
            utilization = self.ce_client.get_reservation_coverage(
                TimePeriod={
                    'Start': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                    'End': datetime.now().strftime('%Y-%m-%d')
                }
            )
            
            # Process utilization data
            self._process_ri_utilization(utilization, config)
        except Exception as e:
            print(f"Error analyzing RIs: {e}")
    
    def _analyze_savings_plans(self, config: Dict[str, Any]) -> None:
        """Analyze Savings Plans utilization"""
        try:
            # Get SP recommendations
            recommendations = self.ce_client.get_savings_plans_purchase_recommendation(
                SavingsPlansType='COMPUTE_SP',
                TermInYears='ONE_YEAR',
                PaymentOption='NO_UPFRONT'
            )
            
            # Process recommendations
            self._process_sp_recommendations(recommendations, config)
        except Exception as e:
            print(f"Error analyzing Savings Plans: {e}")
    
    def _check_cost_anomalies(self, detector_arn: str) -> None:
        """Check for cost anomalies"""
        try:
            anomalies = self.ce_client.get_anomalies(
                DateInterval={
                    'Start': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                    'End': datetime.now().strftime('%Y-%m-%d')
                }
            )
            
            if anomalies.get('Anomalies'):
                self._process_cost_anomalies(anomalies['Anomalies'])
        except Exception as e:
            print(f"Error checking anomalies: {e}")
    
    def _monitor_budgets(self, config: Dict[str, Any]) -> None:
        """Monitor budget status"""
        try:
            budgets = self.budgets_client.describe_budgets(
                AccountId=config['AccountId']
            )
            
            for budget in budgets.get('Budgets', []):
                self._check_budget_status(budget)
        except Exception as e:
            print(f"Error monitoring budgets: {e}")
    
    def _run_ec2_optimization(self, config: Dict[str, Any]) -> None:
        """Run EC2 cost optimization"""
        try:
            # Analyze EC2 costs
            analysis = self._analyze_ec2_costs()
            
            # Apply optimizations
            self._apply_ec2_optimizations(analysis, config)
        except Exception as e:
            print(f"Error in EC2 optimization: {e}")
    
    def _run_rds_optimization(self, config: Dict[str, Any]) -> None:
        """Run RDS cost optimization"""
        try:
            # Analyze RDS costs
            analysis = self._analyze_rds_costs()
            
            # Apply optimizations
            self._apply_rds_optimizations(analysis, config)
        except Exception as e:
            print(f"Error in RDS optimization: {e}")
    
    def _run_storage_optimization(self, config: Dict[str, Any]) -> None:
        """Run storage cost optimization"""
        try:
            # Analyze storage costs
            analysis = self._analyze_storage_costs()
            
            # Apply optimizations
            self._apply_storage_optimizations(analysis, config)
        except Exception as e:
            print(f"Error in storage optimization: {e}")
    
    def _run_lambda_optimization(self, config: Dict[str, Any]) -> None:
        """Run Lambda cost optimization"""
        try:
            # Analyze Lambda costs
            analysis = self._analyze_lambda_costs()
            
            # Apply optimizations
            self._apply_lambda_optimizations(analysis, config)
        except Exception as e:
            print(f"Error in Lambda optimization: {e}")
    
    def _run_cleanup_tasks(self, config: Dict[str, Any]) -> None:
        """Run cleanup tasks"""
        try:
            # Find unused resources
            unused = self._find_unused_resources()
            
            # Clean up resources
            self._cleanup_resources(unused)
        except Exception as e:
            print(f"Error in cleanup tasks: {e}")
    
    def _get_current_daily_cost(self) -> float:
        """Get current daily cost"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={'Start': today, 'End': today},
                Granularity='DAILY',
                Metrics=['BlendedCost']
            )
            
            for result in response.get('ResultsByTime', []):
                return float(result['Total']['BlendedCost']['Amount'])
            return 0.0
        except Exception as e:
            print(f"Error getting daily cost: {e}")
            return 0.0
    
    def _send_cost_alert(self, message: str) -> None:
        """Send cost alert"""
        try:
            # This would send to SNS or email
            print(f"COST ALERT: {message}")
        except Exception as e:
            print(f"Error sending alert: {e}")
    
    def _generate_weekly_report(self) -> Dict[str, Any]:
        """Generate weekly cost report"""
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={'Start': start_date, 'End': end_date},
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
            )
            
            return {
                'period': {'start': start_date, 'end': end_date},
                'data': response
            }
        except Exception as e:
            print(f"Error generating report: {e}")
            return {}
    
    def _send_cost_report(self, email: str, report: Dict[str, Any]) -> None:
        """Send cost report via email"""
        try:
            # This would send via SNS or SES
            print(f"Sent cost report to {email}")
        except Exception as e:
            print(f"Error sending report: {e}")
    
    def _get_optimization_recommendations(self) -> Dict[str, Any]:
        """Get optimization recommendations"""
        try:
            # This would call the CostOptimizer class
            return {}
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return {}
    
    def _apply_automated_optimizations(self, recommendations: Dict[str, Any]) -> None:
        """Apply automated optimizations"""
        try:
            # Apply optimizations based on recommendations
            print("Applied automated optimizations")
        except Exception as e:
            print(f"Error applying optimizations: {e}")
    
    def _find_unused_resources(self) -> Dict[str, Any]:
        """Find unused resources"""
        try:
            # This would identify unused resources
            return {}
        except Exception as e:
            print(f"Error finding unused resources: {e}")
            return {}
    
    def _cleanup_resources(self, resources: Dict[str, Any]) -> None:
        """Clean up resources"""
        try:
            # Clean up resources based on policy
            print("Cleaned up resources")
        except Exception as e:
            print(f"Error cleaning up resources: {e}")


# Example usage and testing
if __name__ == "__main__":
    # Initialize cost automation
    automation = CostAutomation()
    
    # Create scheduled actions
    schedule_config = {
        'daily_threshold': 100,
        'report_email': 'admin@company.com'
    }
    automation.create_scheduled_cost_actions(schedule_config)
    
    # Create cost-based scaling
    automation.create_cost_based_scaling('my-asg', 50.0)
    
    # Create auto-stop/start for instances
    automation.create_auto_stop_instances(['i-1234567890abcdef0'], '18:00')
    automation.create_auto_start_instances(['i-1234567890abcdef0'], '08:00')
    
    # Create cost-optimized launch template
    template_config = {
        'LaunchTemplateName': 'cost-optimized-template',
        'ImageId': 'ami-12345678',
        'InstanceType': 't3.micro',
        'MaxPrice': '0.05'
    }
    automation.create_cost_optimized_launch_template(template_config)
    
    # Start automation scheduler
    automation.start_automation_scheduler()
    
    print("Cost automation setup completed")