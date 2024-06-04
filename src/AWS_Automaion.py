import sys
import boto3
import json
from EC2_Maker import *
from SSH_Connect import *

with open("./data/AWS_Config.json", 'r') as config_file:
    config = json.load(config_file)

webConfig = config['web']
wasConfig = config['was']
dbConfig = config['db']

aws_access_key_id = os.getenv('AWS_ACCESS_KEY')
aws_secret_access_key = os.getenv('AWS_SECRET_KEY')
region_name = config['regionName']

# 클라이언트 생성
ec2 = boto3.client('ec2', 
                   aws_access_key_id=aws_access_key_id, 
                   aws_secret_access_key=aws_secret_access_key, 
                   region_name=region_name)

'''
sys로 외부 argument 받아서 create, delete, start, stop 구현 
create일 경우 몇개를 만들지 입력받음 default값은 1 

각 ec2에 필수 프로그램들 자동 실행 되도록 설정
delete, start, stop 일 경우 자동으로 만들어진 세트 ec2만 검색해서 작업함.

'''

# 1. webEC2 생성 및 초기 프로그램 설치
webInstanceid, webPrivateIP, webPublicIP, webKeyFile = make(ec2, webConfig, '0.0.0.0/0')
cmd = "sudo apt-get install -y net-tools nginx && sudo systemctl enable nginx"
ssh_to_instance(webPublicIP, webKeyFile, cmd)

# 2. wasEC2 생성 및 초기 프로그램 설치 설정. webEC2 로컬IP필요
wasInstanceid, wasPrivateIP, wasPublicIP, wasKeyFile = make(ec2, wasConfig, f'{webPrivateIP}/32')

wasSource = '''export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-amd64/
export CATALINA_HOME=/usr/local/tomcat
PATH=$PATH:$JAVA_HOME/bin:$CATALINA_HOME/bin
export CLASSPATH=.:$JAVA_HOME/lib/mariadb-java-client-2.7.5.jar:$CATALINA_HOME/lib/mariadb-java-client-2.7.5.jar
'''

cmd = """sudo apt-get update && sudo apt update && sudo apt install -y openjdk-8-jdk && \\
sudo wget http://archive.apache.org/dist/tomcat/tomcat-9/v9.0.4/bin/apache-tomcat-9.0.4.tar.gz && \\
sudo tar xvzf ./apache-tomcat-9.0.4.tar.gz && sudo mv ./apache-tomcat-9.0.4 /usr/local/tomcat && \\
sudo /usr/local/tomcat/bin/startup.sh && \\
sudo wget https://dlm.mariadb.com/1965742/Connectors/java/connector-java-2.7.5/mariadb-java-client-2.7.5.jar && \\
sudo cp mariadb-java-client-2.7.5.jar /usr/lib/jvm/java-1.8.0-openjdk-amd64/lib/ && \\
sudo cp mariadb-java-client-2.7.5.jar /usr/local/tomcat/lib/ && \\
sudo wget https://downloads.mysql.com/archives/get/p/3/file/mysql-connector-java-5.1.40.tar.gz && \\
sudo tar xvf mysql-connector-java-5.1.40.tar.gz && \\
sudo cp mysql-connector-java-5.1.40/mysql-connector-java-5.1.40-bin.jar /usr/local/tomcat/lib/ && \\
sudo chmod 666 /etc/profile && sudo echo '%s' >> /etc/profile && source /etc/profile
""" % (wasSource)

ssh_to_instance(wasPublicIP, wasKeyFile, cmd)
# # 3. wasEC2의 로컬 IP를 이용해서 webEC2의 /etc/nginx/sites-available/default 파일 설정
webSource = """
server {
        listen 80 default_server;

        server_name _;

        location / {
                index index.html index.htm index.jsp;
                proxy_pass http://%s:8080;
        }
}
""" % (wasPrivateIP)

cmd = f"sudo chmod 666 /etc/nginx/sites-available/default && sudo echo '{webSource}' > /etc/nginx/sites-available/default && sudo systemctl restart nginx"
ssh_to_instance(webPublicIP, webKeyFile, cmd)


# 4. dbEC2 생성및 초기 프로그램 설치 설정. wasEC2 로컬IP필요
dbInstanceid, dbPrivateIP, dbPublicIP, dbKeyFile = make(ec2, dbConfig, f'{wasPrivateIP}/32')

cmd = """sudo apt-get update && sudo apt update && \\
sudo apt install -y mariadb-server && \\
sudo sed -i 's/bind-address\\s*=\\s*127.0.0.1/bind-address = 0.0.0.0/' /etc/mysql/mariadb.conf.d/50-server.cnf && \\
sudo systemctl restart mariadb && \\
sudo systemctl enable mariadb && sudo mysqladmin -u root password abcd1234
"""
ssh_to_instance(dbPublicIP, dbKeyFile, cmd)