# Desync.AI Tools

A modular, open-source toolkit for stealthy web data extraction, boilerplate cleaning, and structured output storage — powered by the `desync-search` API.

---

## 🔧 Features

- **Crawling & Bulk Search**: Easily scrape websites using `DesyncClient` with optional stealth mode.
- **Boilerplate Removal**: Clean repetitive content (like navbars and footers) from results.
- **Structured Storage**: Export to CSV, JSON, or SQLite formats.
- **Contact Extraction** *(WIP)*: Tools to extract LinkedIn profiles and other contact info.
- **Extensible**: Plug your pipeline into examples, output clean structured data to `/output`.

---

## 🗂 Directory Structure

```
DESYNC.AI_TOOLS/
│
├── basic_implementation/         # The fundamental search methods (crawl, bulk, stealth)
├── data_extraction/              # contact_extractor.py and related tools
├── examples/                     # usage examples (bulk_clean_and_save_csv.py)
├── output/                       # saved outputs (CSV/JSON/DB)
├── result_cleaning/              # boilerplate removal tools
├── storage/
│   ├── csv/                      # save_to_csv.py
│   ├── json/                     # save_to_json.py
│   └── sqlite/                   # save_to_sqlite.py
│
├── .env                          # credentials (not committed)
├── search_demo.ipynb             # interactive notebook demo
├── .gitignore
└── README.md                     # this file
```

---

## 🚀 Quick Start

1. **Install dependencies** (via pip/venv)

```bash
pip install desync-search
```

2. **Set your credentials** in `.env`:

```
DESYNC_API_KEY=your_api_key_here
```

3. **Run an example:**

```bash
python examples/bulk_clean_and_save_csv.py
```

---

## 📦 Storage Options

| Format | Path                    | Description                     |
|--------|-------------------------|---------------------------------|
| CSV    | `storage/csv/`          | Easy to open in Excel or Pandas |
| JSON   | `storage/json/`         | Flexible, human-readable        |
| SQLite | `storage/sqlite/`       | Structured, queryable data      |

---

## 👨‍💻 Authors

- Jackson Ballow
- Mark Evgenev
- Maks Kubicki

---

## 🪪 License

MIT — use freely and give credit. Contributions welcome!

