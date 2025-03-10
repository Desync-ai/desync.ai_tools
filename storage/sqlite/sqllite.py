import sqlite3
import json
from typing import List, Dict, Optional, Any
from desync_search import DesyncClient

class SQLiteStorage:
    """
    A class to handle saving and managing scraped page data in a SQLite database.
    It supports saving results from search, crawl, and bulk operations, and creates
    three different views: view_search, view_crawl, and view_bulk.
    """

    def __init__(self, db_path: str, desync_client: Optional[DesyncClient] = None):
        """
        Initialize the SQLiteStorage with the desired SQLite database path and optionally a DesyncClient.
        
        :param db_path: Path to the SQLite database file.
        :param desync_client: An instance of DesyncClient used for performing searches/crawls.
        """
        self.db_path = db_path
        self.desync_client = desync_client
        self._ensure_table()
        self._create_views()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _ensure_table(self):
        """
        Ensure that the table to store page data exists in the database.
        """
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS page_data (
                db_id INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT,
                url TEXT,
                domain TEXT,
                timestamp TEXT,
                bulk_search_id TEXT,
                search_type TEXT,
                text_content TEXT,
                html_content TEXT,
                internal_links TEXT,
                external_links TEXT,
                latency_ms REAL,
                complete INTEGER,
                created_at TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def _create_views(self):
        """
        Create SQLite views for search, crawl, and bulk data.
        """
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("CREATE VIEW IF NOT EXISTS view_search AS SELECT * FROM page_data WHERE search_type='search'")
        c.execute("CREATE VIEW IF NOT EXISTS view_crawl AS SELECT * FROM page_data WHERE search_type='crawl'")
        c.execute("CREATE VIEW IF NOT EXISTS view_bulk AS SELECT * FROM page_data WHERE search_type='bulk'")
        conn.commit()
        conn.close()

    def save(self, data: List[Dict[str, Any]]):
        """
        Overwrite the existing data in the database with the provided data.
        
        :param data: List of dictionaries containing the scraped page data.
        """
        conn = self._get_connection()
        c = conn.cursor()
        # Clear existing data
        c.execute('DELETE FROM page_data')
        # Insert new data
        for record in data:
            c.execute('''
                INSERT INTO page_data 
                (id, url, domain, timestamp, bulk_search_id, search_type, text_content, html_content, internal_links, external_links, latency_ms, complete, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.get("id"),
                record.get("url"),
                record.get("domain"),
                record.get("timestamp"),
                record.get("bulk_search_id"),
                record.get("search_type"),
                record.get("text_content"),
                record.get("html_content"),
                json.dumps(record.get("internal_links", [])),
                json.dumps(record.get("external_links", [])),
                record.get("latency_ms"),
                1 if record.get("complete") else 0,
                record.get("created_at")
            ))
        conn.commit()
        conn.close()

    def append(self, data: List[Dict[str, Any]]):
        """
        Append a list of dictionaries to the SQLite database.
        
        :param data: List of dictionaries containing the scraped page data.
        """
        conn = self._get_connection()
        c = conn.cursor()
        for record in data:
            c.execute('''
                INSERT INTO page_data 
                (id, url, domain, timestamp, bulk_search_id, search_type, text_content, html_content, internal_links, external_links, latency_ms, complete, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.get("id"),
                record.get("url"),
                record.get("domain"),
                record.get("timestamp"),
                record.get("bulk_search_id"),
                record.get("search_type"),
                record.get("text_content"),
                record.get("html_content"),
                json.dumps(record.get("internal_links", [])),
                json.dumps(record.get("external_links", [])),
                record.get("latency_ms"),
                1 if record.get("complete") else 0,
                record.get("created_at")
            ))
        conn.commit()
        conn.close()

    def load(self) -> List[Dict[str, Any]]:
        """
        Load all data from the SQLite database into a list of dictionaries.
        
        :return: List of dictionaries containing the page data.
        """
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM page_data')
        rows = c.fetchall()
        conn.close()
        result = []
        for row in rows:
            result.append({
                "id": row["id"],
                "url": row["url"],
                "domain": row["domain"],
                "timestamp": row["timestamp"],
                "bulk_search_id": row["bulk_search_id"],
                "search_type": row["search_type"],
                "text_content": row["text_content"],
                "html_content": row["html_content"],
                "internal_links": json.loads(row["internal_links"]) if row["internal_links"] else [],
                "external_links": json.loads(row["external_links"]) if row["external_links"] else [],
                "latency_ms": row["latency_ms"],
                "complete": bool(row["complete"]),
                "created_at": row["created_at"]
            })
        return result

    def update(self, criteria: Dict[str, Any], new_data: Dict[str, Any]):
        """
        Update records in the SQLite database that match the given criteria with new data.
        
        :param criteria: Dictionary of field-value pairs to match records.
        :param new_data: Dictionary of field-value pairs to update matched records.
        """
        conn = self._get_connection()
        c = conn.cursor()

        # Build the WHERE clause
        where_clause = " AND ".join([f"{k}=?" for k in criteria.keys()])
        where_values = list(criteria.values())

        # Build the SET clause; if updating list fields, ensure they're stored as JSON
        set_clauses = []
        set_values = []
        for key, value in new_data.items():
            if key in ["internal_links", "external_links"]:
                set_clauses.append(f"{key}=?")
                set_values.append(json.dumps(value))
            elif key == "complete":
                set_clauses.append(f"{key}=?")
                set_values.append(1 if value else 0)
            else:
                set_clauses.append(f"{key}=?")
                set_values.append(value)
        set_clause = ", ".join(set_clauses)

        sql = f"UPDATE page_data SET {set_clause} WHERE {where_clause}"
        c.execute(sql, set_values + where_values)
        conn.commit()
        conn.close()

    def delete(self, criteria: Dict[str, Any]):
        """
        Delete records from the SQLite database that match the given criteria.
        
        :param criteria: Dictionary of field-value pairs to match records.
        """
        conn = self._get_connection()
        c = conn.cursor()
        where_clause = " AND ".join([f"{k}=?" for k in criteria.keys()])
        where_values = list(criteria.values())
        sql = f"DELETE FROM page_data WHERE {where_clause}"
        c.execute(sql, where_values)
        conn.commit()
        conn.close()

    def exists(self) -> bool:
        """
        Check if there is any data stored in the SQLite database.
        
        :return: True if data exists, False otherwise.
        """
        conn = self._get_connection()
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM page_data')
        count = c.fetchone()[0]
        conn.close()
        return count > 0

    def _page_data_to_dict(self, page_data: Any) -> Dict[str, Any]:
        """
        Convert a PageData object (returned by DesyncClient methods) to a dictionary for SQLite storage.
        
        :param page_data: The PageData object.
        :return: Dictionary representation of the page data.
        """
        text_content = getattr(page_data, "text_content", None)
        if text_content:
            text_content = text_content.replace("\n", " ").replace("\r", " ")

        return {
            "id": getattr(page_data, "id", None),
            "url": getattr(page_data, "url", None),
            "domain": getattr(page_data, "domain", None),
            "timestamp": getattr(page_data, "timestamp", None),
            "bulk_search_id": getattr(page_data, "bulk_search_id", None),
            "search_type": getattr(page_data, "search_type", None),
            "text_content": text_content,
            "html_content": getattr(page_data, "html_content", None),
            "internal_links": getattr(page_data, "internal_links", []),
            "external_links": getattr(page_data, "external_links", []),
            "latency_ms": getattr(page_data, "latency_ms", None),
            "complete": getattr(page_data, "complete", None),
            "created_at": getattr(page_data, "created_at", None),
        }

    def search_and_save(self, url: str, save_mode: str = "append", **desync_params):
        """
        Perform a search using the integrated DesyncClient and save the result to SQLite.
        
        :param url: The URL to search.
        :param save_mode: Either "append" to add to an existing database or "overwrite" to clear existing data.
        :param desync_params: Additional keyword arguments passed to DesyncClient.search().
        """
        if not self.desync_client:
            raise ValueError("DesyncClient not provided. Initialize SQLiteStorage with a valid DesyncClient.")

        result = self.desync_client.search(url, **desync_params)
        result_dict = self._page_data_to_dict(result)
        result_dict["search_type"] = "search"  # Mark as a search result

        if save_mode == "append":
            self.append([result_dict])
        else:
            self.save([result_dict])

    def crawl_and_save(self, start_url: str, max_depth: int = 2, save_mode: str = "append", **desync_params):
        """
        Perform a crawl using the integrated DesyncClient and save the results to SQLite.
        
        :param start_url: The initial URL to begin crawling.
        :param max_depth: Maximum depth for the crawl.
        :param save_mode: Either "append" to add to an existing database or "overwrite" to clear existing data.
        :param desync_params: Additional keyword arguments passed to DesyncClient.crawl().
        """
        if not self.desync_client:
            raise ValueError("DesyncClient not provided. Initialize SQLiteStorage with a valid DesyncClient.")

        results = self.desync_client.crawl(start_url=start_url, max_depth=max_depth, **desync_params)
        data = []
        for result in results:
            result_dict = self._page_data_to_dict(result)
            result_dict["search_type"] = "crawl"  # Mark as a crawl result
            data.append(result_dict)

        if save_mode == "append":
            self.append(data)
        else:
            self.save(data)

    def bulk_search_and_save(
        self,
        target_list: List[str],
        save_mode: str = "append",
        bulk_search_params: Optional[Dict[str, Any]] = None,
        collect_results_params: Optional[Dict[str, Any]] = None
    ):
        """
        Perform a bulk search using the integrated DesyncClient and save the results to SQLite.
        
        :param target_list: List of URLs to process.
        :param save_mode: Either "append" to add to an existing database or "overwrite" to clear existing data.
        :param bulk_search_params: Additional parameters for DesyncClient.bulk_search().
        :param collect_results_params: Additional parameters for DesyncClient.collect_results().
        """
        if not self.desync_client:
            raise ValueError("DesyncClient not provided. Initialize SQLiteStorage with a valid DesyncClient.")

        bulk_search_params = bulk_search_params or {}
        collect_results_params = collect_results_params or {}

        bulk_info = self.desync_client.bulk_search(target_list=target_list, **bulk_search_params)
        bulk_search_id = bulk_info.get("bulk_search_id")

        results = self.desync_client.collect_results(
            bulk_search_id=bulk_search_id, target_links=target_list, **collect_results_params
        )
        data = []
        for result in results:
            result_dict = self._page_data_to_dict(result)
            result_dict["search_type"] = "bulk"  # Mark as a bulk search result
            data.append(result_dict)

        if save_mode == "append":
            self.append(data)
        else:
            self.save(data)
