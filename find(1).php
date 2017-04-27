
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
$nam= $_POST['Cluster'];
$name=$nam."%";
$version=$_POST['Version']."%";
//echo $name;
$sql = "SELECT GeneName, ONS,Translations FROM Gene  where GeneName LIKE '".$name."'";
$places = "SELECT Promoter,Terminator FROM VTwoTwo";

$result = $conn->query($sql);
$resulters =$conn ->query($places);
$x=1;
$v=1;
$geneArray=array();
$nameArray=array();
if ($result->num_rows >0) {
    // output data of each row
        while($row = $result->fetch_assoc()) {
//	while($v<8){
		$nameArray[]=$row['GeneName'];
		$geneArray[]=$row['ONS'];
	//        echo "gene".$x. $row['ONS']. "<br>";
		$x=$x+1;
		//$v=$v+1;
		   // }
		    }
		    } else {
		        echo "0 results";
			}
$x=1;
$prom=array();
$term=array();
if ($resulters->num_rows > 0) {
    // output data of each row
            while($rows= $resulters->fetch_assoc()) {
                            $prom[]="'".$rows['Promoter']."'";
			    $term[]="'".$rows['Terminator']."'";



$x=$x+1;
				                    }
						                        } else {
									                        echo "0 results";
												                        }
$finalProm= implode(",",$prom);
$finalTerm= implode(",",$term);

$seqP=" SELECT Sequence,CommonName FROM Promoter where CommonName in (".$finalProm.")";
$seqT=" SELECT Sequence,CommonName FROM Terminator where CommonName in (".$finalTerm.")";


$sequenceT= $conn->query($seqT);   
$sequenceP= $conn->query($seqP);
$promArray=array();
$termArray=array();
$x=0;

if($sequenceP->num_rows>0) {
    // output data of each row
while($finalP= $sequenceP->fetch_assoc()){
    $key= array_search($prom[$x],$finalP['CommonName']);
    $promArray[]=$finalP['Sequence'];
    	
} 

              
        
                    
                    } else {
                        echo "0 results";
			     	}
if($sequenceT->num_rows>0) {
    // output data of each row



while($finalT= $sequenceT->fetch_assoc()){
     $termArray[]=$finalT['Sequence'];
     echo"Term".$finalT['CommonName']. "<br>";
    }
                    } else {
		                            echo "0 results";
					                                    }

$termArray[]=$termArray[0];
$x=0;



$finalString="";
foreach($geneArray as $value){
      // $rest=substr($termArray[$x],50,strlen($termArray[$x]));
      // $tired=substr($promArray[$x],0,strlen($promArray[$x])-50);

       echo ">".$prom[$x]." ".$nameArray[$x]." ".$term[$x]."<br>";
       echo $promArray[$x]."<br>"."<br>".$geneArray[$x]."<br>"."<br>".$termArray[$x]."<br>";
       $finalString=$finalString.">".$nameArray[$x]."\n";
       $finalString=$finalString.$promArray[$x].$geneArray[$x].$termArray[$x]."\n";      
       $x=$x+1;
}



$myfile = fopen($nam.".fasta", "w") or die("Unable to open file!");
fwrite($myfile, $finalString);
echo $myfile;
fclose($myfile);
//chomd($myfile,0777);
$output=shell_exec(" python genebank.py ".$nam.".fasta 'Clusters' ".$nam.".fasta 'KU32'");
$conn->close();
?>

<button type="button" onclick="location.href='download.php'">Download the GenebankFile</button>


<button type="button" onclick="location.href='downloads.php'">Download the Fasta File</button>
