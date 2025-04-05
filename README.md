# Desync.AI Tools

An open-source toolkit for stealthy web data extraction, boilerplate cleaning, structured output storage, and a lot more coming soon — powered by the `desync-search` API.

---

## 🔧 Features

- **Crawling & Bulk Search**: Easily scrape websites using `DesyncClient` with optional stealth mode.
- **Boilerplate Removal**: Clean repetitive content (like navbars and footers) from results.
- **Structured Storage**: Export to CSV, JSON, or SQLite formats.
- **Contact Extraction** *(WIP)*: Tools to extract email, phone mumbers, LinkedIn profiles and other contact info.

---

## 🗂 Directory Structure

```
DESYNC.AI_TOOLS/
│
├── basic_implementation/         # The fundamental search methods (crawl, bulk, stealth)
├── data_extraction/              # Contact info extraction tools (emails, LinkedIns, phones, etc.)
├── examples/                     # Usage examples (e.g., bulk_clean_and_save_csv.py)
├── parsers/                      # HTML structure extraction and parsing
├── output/                       # Saved outputs (CSV/JSON/DB) - not committed
├── result_cleaning/
│   ├── html_cleaning/            # Boilerplate removal from HTML content (e.g., header, nav, footer)
│   └── text_content_cleaning/    # Boilerplate removal from .text_content (e.g., repeated lines/paragraphs)
├── storage/
│   ├── csv/                      # save_to_csv.py
│   ├── json/                     # save_to_json.py
│   └── sqlite/                   # save_to_sqlite.py
│
├── .env                          # Credentials (not committed)
├── .gitignore
└── README.md                     # This file

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

