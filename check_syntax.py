import ast

try:
    with open('parsers/eis_parser.py', 'r', encoding='utf-8') as f:
        ast.parse(f.read())
    print('✓ Синтаксис eis_parser.py корректен')
except SyntaxError as e:
    print(f'✗ Ошибка синтаксиса: {e}')
