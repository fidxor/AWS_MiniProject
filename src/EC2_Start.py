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

# 중지된 인스턴스를 시작하는 함수
def start_stopped_instance(tag_key, tag_value):
    # 필터 조건 설정
    filters = [
        {
            'Name': f'tag:{tag_key}',
            'Values': [tag_value]
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

# 메인 함수
def main():
    # 특정 태그 정보
    tag_key = 'cloud'
    tag_value = 'project'
    
    # 중지된 인스턴스 시작
    start_stopped_instance(tag_key, tag_value)

if __name__ == '__main__':
    main()
