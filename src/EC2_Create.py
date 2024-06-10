import boto3
from EC2_Maker import *
from SSH_Connect import *

def createEC2(ec2, config, index):
    webConfig = config['web']
    wasConfig = config['was']
    dbConfig = config['db']

    tagName = config['tagName']
    tagValue = config['tagValue']

    '''
    sys로 외부 argument 받아서 create, delete, start, stop 구현 
    create일 경우 몇개를 만들지 입력받음 default값은 1 

    각 ec2에 필수 프로그램들 자동 실행 되도록 설정
    delete, start, stop 일 경우 자동으로 만들어진 세트 ec2만 검색해서 작업함.

    '''

    # 1. webEC2 생성 및 초기 프로그램 설치
    webInstanceid, webPrivateIP, webPublicIP, webKeyFile = make(ec2, webConfig, tagName, tagValue, index, '0.0.0.0/0')
    cmd = "sudo apt-get install -y net-tools nginx && sudo systemctl enable nginx"
    ssh_to_instance(webPublicIP, webKeyFile, cmd)

    # 2. wasEC2 생성 및 초기 프로그램 설치 설정. webEC2 로컬IP필요
    wasInstanceid, wasPrivateIP, wasPublicIP, wasKeyFile = make(ec2, wasConfig,  tagName, tagValue, index, f'{webPrivateIP}/32')


 # 줄바꿈 수정하지 말아주세요
    wasSource = '''export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-amd64/
export CATALINA_HOME=/usr/local/tomcat
PATH=$PATH:$JAVA_HOME/bin:$CATALINA_HOME/bin
export CLASSPATH=.:$JAVA_HOME/lib/mariadb-java-client-2.7.5.jar:$CATALINA_HOME/lib/mariadb-java-client-2.7.5.jar:$CATALINA_HOME/lib/mysql-connector-java-5.1.40-bin.jar
    '''

    tomcatSource = '''[Unit] 
Description=Startup script for Tomcat
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/tomcat/bin/startup.sh
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
'''

    cmd = """
    sudo apt-get update && sudo apt update && sudo apt install -y openjdk-8-jdk && \\
    sudo wget http://archive.apache.org/dist/tomcat/tomcat-9/v9.0.4/bin/apache-tomcat-9.0.4.tar.gz && \\
    sudo tar xvzf ./apache-tomcat-9.0.4.tar.gz && sudo mv ./apache-tomcat-9.0.4 /usr/local/tomcat && \\
    sudo wget https://dlm.mariadb.com/1965742/Connectors/java/connector-java-2.7.5/mariadb-java-client-2.7.5.jar && \\
    sudo cp mariadb-java-client-2.7.5.jar /usr/lib/jvm/java-1.8.0-openjdk-amd64/lib/ && \\
    sudo cp mariadb-java-client-2.7.5.jar /usr/local/tomcat/lib/ && \\
    sudo wget https://downloads.mysql.com/archives/get/p/3/file/mysql-connector-java-5.1.40.tar.gz && \\
    sudo tar xvf mysql-connector-java-5.1.40.tar.gz && \\
    sudo cp mysql-connector-java-5.1.40/mysql-connector-java-5.1.40-bin.jar /usr/local/tomcat/lib/ && \\
    sudo chmod 666 /etc/profile && echo '%s' | sudo tee -a /etc/profile && source /etc/profile && \\
    sudo touch /etc/systemd/system/tomcat_startup.service && sudo chmod 666 /etc/systemd/system/tomcat_startup.service && \\
    echo '%s' | sudo tee /etc/systemd/system/tomcat_startup.service && \\
    sudo /usr/local/tomcat/bin/startup.sh
    sudo systemctl daemon-reload && \\
    sudo systemctl enable tomcat_startup.service && \\
    sudo systemctl start tomcat_startup.service && \\
    sudo systemctl status tomcat && \\
    sudo chmod -R 777 /usr/local/tomcat/webapps/
    """ % (wasSource, tomcatSource)

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
    dbInstanceid, dbPrivateIP, dbPublicIP, dbKeyFile = make(ec2, dbConfig,  tagName, tagValue, index, f'{wasPrivateIP}/32')
    # dbInstanceid, dbPrivateIP, dbPublicIP, dbKeyFile = make(ec2, dbConfig, '0.0.0.0/0')

    # 초기 설정할 sql 파일 로드
    with open("./data/initQuery.sql", 'r') as sql_file:
        sqlFile = ""
        for line in sql_file:
            sqlFile += line


    print(sqlFile)

    # sudo apt-get install -y mysql-server-8.0
    # /etc/mysql/mysql.conf.d/mysqld.cnf

    '''
    cmd = """sudo apt-get update && sudo apt update && \\
    sudo apt install -y mysql-server-8.0 && \\
    sudo sed -i 's/127.0.0.1/0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf && \\
    sudo systemctl restart mysql && \\
    sudo systemctl enable mysql && sudo mysqladmin -u root password abcd1234 && \\
    echo '%s' > ./initSql.sql && sudo mysql -u root -pabcd1234 < ./initSql.sql
    """ % (sqlFile)    
    '''

    cmd = """sudo apt-get update && sudo apt update && \\
    sudo apt install -y mariadb-server && \\
    sudo sed -i 's/bind-address\\s*=\\s*127.0.0.1/bind-address = 0.0.0.0/' /etc/mysql/mariadb.conf.d/50-server.cnf && \\
    sudo systemctl restart mariadb && \\
    sudo systemctl enable mariadb && sudo mysqladmin -u root password abcd1234 && \\
    echo '%s' > ./initSql.sql && sudo mysql -u root -pabcd1234 < ./initSql.sql
    """ % (sqlFile)
    ssh_to_instance(dbPublicIP, dbKeyFile, cmd)

    #db 연결 확인용 jsp 파일
    with open("./data/connect_db.jsp", 'r') as jsp_file:
        jspFile = ""
        for line in jsp_file:
            jspFile += line

    cmd = f"sudo echo '{jspFile}' > /usr/local/tomcat/webapps/ROOT/connect_db.jsp && sudo sed -i 's/ipAddress/{dbPrivateIP}/' /usr/local/tomcat/webapps/ROOT/connect_db.jsp"

    ssh_to_instance(wasPublicIP, wasKeyFile, cmd)