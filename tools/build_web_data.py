#!/usr/bin/env python3
"""
tools/build_web_data.py

Compiles all architectural standards from YAML files under standards/
into docs/data.json for consumption by the interactive web catalog explorer.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent
STANDARDS_DIR = ROOT_DIR / "standards"
OUTPUT_FILE = ROOT_DIR / "docs" / "data.json"


def build_web_data():
    human_scale_items = []
    regulation_rulesets = []
    materials_map = {}  # Map item_id -> merged material dict

    yaml_files = sorted(STANDARDS_DIR.glob("**/*.yaml"))

    for filepath in yaml_files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)

        if not content or not isinstance(content, dict):
            continue

        schema = content.get("schema", "")

        # 1. Human Scale Standards
        if "human-scale" in schema:
            space_category = content.get("category", "")
            catalog_desc = content.get("description", "")
            items = content.get("items", {})
            for item_key, item_data in items.items():
                item_entry = dict(item_data)
                item_entry["item_key"] = item_key
                item_entry["catalog_category"] = space_category
                item_entry["catalog_description"] = catalog_desc
                human_scale_items.append(item_entry)

        # 2. Regulation Rulesets
        elif "regulation" in schema:
            reg_id = content.get("regulation_id", "")
            reg_title = content.get("title", "")
            reg_title_en = content.get("title_en", "")
            reg_desc = content.get("description", "")
            jurisdiction = content.get("jurisdiction", "TH")
            clauses_raw = content.get("clauses", {})

            clauses_list = []
            for clause_key, clause_data in clauses_raw.items():
                c_entry = dict(clause_data)
                c_entry["clause_key"] = clause_key
                c_entry["regulation_id"] = reg_id
                c_entry["regulation_title"] = reg_title
                clauses_list.append(c_entry)

            ruleset_entry = {
                "regulation_id": reg_id,
                "title": reg_title,
                "title_en": reg_title_en,
                "description": reg_desc,
                "jurisdiction": jurisdiction,
                "clauses": clauses_list,
            }
            regulation_rulesets.append(ruleset_entry)

        # 3. Material Specifications & Pricing
        elif "material" in schema:
            catalog_id = content.get("catalog_id", "")
            catalog_title = content.get("title", "")
            items = content.get("items", {})

            for item_key, item_data in items.items():
                item_id = item_data.get("id", item_key)
                if item_id not in materials_map:
                    materials_map[item_id] = {
                        "id": item_id,
                        "item_key": item_key,
                        "name": item_data.get("name", ""),
                        "name_en": item_data.get("name_en", ""),
                        "category": item_data.get("category", ""),
                        "unit": item_data.get("unit", ""),
                        "cost": item_data.get("cost"),
                        "carbon": item_data.get("carbon"),
                        "specification": item_data.get("specification", ""),
                        "tags": item_data.get("tags", []),
                        "catalogs": [catalog_id],
                    }
                else:
                    # Merge existing entry with new information (e.g. merge cost or carbon)
                    existing = materials_map[item_id]
                    if catalog_id not in existing["catalogs"]:
                        existing["catalogs"].append(catalog_id)
                    if item_data.get("cost") and not existing.get("cost"):
                        existing["cost"] = item_data.get("cost")
                    if item_data.get("carbon") and not existing.get("carbon"):
                        existing["carbon"] = item_data.get("carbon")
                    if item_data.get("specification") and not existing.get("specification"):
                        existing["specification"] = item_data.get("specification")
                    # Merge tags without duplicates
                    for t in item_data.get("tags", []):
                        if t not in existing["tags"]:
                            existing["tags"].append(t)

    materials_list = list(materials_map.values())

    data = {
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "human_scale_count": len(human_scale_items),
            "regulation_rulesets_count": len(regulation_rulesets),
            "regulation_clauses_count": sum(len(r["clauses"]) for r in regulation_rulesets),
            "materials_count": len(materials_list),
        },
        "human_scale": human_scale_items,
        "regulations": regulation_rulesets,
        "materials": materials_list,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Successfully compiled standards into {OUTPUT_FILE}")
    print(f"Summary: {data['summary']}")
    return data


if __name__ == "__main__":
    build_web_data()
