# AWS Server Hardening Framework

A comprehensive AWS server hardening framework that provides automated Linux and Windows server hardening with security compliance, monitoring, and best practices. This project implements CIS benchmarks, security hardening, compliance monitoring, and automated remediation for enterprise environments.

## 🎯 Overview

This project provides a complete server hardening solution including:

- **Linux Server Hardening** - Automated Linux security hardening with CIS benchmarks
- **Windows Server Hardening** - Automated Windows security hardening and compliance
- **Security Compliance** - CIS benchmarks, STIG, and custom security policies
- **Automated Hardening** - Infrastructure as Code for server hardening
- **Compliance Monitoring** - Continuous compliance monitoring and reporting
- **Remediation Automation** - Automated security remediation and patching
- **Security Baselines** - Pre-configured security baselines for different environments

## 🏗️ Architecture

### Server Hardening Components
```
AWS Server Hardening Framework
├── Linux Hardening
│   ├── CIS Benchmarks Implementation
│   ├── Security Configuration Management
│   ├── User Access Control
│   ├── Network Security Hardening
│   └── System Hardening
├── Windows Hardening
│   ├── Group Policy Management
│   ├── Security Policy Configuration
│   ├── Windows Defender Configuration
│   ├── User Account Control
│   └── Registry Hardening
├── Security Compliance
│   ├── CIS Benchmark Compliance
│   ├── STIG Compliance
│   ├── Custom Security Policies
│   ├── Compliance Reporting
│   └── Audit Trails
├── Automated Hardening
│   ├── Infrastructure as Code
│   ├── Automated Deployment
│   ├── Configuration Management
│   ├── Patch Management
│   └── Security Updates
├── Compliance Monitoring
│   ├── Continuous Monitoring
│   ├── Security Scanning
│   ├── Vulnerability Assessment
│   ├── Compliance Validation
│   └── Alert Management
└── Remediation
    ├── Automated Remediation
    ├── Security Patching
    ├── Configuration Drift Detection
    ├── Incident Response
    └── Recovery Procedures
```

## 📁 Project Structure

```
aws-server-hardening/
├── README.md                           # This documentation
├── python/                             # Python hardening automation
│   ├── linux_hardening/                # Linux hardening automation
│   │   ├── cis_benchmark.py           # CIS benchmark implementation
│   │   ├── security_config.py         # Security configuration
│   │   ├── user_management.py         # User access control
│   │   ├── network_hardening.py       # Network security
│   │   └── system_hardening.py        # System hardening
│   ├── windows_hardening/              # Windows hardening automation
│   │   ├── group_policy.py            # Group policy management
│   │   ├── security_policy.py         # Security policy configuration
│   │   ├── windows_defender.py        # Windows Defender setup
│   │   ├── user_accounts.py           # User account management
│   │   └── registry_hardening.py      # Registry hardening
│   ├── compliance/                     # Compliance automation
│   │   ├── compliance_checker.py      # Compliance validation
│   │   ├── audit_reporter.py          # Audit reporting
│   │   ├── policy_enforcer.py         # Policy enforcement
│   │   └── baseline_manager.py        # Security baseline management
│   ├── monitoring/                     # Monitoring automation
│   │   ├── security_monitor.py        # Security monitoring
│   │   ├── vulnerability_scanner.py   # Vulnerability scanning
│   │   ├── drift_detector.py          # Configuration drift detection
│   │   └── alert_manager.py           # Alert management
│   └── remediation/                    # Remediation automation
│       ├── auto_remediation.py        # Automated remediation
│       ├── patch_manager.py           # Patch management
│       ├── incident_response.py       # Incident response
│       └── recovery_manager.py        # Recovery procedures
├── terraform/                          # Terraform infrastructure
│   ├── main.tf                        # Main Terraform configuration
│   ├── variables.tf                   # Terraform variables
│   ├── outputs.tf                     # Terraform outputs
│   ├── modules/                       # Terraform modules
│   │   ├── linux_hardening/           # Linux hardening module
│   │   ├── windows_hardening/         # Windows hardening module
│   │   ├── compliance_monitoring/     # Compliance monitoring module
│   │   ├── security_baselines/        # Security baselines module
│   │   └── remediation/               # Remediation module
│   └── examples/                      # Example configurations
├── cloudformation/                    # CloudFormation templates
│   ├── server-hardening.yaml          # Main server hardening template
│   ├── linux-hardening.yaml           # Linux hardening template
│   ├── windows-hardening.yaml         # Windows hardening template
│   ├── compliance-monitoring.yaml     # Compliance monitoring template
│   └── security-baselines.yaml        # Security baselines template
├── hardening-scripts/                 # Hardening scripts
│   ├── linux/                         # Linux hardening scripts
│   │   ├── cis_benchmark.sh           # CIS benchmark implementation
│   │   ├── security_config.sh         # Security configuration
│   │   ├── user_management.sh         # User management
│   │   ├── network_hardening.sh       # Network hardening
│   │   └── system_hardening.sh        # System hardening
│   ├── windows/                       # Windows hardening scripts
│   │   ├── group_policy.ps1           # Group policy configuration
│   │   ├── security_policy.ps1        # Security policy setup
│   │   ├── windows_defender.ps1       # Windows Defender configuration
│   │   ├── user_accounts.ps1          # User account management
│   │   └── registry_hardening.ps1     # Registry hardening
│   └── ansible/                       # Ansible playbooks
│       ├── linux_hardening.yml        # Linux hardening playbook
│       ├── windows_hardening.yml      # Windows hardening playbook
│       ├── compliance_check.yml       # Compliance checking
│       └── remediation.yml            # Remediation playbook
├── security-baselines/                # Security baseline configurations
│   ├── linux/                         # Linux security baselines
│   │   ├── cis_ubuntu_20.04.yml       # CIS Ubuntu 20.04 baseline
│   │   ├── cis_centos_8.yml           # CIS CentOS 8 baseline
│   │   ├── cis_amazon_linux_2.yml     # CIS Amazon Linux 2 baseline
│   │   └── custom_baseline.yml        # Custom security baseline
│   ├── windows/                       # Windows security baselines
│   │   ├── cis_windows_server_2019.yml # CIS Windows Server 2019 baseline
│   │   ├── stig_windows_server_2019.yml # STIG Windows Server 2019 baseline
│   │   ├── custom_windows_baseline.yml # Custom Windows baseline
│   │   └── group_policy_objects/      # Group Policy Objects
│   └── compliance/                    # Compliance configurations
│       ├── cis_benchmarks/            # CIS benchmark configurations
│       ├── stig_guidelines/           # STIG guideline configurations
│       ├── custom_policies/           # Custom security policies
│       └── compliance_reports/        # Compliance report templates
├── monitoring/                        # Monitoring configurations
│   ├── cloudwatch/                    # CloudWatch monitoring
│   │   ├── security_metrics.json      # Security metrics
│   │   ├── compliance_dashboard.json  # Compliance dashboard
│   │   └── alerting_rules.json        # Alerting rules
│   ├── security_hub/                  # Security Hub integration
│   │   ├── custom_findings.json       # Custom security findings
│   │   ├── compliance_standards.json  # Compliance standards
│   │   └── remediation_actions.json   # Remediation actions
│   └── config/                        # AWS Config rules
│       ├── linux_compliance_rules.json # Linux compliance rules
│       ├── windows_compliance_rules.json # Windows compliance rules
│       └── custom_rules.json          # Custom compliance rules
├── config/                            # Configuration files
│   ├── hardening_config.yaml          # Hardening configuration
│   ├── compliance_config.yaml         # Compliance configuration
│   ├── monitoring_config.yaml         # Monitoring configuration
│   ├── baseline_config.yaml           # Baseline configuration
│   └── remediation_config.yaml        # Remediation configuration
├── scripts/                           # Deployment and utility scripts
│   ├── deploy_hardening.sh            # Deploy server hardening
│   ├── setup_compliance.sh            # Setup compliance monitoring
│   ├── run_hardening_scan.sh          # Run hardening scan
│   ├── apply_security_baseline.sh     # Apply security baseline
│   └── generate_compliance_report.sh  # Generate compliance report
├── dashboards/                        # Monitoring dashboards
│   ├── security_dashboard.json        # Security monitoring dashboard
│   ├── compliance_dashboard.json      # Compliance dashboard
│   ├── hardening_status_dashboard.json # Hardening status dashboard
│   └── remediation_dashboard.json     # Remediation dashboard
└── requirements.txt                   # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
1. **AWS CLI** installed and configured
2. **Python 3.8+** for hardening automation
3. **Terraform** (for Terraform implementation)
4. **Ansible** (for configuration management)
5. **PowerShell** (for Windows hardening)
6. **AWS Permissions** - EC2, Systems Manager, Config, Security Hub permissions

### Installation

#### 1. Clone and Setup
```bash
cd projects/aws-server-hardening
pip install -r requirements.txt
```

#### 2. Configure Hardening Framework
```bash
cp config/hardening_config.yaml.example config/hardening_config.yaml
# Edit configuration with your security requirements
```

#### 3. Deploy Infrastructure
```bash
# Using Terraform
cd terraform
terraform init
terraform plan
terraform apply

# Using CloudFormation
cd cloudformation
./deploy_hardening.sh
```

#### 4. Apply Security Baselines
```bash
# For Linux servers
./scripts/apply_security_baseline.sh linux

# For Windows servers
./scripts/apply_security_baseline.sh windows
```

#### 5. Setup Compliance Monitoring
```bash
./scripts/setup_compliance.sh
```

## 🔧 Core Features

### 1. Linux Server Hardening

#### CIS Benchmark Implementation
```python
# Automated CIS benchmark compliance
- CIS Ubuntu 20.04 LTS Benchmark
- CIS CentOS 8 Benchmark
- CIS Amazon Linux 2 Benchmark
- Custom security baselines
- Automated compliance checking
```

#### Security Configuration
```python
# Comprehensive security configuration
- User access control and management
- Network security hardening
- System hardening and lockdown
- Service hardening and optimization
- File system security
```

### 2. Windows Server Hardening

#### Group Policy Management
```python
# Automated Group Policy configuration
- Security policy enforcement
- User account control
- Windows Defender configuration
- Registry hardening
- Audit policy configuration
```

#### Security Policy Configuration
```python
# Security policy automation
- Password policy enforcement
- Account lockout policies
- Audit policy configuration
- Security options hardening
- User rights assignment
```

### 3. Security Compliance

#### Compliance Standards
```python
# Multiple compliance frameworks
- CIS Benchmarks compliance
- STIG guidelines compliance
- Custom security policies
- Industry-specific compliance
- Regulatory compliance (SOX, HIPAA, PCI)
```

#### Compliance Monitoring
```python
# Continuous compliance monitoring
- Real-time compliance checking
- Automated compliance reporting
- Compliance drift detection
- Remediation tracking
- Audit trail management
```

### 4. Automated Hardening

#### Infrastructure as Code
```python
# IaC for server hardening
- Terraform hardening modules
- CloudFormation hardening templates
- Ansible hardening playbooks
- Automated deployment
- Configuration management
```

#### Security Baselines
```python
# Pre-configured security baselines
- Production security baseline
- Development security baseline
- High-security baseline
- Compliance-specific baselines
- Custom baseline creation
```

### 5. Compliance Monitoring

#### Continuous Monitoring
```python
# Real-time security monitoring
- Security configuration monitoring
- Compliance status tracking
- Vulnerability scanning
- Security event monitoring
- Performance impact monitoring
```

#### Alert Management
```python
# Intelligent alerting system
- Security violation alerts
- Compliance drift alerts
- Remediation failure alerts
- Performance impact alerts
- Escalation procedures
```

### 6. Remediation Automation

#### Automated Remediation
```python
# Self-healing security
- Automatic security fixes
- Configuration drift correction
- Vulnerability remediation
- Patch management
- Incident response automation
```

#### Recovery Procedures
```python
# Disaster recovery for security
- Security baseline recovery
- Configuration backup and restore
- Rollback procedures
- Incident recovery
- Business continuity
```

## 🛠️ Implementation Examples

### Python Implementation

#### Linux Hardening Manager
```python
# python/linux_hardening/cis_benchmark.py
import subprocess
import yaml
import logging
from typing import Dict, List, Any

class LinuxHardeningManager:
    """
    Linux Server Hardening Manager for CIS benchmark implementation.
    """
    
    def __init__(self, config_file: str = 'config/hardening_config.yaml'):
        self.config = self.load_config(config_file)
        self.logger = logging.getLogger(__name__)
        
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load hardening configuration."""
        try:
            with open(config_file, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            return {}
    
    def apply_cis_benchmark(self, benchmark_version: str = 'ubuntu_20.04'):
        """Apply CIS benchmark hardening."""
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
            
        except Exception as e:
            self.logger.error(f"Error applying CIS benchmark: {str(e)}")
    
    def _harden_system_settings(self, system_config: Dict[str, Any]):
        """Harden system settings."""
        try:
            # Disable unnecessary services
            for service in system_config.get('disable_services', []):
                subprocess.run(['systemctl', 'disable', service], check=True)
                subprocess.run(['systemctl', 'stop', service], check=True)
            
            # Configure system parameters
            for param, value in system_config.get('sysctl_params', {}).items():
                subprocess.run(['sysctl', '-w', f'{param}={value}'], check=True)
            
            # Apply kernel parameters
            for param, value in system_config.get('kernel_params', {}).items():
                with open(f'/proc/sys/{param}', 'w') as f:
                    f.write(str(value))
                    
        except Exception as e:
            self.logger.error(f"Error hardening system settings: {str(e)}")
    
    def _harden_network_settings(self, network_config: Dict[str, Any]):
        """Harden network settings."""
        try:
            # Configure firewall rules
            for rule in network_config.get('firewall_rules', []):
                subprocess.run(['iptables', '-A'] + rule.split(), check=True)
            
            # Configure network parameters
            for param, value in network_config.get('network_params', {}).items():
                subprocess.run(['sysctl', '-w', f'net.{param}={value}'], check=True)
                
        except Exception as e:
            self.logger.error(f"Error hardening network settings: {str(e)}")
    
    def _harden_user_management(self, user_config: Dict[str, Any]):
        """Harden user management."""
        try:
            # Configure password policy
            subprocess.run(['chage', '-M', str(user_config.get('max_days', 90)), 'root'], check=True)
            
            # Configure account lockout
            subprocess.run(['pam_tally2', '--deny', str(user_config.get('max_attempts', 5))], check=True)
            
            # Remove unnecessary users
            for user in user_config.get('remove_users', []):
                subprocess.run(['userdel', '-r', user], check=True)
                
        except Exception as e:
            self.logger.error(f"Error hardening user management: {str(e)}")
    
    def _harden_file_system(self, fs_config: Dict[str, Any]):
        """Harden file system security."""
        try:
            # Set file permissions
            for file_path, permissions in fs_config.get('file_permissions', {}).items():
                subprocess.run(['chmod', permissions, file_path], check=True)
            
            # Set directory permissions
            for dir_path, permissions in fs_config.get('directory_permissions', {}).items():
                subprocess.run(['chmod', permissions, dir_path], check=True)
                
        except Exception as e:
            self.logger.error(f"Error hardening file system: {str(e)}")
```

#### Windows Hardening Manager
```python
# python/windows_hardening/group_policy.py
import subprocess
import yaml
import logging
from typing import Dict, List, Any

class WindowsHardeningManager:
    """
    Windows Server Hardening Manager for Group Policy and security configuration.
    """
    
    def __init__(self, config_file: str = 'config/hardening_config.yaml'):
        self.config = self.load_config(config_file)
        self.logger = logging.getLogger(__name__)
        
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load hardening configuration."""
        try:
            with open(config_file, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            return {}
    
    def apply_security_policy(self, policy_name: str = 'high_security'):
        """Apply security policy configuration."""
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
            
        except Exception as e:
            self.logger.error(f"Error applying security policy: {str(e)}")
    
    def _configure_password_policy(self, password_config: Dict[str, Any]):
        """Configure password policy."""
        try:
            # Set minimum password length
            subprocess.run([
                'net', 'accounts', '/minpwlen:' + str(password_config.get('min_length', 12))
            ], check=True)
            
            # Set password complexity
            subprocess.run([
                'net', 'accounts', '/pwcomplexity:' + str(password_config.get('complexity', 1))
            ], check=True)
            
            # Set password history
            subprocess.run([
                'net', 'accounts', '/uniquepw:' + str(password_config.get('history', 24))
            ], check=True)
            
            # Set maximum password age
            subprocess.run([
                'net', 'accounts', '/maxpwage:' + str(password_config.get('max_age', 90))
            ], check=True)
            
        except Exception as e:
            self.logger.error(f"Error configuring password policy: {str(e)}")
    
    def _configure_account_lockout(self, lockout_config: Dict[str, Any]):
        """Configure account lockout policy."""
        try:
            # Set lockout threshold
            subprocess.run([
                'net', 'accounts', '/lockoutthreshold:' + str(lockout_config.get('threshold', 5))
            ], check=True)
            
            # Set lockout duration
            subprocess.run([
                'net', 'accounts', '/lockoutduration:' + str(lockout_config.get('duration', 30))
            ], check=True)
            
            # Set lockout window
            subprocess.run([
                'net', 'accounts', '/lockoutwindow:' + str(lockout_config.get('window', 30))
            ], check=True)
            
        except Exception as e:
            self.logger.error(f"Error configuring account lockout: {str(e)}")
    
    def _configure_audit_policy(self, audit_config: Dict[str, Any]):
        """Configure audit policy."""
        try:
            # Set audit policy categories
            for category, setting in audit_config.get('categories', {}).items():
                subprocess.run([
                    'auditpol', '/set', '/category:' + category, setting
                ], check=True)
            
            # Set audit policy subcategories
            for subcategory, setting in audit_config.get('subcategories', {}).items():
                subprocess.run([
                    'auditpol', '/set', '/subcategory:' + subcategory, setting
                ], check=True)
                
        except Exception as e:
            self.logger.error(f"Error configuring audit policy: {str(e)}")
    
    def _configure_security_options(self, security_config: Dict[str, Any]):
        """Configure security options."""
        try:
            # Configure security options using registry
            for key, value in security_config.get('registry_settings', {}).items():
                subprocess.run([
                    'reg', 'add', key, '/v', value['name'], '/t', value['type'], 
                    '/d', str(value['data']), '/f'
                ], check=True)
                
        except Exception as e:
            self.logger.error(f"Error configuring security options: {str(e)}")
```

### Terraform Implementation

#### Linux Hardening Module
```hcl
# terraform/modules/linux_hardening/main.tf
resource "aws_systems_manager_document" "linux_hardening" {
  name          = "${var.project_name}-linux-hardening"
  document_type = "Command"
  document_format = "YAML"

  content = yamlencode({
    schemaVersion = "2.2"
    description   = "Linux Server Hardening Automation"
    parameters = {
      BenchmarkVersion = {
        type = "String"
        default = "ubuntu_20.04"
        description = "CIS Benchmark version to apply"
      }
    }
    mainSteps = [
      {
        action = "aws:runShellScript"
        name   = "ApplyCISBenchmark"
        inputs = {
          runCommand = [
            "#!/bin/bash",
            "cd /opt/aws-server-hardening",
            "python3 hardening_manager.py --benchmark ${BenchmarkVersion}",
            "echo 'Linux hardening completed successfully'"
          ]
        }
      },
      {
        action = "aws:runShellScript"
        name   = "VerifyCompliance"
        inputs = {
          runCommand = [
            "#!/bin/bash",
            "cd /opt/aws-server-hardening",
            "python3 compliance_checker.py --os linux",
            "echo 'Compliance verification completed'"
          ]
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-linux-hardening"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_systems_manager_association" "linux_hardening" {
  name = aws_systems_manager_document.linux_hardening.name

  targets {
    key    = "tag:OS"
    values = ["Linux"]
  }

  schedule_expression = "rate(1 day)"

  tags = {
    Name        = "${var.project_name}-linux-hardening-association"
    Environment = var.environment
  }
}

# Security Group for hardened Linux instances
resource "aws_security_group" "hardened_linux" {
  name_prefix = "${var.project_name}-hardened-linux-"
  vpc_id      = var.vpc_id

  # SSH access (restricted)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidrs
    description = "SSH access from allowed CIDRs"
  }

  # HTTPS access
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.allowed_https_cidrs
    description = "HTTPS access"
  }

  # HTTP access (if required)
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.allowed_http_cidrs
    description = "HTTP access"
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-hardened-linux-sg"
    Environment = var.environment
    Project     = var.project_name
  }
}

# IAM role for Linux hardening
resource "aws_iam_role" "linux_hardening_role" {
  name = "${var.project_name}-linux-hardening-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-linux-hardening-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy" "linux_hardening_policy" {
  name = "${var.project_name}-linux-hardening-policy"
  role = aws_iam_role.linux_hardening_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:SendCommand",
          "ssm:GetParameter",
          "ssm:PutParameter",
          "cloudwatch:PutMetricData",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}
```

#### Windows Hardening Module
```hcl
# terraform/modules/windows_hardening/main.tf
resource "aws_systems_manager_document" "windows_hardening" {
  name          = "${var.project_name}-windows-hardening"
  document_type = "Command"
  document_format = "YAML"

  content = yamlencode({
    schemaVersion = "2.2"
    description   = "Windows Server Hardening Automation"
    parameters = {
      SecurityLevel = {
        type = "String"
        default = "high"
        description = "Security level to apply"
      }
    }
    mainSteps = [
      {
        action = "aws:runPowerShellScript"
        name   = "ApplySecurityPolicy"
        inputs = {
          runCommand = [
            "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Force",
            "cd C:\\aws-server-hardening",
            "python hardening_manager.py --os windows --level ${SecurityLevel}",
            "Write-Host 'Windows hardening completed successfully'"
          ]
        }
      },
      {
        action = "aws:runPowerShellScript"
        name   = "VerifyCompliance"
        inputs = {
          runCommand = [
            "cd C:\\aws-server-hardening",
            "python compliance_checker.py --os windows",
            "Write-Host 'Compliance verification completed'"
          ]
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-windows-hardening"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_systems_manager_association" "windows_hardening" {
  name = aws_systems_manager_document.windows_hardening.name

  targets {
    key    = "tag:OS"
    values = ["Windows"]
  }

  schedule_expression = "rate(1 day)"

  tags = {
    Name        = "${var.project_name}-windows-hardening-association"
    Environment = var.environment
  }
}

# Security Group for hardened Windows instances
resource "aws_security_group" "hardened_windows" {
  name_prefix = "${var.project_name}-hardened-windows-"
  vpc_id      = var.vpc_id

  # RDP access (restricted)
  ingress {
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = var.allowed_rdp_cidrs
    description = "RDP access from allowed CIDRs"
  }

  # HTTPS access
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.allowed_https_cidrs
    description = "HTTPS access"
  }

  # HTTP access (if required)
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.allowed_http_cidrs
    description = "HTTP access"
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-hardened-windows-sg"
    Environment = var.environment
    Project     = var.project_name
  }
}

# IAM role for Windows hardening
resource "aws_iam_role" "windows_hardening_role" {
  name = "${var.project_name}-windows-hardening-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-windows-hardening-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy" "windows_hardening_policy" {
  name = "${var.project_name}-windows-hardening-policy"
  role = aws_iam_role.windows_hardening_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:SendCommand",
          "ssm:GetParameter",
          "ssm:PutParameter",
          "cloudwatch:PutMetricData",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}
```

## 📊 Security Dashboard

### Server Hardening Dashboard
```json
{
  "dashboard": {
    "title": "Server Hardening Overview",
    "panels": [
      {
        "title": "Hardening Compliance Status",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(server_hardening_compliance{status=\"compliant\"}) / sum(server_hardening_compliance) * 100",
            "legendFormat": "Compliance Rate %"
          }
        ]
      },
      {
        "title": "Security Violations by OS",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(security_violations_total[5m])) by (os_type)",
            "legendFormat": "{{os_type}}"
          }
        ]
      },
      {
        "title": "Remediation Success Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(remediation_attempts_total{status=\"success\"}[5m])) / sum(rate(remediation_attempts_total[5m])) * 100",
            "legendFormat": "Success Rate %"
          }
        ]
      }
    ]
  }
}
```

## 🔒 Security Features

### Hardening Standards
- **CIS Benchmarks** - Industry-standard security benchmarks
- **STIG Guidelines** - Security Technical Implementation Guides
- **Custom Security Policies** - Organization-specific requirements
- **Compliance Frameworks** - SOX, HIPAA, PCI, GDPR compliance

### Security Controls
- **Access Control** - User management and authentication
- **Network Security** - Firewall and network hardening
- **System Security** - OS hardening and configuration
- **Application Security** - Application-level security controls
- **Data Protection** - Encryption and data security

## 📈 Performance Optimization

### Hardening Optimization
- **Baseline Templates** - Pre-configured security baselines
- **Automated Deployment** - Infrastructure as Code deployment
- **Configuration Management** - Automated configuration management
- **Performance Monitoring** - Impact assessment and monitoring

## 📞 Support and Resources

### Documentation
- [CIS Benchmarks](https://www.cisecurity.org/benchmark/)
- [STIG Guidelines](https://public.cyber.mil/stigs/)
- [AWS Systems Manager](https://docs.aws.amazon.com/systems-manager/)
- [AWS Config](https://docs.aws.amazon.com/config/)

### Community Resources
- [AWS Security Blog](https://aws.amazon.com/blogs/security/)
- [CIS Security Blog](https://www.cisecurity.org/blog/)
- [Microsoft Security Blog](https://www.microsoft.com/security/blog/)

### Professional Services
- AWS Professional Services
- CIS Security Services
- Microsoft Security Services

## 📄 License

This project is provided as-is for educational and demonstration purposes. Please review and modify according to your specific security requirements and compliance policies.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 Changelog

### Version 1.0.0
- Initial release with comprehensive server hardening framework
- Linux server hardening with CIS benchmarks
- Windows server hardening with Group Policy
- Security compliance monitoring and reporting
- Automated remediation and patching
- Security baselines and templates
- Terraform and CloudFormation implementations
- Python automation scripts and Ansible playbooks
