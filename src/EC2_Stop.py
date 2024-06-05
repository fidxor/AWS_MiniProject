# 특정 태그를 가진 EC2 인스턴스 검색
def get_instance_id_by_tag(ec2, filters):
    response = ec2.describe_instances(
        Filters=filters
    )
    instances = response['Reservations']
    if not instances:
        print(f"No instances found with specified tags")
        return None
    
    instance_ids = [instance['Instances'][0]['InstanceId'] for instance in instances]
    print(f"Found instances {instance_ids} with specified tags")
    return instance_ids

# EC2 인스턴스 중지
def stop_ec2_instance(ec2, instance_ids):
    response = ec2.stop_instances(InstanceIds=instance_ids)
    print(f'Stopping EC2 instances {instance_ids}')
    return response

# 메인 함수
def stopEC2(ec2, tagName, tagValue):
    # 태그 필터 구성
    filters = [
        {'Name': tagName,'Values': tagValue}
    ]
    
    instance_ids = get_instance_id_by_tag(filters)
    
    if instance_ids:
        stop_ec2_instance(ec2, instance_ids)
