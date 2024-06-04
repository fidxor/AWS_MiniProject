import paramiko
import time

# 4. 인스턴스가 실행될 때까지 대기
def wait_until_running(ec2, instance_id):
    print("Waiting for instance to be running...")
    waiter = ec2.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])
    print("Instance is now running")

# 5. SSH로 인스턴스에 연결하여 명령 실행
def ssh_to_instance(ip_address, key_file, cmd, username='ubuntu', max_attempts=20, sleep_time=3):
    key = paramiko.RSAKey.from_private_key_file(key_file)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print(f'Connecting to {ip_address}...')
    for attempt in range(max_attempts):
        try:
            print(f"Connecting to {ip_address} (Attempt {attempt + 1}/{max_attempts})...")
            client.connect(hostname=ip_address, username=username, pkey=key)
            print('Connected!')
            break
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            time.sleep(sleep_time)  # 잠시 대기 후 다시 시도  
    

    stdin, stdout, stderr = client.exec_command(cmd)
    print('stdout:', stdout.read())
    print('stderr:', stderr.read())

    client.close()