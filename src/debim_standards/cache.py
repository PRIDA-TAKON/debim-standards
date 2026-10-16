"""
Local disk cache manager for debim-standards SDK with 7-day TTL and air-gapped fallback.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import yaml


DEFAULT_CACHE_DIR = Path.home() / ".debim" / "standards_cache"
DEFAULT_TTL_SECONDS = 7 * 24 * 3600  # 7 days


def find_bundled_standards_dir() -> Path:
    """
    Locates the bundled standards directory containing YAML definition files.
    Checks environment variable DEBIM_STANDARDS_DIR, repo root, package dir, and cwd.
    """
    env_dir = os.environ.get("DEBIM_STANDARDS_DIR")
    if env_dir:
        p = Path(env_dir)
        if p.is_dir():
            return p

    # Relative to this file: src/debim_standards/cache.py -> repo root is parents[2]
    repo_standards = Path(__file__).resolve().parents[2] / "standards"
    if repo_standards.is_dir():
        return repo_standards

    pkg_standards = Path(__file__).resolve().parent / "standards"
    if pkg_standards.is_dir():
        return pkg_standards

    cwd_standards = Path.cwd() / "standards"
    if cwd_standards.is_dir():
        return cwd_standards

    # Fallback to repo standards path even if not yet created
    return repo_standards


class StandardsCache:
    """
    Manages loading, caching, TTL expiration, and fallback for standards data.
    """

    def __init__(
        self,
        cache_dir: Optional[Union[str, Path]] = None,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        standards_dir: Optional[Union[str, Path]] = None,
    ):
        if cache_dir is not None:
            self.cache_dir = Path(cache_dir)
        elif os.environ.get("DEBIM_CACHE_DIR"):
            self.cache_dir = Path(os.environ["DEBIM_CACHE_DIR"])
        else:
            self.cache_dir = DEFAULT_CACHE_DIR

        self.ttl_seconds = ttl_seconds
        self.cache_file = self.cache_dir / "standards_cache.json"

        if standards_dir is not None:
            self.standards_dir = Path(standards_dir)
        else:
            self.standards_dir = find_bundled_standards_dir()

    def is_cache_valid(self) -> bool:
        """
        Checks if local cache file exists, is non-empty, and has not expired (TTL < 7 days).
        """
        if not self.cache_file.exists():
            return False

        try:
            mtime = self.cache_file.stat().st_mtime
            if (time.time() - mtime) > self.ttl_seconds:
                return False

            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            created_at = data.get("created_at", 0)
            if (time.time() - created_at) > self.ttl_seconds:
                return False

            return True
        except Exception:
            return False

    def load_from_cache(self) -> Optional[Dict[str, Any]]:
        """
        Loads standards dictionary from local disk cache if valid.
        """
        if not self.is_cache_valid():
            return None

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("data")
        except Exception:
            return None

    def save_to_cache(self, raw_data: Dict[str, Any]) -> bool:
        """
        Persists data to local disk cache. Creates directories if needed.
        Returns True if successful, False otherwise.
        """
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            payload = {
                "created_at": time.time(),
                "ttl_seconds": self.ttl_seconds,
                "data": raw_data,
            }
            tmp_file = self.cache_file.with_suffix(".tmp")
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            tmp_file.replace(self.cache_file)
            return True
        except Exception:
            # Failure to cache (e.g., read-only filesystem) should not crash the SDK
            return False

    def load_bundled_data(self) -> Dict[str, Any]:
        """
        Loads and compiles static standards data from bundled YAML files.
        """
        human_scale_data: Dict[str, Any] = {}
        regulations_data: Dict[str, List[Any]] = {}
        materials_data: Dict[str, Any] = {}

        if self.standards_dir.is_dir():
            yaml_files = sorted(self.standards_dir.glob("**/*.yaml"))
            for filepath in yaml_files:
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = yaml.safe_load(f)
                except Exception:
                    continue

                if not content or not isinstance(content, dict):
                    continue

                schema = content.get("schema", "")

                # 1. Human Scale
                if "human-scale" in schema:
                    category = content.get("category", "")
                    items = content.get("items", {})
                    for item_key, item_val in items.items():
                        item_dict = dict(item_val)
                        ref_id = item_dict.get("id", item_key)
                        item_dict["item_key"] = item_key

                        # Store under various reference keys for quick lookup
                        keys_to_index = {
                            item_key,
                            ref_id,
                            item_key.lower(),
                            ref_id.lower(),
                            f"standards.human_scale.{category}.{item_key}",
                            f"standards.human_scale.{category}.{ref_id}",
                            f"human_scale.{category}.{item_key}",
                            f"{category}.{item_key}",
                        }
                        for k in keys_to_index:
                            human_scale_data[k] = item_dict

                # 2. Regulations
                elif "regulation" in schema:
                    jurisdiction = content.get("jurisdiction", "TH").upper()
                    clauses = content.get("clauses", {})
                    clause_list = regulations_data.setdefault(jurisdiction, [])
                    for clause_key, clause_val in clauses.items():
                        c_dict = dict(clause_val)
                        c_dict["clause_key"] = clause_key
                        clause_list.append(c_dict)

                # 3. Materials
                elif "material" in schema:
                    catalog_id = content.get("catalog_id", "")
                    items = content.get("items", {})
                    for item_key, item_val in items.items():
                        m_id = item_val.get("id", item_key)

                        # Check if material already registered to merge cost/carbon
                        existing = materials_data.get(m_id) or materials_data.get(item_key)
                        if existing is None:
                            merged = dict(item_val)
                            merged["item_key"] = item_key
                            if "id" not in merged:
                                merged["id"] = m_id
                        else:
                            merged = dict(existing)
                            if item_val.get("cost") and not merged.get("cost"):
                                merged["cost"] = item_val.get("cost")
                            if item_val.get("carbon") and not merged.get("carbon"):
                                merged["carbon"] = item_val.get("carbon")
                            if item_val.get("specification") and not merged.get("specification"):
                                merged["specification"] = item_val.get("specification")
                            # Merge tags
                            tags_set = set(merged.get("tags", [])) | set(item_val.get("tags", []))
                            merged["tags"] = sorted(list(tags_set))

                        # Index under id, key, and lowercases
                        for k in {m_id, item_key, m_id.lower(), item_key.lower()}:
                            materials_data[k] = merged

        return {
            "human_scale": human_scale_data,
            "regulations": regulations_data,
            "materials": materials_data,
        }

    def get_data(self) -> Dict[str, Any]:
        """
        Retrieves standards data from cache if valid, or loads bundled data and updates cache.
        Guarantees air-gapped zero network dependency.
        """
        cached = self.load_from_cache()
        if cached is not None:
            return cached

        bundled = self.load_bundled_data()
        self.save_to_cache(bundled)
        return bundled

    def clear_cache(self) -> bool:
        """
        Clears cached data file.
        """
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
            return True
        except Exception:
            return False
