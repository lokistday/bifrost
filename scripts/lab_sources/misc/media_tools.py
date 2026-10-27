"""Original fixed offline media/container and bounded-processing exercises.

No image is edited. PPM is an authored text fixture read as pixel data.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import zlib

HERE = Path(__file__).resolve().parent
TRANSFORM_VERSION = "upper-ascii-v1"


def kind(data):
    if data.startswith(b"\x1f\x8b"):
        return "GZIP-CANDIDATE"
    if data.startswith(b"PK\x03\x04"):
        return "ZIP-CANDIDATE"
    if data.startswith(b"P3"):
        return "PPM-CANDIDATE"
    return "UNKNOWN"


def identify():
    # gzip compression only packages our tiny local constant.
    data = gzip.compress(b"Bifrost\n", mtime=0)
    print(f"outer={kind(data)}")
    with gzip.GzipFile(fileobj=io.BytesIO(data), mode="rb") as file:
        body = file.read(65)
    print(f"inner-bytes={len(body)} text={body.decode('ascii').strip()}")
    print(f"truncated-header={kind(data[:2])} structure-validated=False")


def read_ppm(text):
    tokens = " ".join(line.split("#", 1)[0] for line in text.splitlines()).split()
    if len(tokens) < 4 or tokens[0] != "P3":
        raise ValueError("P3 header required")
    width, height, maximum = map(int, tokens[1:4])
    if not 1 <= width <= 64 or not 1 <= height <= 64 or not 1 <= maximum <= 255:
        raise ValueError("exercise bounds: 1..64 dimensions, max 1..255")
    values = list(map(int, tokens[4:]))
    if len(values) != width * height * 3 or any(not 0 <= value <= maximum for value in values):
        raise ValueError("sample count/range")
    return width, height, maximum, [tuple(values[i:i + 3]) for i in range(0, len(values), 3)]


def ppm(source):
    width, height, maximum, pixels = read_ppm(Path(source).read_text(encoding="ascii"))
    sums = [sum(pixel[i] for pixel in pixels) for i in range(3)]
    print(f"magic=P3 width={width} height={height} max={maximum}")
    print(f"pixels={len(pixels)} red-sum={sums[0]} green-sum={sums[1]} blue-sum={sums[2]}")
    print(f"first={pixels[0]}")


def entropy(data):
    if not data:
        return 0.0
    counts = Counter(data)
    return max(0.0, -sum((count / len(data)) * math.log2(count / len(data)) for count in counts.values()))


def frequency():
    samples = {"constant": b"A" * 256, "alternating": b"AB" * 128, "all-values": bytes(range(256))}
    for name, data in samples.items():
        print(f"{name} bytes={len(data)} unique={len(set(data))} H={entropy(data):.3f}")
    print("classification=NOT-DETERMINED")


def bounded_decompress(data, output_limit=64, input_limit=1024):
    if type(output_limit) is not int or output_limit < 0 or type(input_limit) is not int or input_limit < 0:
        raise ValueError("nonnegative integer budgets required")
    if len(data) > input_limit:
        raise ValueError("input budget")
    decoder = zlib.decompressobj()
    # Ask for at most limit+1. Never use flush() to emit an unbounded remainder.
    output = decoder.decompress(data, output_limit + 1)
    if len(output) > output_limit or decoder.unconsumed_tail:
        raise ValueError("output budget")
    if not decoder.eof:
        raise ValueError("truncated stream")
    if decoder.unused_data:
        raise ValueError("trailing/concatenated stream")
    return output


def decompress(limit):
    packed = zlib.compress(b"A" * 32)
    try:
        body = bounded_decompress(packed, limit)
        print(f"accepted=True output={len(body)} limit={limit}")
    except ValueError as error:
        print(f"accepted=False reason={error} limit={limit}")


def job_key(job):
    data = job["text"].encode("ascii")
    return hashlib.sha256(TRANSFORM_VERSION.encode("ascii") + b"\x00" + data).hexdigest()


def batch_process(sample, previous):
    if not isinstance(sample, dict) or type(sample.get("schema")) is not int or sample["schema"] != 1 or not isinstance(sample.get("jobs"), list):
        raise ValueError("job schema")
    jobs = sample["jobs"]
    seen = set()
    for job in jobs:
        if (not isinstance(job, dict) or set(job) != {"id", "text"}
                or not isinstance(job["id"], str) or not job["id"].strip()
                or not isinstance(job["text"], str) or not job["text"].isascii()
                or job["id"] in seen):
            raise ValueError("invalid/duplicate job")
        seen.add(job["id"])
    if (not isinstance(previous, dict) or type(previous.get("schema")) is not int or previous["schema"] != 1
            or previous.get("transform") != TRANSFORM_VERSION or not isinstance(previous.get("done"), dict)):
        raise ValueError("checkpoint schema/version")
    done = dict(previous["done"])
    results = []
    for job in jobs:
        key = job_key(job)
        # In the fixture we verify cached output, rather than trusting its hash field alone.
        expected = job["text"].upper()
        cached = done.get(job["id"])
        if isinstance(cached, dict) and cached.get("key") == key and cached.get("result") == expected:
            results.append((job["id"], "SKIP", expected))
        else:
            results.append((job["id"], "RUN", expected))
            done[job["id"]] = {"key": key, "result": expected}
    return results, {"schema":1, "transform":TRANSFORM_VERSION, "done":done}


def batch(source, checkpoint):
    sample = json.loads(Path(source).read_text(encoding="utf-8"))
    previous = {"schema":1, "transform":TRANSFORM_VERSION, "done":{}}
    if checkpoint and Path(checkpoint).exists():
        previous = json.loads(Path(checkpoint).read_text(encoding="utf-8"))
    results, state = batch_process(sample, previous)
    for id, status, result in results:
        print(f"{id} {status} {result}")
    if checkpoint:
        path = Path(checkpoint)
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_text(json.dumps(state, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        temporary.replace(path)
    print(f"jobs={len(results)} checkpoint={'WRITTEN' if checkpoint else 'MEMORY-ONLY'}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["identify", "ppm", "frequency", "decompress", "batch"])
    parser.add_argument("--source")
    parser.add_argument("--limit", type=int, default=64)
    parser.add_argument("--checkpoint")
    args = parser.parse_args()
    try:
        if args.mode == "identify": identify()
        elif args.mode == "ppm": ppm(args.source or HERE / "sample-p3.ppm")
        elif args.mode == "frequency": frequency()
        elif args.mode == "decompress": decompress(args.limit)
        else: batch(args.source or HERE / "batch-jobs.json", args.checkpoint)
    except (OSError, ValueError, KeyError, TypeError, zlib.error) as error:
        parser.exit(2, f"INVALID: {error}\n")


if __name__ == "__main__":
    main()
