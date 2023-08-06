from Bio import SeqIO
from Bio.Seq import Seq
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import glob,os,math,sys,json,pysam,operator
from gtf_parsing import load_gtf_as_dataframe

#pd.options.display.mpl_style = 'default'

#TODO: add strand to the gbk and gtf processors (for plotting the subfeatures
#TODO add ability to plot subfeatures as bars under the x axis

def parsearguments():
    epilog = """============================== Alea jacta est =============================="""
    parser = argparse.ArgumentParser(epilog=epilog,formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('ALNFILES',help="Comma separated sequence of labels and bam/sam files e.g. (experiment1:exp1.bam,experiment2:exp2.sam,...)")
    parser.add_argument('FEATURESFILE',help="File from which to extract the features")
    parser.add_argument('OUTDIR',help="Output directory")
    parser.add_argument('--outprefix',help="Prefix for the output file names",default="")
    parser.add_argument('--features',help="Comma separated list of features to extract")
    parser.add_argument('--normfeat',help="Name of the subfeature to normalise all reads to")
    parser.add_argument('--normnreads',help="Normalise to the total number of aligned reads (per library)",action="store_true")
    parser.add_argument('--normvals',help="Normalisation factors (comma separated).",default=None) #TODO improve behaviour
    parser.add_argument('--stranded', help="Generate a stranded plot", action="store_true")
    parser.add_argument('--binsize', help="Bin size to use for the histogram", type=int)
    parser.add_argument('--offsetup',help="Portion of sequence to show after the feature. Accepts a number (e.g. 1000) of nts, or a length multiplier (e.g. 1.5x)",default="0")
    parser.add_argument('--offsetdown',help="Portion of sequence to show before the feature. Accepts a number (e.g. 1000) of nts, or a length multiplier (e.g. 1.5x)",default="0")
    parser.add_argument('--log', help="Generate the y axis in log scale", action="store_true")
    parser.add_argument('--mmapweight', help="Weight the reads by the number of times it maps.", action="store_true")
    parser.add_argument('--nmaps', help="Maximum number of multi maps a read can have and still be counted", type=int, default=1)
    parser.add_argument('--length', help="Restrict counted reads to this length", type=int, default=None)
    parser.add_argument('--5pnt', help="Restrict counted reads to the ones with this 5p nt", default=None)

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    return(vars(parser.parse_args()))

def processbed(fname,featnames=None):
    features = []

    with open(fname, "rU") as f:
        for r in f:
            row = r.split()
            chrname = row[0]
            start = int(row[1])
            end = int(row[2])
            name = row[3]
            strand = row[5]
            if not featnames or name in featnames:
                features.append({"strand":strand,"name":name,"chr":chrname,"start":start,"end":end,"subfeatures":[]})

    return(features)

def processgbk(fname,featnames=None):
    features = []

    records = SeqIO.parse(open(fname, "rU"), "gb")
    for record in records:
        if not featnames or (record.name in featnames or record.id in featnames):
            subfeatures = [] 
            for subfeature in record.features:
                f = {}
                f["start"] = int(subfeature.location.start)
                f["end"] = int(subfeature.location.end)
                f["label"] = subfeature.qualifiers["label"][0]
                if "color" in subfeature.qualifiers:
                    f["color"] = subfeature.qualifiers["color"][0]
                if "fwcolor" in subfeature.qualifiers:
                    f["fwcolor"] = subfeature.qualifiers["fwcolor"][0]
                if "rvcolor" in subfeature.qualifiers:
                    f["rvcolor"] = subfeature.qualifiers["rvcolor"][0]
                subfeatures.append(f)
            features.append({"name":record.name,"start":1,"end":len(record.seq),"subfeatures":subfeatures})

    return(features)

def processgtf(gtffname,feattypes=['gene','exon'],featnames=None):
    #ensembl compatible...
    genes = []
    gene = None
    df = load_gtf_as_dataframe(gtffname)
    for row in df[df["feature"].isin(feattypes)].iterrows():
        data = row[1]
        if "gene_name" not in data:
            data["gene_name"] = data["gene_id"]
        ftype = data["feature"]
        if ftype == "gene" and (not featnames or (data["gene_name"] in featnames or data["gene_id"] in featnames)):
            if gene:
                genes.append(gene)
            gene = {"name":data["gene_name"],"id":data["gene_id"],"chr":data["seqname"],"start":data["start"],"end":data["end"],"subfeatures":[]}
        elif ftype == "exon":
            if gene:
                gene["subfeatures"].append({"label":"exon" + data["exon_number"],"start":data["start"],"end":data["end"]})

    genes.append(gene) #last gene would miss the filter otherwise
                
    return(genes)

def checkfilters(r):
    length = False if args["length"] and len(r.seq) != args["length"] else True
    if r.is_reverse:
        seq = Seq(r.seq)
        seq = seq.reverse_complement()
    else:
        seq = r.seq
    nt = False if args["5pnt"] and seq[0] != args["5pnt"] else True
    try:
        mult = True if dict(r.get_tags())["NH"] <= args["nmaps"] else False
    except KeyError:
        #print("WARNING: NH tag not present. Ignoring multi-mapper restriction")
        mult = True
    return mult and length and nt

if __name__ == "__main__":
    import argparse,sys
    from common import *

    args = parsearguments()

    featsfname = args["FEATURESFILE"]
    fext = os.path.splitext(featsfname)[1]

    stranded = args["stranded"]

    if args["features"]:
        featlist = args["features"].split(",")
    else:
        featlist = None

    if fext in [".gbk",".gb",".ape"]:
        features = processgbk(featsfname,featnames=featlist)
    elif fext == ".gtf":
        features = processgtf(featsfname,featnames=featlist)
    elif fext == ".bed":
        features = processbed(featsfname,featnames=featlist)
    else:
        raise ValueError("Could not identify features file type from extension {}".format(fext))

    if features == [None]:
        print("There requested features were not found in the specified feature file")
        quit()

    for feature in features:
        reflen = feature["end"] - feature["start"]

        if "x" in args["offsetup"]:
            offsetup = int(reflen * float(args["offsetup"].replace("x","")))
        else:
            offsetup = int(args["offsetup"])

        if "x" in args["offsetdown"]:
            offsetdown = int(reflen * float(args["offsetdown"].replace("x","")))
        else:
            offsetdown = int(args["offsetdown"])

        reflen += offsetdown + offsetup

        try:
            refname = feature["name"]
        except KeyError:
            refname = feature["id"]

        try:
            chrname = feature["chr"]
        except KeyError:
            chrname = feature["name"]

        normfeat = None
        if args["normfeat"]:
            for sf in feature["subfeatures"]:
                if sf["label"] == args["normfeat"]:
                    normfeat = sf

        xps = []
        for f in args["ALNFILES"].split(","): 
            try:
                xps.append({"fname":f.split(":")[1],"label":f.split(":")[0]})
            except IndexError:
                xps.append({"fname":f,"label": os.path.basename(f)})

        nxps = len(xps)

        fheight = 14
        fwidth = 6
        if args["binsize"]:
            binsize = args["binsize"]
        else:
            binsize = reflen / 500 if reflen >= 500 else 1
        nbins = reflen/binsize
        tick_labels = range(0,reflen,500)
        ticks = [tick/10 for tick in tick_labels]

        maxy = 0
        miny = 0

        data = {}
        if args["normvals"]:
            normvals = [float(v) for v in args["normvals"].split(",")]
            if len(normvals) != len(xps):
                raise ValueError("The number of normalisation values must match the number of experiments")

        for i,x in enumerate(xps):
            if args["normvals"]:
                normval = normvals[i]

            bamfile = pysam.AlignmentFile(x["fname"])
            reads = [r for r in bamfile.fetch(chrname,feature["start"]-offsetdown,feature["end"]+offsetup) if checkfilters(r)] #get it into a list, otherwise it doesn't rewind after loop TODO: use multi_iterators param

            if stranded:
                read_starts_fw = [read.reference_start + offsetdown - feature["start"] + 2 for read in reads if not read.is_reverse]
                read_starts_rv = [read.reference_start + offsetdown - feature["start"] + 2 for read in reads if read.is_reverse]
                try:
                    read_weights_fw = [1/dict(read.get_tags())["NH"] for read in reads if not read.is_reverse]
                    read_weights_rv = [1/dict(read.get_tags())["NH"] for read in reads if read.is_reverse]
                except KeyError:
                    read_weights_fw = [1 for read in reads if not read.is_reverse]
                    read_weights_rv = [1 for read in reads if read.is_reverse]
            else:
                read_starts_fw = [read.reference_start + offsetdown - feature["start"] + 2 for read in reads]
                try:
                    read_weights_fw = [1/dict(read.get_tags())["NH"] for read in reads]
                except KeyError:
                    read_weights_fw = [1 for read in reads]

                read_starts_rv = [0 for read in reads]
                read_weights_rv = [1 for read in reads]

            if not args["mmapweight"]:
                read_weights_fw = read_weights_rv = None
                
            x["counts_fw"],x["bins_fw"] = np.histogram(np.array(read_starts_fw),bins=nbins,range=(0,reflen),weights=read_weights_fw)
            x["counts_rv"],x["bins_rv"] = np.histogram(np.array(read_starts_rv),bins=nbins,range=(0,reflen),weights=read_weights_rv)

            if stranded:
                x["counts_rv"] = x["counts_rv"] * -1

            if not stranded or sum(x["counts_fw"]) > sum(x["counts_rv"]): #which bins to use when calculating width, etc
                refbins = "bins_fw"
            else:
                refbins = "bins_rv"

            #TODO: improve this logic. They are not mutually exclusive at the argument level
            if args["normvals"]:
                x["counts_fw"] = x["counts_fw"] / normval
                x["counts_rv"] = x["counts_rv"] / normval
            elif args["normnreads"]:
                print("WARNING: total number of reads is currently counting multi-mappers multiple times")
                nalnreads = int(pysam.view("-c", "-F", "4",x["fname"])[0])
                x["counts_fw"] = x["counts_fw"] / nalnreads
                x["counts_rv"] = x["counts_rv"] / nalnreads
            elif normfeat:
                tmp = sum(r >= normfeat["start"] and r <= normfeat["end"] for r in read_starts_fw)
                tmp += sum(r >= normfeat["start"] and r <= normfeat["end"] for r in read_starts_rv)
                x["counts_fw"] = x["counts_fw"] / tmp
                x["counts_rv"] = x["counts_rv"] / tmp

            x["width"] = (x[refbins][1] - x[refbins][0])
            x["center"] = (x[refbins][:-1] + x[refbins][1:]) / 2

            if max(x["counts_fw"]) > maxy:
                maxy = max(x["counts_fw"])
            if stranded and min(x["counts_rv"]) < miny:
                miny = min(x["counts_rv"])

            if stranded:
                fwcolordef = "blue"
            else:
                fwcolordef = "black"
            rvcolordef = "red"

        for x in xps:
            fig, ax = plt.subplots(figsize=(fheight,fwidth))
            fwax = ax.bar(x["center"], x["counts_fw"], align='center', width=x["width"])
            if stranded:
                rvax = ax.bar(x["center"], x["counts_rv"], align='center', width=x["width"])

            for (bin_start,patch) in zip(x[refbins],fwax.patches):
                patch.set_edgecolor("none")
                patch.set_color(fwcolordef)
                if "subfeatures" in feature:
                    for sf in feature["subfeatures"]:
                        try:
                            fwcolor = sf["fwcolor"]
                        except KeyError:
                            try:
                                fwcolor = sf["color"]
                            except KeyError:
                                if stranded:
                                    fwcolor = "blue"
                                else:
                                    fwcolor = "black"

                        if bin_start >= sf["start"] and bin_start < sf["end"]:
                            patch.set_color(fwcolor)
                            break

            if stranded:
                for (bin_start,patch) in zip(x[refbins],rvax.patches):
                    patch.set_edgecolor("none")
                    patch.set_color(rvcolordef)
                    if "subfeatures" in feature:
                        for sf in feature["subfeatures"]:
                            try:
                                rvcolor = sf["rvcolor"]
                            except KeyError:
                                try:
                                    rvcolor = sf["color"]
                                except KeyError:
                                    rvcolor = "red"

                            if bin_start >= sf["start"] and bin_start < sf["end"]:
                                patch.set_color(rvcolor)
                                break

            ax.set_title("{} ({})".format(feature["name"],x["label"]))
            ax.set_xlim(0,reflen)
            ax.set_ylim(miny,maxy)

            fig.savefig("{}/{}{}_featurehist_{}.svg".format(args["OUTDIR"],args["outprefix"],x["label"],feature["name"]))
            plt.close()
