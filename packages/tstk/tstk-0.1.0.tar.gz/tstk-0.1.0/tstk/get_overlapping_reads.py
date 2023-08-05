from tstk.common import *
import pysam
import sys

def parsearguments():
    import argparse

    description = """===================== Uber getter of overlapping reads ====================="""
    epilog = """============================== Alea jacta est =============================="""
    parser = argparse.ArgumentParser(description=description, epilog=epilog,formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('seqfile',help="Path to the bam file containing the reads")
    parser.add_argument('outfname',help="Output bam file name")
    parser.add_argument('--lengths',type=int,default=[21,22,23,24],metavar='N',help="Length of the + strand read",nargs="*")
    parser.add_argument('--offset',type=int,default=2,metavar='N',help="Offset of the reverse read (positive value => offset towards the forward read 3')")
    parser.add_argument('--chrname', help="Count reads for the specified 'chromosome' only (BAM exclusive)")

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    return(vars(parser.parse_args()))

def checksoutplus(read,lengths):
    return not read.is_reverse and read.alen in lengths

def checksoutminus(readp,readm,offset):
    return readm.is_reverse and read.alen == readp.alen and readp.reference_start - readm.reference_start == offset

def getchunks(l, n):
    return [l[i::n] for i in range(n)]

def processreads(seqfile,refpositions,offset):
    nreads = len(refpositions)
    res = []

    fi = pysam.AlignmentFile(seqfile)

    for i,fwpos in enumerate(refpositions):
        if __name__ == "__main__":
            sys.stderr.write("Processing read {}/{}\n".format(i+1,nreads))

        chrname = fwpos[0]
        start = fwpos[1]
        end = fwpos[2]

        reads = fi.fetch(reference=fi.getrname(chrname),start=start,end=end)

        dps = {"fw":[],"rv":[]}

        for read in reads:
            if read.alen == (end-start+1):
                if read.is_reverse:
                    if read.reference_start == start - offset:
                        dps["rv"].append(read)
                else:
                    if read.reference_start == start:
                        dps["fw"].append(read)

        if len(dps["rv"]) > 0:                
            res += dps["fw"]
            res += dps["rv"]

    fi.close()

    return(res)

def getrefpositions(seqfile,chrname,lengths):
    infile = pysam.AlignmentFile(seqfile)
    refpos = {(r.reference_id,r.reference_start,r.reference_start+r.qend-r.qstart-1) for r in infile.fetch(chrname) if checksoutplus(r,lengths)}
    infile.close()

    return refpos

def getdicerproducts(seqfile, chrname, lengths, offset):
    refpos = getrefpositions(seqfile,chrname,lengths)
    return processreads(seqfile,refpos,offset)

def main(seqfile, outfname, chrname, lengths, offset):
    infile = pysam.AlignmentFile(seqfile)
    outfile = pysam.AlignmentFile(outfname, "wb", template=infile)
    infile.close()

    for read in getdicerproducts(seqfile,chrname,lengths,offset):
        outfile.write(read)

    outfile.close()

if __name__ == "__main__":
    args = parsearguments()
    main(**args)
