"""Own token protocol model, not a socket server or a network security protocol."""
import argparse


def trace(tokens):
    state = "CLOSED"
    count = 0
    transitions = []
    for index, token in enumerate(tokens, 1):
        before = state
        if state == "CLOSED" and token == "HELLO":
            state = "READY"
        elif state == "READY" and token == "DATA":
            count += 1
        elif state == "READY" and token == "END":
            state = "DONE"
        else:
            raise ValueError(f"step={index} state={state} token={token}")
        transitions.append(f"{before} --{token}--> {state}")
    if state != "DONE":
        raise ValueError(f"incomplete final={state}")
    return transitions, count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tokens", nargs="*", default=["HELLO", "DATA", "END"])
    args = parser.parse_args()
    try:
        transitions, count = trace(args.tokens)
    except ValueError as error:
        parser.exit(2, f"REJECT: {error}\n")
    print("\n".join(transitions))
    print(f"accepted=True data={count}")


if __name__ == "__main__":
    main()
