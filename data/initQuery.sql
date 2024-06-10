create database cloud_db;
create user 'mydb'@'ipAddress';
grant all privileges on cloud_db.* to 'mydb'@'ipAddress';
flush privileges;