
# coding: utf-8

# #  Plasmid Builder
# 
# The purpose of this notebook is to build the combined plasmid sequences based on user specified inputs.

#######  Usage python plasmid_builder.py [name of CSV file with plasmid list, no extension] [version number]
#######   Sample usage:  python plasmid_builder.py 160624_plasmid_builder 2.2

# Import the required libraries

# In[1]:

import sys
import os
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqUtils import MeltingTemp as mt
from subprocess import call
import numpy
import csv
import requests
import pandas as pd
import io
from StringIO import StringIO


# Enter the required file locations

# In[16]:

#  Get the user input

plasmid_list = sys.argv[1]
version_num = sys.argv[2]

parent_dir = "~/Google Drive/U01_assemblies_and_biomek/cluster_assemblies/{}"
plasmid_dir = "~/Google Drive/U01_assemblies_and_biomek/plasmid_files/{}"
plasmid_combined_file = "1HxcYhlqhlpO1zGXplX7EWHkztH5tl-2Ppzh9y4Ep7Y8"
plasmid_list_file = plasmid_dir.format(plasmid_list +".csv")


# Define functions to run the script

# In[17]:

def read_csv_gsheet(key,header):
    csv_name = requests.get("https://docs.google.com/spreadsheets/d/{}/export?gid=0&format=csv".format(key))
    if csv_name.status_code != 200:
        print "request failed -- bad key?"    
 
    dat = list(csv.reader(StringIO(csv_name.content)))
    
    if header:
        del dat[0]
        
    return dat

def read_csv_file(csv_file,header):
    with open(os.path.expanduser(csv_file),"rU") as f:
        plate = list(csv.reader(f,dialect="excel"))
    if header:
        del plate[0]
    return(plate)


def std_parts(parent_dir,version_num):
    global promoters
    global terminators
    global version
    global vectors
    global resists
    
    #  open the promoter, terminator, vector, and assembly version files

    promoter_file_name = parent_dir.format("standard_parts/promoter_seqs.fasta")
    with open(os.path.expanduser(promoter_file_name),"r") as f:
        promoters = SeqIO.to_dict(SeqIO.parse(f,"fasta"))
   
    terminator_file_name = parent_dir.format("standard_parts/terminator_seqs.fasta")
    with open(os.path.expanduser(terminator_file_name),"r") as f:
        terminators = SeqIO.to_dict(SeqIO.parse(f,"fasta"))

    vector_file_name = parent_dir.format("standard_parts/vector_seqs.fasta")
    with open(os.path.expanduser(vector_file_name),"r") as f:
        vectors = SeqIO.to_dict(SeqIO.parse(f,"fasta"))

    resist_file_name = parent_dir.format("standard_parts/resist_seqs.fasta")
    with open(os.path.expanduser(resist_file_name),"r") as f:
        resists = SeqIO.to_dict(SeqIO.parse(f,"fasta"))
        
    version_file_name = parent_dir.format("standard_parts/version_" + str(version_num) + ".txt")
    with open(os.path.expanduser(version_file_name),"r") as f:
        version = list(line.strip().split("\t") for line in f)

def get_cluster_seqs(parent_dir,cluster):
    #  Open the FASTA file containing the cluster sequence names

    cluster_file_name = parent_dir.format("raw_cluster_sequence_files/" + cluster + ".fasta")
    cluster_file = open(os.path.expanduser(cluster_file_name),"r")
    cluster_seqs = SeqIO.to_dict(SeqIO.parse(cluster_file,"fasta"))
    cluster_file.close()
    return cluster_seqs

def get_plasmids_combined(plasmid_combined_file):
    
    #  open and read the file containing the combined information on all plasmids
    plasmid_raw = read_csv_gsheet(plasmid_combined_file,True)
    plasmids = dict()
    
    for entry in plasmid_raw:
        this_plasmid = "{}.{}".format(entry[0],entry[1])
        if not this_plasmid in plasmids:
            plasmids[this_plasmid] = list()
            plasmids[this_plasmid].append(entry[2])
        else:
            plasmids[this_plasmid].append(entry[2])
    
    return plasmids

def get_clusters_combined(plasmid_combined_file):
    plasmid_raw = read_csv_gsheet(plasmid_combined_file,True)
   
    clusters = dict()
    
    for entry in plasmid_raw:
        this_cluster = entry[0]
        this_plasmid = "{}.{}".format(entry[0],entry[1])
        if not this_cluster in clusters:
            clusters[this_cluster] = list()
            clusters[this_cluster].append(this_plasmid)
        else:
            if not this_plasmid in clusters[this_cluster]:
                clusters[this_cluster].append(this_plasmid)
                
    return clusters

def get_gene_positions(plasmid_combined_file):
    plasmid_raw = read_csv_gsheet(plasmid_combined_file,True)
    
    positions = dict()
    
    for entry in plasmid_raw:
        positions[entry[2]] = str(entry[3])
        
    return positions

def get_reg_cassettes(version, promoters,terminators):
    cassette = dict()
    
    for entry in version:
        cassette[entry[0]] = list([str(promoters[entry[1]].seq),str(terminators[entry[2]].seq) ])
    
    return(cassette)

def build_plasmid(plasmid, positions,reg_cassettes,resists,vectors,cluster,cluster_seqs,vector,resist): 

    print str(plasmid)
    this_plasmid_seq = str()
    lplasmid = len(plasmids[plasmid])
    for gene in plasmids[plasmid]:
        this_promoter = reg_cassettes[positions[gene]][0]
        if positions[gene] == str(lplasmid):
            last=True
            this_terminator = reg_cassettes["7"][1]
        else:
            last=False
            this_terminator = reg_cassettes[positions[gene]][1]
        this_gene = str(cluster_seqs[gene].seq)
        this_plasmid_seq = this_plasmid_seq + this_promoter + this_gene + this_terminator
        if positions[gene] == "2":
            if not resist == "none":
                this_plasmid_seq = this_plasmid_seq + str(resists[resist].seq)
    
    this_vector = str(vectors[vector].seq)
    this_plasmid_seq = this_plasmid_seq + this_vector
    return this_plasmid_seq

def bulk_plasmid(parent_dir,plasmid_dir,plasmid_set,plasmid_combined_file,positions,regs,vectors,resists,version_num):
   
    for entry in plasmid_set:
        cluster = entry[0]
        plasmid = entry[1]
        this_vector = entry[2]
        this_resist = entry[3]
        cluster_seqs = get_cluster_seqs(parent_dir,cluster)
        this_plasmid = build_plasmid(plasmid, positions,regs,resists,vectors,
                                     cluster,cluster_seqs,this_vector,this_resist)
        
        plasmid_name = "pCH{}-{}".format(plasmid,version_num)
        output_file = plasmid_dir.format(plasmid_name+".fasta")
        with open(os.path.expanduser(output_file),"w") as f:
            f.write(">{}\n{}\n".format(plasmid_name,this_plasmid))


# In[18]:

std_parts(parent_dir, 2.2)
clusters = get_clusters_combined(plasmid_combined_file)
plasmids = get_plasmids_combined(plasmid_combined_file)
positions = get_gene_positions(plasmid_combined_file)
regs = get_reg_cassettes(version,promoters,terminators)
plasmid_set = read_csv_file(plasmid_list_file,True)


# In[19]:

bulk_plasmid(parent_dir,plasmid_dir,plasmid_set,plasmid_combined_file,positions,regs,vectors,resists,version_num)


# In[ ]:



