import sys,glob,os

def countdups(fi,fo):
    #This function takes a collapsed fasta file (from fastx_collapser) and calculates the fractions of Unique reads, duplicate reads and singletons.
    #It then prints out the info to a tab-delimited text file that can be opened in Excel.

    #Opens a fasta file with the database sequences as specified by user. Must be non-interleaved.
    with open(fi, 'r') as SEQS:
        #Opens an output text file as specified by user
        with open(fo, 'w') as HEADERS:
            with open(fi.replace(".txt","_dupcount.csv"), 'w') as OUT:
                duplicates=0
                dupreadcount=0
                singletons=0
                totalreadcount=0
                HEADERS.write('UniqueNumber'+'\t'+'Numseqscollapsed')
                for line in SEQS:
                    line=line.rstrip()
                    if line[0:1] == '>':
                        line=line.strip('>')
                        cols=line.split('-')
                        if int(cols[1]) > 1:
                            duplicates+=1
                            dupreadcount+=int(cols[1])
                            totalreadcount+=int(cols[1])
                            HEADERS.write('\n'+'\t'.join(cols))
                        elif int(cols[1]) == 1:	
                            totalreadcount+=int(cols[1])
                            singletons+=1

                percentsingletons=float(singletons)/float(totalreadcount)
                percentduplicates=float(dupreadcount)/float(totalreadcount)
                percentuniquedups=float(duplicates)/float(dupreadcount)
                OUT.write('n_uniq_w_dups'+'\t'+'n_collapsed_dups'+'\t'+ 'n_singletons' + '\t' + 'total_reads' + '\t' + 'pct_singletons' + '\t' + 'pct_dups' + '\t' + 'pct_uniq_w_dups')
                OUT.write('\n' + str(duplicates) + '\t' + str(dupreadcount) + '\t' + str(singletons) + '\t' + str(totalreadcount) + '\t' + str(percentsingletons) + '\t' + str(percentduplicates) + '\t' + str(percentuniquedups))

for f in glob.glob("fastq/out/*.txt"):
    print("*************")
    print(f)
    fo = f.replace(".txt","_headers.txt")
    countdups(f,fo)
    os.remove(fo)
