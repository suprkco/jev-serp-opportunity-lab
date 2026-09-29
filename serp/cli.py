import argparse
import json
from pathlib import Path

from serp.engine import (
    decide,
    lexical_baseline,
    live_judge,
    load_records,
    simulated_judge,
    write_html,
)


def main():
    parser = argparse.ArgumentParser(description='Triage supplied search snippets; no scraping or autonomous publishing.')
    parser.add_argument('--mode', choices=['fixture','live'], default='fixture')
    parser.add_argument('--input', default='data/synthetic_serp.json')
    parser.add_argument('--output', default='output')
    parser.add_argument('--max-requests', type=int, default=0, help='Explicit upper bound for paid API calls; live mode only')
    args = parser.parse_args()
    records = load_records(args.input)
    if args.mode == 'live' and not len(records) <= args.max_requests <= 50:
        parser.error('Live mode requires --max-requests covering the input (at most 50)')
    rows = []
    for record in records:
        result = live_judge(record) if args.mode == 'live' else simulated_judge(record)
        rows.append({k:record[k] for k in ['query','title','snippet']} | result |
                    {'decision': decide(result['answers']), 'lexical_baseline': lexical_baseline(record)})
    report = {'mode': args.mode,
        'disclaimer': 'SIMULATED RESPONSES: no Jev API calls or model benchmark.' if args.mode == 'fixture' else 'Live Jev responses on supplied snippets. Probabilities are not independently calibrated here. Inspect full pages before acting.',
        'results': rows}
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output/'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    write_html(report, output/'index.html')
    print(f'Wrote {len(rows)} records to {output}; mode={args.mode}')

if __name__ == '__main__':
    main()
