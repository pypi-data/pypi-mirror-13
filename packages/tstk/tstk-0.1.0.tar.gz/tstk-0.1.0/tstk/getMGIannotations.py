def parsearguments():
    import argparse,sys

    epilog = """============================== Alea jacta est =============================="""
    parser = argparse.ArgumentParser(epilog=epilog,formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('OUTDIR',help="Output directory")

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    return(vars(parser.parse_args()))

if __name__ == "__main__":
    import urllib.request
    import pandas as pd
    from time import strftime

    args = parsearguments()

    types = [['tRNA',6238164],['rRNA',6238163]]

    for t in types:
        url = "http://www.informatics.jax.org/marker/report.txt?mcv={}".format(t[1])
        data = pd.read_table(urllib.request.urlopen(url))

        data.columns = ['chr', 'start', 'end', 'cM', 'strand', 'MGI ID', 'Feature Type', 'symbol', 'name', 'Unnamed: 9', 'Unnamed: 10']
        data['score'] = 0
        data['chr'] = 'chr' + data['chr']
        data = data[['chr','start','end','symbol','score','strand']].dropna()
        data.loc[data['chr']=='chrMT','chr'] = 'chrM'
        data[['start','end']] = data[['start','end']].astype(int)

        outfname = "{}/MGI_{}_{}.bed".format(args["OUTDIR"],t[0],strftime("%Y%m%d"))
        data.to_csv(outfname,sep="\t",header=False,index=False)

