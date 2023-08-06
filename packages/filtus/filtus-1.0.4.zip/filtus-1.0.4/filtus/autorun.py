
def vcf(filtus):
    with open('C:\\Projects\\database.vcf', 'a') as db:
        for vf in filtus.filteredFiles:
            print vf.shortName
            chromPosRefAlt = vf.chromPosRefAlt
            GTnum = vf.GTnum()
            for v in vf.variants:
                vdef = chromPosRefAlt(v)
                if ',' in vdef[3]: continue
                db.write('\t'.join(map(str, vdef + (vf.shortName, GTnum(v)))) + '\n')
