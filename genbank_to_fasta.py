#!/usr/bin/env python

# Convert gb file to fasta file, write dna sequence, as not all genbank files
# have predicted protein sequences.

from Bio import SeqIO
import glob
import sys

gbfilenames = glob.glob("*.gb")
for gbfilename in gbfilenames:
    print gbfilename
    f = open(gbfilename, 'r')
    gbid = gbfilename.split(".gb")[0]
    dseqfile = gbid + ".fasta"
    fd = open(dseqfile, "w")
    fstatfile = gbid + "_stat.txt"
    fstat = open(fstatfile, "w")
    data = f.read()
    fd.write(">%s" % gbid)
    fd.write("\n")
                
    for record in SeqIO.parse(open(gbfilename, "rU"), "genbank"):
        print record.name
    
        sequence = record.seq
        fd.write(str(sequence))
        fd.write("\n")
        for feature in record.features:
            coord1 = str(feature.location)
            coord = coord1.split("(")[0]
            print feature
            print coord, feature.type, 
            fstat.write("%s\t%s\t%s\n" % (coord, feature.type,coord1))

    fd.close()
    fstat.close()
