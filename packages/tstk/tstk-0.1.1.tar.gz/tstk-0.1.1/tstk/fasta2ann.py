#converts a fasta file to a simplified annotation format file or BED file. Each sequence is converted into a single entry that takes an entire "chromosome"
# SAF files are accepted by featureCounts. Useful when building custom "genomes".
from Bio import SeqIO
import sys,os

def parsearguments():
    epilog = """============================== Alea jacta est =============================="""
    parser = argparse.ArgumentParser(epilog=epilog,formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('FASTAFILE',help="Path to the fasta file containing the reads")
    parser.add_argument('OUTFNAME',help="Output file name. Should have a .bed or .saf extension.")

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    return(vars(parser.parse_args()))

if __name__ == "__main__":
    import argparse,sys,collections
    from Bio import SeqIO

    args = parsearguments()
    fname,ext = os.path.splitext(args["OUTFNAME"])

    if ext == ".saf":
        rowt = "{name}\t{chrname}\t0\t{end}\t+\n"
    elif ext == ".bed":
        rowt = "{chrname}\t0\t{end}\t{name}\t.\t+\n"
    else:
        raise ValueError("Output file extension must be either .bed or .saf")

    with open(args["OUTFNAME"],"w") as fo:
        for record in SeqIO.parse(args["FASTAFILE"],"fasta"):
            fo.write(rowt.format(chrname = record.id,end = len(record.seq)-1,name = record.id))
