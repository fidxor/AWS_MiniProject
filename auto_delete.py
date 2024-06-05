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

# 태그 기반으로 보안 그룹 삭제
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

# 태그 기반으로 키 페어 삭제
def delete_key_pairs_by_tag(tag_key, tag_value):
    # 키 페어 이름 가져오기
    response = ec2.describe_key_pairs(
        Filters=[
            {
                'Name': f'tag:{tag_key}',
                'Values': [tag_value]
            }
        ]
    )
    
    key_names = [kp['KeyName'] for kp in response['KeyPairs']]
    
    if not key_names:
        print("No key pairs found with the specified tag.")
        return
    
    # 키 페어 삭제
    for key_name in key_names:
        ec2.delete_key_pair(KeyName=key_name)
        if os.path.exists(f"./{key_name}.pem"):
            os.remove(f"./{key_name}.pem")
        print(f"Key pair {key_name} and file {key_name}.pem deleted.")

# 메인 함수
def main():
    # 태그 기반으로 인스턴스, 보안 그룹, 키 페어 삭제
    tag_key = 'cloud'
    tag_value = 'project'
    
    terminate_instances_by_tag(tag_key, tag_value)
    delete_security_groups_by_tag(tag_key, tag_value)
    delete_key_pairs_by_tag(tag_key, tag_value)

if __name__ == '__main__':
    main()
