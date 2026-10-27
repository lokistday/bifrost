"""Local result checker. Reads JSON answers; never imports or runs submitted code."""
import argparse
import json
from pathlib import Path
from lab_input import InputError, read_json
from project_reference import solve

ROOT = Path(__file__).resolve().parent


def compare(actual, expected, path='$'):
    if type(actual) is not type(expected):
        return [f'{path}: 자료형을 확인하세요.']
    if isinstance(expected, dict):
        if set(actual) != set(expected):
            return [f'{path}: 필드 목록을 확인하세요.']
        return [issue for key in expected for issue in compare(actual[key], expected[key], f'{path}.{key}')]
    if isinstance(expected, list):
        if len(actual) != len(expected):
            return [f'{path}: 항목 수를 확인하세요.']
        return [issue for i, (a, e) in enumerate(zip(actual, expected)) for issue in compare(a, e, f'{path}[{i}]')]
    return [] if actual == expected else [f'{path}: 입력 근거·경계값·순서를 다시 확인하세요.']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['check', 'example', 'template'])
    parser.add_argument('answer', nargs='?')
    parser.add_argument('--variant', choices=['a', 'b'], default='a')
    args = parser.parse_args()
    if args.mode == 'template':
        print((ROOT / 'project-answer-template.json').read_text(encoding='utf-8'))
        return 0
    expected = solve(ROOT, args.variant)
    if args.mode == 'example':
        print(json.dumps(expected, ensure_ascii=False, indent=2))
        return 0
    if not args.answer:
        parser.error('check에는 직접 만든 답안 JSON 경로가 필요합니다.')
    try:
        actual = read_json(args.answer)
    except InputError as error:
        parser.error(str(error))
    issues = compare(actual, expected)
    if issues:
        print('\n'.join(issues[:20]))
        print('REVIEW: project-brief.md의 출력 계약과 루브릭을 확인하세요.')
        return 1
    print('RESULT MATCH: 이 표본의 결과값이 일치합니다. 코드 품질·분석 근거·실력 인증을 의미하지 않습니다.')
    print('B 변형도 풀고 project-report.md의 근거와 한계를 별도로 검토하세요.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
