# Desync.AI Tools

An open-source toolkit for stealthy web data extraction, boilerplate cleaning, structured storage, transformer embedding, and more — powered by the `desync-search` API.

---

## 🔧 Features

- **Crawling & Bulk Search**: Grab web data using `DesyncClient`, with support for stealthy headful scraping.
- **Boilerplate Removal**: Strip repeated pages, headers, footers, and navbars from raw HTML or `.text_content`.
- **Data Extraction** *(WIP)*: Find emails, phones, LinkedIns, and named entities from raw text or HTML.
- **Embedding Pipelines**: Chunk, tokenize, and run transformer inference (BERT, S-BERT).
- **Link Graph Tools**: Construct internal/external page link graphs for sitemaps or network analysis.
- **Text Stats + Heuristics**: Score content quality (word count, link ratio, etc.)
- **Structured Output**: Store clean results in CSV, JSON, or SQLite.
- **Sentiment Analysis and Summarisation**: Create a concise summary and sentiment analysis on the pages you scrape.
- **Link Graph Generation**: Construct a graph on how the pages you scraped link to one another.

---

## 🗂 Directory Structure

```
DESYNC.AI_TOOLS/
│
├── basic_implementation/         # Core DesyncClient tools
│   ├── bulk_search.py
│   ├── crawl_search.py
│   ├── stealth_search.py
│   └── test_search.py
│
├── data_extraction/              # Contact info extraction (email, phone, LinkedIn)
│   ├── extract_contacts.py
│   ├── text_summarization.py
│   ├── sentiment_analyzer.py
│   └── named_entity_extractor.py
│
├── examples/                     # Example scripts
│   └── bulk_clean_and_save_csv.py
│
├── model_prep/                   # Transformer-based modeling pipeline
│   ├── chunk_text_blocks.py
│   ├── dataset_builder.py
│   ├── tokenizer_loader.py
│   ├── torch_loader.py
│   └── transformer_runner.py
│
├── parsers/                      # General-purpose HTML and graph tools
│   ├── html_parser.py
│   ├── language_detector.py
│   ├── link_graph.py
│   └── text_stats.py
│
├── result_cleaning/              # Cleaning and deduplication
│   ├── html_cleaning/
│   │   └── remove_boilerplate_html.py
│   ├── text_content_cleaning/
│   │    └── remove_boilerplate_text.py
│   └── duplicate_page_remover.py
│
├── storage/                      # Save your search results
│   ├── csv_storage.py
│   ├── json_storage.py
│   └── sqlite_storage.py
│
├── output/                       # Your saved outputs (ignored by git)
│
├── .env                          # Credentials (not committed)
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install desync_search
```

```bash
pip install desync-data
```

### 2. Add your API key

Create a `.env` file in the root folder:

```
DESYNC_API_KEY=your_api_key_here
```

### 3. Run an example

```bash
python examples/bulk_clean_and_save_csv.py
```

---

## 📦 Storage Formats

| Format | Path                | Notes                              |
|--------|---------------------|------------------------------------|
| CSV    | `storage/csv/`      | For spreadsheets, Pandas, Excel    |
| JSON   | `storage/json/`     | Human-readable + flexible          |
| SQLite | `storage/sqlite/`   | Lightweight relational database    |

---

## 👨‍💻 Authors

- Jackson Ballow  
- Mark Evgenev  
- Maks Kubicki

---

## 🪪 License

MIT — use freely, improve freely, and credit where due.
