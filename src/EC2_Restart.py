<<<<<<< HEAD


# 실행 중인 인스턴스를 재부팅하는 함수
def reboot_running_instance(ec2, tag_key, tag_value):
=======
# 실행 중인 인스턴스를 재부팅하는 함수
def reboot_running_instance(ec2, tagName, tagValue):
>>>>>>> 2eecc42f6bc2cfafba6a2a9f894408b1b07ba12c
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

# 메인 함수
<<<<<<< HEAD
def restartEC2(ec2, tagName, tagValue):    
    
    # 실행 중인 인스턴스 재부팅
    reboot_running_instance(ec2, tagName, tagValue)
=======
def restartEC2(ec2, tagName, tagValue):
    # 실행 중인 인스턴스 재부팅
    reboot_running_instance(ec2, tagName, tagValue)
>>>>>>> 2eecc42f6bc2cfafba6a2a9f894408b1b07ba12c
