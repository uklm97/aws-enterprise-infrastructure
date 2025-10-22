#!/usr/bin/env python3
"""
AWS Instance Scheduler - Cost Savings Automation

This script provides automated start/stop functionality for EC2 instances
to achieve significant cost savings by running instances only when needed.

Features:
- Scheduled start/stop based on business hours
- Weekend and holiday shutdown
- Tag-based instance selection
- Cost savings reporting
- Email notifications

Author: AWS Operations Automation
Version: 1.0.0
"""

import boto3
import schedule
import time
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import yaml
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instance_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class InstanceScheduler:
    """
    AWS Instance Scheduler for cost savings automation.
    """
    
    def __init__(self, config_file: str = 'config/automation_config.yaml'):
        """
        Initialize the instance scheduler.
        
        Args:
            config_file (str): Path to configuration file
        """
        self.config = self.load_config(config_file)
        self.ec2_client = boto3.client('ec2', region_name=self.config.get('aws_region', 'us-east-1'))
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=self.config.get('aws_region', 'us-east-1'))
        self.sns_client = boto3.client('sns', region_name=self.config.get('aws_region', 'us-east-1'))
        
        # Cost tracking
        self.cost_savings = {
            'instances_started': 0,
            'instances_stopped': 0,
            'estimated_savings': 0.0
        }
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Args:
            config_file (str): Path to configuration file
            
        Returns:
            Dict containing configuration
        """
        try:
            with open(config_file, 'r') as file:
                config = yaml.safe_load(file)
            logger.info(f"Configuration loaded from {config_file}")
            return config
        except FileNotFoundError:
            logger.warning(f"Configuration file {config_file} not found, using defaults")
            return self.get_default_config()
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration.
        
        Returns:
            Dict containing default configuration
        """
        return {
            'aws_region': 'us-east-1',
            'schedules': {
                'business_hours': {
                    'start_time': '08:00',
                    'stop_time': '18:00',
                    'timezone': 'UTC'
                },
                'weekend_shutdown': True,
                'holiday_shutdown': True,
                'holidays': [],  # List of YYYY-MM-DD strings
                'holiday_check_time': '08:00'
            },
            'instance_tags': {
                'start_tag': 'AutoStart',
                'stop_tag': 'AutoStop',
                'environment_tag': 'Environment'
            },
            'notifications': {
                'email': 'admin@company.com',
                'sns_topic': 'aws-operations-alerts'
            },
            'cost_tracking': {
                'enabled': True,
                'hourly_cost': 0.10  # Default hourly cost per instance
            }
        }
    
    def get_instances_by_tag(self, tag_key: str, tag_value: str) -> List[Dict[str, Any]]:
        """
        Get instances by tag.
        
        Args:
            tag_key (str): Tag key to filter by
            tag_value (str): Tag value to filter by
            
        Returns:
            List of instance dictionaries
        """
        try:
            response = self.ec2_client.describe_instances(
                Filters=[
                    {
                        'Name': f'tag:{tag_key}',
                        'Values': [tag_value]
                    },
                    {
                        'Name': 'instance-state-name',
                        'Values': ['running', 'stopped']
                    }
                ]
            )
            
            instances = []
            for reservation in response['Reservations']:
                instances.extend(reservation['Instances'])
            
            logger.info(f"Found {len(instances)} instances with tag {tag_key}={tag_value}")
            return instances
            
        except Exception as e:
            logger.error(f"Error getting instances by tag: {str(e)}")
            return []
    
    def start_instances(self, tag_key: str = 'AutoStart', tag_value: str = 'true'):
        """
        Start instances based on tag.
        
        Args:
            tag_key (str): Tag key to filter instances
            tag_value (str): Tag value to filter instances
        """
        try:
            instances = self.get_instances_by_tag(tag_key, tag_value)
            started_count = 0
            
            for instance in instances:
                if instance['State']['Name'] == 'stopped':
                    try:
                        self.ec2_client.start_instances(
                            InstanceIds=[instance['InstanceId']]
                        )
                        started_count += 1
                        logger.info(f"Started instance: {instance['InstanceId']}")
                        
                        # Add cost tracking
                        self.cost_savings['instances_started'] += 1
                        
                    except Exception as e:
                        logger.error(f"Error starting instance {instance['InstanceId']}: {str(e)}")
            
            if started_count > 0:
                self.send_notification(
                    f"Started {started_count} instances",
                    f"Successfully started {started_count} instances at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            
            logger.info(f"Started {started_count} instances")
            
        except Exception as e:
            logger.error(f"Error in start_instances: {str(e)}")
    
    def stop_instances(self, tag_key: str = 'AutoStop', tag_value: str = 'true'):
        """
        Stop instances based on tag.
        
        Args:
            tag_key (str): Tag key to filter instances
            tag_value (str): Tag value to filter instances
        """
        try:
            instances = self.get_instances_by_tag(tag_key, tag_value)
            stopped_count = 0
            
            for instance in instances:
                if instance['State']['Name'] == 'running':
                    try:
                        self.ec2_client.stop_instances(
                            InstanceIds=[instance['InstanceId']]
                        )
                        stopped_count += 1
                        logger.info(f"Stopped instance: {instance['InstanceId']}")
                        
                        # Add cost tracking
                        self.cost_savings['instances_stopped'] += 1
                        hourly_cost = self.config.get('cost_tracking', {}).get('hourly_cost', 0.10)
                        self.cost_savings['estimated_savings'] += hourly_cost
                        
                    except Exception as e:
                        logger.error(f"Error stopping instance {instance['InstanceId']}: {str(e)}")
            
            if stopped_count > 0:
                self.send_notification(
                    f"Stopped {stopped_count} instances",
                    f"Successfully stopped {stopped_count} instances at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            
            logger.info(f"Stopped {stopped_count} instances")
            
        except Exception as e:
            logger.error(f"Error in stop_instances: {str(e)}")
    
    def start_business_hours(self):
        """Start instances for business hours."""
        logger.info("Starting instances for business hours")
        self.start_instances('AutoStart', 'true')
    
    def stop_business_hours(self):
        """Stop instances at end of business hours."""
        logger.info("Stopping instances at end of business hours")
        self.stop_instances('AutoStop', 'true')
    
    def weekend_shutdown(self):
        """Stop non-critical instances for weekend."""
        logger.info("Performing weekend shutdown")
        self.stop_instances('WeekendShutdown', 'true')
    
    def holiday_shutdown(self):
        """Stop instances for holidays."""
        logger.info("Performing holiday shutdown")
        self.stop_instances('HolidayShutdown', 'true')
    
    def _is_today_holiday(self) -> bool:
        """Return True if today is in configured holidays (YYYY-MM-DD)."""
        try:
            schedules = self.config.get('schedules', {})
            holidays = set(schedules.get('holidays', []) or [])
            today_str = datetime.now().strftime('%Y-%m-%d')
            return today_str in holidays
        except Exception:
            return False

    def check_holiday_and_shutdown(self):
        """Check if today is a holiday and trigger shutdown if so."""
        try:
            if self._is_today_holiday():
                logger.info("Today is a configured holiday. Triggering holiday shutdown.")
                self.holiday_shutdown()
            else:
                logger.info("Today is not a configured holiday. No holiday shutdown performed.")
        except Exception as e:
            logger.error(f"Error during holiday check: {str(e)}")
    
    def send_notification(self, subject: str, message: str):
        """
        Send notification via SNS.
        
        Args:
            subject (str): Notification subject
            message (str): Notification message
        """
        try:
            sns_topic = self.config.get('notifications', {}).get('sns_topic')
            if sns_topic:
                self.sns_client.publish(
                    TopicArn=sns_topic,
                    Subject=subject,
                    Message=message
                )
                logger.info(f"Notification sent: {subject}")
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
    
    def publish_metrics(self):
        """Publish metrics to CloudWatch."""
        try:
            if self.config.get('cost_tracking', {}).get('enabled', True):
                self.cloudwatch_client.put_metric_data(
                    Namespace='AWS/OperationsAutomation',
                    MetricData=[
                        {
                            'MetricName': 'InstancesStarted',
                            'Value': self.cost_savings['instances_started'],
                            'Unit': 'Count',
                            'Timestamp': datetime.utcnow()
                        },
                        {
                            'MetricName': 'InstancesStopped',
                            'Value': self.cost_savings['instances_stopped'],
                            'Unit': 'Count',
                            'Timestamp': datetime.utcnow()
                        },
                        {
                            'MetricName': 'EstimatedSavings',
                            'Value': self.cost_savings['estimated_savings'],
                            'Unit': 'None',
                            'Timestamp': datetime.utcnow()
                        }
                    ]
                )
                logger.info("Metrics published to CloudWatch")
        except Exception as e:
            logger.error(f"Error publishing metrics: {str(e)}")
    
    def generate_cost_report(self) -> Dict[str, Any]:
        """
        Generate cost savings report.
        
        Returns:
            Dict containing cost savings report
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'instances_started': self.cost_savings['instances_started'],
            'instances_stopped': self.cost_savings['instances_stopped'],
            'estimated_savings': self.cost_savings['estimated_savings'],
            'hourly_cost': self.config.get('cost_tracking', {}).get('hourly_cost', 0.10),
            'daily_savings': self.cost_savings['estimated_savings'] * 24,
            'monthly_savings': self.cost_savings['estimated_savings'] * 24 * 30
        }
        
        logger.info(f"Cost savings report generated: {report}")
        return report
    
    def setup_schedules(self):
        """Setup automation schedules."""
        try:
            schedules = self.config.get('schedules', {})
            
            # Business hours schedule
            business_hours = schedules.get('business_hours', {})
            start_time = business_hours.get('start_time', '08:00')
            stop_time = business_hours.get('stop_time', '18:00')
            
            schedule.every().day.at(start_time).do(self.start_business_hours)
            schedule.every().day.at(stop_time).do(self.stop_business_hours)
            
            # Weekend shutdown
            if schedules.get('weekend_shutdown', True):
                schedule.every().friday.at('18:00').do(self.weekend_shutdown)
                schedule.every().monday.at('08:00').do(self.start_business_hours)
            
            # Holiday shutdown
            if schedules.get('holiday_shutdown', True):
                holiday_check_time = schedules.get('holiday_check_time', '08:00')
                schedule.every().day.at(holiday_check_time).do(self.check_holiday_and_shutdown)
            
            # Daily metrics publishing
            schedule.every().day.at('00:00').do(self.publish_metrics)
            
            # Weekly cost report
            schedule.every().sunday.at('09:00').do(self.generate_weekly_report)
            
            logger.info("Schedules setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up schedules: {str(e)}")
    
    def generate_weekly_report(self):
        """Generate weekly cost savings report."""
        try:
            report = self.generate_cost_report()
            
            # Send weekly report notification
            subject = "Weekly AWS Cost Savings Report"
            message = f"""
Weekly AWS Cost Savings Report
            
Instances Started: {report['instances_started']}
Instances Stopped: {report['instances_stopped']}
Estimated Daily Savings: ${report['daily_savings']:.2f}
Estimated Monthly Savings: ${report['monthly_savings']:.2f}
Total Estimated Savings: ${report['estimated_savings']:.2f}

Generated on: {report['timestamp']}
            """
            
            self.send_notification(subject, message)
            
            # Reset counters for new week
            self.cost_savings = {
                'instances_started': 0,
                'instances_stopped': 0,
                'estimated_savings': 0.0
            }
            
            logger.info("Weekly report generated and sent")
            
        except Exception as e:
            logger.error(f"Error generating weekly report: {str(e)}")
    
    def run_scheduler(self):
        """Run the scheduler continuously."""
        logger.info("Starting AWS Instance Scheduler")
        
        try:
            # Setup schedules
            self.setup_schedules()
            
            # Run scheduler
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Error in scheduler: {str(e)}")


def lambda_handler(event, context):
    """
    AWS Lambda handler for serverless execution.
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        Dict containing execution results
    """
    try:
        scheduler = InstanceScheduler()
        
        # Determine action based on event
        action = event.get('action', 'start')
        
        if action == 'start':
            scheduler.start_business_hours()
        elif action == 'stop':
            scheduler.stop_business_hours()
        elif action == 'weekend_shutdown':
            scheduler.weekend_shutdown()
        elif action == 'holiday_shutdown':
            scheduler.holiday_shutdown()
        elif action == 'publish_metrics':
            scheduler.publish_metrics()
        elif action == 'generate_report':
            report = scheduler.generate_cost_report()
            return {
                'statusCode': 200,
                'body': json.dumps(report)
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Action {action} completed successfully',
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }


if __name__ == '__main__':
    # Run scheduler locally
    scheduler = InstanceScheduler()
    scheduler.run_scheduler()
