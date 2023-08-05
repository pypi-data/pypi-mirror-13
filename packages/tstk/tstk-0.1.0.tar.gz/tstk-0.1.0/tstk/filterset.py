from tstk.io import openfastx
import gzip,sys,os
from Bio import SeqIO
from Bio.Seq import Seq

def getfiltseqs(fname):
    fpathnoext, fext = os.path.splitext(fname)
    if fext in [".bam",".sam"]:
        filt_seqs = [(record.query_name,str(record.seq)) for record in openxam(fname)]
    else:
        fpathnoext,fext,ftype,fh = openfastx(fname)
        filt_seqs = [(record.id,str(record.seq)) for record in SeqIO.parse(fh,ftype)]

    return(set(filt_seqs))

def gettargetseqs(fname):
    fpathnoext, fext = os.path.splitext(fname)
    if fext in [".bam",".sam"]:
        return openxam(fname,"r")
    else:
        fpathnoext,fext,ftype,fh = openfastx(fname)
        return SeqIO.parse(fh,ftype)

    return(set(filt_seqs))

def parsearguments():
    import argparse
    epilog = """============================== Alea jacta est =============================="""
    parser = argparse.ArgumentParser(epilog=epilog,formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('TARGETS',help="Path to the SAM/BAM/fastq/fasta file containing target sequences")
    parser.add_argument('FILTERS',help="Path to the SAM/BAM/fastq/fasta file containing filtering reads")
    parser.add_argument('OUTFNAME',help="Output file name.")
    parser.add_argument('--3ponly',help="Don't get sequences that have a 5' overhang",action="store_true")
    parser.add_argument('--output_filters',help="Output a file containing the matched filters",action="store_true",default=True)
    parser.add_argument('--output_targets',help="Output a file containing the matched targets",action="store_true")

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    return(vars(parser.parse_args()))

def filter_boyer(filter_seq,target_seqs,target_seqs_flat,target_seqs_flat_divs,only3p):
    import bisect

    matched_target_seqs = []
    matched_target_ids = []
    i = target_seqs_flat.find(filter_seq)
    while i != -1:
        p = bisect.bisect_right(target_seqs_flat_divs, i) - 1
        matched_target_seq = target_seqs[p]
        if not only3p or matched_target_seq[1].find(filter_seq) == 0:
            matched_target_seqs.append(matched_target_seq)
        i = target_seqs_flat.find(filter_seq, target_seqs_flat_divs[p] + len(matched_target_seq[1]))

    return matched_target_seqs

def filterseqs(target_seqs,filter_seqs,only3p=False):
    import re

    matched_target_seqs = []
    matched_target_ids=[]
    matching_filter_seqs = []

    target_seqs_flat = "#"+"#".join([s[1] for s in target_seqs]) 
    target_seqs_flat_divs = [m.start()+1 for m in re.finditer('#', target_seqs_flat)]

    nfilts = len(filter_seqs)
    for i,fs in enumerate(filter_seqs):
        m = filter_boyer(fs[1],target_seqs,target_seqs_flat,target_seqs_flat_divs,only3p) 
        matched_target_seqs += m
        if len(m) > 0:
            matching_filter_seqs.append(fs)

    return(set(matched_target_seqs),matching_filter_seqs)

def filterseqs_from_files(ftargets,ffilters):

    target_seqs = []

    for record in gettargetseqs(ftargets):
        try:
            seq = Seq(record.seq)
            if record.is_reverse:
                seq = seq.reverse_complement()
            target_seqs.append((record.query_name,str(seq)))
        except TypeError:
            seq = str(record.seq)
            target_seqs.append((record.id,str(seq)))

    filter_seqs = getfiltseqs(ffilters)

    return filterseqs(target_seqs,filter_seqs)

if __name__ == "__main__":
    args = parsearguments()

    if not args["OUTFNAME"].endswith(".fasta"):
        args["OUTFNAME"] += ".fasta"

    matched_target_seqs,matching_filter_seqs = filterseqs_from_files(args["TARGETS"],args["FILTERS"])

    if args["output_targets"]:
        ofpathnoext,ofext,oftype,ofh = openfastx("targets_" + args["OUTFNAME"],mode="wt")
        for id,seq in matched_target_seqs:
           ofh.write(">{}\n{}\n".format(id,seq))
        ofh.close()

    if args["output_filters"]:
        ofpathnoext,ofext,oftype,ofh = openfastx("filters_" + args["OUTFNAME"],mode="wt")
        for id,seq in matching_filter_seqs:
           ofh.write(">{}\n{}\n".format(id,seq))
        ofh.close()
