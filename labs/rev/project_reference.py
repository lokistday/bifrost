from lab_input import read_json
def solve(root, variant):
    state, accepted, states = 0, 0, []
    for token in read_json(root / f'project-input-{variant}.json')['tokens']:
        if token == 'login' and not state: state=1; accepted+=1
        elif token == 'read' and state: accepted+=1
        elif token == 'logout' and state: state=0; accepted+=1
        states.append(state)
    return dict(states=states, accepted=accepted)
