#!/usr/bin/env python3
"""Merge the existing Part 3.1 notebook into the team notebook and fill in 3.2--3.3.

Run in your Codespace repository root, without pushing to GitHub.
Preserves the existing Part 1/2 cells and creates a backup of the original.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys

MAIN = Path('Project1_Text_Analytics69_Teams.ipynb')
PART3 = Path('Project1_Text_Analytics69_Teams_Part3.ipynb')
BACKUP = Path('Project1_Text_Analytics69_Teams.before_Part3_merge.bak.ipynb')

QC_CODE = r'''# 3.2 Data Quality Check — ทำต่อจาก DataFrame df ในข้อ 3.1
import pandas as pd
import re
import html
from pathlib import Path

# การรวบรวมข้อมูลจาก 3.1 ต้องรันสำเร็จก่อน (หรือใช้ corpus.jsonl ที่บันทึกไว้)
if 'df' not in globals() or not isinstance(df, pd.DataFrame):
    if Path('corpus.jsonl').exists():
        df = pd.read_json('corpus.jsonl', lines=True)
        print('ใช้ข้อมูลจาก corpus.jsonl ที่บันทึกไว้')
    else:
        raise RuntimeError('กรุณารัน 3.1 เพื่อสร้าง df ก่อนรัน 3.2')

required = {'doc_id', 'text', 'score', 'n_comments', 'published_at'}
missing_cols = required - set(df.columns)
if missing_cols:
    raise KeyError(f'คอลัมน์จาก API ไม่ครบ: {sorted(missing_cols)}')

initial_count = len(df)
work = df.copy()

# ตั้งรูปแบบ field ให้แน่นอน เพื่อให้การนับ Missing / Duplicate ไม่คลาดเคลื่อน
work['doc_id'] = work['doc_id'].astype('string').str.strip()
work['text'] = work['text'].astype('string').map(
    lambda x: html.unescape(re.sub(r'<[^>]*>', ' ', x)) if pd.notna(x) else x,
    na_action='ignore'
).str.replace(r'\s+', ' ', regex=True).str.strip()
for col in ['doc_id', 'text']:
    work[col] = work[col].replace(['', 'None', 'nan'], pd.NA)

# 1) Missing ในคีย์ระบุตัวโพสต์และหัวข้อข่าว
before = len(work)
work = work.dropna(subset=['doc_id', 'text']).copy()
missing_removed = before - len(work)

# 2) โพสต์ซ้ำด้วย doc_id (1 record = 1 HN story)
before = len(work)
work = work.drop_duplicates(subset=['doc_id']).copy()
duplicate_id_removed = before - len(work)

# 3) หัวข้อข่าวซ้ำ (ป้องกันเรื่องเดียวกันถูกเก็บหลายโพสต์)
work['_normalized_text'] = (work['text'].str.casefold()
                            .str.replace(r'\W+', ' ', regex=True).str.strip())
before = len(work)
work = work.drop_duplicates(subset=['_normalized_text']).copy()
duplicate_text_removed = before - len(work)

# 4) กรองหัวข้อสั้นผิดปกติ โดยดูจำนวนตัวอักษร
before = len(work)
work = work[work['text'].str.len() >= 15].copy()
short_removed = before - len(work)

# 5) แปลงชนิดข้อมูล; ค่าตัวเลขที่ไม่มีจริงไม่ถือว่าเป็นศูนย์โดยอัตโนมัติ
for col in ['score', 'n_comments']:
    work[col] = pd.to_numeric(work[col], errors='coerce')
work['published_at'] = pd.to_datetime(work['published_at'], errors='coerce', utc=True)
metrics_missing = work[['score', 'n_comments']].isna().sum().to_dict()
negative_metrics = int(((work['score'] < 0) | (work['n_comments'] < 0)).fillna(False).sum())
work = work[~((work['score'] < 0) | (work['n_comments'] < 0)).fillna(False)].copy()

corp = work.drop(columns=['_normalized_text']).reset_index(drop=True)
final_count = len(corp)
removed_total = missing_removed + duplicate_id_removed + duplicate_text_removed + short_removed + negative_metrics
assert initial_count - removed_total == final_count, 'ตรวจสอบจำนวนที่ตัดออกอีกครั้ง'
assert not corp['doc_id'].duplicated().any()
assert not corp['text'].isna().any()

# บันทึกข้อมูลที่ clean แล้ว ไม่ต้องเก็บข้อมูลใหม่เพื่อวิเคราะห์ 3.3
corp.to_json('corpus.jsonl', orient='records', lines=True,
             force_ascii=False, date_format='iso')
print('บันทึกไฟล์ corpus.jsonl เรียบร้อย')
'''

QC_REPORT = r'''# 3.2 รายงานจำนวนที่ตรวจสอบและขอบเขตข้อมูล
report = pd.DataFrame({
    'รายการตรวจคุณภาพ': [
        'API records ที่เก็บมา (ก่อน clean)',
        'ตัด Missing doc_id / title',
        'ตัด Duplicate doc_id',
        'ตัด Duplicate title',
        'ตัดข้อความสั้นกว่า 15 ตัวอักษร',
        'ตัดค่าการมีส่วนร่วมติดลบ',
        'Final corpus (หลัง clean)',
    ],
    'จำนวน records': [
        initial_count, missing_removed, duplicate_id_removed,
        duplicate_text_removed, short_removed, negative_metrics, final_count,
    ]
})
display(report)
print('จำนวนข้อมูลการมีส่วนร่วมที่ขาดหาย (เก็บไว้เป็น NaN):', metrics_missing)
if corp['published_at'].notna().any():
    start = corp['published_at'].min().date()
    end = corp['published_at'].max().date()
    print(f'ช่วงเวลาข้อมูลจริง: {start} ถึง {end} (UTC)')
else:
    print('ไม่พบวันที่ที่แปลงได้')
print('แหล่ง/หัวข้อ: Hacker News ผ่าน Algolia Search API; ค้นด้วยคำว่า politics')
print(f'ข้อกำหนดอย่างน้อย 200 valid records: {"ผ่าน" if final_count >= 200 else "ยังไม่ผ่าน — ต้องเพิ่มข้อมูลจาก API"} ({final_count})')
print('หมายเหตุ: keyword politics อาจพบทั้งข่าว ความเห็น และบทสนทนา ไม่ใช่ข่าวการเมืองทั้งหมด')
'''

INSIGHT_CODE = r'''# 3.3 เทคนิคที่ 1: Frequency / n-gram ตามตัวอย่าง CountVectorizer ของอาจารย์
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer

corp = pd.read_json('corpus.jsonl', lines=True)
corp['text'] = corp['text'].fillna('').astype(str)
corp['n_comments'] = pd.to_numeric(corp['n_comments'], errors='coerce')
corp['score'] = pd.to_numeric(corp['score'], errors='coerce')

# binary=True นับว่าแต่ละคำปรากฏในกี่หัวข้อ ไม่ใช่นับการซ้ำของคำในหัวข้อเดียว
vectorizer = CountVectorizer(stop_words='english', ngram_range=(1, 2),
                             max_features=25, binary=True)
X = vectorizer.fit_transform(corp['text'])
word_freq = (pd.DataFrame({
    'keyword': vectorizer.get_feature_names_out(),
    'n_posts': X.sum(axis=0).A1.astype(int)
}).sort_values(['n_posts', 'keyword'], ascending=[False, True])
  .reset_index(drop=True))
print('ความถี่ของคำ/วลี (จำนวนโพสต์ที่มีคำดังกล่าว)')
display(word_freq.head(12))

# 3.3 เทคนิคที่ 2: เปรียบเทียบการมีส่วนร่วมตามหัวข้ออย่างหยาบ
# เป็นการจัดประเภทจาก keyword ในหัวข้อ ไม่ใช่ classifier ที่ตรวจสอบความแม่นยำแล้ว
CATEGORY_PATTERNS = {
    'Economy / policy': r'\b(economy|economic|inflation|tax|trade|tariff|budget|wages?)\b',
    'Technology / regulation': r'\b(ai|privacy|data|internet|social media|regulation|censor|antitrust|surveillance)\b',
    'International affairs': r'\b(war|foreign|international|diplomac\w*|sanctions?|border|geopolitic\w*)\b',
}

def classify_title(text):
    for category, pattern in CATEGORY_PATTERNS.items():
        if re.search(pattern, str(text), flags=re.IGNORECASE):
            return category
    return 'Other / unclassified'

corp['topic_group'] = corp['text'].map(classify_title)
summary = (corp.groupby('topic_group', as_index=False)
           .agg(n_posts=('doc_id', 'size'),
                comments_observed=('n_comments', 'count'),
                median_comments=('n_comments', 'median'),
                mean_comments=('n_comments', 'mean'),
                median_score=('score', 'median')))
summary['share_of_corpus_pct'] = (100 * summary['n_posts'] / len(corp)).round(1)
summary['mean_comments'] = summary['mean_comments'].round(1)
summary['median_comments'] = summary['median_comments'].round(1)
summary['median_score'] = summary['median_score'].round(1)
print('ตารางเปรียบเทียบแบบพรรณนา: ไม่ใช่การจัดอันดับคุณภาพหรือความสำคัญทางการเมือง')
display(summary)
'''

CHART_CODE = r'''# 3.3 กราฟหลัก: ความถี่คำและจำนวนความคิดเห็นต่อโพสต์ของแต่ละกลุ่มหัวข้อ
# ใช้ label ภาษาอังกฤษบนกราฟเพื่อเลี่ยงปัญหาฟอนต์ภาษาไทยบน matplotlib
plt.figure(figsize=(11, 5))
show = word_freq.head(12).sort_values('n_posts')
plt.barh(show['keyword'], show['n_posts'])
plt.xlabel('Number of posts containing the term')
plt.ylabel('Keyword / bigram')
plt.title('Hacker News posts matched by "politics": term frequency')
plt.tight_layout()
plt.savefig('part3_keyword_frequency.png', dpi=150, bbox_inches='tight')
plt.show()

plt.figure(figsize=(10, 5))
plt.bar(summary['topic_group'], summary['median_comments'].fillna(0))
for i, n in enumerate(summary['n_posts']):
    plt.text(i, summary['median_comments'].fillna(0).iloc[i], f'n={n}',
             ha='center', va='bottom')
plt.xticks(rotation=20, ha='right')
plt.xlabel('Keyword-based topic group')
plt.ylabel('Median comments per post (where available)')
plt.title('Descriptive engagement by topic group')
plt.tight_layout()
plt.savefig('part3_engagement_by_group.png', dpi=150, bbox_inches='tight')
plt.show()
'''

INSIGHT_MARKDOWN = '''**สรุปเพื่อผู้ใช้ผลวิเคราะห์ (Part 3.3)**

- **สิ่งที่พบ:** ดู `word_freq` และ `summary` ที่คำนวณจากข้อมูลจริง เพื่อรายงานคำ/ประเด็นที่ปรากฏ พร้อม `n_posts` และค่ากลางของจำนวนความคิดเห็นในแต่ละกลุ่ม หลีกเลี่ยงการคาดเดาตัวเลขก่อนรัน
- **ความหมายต่อการสื่อสาร:** ตารางช่วยให้ทีมเนื้อหาแยกประเด็นที่มีจำนวนโพสต์มาก ออกจากประเด็นที่มีความคิดเห็นต่อโพสต์มาก โดยไม่ตีความเป็นคุณค่าหรือความถูกต้องทางการเมือง
- **สิ่งที่ควรทำต่อ:** ตรวจหัวข้อด้วยคนอย่างน้อยบางส่วนเพื่อประเมินความถูกต้องของการจัดกลุ่ม keyword; จากนั้นทำการวิเคราะห์ซ้ำในช่วงเวลาเดียวกัน และดูจำนวนโพสต์ควบคู่กับค่าการมีส่วนร่วม
- **ข้อจำกัด:** API query เป็นการค้นคำว่า `politics` ไม่ใช่ตัวแทนของความคิดเห็นประชากร/ชุมชน Tech ทั้งหมด และไม่จำเป็นต้องเป็นข่าวทั้งหมด; HN score/comments เปลี่ยนได้ตามเวลา; ตัวอย่างข้ามปีไม่ควรอธิบายเป็นแนวโน้มปัจจุบัน; การจำแนกด้วย keyword เป็นเพียงเบื้องต้น

> เติม Insight Card ข้อ 3.4 หลังรันและตรวจค่าตัวเลขจริงจากตาราง ไม่สร้างตัวเลขขึ้นเอง'''


def load_nb(path):
    if not path.exists():
        sys.exit(f'ไม่พบไฟล์ {path.name} ในโฟลเดอร์ปัจจุบัน — กรุณาตรวจดู Explorer/แก้ Git conflict ก่อน')
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        sys.exit(f'ไฟล์ {path.name} อ่านเป็น JSON Notebook ไม่ได้: {exc}')
    if not isinstance(data, dict) or not isinstance(data.get('cells'), list):
        sys.exit(f'{path.name} ไม่ใช่ Jupyter Notebook ที่สมบูรณ์')
    return data


def src(cell):
    return ''.join(cell.get('source') or [])


def is_part3(cell):
    s = src(cell)
    return cell.get('cell_type') == 'markdown' and '# Part 3: Data Collection Robot' in s


def is_rubric(cell):
    s = src(cell)
    return cell.get('cell_type') == 'markdown' and '# เกณฑ์การให้คะแนน' in s


def is_section(cell, section):
    s = src(cell).lstrip()
    return cell.get('cell_type') == 'markdown' and s.startswith(f'### {section}')


def new_code(body):
    ast.parse(body)  # detect syntax errors before touching main notebook
    return {
        'cell_type': 'code', 'id': 'p3-' + hashlib.sha1(body.encode()).hexdigest()[:12], 'execution_count': None,
        'metadata': {}, 'outputs': [], 'source': body.splitlines(keepends=True),
    }


def new_markdown(body):
    return {'cell_type': 'markdown', 'id': 'p3-' + hashlib.sha1(body.encode()).hexdigest()[:12], 'metadata': {}, 'source': body.splitlines(keepends=True)}


def main():
    team = load_nb(MAIN)
    part3 = load_nb(PART3)

    starts_team = [i for i, c in enumerate(team['cells']) if is_part3(c)]
    starts_part3 = [i for i, c in enumerate(part3['cells']) if is_part3(c)]
    if len(starts_team) != 1 or len(starts_part3) != 1:
        sys.exit('หา Part 3 header ไม่ตรงหนึ่งตำแหน่งในไฟล์ทั้งคู่: จะไม่แก้ไขไฟล์เพื่อความปลอดภัย')
    start = starts_team[0]
    src_start = starts_part3[0]
    end_candidates = [i for i in range(start + 1, len(team['cells'])) if is_rubric(team['cells'][i])]
    src_end_candidates = [i for i in range(src_start + 1, len(part3['cells'])) if is_rubric(part3['cells'][i])]
    if not end_candidates and not is_section(team['cells'][-1], '3.4'):
        sys.exit('Notebook หลักไม่ได้จบที่ข้อ 3.4')
    if not src_end_candidates and not is_section(part3['cells'][-1], '3.4'):
        sys.exit('Notebook Part3 ไม่พบจุดสิ้นสุดที่ปลอดภัย')
    end = end_candidates[0] if end_candidates else len(team['cells'])
    src_end = src_end_candidates[0] if src_end_candidates else len(part3['cells'])

    chunk = copy.deepcopy(part3['cells'][src_start:src_end])
    for c in chunk:
        if c['cell_type'] == 'code':
            c['execution_count'] = None
            c['outputs'] = []  # avoid falsely showing earlier output as fresh test results

    i32 = next((i for i, c in enumerate(chunk) if is_section(c, '3.2')), None)
    i33 = next((i for i, c in enumerate(chunk) if is_section(c, '3.3')), None)
    i34 = next((i for i, c in enumerate(chunk) if is_section(c, '3.4')), None)
    if None in (i32, i33, i34) or not (i32 < i33 < i34):
        sys.exit('ไม่พบลำดับหัวข้อ 3.2, 3.3, 3.4 — จะไม่เขียนทับโน้ตบุ๊ก')
    new_chunk = (chunk[:i32+1]
                 + [new_code(QC_CODE), new_code(QC_REPORT)]
                 + [chunk[i33]]
                 + [new_code(INSIGHT_CODE), new_code(CHART_CODE), new_markdown(INSIGHT_MARKDOWN)]
                 + chunk[i34:])

    # Preserve all main notebook cells outside Part 3, including Part 1/2 and rubric.
    final = copy.deepcopy(team)
    final['cells'] = team['cells'][:start] + new_chunk + team['cells'][end:]

    if BACKUP.exists():
        sys.exit(f'พบไฟล์สำรองเดิม {BACKUP.name}; กรุณาจัดการไฟล์สำรองก่อนรันซ้ำ')
    shutil.copy2(MAIN, BACKUP)
    temp = MAIN.with_suffix('.merging.tmp')
    try:
        temp.write_text(json.dumps(final, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        json.loads(temp.read_text(encoding='utf-8'))
        temp.replace(MAIN)
    finally:
        if temp.exists():
            temp.unlink()

    print(f'รวม Part 3.1 จาก {PART3.name} และเติม 3.2–3.3 ลง {MAIN.name} สำเร็จ')
    print('Part 1–2 และส่วนอื่นนอก Part 3 ไม่ถูกเปลี่ยนแปลง')
    print(f'สำรองไฟล์เก่าไว้ที่ {BACKUP.name}')
    print('ยังไม่รัน API/Notebook, ยังไม่ commit และยังไม่ push')
    print('เปิด Notebook หลัก แล้ว Run All เพื่อสร้าง corpus.jsonl และกราฟจากข้อมูลจริง')


if __name__ == '__main__':
    main()
