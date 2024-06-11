import os

# 인스턴스 종료 및 삭제
def terminate_instances_by_tag(ec2, tagName, tagValue):
    # 인스턴스 ID 가져오기
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': f'tag:{tagName}',
                'Values': [tagValue]
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
def delete_security_groups_by_tag(ec2, tagName, tagValue):
    # 보안 그룹 ID 가져오기
    response = ec2.describe_security_groups(
        Filters=[
            {
                'Name': f'tag:{tagName}',
                'Values': [tagValue]
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
def delete_key_pairs_by_tag(ec2, tagName, tagValue):
    # 키 페어 이름 가져오기
    response = ec2.describe_key_pairs(
        Filters=[
            {
                'Name': f'tag:{tagName}',
                'Values': [tagValue]
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

# 태그 기반으로 스냅샷 삭제
def delete_snapshot_by_tag(ec2, tagName, tagValue):
    response = ec2.describe_snapshots(
        Filters=[
            {
                'Name':f'tag:{tagName}',
                'Values': [tagValue]
            }
        ]
    )

    snapshots = response['Snapshots']

    # 스냅샷 삭제
    for snapshot in snapshots:
        snapshot_id = snapshot['SnapshotId']
        print(f"Deleting snapshot {snapshot_id}...")
        ec2.delete_snapshot(SnapshotId=snapshot_id)
        print(f"Deleted snapshot {snapshot_id}")

# 메인 함수
def deleteEC2(ec2, tagName, tagValue):
    terminate_instances_by_tag(ec2, tagName, tagValue)
    delete_security_groups_by_tag(ec2, tagName, tagValue)
    delete_key_pairs_by_tag(ec2, tagName, tagValue)
    delete_snapshot_by_tag(ec2, tagName, tagValue)
