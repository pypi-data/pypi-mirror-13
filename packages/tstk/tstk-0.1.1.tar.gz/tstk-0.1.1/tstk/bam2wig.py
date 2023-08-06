import pysam
import subprocess
from contextlib import contextmanager, closing

def parsearguments():
    epilog = """============================== Alea jacta est =============================="""
    parser = argparse.ArgumentParser(epilog=epilog,formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('BAMFILE',help="BAM file containing the reads")
    parser.add_argument('OUTFILE',help="Output file (wig)")
    parser.add_argument('--chrom',help="Limit the processing to a specific chromosome",default="all")
    parser.add_argument('--strand',help="Limit the processing to a specific strand",choices=["fw","rv"])
    parser.add_argument('--rpm', help="Write counts as reads per million", action="store_true")
    parser.add_argument('--neg', help="Negate counts", action="store_true")

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    return(vars(parser.parse_args()))

@contextmanager
def indexed_bam(bam_file):
    if not os.path.exists(bam_file + ".bai"):
        pysam.index(bam_file)
    bam = pysam.AlignmentFile(bam_file)
    yield bam
    bam.close()

def main(bam_file, outfile, chrom='all', start=0, end=None, rpm=False,strand=None):
    if start > 0:
        start = int(start) - 1
    if end is not None:
        end = int(end)
    regions = [(chrom, start, end)]

    if strand:
        n,x = os.path.splitext(outfile)
        outfile = "{}.{}{}".format(n,strand,x)

    out_handle = open(outfile, "w")
    with closing(out_handle):
        chr_sizes = write_bam_track(bam_file, regions, out_handle, rpm, strand)
    convert_to_bigwig(outfile, chr_sizes)

def write_bam_track(bam_file, regions, out_handle, rpm, strand=None):
    out_handle.write("track {}\n".format(" ".join(["type=wiggle_0", "name={}{}".format(os.path.splitext(os.path.split(bam_file)[-1])[0],"_"+strand if strand else ""), "visibility=full", ])))
    with indexed_bam(bam_file) as work_bam:
        if strand:
            if strand == "fw":
                goodstrand = lambda r: not r.is_reverse
            elif strand == "rv":
                goodstrand = lambda r: r.is_reverse
            else:
                raise ValueError("Bad strand value {}".format(strand))
        else:
            goodstrand = lambda r: True

        total = sum(1.0 / dict(r.get_tags())["NH"] for r in work_bam.fetch() if not r.is_unmapped) if rpm else None
        sizes = list(zip(work_bam.references, work_bam.lengths))
        if len(regions) == 1 and regions[0][0] == "all":
            regions = [(name, 0, length) for name, length in sizes]
        for chrom, start, end in regions:
            if end is None and chrom in work_bam.references:
                end = work_bam.lengths[work_bam.references.index(chrom)]
            assert end is not None, "Could not find {} in header".format(chrom)
            out_handle.write("variableStep chrom={}\n".format(chrom))
            for col in work_bam.pileup(chrom, start, end):
                n = sum(1.0 / dict(r.alignment.get_tags())["NH"] for r in col.pileups if goodstrand(r.alignment)) 
                if rpm:
                    n = float(n) / total * 1e6
                if args["neg"]:
                    n *= -1
                out_handle.write("%s %.1f\n" % (col.pos+1, n))

    return sizes

def convert_to_bigwig(wig_file, chr_sizes):
    bw_file = "{}.bw".format(os.path.splitext(wig_file)[0])
    size_file = "{}.sizes.txt".format(os.path.splitext(wig_file)[0])
    with open(size_file, "w") as out_handle:
        for chrom, size in chr_sizes:
            out_handle.write("%s\t%s\n" % (chrom, size))
    try:
        import shlex
        s = subprocess.Popen(shlex.split("wigToBigWig {} {} {}".format(wig_file,size_file,bw_file)),stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        s.communicate()
    finally:
        os.remove(size_file)
    return bw_file

if __name__ == "__main__":
    import argparse,sys,os

    args = parsearguments()

    main(args["BAMFILE"],args["OUTFILE"],chrom=args["chrom"],rpm=args["rpm"],strand=args["strand"])
