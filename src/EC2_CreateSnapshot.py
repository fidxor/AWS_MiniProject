def createSnapshot(ec2, instanceID, tagName, tagValue):
    instance = ec2.describe_instances(InstanceIds=[instanceID])

    volumeId = instance['Reservations'][0]['Instances'][0]['BlockDeviceMappings'][0]['Ebs']['VolumeId']

    tags = [
                {'Key': tagName, 'Value': tagValue},
    ]

    description = f"Snapshot of volume {volumeId} from instance {instanceID}"

    response = ec2.create_snapshot(VolumeId=volumeId, Description=description)
    snapshot_id = response['SnapshotId']
    #스냅샷 완료 대기
    ec2.get_waiter('snapshot_completed').wait(SnapshotIds=[snapshot_id])
    print(f"Snapshot {snapshot_id} is now available")

    #스냅샷 태그 지정
    ec2.create_tags(Resources=[snapshot_id], Tags=tags)