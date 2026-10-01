#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integrate the team's Part 3 into the main team notebook in 10 LOCAL Git commits.

Run from the root of audomsak-pypy/Project1-Text_Analytics69 in the
`sukanya` branch. Nothing in this program calls `git push` or writes remotely.
"""
import copy
import json
import re
import subprocess
import sys
import uuid
from pathlib import Path

TARGET_NAME = 'Project1_Text_Analytics69_Teams.ipynb'
SOURCE_NAME = 'Project1_Text_Analytics69_Teams_Part3.ipynb'


def git(*args, check=True):
    return subprocess.run(['git', *args], check=check, text=True,
                          capture_output=True)


def source(cell):
    s = cell.get('source', [])
    return ''.join(s) if isinstance(s, list) else s


def new_cell(typ, content):
    c = {'cell_type': typ, 'id': uuid.uuid4().hex[:8], 'metadata': {}, 'source': content.splitlines(True)}
    if typ == 'code':
        c.update(execution_count=None, outputs=[])
    return c


def sanitized_cell_update(cell, replacement):
    cell.clear()
    cell.update(replacement)


def notebook(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    if 'cells' not in data:
        raise ValueError('Expected Jupyter notebook JSON with cells')
    return data


def save(data, path):
    # Keep original pre-existing cells/outputs and top-level metadata.
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write('\n')


def find_heading(data, regex, begin=0):
    for i in range(begin, len(data['cells'])):
        c = data['cells'][i]
        if c['cell_type'] == 'markdown' and re.search(regex, source(c), re.I | re.M):
            return i
    return None


def replace_section(data, section_regex, cells):
    idx = find_heading(data, section_regex)
    if idx is None:
        raise ValueError('Missing heading: '+section_regex)
    j = idx+1
    while j < len(data['cells']):
        c = data['cells'][j]
        if c['cell_type'] == 'markdown' and re.match(r'^\s*#{2,3}\s+3\.[1-4]\b', source(c)):
            break
        if c['cell_type'] == 'markdown' and re.match(r'^\s*#\s+(เกณฑ์การให้คะแนน|เสร็จแล้ว)', source(c)):
            break
        j += 1
    data['cells'][idx+1:j] = cells


def commit(data, path, message):
    save(data, path)
    # stdlib validation + verify round trip and valid Python code cells separately
    parsed = notebook(path)
    assert parsed['nbformat'] == 4
    assert len(parsed['cells']) == len(data['cells'])
    for c in parsed['cells']:
        assert c['cell_type'] in ('markdown', 'code', 'raw')
    git('add','--',path.name)
    git('-c','user.name=sukanya-ggez','-c','user.email=298513670+sukanya-ggez@users.noreply.github.com', 'commit','-m', message, '--',path.name)
    print('[LOCAL COMMIT]', message)


def main():
    root = Path.cwd()
    if git('rev-parse','--is-inside-work-tree').stdout.strip() != 'true':
        raise RuntimeError('Please run from inside the Git repository')
    branch = git('branch','--show-current').stdout.strip()
    if branch != 'sukanya':
        raise RuntimeError(f'STOP: current branch is {branch!r}; must be sukanya')
    if root.name != 'Project1-Text_Analytics69' and not (root / TARGET_NAME).is_file():
        raise RuntimeError('Please run from the repository root containing the team notebook')
    path = root / TARGET_NAME
    if not path.is_file():
        raise FileNotFoundError('Main notebook not found: '+TARGET_NAME)
    dirty = git('status','--porcelain','--',TARGET_NAME).stdout.strip()
    if dirty:
        raise RuntimeError('STOP: main notebook has uncommitted changes. Commit/stash them first to avoid mixing or losing work.')
    if (root / SOURCE_NAME).is_file():
        other = notebook(root / SOURCE_NAME)
        origin = 'local Part3 file (existing Codespace copy)'
    else:
        # Fall back to the known Part3 notebook on teammate's branch.
        # `git fetch` only downloads refs; it NEVER pushes or modifies the branch.
        cmd = git('show', f'origin/toto:{SOURCE_NAME}', check=False)
        if cmd.returncode:
            cmd = git('show', f'toto:{SOURCE_NAME}', check=False)
        if cmd.returncode:
            print('Part3 missing locally; fetching the known teammate branch (read only)...')
            git('fetch','--no-tags','origin','toto')
            cmd = git('show',f'FETCH_HEAD:{SOURCE_NAME}',check=False)
        if cmd.returncode:
            raise FileNotFoundError('Cannot find Part3 file locally or on toto branch. '+cmd.stderr)
        other = json.loads(cmd.stdout)
        origin = 'origin/toto Part3 file (read only)'
    main = notebook(path)
    a = find_heading(main,r'^\s*#\s*Part\s*3\s*:')
    b = find_heading(main,r'^\s*#\s*เกณฑ์การให้คะแนน')
    c = find_heading(other,r'^\s*#\s*Part\s*3\s*:')
    d = find_heading(other,r'^\s*#\s*เกณฑ์การให้คะแนน')
    if c is None or d is None:
        raise ValueError('Part3 source lacks expected Part3 or Rubric headings')
    if a is None:
        if b is None:
            raise ValueError('Main notebook lacks Part3 and Rubric anchors: stop to preserve original')
        a = b
    if b is None:
        b = len(main['cells'])
    if b < a:
        raise ValueError('Unexpected notebook layout (rubric precedes Part3)')
    # Backup is intentionally an untracked, uncommitted local file.
    backup = Path(git('rev-parse','--git-path','part3-main-before-merge.ipynb').stdout.strip())
    if not backup.is_absolute():
        backup = root / backup
    backup.parent.mkdir(parents=True, exist_ok=True)
    if backup.exists():
        raise FileExistsError('Backup already exists; please review before rerunning: '+str(backup))
    backup.write_bytes(path.read_bytes())
    # 1/10: put the already existing Part3 work into the MAIN notebook.
    main['cells'][a:b] = copy.deepcopy(other['cells'][c:d])
    commit(main, path, 'part3 01/10 integrate existing team Part3 into main notebook')

    # 2/10: preserve source and clarify the scope of claims.
    q31 = find_heading(main,r'^\s*###\s*3\.1\s')
    meta = new_cell('markdown', '''#### วัตถุประสงค์และหน่วยวิเคราะห์ (การปรับปรุงงานกลุ่ม)

- **แหล่งที่มา:** บทความข่าวที่หน้า Thai PBS หมวดการเมืองและหน้าข่าวรอบวันย้อนหลังเชื่อมถึงได้ (หลังขยายแล้วครอบคลุมหลายหมวด ไม่ใช่เฉพาะข่าวการเมือง และไม่ใช่ตัวแทนข่าวทุกสำนัก)
- **คำถามเชิงพรรณนา:** ใน *ชุดบทความที่เก็บได้* มีสัดส่วนข่าวที่กล่าวถึงแต่ละหมวดคำสำคัญเท่าใด และสัดส่วนเปลี่ยนตามสัปดาห์หรือไม่?
- **ผู้ใช้ผล:** ทีมวิเคราะห์คอนเทนต์/กองบรรณาธิการ เพื่อตรวจสอบความครอบคลุมหัวข้อในชุดข้อมูล
- **หน่วยวิเคราะห์:** 1 record = 1 บทความข่าวจริงที่มี URL, ชื่อเรื่อง, วันเผยแพร่ และเนื้อหาผ่านเกณฑ์
- **วิธีเก็บหนึ่งวิธี:** Web Robot (Requests + BeautifulSoup) โดยตรวจ robots.txt และพักระหว่างคำขอ
- **ผลที่สรุปไม่ได้:** ความเห็น/อารมณ์/ความนิยมของประชาชน หรือแนวโน้มของสื่อทุกสำนักจากข้อมูลเว็บไซต์เดียว

**ข้อสำคัญ:** ฉบับทดลองเดิมมี 17 valid records ซึ่ง **ต่ำกว่าเกณฑ์อย่างน้อย 200 records** ต้องเก็บเพิ่มและคำนวณผลจริงใหม่ ไม่ใช้เปอร์เซ็นต์ 88.2% เป็นผลของชุดใหม่
''')
    main['cells'].insert(q31+1, meta)
    commit(main,path,'part3 02/10 define question unit of analysis and inference limits')

    # 3/10: configure ethical collection and disable unrelated demo API calls.
    for cell in main['cells']:
        if 'rows = fetch_hackernews(50)' in source(cell):
            sanitized_cell_update(cell, new_cell('markdown','> ตัวอย่าง Hacker News API ของใบงานถูกปิดการรัน: งานกลุ่มนี้เลือกเก็บเพียง **Web Robot – Thai PBS** เท่านั้น\n'))
        if cell['cell_type'] == 'code' and 'MAX_ARTICLES = 20' in source(cell):
            sanitized_cell_update(cell, new_cell('code', '''# Part 3 — Web Robot config (one source/one method)
import re, time, requests, pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.robotparser import RobotFileParser
BASE_URL = 'https://www.thaipbs.or.th'
LISTING_URL = BASE_URL + '/news/politics'
ARTICLE_PATH_PATTERN = r'^/news/content/\\d+$'
MIN_VALID_RECORDS = 200
MAX_LISTING_PAGES = 40
MAX_ARCHIVE_DAYS = 60      # permitted day-indexed news/archive pages
MAX_ARTICLES = 350          # เก็บเผื่อการตัด invalid / duplicate
DELAY = 1.5                # seconds between requests
BOT_USER_AGENT = 'KKU-TextAnalytics-StudentBot/1.0 (education; respects robots.txt)'
session = requests.Session()
session.headers.update({'User-Agent': BOT_USER_AGENT})
RANDOM_SEED = 42
print('Source:', LISTING_URL, '| required valid records:', MIN_VALID_RECORDS)
'''))
        if cell['cell_type'] == 'code' and 'def robots_allowed(' in source(cell):
            sanitized_cell_update(cell, new_cell('code', '''# Ethical / fail-closed robots checking: no bypassing access controls
_robots_cache = {}
def normalize_url(url):
    return urldefrag(url)[0].rstrip('/')
def robots_allowed(url, user_agent=BOT_USER_AGENT):
    parsed = urlparse(url)
    root = f'{parsed.scheme}://{parsed.netloc}'
    if parsed.scheme != 'https' or parsed.netloc != urlparse(BASE_URL).netloc:
        return False
    if root not in _robots_cache:
        try:
            response = session.get(root + '/robots.txt', timeout=20)
            if response.status_code != 200:
                _robots_cache[root] = None
            else:
                rp = RobotFileParser()
                rp.parse(response.text.splitlines())
                _robots_cache[root] = rp
        except requests.RequestException:
            _robots_cache[root] = None
    rp = _robots_cache[root]
    return bool(rp is not None and rp.can_fetch(user_agent,url))
print('Robots permission for listing:',robots_allowed(LISTING_URL))
if not robots_allowed(LISTING_URL):
    raise PermissionError('robots.txt unavailable/disallows this page: switch to an authorized source; do not bypass')
'''))
    commit(main,path,'part3 03/10 configure single-source collector and robots safeguards')

    # 4/10: discovery with pagination and duplicate URL filtering.
    for cell in main['cells']:
        if cell['cell_type']=='code' and 'def find_article_links(' in source(cell):
            sanitized_cell_update(cell, new_cell('code', '''# Step 3: targeted discovery from news/politics and its pagination (no generic crawl)
def find_article_links(listing_url):
    if not robots_allowed(listing_url):
        raise PermissionError('Disallowed listing URL: ' + listing_url)
    response = session.get(listing_url,timeout=25)
    response.raise_for_status()
    soup = BeautifulSoup(response.text,'html.parser')
    found = set()
    for a in soup.find_all('a',href=True):
        url = normalize_url(urljoin(listing_url,a['href']))
        p = urlparse(url)
        if p.netloc == urlparse(BASE_URL).netloc and re.fullmatch(ARTICLE_PATH_PATTERN,p.path):
            found.add(url)
    return found

article_urls, no_new_pages = set(), 0
for page_no in range(1,MAX_LISTING_PAGES+1):
    page_url = LISTING_URL if page_no == 1 else f'{LISTING_URL}?page={page_no}'
    try:
        page_links = find_article_links(page_url)
    except (requests.RequestException,PermissionError) as exc:
        print('Stopping listing:',type(exc).__name__,str(exc)[:120]); break
    fresh = page_links - article_urls
    article_urls.update(fresh)
    print('listing',page_no,'new links',len(fresh),'unique links',len(article_urls))
    no_new_pages = 0 if fresh else no_new_pages + 1
    if len(article_urls) >= MAX_ARTICLES or no_new_pages >= 3: break
    time.sleep(DELAY)
# If one landing page exposes too few links, use public *daily news archive* pages.
# This BROADENS the sampling frame to ALL news categories; reflect that in analysis.
from datetime import datetime, timezone, timedelta
archive_pages_visited = 0
if len(article_urls) < MAX_ARTICLES:
    for days_back in range(MAX_ARCHIVE_DAYS):
        day = (datetime.now(timezone.utc).date() - timedelta(days=days_back)).isoformat()
        archive_url = f'{BASE_URL}/news/archive/{day}'
        if not robots_allowed(archive_url):
            print('Archive not permitted or robots unavailable; stopping at', day)
            break
        try:
            discovered = find_article_links(archive_url)
        except requests.RequestException as exc:
            print('Archive request failed; stopping:', type(exc).__name__)
            break
        archive_pages_visited += 1
        article_urls.update(discovered)
        print('archive', day, 'unique candidates', len(article_urls))
        if len(article_urls) >= MAX_ARTICLES: break
        time.sleep(DELAY)
print('archive pages visited:',archive_pages_visited)
article_urls = sorted(article_urls)
print('Discovered distinct candidate URLs:',len(article_urls))
if len(article_urls)<MIN_VALID_RECORDS:
    print('WARNING: discovery below 200. Pagination may be dynamic; do NOT report completion until actual valid n>=200.')
'''))
    commit(main,path,'part3 04/10 discover article links across listing pages with deduplication')

    # 5/10: robust article extraction with Thai token counts.
    for cell in main['cells']:
        if cell['cell_type']=='code' and 'def extract_article(' in source(cell):
            sanitized_cell_update(cell, new_cell('code', '''# Step 4: extract actual article body. Thai word count uses PyThaiNLP.
from pythainlp.tokenize import word_tokenize
from urllib.parse import urlparse
from hashlib import sha256

def extract_article(url):
    if not robots_allowed(url):
        return None
    r = session.get(url,timeout=25)
    r.raise_for_status()
    soup=BeautifulSoup(r.text,'html.parser')
    h1=soup.find('h1')
    title=h1.get_text(' ',strip=True) if h1 else ''
    meta=soup.find('meta',attrs={'property':'article:published_time'})
    t=soup.find('time')
    published=(meta.get('content') if meta else '') or ((t.get('datetime') or t.get_text(' ',strip=True)) if t else '')
    body=soup.find('article') or soup.find('main')
    if body is None: return None
    for trash in body.find_all(['script','style','nav','footer','aside']):trash.decompose()
    paras=[p.get_text(' ',strip=True) for p in body.find_all('p')]
    text=' '.join(p for p in paras if len(p)>=30).strip()
    words=[w for w in word_tokenize(text,engine='newmm') if w.strip()]
    return {'doc_id':urlparse(url).path.rsplit('/',1)[-1], 'url':normalize_url(url),
            'title':title,'published_at':published,'text':text,'word_count':len(words),
            'source_domain':urlparse(url).netloc,'text_hash':sha256(text.encode('utf-8')).hexdigest()}
'''))
    commit(main,path,'part3 05/10 extract article metadata and tokenize Thai content')

    # 6/10: collection and local raw persistence; don't overwrite unrelated source files.
    for cell in main['cells']:
        if cell['cell_type']=='code' and 'def collect_articles(' in source(cell):
            sanitized_cell_update(cell, new_cell('code', '''# Step 5: collect, throttle requests and save raw evidence locally
import json
from pathlib import Path
attempted_urls=[]
collection_errors=[]
rows=[]
for i,url in enumerate(article_urls[:MAX_ARTICLES],1):
    attempted_urls.append(url)
    try:
        item=extract_article(url)
        if item is not None: rows.append(item)
        else: collection_errors.append({'url':url,'reason':'not allowed / invalid article layout'})
    except requests.RequestException as exc:
        collection_errors.append({'url':url,'reason':type(exc).__name__})
    finally:
        time.sleep(DELAY)
    if i%25==0: print('attempted=',i,'extracted=',len(rows))
print('attempted:',len(attempted_urls),'extracted:',len(rows),'failures:',len(collection_errors))
with open('corpus.jsonl','w',encoding='utf-8') as f:
    for record in rows: f.write(json.dumps(record,ensure_ascii=False)+'\\n')
print('Saved raw corpus.jsonl for audit and reruns')
'''))
        # remove old Step6/7 cells (they refer to df_robot/corp_final of old 17-record pipeline)
    for cell in main['cells']:
        if cell['cell_type']=='code' and ('df_robot = pd.DataFrame(rows)' in source(cell) or 'corp_final = corp_cleaned' in source(cell)):
            sanitized_cell_update(cell, new_cell('markdown','> **ขั้นตอนตรวจคุณภาพและบันทึกข้อมูล (Step 6–7):** ใช้กระบวนการที่แก้ไขในข้อ **3.2** ด้านล่างแทน เพื่อให้รายงานการตัดข้อมูลไม่ซ้ำซ้อน\n'))
    commit(main,path,'part3 06/10 collect with delay and persist raw jsonl corpus')

    # 7/10: sequential mutually exclusive quality counts (no double counts).
    q32_code = '''# 3.2 Data Quality: each exclusion reason counted ONCE, in sequence
import pandas as pd
from pathlib import Path
raw_path = Path('corpus.jsonl')
if not raw_path.exists() or raw_path.stat().st_size == 0:
    raise RuntimeError('No raw corpus.jsonl available. Run 3.1 collection or check robots/access first.')
raw = pd.read_json(raw_path,lines=True,dtype={'doc_id':'string'})
raw_count = len(raw)
required = ['url','title','text','published_at','word_count','source_domain']
for col in required:
    if col not in raw.columns: raw[col] = pd.NA
work = raw.copy()
ledger=[]
def filter_and_count(reason,bad):
    global work
    removed=int(bad.fillna(False).sum())
    ledger.append({'exclusion':reason,'removed':removed})
    work=work.loc[~bad.fillna(False)].copy()

filter_and_count('duplicate url',work.duplicated('url',keep='first'))
filter_and_count('duplicate text',work.duplicated('text',keep='first'))
missing=work[['url','title','text','published_at']].isna().any(axis=1)
for field in ['url','title','text','published_at']:
    missing |= work[field].fillna('').astype(str).str.strip().eq('')
filter_and_count('missing required fields',missing)
work['published_at_parsed']=pd.to_datetime(work['published_at'],errors='coerce',utc=True)
filter_and_count('invalid date',work['published_at_parsed'].isna())
work['word_count']=pd.to_numeric(work['word_count'],errors='coerce')
filter_and_count('too short (<80 Thai tokens)',work['word_count'].fillna(0).lt(80))
work=work.reset_index(drop=True)
valid_n=len(work)
assert raw_count == valid_n + sum(row['removed'] for row in ledger)
quality_report=pd.DataFrame(ledger)
print('attempted URLs:',len(attempted_urls) if 'attempted_urls' in globals() else 'not recorded (reused raw corpus)')
print('successfully extracted rows:',raw_count)
print('removed total:',raw_count-valid_n)
print(quality_report.to_string(index=False))
print('FINAL valid corpus:',valid_n,'target:',MIN_VALID_RECORDS)
'''
    replace_section(main,r'^\s*###\s*3\.2\b',[new_cell('markdown','#### 3.2 — Sequential Data Quality Audit\n\nตัด URL ซ้ำ → เนื้อหาซ้ำ → missing → วันที่อ่านไม่ได้ → ข่าวสั้นผิดปกติ ตามลำดับเดียวกัน เพื่อไม่ให้นับ record เดียวซ้ำหลายเหตุผล\n'),new_cell('code',q32_code)])
    commit(main,path,'part3 07/10 audit duplicates missing dates and short records')

    # 8/10: final provenance coverage and minimum n gate.
    q32_ix=find_heading(main,r'^\s*###\s*3\.2\b')
    q33_ix=find_heading(main,r'^\s*###\s*3\.3\b')
    main['cells'][q33_ix:q33_ix]=[
        new_cell('code', '''# 3.2 Save final analytical corpus and document source/date coverage
work=work.copy()
work['date_utc']=work['published_at_parsed'].dt.date.astype(str)
work.to_json('corpus_cleaned.jsonl',orient='records',lines=True,force_ascii=False,date_format='iso')
print('Source coverage (domain):')
print(work['source_domain'].value_counts(dropna=False).to_string())
print('Date span UTC:',work['published_at_parsed'].min(), 'to',work['published_at_parsed'].max())
print('Distinct article URLs:',work['url'].nunique(),'| missing columns:',work[required].isna().sum().to_dict())
print('Random manual spot-check of 10 article headlines and URLs:')
if valid_n:
    print(work[['title','url','word_count','date_utc']].sample(min(10,valid_n),random_state=RANDOM_SEED).to_string(index=False))
if valid_n < MIN_VALID_RECORDS:
    raise RuntimeError(f'Not yet compliant: {valid_n} valid records; need at least {MIN_VALID_RECORDS}. Expand permitted listing/archive pages and rerun. Do not invent records.')
print('PASS: minimum valid analytical records satisfied')
''')]
    commit(main,path,'part3 08/10 report corpus coverage save final and enforce minimum 200')

    # 9/10: keyword mention share and temporal distribution; avoid public opinion inference.
    q33_md = '''#### 3.3 — เทคนิคที่เลือกและข้อจำกัด

ใช้ **(1) การนับสัดส่วนบทความที่กล่าวถึงคำสำคัญ** จากพาดหัวข่าว และ **(2) แนวโน้มจำนวนข่าวรายสัปดาห์** บนชุดที่ผ่านเกณฑ์ โดยไม่ใช้ Sentiment เป็นตัวแทนความคิดเห็นของผู้อ่าน

- ข่าวเดียวกันอาจกล่าวถึงได้หลายหมวด ดังนั้นผลรวมเปอร์เซ็นต์ทุกหมวด **อาจเกิน 100%**
- รูปแบบคำค้นเป็นการจัดหมวดแบบ heuristic ควรตรวจพาดหัวที่ตรง/ไม่ตรงด้วยตา
- กราฟสะท้อนเพียง **บทความในตัวอย่างที่เก็บจริง** ไม่ใช่ความเห็นของประชาชน ไม่ใช่ความนิยมเชิงเลือกตั้ง
'''
    q33_code = '''# 3.3 descriptive content analysis with transparent denominators
import re
import matplotlib.pyplot as plt
import pandas as pd
analysis=pd.read_json('corpus_cleaned.jsonl',lines=True)
analysis['published_at_parsed']=pd.to_datetime(analysis['published_at'],utc=True,errors='coerce')
assert len(analysis) >= MIN_VALID_RECORDS
n=len(analysis)
patterns={
  'กฎหมายและศาล':r'ศาลรัฐธรรมนูญ|รัฐธรรมนูญ|คำวินิจฉัย|กฎหมาย',
  'การเลือกตั้ง':r'การเลือกตั้ง|กกต\\.?|สมาชิกวุฒิสภา|วุฒิสภา|อบจ\\.?',
  'เศรษฐกิจและงบประมาณ':r'งบประมาณ|เศรษฐกิจ|ดิจิทัลวอลเล็ต',
  'ความมั่นคงและชายแดน':r'ชายแดน|ความมั่นคง|ปัตตานี|ยะลา|นราธิวาส',
}
# Count unique articles mentioning any keyword in TITLE (not repeated token occurrences).
matches=pd.DataFrame({k:analysis['title'].fillna('').astype(str).str.contains(p,regex=True,flags=re.I) for k,p in patterns.items()})
counts=matches.sum().sort_values(ascending=True)
keyword_table=pd.DataFrame({'articles':counts.astype(int),'share_percent':(100*counts/n).round(1)})
print('n =',n,'| multiple labels allowed, percentages need not sum to 100%')
print(keyword_table.to_string())
fig,ax=plt.subplots(figsize=(10,5))
ax.barh(list(counts.index),counts.values)
ax.set_xlim(0,max(1,int(counts.max())*1.18));ax.set_xlabel('Number of articles')
ax.set_title('Thai PBS sampled articles: headline topic mentions (n='+str(n)+')')
for i,v in enumerate(counts.values):ax.text(v+max(1,n*.005),i,f'{v} ({v/n:.1%})',va='center')
fig.tight_layout();plt.show()
weekly=analysis.groupby(analysis['published_at_parsed'].dt.to_period('W').astype(str)).size().sort_index()
print('Article counts by week:'); print(weekly.to_string())
if len(weekly)>1:
    fig,ax=plt.subplots(figsize=(9,4))
    weekly.plot(ax=ax,marker='o')
    ax.set_title('Articles in sampled corpus by publication week')
    ax.set_xlabel('Publication week (UTC)');ax.set_ylabel('Articles')
    ax.tick_params(axis='x',rotation=35);fig.tight_layout();plt.show()
print('Check category matches manually:')
for category in patterns:
    subset=analysis.loc[matches[category],'title']
    print('\\n',category,':',subset.head(3).to_list())
'''
    replace_section(main,r'^\s*###\s*3\.3\b',[new_cell('markdown',q33_md),new_cell('code',q33_code)])
    commit(main,path,'part3 09/10 add evidence-backed topic counts charts and weekly trend')

    # 10/10: evidence-driven card using dynamically calculated n, not fabricated figures.
    q34_md='''#### 3.4 — Insight Card (generate from actually collected records)

Insight Card ด้านล่างคำนวณจาก corpus ที่สะอาดจริงทุกครั้ง ไม่มีการใส่เปอร์เซ็นต์ของตัวอย่างเดิม 17 ข่าวเป็นผลของข้อมูลชุดใหม่ และแยก **หัวข้อที่สำนักข่าวเผยแพร่** ออกจาก **ความเห็นของผู้อ่าน** อย่างชัดเจน
'''
    q34_code='''# Reproducible descriptive insight card (no claims about voter/public sentiment)
leading=keyword_table.sort_values('articles',ascending=False).iloc[0]
leading_name=keyword_table.sort_values('articles',ascending=False).index[0]
print('INSIGHT: Among n={} sampled Thai PBS articles, {:d} ({:.1f}%) headlines mention [{}].'.format(
    n,int(leading['articles']),leading['share_percent'],leading_name))
print('EVIDENCE: keyword_table + headline-topic bar chart; articles may have multiple labels.')
print('SO WHAT: A content analyst can compare this category coverage within the collected period; this is not a measure of public demand or opinion.')
print('ACTION: Content analytics team should manually audit 10 randomly selected headline classifications, check period coverage and repeat weekly with the same definitions; track misclassification rate and share by week.')
print('CONFIDENCE: Limited to one source, selected political/archive listing pages (archive mixes news categories), keyword heuristics and sample dates; requires manual validation.')
print('AI USAGE: AI assisted code and text drafting; team must verify robots permission, real data counts, sample titles, charts and interpretations before submission.')
'''
    replace_section(main,r'^\s*###\s*3\.4\b',[new_cell('markdown',q34_md),new_cell('code',q34_code)])
    commit(main,path,'part3 10/10 complete dynamic insight card limitations and AI disclosure')

    print('\\nSUCCESS: 10 LOCAL commits completed on branch sukanya. NO PUSH performed.')
    print('Source used:',origin)
    print('Main notebook:',path)
    print('Backup:',backup)
    print('Run Part3 cells in Jupyter to collect real records and validate n >= 200.')
    print('git status:',git('status','--short').stdout.strip() or 'clean')

if __name__=='__main__':
    try:
        main()
    except Exception as exc:
        print('ERROR:',str(exc),file=sys.stderr)
        sys.exit(1)
