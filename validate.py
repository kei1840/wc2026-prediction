#!/usr/bin/env python3
"""
W杯2026 index.html 定数整合性チェック
コミット前に必ず実行: python3 validate.py
エラーがあれば非ゼロ終了コードで返す
"""
import re, sys

with open('index.html', encoding='utf-8') as f:
    src = f.read()

def extract_array(name):
    m = re.search(rf'const {name}\s*=\s*\[([^\]]*)\]', src, re.DOTALL)
    if not m: return []
    return re.findall(r"'([^']+)'", m.group(1))

def extract_str(name):
    m = re.search(rf'const {name}\s*=\s*[\'"]([^\'"]*)[\'"]', src)
    return m.group(1) if m else ''

b24     = extract_array('CONFIRMED_B24')
b8      = extract_array('CONFIRMED_B8')
out_b8  = extract_array('CONFIRMED_OUT_B8')
sf      = extract_array('CONFIRMED_SF')
out_qf  = extract_array('CONFIRMED_OUT_QF')
out_sf  = extract_array('CONFIRMED_OUT_SF')
champ   = extract_str('CONFIRMED_CHAMP')

# QF winners
qf_matches = re.findall(r"winner:'([^']*)'", src)
qf_winners = [w for w in qf_matches if w]

errors = []

# 1. b8 + out_b8 の合計が b24 と一致
covered = set(b8) | set(out_b8)
missing = [t for t in b24 if t not in covered]
overlap = [t for t in b8 if t in out_b8]
extra   = [t for t in covered if t not in b24]

if missing:  errors.append(f'未分類（b8にもOUT_B8にもない）: {missing}')
if overlap:  errors.append(f'重複（b8とOUT_B8の両方に存在）: {overlap}')
if extra:    errors.append(f'b24外チームがb8/OUT_B8に混入: {extra}')
if len(b8) > 8: errors.append(f'CONFIRMED_B8が8チームを超えている: {len(b8)}チーム')

# 2. QF勝者はb8に含まれるべき
for w in qf_winners:
    if w not in b8:
        errors.append(f'QF勝者がCONFIRMED_B8にない: {w}')

# 3. SF進出チームとQF敗退チームの重複なし
sf_out_overlap = [t for t in sf if t in out_qf]
if sf_out_overlap: errors.append(f'SF進出とQF敗退の両方に存在: {sf_out_overlap}')

# 4. 優勝チームは存在するチームか
if champ and champ not in b8 and champ not in sf:
    errors.append(f'優勝チームがB8/SFにない: {champ}')

# 5. サマリー表示
print(f'b24: {len(b24)}チーム  b8: {len(b8)}チーム  out_b8: {len(out_b8)}チーム  sf: {len(sf)}チーム')
match_msg = f'✅ b24({len(b24)})と一致' if len(b8)+len(out_b8)==len(b24) else '❌ 不一致'
print(f'b8+out_b8={len(b8)+len(out_b8)}  ({match_msg})')
if champ: print(f'優勝: {champ}')

if errors:
    print('\n❌ 整合性エラー:')
    for e in errors:
        print(f'  · {e}')
    sys.exit(1)
else:
    print('\n✅ 整合性OK — コミット可能')
    sys.exit(0)
