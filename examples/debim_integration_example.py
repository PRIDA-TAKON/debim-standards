#!/usr/bin/env python3
"""
examples/debim_integration_example.py

Integration showcase example demonstrating how the debim compiler (`debim derive`)
consumes `debim-standards` for human scale clearance solving, regulatory code compliance,
and CGD v480 BOQ cost/carbon estimation.
"""

from debim_standards import (
    get_furniture,
    get_material_price,
    get_regulations,
)


def run_debim_derive_integration_showcase():
    print("=" * 70)
    print("🚀 debim derive Compiler Integration Showcase with debim-standards")
    print("=" * 70)

    # 1. Human Scale Furniture & Clearance Envelope Resolution
    print("\n[Step 1] Resolving Space Elements & Clearance Envelopes...")
    bedroom_refs = [
        "standards.human_scale.bedroom.BED_KING_6FT",
        "WARDROBE_18M",
        "DRESSING_TABLE",
    ]

    total_space_needed = 0.0
    for ref in bedroom_refs:
        furniture = get_furniture(ref)
        if furniture:
            print(f"  • Ref: {ref}")
            print(f"    Item Name  : {furniture.name} ({furniture.name_en})")
            print(f"    Dimensions : {furniture.dimensions.width}m (W) x {furniture.dimensions.depth}m (D) x {furniture.dimensions.height}m (H)")
            print(f"    Clearances : Front={furniture.clearance.front}m, Left={furniture.clearance.left}m, Right={furniture.clearance.right}m")
            print(f"    Total Space: {furniture.total_space_area} sq.m (Footprint: {furniture.footprint_area} sq.m)")
            total_space_needed += furniture.total_space_area

    print(f"  => Total Minimum Allocated Floor Area for Bedroom: {total_space_needed:.2f} sq.m")

    # 2. Building Code & Regulation Compliance Evaluation
    print("\n[Step 2] Evaluating Thai Building Code Regulations (Jurisdiction: 'TH')...")
    clauses = get_regulations("TH")
    print(f"  • Loaded {len(clauses)} legal regulation clauses for Thailand.")

    # Example simulation: Evaluate room light/ventilation ratio & stair riser height
    sample_evaluations = [
        ("CLAUSE-51", "opening_area_ratio", 0.12, "Window Light & Ventilation Ratio"),
        ("CLAUSE-22", "riser_height", 0.18, "Stair Riser Height"),
        ("CLAUSE-33", "clear_height", 2.40, "Habitable Room Clear Height"),
    ]

    for clause_id_target, param, val, label in sample_evaluations:
        for clause in clauses:
            if clause.clause_id == clause_id_target:
                for metric in clause.metrics:
                    if metric.parameter == param:
                        is_compliant = metric.evaluate(val)
                        status = "✅ COMPLIANT" if is_compliant else "❌ NON-COMPLIANT"
                        print(f"  • {label} [{clause.clause_id}]: Test value = {val} {metric.unit}")
                        print(f"    Rule       : {metric.name} ({metric.parameter} {metric.operator} {metric.threshold})")
                        print(f"    Status     : {status}")
                        if not is_compliant and metric.remediation:
                            print(f"    Remediation: {metric.remediation.message_en}")

    # 3. Material Pricing & Embodied Carbon BOQ Generation
    print("\n[Step 3] Material Cost Breakdown (CGD v480) & Carbon Metrics...")
    materials_to_estimate = [
        ("MAT-CONCRETE-240-CUBE", 15.0),  # 15 cu.m
        ("MAT-REBAR-DB12", 1200.0),      # 1,200 kg
        ("MASONRY_AAC_75MM", 85.0),       # 85 sq.m
    ]

    total_cost_thb = 0.0
    total_carbon_co2e = 0.0

    print("  " + "-" * 62)
    print(f"  {'Material Name':<32} | {'Qty':<6} | {'Cost (THB)':<10} | {'Carbon (kgCO2e)'}")
    print("  " + "-" * 62)

    for mat_ref, qty in materials_to_estimate:
        item = get_material_price(mat_ref)
        if item:
            cost_amount = (item.cost.total_price * qty) if item.cost else 0.0
            carbon_amount = (item.carbon.embodied_carbon * qty) if item.carbon else 0.0
            total_cost_thb += cost_amount
            total_carbon_co2e += carbon_amount
            print(f"  {item.name_en[:32]:<32} | {qty:<6.1f} | {cost_amount:<10.2f} | {carbon_amount:.2f}")

    print("  " + "-" * 62)
    print(f"  TOTAL ESTIMATED BOQ COST : THB {total_cost_thb:,.2f}")
    print(f"  TOTAL EMBODIED CARBON    : {total_carbon_co2e:,.2f} kgCO2e")
    print("=" * 70)


if __name__ == "__main__":
    run_debim_derive_integration_showcase()
