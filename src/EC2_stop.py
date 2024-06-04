import boto3

# AWS 자격 증명 설정 (환경 변수나 aws configure를 사용하여 설정된 상태여야 합니다)
aws_access_key_id = 'AKIAYS2NWAAC7EGXENS4'
aws_secret_access_key = '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'
region_name = 'ap-northeast-2'

# 클라이언트 생성
ec2 = boto3.client('ec2', 
                   aws_access_key_id=aws_access_key_id, 
                   aws_secret_access_key=aws_secret_access_key, 
                   region_name=region_name)

# 특정 태그를 가진 EC2 인스턴스 검색
def get_instance_id_by_tag(tag_filters):
    response = ec2.describe_instances(
        Filters=tag_filters
    )
    instances = response['Reservations']
    if not instances:
        print(f"No instances found with specified tags")
        return None
    
    instance_ids = [instance['Instances'][0]['InstanceId'] for instance in instances]
    print(f"Found instances {instance_ids} with specified tags")
    return instance_ids

# EC2 인스턴스 중지
def stop_ec2_instance(instance_ids):
    response = ec2.stop_instances(InstanceIds=instance_ids)
    print(f'Stopping EC2 instances {instance_ids}')
    return response

# 메인 함수
def main():
    # 중지할 인스턴스의 태그
    tag_key1 = 'Name'
    tag_value1 = 'db_1141'#input(f"Enter the value for the tag '{tag_key1}': ")

    tag_key2 = 'Creator'
    tag_value2 = 'jessy'#input(f"Enter the value for the tag '{tag_key2}': ")

    # 태그 필터 구성
    tag_filters = [
        {'Name': f'tag:{tag_key1}', 'Values': [tag_value1]},
        {'Name': f'tag:{tag_key2}', 'Values': [tag_value2]}
    ]
    
    instance_ids = get_instance_id_by_tag(tag_filters)
    
    if instance_ids:
        stop_ec2_instance(instance_ids)

if __name__ == '__main__':
    main()
