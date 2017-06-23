# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 18:56:17 2016

@author: kevinroy
"""
import os
import zipfile
import gzip
import shutil
import tarfile


import commands
import cgi, cgitb

import os
import posixpath
import BaseHTTPServer
import urllib
import cgi
import shutil
import mimetypes
import re
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
cgitb.enable()
print "Content-Type: text/html"
print
print 'start!'
form = cgi.FieldStorage()
#filedata = form['upload']
cwd=os.getcwd()
RUN_NAME='RptPMP3_screen_SEC14_FPR1_editing_windows'
DIR= cwd+"/Files/"
print DIR
SAMPLE_NAME='RptPMP3-screen-yL_S1_L001'
read1_fastq = DIR+'header_read1.fastq'
read2_fastq = DIR+'header_read2.fastq'
BARCODE_PREFIX_LENGTH = 11

## PROBLEM WITH READ2 WILL FORCE NEEDING TO DEAL WITH N's in barcodes!!!

BARCODE_FILENAME=  filedata.read()
ALLOWABLE_BARCODE_EDIT_DISTANCE = 2

def generate_variants_one_edit_distance_away(sequences):
    close_variants = set([])
    for seq in sequences:
        seq_list = list(seq)
        for idx in range(len(seq_list)):
            base = seq_list[idx]
            for other_base in 'ACTG':
                new_seq_list = seq_list[:]
                if base != other_base:
                    new_seq_list[idx] = other_base
                    close_variants.add( ''.join(new_seq_list) )
## uncomment below code to allow for single bp deletions to count as one edit distance
#                new_seq_list = seq_list[:]
#                new_seq_list.insert(idx, other_base)
#                close_variants.add( ''.join(new_seq_list) )
#            new_seq_list = seq_list[:]
#            new_seq_list[idx] = ''
#            close_variants.add( ''.join(new_seq_list) )
    return close_variants
    
## initialize barcode lengths
max_read_1_bc_length = 0
min_read_1_bc_length = 100

max_read_2_bc_length = 0
min_read_2_bc_length = 100

category_to_sample_name = {}


with open(DIR + BARCODE_FILENAME, 'r') as infile:
    sample_name_to_read_1_barcode_close_matches = {}
    sample_name_to_read_2_barcode_close_matches = {}
    sample_name_to_read_1_outfile = {}
    sample_name_to_read_2_outfile = {}
    sample_name_to_num_reads = {}
    sample_name_to_category_and_desired_category_percentage = {}
    header = True
    for line in infile:
        if header == False:
            read1_bc, read2_bc, sample_name, category, desired_category_percentage = line.strip().split()
            read1_bc = read1_bc.upper()[:BARCODE_PREFIX_LENGTH]
            read2_bc = read2_bc.upper()[:BARCODE_PREFIX_LENGTH]
            print(line.strip().split())
            desired_category_percentage = float(desired_category_percentage)
            if len(read1_bc) > max_read_1_bc_length:
                max_read_1_bc_length = len(read1_bc)
                
            if len(read2_bc) > max_read_2_bc_length:
                max_read_2_bc_length = len(read2_bc)
                
            if len(read1_bc) < min_read_1_bc_length:
                min_read_1_bc_length = len(read1_bc)
                
            if len(read2_bc) < min_read_2_bc_length:
                min_read_2_bc_length = len(read2_bc)
             
            sample_name_to_num_reads[sample_name] = 0
            sample_name_to_category_and_desired_category_percentage[sample_name] = category, desired_category_percentage
            if category not in category_to_sample_name:
                category_to_sample_name[category] = [sample_name]
            else:
                category_to_sample_name[category] += [sample_name]
            
            sample_name_to_read_1_outfile[sample_name] = open(DIR + sample_name + '_R1.fastq', 'w')
            sample_name_to_read_2_outfile[sample_name] = open(DIR + sample_name + '_R2.fastq', 'w')
            
            sample_name_to_read_1_barcode_close_matches[sample_name] = {}
            sample_name_to_read_2_barcode_close_matches[sample_name] = {}
    
            sample_name_to_read_1_barcode_close_matches[sample_name][0] = [read1_bc]
            sample_name_to_read_2_barcode_close_matches[sample_name][0] = [read2_bc]
            for idx in range(1, ALLOWABLE_BARCODE_EDIT_DISTANCE + 1):
                print('processing edit distance ', idx, 'for sample', sample_name)
                sequences = sample_name_to_read_1_barcode_close_matches[sample_name][idx - 1]
                sample_name_to_read_1_barcode_close_matches[sample_name][idx] = generate_variants_one_edit_distance_away(sequences)
                sequences = sample_name_to_read_2_barcode_close_matches[sample_name][idx - 1]
                sample_name_to_read_2_barcode_close_matches[sample_name][idx] = generate_variants_one_edit_distance_away(sequences)
        header = False
    # print(sample_name_to_read_1_barcode_close_matches)

## verify whether all barcodes are at least ALLOWABLE_BARCODE_EDIT_DISTANCE away from each other

sample_to_samples_with_identical_read_1_barcodes = {}

for sample_name in sample_name_to_read_1_barcode_close_matches:
    sample_to_samples_with_identical_read_1_barcodes[sample_name] = []
    for other_sample_name in sample_name_to_read_1_barcode_close_matches:
        if sample_name != other_sample_name:
            
            ## next(iter(s)) allows extracting 
            sample_bc = sample_name_to_read_1_barcode_close_matches[sample_name][0][0]
            other_sample_bc = sample_name_to_read_1_barcode_close_matches[other_sample_name][0][0]
            if sample_bc == other_sample_bc:
                sample_to_samples_with_identical_read_1_barcodes[sample_name].append(other_sample_name)
            
sample_to_samples_with_identical_read_2_barcodes = {}

for sample_name in sample_name_to_read_2_barcode_close_matches:
    sample_to_samples_with_identical_read_2_barcodes[sample_name] = []
    for other_sample_name in sample_name_to_read_2_barcode_close_matches:
        if sample_name != other_sample_name:
            ## next(iter(s)) allows extracting 
            sample_bc = sample_name_to_read_2_barcode_close_matches[sample_name][0][0]
            other_sample_bc = sample_name_to_read_2_barcode_close_matches[other_sample_name][0][0]
            if sample_bc == other_sample_bc:
                sample_to_samples_with_identical_read_2_barcodes[sample_name].append(other_sample_name)
    if other_sample_name == 'yL8_plasmid_prep' and sample_name == 'Justin_16':
        print(sample_bc, other_sample_bc)

edit_distances_to_read_1_seqs_to_sample_name = {}
edit_distances_to_read_2_seqs_to_sample_name = {}


for idx in range(ALLOWABLE_BARCODE_EDIT_DISTANCE + 1):
    edit_distances_to_read_1_seqs_to_sample_name[idx] = {}
    edit_distances_to_read_2_seqs_to_sample_name[idx] = {}
    for sample_name in sample_name_to_read_1_barcode_close_matches:
        for seq in sample_name_to_read_1_barcode_close_matches[sample_name][idx]:
            if seq in edit_distances_to_read_1_seqs_to_sample_name[idx]:
#                other_samples = edit_distances_to_read_1_seqs_to_sample_name[idx][seq]
#                for other_sample in other_samples:
#                    if other_sample not in sample_to_samples_with_identical_read_1_barcodes[sample_name]: ## identify unintended barcode clashes
#                        
#                        print(str(idx) + ' edit distance read 1 barcode clash for ', other_sample, 'with ', sample_name, ' for sequence', seq)
                edit_distances_to_read_1_seqs_to_sample_name[idx][seq].append(sample_name)
            else:
                edit_distances_to_read_1_seqs_to_sample_name[idx][seq] = [sample_name]
                
    for sample_name in sample_name_to_read_2_barcode_close_matches:
        for seq in sample_name_to_read_2_barcode_close_matches[sample_name][idx]:
            if seq in edit_distances_to_read_2_seqs_to_sample_name[idx]:
#                other_samples = edit_distances_to_read_2_seqs_to_sample_name[idx][seq]
#                for other_sample in other_samples:
#
#                    if other_sample not in sample_to_samples_with_identical_read_2_barcodes[sample_name]: ## identify unintended barcode clashes
#                        
#                        print(str(idx) + ' edit distance read 2 barcode clash for ', other_sample, 'with ', sample_name, ' for sequence', seq)
#                other_sample = edit_distances_to_read_2_seqs_to_sample_name[idx][seq]
#                print(str(idx) + ' edit distance barcode clash for ', other_sample, 'with ', sample_name, ' for sequence', seq)
                edit_distances_to_read_2_seqs_to_sample_name[idx][seq].append(sample_name)
            else:
                edit_distances_to_read_2_seqs_to_sample_name[idx][seq] = [sample_name]
     

def process_paird_end_fastq():
    with open(read1_fastq) as textfile1, open(read2_fastq) as textfile2: 
        unmapped_read_1_fastq = open(DIR + 'no_barcode_match_R1.fastq', 'w')
        unmapped_read_2_fastq = open(DIR + 'no_barcode_match_R2.fastq', 'w')

        current_read_1_info = []
        current_read_2_info = []
        read_1_barcode_match = False
        read_2_barcode_match = False
        line_in_read = 0
        sample_found = False
        reads_processed = 0
        reads_matched_to_sample_barcode = 0
        reads_not_matched_to_sample_barcode = 0
        current_best_score = ALLOWABLE_BARCODE_EDIT_DISTANCE*2 + 1
        for x, y in zip(textfile1, textfile2):
            if reads_processed % 10000 == 0 and line_in_read == 0:
                print(reads_processed, 'reads_processed')
                print(reads_matched_to_sample_barcode, 'reads_matched_to_sample_barcode')
                print(reads_not_matched_to_sample_barcode, 'reads_not_matched_to_sample_barcode')
                print()
            #print(line_in_read, x, y)
            possible_read_1_matches = []
            possible_read_2_matches = []
            possible_read_1_matches_to_scores = {}
            possible_read_2_matches_to_scores = {}
            x = x.strip()
            y = y.strip()
            current_read_1_info.append(x)
            current_read_2_info.append(y)
            if line_in_read == 3:
                #print(x,y)
                reads_processed += 1
                if sample_found:
                    reads_matched_to_sample_barcode += 1
                    sample_name_to_num_reads[sample_name] += 1
                    for i in range(4):
                        #print(current_read_1_info)
                        sample_read_1_outfile.write(current_read_1_info[i] + '\n')
                        sample_read_2_outfile.write(current_read_2_info[i] + '\n')
                else:
                    reads_not_matched_to_sample_barcode += 1
                    for i in range(4):
                        #print(current_read_1_info)
                        unmapped_read_1_fastq.write(current_read_1_info[i] + '\n')
                        unmapped_read_2_fastq.write(current_read_2_info[i] + '\n')
                current_read_1_info = []
                current_read_2_info = []
                read_1_barcode_match = False
                read_2_barcode_match = False
                line_in_read = -1
                possible_read_1_matches = []
                possible_read_2_matches = []
                possible_read_1_matches_to_scores = {}
                possible_read_2_matches_to_scores = {}
                sample_found = False
                current_best_score = ALLOWABLE_BARCODE_EDIT_DISTANCE*2 + 1
            if line_in_read == 1:
                for edit_dist in range(ALLOWABLE_BARCODE_EDIT_DISTANCE):
                    for idx in range(max_read_1_bc_length, min_read_1_bc_length - 1, -1):
                        read1_substring = x[:idx]
                        if read1_substring in edit_distances_to_read_1_seqs_to_sample_name[edit_dist]:
                            
                            for potential_sample in edit_distances_to_read_1_seqs_to_sample_name[edit_dist][read1_substring]:
                                possible_read_1_matches.append(potential_sample)
                                possible_read_1_matches_to_scores[potential_sample] = edit_dist
                    for idx in range(max_read_2_bc_length, min_read_2_bc_length - 1, -1):
                        read2_substring = y[:idx]
                        if read2_substring in edit_distances_to_read_2_seqs_to_sample_name[edit_dist]:
                            for potential_sample in edit_distances_to_read_2_seqs_to_sample_name[edit_dist][read2_substring]:
                                possible_read_2_matches.append(potential_sample)
                                possible_read_2_matches_to_scores[potential_sample] = edit_dist
                if possible_read_1_matches != [] and possible_read_2_matches != []:
                    for potential_sample_name in possible_read_1_matches:
                        if potential_sample_name in possible_read_2_matches:
                            combined_score = possible_read_1_matches_to_scores[potential_sample_name] + possible_read_2_matches_to_scores[potential_sample_name]
                            if combined_score < current_best_score:
                                current_best_score = combined_score
                                sample_name = potential_sample_name
                                sample_read_1_outfile = sample_name_to_read_1_outfile[sample_name]
                                sample_read_2_outfile = sample_name_to_read_2_outfile[sample_name]
                                sample_found = True
                            
            
            line_in_read += 1
            
    read_tally_outfile = open(DIR + RUN_NAME + '_read_tallies.xls', 'w')
    category_to_num_reads = {}
    total_category_reads = 0
    for category in category_to_sample_name:
        reads_for_entire_category = 0
        for sample_name in category_to_sample_name[category]:
            reads_for_entire_category += sample_name_to_num_reads[sample_name]
        category_to_num_reads[category] = reads_for_entire_category
        total_category_reads += reads_for_entire_category
    header = '\t'.join(['sample name', 'number of reads', 'percent_total_reads', 'percent_barcode_matching_reads', 'category', 'reads_for_entire_category', 'desired_category_percentage', 'actual_category_percentage', 'actual_minus_desired_percentage']) + '\n'
    read_tally_outfile.write(header)
    for sample_name in sample_name_to_num_reads:
        category, desired_category_percentage = sample_name_to_category_and_desired_category_percentage[sample_name]
        category_reads = category_to_num_reads[category]
        actual_category_percentage = category_reads/float(total_category_reads) * 100
        actual_minus_desired_percentage = actual_category_percentage - desired_category_percentage
        num_reads = sample_name_to_num_reads[sample_name]
        percent_barcode_matching_reads = num_reads / float(reads_matched_to_sample_barcode ) * 100
        percent_total_reads = num_reads / float(reads_matched_to_sample_barcode + reads_not_matched_to_sample_barcode) * 100
        read_tally_outfile.write('\t'.join( [sample_name, str(num_reads), str(percent_total_reads), str(percent_barcode_matching_reads), category, str(category_reads), str(desired_category_percentage), str(actual_category_percentage), str(actual_minus_desired_percentage)] ) + '\n')        
    
    for file_object in textfile1, textfile2, unmapped_read_1_fastq, unmapped_read_2_fastq, read_tally_outfile:
        file_object.close()
            
    for sample_name in sample_name_to_read_1_outfile:
        sample_name_to_read_1_outfile[sample_name].close()
    for sample_name in sample_name_to_read_2_outfile:
        sample_name_to_read_2_outfile[sample_name].close()
        
process_paird_end_fastq()
cwd=os.getcwd()
abs_src = os.path.abspath(cwd+"/Files/")
    
for dirname, subdirs, files in os.walk(cwd+"/Files/"):
    for filename in files:
        absname = os.path.abspath(os.path.join(dirname, filename))
        arcname = absname[len(abs_src) + 1:]
                                            
        with open(abs_src+"/"+filename, 'rb') as f_in, gzip.open('file.txt.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def zip(src, dst):
    print "trie"
    zf = tarfile.open("sample.tar.gz", "w:gz")
 
    abs_src = os.path.abspath(src)
    for dirname, subdirs, files in os.walk(src):
        for filename in files:
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(abs_src) + 1:]
            print 'zipping %s as %s' % (os.path.join(dirname, filename),arcname)
            zf.add(absname,arcname)
 
    zf.close()

cwd = os.getcwd()
print cwd
zip(cwd,cwd)
