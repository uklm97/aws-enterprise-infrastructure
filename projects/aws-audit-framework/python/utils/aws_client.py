from typing import Dict, Any, Optional

try:
    import boto3  # type: ignore
except Exception:
    boto3 = None  # type: ignore

class AWSClientManager:
    """
    Manages initialization of AWS service clients used by the audit framework.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config or {}
        self.region = self.config.get('aws_region') or 'us-east-1'
        self.profile = self.config.get('aws_profile')

    def initialize_clients(self) -> Dict[str, Any]:
        if boto3 is None:
            # Return empty client map if boto3 is not available; modules guard for this
            return {}

        session_kwargs: Dict[str, Any] = {}
        if self.profile:
            session_kwargs['profile_name'] = self.profile
        session = boto3.Session(**session_kwargs)

        client_names = [
            'iam', 'ec2', 's3', 'rds', 'kms', 'cloudtrail', 'securityhub',
            'guardduty', 'cloudwatch', 'ce', 'sts'
        ]
        clients: Dict[str, Any] = {}
        for name in client_names:
            try:
                clients[name] = session.client(name, region_name=self.region)
            except Exception:
                # Non-fatal; module code guards for missing clients
                continue
        return clients
