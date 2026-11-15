import sys
d=open(sys.argv[1]).read(); s=open(sys.argv[2]).read()
assert '/*DATOS*/null' in s
open(sys.argv[3],'w').write(s.replace('/*DATOS*/null', d))
