import os

# 1. 키 페어 생성 및 다운로드
def create_key_pair(ec2, key_name):
    response = ec2.create_key_pair(KeyName=key_name)
    key_material = response['KeyMaterial']
    with open(f"./{key_name}.pem", 'w') as file:
        file.write(key_material)
    os.chmod(f"./{key_name}.pem", 0o400)
    print(f"Key pair {key_name} created and downloaded as {key_name}.pem")
    return f"{key_name}.pem"

def get_default_vpc_id(ec2):
    response = ec2.describe_vpcs(
        Filters=[
            {
                'Name': 'isDefault',
                'Values': ['true']
            }
        ]
    )
    default_vpc_id = response['Vpcs'][0]['VpcId']
    print(f"Default VPC ID: {default_vpc_id}")
    return default_vpc_id

# 2. 보안 그룹 생성 및 설정
def create_security_group(ec2, group_name, description, vpc_id, conf, privateIP):
    response = ec2.create_security_group(GroupName=group_name, Description=description, VpcId=vpc_id)
    security_group_id = response['GroupId']
    ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            # 22번 포트는 기본 default
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            },
            {
                'IpProtocol': 'tcp',
                'FromPort': conf['port'],
                'ToPort': conf['port'],
                'IpRanges': [{'CidrIp': f'{privateIP}'}]
            }
        ]
    )
    print(f"Security group {group_name} created with ID {security_group_id}")
    return security_group_id

# 3. EC2 인스턴스 생성
def create_ec2_instance(ec2, image_id, instance_type, key_name, security_group_ids, tags, block_device_mappings, user_data):
    response = ec2.run_instances(
        ImageId=image_id,
        InstanceType=instance_type,
        KeyName=key_name,
        SecurityGroupIds=security_group_ids,
        TagSpecifications=tags,
        BlockDeviceMappings=block_device_mappings,
        UserData=user_data,
        MinCount=1,
        MaxCount=1
    )

    instance_id = response['Instances'][0]['InstanceId']
    privateIP = response['Instances'][0]['PrivateIpAddress']

    # 아직 publicip가 할당이 안됐을수 있으니 기다린다.
    print(f'Waiting for instance {instance_id} to be in running state...')
    ec2.get_waiter('instance_running').wait(InstanceIds=[instance_id])

    # publicIP = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
    print(f'Created EC2 instance {instance_id}')
    return instance_id, privateIP

def make(ec2, conf, index = 1, privateIP = "0.0.0.0"):    
    key_name = f"{conf['instanceName']}{index}"
    key_file = create_key_pair(ec2, key_name)

    # vpc_id = 'vpc-0b10a563fee278371'
    vpc_id = get_default_vpc_id(ec2)
    print(f"vpc_id {vpc_id}")

    # 보안 그룹 생성
    group_name = f'{key_name}_sg'
    description = f'Security group for {key_name} instance'
    security_group_id = create_security_group(ec2, group_name, description, vpc_id, conf, privateIP)

    # EC2 인스턴스 생성
    image_id = conf['imageID']  # Ubuntu 22.04 LTS의 AMI ID
    instance_type = conf['instanceType']
    tags = [
        {
            'ResourceType': 'instance',
            'Tags': [
                {'Key': 'Name', 'Value': key_name}                
            ]
        }
    ]
    
    block_device_mappings = [
        {
            'DeviceName': '/dev/sda1',
            'Ebs': {
                'DeleteOnTermination': conf['deviceMapping']['Ebs']['DeleteOnTermination'],
                'VolumeSize': conf['deviceMapping']['Ebs']['VolumeSize'],  # 8 GiB
                'VolumeType': conf['deviceMapping']['Ebs']['VolumeType']
            }
        }
    ]

    user_data = '''#!/bin/bash
    echo "Hello, World!" > /var/www/html/index.html
    '''

    instance_id, privateIP = create_ec2_instance(ec2, image_id, instance_type, key_name, [security_group_id], tags, block_device_mappings, user_data)

    response = ec2.describe_instances(InstanceIds=[instance_id])
    publicIP = response['Reservations'][0]['Instances'][0]['PublicIpAddress']

    return instance_id, privateIP, publicIP, key_file