"""Subset a licensed Noto Sans SC variable TTF to the current CV content.

Usage: python3 .github/scripts/prepare-cv-fonts.py /path/to/NotoSansSC[wght].ttf
Requires fonttools. See ../fonts/README.md for the source and license.
"""
import sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools import subset
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / '.github/fonts'
SOURCES = [ROOT / '.github/scripts/build-cv.py', *sorted((ROOT / '_data').glob('*.yml'))]
text = ''.join(path.read_text(encoding='utf-8') for path in SOURCES)
codepoints = set(map(ord, text)) | set(range(32, 256)) | {0x2192, 0x00d7, 0x2022, 0x2013, 0x2014}
for label, weight in (('Regular', 400), ('Bold', 650)):
    font = TTFont(sys.argv[1], recalcTimestamp=False)
    options = subset.Options()
    options.name_IDs = ['*']
    options.name_legacy = True
    options.name_languages = ['*']
    sub = subset.Subsetter(options=options)
    sub.populate(unicodes=codepoints)
    sub.subset(font)
    font = instantiateVariableFont(font, {'wght': weight}, inplace=True)
    # Give the static faces distinct PostScript names so PDF font caches do not
    # confuse the variable font's original Thin name with both output weights.
    names = {1: 'CV Sans SC', 2: label, 3: 'CVSansSC-' + label,
             4: 'CV Sans SC ' + label, 6: 'CVSansSC-' + label,
             16: 'CV Sans SC', 17: label}
    for record in list(font['name'].names):
        if record.nameID in names:
            font['name'].setName(names[record.nameID], record.nameID,
                                 record.platformID, record.platEncID, record.langID)
    target = OUTPUT / f'NotoSansSC-CV-{label}.ttf'
    font.save(target)
    print(f'{target}: {target.stat().st_size:,} bytes')
