# 중지된 인스턴스를 시작하는 함수
def startEC2(ec2, tagName, tagValue):
    # 필터 조건 설정
    filters = [
        {
            'Name': f'tag:{tagName}',
            'Values': [tagValue]
        },
        {
            'Name': 'instance-state-name',
            'Values': ['stopped']
        }
        
    ]
    
    # 중지된 인스턴스 조회
    response = ec2.describe_instances(Filters=filters)
    
    # 중지된 인스턴스가 있을 경우 시작
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            print(f"Starting instance {instance_id}")
            ec2.start_instances(InstanceIds=[instance_id])
            print(f"Instance {instance_id} started successfully.")
