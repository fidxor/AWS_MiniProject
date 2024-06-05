create database cloud_db;
create user 'mydb'@'%' identified by 'abcd1234';
grant all privileges on *.* to 'mydb'@'%';
flush privileges;