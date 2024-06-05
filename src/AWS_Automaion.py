import sys
import boto3
import json
from EC2_Create import *
from EC2_Maker import *
from SSH_Connect import *
from EC2_Stop import *
from EC2_Start import *

option = ""
createCnt = 1

print(sys.argv)

if len(sys.argv) == 2:
    option = sys.argv[1]
elif len(sys.argv) > 2:
    option = sys.argv[1]
    createCnt = int(sys.argv[2])
else:
    print(os.getenv('AWS_ACCESS_KEY'))
    print(os.getenv('AWS_SECRET_KEY'))
    print("옵션을 지정해 주세요.")
    exit(1)

print(option)

with open("./data/AWS_Config.json", 'r') as config_file:
    config = json.load(config_file)

aws_access_key_id = os.getenv('AWS_ACCESS_KEY')
aws_secret_access_key = os.getenv('AWS_SECRET_KEY')
region_name = config['regionName']

# 클라이언트 생성
ec2 = boto3.client('ec2', 
                   aws_access_key_id=aws_access_key_id, 
                   aws_secret_access_key=aws_secret_access_key, 
                   region_name=region_name)

if option == "create":
    for i in range(1, createCnt + 1):
        createEC2(ec2, config, i)
elif option == "delete":
    #deleteEC2(ec2, config['tagName'], config['tagValue'])
    print("delete EC2")
elif option == "start":
    startEC2(ec2, config['tagName'], config['tagValue'])    
elif option == "stop":
    #stopEC2(ec2, config['tagName'], config['tagValue'])
    print("stop EC2")
else:
    print("옵션값이 잘못 되었습니다.")