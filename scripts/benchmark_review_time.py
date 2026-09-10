"""Small helper to compute before/after review-time reduction from your timed PR samples."""
import argparse, statistics
p=argparse.ArgumentParser(); p.add_argument('--before',nargs='+',type=float,required=True); p.add_argument('--after',nargs='+',type=float,required=True); a=p.parse_args()
b=statistics.mean(a.before); c=statistics.mean(a.after); reduction=(b-c)/b*100
print(f'Before mean: {b:.2f} min'); print(f'After mean: {c:.2f} min'); print(f'Reduction: {reduction:.1f}%')
