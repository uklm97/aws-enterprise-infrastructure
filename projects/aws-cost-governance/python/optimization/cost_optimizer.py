#!/usr/bin/env python3
"""
AWS Cost Optimizer
Comprehensive cost optimization with recommendations, analysis, and automated actions
"""

import boto3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from botocore.exceptions import ClientError
import pandas as pd


class CostOptimizer:
    """Comprehensive AWS cost optimization and analysis"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.ce_client = boto3.client('ce', region_name=region)
        self.ec2_client = boto3.client('ec2', region_name=region)
        self.rds_client = boto3.client('rds', region_name=region)
        self.elasticache_client = boto3.client('elasticache', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=region)
        self.organizations_client = boto3.client('organizations', region_name=region)
        
    def analyze_ec2_costs(self, days: int = 30) -> Dict[str, Any]:
        """Analyze EC2 costs and provide optimization recommendations"""
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Get EC2 cost data
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={'Start': start_date, 'End': end_date},
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'INSTANCE_TYPE'}
                ],
                Filter={
                    'Dimensions': {
                        'Key': 'SERVICE',
                        'Values': ['Amazon Elastic Compute Cloud - Compute']
                    }
                }
            )
            
            # Analyze data
            total_cost = 0
            instance_costs = {}
            
            for result in response.get('ResultsByTime', []):
                for group in result.get('Groups', []):
                    instance_type = group['Keys'][1] if len(group['Keys']) > 1 else 'Unknown'
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    total_cost += cost
                    
                    if instance_type in instance_costs:
                        instance_costs[instance_type] += cost
                    else:
                        instance_costs[instance_type] = cost
            
            # Get current instances
            instances = self._get_ec2_instances()
            
            # Generate recommendations
            recommendations = self._generate_ec2_recommendations(instances, instance_costs)
            
            return {
                'total_cost': total_cost,
                'instance_costs': instance_costs,
                'instances': instances,
                'recommendations': recommendations,
                'period': {'start': start_date, 'end': end_date}
            }
        except Exception as e:
            print(f"Error analyzing EC2 costs: {e}")
            return {}
    
    def analyze_rds_costs(self, days: int = 30) -> Dict[str, Any]:
        """Analyze RDS costs and provide optimization recommendations"""
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Get RDS cost data
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={'Start': start_date, 'End': end_date},
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'DATABASE_ENGINE'}
                ],
                Filter={
                    'Dimensions': {
                        'Key': 'SERVICE',
                        'Values': ['Amazon Relational Database Service']
                    }
                }
            )
            
            total_cost = 0
            engine_costs = {}
            
            for result in response.get('ResultsByTime', []):
                for group in result.get('Groups', []):
                    engine = group['Keys'][1] if len(group['Keys']) > 1 else 'Unknown'
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    total_cost += cost
                    
                    if engine in engine_costs:
                        engine_costs[engine] += cost
                    else:
                        engine_costs[engine] = cost
            
            # Get current RDS instances
            rds_instances = self._get_rds_instances()
            
            # Generate recommendations
            recommendations = self._generate_rds_recommendations(rds_instances, engine_costs)
            
            return {
                'total_cost': total_cost,
                'engine_costs': engine_costs,
                'instances': rds_instances,
                'recommendations': recommendations,
                'period': {'start': start_date, 'end': end_date}
            }
        except Exception as e:
            print(f"Error analyzing RDS costs: {e}")
            return {}
    
    def analyze_storage_costs(self, days: int = 30) -> Dict[str, Any]:
        """Analyze storage costs across services"""
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Get storage cost data
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={'Start': start_date, 'End': end_date},
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'}
                ],
                Filter={
                    'Or': [
                        {'Dimensions': {'Key': 'SERVICE', 'Values': ['Amazon Simple Storage Service']}},
                        {'Dimensions': {'Key': 'SERVICE', 'Values': ['Amazon Elastic Block Store']}},
                        {'Dimensions': {'Key': 'SERVICE', 'Values': ['Amazon Elastic File System']}}
                    ]
                }
            )
            
            total_cost = 0
            service_costs = {}
            usage_costs = {}
            
            for result in response.get('ResultsByTime', []):
                for group in result.get('Groups', []):
                    service = group['Keys'][0]
                    usage_type = group['Keys'][1] if len(group['Keys']) > 1 else 'Unknown'
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    total_cost += cost
                    
                    if service in service_costs:
                        service_costs[service] += cost
                    else:
                        service_costs[service] = cost
                    
                    if usage_type in usage_costs:
                        usage_costs[usage_type] += cost
                    else:
                        usage_costs[usage_type] = cost
            
            # Generate recommendations
            recommendations = self._generate_storage_recommendations(service_costs, usage_costs)
            
            return {
                'total_cost': total_cost,
                'service_costs': service_costs,
                'usage_costs': usage_costs,
                'recommendations': recommendations,
                'period': {'start': start_date, 'end': end_date}
            }
        except Exception as e:
            print(f"Error analyzing storage costs: {e}")
            return {}
    
    def analyze_lambda_costs(self, days: int = 30) -> Dict[str, Any]:
        """Analyze Lambda costs and provide optimization recommendations"""
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Get Lambda cost data
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={'Start': start_date, 'End': end_date},
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ],
                Filter={
                    'Dimensions': {
                        'Key': 'SERVICE',
                        'Values': ['AWS Lambda']
                    }
                }
            )
            
            total_cost = 0
            for result in response.get('ResultsByTime', []):
                for group in result.get('Groups', []):
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    total_cost += cost
            
            # Get Lambda functions
            functions = self._get_lambda_functions()
            
            # Analyze function metrics
            function_analysis = self._analyze_lambda_functions(functions)
            
            # Generate recommendations
            recommendations = self._generate_lambda_recommendations(function_analysis)
            
            return {
                'total_cost': total_cost,
                'functions': functions,
                'analysis': function_analysis,
                'recommendations': recommendations,
                'period': {'start': start_date, 'end': end_date}
            }
        except Exception as e:
            print(f"Error analyzing Lambda costs: {e}")
            return {}
    
    def get_reserved_instance_recommendations(self) -> Dict[str, Any]:
        """Get Reserved Instance purchase recommendations"""
        try:
            # Get EC2 RI recommendations
            ec2_recommendations = self.ce_client.get_reservation_purchase_recommendation(
                Service='EC2',
                LookbackPeriodInDays='THIRTY_DAYS',
                TermInYears='ONE_YEAR',
                PaymentOption='NO_UPFRONT'
            )
            
            # Get RDS RI recommendations
            rds_recommendations = self.ce_client.get_reservation_purchase_recommendation(
                Service='RDS',
                LookbackPeriodInDays='THIRTY_DAYS',
                TermInYears='ONE_YEAR',
                PaymentOption='NO_UPFRONT'
            )
            
            return {
                'ec2_recommendations': ec2_recommendations,
                'rds_recommendations': rds_recommendations,
                'total_potential_savings': self._calculate_ri_savings(ec2_recommendations, rds_recommendations)
            }
        except Exception as e:
            print(f"Error getting RI recommendations: {e}")
            return {}
    
    def get_rightsizing_recommendations(self) -> Dict[str, Any]:
        """Get rightsizing recommendations for EC2 instances"""
        try:
            response = self.ce_client.get_rightsizing_recommendation(
                Service='EC2'
            )
            
            recommendations = []
            total_potential_savings = 0
            
            for recommendation in response.get('RightsizingRecommendations', []):
                current_instance = recommendation.get('CurrentInstance', {})
                recommended_instance = recommendation.get('TargetInstances', [{}])[0]
                
                savings = float(recommendation.get('EstimatedMonthlySavings', '0'))
                total_potential_savings += savings
                
                recommendations.append({
                    'instance_id': current_instance.get('InstanceId'),
                    'current_type': current_instance.get('InstanceType'),
                    'recommended_type': recommended_instance.get('InstanceType'),
                    'monthly_savings': savings,
                    'reason': recommendation.get('RightsizingType')
                })
            
            return {
                'recommendations': recommendations,
                'total_potential_savings': total_potential_savings,
                'count': len(recommendations)
            }
        except Exception as e:
            print(f"Error getting rightsizing recommendations: {e}")
            return {}
    
    def get_savings_plans_recommendations(self) -> Dict[str, Any]:
        """Get Savings Plans recommendations"""
        try:
            # Compute Savings Plans
            compute_sp = self.ce_client.get_savings_plans_purchase_recommendation(
                SavingsPlansType='COMPUTE_SP',
                TermInYears='ONE_YEAR',
                PaymentOption='NO_UPFRONT'
            )
            
            # EC2 Instance Savings Plans
            ec2_sp = self.ce_client.get_savings_plans_purchase_recommendation(
                SavingsPlansType='EC2_INSTANCE_SP',
                TermInYears='ONE_YEAR',
                PaymentOption='NO_UPFRONT'
            )
            
            return {
                'compute_savings_plans': compute_sp,
                'ec2_savings_plans': ec2_sp,
                'total_potential_savings': self._calculate_sp_savings(compute_sp, ec2_sp)
            }
        except Exception as e:
            print(f"Error getting Savings Plans recommendations: {e}")
            return {}
    
    def identify_unused_resources(self) -> Dict[str, Any]:
        """Identify unused or underutilized resources"""
        try:
            unused_resources = {
                'unused_volumes': self._find_unused_volumes(),
                'unused_snapshots': self._find_unused_snapshots(),
                'unused_elastic_ips': self._find_unused_elastic_ips(),
                'unused_load_balancers': self._find_unused_load_balancers(),
                'unused_nat_gateways': self._find_unused_nat_gateways(),
                'unused_elastic_ips': self._find_unused_elastic_ips()
            }
            
            # Calculate potential savings
            total_savings = sum(resource.get('monthly_cost', 0) for resource in unused_resources.values())
            
            return {
                'resources': unused_resources,
                'total_monthly_savings': total_savings,
                'recommendations': self._generate_cleanup_recommendations(unused_resources)
            }
        except Exception as e:
            print(f"Error identifying unused resources: {e}")
            return {}
    
    def get_cost_anomalies(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get cost anomalies and unusual spending patterns"""
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
                    'root_cause': anomaly.get('RootCauses', [])
                })
            
            return anomalies
        except Exception as e:
            print(f"Error getting cost anomalies: {e}")
            return []
    
    def generate_optimization_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive cost optimization report"""
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'analysis_period_days': days,
                'ec2_analysis': self.analyze_ec2_costs(days),
                'rds_analysis': self.analyze_rds_costs(days),
                'storage_analysis': self.analyze_storage_costs(days),
                'lambda_analysis': self.analyze_lambda_costs(days),
                'reserved_instance_recommendations': self.get_reserved_instance_recommendations(),
                'rightsizing_recommendations': self.get_rightsizing_recommendations(),
                'savings_plans_recommendations': self.get_savings_plans_recommendations(),
                'unused_resources': self.identify_unused_resources(),
                'cost_anomalies': self.get_cost_anomalies(days)
            }
            
            # Calculate total potential savings
            total_savings = 0
            total_savings += report['reserved_instance_recommendations'].get('total_potential_savings', 0)
            total_savings += report['rightsizing_recommendations'].get('total_potential_savings', 0)
            total_savings += report['savings_plans_recommendations'].get('total_potential_savings', 0)
            total_savings += report['unused_resources'].get('total_monthly_savings', 0)
            
            report['total_potential_monthly_savings'] = total_savings
            
            return report
        except Exception as e:
            print(f"Error generating optimization report: {e}")
            return {}
    
    def _get_ec2_instances(self) -> List[Dict[str, Any]]:
        """Get current EC2 instances"""
        try:
            response = self.ec2_client.describe_instances()
            instances = []
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append({
                        'instance_id': instance['InstanceId'],
                        'instance_type': instance['InstanceType'],
                        'state': instance['State']['Name'],
                        'launch_time': instance['LaunchTime'],
                        'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                    })
            
            return instances
        except Exception as e:
            print(f"Error getting EC2 instances: {e}")
            return []
    
    def _get_rds_instances(self) -> List[Dict[str, Any]]:
        """Get current RDS instances"""
        try:
            response = self.rds_client.describe_db_instances()
            instances = []
            
            for instance in response['DBInstances']:
                instances.append({
                    'db_instance_identifier': instance['DBInstanceIdentifier'],
                    'engine': instance['Engine'],
                    'instance_class': instance['DBInstanceClass'],
                    'allocated_storage': instance['AllocatedStorage'],
                    'multi_az': instance['MultiAZ'],
                    'tags': {tag['Key']: tag['Value'] for tag in instance.get('TagList', [])}
                })
            
            return instances
        except Exception as e:
            print(f"Error getting RDS instances: {e}")
            return []
    
    def _get_lambda_functions(self) -> List[Dict[str, Any]]:
        """Get Lambda functions"""
        try:
            response = self.lambda_client.list_functions()
            functions = []
            
            for function in response['Functions']:
                functions.append({
                    'function_name': function['FunctionName'],
                    'runtime': function['Runtime'],
                    'memory_size': function['MemorySize'],
                    'timeout': function['Timeout'],
                    'last_modified': function['LastModified']
                })
            
            return functions
        except Exception as e:
            print(f"Error getting Lambda functions: {e}")
            return []
    
    def _analyze_lambda_functions(self, functions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze Lambda function performance and costs"""
        analysis = {
            'total_functions': len(functions),
            'high_memory_functions': [],
            'long_timeout_functions': [],
            'old_runtime_functions': []
        }
        
        for function in functions:
            # Check for high memory allocation
            if function['memory_size'] > 1024:
                analysis['high_memory_functions'].append(function)
            
            # Check for long timeouts
            if function['timeout'] > 300:
                analysis['long_timeout_functions'].append(function)
            
            # Check for old runtimes
            if function['runtime'].startswith('python2') or function['runtime'].startswith('nodejs6'):
                analysis['old_runtime_functions'].append(function)
        
        return analysis
    
    def _generate_ec2_recommendations(self, instances: List[Dict[str, Any]], 
                                    instance_costs: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate EC2 optimization recommendations"""
        recommendations = []
        
        # Check for running instances with high costs
        for instance in instances:
            if instance['state'] == 'running':
                instance_type = instance['instance_type']
                if instance_type in instance_costs and instance_costs[instance_type] > 100:
                    recommendations.append({
                        'type': 'high_cost_instance',
                        'instance_id': instance['instance_id'],
                        'instance_type': instance_type,
                        'monthly_cost': instance_costs[instance_type],
                        'recommendation': 'Consider Reserved Instances or rightsizing'
                    })
        
        return recommendations
    
    def _generate_rds_recommendations(self, instances: List[Dict[str, Any]], 
                                    engine_costs: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate RDS optimization recommendations"""
        recommendations = []
        
        for instance in instances:
            if instance['engine'] in engine_costs and engine_costs[instance['engine']] > 50:
                recommendations.append({
                    'type': 'high_cost_rds',
                    'instance_id': instance['db_instance_identifier'],
                    'engine': instance['engine'],
                    'instance_class': instance['instance_class'],
                    'monthly_cost': engine_costs[instance['engine']],
                    'recommendation': 'Consider Reserved Instances or Aurora Serverless'
                })
        
        return recommendations
    
    def _generate_storage_recommendations(self, service_costs: Dict[str, float], 
                                        usage_costs: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate storage optimization recommendations"""
        recommendations = []
        
        # Check for expensive storage types
        for usage_type, cost in usage_costs.items():
            if cost > 50:
                if 'Standard' in usage_type and 'IA' not in usage_type:
                    recommendations.append({
                        'type': 'storage_optimization',
                        'usage_type': usage_type,
                        'monthly_cost': cost,
                        'recommendation': 'Consider moving to Infrequent Access or Glacier'
                    })
        
        return recommendations
    
    def _generate_lambda_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate Lambda optimization recommendations"""
        recommendations = []
        
        # High memory functions
        for function in analysis['high_memory_functions']:
            recommendations.append({
                'type': 'lambda_memory_optimization',
                'function_name': function['function_name'],
                'current_memory': function['memory_size'],
                'recommendation': 'Consider reducing memory allocation if not needed'
            })
        
        # Long timeout functions
        for function in analysis['long_timeout_functions']:
            recommendations.append({
                'type': 'lambda_timeout_optimization',
                'function_name': function['function_name'],
                'current_timeout': function['timeout'],
                'recommendation': 'Consider reducing timeout or using Step Functions for long-running tasks'
            })
        
        return recommendations
    
    def _calculate_ri_savings(self, ec2_recs: Dict[str, Any], rds_recs: Dict[str, Any]) -> float:
        """Calculate potential RI savings"""
        total_savings = 0
        
        if 'Recommendations' in ec2_recs:
            for rec in ec2_recs['Recommendations']:
                total_savings += float(rec.get('EstimatedMonthlySavings', 0))
        
        if 'Recommendations' in rds_recs:
            for rec in rds_recs['Recommendations']:
                total_savings += float(rec.get('EstimatedMonthlySavings', 0))
        
        return total_savings
    
    def _calculate_sp_savings(self, compute_sp: Dict[str, Any], ec2_sp: Dict[str, Any]) -> float:
        """Calculate potential Savings Plans savings"""
        total_savings = 0
        
        if 'SavingsPlansPurchaseRecommendation' in compute_sp:
            rec = compute_sp['SavingsPlansPurchaseRecommendation']
            total_savings += float(rec.get('SavingsPlansDetails', {}).get('EstimatedMonthlySavings', 0))
        
        if 'SavingsPlansPurchaseRecommendation' in ec2_sp:
            rec = ec2_sp['SavingsPlansPurchaseRecommendation']
            total_savings += float(rec.get('SavingsPlansDetails', {}).get('EstimatedMonthlySavings', 0))
        
        return total_savings
    
    def _find_unused_volumes(self) -> Dict[str, Any]:
        """Find unused EBS volumes"""
        try:
            response = self.ec2_client.describe_volumes(
                Filters=[{'Name': 'status', 'Values': ['available']}]
            )
            
            unused_volumes = []
            total_cost = 0
            
            for volume in response['Volumes']:
                # Calculate monthly cost (simplified)
                size_gb = volume['Size']
                monthly_cost = size_gb * 0.10  # $0.10 per GB per month
                total_cost += monthly_cost
                
                unused_volumes.append({
                    'volume_id': volume['VolumeId'],
                    'size_gb': size_gb,
                    'monthly_cost': monthly_cost,
                    'created': volume['CreateTime']
                })
            
            return {
                'volumes': unused_volumes,
                'count': len(unused_volumes),
                'monthly_cost': total_cost
            }
        except Exception as e:
            print(f"Error finding unused volumes: {e}")
            return {'volumes': [], 'count': 0, 'monthly_cost': 0}
    
    def _find_unused_snapshots(self) -> Dict[str, Any]:
        """Find old/unused snapshots"""
        try:
            response = self.ec2_client.describe_snapshots(OwnerIds=['self'])
            
            old_snapshots = []
            total_cost = 0
            
            cutoff_date = datetime.now() - timedelta(days=90)
            
            for snapshot in response['Snapshots']:
                if snapshot['StartTime'].replace(tzinfo=None) < cutoff_date:
                    # Calculate monthly cost (simplified)
                    size_gb = snapshot['VolumeSize']
                    monthly_cost = size_gb * 0.05  # $0.05 per GB per month
                    total_cost += monthly_cost
                    
                    old_snapshots.append({
                        'snapshot_id': snapshot['SnapshotId'],
                        'size_gb': size_gb,
                        'monthly_cost': monthly_cost,
                        'created': snapshot['StartTime']
                    })
            
            return {
                'snapshots': old_snapshots,
                'count': len(old_snapshots),
                'monthly_cost': total_cost
            }
        except Exception as e:
            print(f"Error finding unused snapshots: {e}")
            return {'snapshots': [], 'count': 0, 'monthly_cost': 0}
    
    def _find_unused_elastic_ips(self) -> Dict[str, Any]:
        """Find unused Elastic IPs"""
        try:
            response = self.ec2_client.describe_addresses()
            
            unused_ips = []
            total_cost = 0
            
            for address in response['Addresses']:
                if 'InstanceId' not in address:
                    monthly_cost = 3.65  # $3.65 per month for unused EIP
                    total_cost += monthly_cost
                    
                    unused_ips.append({
                        'allocation_id': address['AllocationId'],
                        'public_ip': address['PublicIp'],
                        'monthly_cost': monthly_cost
                    })
            
            return {
                'elastic_ips': unused_ips,
                'count': len(unused_ips),
                'monthly_cost': total_cost
            }
        except Exception as e:
            print(f"Error finding unused Elastic IPs: {e}")
            return {'elastic_ips': [], 'count': 0, 'monthly_cost': 0}
    
    def _find_unused_load_balancers(self) -> Dict[str, Any]:
        """Find unused load balancers"""
        # This would require ELB/ALB client calls
        # Simplified implementation
        return {'load_balancers': [], 'count': 0, 'monthly_cost': 0}
    
    def _find_unused_nat_gateways(self) -> Dict[str, Any]:
        """Find unused NAT gateways"""
        # This would require VPC client calls
        # Simplified implementation
        return {'nat_gateways': [], 'count': 0, 'monthly_cost': 0}
    
    def _generate_cleanup_recommendations(self, unused_resources: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate cleanup recommendations"""
        recommendations = []
        
        for resource_type, data in unused_resources.items():
            if data.get('count', 0) > 0:
                recommendations.append({
                    'type': 'cleanup',
                    'resource_type': resource_type,
                    'count': data['count'],
                    'monthly_savings': data.get('monthly_cost', 0),
                    'recommendation': f"Clean up {data['count']} unused {resource_type}"
                })
        
        return recommendations


# Example usage and testing
if __name__ == "__main__":
    # Initialize cost optimizer
    optimizer = CostOptimizer()
    
    # Generate comprehensive optimization report
    report = optimizer.generate_optimization_report(days=30)
    
    print("=== Cost Optimization Report ===")
    print(f"Total Potential Monthly Savings: ${report.get('total_potential_monthly_savings', 0):.2f}")
    
    # Print EC2 recommendations
    ec2_recs = report.get('ec2_analysis', {}).get('recommendations', [])
    print(f"\nEC2 Recommendations: {len(ec2_recs)}")
    for rec in ec2_recs[:3]:  # Show first 3
        print(f"  - {rec['recommendation']}")
    
    # Print unused resources
    unused = report.get('unused_resources', {})
    print(f"\nUnused Resources Monthly Cost: ${unused.get('total_monthly_savings', 0):.2f}")
    
    # Print cost anomalies
    anomalies = report.get('cost_anomalies', [])
    print(f"\nCost Anomalies Found: {len(anomalies)}")
    for anomaly in anomalies[:3]:  # Show first 3
        print(f"  - Impact: ${anomaly.get('impact', 0):.2f}")