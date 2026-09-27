"""
AeroTwin MoE — Expert Dataset Preparation
Reads real datasets via StreamingLoader and saves per-expert Parquet files.

Output:
  ml_models/data/experts/
    E1_performance.parquet
    E2_fault.parquet
    E3_health.parquet
    E4_rul.parquet
    E5_operating.parquet
    E6_cross_engine.parquet
    E7_physics.parquet
    dataset_stats.json
"""

import os, sys, json, time
import numpy as np
import pandas as pd
sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_models.streaming_loader import AeroTwinStreamingLoader, AEROTWIN_27_PARAMS

# ── Config ────────────────────────────────────────────────────────────────────
OUT_DIR   = os.path.join(os.path.dirname(__file__), "data", "experts")
MAX_ROWS  = 300_000   # per expert (memory safe)
os.makedirs(OUT_DIR, exist_ok=True)

EXPERTS = [
    ("E1_performance",  "E1_performance",  "Performance — RPM, Power, Torque, MAP"),
    ("E2_fault",        "E2_fault",        "Fault Classification — CWRU, MFPT, Paderborn, XJTU"),
    ("E3_health",       "E3_health",       "Health Index — Oil, Coolant, FEMTO"),
    ("E4_rul",          "E4_rul",          "Remaining Useful Life — NASA CMAPSS"),
    ("E5_operating",    "E5_operating",    "Operating Conditions — Altitude, Temp, Drone"),
    ("E6_cross_engine", "E6_cross_engine", "Cross-Engine — ROTAX/AUSTRO/LYCOMING transfer"),
    ("E7_physics",      "E7_physics",      "Physics Model — Physics-informed residuals"),
]


def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def prepare_expert(loader, expert_id, expert_tag, description, max_rows):
    """Load, clean, and save one expert's dataset."""
    t0 = time.time()
    print(f"\n[{expert_id}] {description}")
    print(f"  Loading data (max {max_rows:,} rows)...")

    df = loader.load_expert_dataset(expert_tag, max_rows=max_rows)

    if df is None or len(df) == 0:
        print(f"  ⚠  No data found — generating synthetic fallback")
        df = loader._generate_synthetic_fallback(expert_tag, n=10000)

    # ── Clean up ────────────────────────────────────────────────────────────
    # Keep 27 params + labels
    keep_cols = AEROTWIN_27_PARAMS + ["fault_label", "rul_hours", "source_dataset"]
    df = df[[c for c in keep_cols if c in df.columns]]

    # Fill missing label columns
    if "fault_label"    not in df.columns: df["fault_label"]    = "Nominal"
    if "rul_hours"      not in df.columns: df["rul_hours"]      = 875.0
    if "source_dataset" not in df.columns: df["source_dataset"] = "unknown"

    # Drop fully-null rows
    feature_cols = [c for c in AEROTWIN_27_PARAMS if c in df.columns]
    df = df.dropna(subset=feature_cols, how="all")

    # Fill remaining NaNs with column median
    for col in feature_cols:
        if df[col].isna().any():
            df[col] = df[col].fillna(df[col].median())

    # ── Fault label distribution ─────────────────────────────────────────────
    label_dist = df["fault_label"].value_counts().to_dict()

    # ── Save as Parquet ──────────────────────────────────────────────────────
    out_path = os.path.join(OUT_DIR, f"{expert_id}.parquet")
    df.to_parquet(out_path, index=False, engine="pyarrow", compression="snappy")
    sz_mb = os.path.getsize(out_path) / 1024**2

    elapsed = time.time() - t0
    print(f"  ✅ {len(df):>8,} rows | {len(df.columns)} cols | {sz_mb:.1f} MB | {elapsed:.1f}s")
    print(f"     Sources: {df['source_dataset'].unique().tolist()}")
    print(f"     Labels:  {dict(list(label_dist.items())[:5])}")

    return {
        "expert":       expert_id,
        "description":  description,
        "rows":         len(df),
        "cols":         len(df.columns),
        "size_mb":      round(sz_mb, 2),
        "sources":      df["source_dataset"].unique().tolist(),
        "fault_labels": label_dist,
        "rul_mean":     round(df["rul_hours"].mean(), 1),
        "rul_std":      round(df["rul_hours"].std(), 1),
        "features":     feature_cols,
        "parquet_path": out_path,
        "elapsed_s":    round(elapsed, 1),
    }


def main():
    print_section("AeroTwin MoE — Expert Dataset Preparation")
    print(f"  Output dir: {OUT_DIR}")
    print(f"  Max rows per expert: {MAX_ROWS:,}")
    print(f"  Experts: {len(EXPERTS)}")

    loader = AeroTwinStreamingLoader()

    # Show dataset availability first
    print_section("Dataset Availability Check")
    summary = loader.get_dataset_summary()
    available = sum(1 for v in summary.values() if v["available"])
    print(f"  Available: {available}/{len(summary)} datasets")
    for ds_id, info in summary.items():
        status = "✅" if info["available"] else "❌"
        print(f"  {status} {ds_id:40} files:{info['files_found']:3} -> {', '.join(info['expert_tags'])}")

    # Prepare each expert dataset
    print_section("Loading & Saving Expert Datasets")
    stats = []
    total_t0 = time.time()

    for expert_id, expert_tag, description in EXPERTS:
        out_path = os.path.join(OUT_DIR, f"{expert_id}.parquet")

        # Skip if already exists and recent (< 1 day old)
        if os.path.exists(out_path):
            age_h = (time.time() - os.path.getmtime(out_path)) / 3600
            sz_mb = os.path.getsize(out_path) / 1024**2
            rows = pd.read_parquet(out_path).shape[0]
            if age_h < 0 and rows > 1000:  # Cache disabled — always refresh
                print(f"\n[{expert_id}] Already prepared ({rows:,} rows, {sz_mb:.1f} MB, {age_h:.1f}h ago) — SKIP")
                stats.append({
                    "expert": expert_id, "description": description,
                    "rows": rows, "size_mb": round(sz_mb, 2),
                    "status": "cached",
                })
                continue

        stat = prepare_expert(loader, expert_id, expert_tag, description, MAX_ROWS)
        stat["status"] = "prepared"
        stats.append(stat)

    # ── Summary ──────────────────────────────────────────────────────────────
    total_elapsed = time.time() - total_t0
    print_section("SUMMARY")
    total_rows = sum(s.get("rows", 0) for s in stats)
    total_mb   = sum(s.get("size_mb", 0) for s in stats)

    print(f"  {'Expert':<20} {'Rows':>10} {'Size':>8} {'Status'}")
    print(f"  {'-'*55}")
    for s in stats:
        print(f"  {s['expert']:<20} {s.get('rows',0):>10,} {s.get('size_mb',0):>7.1f}MB  {s.get('status','?')}")
    print(f"  {'-'*55}")
    print(f"  {'TOTAL':<20} {total_rows:>10,} {total_mb:>7.1f}MB")
    print(f"\n  Time elapsed: {total_elapsed:.1f}s")
    print(f"  Output: {OUT_DIR}")

    # Save stats JSON
    stats_path = os.path.join(OUT_DIR, "dataset_stats.json")
    with open(stats_path, "w") as f:
        json.dump({
            "prepared_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_rows":  total_rows,
            "total_mb":    total_mb,
            "experts":     stats,
        }, f, indent=2)
    print(f"  Stats: {stats_path}")
    print(f"\n✅ Expert datasets ready — now run train_moe.py")


if __name__ == "__main__":
    main()
