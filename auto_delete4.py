import boto3
import os
from dotenv import load_dotenv
import subprocess

# .env 파일에서 환경 변수 로드
load_dotenv()

setx AWS_ACCESS_KEY_ID "AKIA47CRVHADYUD7ST42"
setx AWS_SECRET_ACCESS_KEY "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"
setx AWS_DEFAULT_REGION "ap-northeast-2"

# 클라이언트 생성
ec2 = boto3.client('ec2', 
                   aws_access_key_id=aws_access_key_id, 
                   aws_secret_access_key=aws_secret_access_key, 
                   region_name=region_name)

# 인스턴스 종료 및 삭제
def terminate_instances_by_tag(tag_key, tag_value):
    # 인스턴스 ID 가져오기
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': f'tag:{tag_key}',
                'Values': [tag_value]
            }
        ]
    )
    
    instance_ids = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])
    
    if not instance_ids:
        print("No instances found with the specified tag.")
        return
    
    # 인스턴스 종료
    ec2.terminate_instances(InstanceIds=instance_ids)
    print(f"Terminating EC2 instances {instance_ids}")
    waiter = ec2.get_waiter('instance_terminated')
    waiter.wait(InstanceIds=instance_ids)
    print(f"EC2 instances {instance_ids} terminated.")

# 보안 그룹 삭제
def delete_security_groups_by_tag(tag_key, tag_value):
    # 보안 그룹 ID 가져오기
    response = ec2.describe_security_groups(
        Filters=[
            {
                'Name': f'tag:{tag_key}',
                'Values': [tag_value]
            }
        ]
    )
    
    security_group_ids = [sg['GroupId'] for sg in response['SecurityGroups']]
    
    if not security_group_ids:
        print("No security groups found with the specified tag.")
        return
    
    # 보안 그룹 삭제
    for sg_id in security_group_ids:
        ec2.delete_security_group(GroupId=sg_id)
        print(f"Security group with ID {sg_id} deleted.")

# 키 페어 삭제
def delete_key_pair(key_name):
    ec2.delete_key_pair(KeyName=key_name)
    if os.path.exists(f"./{key_name}.pem"):
        # 파일 권한 변경 (Windows)
        if os.name == 'nt':
            subprocess.run(['icacls', f"{key_name}.pem", '/grant', 'Users:(F)'])
        # 파일 삭제
        os.remove(f"./{key_name}.pem")
        print(f"Key pair {key_name} and file {key_name}.pem deleted.")

# 메인 함수
def main():
    key_name = 'was_1'
    
    # 태그 기반 인스턴스 및 보안 그룹 삭제
    tag_key = 'Name'
    tag_value = 'was_1'
    
    terminate_instances_by_tag(tag_key, tag_value)
    delete_security_groups_by_tag(tag_key, tag_value)
    delete_key_pair(key_name)

if __name__ == '__main__':
    main()
