#!/usr/bin/env python3
"""
Windows Group Policy Hardening Implementation
Automated Windows server hardening using Group Policy and PowerShell
"""

import subprocess
import yaml
import logging
import os
import sys
from typing import Dict, List, Any
from datetime import datetime

class WindowsHardeningManager:
    """
    Windows Server Hardening Manager for Group Policy and security configuration.
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
                logging.FileHandler('windows_hardening.log'),
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
            'windows_policies': {
                'high_security': {
                    'password_policy': {
                        'min_length': 12,
                        'complexity': 1,
                        'history': 24,
                        'max_age': 90,
                        'min_age': 1
                    },
                    'account_lockout': {
                        'threshold': 5,
                        'duration': 30,
                        'window': 30
                    },
                    'audit_policy': {
                        'categories': {
                            'Account Logon': 'Success,Failure',
                            'Account Management': 'Success,Failure',
                            'Directory Service Access': 'Success,Failure',
                            'Logon': 'Success,Failure',
                            'Object Access': 'Success,Failure',
                            'Policy Change': 'Success,Failure',
                            'Privilege Use': 'Success,Failure',
                            'Process Tracking': 'Success,Failure',
                            'System': 'Success,Failure'
                        }
                    },
                    'security_options': {
                        'registry_settings': {
                            'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\ClearPageFileAtShutdown': {
                                'name': 'ClearPageFileAtShutdown',
                                'type': 'REG_DWORD',
                                'data': 1
                            },
                            'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Kernel\\ObCaseInsensitive': {
                                'name': 'ObCaseInsensitive',
                                'type': 'REG_DWORD',
                                'data': 1
                            }
                        }
                    }
                }
            }
        }
    
    def apply_security_policy(self, policy_name: str = 'high_security'):
        """Apply security policy configuration."""
        self.logger.info(f"Starting Windows security policy {policy_name} hardening")
        
        try:
            policy_config = self.config['windows_policies'][policy_name]
            
            # Apply password policy
            self._configure_password_policy(policy_config['password_policy'])
            
            # Apply account lockout policy
            self._configure_account_lockout(policy_config['account_lockout'])
            
            # Apply audit policy
            self._configure_audit_policy(policy_config['audit_policy'])
            
            # Apply security options
            self._configure_security_options(policy_config['security_options'])
            
            self.logger.info(f"Security policy {policy_name} applied successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying security policy: {str(e)}")
            return False
    
    def _configure_password_policy(self, password_config: Dict[str, Any]):
        """Configure password policy."""
        self.logger.info("Configuring password policy")
        
        try:
            # Set minimum password length
            try:
                subprocess.run([
                    'net', 'accounts', '/minpwlen:' + str(password_config.get('min_length', 12))
                ], check=True, capture_output=True)
                self.logger.info(f"Set minimum password length: {password_config.get('min_length', 12)}")
                self.hardening_results.append(f"Min password length: {password_config.get('min_length', 12)}")
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"Could not set minimum password length: {e}")
            
            # Set password complexity
            try:
                subprocess.run([
                    'net', 'accounts', '/pwcomplexity:' + str(password_config.get('complexity', 1))
                ], check=True, capture_output=True)
                self.logger.info(f"Set password complexity: {password_config.get('complexity', 1)}")
                self.hardening_results.append(f"Password complexity: {password_config.get('complexity', 1)}")
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"Could not set password complexity: {e}")
            
            # Set password history
            try:
                subprocess.run([
                    'net', 'accounts', '/uniquepw:' + str(password_config.get('history', 24))
                ], check=True, capture_output=True)
                self.logger.info(f"Set password history: {password_config.get('history', 24)}")
                self.hardening_results.append(f"Password history: {password_config.get('history', 24)}")
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"Could not set password history: {e}")
            
            # Set maximum password age
            try:
                subprocess.run([
                    'net', 'accounts', '/maxpwage:' + str(password_config.get('max_age', 90))
                ], check=True, capture_output=True)
                self.logger.info(f"Set maximum password age: {password_config.get('max_age', 90)}")
                self.hardening_results.append(f"Max password age: {password_config.get('max_age', 90)}")
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"Could not set maximum password age: {e}")
            
            # Set minimum password age
            try:
                subprocess.run([
                    'net', 'accounts', '/minpwage:' + str(password_config.get('min_age', 1))
                ], check=True, capture_output=True)
                self.logger.info(f"Set minimum password age: {password_config.get('min_age', 1)}")
                self.hardening_results.append(f"Min password age: {password_config.get('min_age', 1)}")
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"Could not set minimum password age: {e}")
            
        except Exception as e:
            self.logger.error(f"Error configuring password policy: {str(e)}")
    
    def _configure_account_lockout(self, lockout_config: Dict[str, Any]):
        """Configure account lockout policy."""
        self.logger.info("Configuring account lockout policy")
        
        try:
            # Set lockout threshold
            try:
                subprocess.run([
                    'net', 'accounts', '/lockoutthreshold:' + str(lockout_config.get('threshold', 5))
                ], check=True, capture_output=True)
                self.logger.info(f"Set lockout threshold: {lockout_config.get('threshold', 5)}")
                self.hardening_results.append(f"Lockout threshold: {lockout_config.get('threshold', 5)}")
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"Could not set lockout threshold: {e}")
            
            # Set lockout duration
            try:
                subprocess.run([
                    'net', 'accounts', '/lockoutduration:' + str(lockout_config.get('duration', 30))
                ], check=True, capture_output=True)
                self.logger.info(f"Set lockout duration: {lockout_config.get('duration', 30)}")
                self.hardening_results.append(f"Lockout duration: {lockout_config.get('duration', 30)}")
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"Could not set lockout duration: {e}")
            
            # Set lockout window
            try:
                subprocess.run([
                    'net', 'accounts', '/lockoutwindow:' + str(lockout_config.get('window', 30))
                ], check=True, capture_output=True)
                self.logger.info(f"Set lockout window: {lockout_config.get('window', 30)}")
                self.hardening_results.append(f"Lockout window: {lockout_config.get('window', 30)}")
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"Could not set lockout window: {e}")
            
        except Exception as e:
            self.logger.error(f"Error configuring account lockout: {str(e)}")
    
    def _configure_audit_policy(self, audit_config: Dict[str, Any]):
        """Configure audit policy."""
        self.logger.info("Configuring audit policy")
        
        try:
            # Set audit policy categories
            for category, setting in audit_config.get('categories', {}).items():
                try:
                    subprocess.run([
                        'auditpol', '/set', '/category:' + category, setting
                    ], check=True, capture_output=True)
                    self.logger.info(f"Set audit category {category}: {setting}")
                    self.hardening_results.append(f"Audit category {category}: {setting}")
                except subprocess.CalledProcessError as e:
                    self.logger.warning(f"Could not set audit category {category}: {e}")
            
            # Set audit policy subcategories
            for subcategory, setting in audit_config.get('subcategories', {}).items():
                try:
                    subprocess.run([
                        'auditpol', '/set', '/subcategory:' + subcategory, setting
                    ], check=True, capture_output=True)
                    self.logger.info(f"Set audit subcategory {subcategory}: {setting}")
                    self.hardening_results.append(f"Audit subcategory {subcategory}: {setting}")
                except subprocess.CalledProcessError as e:
                    self.logger.warning(f"Could not set audit subcategory {subcategory}: {e}")
                
        except Exception as e:
            self.logger.error(f"Error configuring audit policy: {str(e)}")
    
    def _configure_security_options(self, security_config: Dict[str, Any]):
        """Configure security options."""
        self.logger.info("Configuring security options")
        
        try:
            # Configure security options using registry
            for key, value in security_config.get('registry_settings', {}).items():
                try:
                    subprocess.run([
                        'reg', 'add', key, '/v', value['name'], '/t', value['type'], 
                        '/d', str(value['data']), '/f'
                    ], check=True, capture_output=True)
                    self.logger.info(f"Set registry key {key}: {value['name']}={value['data']}")
                    self.hardening_results.append(f"Registry {key}: {value['name']}={value['data']}")
                except subprocess.CalledProcessError as e:
                    self.logger.warning(f"Could not set registry key {key}: {e}")
                
        except Exception as e:
            self.logger.error(f"Error configuring security options: {str(e)}")
    
    def configure_windows_defender(self):
        """Configure Windows Defender settings."""
        self.logger.info("Configuring Windows Defender")
        
        try:
            # PowerShell commands for Windows Defender configuration
            ps_commands = [
                "Set-MpPreference -DisableRealtimeMonitoring $false",
                "Set-MpPreference -DisableBehaviorMonitoring $false",
                "Set-MpPreference -DisableBlockAtFirstSeen $false",
                "Set-MpPreference -DisableIOAVProtection $false",
                "Set-MpPreference -DisablePrivacyMode $false",
                "Set-MpPreference -SignatureDisableUpdateOnStartupWithoutEngine $false",
                "Set-MpPreference -DisableArchiveScanning $false",
                "Set-MpPreference -DisableIntrusionPreventionSystem $false",
                "Set-MpPreference -DisableScriptScanning $false",
                "Set-MpPreference -SubmitSamplesConsent 'SendSafeSamples'",
                "Set-MpPreference -MAPSReporting 'Advanced'",
                "Set-MpPreference -HighThreatDefaultAction 'Quarantine'",
                "Set-MpPreference -ModerateThreatDefaultAction 'Quarantine'",
                "Set-MpPreference -LowThreatDefaultAction 'Quarantine'",
                "Set-MpPreference -SevereThreatDefaultAction 'Quarantine'"
            ]
            
            for command in ps_commands:
                try:
                    subprocess.run(['powershell', '-Command', command], check=True, capture_output=True)
                    self.logger.info(f"Applied Windows Defender setting: {command}")
                    self.hardening_results.append(f"Windows Defender: {command}")
                except subprocess.CalledProcessError as e:
                    self.logger.warning(f"Could not apply Windows Defender setting: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error configuring Windows Defender: {str(e)}")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate hardening report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_actions': len(self.hardening_results),
            'actions': self.hardening_results,
            'status': 'completed'
        }
    
    def save_report(self, filename: str = 'windows_hardening_report.yaml'):
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
    
    parser = argparse.ArgumentParser(description='Windows Server Hardening Tool')
    parser.add_argument('--policy', default='high_security', 
                       help='Security policy to apply')
    parser.add_argument('--config', default='config/hardening_config.yaml',
                       help='Configuration file path')
    parser.add_argument('--report', default='windows_hardening_report.yaml',
                       help='Report output file')
    parser.add_argument('--defender', action='store_true',
                       help='Configure Windows Defender')
    
    args = parser.parse_args()
    
    # Create hardening manager
    hardening_manager = WindowsHardeningManager(args.config)
    
    # Apply security policy
    success = hardening_manager.apply_security_policy(args.policy)
    
    # Configure Windows Defender if requested
    if args.defender:
        hardening_manager.configure_windows_defender()
    
    # Generate report
    hardening_manager.save_report(args.report)
    
    if success:
        print("✅ Windows hardening completed successfully!")
        sys.exit(0)
    else:
        print("❌ Windows hardening failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
