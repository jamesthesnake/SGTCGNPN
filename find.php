//Used to create a fasta file from GeneClusters

<?php
$servername = "localhost";
$username = "root";
$password = "***";
$dbname = "GNPNDB";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
     die("Connection failed: " . $conn->connect_error);
     }
$nam= $_POST['Cluster'];
$name=$nam."%";
$version=$_POST['Version']."%";
//echo $name;
$sql = "SELECT * FROM Gene  where GeneName LIKE '".$name."'";
$result = $conn->query($sql);
$x=1;
$geneArray=array();
$nameArray=array();
$cassNumTable=array();
if ($result->num_rows >0) {
    // output data of each row
        while($row = $result->fetch_assoc()) {

		$nameArray[]=$row['GeneName'];
		$curve= strlen($row['ONS']);
		$nameforGene=substr($row['ONS'] ,50,curve-50);
	
		$geneArray[]=$nameforGene;
		$cassNumTable[]="'".$row['GeneID']."'";

		$x=$x+1;
		    }
		    } else {
		        echo "0 results";
			}
$x=1;
$cassNumTable=implode(",",$cassNumTable);
echo print_r($cassNumTable);
$cass="SELECT OOP FROM Cassette WHERE GeneID IN (".$cassNumTable.")";
$orderTable=array();
$cassResults=$conn->query($cass);
if($cassResults->num_rows >0){
	while($rower=$cassResults->fetch_assoc()){	
	$orderTable[]="'".$rower['OOP']."'";
	}
} else{
   echo "nO LUCK";
}
$tLength= count($orderTable);



$x=0;

$prom=array();
$term=array();
$x=0;
echo print_r($orderTable);
while($x<$tLength){
 $places = "SELECT Promoter FROM VTwoTwo WHERE GenePlace IN (".$orderTable[$x].")";
 
    if($x!=$tLength-1){
     $extra=$x+1;
     
       if($orderTable[$extra] != "'1'" || $orderTable[$x] =="'1f'"){
              $spaces = "SELECT Terminator FROM VTwoTwo WHERE GenePlace in (".$orderTable[$x].")";
 
         }else{
	    $spaces = "SELECT Terminator FROM VTwoTwo WHERE GenePlace IN (".$orderTable[0].")";


        } 
     }
    else{
       $spaces = "SELECT Terminator FROM VTwoTwo WHERE GenePlace IN (".$orderTable[0].")";


    }

      $resulters =$conn ->query($places);
    if ($resulters->num_rows > 0) {
    // output data of each row
            while($rows= $resulters->fetch_assoc()) {
                   $prom[]=$rows['Promoter'];
       }
       }
$resulters =$conn ->query($spaces);
if ($resulters->num_rows > 0) {
    // output data of each row
                while($rows= $resulters->fetch_assoc()) {
		                            $term[]=$rows['Terminator'];

						                                    }
										    

									}
$x=$x+1;
}
echo print_r($prom);
//$finalProm= implode(",",$prom);
//$finalTerm= implode(",",$term);
$x=0;
echo $nam."Cluster"."<br>";
$promArray=array();
$termArray=array();
$length=count($prom);
$lengthT=count($term);

$filledPromoter=array();
$seqPlace=array();

while($x<$length){
$seqP=" SELECT Sequence,CommonName FROM Promoter where CommonName LIKE '".$prom[$x]."'";
$seqT=" SELECT Sequence,CommonName FROM Terminator where CommonName = '".$term[$x]."'";
echo $prom[$x]."<br>";
echo $term[$x]."<br>";
$sequenceT= $conn->query($seqT);   
$sequenceP= $conn->query($seqP);


if($sequenceP->num_rows>0){
//  if($v>0){
    // output data of each row
    
    while($finalP= $sequenceP->fetch_assoc()){
    		  
		 
		   		 
    		   if(in_array($prom[$x],$filledPromoter)){
		 
		  
		  $key=array_search($prom[$x],$filledPromoter);
		  $promArray[]=$seqPlace[$key];
		  echo "<br>".$promArray[$x]."<br>";
    //$promArray[]=$filledPromoter[$prom[$x]];
			}else{
   
    $promArray[]=$finalP['Sequence'];
    $filledPromoter[]= $prom[$x];
    echo "Fyre"."<br>".$finalP['Sequence']."<br>";
	
    $seqPlace[]=$finalP['Sequence'];
    }

 
}

                    } else {
                        echo "0 results";
			     	}
if($sequenceT->num_rows>0) {
    // output data of each row



while($finalT= $sequenceT->fetch_assoc()){
     $termArray[]=$finalT['Sequence'];

    }
                    } else {
		                            echo "0 results";

}

$x=$x+1;
}






$termArray[]=$termArray[0];
$x=0;



$finalString="";
foreach($geneArray as $value){
      // $rest=substr($termArray[$x],50,strlen($termArray[$x]));
      // $tired=substr($promArray[$x],0,strlen($promArray[$x])-50);
       
       echo ">".$nameArray[$x]."<br>";
       echo $promArray[$x].$geneArray[$x].$termArray[$x]."<br>";
       $finalString=$finalString.">".$nameArray[$x]."\n";
       $finalString=$finalString.$promArray[$x].$geneArray[$x].$termArray[$x]."\n";      
       $x=$x+1;
}



$myfile = fopen("file.fasta", "w") or die("Unable to open file!");
fwrite($myfile, $finalString);

fclose($myfile);
//chomd($myfile,0777);
//$output=shell_exec(" python genebank.py ".$nam.".fasta 'Clusters' ".$nam.".fasta 'KU32'");
$conn->close();
?>

<button type="button" onclick="location.href='download.php'">Download the GenebankFile</button>


<button type="button" onclick="location.href='downloads.php'">Download the Fasta File</button>
