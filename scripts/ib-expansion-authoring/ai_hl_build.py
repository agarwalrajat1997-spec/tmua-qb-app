"""Reproduce all 500 original AI HL practice questions deterministically."""
import argparse, importlib
from ai_hl_common import *
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int,choices=[80,100],default=100);args=parser.parse_args()
 for name in ['number','functions','geometry','statistics','calculus']:
  importlib.import_module('ai_hl_'+name).build()
 write(args.limit)
 print(json.dumps({'records':5*args.limit,'perTopic':args.limit,'families':{t:len(x) for t,x in FAMILIES.items()},'investigations':sum(r['marks']>=12 for r in LEDGER if int(r['id'][-3:])<=args.limit),'diagrams':sum(bool(r['figureHashes']) for r in LEDGER if int(r['id'][-3:])<=args.limit)}))
if __name__=='__main__':main()
