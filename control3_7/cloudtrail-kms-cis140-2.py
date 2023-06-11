import boto3
import json
import time

def lambda_handler(event, context):
    # parse noncompliant trail from SecHub finding
    noncompliantTrail = str(event['detail']['findings'][0]['Resources'][0]['Details']['AwsCloudTrailTrail']['Name'])
    # parse account id from noncompliant SecHub finding
    accountID = str(event['detail']['findings'][0]['AwsAccountId'])
    
    #import boto3 clients for KMS and cloudtrail.
    kms = boto3.client('kms')
    cloudtrail = boto3.client('cloudtrail')
    
    # Create a new KMS key to encrypt and decrypt the non-compliant trail.
    try:
        createKey = kms.create_key(
            Description='Generated by SecHub to remediate CIS 2.7 Ensure CloudTrail logs are encrypted at rest using KMS-CMk',
            KeyUsage='ENCRYPT_DECRYPT',
            Origin='AWS_KMS'          
        )

        # save the keyId as variable
        cloudtrailKey = str(createKey['KeyMetadata']['KeyId'])
        print("KMS Key ID" + " " + cloudtrailKey)
    except Exception as e:
        print(e)
        print("KMS key creation failed")
        raise

    # wait for two secs for key creation to complete
    time.sleep(2)

    # Attach alias to the KMS key for easy identification
    try:
        createAlias = kms.create_alias(
            AliasName='alias/' + noncompliantTrail + '-CMK5',
            TargetKeyId=cloudtrailKey
        )
        print(createAlias)
    except Exception as e:
        print(e)
        print("KMS Alias creation failed")
        raise

    # wait for 2 sec
    time.sleep(2)

    # set key policy in JSON
    keyPolicy = {
        "Version": "2012-10-17",
        "Id": "Key policy created by CloudTrail",
        "Statement": [
            {
                "Sid": "Enable IAM User Permissions",
                "Effect": "Allow",
                "Principal": {
                    "AWS": [ "arn:aws:iam::" + accountID + ":root" ]
                },
                "Action": "kms:*",
                "Resource": "*"
            },
            {
                "Sid": "Allow CloudTrail to encrypt logs",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudtrail.amazonaws.com"
                },
                "Action": "kms:GenerateDataKey*",
                "Resource": "*",
                "Condition": {
                    "StringLike": {
                        "kms:EncryptionContext:aws:cloudtrail:arn": "arn:aws:cloudtrail:*:" + accountID + ":trail/" + noncompliantTrail
                    }
                }
            },
            {
                "Sid": "Allow CloudTrail to describe key",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudtrail.amazonaws.com"
                },
                "Action": "kms:DescribeKey",
                "Resource": "*"
            },
            {
                "Sid": "Allow principals in the account to decrypt log files",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "*"
                },
                "Action": [
                    "kms:Decrypt",
                    "kms:ReEncryptFrom"
                ],
                "Resource": "*",
                "Condition": {
                    "StringEquals": {
                        "kms:CallerAccount": accountID
                    },
                    "StringLike": {
                        "kms:EncryptionContext:aws:cloudtrail:arn": "arn:aws:cloudtrail:*:" + accountID + ":trail/" + noncompliantTrail
                    }
                }
            },
            {
                "Sid": "Allow alias creation during setup",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "*"
                },
                "Action": "kms:CreateAlias",
                "Resource": "*",
                "Condition": {
                    "StringEquals": {
                        "kms:CallerAccount": accountID
                    }
                }
            }
        ]
    }

    # attaches above key policy to key
    # policy name for putkey is always default
    try:
        attachKeyPolicy = kms.put_key_policy(
            KeyId=cloudtrailKey,
            PolicyName='default',
            Policy=json.dumps(keyPolicy),
        )
        print(attachKeyPolicy)
    except Exception as e:
        print(e)
        print("Failed to attach key policy" + " " + cloudtrailKey)
        raise

    # Update cloudtrail with the new CMK
    try:
        encryptTrail = cloudtrail.update_trail(
            Name=noncompliantTrail,
            KmsKeyId=cloudtrailKey,
        )
        print(encryptTrail)
    except Exception as e:
        print(e)
        print("Failed to attach KMS key" + " " + cloudtrailKey)
        raise