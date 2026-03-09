import ast

try:
    with open('parsers/suppliers_portal_parser.py', 'r', encoding='utf-8') as f:
        ast.parse(f.read())
    print('✓ Синтаксис suppliers_portal_parser.py корректен')
except SyntaxError as e:
    print(f'✗ Ошибка синтаксиса: {e}')
