#!/usr/bin/env python3
"""
Linux CIS Benchmark Implementation
Automated Linux server hardening based on CIS benchmarks
"""

import subprocess
import yaml
import logging
import os
import sys
from typing import Dict, List, Any
from datetime import datetime

class LinuxHardeningManager:
    """
    Linux Server Hardening Manager for CIS benchmark implementation.
    """
    
    def __init__(self, config_file: str = 'config/hardening_config.yaml'):
        self.config = self.load_config(config_file)
        self.logger = self.setup_logging()
        self.hardening_results = []
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('linux_hardening.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)
        
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load hardening configuration."""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as file:
                    return yaml.safe_load(file)
            else:
                # Default configuration if file doesn't exist
                return self.get_default_config()
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default hardening configuration."""
        return {
            'cis_benchmarks': {
                'ubuntu_20.04': {
                    'system': {
                        'disable_services': ['telnet', 'rsh', 'rlogin', 'rexec'],
                        'sysctl_params': {
                            'net.ipv4.ip_forward': '0',
                            'net.ipv4.conf.all.send_redirects': '0',
                            'net.ipv4.conf.default.send_redirects': '0',
                            'net.ipv4.conf.all.accept_source_route': '0',
                            'net.ipv4.conf.default.accept_source_route': '0'
                        }
                    },
                    'network': {
                        'firewall_rules': [
                            'INPUT -p tcp --dport 22 -j ACCEPT',
                            'INPUT -p tcp --dport 80 -j ACCEPT',
                            'INPUT -p tcp --dport 443 -j ACCEPT',
                            'INPUT -j DROP'
                        ]
                    },
                    'users': {
                        'max_days': 90,
                        'max_attempts': 5,
                        'remove_users': ['games', 'gopher']
                    },
                    'filesystem': {
                        'file_permissions': {
                            '/etc/passwd': '644',
                            '/etc/shadow': '600',
                            '/etc/group': '644',
                            '/etc/gshadow': '600'
                        }
                    }
                }
            }
        }
    
    def apply_cis_benchmark(self, benchmark_version: str = 'ubuntu_20.04'):
        """Apply CIS benchmark hardening."""
        self.logger.info(f"Starting CIS benchmark {benchmark_version} hardening")
        
        try:
            benchmark_config = self.config['cis_benchmarks'][benchmark_version]
            
            # Apply system hardening
            self._harden_system_settings(benchmark_config['system'])
            
            # Apply network hardening
            self._harden_network_settings(benchmark_config['network'])
            
            # Apply user management
            self._harden_user_management(benchmark_config['users'])
            
            # Apply file system security
            self._harden_file_system(benchmark_config['filesystem'])
            
            self.logger.info(f"CIS benchmark {benchmark_version} applied successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying CIS benchmark: {str(e)}")
            return False
    
    def _harden_system_settings(self, system_config: Dict[str, Any]):
        """Harden system settings."""
        self.logger.info("Applying system hardening settings")
        
        try:
            # Disable unnecessary services
            for service in system_config.get('disable_services', []):
                try:
                    subprocess.run(['systemctl', 'disable', service], check=True, capture_output=True)
                    subprocess.run(['systemctl', 'stop', service], check=True, capture_output=True)
                    self.logger.info(f"Disabled and stopped service: {service}")
                    self.hardening_results.append(f"Disabled service: {service}")
                except subprocess.CalledProcessError as e:
                    self.logger.warning(f"Could not disable service {service}: {e}")
            
            # Configure system parameters
            for param, value in system_config.get('sysctl_params', {}).items():
                try:
                    subprocess.run(['sysctl', '-w', f'{param}={value}'], check=True, capture_output=True)
                    self.logger.info(f"Set sysctl parameter: {param}={value}")
                    self.hardening_results.append(f"Set sysctl: {param}={value}")
                except subprocess.CalledProcessError as e:
                    self.logger.warning(f"Could not set sysctl {param}: {e}")
            
            # Apply kernel parameters permanently
            self._apply_sysctl_permanent(system_config.get('sysctl_params', {}))
                    
        except Exception as e:
            self.logger.error(f"Error hardening system settings: {str(e)}")
    
    def _apply_sysctl_permanent(self, sysctl_params: Dict[str, str]):
        """Apply sysctl parameters permanently."""
        try:
            with open('/etc/sysctl.conf', 'a') as f:
                f.write('\n# CIS Benchmark Hardening\n')
                for param, value in sysctl_params.items():
                    f.write(f'{param} = {value}\n')
            self.logger.info("Applied sysctl parameters permanently")
        except Exception as e:
            self.logger.warning(f"Could not apply sysctl permanently: {e}")
    
    def _harden_network_settings(self, network_config: Dict[str, Any]):
        """Harden network settings."""
        self.logger.info("Applying network hardening settings")
        
        try:
            # Configure firewall rules
            for rule in network_config.get('firewall_rules', []):
                try:
                    subprocess.run(['iptables', '-A'] + rule.split(), check=True, capture_output=True)
                    self.logger.info(f"Applied firewall rule: {rule}")
                    self.hardening_results.append(f"Firewall rule: {rule}")
                except subprocess.CalledProcessError as e:
                    self.logger.warning(f"Could not apply firewall rule {rule}: {e}")
            
            # Save iptables rules
            try:
                subprocess.run(['iptables-save'], stdout=open('/etc/iptables/rules.v4', 'w'), check=True)
                self.logger.info("Saved iptables rules")
            except subprocess.CalledProcessError:
                self.logger.warning("Could not save iptables rules")
                
        except Exception as e:
            self.logger.error(f"Error hardening network settings: {str(e)}")
    
    def _harden_user_management(self, user_config: Dict[str, Any]):
        """Harden user management."""
        self.logger.info("Applying user management hardening")
        
        try:
            # Configure password policy
            try:
                subprocess.run(['chage', '-M', str(user_config.get('max_days', 90)), 'root'], 
                             check=True, capture_output=True)
                self.logger.info(f"Set password max age: {user_config.get('max_days', 90)} days")
                self.hardening_results.append(f"Password max age: {user_config.get('max_days', 90)} days")
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"Could not set password policy: {e}")
            
            # Configure account lockout
            try:
                subprocess.run(['pam_tally2', '--deny', str(user_config.get('max_attempts', 5))], 
                             check=True, capture_output=True)
                self.logger.info(f"Set account lockout threshold: {user_config.get('max_attempts', 5)}")
                self.hardening_results.append(f"Account lockout threshold: {user_config.get('max_attempts', 5)}")
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"Could not set account lockout: {e}")
            
            # Remove unnecessary users
            for user in user_config.get('remove_users', []):
                try:
                    subprocess.run(['userdel', '-r', user], check=True, capture_output=True)
                    self.logger.info(f"Removed user: {user}")
                    self.hardening_results.append(f"Removed user: {user}")
                except subprocess.CalledProcessError as e:
                    self.logger.warning(f"Could not remove user {user}: {e}")
                
        except Exception as e:
            self.logger.error(f"Error hardening user management: {str(e)}")
    
    def _harden_file_system(self, fs_config: Dict[str, Any]):
        """Harden file system security."""
        self.logger.info("Applying file system hardening")
        
        try:
            # Set file permissions
            for file_path, permissions in fs_config.get('file_permissions', {}).items():
                try:
                    if os.path.exists(file_path):
                        subprocess.run(['chmod', permissions, file_path], check=True, capture_output=True)
                        self.logger.info(f"Set permissions {permissions} on {file_path}")
                        self.hardening_results.append(f"File permissions {permissions}: {file_path}")
                except subprocess.CalledProcessError as e:
                    self.logger.warning(f"Could not set permissions on {file_path}: {e}")
            
            # Set directory permissions
            for dir_path, permissions in fs_config.get('directory_permissions', {}).items():
                try:
                    if os.path.exists(dir_path):
                        subprocess.run(['chmod', permissions, dir_path], check=True, capture_output=True)
                        self.logger.info(f"Set permissions {permissions} on directory {dir_path}")
                        self.hardening_results.append(f"Directory permissions {permissions}: {dir_path}")
                except subprocess.CalledProcessError as e:
                    self.logger.warning(f"Could not set permissions on directory {dir_path}: {e}")
                
        except Exception as e:
            self.logger.error(f"Error hardening file system: {str(e)}")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate hardening report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_actions': len(self.hardening_results),
            'actions': self.hardening_results,
            'status': 'completed'
        }
    
    def save_report(self, filename: str = 'hardening_report.yaml'):
        """Save hardening report to file."""
        try:
            report = self.generate_report()
            with open(filename, 'w') as f:
                yaml.dump(report, f, default_flow_style=False)
            self.logger.info(f"Hardening report saved to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving report: {e}")

def main():
    """Main function for command line execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Linux Server Hardening Tool')
    parser.add_argument('--benchmark', default='ubuntu_20.04', 
                       help='CIS benchmark version to apply')
    parser.add_argument('--config', default='config/hardening_config.yaml',
                       help='Configuration file path')
    parser.add_argument('--report', default='hardening_report.yaml',
                       help='Report output file')
    
    args = parser.parse_args()
    
    # Create hardening manager
    hardening_manager = LinuxHardeningManager(args.config)
    
    # Apply hardening
    success = hardening_manager.apply_cis_benchmark(args.benchmark)
    
    # Generate report
    hardening_manager.save_report(args.report)
    
    if success:
        print("✅ Linux hardening completed successfully!")
        sys.exit(0)
    else:
        print("❌ Linux hardening failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
