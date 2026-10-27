"""Offline IPv6/stream/DNS/MTU/time reasoning, not a network stack or resolver."""
import argparse
from lab_input import read_json
from model_contracts import check
import ipaddress
import math
from pathlib import Path


def load(path=None):
    return check(read_json(path or Path(__file__).with_name('protocol-models.json')), 'network')


def scope(address):
    ip = ipaddress.ip_address(address)
    if ip.version == 4:
        return 'ipv4'
    if ip.is_loopback:
        return 'loopback'
    if ip.is_link_local:
        return 'link-local'
    if ip in ipaddress.ip_network('fc00::/7'):
        return 'unique-local'
    return 'other-ipv6'


def family_policy(row, rules):
    address = ipaddress.ip_address(row['destination'])
    if address.version == 6 and address.is_link_local and not row.get('interface'):
        return 'SCOPE_REQUIRED'
    for rule in rules:
        network = ipaddress.ip_network(rule['network'])
        if address.version == network.version and address in network and row['port'] == rule['port']:
            return 'ALLOW'
    return 'DENY'


def reassemble(segments, length):
    if type(length) is not int or not 0 <= length <= 65536:
        raise ValueError('educational stream length outside 0..65536')
    cells, conflicts = {}, set()
    for segment in segments:
        offset = segment['offset']
        payload = bytes.fromhex(segment['hex'])
        if type(offset) is not int or offset < 0 or offset + len(payload) > length:
            raise ValueError('segment outside declared stream')
        for position, value in enumerate(payload, offset):
            if position in cells and cells[position] != value:
                conflicts.add(position)
            else:
                cells[position] = value
    missing = [position for position in range(length) if position not in cells]
    data = bytes(cells[i] for i in range(length)) if not missing and not conflicts else None
    return data, missing, sorted(conflicts), len(cells)


def dns_lookup(records, name, qtype, now):
    # One IN class, fixed source, no DNSSEC, CNAME, delegation, or stale serving.
    name, qtype = name.lower().rstrip('.'), qtype.upper()
    for row in records:
        if row['name'].lower().rstrip('.') != name:
            continue
        negative = row['status'] in ('NXDOMAIN', 'NODATA')
        if row['status'] != 'NXDOMAIN' and row['qtype'] != qtype:
            continue
        ttl = min(row['soa_ttl'], row['soa_minimum']) if negative else row['ttl']
        if row['received'] <= now < row['received'] + ttl:
            return ('NEGATIVE_' + row['status'], None) if negative else ('HIT', row['answer'])
    return 'MISS', None


def tcp_budget(mtu, version, extra_headers=0):
    if version not in (4, 6) or type(mtu) is not int or type(extra_headers) is not int or extra_headers < 0:
        raise ValueError('invalid MTU/header model input')
    if version == 6 and mtu < 1280:
        raise ValueError('IPv6 MTU below the 1280-byte minimum requires lower-layer handling outside this model')
    budget = mtu - (40 if version == 6 else 20) - 20 - extra_headers
    if budget < 0:
        raise ValueError('headers exceed MTU')
    return budget


def sessions(events, timeout):
    if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError('positive finite session timeout required')
    if any(type(row['event_time']) not in (int, float) or not math.isfinite(row['event_time']) for row in events):
        raise ValueError('finite numeric event_time required')
    grouped = []
    for row in sorted(events, key=lambda row: row['event_time']):
        if not grouped or row['event_time'] - grouped[-1][-1]['event_time'] >= timeout:
            grouped.append([row])
        else:
            grouped[-1].append(row)
    return grouped


def accept_late(events, lateness):
    if type(lateness) not in (int, float) or not math.isfinite(lateness) or lateness < 0:
        raise ValueError('nonnegative finite lateness required')
    maximum, accepted, late = float('-inf'), [], []
    # Input order is ingestion order; event_time is allowed to move backwards.
    for row in events:
        if type(row['event_time']) not in (int, float) or not math.isfinite(row['event_time']):
            raise ValueError('finite event_time required')
        if row['event_time'] < maximum - lateness:
            late.append(row)
        else:
            accepted.append(row)
        maximum = max(maximum, row['event_time'])
    return accepted, late


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['ipv6', 'reassembly', 'dns', 'mtu', 'sessions'])
    parser.add_argument('--input')
    parser.add_argument('--case', choices=['complete', 'gap', 'conflict'], default='complete')
    args = parser.parse_args()
    data = load(args.input)
    if args.mode == 'ipv6':
        for row in data['family_requests']:
            print(f"{row['id']} scope={scope(row['destination'])} decision={family_policy(row, data['family_rules'])}")
    elif args.mode == 'reassembly':
        selected = data['stream'][args.case]
        result, missing, conflict, count = reassemble(selected, data['stream']['length'])
        print(f'bytes={count} missing={len(missing)} conflicts={len(conflict)}')
        print('text=' + (result.decode('ascii') if result is not None else 'UNAVAILABLE'))
    elif args.mode == 'dns':
        for query in data['queries']:
            state, answer = dns_lookup(data['dns_records'], query['name'], query['qtype'], query['now'])
            print(f"{query['id']} state={state} answer={answer or '-'}")
    elif args.mode == 'mtu':
        record = data['mtu']
        oversized = record['packet_bytes'] > record['path_mtu']
        print(f'packet={record["packet_bytes"]} path_mtu={record["path_mtu"]} oversized={oversized}')
        print('ptb_blocked=' + ('STALLED' if oversized else 'FITS'))
        print(f'ptb_allowed=tcp_payload_budget_{record["version"]}={tcp_budget(record["path_mtu"], record["version"])}')
    else:
        accepted, late = accept_late(data['events'], data['lateness'])
        print(f'accepted={len(accepted)} late={len(late)} sessions={len(sessions(accepted, data["timeout"]))}')
        print('late_ids=' + ','.join(row['id'] for row in late))
        print(f'retrospective_sessions={len(sessions(data["events"], data["timeout"]))}')


if __name__ == '__main__':
    try:
        main()
    except ValueError as error:
        print("INVALID input: " + str(error), file=__import__("sys").stderr)
        raise SystemExit(2)
