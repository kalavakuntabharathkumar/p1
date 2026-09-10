"""Evaluate alert precision/false-positive rate from CSV: predicted,label where 1 means actionable."""
import csv,sys
rows=list(csv.DictReader(open(sys.argv[1],newline='',encoding='utf-8')))
shown=[r for r in rows if r['predicted'].strip()=='1']
fp=sum(r['label'].strip()=='0' for r in shown)
rate=(fp/len(shown)*100) if shown else 0
print(f'Alerts shown: {len(shown)}'); print(f'False positives: {fp}'); print(f'False-positive rate: {rate:.1f}%')
