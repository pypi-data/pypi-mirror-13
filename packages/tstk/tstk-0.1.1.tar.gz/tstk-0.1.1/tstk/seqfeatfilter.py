def parsearguments():
    epilog = """============================== Alea jacta est =============================="""
    parser = argparse.ArgumentParser(epilog=epilog,formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('INFNAME',help="Path to the SAM/BAM/fastq/fasta file containing the reads")
    parser.add_argument('OUTFNAME',help="Output file name.")
    parser.add_argument('--lengths',type=int,metavar='N',help="Sequence lengths to extract",nargs='*')
    parser.add_argument('--reqnts',type=str,metavar='XN',help="Required nucleotides at a certain positions. For a T in position 10, pass 10T",nargs="*")
    parser.add_argument('--nmaps', help="Maximum number of multi maps", type=int, default=1)
    parser.add_argument('--nmism', help="Maximum number of mismatches", type=int, default=0)

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    return(vars(parser.parse_args()))

def checkreqnts(record,reqnts):
    if reqnts:
        seq = Seq(str(record.seq))
        try:
            if record.is_reverse:
                seq = seq.reverse_complement()
        except AttributeError:
            pass #it's not a xam file
        for nt in reqnts:
            if str(seq)[nt[1]-1] != nt[0]:
                return False
    return True

def isxam(fext):
    return fext in [".bam",".sam"]

def filteralignments(alignments,lengths=None,reqnts=None,nmism=0,nmaps=1):
    for aln in alignments:
        if (not lengths or len(aln.seq) in lengths) and checkreqnts(aln,reqnts):
            tags = dict(aln.get_tags())
            if tags["nM"] <= nmism and tags["NH"] <= nmaps:
                    yield aln

def parsereqnts(reqnts):
    try:
        reqnts = [[nt[-1],int(nt[0:-1])] for nt in args["reqnts"]]
    except TypeError:
        reqnts = []

    return reqnts

if __name__ == "__main__":
    import argparse,sys,os
    from common import *
    from tstk.io import openfastx
    import gzip
    import pysam
    from Bio import SeqIO
    from Bio.Seq import Seq
    from Bio.SeqRecord import SeqRecord

    args = parsearguments()

    lengths = args["lengths"]
    reqnts = parsereqnts(args["reqnts"])
    reqpos = [i[1] for i in reqnts]

    if reqpos and lengths and max(reqpos) > max(lengths):
        print("WARNING: some of your fixed positions fall beyond the maximum requested length")

    ifpathnoext, ifext = os.path.splitext(args["INFNAME"])
    ofpathnoext, ofext = os.path.splitext(args["OUTFNAME"])

    if not isxam(ifext) and isxam(ofext):
        raise TypeError("ERROR: cannot output BAM from a FASTX input")

    if isxam(ifext):
        infile = pysam.AlignmentFile(args["INFNAME"])

        if isxam(ofext):
            outfile = pysam.AlignmentFile(args["OUTFNAME"], mode="wb", template=infile)
            for aln in filteralignments(infile,lengths,reqnts,args["nmism"],args["nmaps"]):
                outfile.write(aln)
        else:
            ofpathnoext,ofext,oftype,ofh = openfastx(args["OUTFNAME"],mode="wt")
            for aln in filteralignments(infile,lengths,reqnts,args["nmism"],args["nmaps"]):
                seq = Seq(aln.seq)
                seq.name = seq.id = seq.description = aln.query_name
                if aln.is_reverse:
                    seq = seq.reverse_complement()
                record = SeqRecord(seq,id=aln.query_name,description="")
                SeqIO.write(record,ofh,oftype)

            ofh.close()
    else:
        fpathnoext,fext,ftype,fh = openfastx(args["INFNAME"])
        infile = SeqIO.parse(fh,ftype)

        ofpathnoext,ofext,oftype,ofh = openfastx(args["OUTFNAME"],mode="wt")

        for record in SeqIO.parse(fh,ftype):
            if (not lengths or len(record.seq) in lengths) and checkreqnts(record,reqnts):
                SeqIO.write(record,ofh,ftype)
        fh.close()
        ofh.close()
