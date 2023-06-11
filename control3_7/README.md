CIS AWS Foundations Benchmark v1.4.0 Remediations

CIS-140 #[CloudTrail.2] CloudTrail should have encryption at-rest enabled
Remediation Playbook to remediate Control 3.7 of the AWS Foundations Benchmark v1.4.0, “ensure CloudTrail logs are encrypted at rest using AWS Key Management Service (KMS) Customer Managed Keys (CMK).” Configuring CloudTrail to use KMS encryption (called SSE-KMS) provides additional confidentiality controls on you log data.

Related requirements: PCI DSS v3.2.1/3.4, CIS AWS Foundations Benchmark v1.2.0/2.7, CIS AWS Foundations Benchmark v1.4.0/3.7, NIST.800-53.r5 AU-9, NIST.800-53.r5 CA-9(1), NIST.800-53.r5 CM-3(6), NIST.800-53.r5 SC-13, NIST.800-53.r5 SC-28, NIST.800-53.r5 SC-28(1), NIST.800-53.r5 SC-7(10), NIST.800-53.r5 SI-7(6)