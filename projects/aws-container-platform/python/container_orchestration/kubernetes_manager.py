#!/usr/bin/env python3
"""
Kubernetes resource manager for container orchestration.

This module provides comprehensive Kubernetes resource management capabilities including
deployment, service, ingress, and other resource management.
"""

import yaml
import subprocess
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from kubernetes import client, config
from kubernetes.client.rest import ApiException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KubernetesManager:
    """
    Kubernetes resource manager for container orchestration.
    """
    
    def __init__(self, kubeconfig_path: str = None):
        """Initialize KubernetesManager with Kubernetes client."""
        try:
            if kubeconfig_path:
                config.load_kube_config(config_file=kubeconfig_path)
            else:
                config.load_kube_config()
            
            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.networking_v1 = client.NetworkingV1Api()
            self.rbac_v1 = client.RbacAuthorizationV1Api()
            self.storage_v1 = client.StorageV1Api()
            
            logger.info("Kubernetes client initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Kubernetes client: {str(e)}")
            raise
    
    def create_namespace(self, namespace: str, labels: Dict[str, str] = None) -> bool:
        """Create Kubernetes namespace."""
        try:
            namespace_obj = client.V1Namespace(
                metadata=client.V1ObjectMeta(
                    name=namespace,
                    labels=labels or {}
                )
            )
            
            self.v1.create_namespace(namespace_obj)
            logger.info(f"Namespace {namespace} created successfully")
            return True
            
        except ApiException as e:
            if e.status == 409:  # Already exists
                logger.info(f"Namespace {namespace} already exists")
                return True
            else:
                logger.error(f"Error creating namespace: {str(e)}")
                return False
        except Exception as e:
            logger.error(f"Error creating namespace: {str(e)}")
            return False
    
    def deploy_application(self, namespace: str, deployment_config: Dict[str, Any]) -> bool:
        """Deploy application to Kubernetes."""
        try:
            # Create namespace if it doesn't exist
            self.create_namespace(namespace)
            
            # Create deployment
            deployment = self._build_deployment(deployment_config, namespace)
            self.apps_v1.create_namespaced_deployment(
                namespace=namespace,
                body=deployment
            )
            
            logger.info(f"Deployment {deployment_config['name']} created successfully")
            
            # Create service if specified
            if 'service' in deployment_config:
                service = self._build_service(deployment_config['service'], namespace)
                self.v1.create_namespaced_service(
                    namespace=namespace,
                    body=service
                )
                logger.info(f"Service {deployment_config['service']['name']} created successfully")
            
            # Create ingress if specified
            if 'ingress' in deployment_config:
                ingress = self._build_ingress(deployment_config['ingress'], namespace)
                self.networking_v1.create_namespaced_ingress(
                    namespace=namespace,
                    body=ingress
                )
                logger.info(f"Ingress {deployment_config['ingress']['name']} created successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deploying application: {str(e)}")
            return False
    
    def _build_deployment(self, config: Dict[str, Any], namespace: str) -> client.V1Deployment:
        """Build Kubernetes deployment object."""
        containers = []
        for container_config in config['containers']:
            container = client.V1Container(
                name=container_config['name'],
                image=container_config['image'],
                ports=[
                    client.V1ContainerPort(
                        container_port=port['port'],
                        name=port.get('name', f"port-{port['port']}"),
                        protocol=port.get('protocol', 'TCP')
                    ) for port in container_config.get('ports', [])
                ],
                env=[
                    client.V1EnvVar(
                        name=env['name'],
                        value=env.get('value', ''),
                        value_from=env.get('value_from')
                    ) for env in container_config.get('env', [])
                ],
                resources=client.V1ResourceRequirements(
                    requests=container_config.get('requests', {}),
                    limits=container_config.get('limits', {})
                ) if container_config.get('requests') or container_config.get('limits') else None,
                liveness_probe=container_config.get('liveness_probe'),
                readiness_probe=container_config.get('readiness_probe'),
                volume_mounts=[
                    client.V1VolumeMount(
                        name=vm['name'],
                        mount_path=vm['mount_path'],
                        sub_path=vm.get('sub_path')
                    ) for vm in container_config.get('volume_mounts', [])
                ]
            )
            containers.append(container)
        
        # Build volumes
        volumes = []
        for volume_config in config.get('volumes', []):
            volume = client.V1Volume(
                name=volume_config['name'],
                config_map=volume_config.get('config_map'),
                secret=volume_config.get('secret'),
                persistent_volume_claim=volume_config.get('persistent_volume_claim'),
                empty_dir=volume_config.get('empty_dir')
            )
            volumes.append(volume)
        
        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(
                name=config['name'],
                namespace=namespace,
                labels=config.get('labels', {}),
                annotations=config.get('annotations', {})
            ),
            spec=client.V1DeploymentSpec(
                replicas=config.get('replicas', 1),
                selector=client.V1LabelSelector(
                    match_labels=config.get('selector', config.get('labels', {}))
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels=config.get('pod_labels', config.get('labels', {}))
                    ),
                    spec=client.V1PodSpec(
                        containers=containers,
                        volumes=volumes,
                        restart_policy=config.get('restart_policy', 'Always'),
                        node_selector=config.get('node_selector'),
                        tolerations=config.get('tolerations'),
                        affinity=config.get('affinity')
                    )
                ),
                strategy=client.V1DeploymentStrategy(
                    type=config.get('strategy_type', 'RollingUpdate'),
                    rolling_update=client.V1RollingUpdateDeployment(
                        max_unavailable=config.get('max_unavailable', 1),
                        max_surge=config.get('max_surge', 1)
                    )
                )
            )
        )
        
        return deployment
    
    def _build_service(self, config: Dict[str, Any], namespace: str) -> client.V1Service:
        """Build Kubernetes service object."""
        ports = []
        for port_config in config['ports']:
            port = client.V1ServicePort(
                port=port_config['port'],
                target_port=port_config['target_port'],
                protocol=port_config.get('protocol', 'TCP'),
                name=port_config.get('name', f"port-{port_config['port']}")
            )
            ports.append(port)
        
        service = client.V1Service(
            metadata=client.V1ObjectMeta(
                name=config['name'],
                namespace=namespace,
                labels=config.get('labels', {}),
                annotations=config.get('annotations', {})
            ),
            spec=client.V1ServiceSpec(
                selector=config['selector'],
                ports=ports,
                type=config.get('type', 'ClusterIP'),
                session_affinity=config.get('session_affinity', 'None')
            )
        )
        
        return service
    
    def _build_ingress(self, config: Dict[str, Any], namespace: str) -> client.V1Ingress:
        """Build Kubernetes ingress object."""
        rules = []
        for rule_config in config['rules']:
            paths = []
            for path_config in rule_config['paths']:
                path = client.V1HTTPIngressPath(
                    path=path_config['path'],
                    path_type=path_config.get('path_type', 'Prefix'),
                    backend=client.V1IngressBackend(
                        service=client.V1IngressServiceBackend(
                            name=path_config['service']['name'],
                            port=client.V1ServiceBackendPort(
                                number=path_config['service']['port']
                            )
                        )
                    )
                )
                paths.append(path)
            
            rule = client.V1IngressRule(
                host=rule_config['host'],
                http=client.V1HTTPIngressRuleValue(paths=paths)
            )
            rules.append(rule)
        
        ingress = client.V1Ingress(
            metadata=client.V1ObjectMeta(
                name=config['name'],
                namespace=namespace,
                labels=config.get('labels', {}),
                annotations=config.get('annotations', {})
            ),
            spec=client.V1IngressSpec(
                rules=rules,
                tls=config.get('tls', [])
            )
        )
        
        return ingress
    
    def scale_deployment(self, namespace: str, deployment_name: str, replicas: int) -> bool:
        """Scale deployment to specified number of replicas."""
        try:
            self.apps_v1.patch_namespaced_deployment_scale(
                name=deployment_name,
                namespace=namespace,
                body={'spec': {'replicas': replicas}}
            )
            
            logger.info(f"Deployment {deployment_name} scaled to {replicas} replicas")
            return True
            
        except Exception as e:
            logger.error(f"Error scaling deployment: {str(e)}")
            return False
    
    def get_pod_status(self, namespace: str = None) -> List[Dict[str, Any]]:
        """Get pod status in namespace."""
        try:
            if namespace:
                pods = self.v1.list_namespaced_pod(namespace=namespace)
            else:
                pods = self.v1.list_pod_for_all_namespaces()
            
            pod_status = []
            for pod in pods.items:
                pod_info = {
                    'name': pod.metadata.name,
                    'namespace': pod.metadata.namespace,
                    'status': pod.status.phase,
                    'ready': pod.status.ready,
                    'restarts': pod.status.container_statuses[0].restart_count if pod.status.container_statuses else 0,
                    'node': pod.spec.node_name,
                    'created_at': pod.metadata.creation_timestamp.isoformat() if pod.metadata.creation_timestamp else None
                }
                
                # Add container statuses
                if pod.status.container_statuses:
                    pod_info['containers'] = []
                    for container in pod.status.container_statuses:
                        container_info = {
                            'name': container.name,
                            'ready': container.ready,
                            'restart_count': container.restart_count,
                            'state': container.state
                        }
                        pod_info['containers'].append(container_info)
                
                pod_status.append(pod_info)
            
            return pod_status
            
        except Exception as e:
            logger.error(f"Error getting pod status: {str(e)}")
            return []
    
    def get_deployment_status(self, namespace: str = None) -> List[Dict[str, Any]]:
        """Get deployment status."""
        try:
            if namespace:
                deployments = self.apps_v1.list_namespaced_deployment(namespace=namespace)
            else:
                deployments = self.apps_v1.list_deployment_for_all_namespaces()
            
            deployment_status = []
            for deployment in deployments.items:
                status = {
                    'name': deployment.metadata.name,
                    'namespace': deployment.metadata.namespace,
                    'replicas': deployment.spec.replicas,
                    'ready_replicas': deployment.status.ready_replicas or 0,
                    'available_replicas': deployment.status.available_replicas or 0,
                    'unavailable_replicas': deployment.status.unavailable_replicas or 0,
                    'created_at': deployment.metadata.creation_timestamp.isoformat() if deployment.metadata.creation_timestamp else None
                }
                deployment_status.append(status)
            
            return deployment_status
            
        except Exception as e:
            logger.error(f"Error getting deployment status: {str(e)}")
            return []
    
    def get_service_status(self, namespace: str = None) -> List[Dict[str, Any]]:
        """Get service status."""
        try:
            if namespace:
                services = self.v1.list_namespaced_service(namespace=namespace)
            else:
                services = self.v1.list_service_for_all_namespaces()
            
            service_status = []
            for service in services.items:
                status = {
                    'name': service.metadata.name,
                    'namespace': service.metadata.namespace,
                    'type': service.spec.type,
                    'cluster_ip': service.spec.cluster_ip,
                    'external_ips': service.spec.external_i_ps or [],
                    'ports': [
                        {
                            'port': port.port,
                            'target_port': port.target_port,
                            'protocol': port.protocol,
                            'name': port.name
                        } for port in service.spec.ports
                    ],
                    'created_at': service.metadata.creation_timestamp.isoformat() if service.metadata.creation_timestamp else None
                }
                service_status.append(status)
            
            return service_status
            
        except Exception as e:
            logger.error(f"Error getting service status: {str(e)}")
            return []
    
    def create_configmap(self, namespace: str, name: str, data: Dict[str, str]) -> bool:
        """Create ConfigMap."""
        try:
            configmap = client.V1ConfigMap(
                metadata=client.V1ObjectMeta(
                    name=name,
                    namespace=namespace
                ),
                data=data
            )
            
            self.v1.create_namespaced_config_map(
                namespace=namespace,
                body=configmap
            )
            
            logger.info(f"ConfigMap {name} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating ConfigMap: {str(e)}")
            return False
    
    def create_secret(self, namespace: str, name: str, data: Dict[str, str], 
                     secret_type: str = 'Opaque') -> bool:
        """Create Secret."""
        try:
            secret = client.V1Secret(
                metadata=client.V1ObjectMeta(
                    name=name,
                    namespace=namespace
                ),
                type=secret_type,
                data=data
            )
            
            self.v1.create_namespaced_secret(
                namespace=namespace,
                body=secret
            )
            
            logger.info(f"Secret {name} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating Secret: {str(e)}")
            return False
    
    def apply_yaml_file(self, yaml_file: str, namespace: str = None) -> bool:
        """Apply Kubernetes resources from YAML file."""
        try:
            with open(yaml_file, 'r') as f:
                yaml_content = yaml.safe_load_all(f)
                
                for resource in yaml_content:
                    if resource is None:
                        continue
                    
                    # Apply resource using kubectl
                    cmd = ['kubectl', 'apply', '-f', yaml_file]
                    if namespace:
                        cmd.extend(['-n', namespace])
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        logger.error(f"Error applying YAML file: {result.stderr}")
                        return False
                    
                    logger.info(f"Resource applied successfully: {resource.get('kind', 'Unknown')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying YAML file: {str(e)}")
            return False
    
    def delete_deployment(self, namespace: str, deployment_name: str) -> bool:
        """Delete deployment."""
        try:
            self.apps_v1.delete_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            logger.info(f"Deployment {deployment_name} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting deployment: {str(e)}")
            return False
    
    def delete_service(self, namespace: str, service_name: str) -> bool:
        """Delete service."""
        try:
            self.v1.delete_namespaced_service(
                name=service_name,
                namespace=namespace
            )
            
            logger.info(f"Service {service_name} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting service: {str(e)}")
            return False


def main():
    """Main function for testing KubernetesManager."""
    # Example usage
    k8s_manager = KubernetesManager()
    
    # Example deployment configuration
    deployment_config = {
        'name': 'my-app',
        'replicas': 3,
        'labels': {
            'app': 'my-app',
            'version': 'v1.0.0'
        },
        'containers': [
            {
                'name': 'app-container',
                'image': 'nginx:1.21',
                'ports': [
                    {'port': 80, 'name': 'http'}
                ],
                'resources': {
                    'requests': {'cpu': '100m', 'memory': '128Mi'},
                    'limits': {'cpu': '500m', 'memory': '512Mi'}
                }
            }
        ],
        'service': {
            'name': 'my-app-service',
            'selector': {'app': 'my-app'},
            'ports': [
                {'port': 80, 'target_port': 80, 'protocol': 'TCP'}
            ],
            'type': 'ClusterIP'
        }
    }
    
    # Deploy application
    success = k8s_manager.deploy_application('default', deployment_config)
    if success:
        print("Application deployed successfully")
        
        # Get pod status
        pods = k8s_manager.get_pod_status('default')
        print(f"Pod status: {json.dumps(pods, indent=2, default=str)}")
        
        # Get deployment status
        deployments = k8s_manager.get_deployment_status('default')
        print(f"Deployment status: {json.dumps(deployments, indent=2, default=str)}")


if __name__ == "__main__":
    main()