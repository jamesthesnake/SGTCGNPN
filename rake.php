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
$table="Beiber";
$sql="SELECT * FROM `mama`";
$result= $conn->query($sql);
$full=array();
echo "Born";
$i=0;
if ($result->num_rows >0) {
   echo "Yolo"."<br>";
 while($row = $result->fetch_assoc()) {
 	  $full[]=$row;
	 
	  print_r($row);
	  echo $row['POS']."<br>";
          if($row['POS']=='1f'){
		$full[$i]['Promoter']=60;
		$full[$i]['Terminator']=7;
	  }
	  else if($row['POS']=='1'){
			
                $full[$i]['Promoter']=26;
		$full[$i]['Terminator']=15;
          }
          else if($row['POS']=='2'){
			
                $full[$i]['Promoter']=55;
                $full[$i]['Terminator']=5;
          }
          else if($row['POS']=='3'){
			
                $full[$i]['Promoter']=17;
                $full[$i]['Terminator']=3;
          }
	   else if($row['POS']=='4'){
			
                $full[$i]['Promoter']=26;
                $full[$i]['Terminator']=15;
          }
          else if($row['POS']=='5'){
			
                $full[$i]['Promoter']=59;
                $full[$i]['Terminator']=1;
          }
          else if($row['POS']=='6'){
			
                $full[$i]['Promoter']=57;
                $full[$i]['Terminator']=2;
          }
          else if($row['POS']=='7'){
			
                $full[$i]['Promoter']=26;
                $full[$i]['Terminator']=7;
          }


	  $i=$i+1;
	}
}
$length=count(array_column($full,'Promoter'));
for($i=1;$i<$length;$i++){
	if( $full[$i]['POS']<$full[$i-1]['POS']){
	    $full[$i-1]['Terminator']='7';  

	}

}
$fp=fopen("news.csv","w");

foreach ($full as $fields) {
    fputcsv($fp, $fields);
    }
fclose($fp);
?>
<button type="button" onclick="location.href='dloads.php'">here</button>
