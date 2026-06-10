#!/usr/bin/env python3
"""
AWS Budget Manager
Comprehensive budget management with cost tracking, alerts, and optimization recommendations
"""

import boto3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from botocore.exceptions import ClientError
import pandas as pd


class BudgetManager:
    """Manage AWS budgets with comprehensive cost tracking and optimization"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.budgets_client = boto3.client('budgets', region_name=region)
        self.ce_client = boto3.client('ce', region_name=region)
        self.organizations_client = boto3.client('organizations', region_name=region)
        self.sns_client = boto3.client('sns', region_name=region)
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=region)
        
    def create_budget(self, budget_config: Dict[str, Any]) -> Optional[str]:
        """Create AWS budget"""
        try:
            response = self.budgets_client.create_budget(
                AccountId=budget_config['AccountId'],
                Budget={
                    'BudgetName': budget_config['BudgetName'],
                    'BudgetLimit': budget_config['BudgetLimit'],
                    'TimeUnit': budget_config['TimeUnit'],
                    'BudgetType': budget_config['BudgetType'],
                    'CostFilters': budget_config.get('CostFilters', {}),
                    'TimePeriod': budget_config.get('TimePeriod', {}),
                    'CalculatedSpend': budget_config.get('CalculatedSpend', {}),
                    'PlannedBudgetLimits': budget_config.get('PlannedBudgetLimits', {}),
                    'CostTypes': budget_config.get('CostTypes', {}),
                    'LastUpdatedTime': budget_config.get('LastUpdatedTime')
                },
                NotificationsWithSubscribers=budget_config.get('NotificationsWithSubscribers', [])
            )
            return response['ResponseMetadata']['RequestId']
        except ClientError as e:
            print(f"Error creating budget: {e}")
            return None
    
    def create_cost_budget(self, budget_name: str, amount: float, 
                          time_unit: str = 'MONTHLY', 
                          subscribers: List[Dict[str, str]] = None) -> bool:
        """Create a simple cost budget"""
        try:
            budget_config = {
                'AccountId': self._get_account_id(),
                'BudgetName': budget_name,
                'BudgetLimit': {
                    'Amount': str(amount),
                    'Unit': 'USD'
                },
                'TimeUnit': time_unit,
                'BudgetType': 'COST',
                'CostFilters': {},
                'TimePeriod': {
                    'Start': datetime.now().replace(day=1).strftime('%Y-%m-%d'),
                    'End': (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1).strftime('%Y-%m-%d')
                }
            }
            
            if subscribers:
                budget_config['NotificationsWithSubscribers'] = [
                    {
                        'Notification': {
                            'NotificationType': 'ACTUAL',
                            'ComparisonOperator': 'GREATER_THAN',
                            'Threshold': 80,
                            'ThresholdType': 'PERCENTAGE'
                        },
                        'Subscribers': subscribers
                    },
                    {
                        'Notification': {
                            'NotificationType': 'ACTUAL',
                            'ComparisonOperator': 'GREATER_THAN',
                            'Threshold': 100,
                            'ThresholdType': 'PERCENTAGE'
                        },
                        'Subscribers': subscribers
                    }
                ]
            
            result = self.create_budget(budget_config)
            return result is not None
        except Exception as e:
            print(f"Error creating cost budget: {e}")
            return False
    
    def create_usage_budget(self, budget_name: str, service: str, 
                           limit: float, time_unit: str = 'MONTHLY',
                           subscribers: List[Dict[str, str]] = None) -> bool:
        """Create a usage budget for specific service"""
        try:
            budget_config = {
                'AccountId': self._get_account_id(),
                'BudgetName': budget_name,
                'BudgetLimit': {
                    'Amount': str(limit),
                    'Unit': 'USD'
                },
                'TimeUnit': time_unit,
                'BudgetType': 'USAGE',
                'CostFilters': {
                    'Service': [service]
                },
                'TimePeriod': {
                    'Start': datetime.now().replace(day=1).strftime('%Y-%m-%d'),
                    'End': (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1).strftime('%Y-%m-%d')
                }
            }
            
            if subscribers:
                budget_config['NotificationsWithSubscribers'] = [
                    {
                        'Notification': {
                            'NotificationType': 'ACTUAL',
                            'ComparisonOperator': 'GREATER_THAN',
                            'Threshold': 80,
                            'ThresholdType': 'PERCENTAGE'
                        },
                        'Subscribers': subscribers
                    }
                ]
            
            result = self.create_budget(budget_config)
            return result is not None
        except Exception as e:
            print(f"Error creating usage budget: {e}")
            return False
    
    def create_ri_budget(self, budget_name: str, amount: float,
                        time_unit: str = 'MONTHLY',
                        subscribers: List[Dict[str, str]] = None) -> bool:
        """Create Reserved Instance budget"""
        try:
            budget_config = {
                'AccountId': self._get_account_id(),
                'BudgetName': budget_name,
                'BudgetLimit': {
                    'Amount': str(amount),
                    'Unit': 'USD'
                },
                'TimeUnit': time_unit,
                'BudgetType': 'RI_UTILIZATION',
                'CostFilters': {},
                'TimePeriod': {
                    'Start': datetime.now().replace(day=1).strftime('%Y-%m-%d'),
                    'End': (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1).strftime('%Y-%m-%d')
                }
            }
            
            if subscribers:
                budget_config['NotificationsWithSubscribers'] = [
                    {
                        'Notification': {
                            'NotificationType': 'ACTUAL',
                            'ComparisonOperator': 'LESS_THAN',
                            'Threshold': 70,
                            'ThresholdType': 'PERCENTAGE'
                        },
                        'Subscribers': subscribers
                    }
                ]
            
            result = self.create_budget(budget_config)
            return result is not None
        except Exception as e:
            print(f"Error creating RI budget: {e}")
            return False
    
    def get_budget(self, budget_name: str) -> Optional[Dict[str, Any]]:
        """Get budget details"""
        try:
            response = self.budgets_client.describe_budget(
                AccountId=self._get_account_id(),
                BudgetName=budget_name
            )
            return response['Budget']
        except ClientError as e:
            print(f"Error getting budget: {e}")
            return None
    
    def list_budgets(self) -> List[Dict[str, Any]]:
        """List all budgets"""
        try:
            response = self.budgets_client.describe_budgets(
                AccountId=self._get_account_id()
            )
            return response['Budgets']
        except ClientError as e:
            print(f"Error listing budgets: {e}")
            return []
    
    def update_budget(self, budget_name: str, budget_config: Dict[str, Any]) -> bool:
        """Update existing budget"""
        try:
            self.budgets_client.update_budget(
                AccountId=self._get_account_id(),
                NewBudget=budget_config
            )
            return True
        except ClientError as e:
            print(f"Error updating budget: {e}")
            return False
    
    def delete_budget(self, budget_name: str) -> bool:
        """Delete budget"""
        try:
            self.budgets_client.delete_budget(
                AccountId=self._get_account_id(),
                BudgetName=budget_name
            )
            return True
        except ClientError as e:
            print(f"Error deleting budget: {e}")
            return False
    
    def get_cost_and_usage(self, start_date: str, end_date: str, 
                          granularity: str = 'MONTHLY',
                          metrics: List[str] = None) -> Dict[str, Any]:
        """Get cost and usage data"""
        try:
            if not metrics:
                metrics = ['BlendedCost', 'UnblendedCost', 'UsageQuantity']
            
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity=granularity,
                Metrics=metrics,
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )
            return response
        except ClientError as e:
            print(f"Error getting cost and usage: {e}")
            return {}
    
    def get_cost_by_service(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get cost breakdown by service"""
        try:
            response = self.get_cost_and_usage(start_date, end_date)
            
            data = []
            for result in response.get('ResultsByTime', []):
                for group in result.get('Groups', []):
                    service = group['Keys'][0]
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    data.append({
                        'Service': service,
                        'Cost': cost,
                        'Date': result['TimePeriod']['Start']
                    })
            
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error getting cost by service: {e}")
            return pd.DataFrame()
    
    def get_cost_by_tag(self, start_date: str, end_date: str, 
                       tag_key: str) -> pd.DataFrame:
        """Get cost breakdown by tag"""
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='MONTHLY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {
                        'Type': 'TAG',
                        'Key': tag_key
                    }
                ]
            )
            
            data = []
            for result in response.get('ResultsByTime', []):
                for group in result.get('Groups', []):
                    tag_value = group['Keys'][0] if group['Keys'][0] else 'No Tag'
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    data.append({
                        'Tag': tag_value,
                        'Cost': cost,
                        'Date': result['TimePeriod']['Start']
                    })
            
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error getting cost by tag: {e}")
            return pd.DataFrame()
    
    def get_cost_forecast(self, start_date: str, end_date: str,
                         metric: str = 'BLENDED_COST',
                         prediction_interval_lower_bound: float = 0.8,
                         prediction_interval_upper_bound: float = 0.9) -> Dict[str, Any]:
        """Get cost forecast"""
        try:
            response = self.ce_client.get_cost_forecast(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Metric=metric,
                PredictionIntervalLowerBound=prediction_interval_lower_bound,
                PredictionIntervalUpperBound=prediction_interval_upper_bound
            )
            return response
        except ClientError as e:
            print(f"Error getting cost forecast: {e}")
            return {}
    
    def get_reservation_coverage(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get Reserved Instance coverage"""
        try:
            response = self.ce_client.get_reservation_coverage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )
            return response
        except ClientError as e:
            print(f"Error getting reservation coverage: {e}")
            return {}
    
    def get_reservation_purchase_recommendation(self, service: str = 'EC2',
                                              lookback_period: str = 'THIRTY_DAYS',
                                              term_in_years: str = 'ONE_YEAR',
                                              payment_option: str = 'NO_UPFRONT') -> Dict[str, Any]:
        """Get Reserved Instance purchase recommendations"""
        try:
            response = self.ce_client.get_reservation_purchase_recommendation(
                Service=service,
                LookbackPeriodInDays=lookback_period,
                TermInYears=term_in_years,
                PaymentOption=payment_option
            )
            return response
        except ClientError as e:
            print(f"Error getting reservation recommendations: {e}")
            return {}
    
    def get_rightsizing_recommendation(self, service: str = 'EC2') -> Dict[str, Any]:
        """Get rightsizing recommendations"""
        try:
            response = self.ce_client.get_rightsizing_recommendation(
                Service=service
            )
            return response
        except ClientError as e:
            print(f"Error getting rightsizing recommendations: {e}")
            return {}
    
    def create_cost_anomaly_detection(self, anomaly_config: Dict[str, Any]) -> Optional[str]:
        """Create cost anomaly detection"""
        try:
            response = self.ce_client.create_anomaly_detector(
                AnomalyDetector=anomaly_config
            )
            return response['AnomalyDetectorArn']
        except ClientError as e:
            print(f"Error creating cost anomaly detection: {e}")
            return None
    
    def get_cost_anomalies(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get cost anomalies"""
        try:
            response = self.ce_client.get_anomalies(
                DateInterval={
                    'Start': start_date,
                    'End': end_date
                }
            )
            return response.get('Anomalies', [])
        except ClientError as e:
            print(f"Error getting cost anomalies: {e}")
            return []
    
    def create_savings_plans_recommendation(self, savings_plans_type: str = 'COMPUTE_SP',
                                          term_in_years: str = 'ONE_YEAR',
                                          payment_option: str = 'NO_UPFRONT') -> Dict[str, Any]:
        """Get Savings Plans recommendations"""
        try:
            response = self.ce_client.get_savings_plans_purchase_recommendation(
                SavingsPlansType=savings_plans_type,
                TermInYears=term_in_years,
                PaymentOption=payment_option
            )
            return response
        except ClientError as e:
            print(f"Error getting savings plans recommendations: {e}")
            return {}
    
    def get_utilization_report(self, service: str = 'EC2') -> Dict[str, Any]:
        """Get resource utilization report"""
        try:
            # This would typically use CloudWatch metrics
            # For now, return a placeholder structure
            return {
                'Service': service,
                'Utilization': 'N/A - Use CloudWatch metrics for detailed utilization',
                'Recommendations': 'Enable detailed monitoring for utilization insights'
            }
        except Exception as e:
            print(f"Error getting utilization report: {e}")
            return {}
    
    def create_cost_allocation_tags(self, tag_keys: List[str]) -> bool:
        """Create cost allocation tags"""
        try:
            self.ce_client.create_cost_category_definition(
                Name='CostAllocation',
                Rules=[
                    {
                        'Value': tag_key,
                        'Rule': {
                            'Dimension': {
                                'Key': 'TAG',
                                'Values': [tag_key]
                            }
                        }
                    } for tag_key in tag_keys
                ]
            )
            return True
        except ClientError as e:
            print(f"Error creating cost allocation tags: {e}")
            return False
    
    def get_cost_optimization_recommendations(self) -> Dict[str, Any]:
        """Get comprehensive cost optimization recommendations"""
        try:
            recommendations = {
                'reserved_instances': self.get_reservation_purchase_recommendation(),
                'rightsizing': self.get_rightsizing_recommendation(),
                'savings_plans': self.create_savings_plans_recommendation(),
                'anomalies': self.get_cost_anomalies(
                    (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                    datetime.now().strftime('%Y-%m-%d')
                )
            }
            return recommendations
        except Exception as e:
            print(f"Error getting optimization recommendations: {e}")
            return {}
    
    def create_cost_dashboard_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Create data for cost dashboard"""
        try:
            # Get cost by service
            cost_by_service = self.get_cost_by_service(start_date, end_date)
            
            # Get cost forecast
            forecast = self.get_cost_forecast(start_date, end_date)
            
            # Get total cost
            total_cost = cost_by_service['Cost'].sum() if not cost_by_service.empty else 0
            
            # Get top services
            top_services = cost_by_service.groupby('Service')['Cost'].sum().nlargest(10).to_dict()
            
            dashboard_data = {
                'total_cost': total_cost,
                'cost_by_service': top_services,
                'forecast': forecast,
                'period': {
                    'start': start_date,
                    'end': end_date
                },
                'generated_at': datetime.now().isoformat()
            }
            
            return dashboard_data
        except Exception as e:
            print(f"Error creating dashboard data: {e}")
            return {}
    
    def export_cost_data(self, start_date: str, end_date: str, 
                        s3_bucket: str, s3_prefix: str = 'cost-data/') -> bool:
        """Export cost data to S3"""
        try:
            # This would typically use Cost Explorer's export feature
            # For now, we'll create a summary and save it
            cost_data = self.get_cost_by_service(start_date, end_date)
            
            if not cost_data.empty:
                # Save to local file (in real implementation, upload to S3)
                filename = f"cost_data_{start_date}_{end_date}.csv"
                cost_data.to_csv(filename, index=False)
                print(f"Cost data exported to {filename}")
                return True
            
            return False
        except Exception as e:
            print(f"Error exporting cost data: {e}")
            return False
    
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
    # Initialize budget manager
    budget_manager = BudgetManager()
    
    # Create a monthly cost budget
    budget_manager.create_cost_budget(
        budget_name="MonthlyCostBudget",
        amount=1000.0,
        time_unit="MONTHLY",
        subscribers=[
            {
                "SubscriptionType": "EMAIL",
                "Address": "admin@company.com"
            }
        ]
    )
    
    # Get cost data for last month
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    cost_data = budget_manager.get_cost_by_service(start_date, end_date)
    print(f"Cost by service:\n{cost_data}")
    
    # Get optimization recommendations
    recommendations = budget_manager.get_cost_optimization_recommendations()
    print(f"Optimization recommendations: {recommendations}")
    
    # Create dashboard data
    dashboard_data = budget_manager.create_cost_dashboard_data(start_date, end_date)
    print(f"Dashboard data: {dashboard_data}")