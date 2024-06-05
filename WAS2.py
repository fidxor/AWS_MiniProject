import boto3
import os

# AWS 자격 증명 설정 (환경 변수나 aws configure를 사용하여 설정된 상태여야 합니다)
aws_access_key_id = 'AKIA47CRVHADWIRRJCK5'
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

    # 키페어에 태그 지정
    ec2.create_tags(
        Resources=[response['KeyPairId']],  # 생성된 키페어의 ID
        Tags=[
            {'Key': 'Name', 'Value': key_name},
            {'Key': 'cloud', 'Value': 'project'}
        ]
    )

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
            },
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }
        ]
    )
    print(f"Security group {group_name} created with ID {security_group_id}")
    
    
    # 보안 그룹에 태그 지정
    ec2.create_tags(
        Resources=[security_group_id],  # 생성된 보안 그룹의 ID
        Tags=[
            {'Key': 'Name', 'Value': group_name},
            {'Key': 'cloud', 'Value': 'project'}
        ]
    )
    
    return security_group_id

# 기본 VPC ID 조회
def get_default_vpc_id():
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
    key_name = 'was_1'
    create_key_pair(key_name)

    vpc_id = get_default_vpc_id()
    
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
                {'Key': 'Name', 'Value': 'was_1'},
                {'Key': 'cloud', 'Value': 'project'}
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
    
    source = """
export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-amd64/
export CATALINA_HOME=/usr/local/tomcat
PATH=$PATH:$JAVA_HOME/bin:$CATALINA_HOME/bin
export CLASSPATH=.:$JAVA_HOME/lib/mariadb-java-client-2.7.5.jar:$CATALINA_HOME/lib/mariadb-java-client-2.7.5.jar
"""

    user_data = '''#!/bin/bash
    sudo su &&\
    sudo apt-get update -y &&\
    sudo apt-get install -y wget openjdk-8-jdk &&\
    wget http://archive.apache.org/dist/tomcat/tomcat-9/v9.0.4/bin/apache-tomcat-9.0.4.tar.gz &&\
    tar xvzf ./apache-tomcat-9.0.4.tar.gz &&\
    mv ./apache-tomcat-9.0.4 /usr/local/tomcat &&\
    /usr/local/tomcat/bin/startup.sh
    sudo chmod 666 /etc/profile &&\
    sudo echo "%s" | sudo tee -a /etc/profile &&\
    sudo source /etc/profile
    ''' % (source)

    create_ec2_instance(image_id, instance_type, key_name, [security_group_id], tags, block_device_mappings, user_data)

if __name__ == '__main__':
    main()

