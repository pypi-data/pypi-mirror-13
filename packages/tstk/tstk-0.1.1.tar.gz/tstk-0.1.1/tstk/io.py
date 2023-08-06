def openfastx(fpath,mode="rt"):
    import os

    gz = False
    fpathnoext, fext = os.path.splitext(fpath)
    if fext == '.gz':
        gz = True
        fpathnoext, fext = os.path.splitext(fpathnoext)

    if fext.lstrip(".") in ['fasta','fa']:
        ftype = 'fasta'
    elif fext.lstrip(".") in ['fastq','fq']:
        ftype = 'fastq'
    else:
        raise ValueError("File type [fasta/fastq] could not be determined from the filename '{}'.".format(fpath))

    if gz:
        import gzip
        fh = gzip.open(fpath,mode)
    else:
        fh = open(fpath,mode)

    return fpathnoext,fext,ftype,fh

def parsefastx(fp): # this is a generator function
    last = None # this is a buffer keeping the last unprocessed line
    while True: # mimic closure; is it a bad idea?
        if not last: # the first record or a record following a fastq
            for l in fp: # search for the start of the next record
                if l[0] in '>@': # fasta/q header line
                    last = l[:-1] # save this line
                    break
        if not last: break
        name, seqs, last = last[1:].partition(" ")[0], [], None
        for l in fp: # read the sequence
            if l[0] in '@+>':
                last = l[:-1]
                break
            seqs.append(l[:-1])
        if not last or last[0] != '+': # this is a fasta record
            yield name, ''.join(seqs), None # yield a fasta record
            if not last: break
        else: # this is a fastq record
            seq, leng, seqs = ''.join(seqs), 0, []
            for l in fp: # read the quality
                seqs.append(l[:-1])
                leng += len(l) - 1
                if leng >= len(seq): # have read enough quality
                    last = None
                    yield name, seq, ''.join(seqs); # yield a fastq record
                    break
            if last: # reach EOF before reading enough quality
                yield name, seq, None # yield a fasta record instead
                break

def openxam(fpath,mode="r",template=None):
    print("DONT USE THIS ANYMORE, JUST CALL pysam.AlignmentFile directly. Quitting now.")
    import pysam,sys,os

    if mode not in ['r','rb','w','wb']:
        raise ValueError("Unrecognized open mode '{}'".format(mode))

    fpathnoext, fext = os.path.splitext(fpath)

    if fext == ".bam" and len(mode) == 1:
        mode += "b"

    return(pysam.AlignmentFile(fpath, mode, template=template))
