<?php
$servername = "localhost";
$username = "root";
$password = "HiMommy12";
$dbname = "GNPNDB";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
     die("Connection failed: " . $conn->connect_error);
          }
	  $name= $_POST['Cluster']."%";
	  $version=$_POST['Version']."%";
	  //echo $name;
	  $sql = "SELECT GeneID, GeneName,CDS,ONS FROM Gene  where GeneName LIKE '%added_1%'";
	  $places = "SELECT Promoter,Terminator FROM".$version;
$n=5;
$result = $conn->query($sql);
$resulters =$conn ->query($places);
if ($result->num_rows > 0) {
    // output data of each row
            while($row = $result->fetch_assoc()) {
	    //      while($v<8){
	                           $best=  $row['CDS'];
				   $finalnum=substr($best,-1);
				   if ($finalnum==$n){
				                $x=$x+1;
						              

}												                           } else {
															                           echo "0 results";
																		                           }
																					   
$conn->close();
?>

>