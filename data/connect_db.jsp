<%@ page import = "java.sql.*"%>

<%
Connection conn=null;
ResultSet result=null;
Statement stmt=null;

ResultSetMetaData rsmd=null;
try {
  Class c=Class.forName("com.mysql.jdbc.Driver");
}
catch(Exception e){
  out.write("Error!!!!!!" + e);
}
try {
  conn=DriverManager.getConnection("jdbc:mysql://ipAddress:3306/cloud_db", "mydb", "");
  out.write("<font color='blue'>Connected!</font>");
}
catch(SQLException e) {
  System.out.println("Error!!!!!!" + e);
}
%>