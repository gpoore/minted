import re

pattern = re.compile(r'\\RequirePackage\{([a-z0-9]+)\}')

with open('minted.sty') as f:
    sty = f.read()

with open('DEPENDS.txt', 'w', encoding='utf8') as f:
    for pkg in sorted(match.group(1) for match in pattern.finditer(sty)):
        f.write(f'{pkg}\n')
