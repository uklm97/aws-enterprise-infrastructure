#!/usr/bin/env python3
"""
AWS CI/CD Monitoring Manager for observability and alerting.

This module provides comprehensive monitoring capabilities including
metrics collection, log aggregation, alerting, and dashboard management.
"""

import boto3
import logging
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitoringManager:
    """
    AWS CI/CD Monitoring Manager for observability and alerting.
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize MonitoringManager with AWS clients."""
        self.region = region
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=region)
        self.logs_client = boto3.client('logs', region_name=region)
        self.sns_client = boto3.client('sns', region_name=region)
        self.codebuild_client = boto3.client('codebuild', region_name=region)
        self.codepipeline_client = boto3.client('codepipeline', region_name=region)
        self.codedeploy_client = boto3.client('codedeploy', region_name=region)
        
    def create_cloudwatch_dashboard(self, dashboard_name: str, dashboard_config: Dict[str, Any]) -> bool:
        """Create CloudWatch dashboard."""
        try:
            logger.info(f"Creating CloudWatch dashboard: {dashboard_name}")
            
            # Build dashboard body
            dashboard_body = self._build_dashboard_body(dashboard_config)
            
            # Create dashboard
            response = self.cloudwatch_client.put_dashboard(
                DashboardName=dashboard_name,
                DashboardBody=json.dumps(dashboard_body)
            )
            
            logger.info(f"Dashboard {dashboard_name} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {str(e)}")
            return False
    
    def _build_dashboard_body(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build CloudWatch dashboard body."""
        widgets = []
        
        # Add widgets based on configuration
        for widget_config in config.get('widgets', []):
            widget = self._create_widget(widget_config)
            if widget:
                widgets.append(widget)
        
        return {
            'widgets': widgets
        }
    
    def _create_widget(self, widget_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create individual dashboard widget."""
        widget_type = widget_config.get('type')
        
        if widget_type == 'metric':
            return self._create_metric_widget(widget_config)
        elif widget_type == 'log':
            return self._create_log_widget(widget_config)
        elif widget_type == 'text':
            return self._create_text_widget(widget_config)
        else:
            logger.warning(f"Unknown widget type: {widget_type}")
            return None
    
    def _create_metric_widget(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create metric widget."""
        return {
            'type': 'metric',
            'x': config.get('x', 0),
            'y': config.get('y', 0),
            'width': config.get('width', 12),
            'height': config.get('height', 6),
            'properties': {
                'metrics': config.get('metrics', []),
                'view': 'timeSeries',
                'stacked': False,
                'region': self.region,
                'title': config.get('title', 'Metric'),
                'period': config.get('period', 300),
                'stat': config.get('stat', 'Average')
            }
        }
    
    def _create_log_widget(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create log widget."""
        return {
            'type': 'log',
            'x': config.get('x', 0),
            'y': config.get('y', 0),
            'width': config.get('width', 12),
            'height': config.get('height', 6),
            'properties': {
                'query': config.get('query', ''),
                'region': self.region,
                'title': config.get('title', 'Logs'),
                'view': 'table'
            }
        }
    
    def _create_text_widget(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create text widget."""
        return {
            'type': 'text',
            'x': config.get('x', 0),
            'y': config.get('y', 0),
            'width': config.get('width', 12),
            'height': config.get('height', 6),
            'properties': {
                'markdown': config.get('markdown', '')
            }
        }
    
    def create_cloudwatch_alarm(self, alarm_config: Dict[str, Any]) -> bool:
        """Create CloudWatch alarm."""
        try:
            logger.info(f"Creating CloudWatch alarm: {alarm_config['AlarmName']}")
            
            # Create alarm
            response = self.cloudwatch_client.put_metric_alarm(**alarm_config)
            
            logger.info(f"Alarm {alarm_config['AlarmName']} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating alarm: {str(e)}")
            return False
    
    def create_log_group(self, log_group_name: str, retention_days: int = 30) -> bool:
        """Create CloudWatch log group."""
        try:
            logger.info(f"Creating log group: {log_group_name}")
            
            # Create log group
            self.logs_client.create_log_group(logGroupName=log_group_name)
            
            # Set retention policy
            self.logs_client.put_retention_policy(
                logGroupName=log_group_name,
                retentionInDays=retention_days
            )
            
            logger.info(f"Log group {log_group_name} created successfully")
            return True
            
        except self.logs_client.exceptions.ResourceAlreadyExistsException:
            logger.info(f"Log group {log_group_name} already exists")
            return True
        except Exception as e:
            logger.error(f"Error creating log group: {str(e)}")
            return False
    
    def create_sns_topic(self, topic_name: str, display_name: str = None) -> Optional[str]:
        """Create SNS topic for notifications."""
        try:
            logger.info(f"Creating SNS topic: {topic_name}")
            
            # Create topic
            response = self.sns_client.create_topic(
                Name=topic_name,
                Attributes={'DisplayName': display_name or topic_name}
            )
            
            topic_arn = response['TopicArn']
            logger.info(f"SNS topic {topic_name} created successfully: {topic_arn}")
            return topic_arn
            
        except Exception as e:
            logger.error(f"Error creating SNS topic: {str(e)}")
            return None
    
    def subscribe_to_topic(self, topic_arn: str, protocol: str, endpoint: str) -> Optional[str]:
        """Subscribe to SNS topic."""
        try:
            logger.info(f"Subscribing {endpoint} to topic {topic_arn}")
            
            # Create subscription
            response = self.sns_client.subscribe(
                TopicArn=topic_arn,
                Protocol=protocol,
                Endpoint=endpoint
            )
            
            subscription_arn = response['SubscriptionArn']
            logger.info(f"Subscription created successfully: {subscription_arn}")
            return subscription_arn
            
        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            return None
    
    def get_pipeline_metrics(self, pipeline_name: str, days: int = 7) -> Dict[str, Any]:
        """Get CodePipeline metrics."""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            # Get pipeline execution history
            response = self.codepipeline_client.list_pipeline_executions(
                pipelineName=pipeline_name,
                maxResults=100
            )
            
            executions = response['pipelineExecutionSummaries']
            
            # Calculate metrics
            total_executions = len(executions)
            successful_executions = len([e for e in executions if e['status'] == 'Succeeded'])
            failed_executions = len([e for e in executions if e['status'] == 'Failed'])
            in_progress_executions = len([e for e in executions if e['status'] == 'InProgress'])
            
            success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
            
            return {
                'pipeline_name': pipeline_name,
                'period_days': days,
                'total_executions': total_executions,
                'successful_executions': successful_executions,
                'failed_executions': failed_executions,
                'in_progress_executions': in_progress_executions,
                'success_rate': round(success_rate, 2),
                'executions': executions
            }
            
        except Exception as e:
            logger.error(f"Error getting pipeline metrics: {str(e)}")
            return {'error': str(e)}
    
    def get_build_metrics(self, project_name: str, days: int = 7) -> Dict[str, Any]:
        """Get CodeBuild metrics."""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            # Get build history
            response = self.codebuild_client.list_builds_for_project(
                projectName=project_name,
                sortOrder='DESCENDING'
            )
            
            build_ids = response['ids']
            
            # Get detailed build information
            builds = []
            if build_ids:
                builds_response = self.codebuild_client.batch_get_builds(ids=build_ids)
                builds = builds_response['builds']
            
            # Calculate metrics
            total_builds = len(builds)
            successful_builds = len([b for b in builds if b['buildStatus'] == 'SUCCEEDED'])
            failed_builds = len([b for b in builds if b['buildStatus'] == 'FAILED'])
            in_progress_builds = len([b for b in builds if b['buildStatus'] == 'IN_PROGRESS'])
            
            success_rate = (successful_builds / total_builds * 100) if total_builds > 0 else 0
            
            # Calculate average build duration
            completed_builds = [b for b in builds if b['buildStatus'] in ['SUCCEEDED', 'FAILED']]
            if completed_builds:
                durations = []
                for build in completed_builds:
                    if 'endTime' in build and 'startTime' in build:
                        duration = (build['endTime'] - build['startTime']).total_seconds()
                        durations.append(duration)
                
                avg_duration = sum(durations) / len(durations) if durations else 0
            else:
                avg_duration = 0
            
            return {
                'project_name': project_name,
                'period_days': days,
                'total_builds': total_builds,
                'successful_builds': successful_builds,
                'failed_builds': failed_builds,
                'in_progress_builds': in_progress_builds,
                'success_rate': round(success_rate, 2),
                'average_duration_seconds': round(avg_duration, 2),
                'builds': builds
            }
            
        except Exception as e:
            logger.error(f"Error getting build metrics: {str(e)}")
            return {'error': str(e)}
    
    def get_deployment_metrics(self, application_name: str, days: int = 7) -> Dict[str, Any]:
        """Get CodeDeploy metrics."""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            # Get deployment groups
            response = self.codedeploy_client.list_deployment_groups(
                applicationName=application_name
            )
            
            deployment_groups = response['deploymentGroups']
            
            # Get deployments for each group
            all_deployments = []
            for group in deployment_groups:
                deployments_response = self.codedeploy_client.list_deployments(
                    applicationName=application_name,
                    deploymentGroupName=group
                )
                
                deployment_ids = deployments_response['deployments']
                if deployment_ids:
                    deployments = self.codedeploy_client.batch_get_deployments(
                        deploymentIds=deployment_ids
                    )
                    all_deployments.extend(deployments['deploymentsInfo'])
            
            # Calculate metrics
            total_deployments = len(all_deployments)
            successful_deployments = len([d for d in all_deployments if d['status'] == 'Succeeded'])
            failed_deployments = len([d for d in all_deployments if d['status'] == 'Failed'])
            in_progress_deployments = len([d for d in all_deployments if d['status'] == 'InProgress'])
            
            success_rate = (successful_deployments / total_deployments * 100) if total_deployments > 0 else 0
            
            return {
                'application_name': application_name,
                'period_days': days,
                'total_deployments': total_deployments,
                'successful_deployments': successful_deployments,
                'failed_deployments': failed_deployments,
                'in_progress_deployments': in_progress_deployments,
                'success_rate': round(success_rate, 2),
                'deployments': all_deployments
            }
            
        except Exception as e:
            logger.error(f"Error getting deployment metrics: {str(e)}")
            return {'error': str(e)}
    
    def create_cicd_dashboard(self, project_name: str) -> bool:
        """Create comprehensive CI/CD dashboard."""
        try:
            dashboard_name = f"{project_name}-cicd-dashboard"
            
            dashboard_config = {
                'widgets': [
                    {
                        'type': 'text',
                        'x': 0, 'y': 0, 'width': 24, 'height': 2,
                        'markdown': f'# {project_name} CI/CD Dashboard\n\nGenerated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                    },
                    {
                        'type': 'metric',
                        'x': 0, 'y': 2, 'width': 12, 'height': 6,
                        'title': 'Pipeline Executions',
                        'metrics': [
                            ['AWS/CodePipeline', 'Executions', 'PipelineName', project_name],
                            ['.', 'FailedExecutions', '.', '.'],
                            ['.', 'SuccessfulExecutions', '.', '.']
                        ]
                    },
                    {
                        'type': 'metric',
                        'x': 12, 'y': 2, 'width': 12, 'height': 6,
                        'title': 'Build Metrics',
                        'metrics': [
                            ['AWS/CodeBuild', 'Builds', 'ProjectName', project_name],
                            ['.', 'Duration', '.', '.'],
                            ['.', 'FailedBuilds', '.', '.']
                        ]
                    },
                    {
                        'type': 'metric',
                        'x': 0, 'y': 8, 'width': 12, 'height': 6,
                        'title': 'Deployment Metrics',
                        'metrics': [
                            ['AWS/CodeDeploy', 'Deployments', 'ApplicationName', project_name],
                            ['.', 'FailedDeployments', '.', '.'],
                            ['.', 'SuccessfulDeployments', '.', '.']
                        ]
                    },
                    {
                        'type': 'log',
                        'x': 12, 'y': 8, 'width': 12, 'height': 6,
                        'title': 'Recent Logs',
                        'query': f'fields @timestamp, @message | filter @message like /{project_name}/ | sort @timestamp desc | limit 100'
                    }
                ]
            }
            
            return self.create_cloudwatch_dashboard(dashboard_name, dashboard_config)
            
        except Exception as e:
            logger.error(f"Error creating CI/CD dashboard: {str(e)}")
            return False
    
    def create_cicd_alarms(self, project_name: str, sns_topic_arn: str) -> bool:
        """Create comprehensive CI/CD alarms."""
        try:
            alarms_created = 0
            
            # Pipeline failure alarm
            pipeline_alarm = {
                'AlarmName': f'{project_name}-pipeline-failures',
                'AlarmDescription': f'Pipeline {project_name} has failed executions',
                'MetricName': 'FailedExecutions',
                'Namespace': 'AWS/CodePipeline',
                'Statistic': 'Sum',
                'Dimensions': [
                    {'Name': 'PipelineName', 'Value': project_name}
                ],
                'Period': 300,
                'EvaluationPeriods': 1,
                'Threshold': 0,
                'ComparisonOperator': 'GreaterThanThreshold',
                'AlarmActions': [sns_topic_arn]
            }
            
            if self.create_cloudwatch_alarm(pipeline_alarm):
                alarms_created += 1
            
            # Build failure alarm
            build_alarm = {
                'AlarmName': f'{project_name}-build-failures',
                'AlarmDescription': f'Build project {project_name} has failed builds',
                'MetricName': 'FailedBuilds',
                'Namespace': 'AWS/CodeBuild',
                'Statistic': 'Sum',
                'Dimensions': [
                    {'Name': 'ProjectName', 'Value': project_name}
                ],
                'Period': 300,
                'EvaluationPeriods': 1,
                'Threshold': 0,
                'ComparisonOperator': 'GreaterThanThreshold',
                'AlarmActions': [sns_topic_arn]
            }
            
            if self.create_cloudwatch_alarm(build_alarm):
                alarms_created += 1
            
            # High build duration alarm
            duration_alarm = {
                'AlarmName': f'{project_name}-build-duration',
                'AlarmDescription': f'Build project {project_name} has high duration',
                'MetricName': 'Duration',
                'Namespace': 'AWS/CodeBuild',
                'Statistic': 'Average',
                'Dimensions': [
                    {'Name': 'ProjectName', 'Value': project_name}
                ],
                'Period': 300,
                'EvaluationPeriods': 2,
                'Threshold': 1800,  # 30 minutes
                'ComparisonOperator': 'GreaterThanThreshold',
                'AlarmActions': [sns_topic_arn]
            }
            
            if self.create_cloudwatch_alarm(duration_alarm):
                alarms_created += 1
            
            logger.info(f"Created {alarms_created} alarms for {project_name}")
            return alarms_created > 0
            
        except Exception as e:
            logger.error(f"Error creating CI/CD alarms: {str(e)}")
            return False
    
    def send_notification(self, topic_arn: str, subject: str, message: str) -> bool:
        """Send notification via SNS."""
        try:
            response = self.sns_client.publish(
                TopicArn=topic_arn,
                Subject=subject,
                Message=message
            )
            
            logger.info(f"Notification sent successfully: {response['MessageId']}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return False
    
    def generate_monitoring_report(self, project_name: str, days: int = 7) -> Dict[str, Any]:
        """Generate comprehensive monitoring report."""
        try:
            logger.info(f"Generating monitoring report for {project_name}")
            
            # Get metrics from all services
            pipeline_metrics = self.get_pipeline_metrics(project_name, days)
            build_metrics = self.get_build_metrics(project_name, days)
            deployment_metrics = self.get_deployment_metrics(project_name, days)
            
            # Calculate overall health score
            health_score = self._calculate_health_score(pipeline_metrics, build_metrics, deployment_metrics)
            
            report = {
                'project_name': project_name,
                'report_date': datetime.now().isoformat(),
                'period_days': days,
                'health_score': health_score,
                'pipeline_metrics': pipeline_metrics,
                'build_metrics': build_metrics,
                'deployment_metrics': deployment_metrics,
                'recommendations': self._generate_recommendations(pipeline_metrics, build_metrics, deployment_metrics)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating monitoring report: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_health_score(self, pipeline_metrics: Dict, build_metrics: Dict, deployment_metrics: Dict) -> float:
        """Calculate overall health score."""
        try:
            scores = []
            
            # Pipeline health (40% weight)
            if 'success_rate' in pipeline_metrics:
                scores.append(pipeline_metrics['success_rate'] * 0.4)
            
            # Build health (35% weight)
            if 'success_rate' in build_metrics:
                scores.append(build_metrics['success_rate'] * 0.35)
            
            # Deployment health (25% weight)
            if 'success_rate' in deployment_metrics:
                scores.append(deployment_metrics['success_rate'] * 0.25)
            
            return round(sum(scores), 2) if scores else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating health score: {str(e)}")
            return 0.0
    
    def _generate_recommendations(self, pipeline_metrics: Dict, build_metrics: Dict, deployment_metrics: Dict) -> List[str]:
        """Generate recommendations based on metrics."""
        recommendations = []
        
        try:
            # Pipeline recommendations
            if pipeline_metrics.get('success_rate', 100) < 80:
                recommendations.append("Pipeline success rate is low. Review failed executions and fix issues.")
            
            # Build recommendations
            if build_metrics.get('success_rate', 100) < 85:
                recommendations.append("Build success rate is low. Check build logs and dependencies.")
            
            if build_metrics.get('average_duration_seconds', 0) > 1800:
                recommendations.append("Build duration is high. Consider optimizing build process or increasing resources.")
            
            # Deployment recommendations
            if deployment_metrics.get('success_rate', 100) < 90:
                recommendations.append("Deployment success rate is low. Review deployment logs and configuration.")
            
            if not recommendations:
                recommendations.append("All systems are performing well. Continue monitoring.")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            recommendations.append("Error generating recommendations.")
        
        return recommendations


def main():
    """Main function for testing MonitoringManager."""
    # Example usage
    monitoring_manager = MonitoringManager()
    
    # Create SNS topic
    topic_arn = monitoring_manager.create_sns_topic('cicd-notifications')
    if topic_arn:
        print(f"SNS topic created: {topic_arn}")
        
        # Subscribe to topic
        subscription_arn = monitoring_manager.subscribe_to_topic(
            topic_arn, 'email', 'admin@example.com'
        )
        if subscription_arn:
            print(f"Subscription created: {subscription_arn}")
    
    # Create CI/CD dashboard
    dashboard_created = monitoring_manager.create_cicd_dashboard('test-project')
    print(f"Dashboard created: {dashboard_created}")
    
    # Generate monitoring report
    report = monitoring_manager.generate_monitoring_report('test-project')
    print(f"Monitoring report: {report}")


if __name__ == "__main__":
    main()