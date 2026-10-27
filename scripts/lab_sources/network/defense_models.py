"""Offline network reasoning models. No sockets, captures, or firewall changes.

State tracking deliberately omits real TCP sequence windows, retransmission,
timeouts, and implementation-specific firewall behavior.
"""
import argparse
import ipaddress
import json
from pathlib import Path


def load(path=None):
    return json.loads(Path(path or Path(__file__).with_name('defense-models.json')).read_text(encoding='utf-8'))


def route(destination, routes):
    address = ipaddress.IPv4Address(destination)
    matches = [(ipaddress.IPv4Network(row['prefix']), row['next_hop']) for row in routes
               if address in ipaddress.IPv4Network(row['prefix'])]
    return max(matches, key=lambda row: row[0].prefixlen) if matches else None


def correlate_nat(observation, mappings):
    return [row['private_ip'] for row in mappings
            if row['public_ip'] == observation['public_ip']
            and row['public_port'] == observation['public_port']
            and row['destination'] == observation['destination']
            and row['start'] <= observation['time'] < row['end']]


def track(events):
    states = {}
    output = []
    for row in events:
        key = (row['client'], row['client_port'], row['server'], row['server_port'])
        state = states.get(key)
        event = row['event']
        allowed = False
        if event == 'SYN' and row['direction'] == 'out' and row['server_port'] == 443 and state is None:
            states[key] = 'pending'
            allowed = True
        elif event == 'SYN_ACK' and row['direction'] == 'in' and state == 'pending':
            states[key] = 'reply-seen'
            allowed = True
        elif event == 'ACK' and row['direction'] == 'out' and state == 'reply-seen':
            states[key] = 'established'
            allowed = True
        elif event == 'DATA' and row['direction'] in ('in', 'out') and state == 'established':
            allowed = True
        elif event == 'CLOSE' and row['direction'] in ('in', 'out') and state == 'established':
            del states[key]
            allowed = True
        output.append((row['id'], allowed, states.get(key, 'none')))
    return output


def metrics(rows, threshold):
    counts = dict(TP=0, FP=0, FN=0, TN=0)
    for row in rows:
        predicted = row['score'] >= threshold
        counts[('T' if predicted == row['attack'] else 'F') + ('P' if predicted else 'N')] += 1
    precision = counts['TP'] / (counts['TP'] + counts['FP']) if counts['TP'] + counts['FP'] else None
    recall = counts['TP'] / (counts['TP'] + counts['FN']) if counts['TP'] + counts['FN'] else None
    return counts, precision, recall


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['routing', 'nat', 'state', 'metrics', 'response'])
    parser.add_argument('--input', help='working copy of defense-models.json')
    parser.add_argument('--destination', default='10.20.1.7')
    parser.add_argument('--threshold', type=int, default=3)
    args = parser.parse_args()
    data = load(args.input)
    if args.mode == 'routing':
        result = route(args.destination, data['routes'])
        print('route=NONE' if result is None else f'prefix={result[0]} next_hop={result[1]}')
    elif args.mode == 'nat':
        for row in data['observations']:
            matches = correlate_nat(row, data['nat'])
            print(f"{row['id']} matches={len(matches)} private={','.join(matches) or 'UNKNOWN'}")
    elif args.mode == 'state':
        for identifier, allowed, state in track(data['state_events']):
            print(f'{identifier} {"ALLOW" if allowed else "DENY"} state={state}')
    elif args.mode == 'metrics':
        counts, precision, recall = metrics(data['detections'], args.threshold)
        print(' '.join(f'{key}={value}' for key, value in counts.items()))
        show = lambda value: 'undefined' if value is None else f'{value:.3f}'
        print(f'precision={show(precision)} recall={show(recall)}')
    else:
        related = sorted((row for row in data['response'] if row['request_id'] == 'R-17'), key=lambda row: row['time'])
        for row in related:
            print(f"{row['time']} {row['source']} {row['result']}")
        expected = {('dns', 'resolved'), ('firewall', 'allow'), ('app', '401')}
        observed = {(row['source'], row['result']) for row in related}
        conclusion = 'attempt_observed' if expected <= observed else 'insufficient_evidence'
        print(f'correlated={len(related)} conclusion={conclusion} impact=UNCONFIRMED')


if __name__ == '__main__':
    main()
