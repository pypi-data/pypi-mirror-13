import sys
import re
import numpy

def match_and_get(pattern):
    p = pattern.split(',')
    text = p[0]
    skip, lines, start, end = map(int, p[1:])
    def match(line):
        return re.search(text, line)
    match.skip = skip
    match.lines = lines
    def get(line):
        #print "get:",line.split()
        fields = [ float(i) for i in line.split()[start-1: end] ]
        #print fields
        return fields
    return (text, match, get, [])
        
if __name__ == '__main__':
    rules=[]

    for p in open(sys.argv[1]).readlines():
        #print p.split()
        rules.append(match_and_get(p))
            
    with open(sys.argv[2]) as target:
        for line in target:
            for t, m, g, r in rules:
                if m(line):
                    for s in range(m.skip): line=next(target)
                    for l in range(m.lines): line+=next(target)
                    r.append(g(line))

    from util import full
    for t,m,g,r in rules:
        print t, full.init(r).T
        
