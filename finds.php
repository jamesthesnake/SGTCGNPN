<?php
//connect to the server 
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
	  $name=$nam;
	  $version=$_POST['Version']."%";
	  echo $name;
	  $sql = "SELECT Distinct(GeneClusterID) FROM EngineeredGeneClusters  where ClusterName LIKE '".$name."' And Version LIKE 2.2";
	  $result = $conn->query($sql);
	  $x=1;
	  $geneArray=array();
	  $nameArray=array();
if ($result->num_rows >0) {
    // output data of each row
            while($row = $result->fetch_assoc()) {
	    	       $nameArray=$row;
		
		                    }
				                        } else {
							                        echo "0 results";
										                        }

$spot= $nameArray['GeneClusterID'];
$sql="SELECT * FROM  Cassette Where GeneClusterID =".$spot;
$result = $conn->query($sql);
echo $spot;	  
$full=array();
if ($result->num_rows >0) {
										    // output data of each row
										    	            while($row = $result->fetch_assoc()) {							     											    $full[]=$row;
        
		                    }
				                        } else {
							                        echo "0 results";
										                        }


										
									        $nameArray=array();							       $promArray=array();							      $termArray=array();							     $resistArray=array();							    $cassNumTable=array();
										$nameProm=array();
										$nameTerm=array();
										$geneArray=array();																							   $length=count($full);
										$backboneArray=array();
										echo "<br>".$length."<br>"."bird"."<br>";																		
$j=0;
for($i=0;$i<$length;$i++){
										
$sql=" SELECT * From Gene Where GeneID=".$full[$i]['GeneID'];
										
									
$result= $conn->query($sql);

if ($result->num_rows >0) {
										    // output data of each row
										            while($row = $result->fetch_assoc()) {
											       //cut off the overhangs for the genes and  get the names of the		      // gene for the fasta file
                $nameArray[]=$row['GeneName'];
		$curve= strlen($row['ONS'])-50;
		$nameforGene=substr($row['ONS'] ,50,$curve);
                $geneArray[]=$nameforGene;
		$cassNumTable[]="'".$row['GeneID']."'";
		$x=$x+1;
		}
				                        }
	else {
											echo "0 results";
										       }
										//get the promoter sequences			
$sql="SELECT * FROM Promoter Where PromoterID=".$full[$i]['PromoterID'];
$result= $conn->query($sql);

if ($result->num_rows >0) {
    // output data of each row
                while($row = $result->fetch_assoc()) {
		                       $promArray[]=$row;
				       $nameProm[]=$row['CommonName'];
			
				       
                 }
				                                                            } else {
											    echo "0 results";
											    }

//select the Resitance Sequences for the plasmid 
$sql="SELECT Sequence FROM Resist Where ResistID =(Select ResistanceID From NewPlasmidID Where PlasmidID =  ".$full[$i]['PlasmidID'].")";
$result= $conn->query($sql);
echo "<br>".$full[$i]['PlasmidID']."<br>";
if ($result->num_rows >0) {
    // output data of each row
                  while($row = $result->fetch_assoc()) {
	
		        $resistArray[]=$row['Sequence'];
			}
				                                                                                                                                    }										  else {													                                                                    echo "0 results";                                                                                         
																				    }

//get Backbone Sequences from the plasmid and append them to the end of the final terminator sequence in each plasmid 
$sql="SELECT Sequence FROM backbone Where backboneid in(Select BackboneID From NewPlasmidID Where PlasmidID =  ".$full[$i]['PlasmidID'].")";
$result= $conn->query($sql);

if ($result->num_rows >0) {
    // output data of each row
                      while($row = $result->fetch_assoc()) {
		      $backboneArray[]=$row;

              	   }
										}
										else {
												     echo "0 results";
}

//Select the Terminators
$sql="SELECT * FROM Terminator Where TerminatorID=".$full[$i]['TerminatorID'];
$result= $conn->query($sql);


if ($result->num_rows >0) {
    // output data of each row
       	      while($row = $result->fetch_assoc()) {
	      if($i==$length-1){
	      	   $termArray[]=$termArray[0].$backboneArray[$j]['Sequence'];
		   $j=$j+1;
	      }
	      //if the next postion is a new plasmid add a backbone sequence
	      else if($full[$i+1]['OOP']==1){
	          $termArray[]=$row['Sequence'].$backboneArray[$j]['Sequence'];
		  $j=$j+1;
						    
	       }
	      else{
	          $termArray[]=$row['Sequence'];
	       }
	       	  $nameTerm[]=$row['CommonName'];

                                    }
				                                               }
									       else {                                                                                                                      echo "0 results";																							                                                                                }

										}

//need two indexs (x,b) one for the geneId's and one for the resitant id's
$x=0;
$b=0;
$len=strlen($geneArray[0]);
$geneArray[0]=substr($geneArray[0],0,len-50);
foreach($geneArray as $value){

	        echo $nameProm[$x]."  ".$nameTerm[$x]."  ".$resistArray[$b]."<br>";    
                echo ">".$nameArray[$x]."<br>";
                    echo $promArray[$x]['Sequence'].$geneArray[$x]."<br>"."hello"."<br>".$termArray[$x]."<br>";
		    if($full[$x]['OOP']==2 && $full[$x+1]['OOP']==3){
                     $finalString=$finalString.">".$nameArray[$x]."\n";
		     $finalString=$finalString.$promArray[$x]['Sequence'].$geneArray[$x].$termArray[$x].$resistArray[$b]."\n";
		    
		     $b=$b+1;			  
		    } else{
 	             $finalString=$finalString.">".$nameArray[$x]."\n";
		     $finalString=$finalString.$promArray[$x]['Sequence'].$geneArray[$x].$termArray[$x]."\n";
		     }
			           $x=$x+1;
			}

//make the fasta file
$myfile = fopen("filers.fasta", "w") or die("Unable to open file!");
fwrite($myfile, $finalString);

fclose($myfile);
//close the connection to phpmyadmin
$conn->close();


													
?>
//download the file 
<button type="button" onclick="location.href='dloadsTwo.php'">Download the Fasta File</button>
