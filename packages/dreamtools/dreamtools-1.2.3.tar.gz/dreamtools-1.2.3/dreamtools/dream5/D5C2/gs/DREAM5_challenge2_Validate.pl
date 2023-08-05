#!/usr/local/bin/perl -w
#$Id: DREAM5_challenge2_Validate.pl 1569 2012-06-25 08:26:52Z cokelaer $
## Raquel Norel (rnorel@us.ibm.com) 09/10/2010

#in order to run the script on a linux machine, please replace the 1st line with:  #!/usr/bin/perl 

use strict;
use warnings;
#validate format of predictions for DREAM5 challenge 2. Better to test the format and data  validity at upload than at processing

## ##################################################
## GLOBALS

my $DATA_POINTS = 2668248; #33 transcription factors, 40526 ME probes and 40330 HK probes
my $N_TFs = 66; #number of Transcription factor IDs

## ##################################################

## command line arguments
if (@ARGV < 1) {
    die "\nUSEAGE: $0 <full path of file to validate>\n\n";
}

## this is the first command line argument, the file name to process
my $file = $ARGV[0];
#print "$file\n";

## ##################################################

open(IN,$file) || die "Can't open file $file";

## ##################################################


## while there is another input line to process
my $valid_data_lines=0; #how many valid data lines have been seen
while (<IN>) {

	chomp;
	my $line = $_;	
	## skip blank lines
	if (/^\s*$/) {
		next;
	}
	##skip header lines
	if (($line =~ /ID/) || ($line =~ /Type/)) {
		next;
	}
	
	my @tmp = split ("\t", $line); #separating line by spaces, separate only once for all the tests
    #print "validating: $line ($valid_data_lines)\n" if ($tmp[0] eq 'TF_1');
	my $n_cols = scalar @tmp; #number of columns

    print "$n_cols";
    print "$tmp[0] $tmp[1] $tmp[2]\n";
	if (!check_column_number($n_cols)){close (IN);exit;} #correct number of columns?	
	if (!check_format_col1($tmp[0])){close (IN);exit;} #correct format of cols 1 
	if (!check_format_col1_col2($tmp[0],$tmp[1])){close (IN);exit;} #correct mix of cols 1 and 2
	if (!check_format_col3($tmp[2])){close (IN);exit;} #positive float?
	$valid_data_lines++;
}
close(IN);

    if ($valid_data_lines == $DATA_POINTS) {print "Valid data file\n";}
	else {print "The number of lines in your file is incorrect. It should be $DATA_POINTS not $valid_data_lines\n";
	      print "Please, fix the format of the data before submitting.\n";
	}

###########subroutines##############

sub check_column_number{
  my ($n_cols) = @_;
	if ($n_cols != 3) {
	   print "****ERROR***\n Valid data must contain 3 columns, for example:\n";
	   print "ID ARRAY_TYPE Signal_Mean\nTF_1    ME     1.23\n";
	   print "Please, fix the format of the data before submitting.\n";
	   return(0);#failed test
	}
	return(1); #test ok
  
}

sub check_format_col1{
  my ($col1) = @_;
    if ($col1 =~ /^TF_(.*)/) {	
	    my $val = $1;
		$val += 0;
		if (($1 =~ /^\d+$/) &&(($val > 0) && ($val <= $N_TFs))) {
	     
			return(1); #test ok
		  }
	}
		
		else {
			print "****ERROR***\n Column 1 must contain TF ID, valid format is TF_n, with n between 1 and $N_TFs. For example:\n";
			print "TF_1 \n";
			print "$col1 is invalid\n";
			print "Please, fix the format of the data  before submitting.\n";
			return(0);#failed test
		}
		
}

sub check_format_col1_col2{ #already know from previous test, col1 is ok
  my ($col1,$col2) = @_;
    $col1 =~ /TF_(.*)/; 
	my $val = $1 + 0; #convert to number

    if (($col2 =~ /ME/)&& ($val < 34)) { return (1);} #test ok
	if (($col2 =~ /HK/)&& ($val > 33)) { return (1);} #test ok
     #else test failed
			print "****ERROR***\n Column 1 and Column 2 must contain TF ID and valid corresponding array type\n";
			print "TF_1 to TF_33 corresponds to  array type ME \n";
			print "TF_34 to TF_66 corresponds to  array type HK \n";
			print "$col1 with $col2  is invalid\n";
			print "Please, fix the format of the data before submitting.\n";
			return(0);#failed test
		
}

sub check_format_col3{ #is it a float? is it positive?
  my ($col3) = @_;
   if (( $col3 =~ m/^\d+.\d+$/) && ($col3 > 0)){ return (1);} #test ok;
   #test failed
   print "\n\n$col3 > 0";
   print "****ERROR***\n Column 3 must be a positive float number\n";
   print "Please, fix the format of the data before submitting.\n";
   return(0);#failed test  
}
