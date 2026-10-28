"""Check explicit CSS colour pairs. This does not inspect rendered browser styles."""
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    ('Body on canvas', '#163b35', '#f7f8f2'), ('Body on white', '#163b35', '#ffffff'),
    ('Muted and placeholder', '#5c6b63', '#ffffff'), ('Muted on canvas', '#5c6b63', '#f7f8f2'),
    ('Primary control', '#ffffff', '#176350'), ('Information status', '#176350', '#eaf4ed'),
    ('Amber status', '#805318', '#fff3dd'), ('Error', '#9b2936', '#fff0f1'),
    ('Success status', '#256344', '#edf7f0'), ('Navigation', '#354e47', '#f0f2e9'),
    ('Active navigation', '#ffffff', '#155543'), ('Navigation hover', '#354e47', '#e1e8dc'),
    ('Rail subtitle', '#5c6b63', '#f0f2e9'), ('Prototype strip', '#52634f', '#ecefe5'),
    ('Count label', '#5c6b63', '#e9eee5'), ('Focus title', '#f4f7ee', '#123b3b'),
    ('Focus supporting copy', '#c2d6ca', '#123b3b'), ('Focus due label', '#f5d28c', '#123b3b'),
    ('Focus button', '#173d32', '#dfedc8'), ('Focus button hover', '#173d32', '#d2e6a7'),
]
def light(colour):
    values = [int(colour[i:i+2], 16)/255 for i in (1, 3, 5)]
    values = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in values]
    return sum(v*w for v, w in zip(values, [.2126, .7152, .0722]))
results = []
css = '\n'.join((ROOT/'frontend/src/design-system'/name).read_text(encoding='utf-8')
                for name in ['tokens.css', 'workspace.css', 'desk.css', 'connections.css'])
css = re.sub(r'#([0-9a-f]{3})(?![0-9a-f])', lambda m: '#' + ''.join(c*2 for c in m[1]), css)
for label, foreground, background in PAIRS:
    assert foreground in css and background in css, 'Pair not present in current CSS'
    low, high = sorted([light(foreground), light(background)])
    ratio = (high+.05)/(low+.05)
    results.append({'label': label, 'foreground': foreground, 'background': background,
                    'ratio': round(ratio, 3), 'meets_4_5': ratio >= 4.5})
passed = all(r['meets_4_5'] for r in results)
output = {'method': 'Static CSS colour-pair calculation, not computed styles or accessibility certification',
          'passed': passed, 'pairs': results}
(ROOT/'docs/evidence/brand-redesign-20261028/contrast.json').write_text(json.dumps(output, indent=2), encoding='utf-8')
print(json.dumps(output, indent=2))
raise SystemExit(0 if passed else 1)
