from lab_input import read_json
from web_state import Checkout
def solve(root, variant):
    source = read_json(root / f'project-input-{variant}.json')
    store = Checkout(source['stock'])
    try:
        outcomes = ['UNAUTHENTICATED' if r['now'] >= r['expires'] else
                    store.reserve(r['user'],r['key'],r['quantity']) for r in source['requests']]
        return dict(outcomes=outcomes, stock=store.db.execute('SELECT stock FROM inventory').fetchone()[0],
                    orders=store.db.execute('SELECT COUNT(*) FROM orders').fetchone()[0])
    finally:
        store.db.close()
