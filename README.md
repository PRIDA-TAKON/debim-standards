# 🌐 debim-standards

**Open Data Standards, Human Scale Anthropometrics, Building Codes, and Material Catalogs for Declarative BIM.**

[![CI Test Suite](https://github.com/PRIDA-TAKON/debim-standards/actions/workflows/ci.yml/badge.svg)](https://github.com/PRIDA-TAKON/debim-standards/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Standards: OpenBIM](https://img.shields.io/badge/Standards-OpenBIM%20Compatible-brightgreen.svg)](https://technical.buildingsmart.org/)
[![debim Ecosystem](https://img.shields.io/badge/Engine-debim%20v0.9.0+-blue.svg)](https://github.com/PRIDA-TAKON/debim)

---

## 📖 พันธกิจและภาพรวม (Mission & Overview)

ในการเขียนแบบสถาปัตยกรรมและวิศวกรรมอาคารด้วย AI หรือ Declarative BIM (Building-as-Code) สถาปนิกและผู้พัฒนาไม่ควรต้องมานั่งประกาศขนาดเตียง โต๊ะ ตู้ หรือเขียนกฎหมายอาคารซ้ำๆ ในทุกโปรเจกต์

**`debim-standards`** ถูกสร้างขึ้นเพื่อเป็น **คลังข้อมูลเปิดสาธารณะ (Open Data Standards)** ที่แยกส่วนออกจากตัวเอนจิน `debim` โดยทำหน้าที่เป็น:
1. **คลังสัดส่วนมนุษย์และระยะใช้งาน (Human Scale & Clearance Envelopes):** สกัดจากมาตรฐานสากล (Neufert, Panero & Zelnik, NASA-STD-3000)
2. **คลังกฎหมายอาคารและระยะร่น (Building Regulations & Codes):** เริ่มต้นด้วยกฎหมายไทย (กฎกระทรวง ฉบับที่ 55 พ.ร.บ. ควบคุมอาคาร พ.ศ. 2522, ข้อบัญญัติ กทม.)
3. **คลังสเปกวัสดุและราคากลาง (Material Specifications & Costing):** บัญชีราคากลางกรมบัญชีกลาง ว480 และดัชนีราคาวัสดุก่อสร้างกระทรวงพาณิชย์
4. **เว็บแค็ตตาล็อกอินเตอร์แอคทีฟ (Interactive Web Catalog):** หน้าเว็บสำหรับสถาปนิก มนุษย์ และนักศึกษาเปิดค้นหาและดูระยะใช้งานแบบ 2D/3D ได้โดยไม่ต้องติดตั้งโปรแกรม

---

## 🏛️ โครงสร้างคลังข้อมูล (Directory Structure)

```text
debim-standards/
├── standards/
│   ├── human_scale/                 # ขนาดเฟอร์นิเจอร์และระยะ Clearance การใช้งานจริง
│   │   ├── bedroom.yaml             # เตียงเดี่ยว, เตียงคู่, ตู้เสื้อผ้า, โต๊ะเครื่องแป้ง
│   │   ├── living.yaml              # โซฟา, โต๊ะกลาง, ตู้วางทีวี, อาร์มแชร์
│   │   ├── dining.yaml              # โต๊ะอาหาร 4/6/8 ที่นั่ง, เก้าอี้ทานข้าว
│   │   ├── kitchen.yaml             # เคาน์เตอร์ครัว, อ่างล้างจาน, เตาปรุงอาหาร, ตู้เย็น
│   │   ├── sanitary.yaml            # โถสุขภัณฑ์, อ่างล้างหน้า, ส่วนอาบน้ำ, อ่างอาบน้ำ
│   │   ├── office.yaml              # โต๊ะทำงาน, เก้าอี้สำนักงาน, ตู้เอกสาร
│   │   └── circulation.yaml         # ระยะทางเดินคนเดียว, ทางเดินสวนกัน, วงเลี้ยวรถเข็น
│   │
│   ├── regulations/                 # ข้อกำหนดกฎหมายอาคารและการตรวจสอบ (Rulesets)
│   │   └── th/                      # ประเทศไทย
│   │       ├── ministerial_reg_55.yaml   # กฎกระทรวง 55 (แสง-ลม 10%, บันได, เพดาน)
│   │       ├── setbacks.yaml             # ระยะร่นแนวเขตที่ดินและถนนสาธารณะ
│   │       └── bma_ordinance.yaml        # ข้อบัญญัติกรุงเทพมหานคร
│   │
│   └── materials/                   # คุณสมบัติวัสดุและราคากลางอ้างอิง
│       ├── cgd_v480.yaml            # เกณฑ์ราคากลางงานก่อสร้างภาครัฐ ว480
│       └── commerce_tpso.yaml       # ข้อมูลวัสดุสำนักงานนโยบายและยุทธศาสตร์การค้า
│
├── docs/                            # เว็บแค็ตตาล็อก GitHub Pages (Zero-install Web UI)
│   ├── index.html                   # Interactive Catalog Explorer
│   └── viewer.js                    # ตัวแสดงมิติ 2D SVG / 3D Canvas
│
├── src/debim_standards/             # Python Client SDK สำหรับดึงข้อมูลเข้า debim
│   ├── __init__.py
│   ├── loader.py                    # ตัวอ่าน YAML และค้นหาข้อมูล
│   └── models.py                    # Pydantic Schema Models
│
├── tests/                           # Automated Verification Suite
│   ├── test_human_scale.py
│   ├── test_regulations.py
│   └── test_materials.py
│
└── tools/                           # เครื่องมือตรวจสอบและ Watchdog Orchestrator
    ├── roadmap_standards.json
    └── watchdog_standards_prs.py
```

---

## ⚡ วิธีที่ `debim` นำไปใช้งาน (Usage with debim)

เมื่อใช้ `debim-standards` ร่วมกับ `debim v0.9.0+` สถาปนิกสามารถเขียนโค้ดสเปซสั้นๆ ได้ทันที โดยไม่ต้องประกาศ `variables:` ยาวเหยียด:

```yaml
schema: "IFC4-Minimal"
spaces:
  MasterBedroom:
    dimensions: [5.0, 4.0]
    # อ้างอิงรหัสจาก debim-standards โดยตรง
    contains:
      - ref: "standards.human_scale.bedroom.BED_KING_6FT"
      - ref: "standards.human_scale.bedroom.WARDROBE_2M"
      - ref: "standards.human_scale.office.WORKING_DESK"
    touching:
      target: "LivingRoom"
      side: "NORTH"
```

เอนจิน `debim` จะไปดึงขนาด กว้าง × ยาว × สูง และระยะเปิดหน้าบาน/ทางเดินรอบเตียงมาคำนวณและตรวจสอบ 2D Fit Solver ให้อัตโนมัติ!

---

## 🤖 ระบบตรวจสอบอัตโนมัติ (Automated PR Verification & CI)

โครงการนี้ใช้ระบบ **Fully Automated Contributor Verification**:
1. **GitHub Actions CI:** รันตรวจสอบทันทีเมื่อมี Pull Request เข้ามา
   - ตรวจสอบความถูกต้องของ Schema (Pydantic Validation)
   - ตรวจสอบว่าไม่มีขนาดติดลบ หรือค่า Clearance ที่ไม่สมเหตุสมผล
   - รัน Pytest Suite 100%
2. **Auto-Merge & Orchestrator:**
   - สำหรับ Jules AI และ Automated Contributor บอทจะทำการตรวจสอบสถานะ CI และรวมโค้ด (Squash Merge) พร้อมเปิดแผนงานถัดไปโดยอัตโนมัติ โดยไม่ต้องให้มนุษย์มานั่งเฝ้าหน้าจอ
