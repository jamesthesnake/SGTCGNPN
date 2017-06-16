from Bio import SeqIO
count = SeqIO.convert("KU42.gb", "genbank", "cor6_7.fasta", "fasta")
print("Converted %i records" % count)
