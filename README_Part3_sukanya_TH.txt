Big Data | Part 3 (3.2-3.3) | branch sukanya | ทำ 10 local commits ไม่ push

เป้าหมาย
- นำเนื้อหาจาก Project1_Text_Analytics69_Teams_Part3.ipynb เข้า Project1_Text_Analytics69_Teams.ipynb โดยเก็บ Part 1/2 ของ Notebook หลักไว้
- แก้ Data Quality, corpus.jsonl / corpus_cleaned.jsonl, การวิเคราะห์หัวข้อข่าวและกราฟ พร้อม Insight Card ซึ่งคำนวณจากข้อมูลจริงเมื่อรัน
- ตรวจเงื่อนไขอย่างน้อย 200 valid analytical records; หากไม่ถึง หยุดพร้อมแจ้งข้อผิดพลาด ไม่แต่งผล
- สร้าง 10 commits เฉพาะ Notebook หลักบน branch sukanya ใน Codespace ของผู้ใช้เท่านั้น และไม่ push

สิ่งที่ต้องทำใน Codespace
1) เปิด Codespace ที่มี Git repository audomsak-pypy/Project1-Text_Analytics69
2) ตรวจสอบว่าอยู่ branch sukanya: git branch --show-current
   ถ้าไม่ใช่ ให้เปลี่ยน branch ด้วยตนเองหลังตรวจสอบการเปลี่ยนแปลงที่ค้างอยู่
3) ตรวจสอบ git status --short; ถ้า Notebook หลักมีงานแก้ไขที่ยังไม่ commit ให้ commit/stash เก็บก่อน
   (สคริปต์จะปฏิเสธการรันถ้า Notebook หลัก dirty เพื่อป้องกันการทำงานทับ)
4) อัปโหลด complete_part3_local.py ลงในโฟลเดอร์รากของ Repository ผ่าน VS Code Explorer > Upload
5) เปิด Terminal ในโฟลเดอร์รากและรัน:

   python3 complete_part3_local.py

6) ตรวจสอบ 10 commits ใหม่:

   git log -10 --format='%h %an <%ae> %s'
   git status --short

   ยังไม่ต้องใช้คำสั่ง git push

7) เปิด Project1_Text_Analytics69_Teams.ipynb แล้วรันเซลล์ Part 3 ตามลำดับ
   หากขาด package ให้ติดตั้ง requests beautifulsoup4 pandas matplotlib pythainlp scipy scikit-learn jupyter
   การเก็บข่าวอาจใช้เวลาหลายนาทีเนื่องจากเว้นระยะระหว่าง requests
   ตรวจ output Final valid corpus >= 200 และเช็คบทความตัวอย่างว่าเป็นข่าวจริง
   หาก robots.txt ไม่อนุญาต / เว็บไซต์เข้าถึงไม่ได้ / ได้ข้อมูลไม่ครบ 200 ให้ระบุผลที่เกิดขึ้นจริง
   และแก้แหล่งหรือช่วงวันที่อย่างถูกต้องก่อนส่งงาน

จุดสำคัญ
- ใช้ Part3 ใน Codespace ก่อน ถ้าไม่พบจะอ่านจาก branch toto ผ่าน git show/fetch (ไม่ใช่ push)
- ใช้การเก็บแบบ Web Robot (Requests + BeautifulSoup) เพียงวิธีเดียวตามโจทย์
- หากหน้าหมวดการเมืองให้รายการน้อย จะใช้หน้าข่าวรอบวันย้อนหลังของ Thai PBS เพื่อขยายการเก็บ
  นั่นหมายถึง corpus รวมหลายหมวดข่าว; ห้ามกล่าวว่าเป็นข่าวการเมืองทั้งหมด
- ข้อมูลจริงและผลลัพธ์ต้องรันใน Codespace ที่เข้าถึงเว็บไซต์ได้ จึงยังไม่ใช่ผลการเก็บที่ตรวจสอบแล้ว
- ไฟล์สำรองของ Notebook หลักอยู่ใน .git/part3-main-before-merge.ipynb (ไม่ commit)
- 10 commits ทั้งหมดจะอยู่ใน Codespace เท่านั้นจนกว่าผู้ใช้สั่ง push เอง
