#!/usr/bin/env python3
"""
AWS Cost Monitor
Comprehensive cost monitoring with alerts, dashboards, and real-time tracking
"""

import boto3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from botocore.exceptions import ClientError
import pandas as pd


class CostMonitor:
    """Comprehensive AWS cost monitoring and alerting"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.ce_client = boto3.client('ce', region_name=region)
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=region)
        self.sns_client = boto3.client('sns', region_name=region)
        self.budgets_client = boto3.client('budgets', region_name=region)
        self.organizations_client = boto3.client('organizations', region_name=region)
        
    def create_cost_dashboard(self, dashboard_name: str, 
                            widgets: List[Dict[str, Any]] = None) -> bool:
        """Create CloudWatch cost dashboard"""
        try:
            if not widgets:
                widgets = self._get_default_cost_widgets()
            
            dashboard_body = {
                "widgets": widgets
            }
            
            self.cloudwatch_client.put_dashboard(
                DashboardName=dashboard_name,
                DashboardBody=json.dumps(dashboard_body)
            )
            return True
        except ClientError as e:
            print(f"Error creating cost dashboard: {e}")
            return False
    
    def create_cost_alarm(self, alarm_config: Dict[str, Any]) -> bool:
        """Create CloudWatch cost alarm"""
        try:
            self.cloudwatch_client.put_metric_alarm(
                AlarmName=alarm_config['AlarmName'],
                ComparisonOperator=alarm_config['ComparisonOperator'],
                EvaluationPeriods=alarm_config.get('EvaluationPeriods', 1),
                MetricName=alarm_config['MetricName'],
                Namespace=alarm_config['Namespace'],
                Period=alarm_config.get('Period', 300),
                Statistic=alarm_config.get('Statistic', 'Average'),
                Threshold=alarm_config['Threshold'],
                ActionsEnabled=alarm_config.get('ActionsEnabled', True),
                AlarmActions=alarm_config.get('AlarmActions', []),
                OKActions=alarm_config.get('OKActions', []),
                AlarmDescription=alarm_config.get('AlarmDescription', ''),
                Dimensions=alarm_config.get('Dimensions', [])
            )
            return True
        except ClientError as e:
            print(f"Error creating cost alarm: {e}")
            return False
    
    def create_daily_cost_alarm(self, threshold: float, 
                               sns_topic_arn: str = None) -> bool:
        """Create daily cost threshold alarm"""
        try:
            alarm_config = {
                'AlarmName': 'DailyCostThreshold',
                'ComparisonOperator': 'GreaterThanThreshold',
                'MetricName': 'EstimatedCharges',
                'Namespace': 'AWS/Billing',
                'Period': 86400,  # 24 hours
                'Statistic': 'Maximum',
                'Threshold': threshold,
                'AlarmDescription': f'Daily cost exceeds ${threshold}',
                'Dimensions': [
                    {
                        'Name': 'Currency',
                        'Value': 'USD'
                    }
                ]
            }
            
            if sns_topic_arn:
                alarm_config['AlarmActions'] = [sns_topic_arn]
            
            return self.create_cost_alarm(alarm_config)
        except Exception as e:
            print(f"Error creating daily cost alarm: {e}")
            return False
    
    def create_service_cost_alarm(self, service: str, threshold: float,
                                 sns_topic_arn: str = None) -> bool:
        """Create service-specific cost alarm"""
        try:
            alarm_config = {
                'AlarmName': f'{service}CostThreshold',
                'ComparisonOperator': 'GreaterThanThreshold',
                'MetricName': 'EstimatedCharges',
                'Namespace': 'AWS/Billing',
                'Period': 86400,
                'Statistic': 'Maximum',
                'Threshold': threshold,
                'AlarmDescription': f'{service} cost exceeds ${threshold}',
                'Dimensions': [
                    {
                        'Name': 'ServiceName',
                        'Value': service
                    },
                    {
                        'Name': 'Currency',
                        'Value': 'USD'
                    }
                ]
            }
            
            if sns_topic_arn:
                alarm_config['AlarmActions'] = [sns_topic_arn]
            
            return self.create_cost_alarm(alarm_config)
        except Exception as e:
            print(f"Error creating service cost alarm: {e}")
            return False
    
    def get_current_month_cost(self) -> Dict[str, Any]:
        """Get current month's cost breakdown"""
        try:
            # Get first day of current month
            first_day = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            today = datetime.now().strftime('%Y-%m-%d')
            
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={'Start': first_day, 'End': today},
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ]
            )
            
            total_cost = 0
            service_costs = {}
            daily_costs = []
            
            for result in response.get('ResultsByTime', []):
                date = result['TimePeriod']['Start']
                day_total = 0
                
                for group in result.get('Groups', []):
                    service = group['Keys'][0]
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    day_total += cost
                    total_cost += cost
                    
                    if service in service_costs:
                        service_costs[service] += cost
                    else:
                        service_costs[service] = cost
                
                daily_costs.append({
                    'date': date,
                    'cost': day_total
                })
            
            return {
                'total_cost': total_cost,
                'service_costs': service_costs,
                'daily_costs': daily_costs,
                'period': {'start': first_day, 'end': today}
            }
        except Exception as e:
            print(f"Error getting current month cost: {e}")
            return {}
    
    def get_cost_trend(self, days: int = 30) -> Dict[str, Any]:
        """Get cost trend over specified days"""
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={'Start': start_date, 'End': end_date},
                Granularity='DAILY',
                Metrics=['BlendedCost']
            )
            
            daily_costs = []
            total_cost = 0
            
            for result in response.get('ResultsByTime', []):
                date = result['TimePeriod']['Start']
                cost = float(result['Total']['BlendedCost']['Amount'])
                daily_costs.append({'date': date, 'cost': cost})
                total_cost += cost
            
            # Calculate trend
            if len(daily_costs) >= 2:
                first_half = daily_costs[:len(daily_costs)//2]
                second_half = daily_costs[len(daily_costs)//2:]
                
                first_avg = sum(day['cost'] for day in first_half) / len(first_half)
                second_avg = sum(day['cost'] for day in second_half) / len(second_half)
                
                trend_percentage = ((second_avg - first_avg) / first_avg) * 100 if first_avg > 0 else 0
            else:
                trend_percentage = 0
            
            return {
                'daily_costs': daily_costs,
                'total_cost': total_cost,
                'average_daily_cost': total_cost / len(daily_costs) if daily_costs else 0,
                'trend_percentage': trend_percentage,
                'period': {'start': start_date, 'end': end_date}
            }
        except Exception as e:
            print(f"Error getting cost trend: {e}")
            return {}
    
    def get_cost_forecast(self, days: int = 30) -> Dict[str, Any]:
        """Get cost forecast for next period"""
        try:
            start_date = datetime.now().strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            
            response = self.ce_client.get_cost_forecast(
                TimePeriod={'Start': start_date, 'End': end_date},
                Metric='BLENDED_COST',
                PredictionIntervalLowerBound=0.8,
                PredictionIntervalUpperBound=0.9
            )
            
            forecast = response.get('ForecastResultsByTime', [])
            total_forecast = sum(float(day['MeanValue']) for day in forecast)
            
            return {
                'forecast_data': forecast,
                'total_forecast': total_forecast,
                'average_daily_forecast': total_forecast / len(forecast) if forecast else 0,
                'period': {'start': start_date, 'end': end_date}
            }
        except Exception as e:
            print(f"Error getting cost forecast: {e}")
            return {}
    
    def get_cost_by_tag(self, tag_key: str, days: int = 30) -> Dict[str, Any]:
        """Get cost breakdown by tag"""
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={'Start': start_date, 'End': end_date},
                Granularity='MONTHLY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {'Type': 'TAG', 'Key': tag_key}
                ]
            )
            
            tag_costs = {}
            total_cost = 0
            
            for result in response.get('ResultsByTime', []):
                for group in result.get('Groups', []):
                    tag_value = group['Keys'][0] if group['Keys'][0] else 'No Tag'
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    total_cost += cost
                    
                    if tag_value in tag_costs:
                        tag_costs[tag_value] += cost
                    else:
                        tag_costs[tag_value] = cost
            
            return {
                'tag_costs': tag_costs,
                'total_cost': total_cost,
                'tag_key': tag_key,
                'period': {'start': start_date, 'end': end_date}
            }
        except Exception as e:
            print(f"Error getting cost by tag: {e}")
            return {}
    
    def get_cost_anomalies(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get cost anomalies and unusual spending"""
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            response = self.ce_client.get_anomalies(
                DateInterval={'Start': start_date, 'End': end_date}
            )
            
            anomalies = []
            for anomaly in response.get('Anomalies', []):
                anomalies.append({
                    'anomaly_id': anomaly.get('AnomalyId'),
                    'anomaly_start_date': anomaly.get('AnomalyStartDate'),
                    'anomaly_end_date': anomaly.get('AnomalyEndDate'),
                    'dimension': anomaly.get('Dimension'),
                    'anomaly_score': anomaly.get('AnomalyScore', {}).get('MaxScore', 0),
                    'impact': anomaly.get('Impact', {}).get('TotalImpact', {}).get('AbsoluteImpact', 0),
                    'root_causes': anomaly.get('RootCauses', [])
                })
            
            return anomalies
        except Exception as e:
            print(f"Error getting cost anomalies: {e}")
            return []
    
    def create_cost_report(self, report_config: Dict[str, Any]) -> bool:
        """Create cost and usage report"""
        try:
            self.ce_client.create_cost_category_definition(
                Name=report_config['Name'],
                Rules=report_config.get('Rules', []),
                RuleVersion=report_config.get('RuleVersion', 'CostCategoryExpression.v1')
            )
            return True
        except ClientError as e:
            print(f"Error creating cost report: {e}")
            return False
    
    def get_reservation_utilization(self, days: int = 30) -> Dict[str, Any]:
        """Get Reserved Instance utilization"""
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            response = self.ce_client.get_reservation_coverage(
                TimePeriod={'Start': start_date, 'End': end_date},
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ]
            )
            
            coverage_data = response.get('CoveragesByTime', [])
            total_coverage = 0
            
            for coverage in coverage_data:
                for group in coverage.get('Groups', []):
                    service = group['Keys'][0]
                    coverage_percentage = group['Coverage'].get('CoverageHours', {}).get('OnDemandCost', 0)
                    total_coverage += coverage_percentage
            
            return {
                'coverage_data': coverage_data,
                'total_coverage': total_coverage,
                'period': {'start': start_date, 'end': end_date}
            }
        except Exception as e:
            print(f"Error getting reservation utilization: {e}")
            return {}
    
    def create_cost_alert_sns_topic(self, topic_name: str) -> Optional[str]:
        """Create SNS topic for cost alerts"""
        try:
            response = self.sns_client.create_topic(Name=topic_name)
            return response['TopicArn']
        except ClientError as e:
            print(f"Error creating SNS topic: {e}")
            return None
    
    def subscribe_to_cost_alerts(self, topic_arn: str, email: str) -> bool:
        """Subscribe email to cost alerts"""
        try:
            response = self.sns_client.subscribe(
                TopicArn=topic_arn,
                Protocol='email',
                Endpoint=email
            )
            return 'SubscriptionArn' in response
        except ClientError as e:
            print(f"Error subscribing to cost alerts: {e}")
            return False
    
    def send_cost_alert(self, topic_arn: str, message: str, subject: str = None) -> bool:
        """Send cost alert via SNS"""
        try:
            if not subject:
                subject = "AWS Cost Alert"
            
            self.sns_client.publish(
                TopicArn=topic_arn,
                Message=message,
                Subject=subject
            )
            return True
        except ClientError as e:
            print(f"Error sending cost alert: {e}")
            return False
    
    def create_cost_budget_with_alerts(self, budget_name: str, amount: float,
                                     email: str, threshold_percentages: List[int] = None) -> bool:
        """Create budget with email alerts"""
        try:
            if not threshold_percentages:
                threshold_percentages = [80, 100]
            
            # Create SNS topic
            topic_arn = self.create_cost_alert_sns_topic(f"{budget_name}-alerts")
            if not topic_arn:
                return False
            
            # Subscribe email
            if not self.subscribe_to_cost_alerts(topic_arn, email):
                return False
            
            # Create budget
            budget_config = {
                'AccountId': self._get_account_id(),
                'BudgetName': budget_name,
                'BudgetLimit': {
                    'Amount': str(amount),
                    'Unit': 'USD'
                },
                'TimeUnit': 'MONTHLY',
                'BudgetType': 'COST',
                'TimePeriod': {
                    'Start': datetime.now().replace(day=1).strftime('%Y-%m-%d'),
                    'End': (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1).strftime('%Y-%m-%d')
                },
                'NotificationsWithSubscribers': []
            }
            
            # Add notifications for each threshold
            for threshold in threshold_percentages:
                budget_config['NotificationsWithSubscribers'].append({
                    'Notification': {
                        'NotificationType': 'ACTUAL',
                        'ComparisonOperator': 'GREATER_THAN',
                        'Threshold': threshold,
                        'ThresholdType': 'PERCENTAGE'
                    },
                    'Subscribers': [
                        {
                            'SubscriptionType': 'SNS',
                            'Address': topic_arn
                        }
                    ]
                })
            
            result = self.budgets_client.create_budget(**budget_config)
            return 'ResponseMetadata' in result
        except Exception as e:
            print(f"Error creating budget with alerts: {e}")
            return False
    
    def get_cost_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive cost summary"""
        try:
            current_month = self.get_current_month_cost()
            trend = self.get_cost_trend(days)
            forecast = self.get_cost_forecast(30)
            anomalies = self.get_cost_anomalies(days)
            
            return {
                'current_month': current_month,
                'trend': trend,
                'forecast': forecast,
                'anomalies': anomalies,
                'summary': {
                    'current_month_total': current_month.get('total_cost', 0),
                    'trend_percentage': trend.get('trend_percentage', 0),
                    'forecast_total': forecast.get('total_forecast', 0),
                    'anomaly_count': len(anomalies)
                }
            }
        except Exception as e:
            print(f"Error getting cost summary: {e}")
            return {}
    
    def _get_default_cost_widgets(self) -> List[Dict[str, Any]]:
        """Get default cost dashboard widgets"""
        return [
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/Billing", "EstimatedCharges", "Currency", "USD"]
                    ],
                    "period": 86400,
                    "stat": "Maximum",
                    "region": self.region,
                    "title": "Daily Estimated Charges"
                }
            },
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/Billing", "EstimatedCharges", "ServiceName", "Amazon Elastic Compute Cloud - Compute", "Currency", "USD"],
                        [".", ".", ".", "Amazon Simple Storage Service", ".", "."],
                        [".", ".", ".", "Amazon Relational Database Service", ".", "."]
                    ],
                    "period": 86400,
                    "stat": "Maximum",
                    "region": self.region,
                    "title": "Cost by Service"
                }
            }
        ]
    
    def _get_account_id(self) -> str:
        """Get current AWS account ID"""
        try:
            sts_client = boto3.client('sts')
            return sts_client.get_caller_identity()['Account']
        except Exception as e:
            print(f"Error getting account ID: {e}")
            return ""


# Example usage and testing
if __name__ == "__main__":
    # Initialize cost monitor
    monitor = CostMonitor()
    
    # Create cost dashboard
    monitor.create_cost_dashboard("AWS-Cost-Dashboard")
    
    # Get current month cost
    current_cost = monitor.get_current_month_cost()
    print(f"Current month cost: ${current_cost.get('total_cost', 0):.2f}")
    
    # Get cost trend
    trend = monitor.get_cost_trend(days=30)
    print(f"Cost trend: {trend.get('trend_percentage', 0):.1f}%")
    
    # Get cost forecast
    forecast = monitor.get_cost_forecast(days=30)
    print(f"30-day forecast: ${forecast.get('total_forecast', 0):.2f}")
    
    # Get cost anomalies
    anomalies = monitor.get_cost_anomalies(days=30)
    print(f"Cost anomalies found: {len(anomalies)}")
    
    # Create budget with alerts
    monitor.create_cost_budget_with_alerts(
        budget_name="MonthlyBudget",
        amount=1000.0,
        email="admin@company.com",
        threshold_percentages=[80, 100]
    )
    
    # Get comprehensive summary
    summary = monitor.get_cost_summary(days=30)
    print(f"Cost summary: {summary.get('summary', {})}")