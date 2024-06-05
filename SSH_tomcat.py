import boto3
import os

# AWS 자격 증명 설정 (환경 변수나 aws configure를 사용하여 설정된 상태여야 합니다)
aws_access_key_id = 'AKIA47CRVHADYMOJZ7JU'
aws_secret_access_key = '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'
region_name = 'ap-northeast-2'

# 클라이언트 생성
ec2 = boto3.client('ec2', 
                   aws_access_key_id=aws_access_key_id, 
                   aws_secret_access_key=aws_secret_access_key, 
                   region_name=region_name)

# 1. 키 페어 생성 및 다운로드
def create_key_pair(key_name):
    response = ec2.create_key_pair(KeyName=key_name)
    key_material = response['KeyMaterial']
    with open(f"./{key_name}.pem", 'w') as file:
        file.write(key_material)
    os.chmod(f"{key_name}.pem", 0o400)
    print(f"Key pair {key_name} created and downloaded as {key_name}.pem")

# 2. 보안 그룹 생성 및 설정
def create_security_group(group_name, description, vpc_id):
    response = ec2.create_security_group(GroupName=group_name, Description=description, VpcId=vpc_id)
    security_group_id = response['GroupId']
    ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 8080,
                'ToPort': 8080,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }
        ]
    )
    print(f"Security group {group_name} created with ID {security_group_id}")
    return security_group_id

# 3. EC2 인스턴스 생성
def create_ec2_instance(image_id, instance_type, key_name, security_group_ids, tags, block_device_mappings, user_data):
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
    print(f'Created EC2 instance {instance_id}')
    return instance_id

# 메인 함수
def main():
    key_name = 'web_1'
    create_key_pair(key_name)

    vpc_id = 'vpc-03d0413f1a6a38505'
    
    # 보안 그룹 생성
    group_name = 'was_1_sg'
    description = 'Security group for web_1 instance'
    security_group_id = create_security_group(group_name, description, vpc_id)
    
    # EC2 인스턴스 생성
    image_id = 'ami-01ed8ade75d4eee2f'  # Ubuntu 22.04 LTS의 AMI ID
    instance_type = 't2.micro'
    tags = [
        {
            'ResourceType': 'instance',
            'Tags': [
                {'Key': 'Name', 'Value': 'was_1'}
            ]
        }
    ]
    
    block_device_mappings = [
        {
            'DeviceName': '/dev/sda1',
            'Ebs': {
                'DeleteOnTermination': True,
                'VolumeSize': 8,  # 8 GiB
                'VolumeType': 'gp3'
            }
        }
    ]
    
    user_data = '''#!/bin/bash
    wget https://dlm.mariadb.com/1965742/Connectors/java/connector-java-2.7.5/mariadb-java-client-2.7.5.jar
    cp mariadb-java-client-2.7.5.jar /usr/lib/jvm/java-1.8.0-openjdk-amd64/lib/
    cp mariadb-java-client-2.7.5.jar /usr/local/tomcat/lib/
    wget https://downloads.mysql.com/archives/get/p/3/file/mysql-connector-java-5.1.40.tar.gz
    tar xvf mysql-connector-java-5.1.40.tar.gz
    cp mysql-connector-java-5.1.40/mysql-connector-java-5.1.40-bin.jar /usr/local/tomcat/lib/
    /usr/local/tomcat/bin/startup.sh
    '''

    create_ec2_instance(image_id, instance_type, key_name, [security_group_id], tags, block_device_mappings, user_data)

    os.environ['AWS_ACCESS_KEY_ID'] = 'AKIA47CRVHADYMOJZ7JU'
    os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
    os.environ['AWS_REGION'] = 'ap-northeast-2'

if __name__ == '__main__':
    main()
