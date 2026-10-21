#!/bin/sh
# Run under Linux/WSL, from any directory. Only a newly allocated /tmp folder is removed.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
build=$(mktemp -d /tmp/bifrost-c-tests.XXXXXX)
case "$build" in /tmp/bifrost-c-tests.*) ;; *) exit 1 ;; esac
trap 'rm -rf -- "$build"' EXIT HUP INT TERM
gcc -Wall -Wextra -g -O0 "$root/labs/foundation/addresses.c" -o "$build/addresses"
"$build/addresses" > "$build/address-output"
grep -q 'value=7 dereferenced=7' "$build/address-output"
grep -q 'after=9' "$build/address-output"
gcc -Wall -Wextra -g -O0 "$root/labs/pwn/memory.c" -o "$build/memory"
test "$("$build/memory")" = "$(printf 'local=7 heap=9\n10 20 30')"
gcc -g -O0 -fsanitize=address -fno-omit-frame-pointer "$root/labs/pwn/bounds.c" -o "$build/bounds"
if ASAN_OPTIONS=detect_leaks=0 "$build/bounds" > "$build/diagnostic" 2>&1; then
  printf 'Expected sanitizer failure did not happen.\n' >&2
  exit 1
fi
grep -q 'stack-buffer-overflow' "$build/diagnostic"
sed 's/i <= 3/i < 3/' "$root/labs/pwn/bounds.c" > "$build/fixed.c"
gcc -g -O0 -fsanitize=address "$build/fixed.c" -o "$build/fixed"
test "$(ASAN_OPTIONS=detect_leaks=0 "$build/fixed")" = "$(printf '10\n20\n30')"
for opt in 0 2; do
  gcc -Wall -Wextra -g -O"$opt" "$root/labs/rev/check.c" -o "$build/check"
  test "$("$build/check" BIFROST)" = match
  test "$("$build/check" BIFROSa)" = 'no match'
  test "$("$build/check" bifrost)" = 'no match'
  nm "$build/check" > "$build/symbols"
  grep -q ' check$' "$build/symbols"
  objdump -d "$build/check" > "$build/disassembly"
done
printf 'PASS: C builds, expected outputs, sanitizer error/fix, reverse-analysis inputs and optimization.\n'
