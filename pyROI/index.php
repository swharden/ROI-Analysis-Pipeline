<html>
<head>
<style>
body{
    background-color: #E0E0E0;
    padding: 50px;
}
.sliceTitle{
    font-size: 300%; 
    font-weight: bold; 
    background-color: #003366; 
    color: white; 
    padding: 20px;
}
.slice{
    border: 2px solid black;
    margin-top: 50px;
}
.sliceBody{
    background-color: white;
    padding: 20px;
}
.section{
    font-size: 150%; 
    font-weight: bold;
    margin-top: 2em;
}
</style>
</head>
<body>
<?php

function tiff_convert_folder($folder, $putInSubFolder="/swhlab/"){
    // given a folder with a bunch of TIF files, use python to make them JPGs.

    if (!file_exists($folder)) return;

    $folder_output=$folder.$putInSubFolder;
    if (!file_exists($folder_output)) mkdir($folder_output);

    $files = scandir($folder);
    $files2 = scandir($folder_output);
    $tifs_to_convert=[];
    foreach ($files as $fname){
        $extension=strtolower(pathinfo($fname, PATHINFO_EXTENSION));
        if ($extension == "tif" || $extension == "tiff") {
            if (!in_array($fname.".jpg",$files2)){
                $tifs_to_convert[]=$fname;
            }
        }
        
    }

    foreach ($tifs_to_convert as $tifFile){
        $fileIn=$folder."/".$tifFile;
        $fileOut=$folder_output.$tifFile.".png";
        if (file_exists($fileOut)) continue;
        $cmd="convert \"$fileIn\" -contrast-stretch 0.15x0.05% \"$fileOut\"";
        echo "<div style='font-family: monospace;'>$cmd</div>";
        exec($cmd);       
        flush();ob_flush();
    }
    
}


$folders=scandir('./');
sort($folders);
foreach($folders as $folder){
    if (!is_dir($folder."/video/")) continue;
    $fullPath=str_replace('D:\X_Drive','X:',realpath($folder));
    $fldrName=basename($fullPath);
    $subtitle="<a href='#$fldrName' style='font-size: 50%; font-weight: normal; font-family: monospace; color: white;'>$fullPath\\</a>";
    echo "<a id='$fldrName'></a>";
    echo "<div class='slice'>";
    echo "<div class='sliceTitle'>$folder<br>$subtitle</div>";
    echo "<div class='sliceBody'>";

    tiff_convert_folder($folder);
    
    if (is_file($folder."/experiment.txt")){
        echo "<div class='section'>experiment.txt</div>";
        echo "<table style='background-color: EEE; font-size: 150%;'><tr><td><pre>";
        include($folder."/experiment.txt");
        echo "</pre></td></tr></table>";
    }
    
    foreach (scandir($folder) as $fname){
        if (strstr($fname,".mp4")){
            echo "<div class='section'>$fname</div>";
            echo "<video style='border: 1px solid black; margin: 10px;' width='696' height='520' controls><source src='$folder/$fname' type='video/mp4'></video><br>";
        }
    }
    /*
    if (is_file($folder."/video.mp4")){
        echo "<div class='section'>Video:</div>";
        echo "<video width='696' height='520' controls><source src='$folder/video.mp4' type='video/mp4'></video><br>";
        
    }
    if (is_file($folder."/render2.mp4")){
        echo "<div class='section'>Video with Analysis:</div>";
        echo "<video width='696' height='520' controls><source src='$folder/render2.mp4' type='video/mp4'></video><br>";
        
    }*/
    echo "<div class='section'>Images:</div>";

    // everything in root folder
    foreach (scandir($folder) as $fname){
        if (!(strpos($fname,".png") || strpos($fname,".jpg"))) continue;
        $url="$folder/$fname";
        echo "<a target='_blank' href='$url'><img style='border: 1px solid black; margin: 10px;' src='$url' height='300'></a> ";
    }

    // everything in SWHLab folder
    foreach (scandir($folder."/swhlab") as $fname){
        if (!(strpos($fname,".png") || strpos($fname,".jpg"))) continue;
        $url="$folder/swhlab/$fname";
        echo "<a target='_blank' href='$url'><img style='border: 1px solid black; margin: 10px;' src='$url' height='300'></a> ";
    }

    echo "</div>";
    echo "</div>";
}

?>
</body>
</html>