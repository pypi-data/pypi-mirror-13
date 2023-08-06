from common import featurecountsdf
import sys

df = featurecountsdf(sys.argv[1])

mapped = {s.split(":")[0] : int(s.split(":")[1]) for s in sys.argv[2].split(",")} # comma separated list of bamfname:mappedreads

#TODO: operate on all of the row's count cells at once as an array

for c in df.columns:
    if c in mapped:
        df[c+".RPKM"] = df[c]
        for row,reads in df[c+".RPKM"].iteritems():
            length = df.ix[row]["Length"]
            df.set_value(row,c+".RPKM", (10**9 * reads) / (length * mapped[c]))

df.to_csv("outas",sep="\t")
