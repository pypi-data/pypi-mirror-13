#!/usr/bin/perl -w
## Raquel Norel (rnorel@us.ibm.com) 06/2014

#validate format of predictions for DREAM9 AML  Challenge (Q2)
#not using gold standard here, hardcode or build needed info

use strict;

## ##################################################
##PARAMETERS
my $DATA_POINTS = 100;  # number of patients
my $Max_OS = 600;
my $Ncols = 3; #ID + OS (weeks) + confidence
my @header = ('#Patient_id','Remission_Duration','Confidence');  #just in case, since values for different columns are quite different
## ##################################################

##MAIN
## command line arguments
if (@ARGV != 1) {
    print "\nUSAGE: perl $0  <file to validate>  \n\n";
    print "Format validation for DREAM9 AML challenge\n";
    print "example: perl $0  my_prediction.csv\n";
    exit;
}

#prediction file
my $file = $ARGV[0];
#print STDERR "reading $file\n";


my $ref_ids = generate_ids($DATA_POINTS,'id_'); #number of patients and name of variable
my %ids = %$ref_ids;


#check that file name ends in csv ###not checking file name as requested by Byron
#if ($file  !~ /\.csv$/)  {print "NOT_OK\nThe prediction file has to be a csv file. Please see the template file and resubmit.\n";exit;}

my $lines;
{
     open my $fh, "<", $file or die $!;
    local $/; # enable localized slurp mode
     $lines = <$fh>;
    close $fh;
}

my @all = split(/[\r\n]+/,$lines);  #Mac, Unix and DOS files
my $valid_data_lines=0; #how many valid data lines have been seen
my $check_header_flag=0;
my $errors = ''; #keep all errors to be reported to user
#while (<IN>) {
my $ln=1; 
foreach (@all){
#print STDERR "processing $_";

         my $line = $_;
	if ($line =~ /^\s*$/) {next;}	## skip blank lines
	$line =~ s/\s//g; #remove spaces
	#need to check for columns number before other check to avoid warning if less columns than expected
	my @tmp = split (",", $line); #separating line by comma, separate only once for all the tests
	my $n_cols = scalar @tmp; #number of columns
	if (!check_column_number($n_cols,$ln)){last;} #correct number of columns?	
	if (/^#/) {   ## check header, assume is 1st line
	    $check_header_flag++ ; #header detected
	    for (my $i=0; $i< scalar(@header); $i++){
		if ($tmp[$i] ne $header[$i]) {
		    $errors .= "\n".'ERROR in the header ';
		    my $tmpi = $i + 1;
		    $errors .= "Column $tmpi is $tmp[$i] and should be $header[$i]. Error at input line # $ln.\n";
		    last;
		}
	    }
	}
        else{
	    if (!check_format_col1($tmp[0],$ln)){last;} #correct format of col 1  
	    if (!check_format_os($tmp[1],$ln)){last;} #correct format of predicted time
	    if (!check_format_conf($tmp[2],$ln)){last;} #correct format of confidence
	    $valid_data_lines++;
	}
	$ln++;
}

if ($check_header_flag != 1) { $errors .=  "Warning: We didn't detect the correct header in the prediction file.\n";}
#error reporting

     if (($errors eq '' ) && ($valid_data_lines == $DATA_POINTS)) {print "OK\nValid data file\n";} #all good; still need to check for header count
     elsif (($errors eq '' ) && ($valid_data_lines < $DATA_POINTS)){
	check_missing(); #only check for missing prediction if no other errors are found, since quiting at 1st error
	print "NOT_OK\nYou have the following error(s): $errors\n";
	print "Please see the template file and  resubmit the updated file.\n";
     } 
    else {
              
	      print "NOT_OK\nYou have the following error(s): $errors\n";
	      print "Please see the template file and resubmit the updated file.\n";
	}

###########subroutines##############

#since I don;t read the gold standard, I need to generate the expected full set if IDs on the prediction file, to check against it
sub generate_ids{
    my ($num, $string) = @_;
    my %ids = ();
    for (my $i=1; $i <= $num; $i++){
	if ($i<10){
	    $string = 'id_00'.$i;
	}
	elsif ($i<100){
	    $string = 'id_0'.$i;
	}
	else{
	    $string = 'id_'.$i;
	}
	$ids{$string}=0; #flag the existence of ID
    }
    return(\%ids);
}


#check that the number of columns per line is ok
sub check_column_number{
  my ($n_cols, $ln) = @_;
	if ($n_cols != $Ncols) {
	   $errors .=  "Please note that the numbers of expected columns is $Ncols not $n_cols. Error at input line # $ln.\n";
	   return(0);#failed test
	}
	return(1); #test ok
  
}

sub check_format_col1{ # checking the ID has not been used twice, and the name is correct
  my ($id,$ln) = @_;
  my $flag =1; #so far so good
  
  if (!defined($ids{$id})) { $errors .= "$id is not a valid ID .Error at input line # $ln.\n"; return(0);} #failed test
  if($ids{$id} == 0){$ids{$id}++;}
  else {$errors .= "$id is a  duplicated entry. Error at input line # $ln.\n"; return(0);};  #failed test
   return(1);
}


 sub check_format_os{ #is numeric? is it positive? < Max_OS?
  my ($val,$ln) = @_;
  #if (( $val =~ /^([+-]?)(?=\d|\.\d)\d*(\.\d*)?([Ee]([+-]?\d+))?$/) && ($val >= 0) && ($val <= $Max_OS)){
if (( $val =~ /^([+]?)(?=\d|\.\d)\d*(\.\d*)?([Ee]([+-]?\d+))?$/) && ($val <= $Max_OS)){#for to be positive
       return(1);
   } #test ok;
   #test failed 
  $errors .= "Overall Survival  must be a positive float number, less or equal to $Max_OS. Got $val, which is incorrect.\nError at input line # $ln.\n";
   return(0);#failed test  
}

 sub check_format_conf{ #is numeric? is it positive?
  my ($val,$ln) = @_;
 # if (( $val =~ /^([+-]?)(?=\d|\.\d)\d*(\.\d*)?([Ee]([+-]?\d+))?$/) && ($val >= 0) && ($val <= 1) || ($val == 1) || ($val==0)){
  if (( $val =~ /^([+]?)(?=\d|\.\d)\d*(\.\d*)?([Ee]([+-]?\d+))?$/) && ($val <= 1) || ($val == 1) || ($val==0)){ #force to be positive
       return(1);
   } #test ok;
   #test failed 
  $errors .= "Confidence must be a positive float number, less or equal to 1. Got $val, which is incorrect.\nError at input line # $ln.\n";
   return(0);#failed test  
}
 
#check patients with no prediction in file, to report 
sub check_missing{
     foreach my $k (sort keys %ids){
	if (! $ids{$k}){ $errors .= "Missing prediction for subject $k\n";}
     }
  return(1);
}