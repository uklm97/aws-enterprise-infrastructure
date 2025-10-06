#!/usr/bin/env python3
"""
Prometheus Manager for Kubernetes monitoring.

This module provides comprehensive Prometheus management capabilities including
installation, configuration, and monitoring setup for Kubernetes clusters.
"""

import boto3
import logging
import json
import yaml
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import subprocess
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PrometheusManager:
    """
    Prometheus Manager for Kubernetes monitoring.
    """
    
    def __init__(self, region: str = 'us-east-1'):
        """Initialize PrometheusManager with AWS clients."""
        self.region = region
        self.eks_client = boto3.client('eks', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        
    def install_prometheus_operator(self, cluster_name: str, namespace: str = 'monitoring') -> bool:
        """Install Prometheus Operator using Helm."""
        try:
            logger.info(f"Installing Prometheus Operator in cluster {cluster_name}")
            
            # Add Prometheus Community Helm repository
            subprocess.run([
                'helm', 'repo', 'add', 'prometheus-community', 
                'https://prometheus-community.github.io/helm-charts'
            ], check=True)
            
            subprocess.run(['helm', 'repo', 'update'], check=True)
            
            # Create namespace if it doesn't exist
            self._create_namespace(namespace)
            
            # Install Prometheus Operator
            subprocess.run([
                'helm', 'install', 'prometheus-operator',
                'prometheus-community/kube-prometheus-stack',
                '--namespace', namespace,
                '--set', 'grafana.adminPassword=admin123',
                '--set', 'prometheus.prometheusSpec.retention=30d',
                '--set', 'prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi',
                '--wait'
            ], check=True)
            
            logger.info(f"Prometheus Operator installed successfully in {namespace} namespace")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing Prometheus Operator: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error installing Prometheus Operator: {str(e)}")
            return False
    
    def _create_namespace(self, namespace: str) -> bool:
        """Create Kubernetes namespace."""
        try:
            subprocess.run([
                'kubectl', 'create', 'namespace', namespace
            ], check=True, capture_output=True)
            logger.info(f"Namespace {namespace} created")
            return True
        except subprocess.CalledProcessError:
            # Namespace might already exist
            logger.info(f"Namespace {namespace} might already exist")
            return True
        except Exception as e:
            logger.error(f"Error creating namespace: {str(e)}")
            return False
    
    def create_service_monitor(self, service_monitor_config: Dict[str, Any]) -> bool:
        """Create ServiceMonitor for Prometheus."""
        try:
            logger.info(f"Creating ServiceMonitor: {service_monitor_config['metadata']['name']}")
            
            # Create ServiceMonitor YAML
            service_monitor_yaml = self._generate_service_monitor_yaml(service_monitor_config)
            
            # Apply to cluster
            result = subprocess.run([
                'kubectl', 'apply', '-f', '-'
            ], input=service_monitor_yaml, text=True, check=True)
            
            logger.info(f"ServiceMonitor {service_monitor_config['metadata']['name']} created successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error creating ServiceMonitor: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error creating ServiceMonitor: {str(e)}")
            return False
    
    def _generate_service_monitor_yaml(self, config: Dict[str, Any]) -> str:
        """Generate ServiceMonitor YAML."""
        service_monitor = {
            'apiVersion': 'monitoring.coreos.com/v1',
            'kind': 'ServiceMonitor',
            'metadata': {
                'name': config['metadata']['name'],
                'namespace': config['metadata'].get('namespace', 'monitoring'),
                'labels': config['metadata'].get('labels', {})
            },
            'spec': {
                'selector': {
                    'matchLabels': config['spec']['selector']
                },
                'endpoints': config['spec']['endpoints']
            }
        }
        
        return yaml.dump(service_monitor, default_flow_style=False)
    
    def create_prometheus_rule(self, rule_config: Dict[str, Any]) -> bool:
        """Create PrometheusRule for alerting."""
        try:
            logger.info(f"Creating PrometheusRule: {rule_config['metadata']['name']}")
            
            # Create PrometheusRule YAML
            rule_yaml = self._generate_prometheus_rule_yaml(rule_config)
            
            # Apply to cluster
            subprocess.run([
                'kubectl', 'apply', '-f', '-'
            ], input=rule_yaml, text=True, check=True)
            
            logger.info(f"PrometheusRule {rule_config['metadata']['name']} created successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error creating PrometheusRule: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error creating PrometheusRule: {str(e)}")
            return False
    
    def _generate_prometheus_rule_yaml(self, config: Dict[str, Any]) -> str:
        """Generate PrometheusRule YAML."""
        rule = {
            'apiVersion': 'monitoring.coreos.com/v1',
            'kind': 'PrometheusRule',
            'metadata': {
                'name': config['metadata']['name'],
                'namespace': config['metadata'].get('namespace', 'monitoring'),
                'labels': config['metadata'].get('labels', {})
            },
            'spec': {
                'groups': config['spec']['groups']
            }
        }
        
        return yaml.dump(rule, default_flow_style=False)
    
    def create_grafana_dashboard(self, dashboard_config: Dict[str, Any]) -> bool:
        """Create Grafana dashboard."""
        try:
            logger.info(f"Creating Grafana dashboard: {dashboard_config['dashboard']['title']}")
            
            # Create ConfigMap for dashboard
            dashboard_yaml = self._generate_dashboard_configmap_yaml(dashboard_config)
            
            # Apply to cluster
            subprocess.run([
                'kubectl', 'apply', '-f', '-'
            ], input=dashboard_yaml, text=True, check=True)
            
            logger.info(f"Grafana dashboard {dashboard_config['dashboard']['title']} created successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error creating Grafana dashboard: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error creating Grafana dashboard: {str(e)}")
            return False
    
    def _generate_dashboard_configmap_yaml(self, config: Dict[str, Any]) -> str:
        """Generate Grafana dashboard ConfigMap YAML."""
        dashboard_name = config['dashboard']['title'].lower().replace(' ', '-')
        
        configmap = {
            'apiVersion': 'v1',
            'kind': 'ConfigMap',
            'metadata': {
                'name': f'grafana-dashboard-{dashboard_name}',
                'namespace': config['metadata'].get('namespace', 'monitoring'),
                'labels': {
                    'grafana_dashboard': '1'
                }
            },
            'data': {
                f'{dashboard_name}.json': json.dumps(config['dashboard'])
            }
        }
        
        return yaml.dump(configmap, default_flow_style=False)
    
    def setup_node_exporter(self, namespace: str = 'monitoring') -> bool:
        """Setup Node Exporter for node metrics."""
        try:
            logger.info("Setting up Node Exporter")
            
            # Create Node Exporter DaemonSet
            node_exporter_yaml = self._generate_node_exporter_yaml(namespace)
            
            # Apply to cluster
            subprocess.run([
                'kubectl', 'apply', '-f', '-'
            ], input=node_exporter_yaml, text=True, check=True)
            
            logger.info("Node Exporter setup completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error setting up Node Exporter: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error setting up Node Exporter: {str(e)}")
            return False
    
    def _generate_node_exporter_yaml(self, namespace: str) -> str:
        """Generate Node Exporter DaemonSet YAML."""
        daemonset = {
            'apiVersion': 'apps/v1',
            'kind': 'DaemonSet',
            'metadata': {
                'name': 'node-exporter',
                'namespace': namespace,
                'labels': {
                    'app': 'node-exporter'
                }
            },
            'spec': {
                'selector': {
                    'matchLabels': {
                        'app': 'node-exporter'
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': 'node-exporter'
                        }
                    },
                    'spec': {
                        'containers': [
                            {
                                'name': 'node-exporter',
                                'image': 'prom/node-exporter:latest',
                                'ports': [
                                    {
                                        'containerPort': 9100,
                                        'name': 'metrics'
                                    }
                                ],
                                'args': [
                                    '--path.sysfs=/host/sys',
                                    '--path.rootfs=/host/root'
                                ],
                                'volumeMounts': [
                                    {
                                        'name': 'sys',
                                        'mountPath': '/host/sys',
                                        'readOnly': True
                                    },
                                    {
                                        'name': 'root',
                                        'mountPath': '/host/root',
                                        'readOnly': True
                                    }
                                ]
                            }
                        ],
                        'volumes': [
                            {
                                'name': 'sys',
                                'hostPath': {
                                    'path': '/sys'
                                }
                            },
                            {
                                'name': 'root',
                                'hostPath': {
                                    'path': '/'
                                }
                            }
                        ],
                        'hostNetwork': True,
                        'hostPID': True
                    }
                }
            }
        }
        
        return yaml.dump(daemonset, default_flow_style=False)
    
    def setup_ingress_controller_monitoring(self, namespace: str = 'monitoring') -> bool:
        """Setup monitoring for NGINX Ingress Controller."""
        try:
            logger.info("Setting up NGINX Ingress Controller monitoring")
            
            # Create ServiceMonitor for NGINX Ingress
            service_monitor_config = {
                'metadata': {
                    'name': 'nginx-ingress-controller',
                    'namespace': namespace,
                    'labels': {
                        'app': 'nginx-ingress-controller'
                    }
                },
                'spec': {
                    'selector': {
                        'matchLabels': {
                            'app': 'nginx-ingress-controller'
                        }
                    },
                    'endpoints': [
                        {
                            'port': 'metrics',
                            'path': '/metrics',
                            'interval': '30s'
                        }
                    ]
                }
            }
            
            self.create_service_monitor(service_monitor_config)
            
            # Create PrometheusRule for NGINX alerts
            rule_config = {
                'metadata': {
                    'name': 'nginx-ingress-alerts',
                    'namespace': namespace
                },
                'spec': {
                    'groups': [
                        {
                            'name': 'nginx-ingress',
                            'rules': [
                                {
                                    'alert': 'NginxIngressHighErrorRate',
                                    'expr': 'rate(nginx_ingress_controller_requests{status=~"5.."}[5m]) > 0.1',
                                    'for': '5m',
                                    'labels': {
                                        'severity': 'warning'
                                    },
                                    'annotations': {
                                        'summary': 'High error rate in NGINX Ingress',
                                        'description': 'NGINX Ingress error rate is {{ $value }} errors per second'
                                    }
                                },
                                {
                                    'alert': 'NginxIngressDown',
                                    'expr': 'up{job="nginx-ingress-controller"} == 0',
                                    'for': '1m',
                                    'labels': {
                                        'severity': 'critical'
                                    },
                                    'annotations': {
                                        'summary': 'NGINX Ingress Controller is down',
                                        'description': 'NGINX Ingress Controller has been down for more than 1 minute'
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
            
            self.create_prometheus_rule(rule_config)
            
            logger.info("NGINX Ingress Controller monitoring setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up NGINX Ingress monitoring: {str(e)}")
            return False
    
    def get_prometheus_status(self, namespace: str = 'monitoring') -> Dict[str, Any]:
        """Get Prometheus deployment status."""
        try:
            # Get Prometheus pods
            result = subprocess.run([
                'kubectl', 'get', 'pods', '-n', namespace, '-l', 'app.kubernetes.io/name=prometheus',
                '-o', 'json'
            ], capture_output=True, text=True, check=True)
            
            pods = json.loads(result.stdout)
            
            # Get Prometheus service
            result = subprocess.run([
                'kubectl', 'get', 'svc', '-n', namespace, '-l', 'app.kubernetes.io/name=prometheus',
                '-o', 'json'
            ], capture_output=True, text=True, check=True)
            
            services = json.loads(result.stdout)
            
            return {
                'pods': pods['items'],
                'services': services['items'],
                'namespace': namespace,
                'timestamp': datetime.now().isoformat()
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting Prometheus status: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Error getting Prometheus status: {str(e)}")
            return {}
    
    def get_grafana_status(self, namespace: str = 'monitoring') -> Dict[str, Any]:
        """Get Grafana deployment status."""
        try:
            # Get Grafana pods
            result = subprocess.run([
                'kubectl', 'get', 'pods', '-n', namespace, '-l', 'app.kubernetes.io/name=grafana',
                '-o', 'json'
            ], capture_output=True, text=True, check=True)
            
            pods = json.loads(result.stdout)
            
            # Get Grafana service
            result = subprocess.run([
                'kubectl', 'get', 'svc', '-n', namespace, '-l', 'app.kubernetes.io/name=grafana',
                '-o', 'json'
            ], capture_output=True, text=True, check=True)
            
            services = json.loads(result.stdout)
            
            return {
                'pods': pods['items'],
                'services': services['items'],
                'namespace': namespace,
                'timestamp': datetime.now().isoformat()
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting Grafana status: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Error getting Grafana status: {str(e)}")
            return {}
    
    def create_sample_dashboard(self, namespace: str = 'monitoring') -> bool:
        """Create sample Grafana dashboard for Kubernetes monitoring."""
        try:
            logger.info("Creating sample Kubernetes monitoring dashboard")
            
            dashboard_config = {
                'metadata': {
                    'namespace': namespace
                },
                'dashboard': {
                    'title': 'Kubernetes Cluster Monitoring',
                    'tags': ['kubernetes', 'monitoring'],
                    'timezone': 'browser',
                    'panels': [
                        {
                            'title': 'Cluster CPU Usage',
                            'type': 'graph',
                            'targets': [
                                {
                                    'expr': '100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)',
                                    'legendFormat': 'CPU Usage %'
                                }
                            ]
                        },
                        {
                            'title': 'Cluster Memory Usage',
                            'type': 'graph',
                            'targets': [
                                {
                                    'expr': '100 - ((node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100)',
                                    'legendFormat': 'Memory Usage %'
                                }
                            ]
                        },
                        {
                            'title': 'Pod Count by Namespace',
                            'type': 'graph',
                            'targets': [
                                {
                                    'expr': 'count by (namespace) (kube_pod_info)',
                                    'legendFormat': '{{namespace}}'
                                }
                            ]
                        }
                    ]
                }
            }
            
            return self.create_grafana_dashboard(dashboard_config)
            
        except Exception as e:
            logger.error(f"Error creating sample dashboard: {str(e)}")
            return False


def main():
    """Main function for testing PrometheusManager."""
    # Example usage
    prometheus_manager = PrometheusManager()
    
    # Install Prometheus Operator
    success = prometheus_manager.install_prometheus_operator('my-cluster')
    if success:
        print("Prometheus Operator installed successfully")
        
        # Setup Node Exporter
        prometheus_manager.setup_node_exporter()
        
        # Setup NGINX Ingress monitoring
        prometheus_manager.setup_ingress_controller_monitoring()
        
        # Create sample dashboard
        prometheus_manager.create_sample_dashboard()


if __name__ == "__main__":
    main()