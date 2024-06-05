import boto3

# AWS 자격 증명 설정 (환경 변수나 aws configure를 사용하여 설정된 상태여야 합니다)
aws_access_key_id = 'AKIATCKATRPTLBDP4BGU'
aws_secret_access_key = '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'
region_name = 'ap-northeast-2'

# 클라이언트 생성
ec2 = boto3.client('ec2', 
                   aws_access_key_id=aws_access_key_id, 
                   aws_secret_access_key=aws_secret_access_key, 
                   region_name=region_name)

# 실행 중인 인스턴스를 재부팅하는 함수
def reboot_running_instance(tag_key, tag_value):
    # 필터 조건 설정
    filters = [
        {
            'Name': f'tag:{tag_key}',
            'Values': [tag_value]
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
def main():
    # 특정 태그 정보
    tag_key = 'cloud'
    tag_value = 'project'
    
    # 실행 중인 인스턴스 재부팅
    reboot_running_instance(tag_key, tag_value)

if __name__ == '__main__':
    main()
