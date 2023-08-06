def parsearguments():
    epilog = """============================== Alea jacta est =============================="""
    parser = argparse.ArgumentParser(epilog=epilog,formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('INFNAME',help="Path to the xam or fastx file containing the reads")
    parser.add_argument('OUTFNAME',help="Output file name (fasta only).")

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    return(vars(parser.parse_args()))

if __name__ == "__main__":
    import argparse,sys,collections,os
    from tstk.io import openfastx,parsefastx
    from tstk.common import revcomp
    import pysam

    args = parsearguments()

    fpathnoext, fext = os.path.splitext(args["INFNAME"])

    if fext in [".bam",".sam"]:
        entries = [entry for entry in pysam.AlignmentFile(args["INFNAME"],"rb") if dict(entry.get_tags())["HI"] == 1]# only get the first entry in case of multi-mappers
        entries = [revcomp(str(e.seq)) if e.is_reverse else str(e.seq) for e in entries]
        counter = collections.Counter(entries) #only include one hit from the multi mappers
    else:
        fpathnoext,fext,ftype,fh = openfastx(args["INFNAME"])
        seqs = [str(seq) for name,seq,qual in parsefastx(fh)]
        counter = collections.Counter(seqs)
        fh.close()

    ofpathnoext,ofext,oftype,ofh = openfastx(args["OUTFNAME"].replace("fastq","fasta"),mode='wt')

    seqid = 1
    for seq in counter.most_common():
        ofh.write(">{}-{}\n{}\n".format(seqid,seq[1],seq[0]))
        seqid += 1

    ofh.close()
