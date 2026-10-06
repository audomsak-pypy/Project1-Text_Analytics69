# Project1-Text_Analytics69

# Text Analytics for Business Insight

**วิชาSC663402 Data Warehouse and Big Data Analytics**    ·ทีม *เบื่อเกี้ยวอยากเคี้ยวข้าว*
ส่งงาน: อังคาร 6 ต.ค. 2569 · นำเสนอ: พุธ 7 ต.ค. 2569 (10 นาที + Q&A)

โครงงานนี้เปลี่ยน**ข้อความดิบ**ให้เป็น *ข้อเสนอที่ทีมธุรกิจนำไปทำต่อได้** ใน 2 ส่วน:
**Part 2**  Voice of Customer และ **Part 3**  Data Collection Robot

---

## 1. ภาพรวม

| | Part 2 — Voice of Customer | Part 3 — Data Collection Robot |
|---|---|---|
| **โจทย์** | Brief B3 (ทีม Marketing): ลูกค้าที่ประทับใจพูดถึงอะไร เอาไปทำ Ad Copy / Claim อย่างไร | หัวข้อบน Hacker News กลุ่มใด (จัดด้วย keyword) มี engagement ต่างกันอย่างไร |
| **ข้อมูล** | Amazon Reviews 2023 หมวด `Digital_Music` สุ่ม 20,000 รีวิว | Hacker News Official API (Top Stories 250 รายการ) |
| **1 record คือ** | 1 รีวิว | 1 โพสต์ข่าว |
| **เทคนิค** | Regex Aspect Features, Rate Comparison, Genre Segmentation, Reality Check | Keyword-based Classification, Median Engagement Comparison |
| **ข้อมูลหลังคลีน** | 19,962 รีวิว | 247 โพสต์ (เกณฑ์ ≥ 200 ผ่าน) |
| **ผลลัพธ์หลัก** | Insight Card 2 ใบ | Insight Card 1 ใบ |

---

## 2. ทีมและการแบ่งงาน

| ส่วน | งาน | ผู้รับผิดชอบ |
|---|---|---|
| Part 2 | 2.2 เตรียมข้อมูล,2.4Text Feature,2.5Insight,2.7InsightCard2 | นาวสาวประภาพร กุลโต |
| Part 2 | Text Features | นาวสาวณนัดดา รัตนาตรี |
| Part 3 | 3.2Data Quality,3.3Text Analytics| นาวสาวสุกัญญา อุดมกัน |
| Part 3 |  กำหนดหัวข้อ,แหล่งข้อมูลและวิธีเก็บ| นายอุดมศักดิ์ พระเสนา |
| Part 3 | เพิ่มคำอธิบายcode,outputเเละวิธีนำไปประยุกต์ใช้ | นาวสาวอาทิติญา ชาชัย |
| Part 3 | 3.4Insight Card | นายเยี่ยมภพ ใบโพธิ์ |

---

| ขั้นตอน | Part 2 | Part 3 |
|---|---|---|
| **Extract** | ดาวน์โหลดไฟล์ JSONL + สุ่มแบบ Reservoir Sampling | เรียก API ทีละ item พร้อมหน่วงเวลา 0.1 วินาที |
| **Transform** | Joinกับmetadata ด้วย `parent_asin`สำเร็จ100% ,ตัดรีวิวซ้ำ,ล้างHTML/URL, สร้าง feature | คลีนข้อมูล 4 ชั้น (ตัดค่าว่าง/ซ้ำ/หัวข้อ < 15 อักษร),สแกนคีย์เวิร์ด4,หมวดแบ่งประเภทคอนเทนต์ด้วยMedian,จัดกลุ่ม4โซน (Star, Controversial, Informative, Niche)|
| **Load** | `df_joined` พร้อม feature | `corpus.jsonl` (ใช้ซ้ำโดยไม่ต้องเรียก API ใหม่) |
| **Analytics** | เปรียบเทียบสัดส่วนการพูดถึง (Mention Rate) | เปรียบเทียบค่ามัธยฐาน (Median) ของ score / comments |

---

# Part 2 — Voice of Customer (Digital Music)

## โจทย์ธุรกิจ

**ผู้ตัดสินใจ:** Marketing(ทีมการตลาดและสื่อสารแบรนด์) — การวางจุดขาย (Selling Points),คำโปรยโฆษณา (Ad Copywriting),คำกล่าวอ้างสรรพคุณสินค้า (Value Claims)

**ความเสี่ยงถ้าตัดสินใจผิด:** เสียการลงทุนในค่าโฆษณาโดยใช้สื่อสารที่ไม่ตรงกับความต้องการจริงของลูกค้า,สูญเสียความน่าเชื่อถือหากทำ Claim Marketing ที่เวอร์เกินจริงไม่ตรงกับสิ่งที่ลูกค้าประทับใจ,สูญเสียความน่าเชื่อถือหากทำ Claim Marketing ที่เวอร์เกินจริงไม่ตรงกับสิ่งที่ลูกค้าประทับใจ

**สมมติฐานตั้งต้น:** ลูกค้าที่ซื้อเพลงในกลุ่ม Digital Music และให้ดาวสูง ไม่ได้ประทับใจแค่เรื่อง "ราคาถูก" แต่เน้นเรื่อง
 *"ความทรงจำ/ความประทับใจในอดีต (Nostalgia)"* และ*"คุณภาพเสียงความคมชัดสูง(Crystal Clear Sound Quality)"*
 ซึ่งเป็น2ประเด็นหลักที่นำมาทำAd Copyแล้วได้ผลดีที่สุด

**ที่มา:Amazon Reviews 2023 หมวด Digital_Music

---

# Part 3 — Data Collection Robot

## โจทย์และการเก็บข้อมูล

**คำถาม:** ข่าวการเมืองประเภทใด เช่นนโยบายเศรษฐกิจ,กฎหมาย,เทคโนโลยี,ข้อพิพากระหว่างประเทศที่กระตุ้นให้เกิดการถก
เถียงและยอดการมีส่วนร่วม
(Engagement) จากกลุ่มคนทำงานสาย Tech มากที่สุด?

**ผู้ใช้ผลวิเคราะห์:** สำนักข่าว,Tech Blogger,หรือทีมนโยบายสาธารณะพื่อใช้อางแผนเลือกประเด็นคอนเทนต์หรือชูประเด็นสื่อสารให้ตรงกับความสนใจของกลุ่มเป้าหมาย

**1 record คือ:** 1 โพสต์หัวข้อข่าวการเมืองบนหน้าHacker News

| หัวข้อ | รายละเอียด |
|---|---|
| วิธีเก็บ | APIผ่านAlgolia Search API —  250รายการแรกแล้วดึงรายละเอียดทีละitem |
| เก็บเฉพาะ | `type = story` ที่มี title |
| ความรับผิดชอบ | ใช้AP สาธารณะ,หน่วงเวลา0.1วินาที/คำขอ, ไม่ผ่าน login / CAPTCHA / paywall |
| Field ที่ใช้วิเคราะห์ | `doc_id`, `text` (หัวข้อ), `score`, `n_comments`, `published_at` |
| Field อื่นที่เก็บ | `doc_id` `text(หัวข้อ)` `score` `n_comments` `published_at` |

**อ้างอิงข้อมูลPart3:** [Hacker News](https://news.ycombinator.com/)


