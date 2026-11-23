"""Build, verify and package the full-range Admiralty variable fonts."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from fontTools.ttLib import TTFont

from audit_symbol_family import BY_NAME, SAMPLES
from audit_text_family import BETWEEN_MASTERS, LOCATIONS
from build_text_family import OUTPUT, REVIEW, ROOT, TEXT, fullrange_unique_id
from check_optical_inventory import SAMPLES as OPTICAL_GRID
from glyph_peers import reference_names
from magnified_audit import GRID as MAGNIFIED_GRID, PPEM

FAMILIES=[*TEXT,'AdmiraltySymbols']
PACKAGE=ROOT/'fonts'/'variable'/'fullrange'
HERE=Path(__file__).resolve().parent


def run(script,*args):
    subprocess.run([sys.executable,str(HERE/script),*map(str,args)],check=True)


def package():
    optical=json.loads((REVIEW/'audits'/'optical-inventory.json').read_text())
    if list(map(tuple,optical['grid']))!=OPTICAL_GRID:
        raise ValueError('Incomplete reading-size proof')
    magnified=json.loads((REVIEW/'audits'/'thin-reference.json').read_text())
    if tuple(map(tuple,magnified['grid']))!=MAGNIFIED_GRID or magnified['ppem']!=PPEM:
        raise ValueError('Refresh the magnified weight comparisons')
    PACKAGE.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=PACKAGE) as temporary:
        stage=Path(temporary)
        css=[]
        for family in FAMILIES:
            font=OUTPUT/(family+'[wght,wdth,RADI].ttf')
            report=json.loads((REVIEW/'audits'/(family+'.json')).read_text())
            if report['sha256']!=hashlib.sha256(font.read_bytes()).hexdigest() or report['exceptions'] or report.get('default_differences'):
                raise ValueError('Rebuild and audit '+family+' before packaging')
            web=font.with_suffix('.woff2')
            with TTFont(font) as native, TTFont(web) as compressed:
                symbols=family=='AdmiraltySymbols'
                grid=SAMPLES if symbols else LOCATIONS+BETWEEN_MASTERS
                names=report['names'] if symbols else report['glyph_order']
                expected=list(BY_NAME) if symbols else native.getGlyphOrder()
                visual=optical['faces'][family]
                if visual['sha256']!=report['sha256'] or list(visual['glyphs'])!=native.getGlyphOrder():
                    raise ValueError('Refresh the exported-font reading-size proof for '+family)
                if not symbols:
                    large=magnified['faces'][family]
                    peers=reference_names(native)
                    if (large['sha256']!=report['sha256'] or list(large['glyphs'])!=expected
                            or any(row['peers']!=list(peers[n]) or len(row['cells'])!=len(MAGNIFIED_GRID)
                                   for n,row in large['glyphs'].items())):
                        raise ValueError('Refresh the per-glyph magnified proof for '+family)
                if names!=expected or sorted(map(tuple,report['sample_grid']))!=sorted(grid):
                    raise ValueError('Incomplete glyph or axis coverage for '+family)
                tables = ('cmap','GSUB','gvar','fvar','hmtx')
                if not symbols:
                    tables += ('GPOS',)
                for tag in tables:
                    if native.getTableData(tag)!=compressed.getTableData(tag):
                        raise ValueError(f'{family} TTF and WOFF2 differ in {tag}')
                # WOFF2 may re-encode flags and padding. Check the drawing
                # commands as well as the deltas that vary those commands.
                for glyph in native.getGlyphOrder():
                    a,b=native['glyf'][glyph],compressed['glyf'][glyph]
                    match=a.numberOfContours==b.numberOfContours
                    if match and a.isComposite():
                        match=([c.getComponentInfo() for c in a.components]
                               ==[c.getComponentInfo() for c in b.components])
                    elif match and a.numberOfContours:
                        match=(a.coordinates==b.coordinates and a.endPtsOfContours==b.endPtsOfContours
                               and [f&1 for f in a.flags]==[f&1 for f in b.flags])
                    if not match:
                        raise ValueError(f'{family} TTF and WOFF2 differ in {glyph}')
                with TTFont(PACKAGE.parent/(family+'[wght].ttf'),lazy=True) as release:
                    version=release['head'].fontRevision
                    version_name=release['name'].getDebugName(5)
                for artifact in (native,compressed):
                    names=artifact['name']
                    unique=fullrange_unique_id(artifact,names.getDebugName(6))
                    values={(r.nameID,r.toUnicode()) for r in names.names if r.nameID in (3,5)}
                    if artifact['head'].fontRevision!=version or values!={(3,unique),(5,version_name)}:
                        raise ValueError(f'{family} version does not match its release source')
                name=native['name'].getDebugName(16) or native['name'].getDebugName(1)
            for source in (font,web):
                shutil.copyfile(source,stage/source.name)
            italic='italic' if family.endswith('-Italic') else 'normal'
            css.append(f"""@font-face {{
  font-family: '{name}';
  src: url('./{web.name}') format('woff2');
  font-weight: 100 900;
  font-stretch: 65% 150%;
  font-style: {italic};
  font-display: swap;
}}""")
        (stage/'admiralty-fullrange.css').write_text('\n\n'.join(css)+'\n')
        for source in sorted(stage.iterdir()):
            os.replace(source,PACKAGE/source.name)
    print(f'{len(FAMILIES)} variable fonts, TTF and WOFF2, in {PACKAGE}')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-checked',action='store_true',help='Package already audited binaries')
    parser.add_argument('--workers',type=int,default=3)
    args=parser.parse_args()
    if not args.package_checked:
        run('build_word_proof.py')
        run('build_axis_study.py')
        run('check_word_proof.py')
        run('check_axis_study.py')
        run('build_text_family.py')
        run('build_symbol_family.py','--workers',args.workers)
        for family in TEXT:
            run('audit_text_family.py',family,'--strict','--out',REVIEW/'audits'/(family+'.json'))
        run('audit_symbol_family.py','--strict','--workers',args.workers)
        run('check_text_layout.py')
        run('check_period.py', *(OUTPUT / (family + '[wght,wdth,RADI].ttf') for family in TEXT))
        run('check_punctuation.py', OUTPUT)
        run('check_serif_t.py')
        run('check_serif_letters.py')
        run('check_optical_inventory.py')
        run('check_thin_reference.py')
        run('check_cross_heavy.py')
        run('check_junctions.py')
        run('check_bowl_joins.py', *(OUTPUT / (family + '[wght,wdth,RADI].ttf') for family in TEXT))
        run('check_figure_cuts.py', *(OUTPUT / (family + '[wght,wdth,RADI].ttf') for family in TEXT))
        run('check_zero_radius.py')
        run('magnified_audit.py')
        run('build_family_proof.py')
    package()


if __name__=='__main__':
    main()
