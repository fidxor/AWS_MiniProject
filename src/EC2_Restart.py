# 실행 중인 인스턴스를 재부팅하는 함수
def restartEC2(ec2, tagName, tagValue):
    # 필터 조건 설정
    filters = [
        {
            'Name': f'tag:{tagName}',
            'Values': [tagValue]
        },
        {
            'Name': 'instance-state-name',
            'Values': ['running']
        }
    ]
    
    # 실행 중인 인스턴스 조회
    response = ec2.describe_instances(Filters=filters)
    
    # 실행 중인 인스턴스가 있을 경우 재부팅
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            print(f"Rebooting instance {instance_id}")
            ec2.reboot_instances(InstanceIds=[instance_id])
            print(f"Instance {instance_id} rebooted successfully.")
