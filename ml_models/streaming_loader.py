"""
AeroTwin MoE — Streaming Data Loader
Loads 110 GB real-world datasets in chunks (Parquet/CSV)
Maps heterogeneous datasets to unified 27-parameter AeroTwin feature space.
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Iterator, List, Dict, Optional
from pathlib import Path

# ── 27 Unified AeroTwin Parameters ────────────────────────────────────────────
AEROTWIN_27_PARAMS = [
    # Performance (E1) — 6 params
    "rpm", "power_output_kw", "torque_nm", "manifold_pressure_hpa",
    "throttle_pct", "combustion_efficiency_pct",
    # Fault Signatures (E2) — 6 params
    "cht_max", "egt_max", "res_cht_spread", "res_egt_spread",
    "vibration_g", "lambda_afr",
    # Health Indicators (E3) — 4 params
    "oil_temperature_c", "oil_pressure_bar",
    "coolant_temperature_c", "fuel_flow_lph",
    # RUL Features (E4) — 3 params
    "engine_hours_used", "res_map_residual", "res_oil_press_residual",
    # Operating Conditions (E5) — 4 params
    "altitude_m", "ambient_temp_c", "fuel_pressure_bar", "bus_voltage_v",
    # Cross-Engine (E6) — 2 params
    "turbo_rpm", "injection_pulse_width_ms",
    # Physics Residuals (E7) — 2 params
    "ignition_timing_btdc", "injection_timing_btdc",
]

assert len(AEROTWIN_27_PARAMS) == 27, f"Expected 27 params, got {len(AEROTWIN_27_PARAMS)}"

# ── Dataset Registry: maps real datasets to AeroTwin features ─────────────────
DATASET_REGISTRY = {
    "nasa_cmapss": {
        "path": r"D:\AeroTwin_Datasets\unpacked\nasa_cmapss",
        "expert_tags": ["E1_performance", "E4_rul"],
        "col_map": {
            # CMAPSS sensor → AeroTwin param
            "s2":  "manifold_pressure_hpa",   # Total pressure at fan inlet
            "s3":  "oil_temperature_c",        # Total temperature at HPC outlet
            "s4":  "oil_pressure_bar",         # Total pressure at HPC outlet (scaled)
            "s7":  "fuel_flow_lph",            # Total pressure at fan inlet (scaled)
            "s8":  "combustion_efficiency_pct",# Static pressure at fan inlet (scaled)
            "s9":  "vibration_g",              # Ratio of fuel flow to Ps30
            "s11": "coolant_temperature_c",    # Static temperature at HPC outlet
            "s12": "power_output_kw",          # Ratio of bypass to core
            "s13": "egt_max",                  # Total temperature at fan inlet
            "s14": "rpm",                      # Core RPM (normalized)
            "s15": "throttle_pct",             # Bypass Ratio
            "RUL": "engine_hours_used",        # RUL as proxy for hours
        },
        "fault_col": None,
        "rul_col": "RUL",
        "chunk_size": 50000,
    },
    "nasa_cmapss2": {
        "path": r"D:\AeroTwin_Datasets\unpacked\nasa_cmapss2",
        "expert_tags": ["E1_performance", "E4_rul"],
        "col_map": {
            "s2": "manifold_pressure_hpa", "s3": "oil_temperature_c",
            "s4": "power_output_kw", "s7": "fuel_flow_lph",
            "s9": "vibration_g", "s11": "coolant_temperature_c",
            "s14": "rpm", "s15": "throttle_pct", "RUL": "engine_hours_used",
        },
        "fault_col": None, "rul_col": "RUL", "chunk_size": 50000,
    },
    "cwru_bearing": {
        "path": r"D:\AeroTwin_Datasets\unpacked\cwru-mat-full-dataset",
        "expert_tags": ["E2_fault", "E3_health"],
        "col_map": {"__rms_col__": "vibration_g", "__mat_fault_from_filename__": "fault_label"},
        "fault_col": "__label_col__", "rul_col": None, "chunk_size": 30000,
    },
    "mfpt_bearing": {
        "path": r"D:\AeroTwin_Datasets\unpacked\MFPT",
        "expert_tags": ["E2_fault", "E3_health"],
        "col_map": {"__rms_col__": "vibration_g", "__mat_fault_from_filename__": "fault_label"},
        "fault_col": "__label_col__", "rul_col": None, "chunk_size": 20000,
    },
    "hust_bearing": {
        "path": r"D:\AeroTwin_Datasets\unpacked\hust-bearing",
        "expert_tags": ["E2_fault", "E3_health"],
        "col_map": {"__rms_col__": "vibration_g", "__mat_fault_from_filename__": "fault_label"},
        "fault_col": "__label_col__", "rul_col": None, "chunk_size": 30000,
    },
    "femto_bearing": {
        "path": r"D:\AeroTwin_Datasets\unpacked\FEMTOBearingDataSet",
        "expert_tags": ["E3_health", "E4_rul"],
        "col_map": {"__rms_col__": "vibration_g"},
        "fault_col": None, "rul_col": "__rul_from_end__", "chunk_size": 20000,
    },
    "paderborn_bearing": {
        "path": r"C:\AeroTwin_Paderborn",
        "expert_tags": ["E2_fault", "E3_health"],
        "col_map": {"__rms_col__": "vibration_g", "__mat_fault_from_filename__": "fault_label"},
        "fault_col": "__label_col__", "rul_col": None, "chunk_size": 30000,
    },
    "xjtu_bearing": {
        "path": r"D:\AeroTwin_Datasets\unpacked\XJTU-SY_Bearing_Datasets",
        "expert_tags": ["E2_fault", "E3_health", "E4_rul"],
        "col_map": {"__rms_col__": "vibration_g", "__mat_fault_from_filename__": "fault_label"},
        "fault_col": "__label_col__", "rul_col": "__rul_from_end__", "chunk_size": 20000,
    },
    "nasa_cmapss_txt": {
        "path": r"D:\AeroTwin_Datasets\unpacked\CMAPSSData",
        "expert_tags": ["E1_performance", "E4_rul"],
        "col_map": {
            "s2":  "manifold_pressure_hpa", "s3": "oil_temperature_c",
            "s4":  "oil_pressure_bar",       "s7": "fuel_flow_lph",
            "s9":  "vibration_g",            "s11": "coolant_temperature_c",
            "s12": "power_output_kw",        "s14": "rpm",
            "s15": "throttle_pct",
        },
        "fault_col": None, "rul_col": None, "chunk_size": 50000,
    },
    "nasa_cmapss2_h5": {
        "path": r"D:\AeroTwin_Datasets\unpacked\nasa_cmapss2",
        "expert_tags": ["E1_performance", "E4_rul"],
        "col_map": {"__rms_col__": "vibration_g"},
        "fault_col": None, "rul_col": "RUL", "chunk_size": 50000,
    },
    "subf_v1_bearing": {
        "path": r"D:\AeroTwin_Datasets\unpacked\subf-v1-0-dataset-bearing-fault-vibration-data",
        "expert_tags": ["E2_fault", "E3_health"],
        "col_map": {"__rms_col__": "vibration_g"},
        "fault_col": "__label_col__", "rul_col": None, "chunk_size": 30000,
    },
    "subf_v2_bearing": {
        "path": r"D:\AeroTwin_Datasets\unpacked\subf-v2-0-dataset-bearing-faults-sound-data",
        "expert_tags": ["E2_fault"],
        "col_map": {"__rms_col__": "vibration_g"},
        "fault_col": "__label_col__", "rul_col": None, "chunk_size": 20000,
    },
    "bispectrum_signal": {
        "path": r"D:\AeroTwin_Datasets\unpacked\bispectrum-signal",
        "expert_tags": ["E1_performance", "E5_operating"],
        "col_map": {"__rms_col__": "vibration_g"},
        "fault_col": None, "rul_col": None, "chunk_size": 50000,
    },
    "drone_telemetry": {
        "path": r"D:\AeroTwin_Datasets\unpacked\drone-telemetry-tampering-dataset-v2",
        "expert_tags": ["E5_operating", "E6_cross_engine"],
        "col_map": {
            "altitude": "altitude_m", "throttle": "throttle_pct",
            "rpm": "rpm", "voltage": "bus_voltage_v",
        },
        "fault_col": "label", "rul_col": None, "chunk_size": 30000,
    },
    "snu_gearbox": {
        "path": r"D:\AeroTwin_Datasets\unpacked\SNU_Gearbox_code",
        "expert_tags": ["E2_fault", "E6_cross_engine"],
        "col_map": {"__rms_col__": "vibration_g"},
        "fault_col": "__label_col__", "rul_col": None, "chunk_size": 20000,
    },
    "electric_motor_temp": {
        "path": r"D:\AeroTwin_Datasets\unpacked\electric_motor_temp",
        "expert_tags": ["E3_health", "E6_cross_engine"],
        "col_map": {
            "coolant": "coolant_temperature_c", "u_q": "bus_voltage_v",
            "motor_speed": "rpm", "torque": "torque_nm",
            "pm": "oil_temperature_c", "stator_tooth": "egt_max",
        },
        "fault_col": None, "rul_col": None, "chunk_size": 50000,
    },
    "gearbox_phm_nasa": {
        "path": r"D:\AeroTwin_Datasets\unpacked\gearbox-fault-detection-dataset-phm-2009-nasa",
        "expert_tags": ["E4_rul", "E2_fault"],
        "col_map": {"__rms_col__": "vibration_g"},
        "fault_col": "__label_col__", "rul_col": None, "chunk_size": 20000,
    },
    "aviation_accident": {
        "path": r"D:\AeroTwin_Datasets\unpacked\aviation-accident-ntsb",
        "expert_tags": ["E5_operating"],
        "col_map": {},
        "fault_col": "AmateurBuilt", "rul_col": None, "chunk_size": 10000,
    },
    "drone_sound_fault": {
        "path": r"D:\AeroTwin_Datasets\unpacked\drone_sound_fault_2023",
        "expert_tags": ["E5_operating", "E2_fault"],
        "col_map": {"__rms_col__": "vibration_g"},
        "fault_col": "__label_col__", "rul_col": None, "chunk_size": 20000,
    },
    "aero_engine_synth": {
        "path": r"ml_models/data/aero_engine_telemetry.csv",  # Our physics-generated data
        "expert_tags": ["E1_performance", "E2_fault", "E3_health", "E4_rul", "E5_operating", "E6_cross_engine", "E7_physics"],
        "col_map": {
            "rpm": "rpm", "power_output_kw": "power_output_kw",
            "torque_nm": "torque_nm", "manifold_pressure_hpa": "manifold_pressure_hpa",
            "throttle_pct": "throttle_pct",
            "combustion_efficiency_pct": "combustion_efficiency_pct",
            "oil_temperature_c": "oil_temperature_c",
            "oil_pressure_bar": "oil_pressure_bar",
            "coolant_temperature_c": "coolant_temperature_c",
            "fuel_flow_lph": "fuel_flow_lph",
            "engine_hours_used": "engine_hours_used",
            "altitude_m": "altitude_m", "ambient_temp_c": "ambient_temp_c",
            "fuel_pressure_bar": "fuel_pressure_bar", "bus_voltage_v": "bus_voltage_v",
            "turbo_rpm": "turbo_rpm",
            "injection_pulse_width_ms": "injection_pulse_width_ms",
            "ignition_timing_btdc": "ignition_timing_btdc",
            "injection_timing_btdc": "injection_timing_btdc",
        },
        "fault_col": "fault_code", "rul_col": "rul_hours", "chunk_size": 100000,
    },
}

# ── Nominal defaults for missing parameters ────────────────────────────────────
NOMINAL_DEFAULTS = {
    "rpm": 5000.0, "power_output_kw": 65.0, "torque_nm": 120.0,
    "manifold_pressure_hpa": 1150.0, "throttle_pct": 75.0,
    "combustion_efficiency_pct": 92.5, "cht_max": 111.5, "egt_max": 812.0,
    "res_cht_spread": 2.5, "res_egt_spread": 5.0, "vibration_g": 1.4,
    "lambda_afr": 1.02, "oil_temperature_c": 90.0, "oil_pressure_bar": 3.8,
    "coolant_temperature_c": 88.0, "fuel_flow_lph": 18.5,
    "engine_hours_used": 50.0, "res_map_residual": 0.0, "res_oil_press_residual": 0.0,
    "altitude_m": 1500.0, "ambient_temp_c": 15.0, "fuel_pressure_bar": 3.0,
    "bus_voltage_v": 28.1, "turbo_rpm": 110000.0, "injection_pulse_width_ms": 3.8,
    "ignition_timing_btdc": 26.0, "injection_timing_btdc": 8.5,
}


class AeroTwinStreamingLoader:
    """
    Streaming loader for 110 GB real-world datasets.
    Converts heterogeneous sensor data → unified 27-parameter AeroTwin feature space.
    """

    def __init__(self, datasets_to_load: Optional[List[str]] = None):
        self.registry    = DATASET_REGISTRY
        self.params      = AEROTWIN_27_PARAMS
        self.defaults    = NOMINAL_DEFAULTS
        self.load_these  = datasets_to_load or list(self.registry.keys())

    def _find_data_files(self, folder: str, limit: int = 20) -> List[str]:
        """Recursively find all supported data files in a folder."""
        files = []
        if not os.path.exists(folder):
            return files
        for root, _, fnames in os.walk(folder):
            for f in fnames:
                if f.endswith(('.csv', '.parquet', '.txt', '.dat', '.mat', '.h5', '.hdf5')):
                    files.append(os.path.join(root, f))
        return sorted(files)[:limit]

    # Keep old name for backward compatibility
    def _find_csv_files(self, folder: str) -> List[str]:
        return self._find_data_files(folder)

    def _read_mat_file(self, fpath: str, chunk_size: int = 30000) -> List[pd.DataFrame]:
        """Read a .mat file and return list of DataFrames (chunked)."""
        try:
            import scipy.io as sio
        except ImportError:
            print("  [LOADER] scipy not installed — pip install scipy")
            return []
        chunks = []
        try:
            mat = sio.loadmat(fpath, squeeze_me=True)
            # Find numeric arrays
            arrays = {k: v for k, v in mat.items()
                      if not k.startswith('_') and isinstance(v, np.ndarray) and v.ndim >= 1}
            if not arrays:
                return []
            # Take largest numeric array as signal
            key = max(arrays, key=lambda k: arrays[k].size)
            data = arrays[key]
            if data.ndim == 1:
                data = data.reshape(-1, 1)
            elif data.ndim > 2:
                data = data.reshape(data.shape[0], -1)
            df = pd.DataFrame(data.astype(np.float32))
            df.columns = [f"ch{i}" for i in range(df.shape[1])]
            # Chunk it
            for start in range(0, len(df), chunk_size):
                chunks.append(df.iloc[start:start+chunk_size].copy())
        except Exception as e:
            print(f"  [LOADER WARN] .mat read error {os.path.basename(fpath)}: {e}")
        return chunks

    def _read_h5_file(self, fpath: str, chunk_size: int = 50000) -> List[pd.DataFrame]:
        """Read a .h5/.hdf5 file and return list of DataFrames."""
        chunks = []
        try:
            import h5py
            with h5py.File(fpath, 'r') as f:
                def collect_arrays(name, obj):
                    if isinstance(obj, h5py.Dataset) and obj.ndim >= 1:
                        try:
                            arr = obj[()]
                            if arr.dtype.kind in ('f', 'i', 'u') and arr.size > 100:
                                df = pd.DataFrame(arr.astype(np.float32).reshape(-1, 1 if arr.ndim == 1 else arr.shape[-1]))
                                df.columns = [f"{name.replace('/','_')}_{i}" for i in range(df.shape[1])]
                                chunks.append(df.head(chunk_size))
                        except Exception:
                            pass
                f.visititems(collect_arrays)
        except ImportError:
            # Fallback: try pandas
            try:
                df = pd.read_hdf(fpath)
                for start in range(0, len(df), chunk_size):
                    chunks.append(df.iloc[start:start+chunk_size].copy())
            except Exception as e:
                print(f"  [LOADER WARN] .h5 read error {os.path.basename(fpath)}: {e}")
        except Exception as e:
            print(f"  [LOADER WARN] .h5 read error {os.path.basename(fpath)}: {e}")
        return chunks

    def _fault_label_from_filename(self, fpath: str) -> str:
        """Infer fault type from filename (CWRU/MFPT/Paderborn convention)."""
        fname = os.path.basename(fpath).lower()
        if any(x in fname for x in ['normal', 'health', 'baseline', 'good', 'no_', 'k001']):
            return 'Nominal'
        if any(x in fname for x in ['inner', 'ir', 'irp']):
            return 'Cylinder_Misfire'
        if any(x in fname for x in ['outer', 'or', 'orp']):
            return 'Turbo_Degradation'
        if any(x in fname for x in ['ball', 'roller', 'br', 'b']):
            return 'Combustion_Knock'
        if any(x in fname for x in ['cage', 'retain']):
            return 'Valve_Leakage'
        if any(x in fname for x in ['crack', 'spall', 'wear']):
            return 'Oil_Starvation'
        return 'Nominal'

    def _compute_rms(self, df: pd.DataFrame) -> pd.Series:
        """Compute RMS vibration from raw sensor channels."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            return pd.Series(np.ones(len(df)) * 1.4)
        rms = np.sqrt((df[numeric_cols] ** 2).mean(axis=1))
        # Normalize to g-range (0.5 - 5.0 g)
        rms_min, rms_max = rms.min(), rms.max()
        if rms_max > rms_min:
            rms = 0.5 + (rms - rms_min) / (rms_max - rms_min) * 4.5
        else:
            rms = pd.Series(np.ones(len(df)) * 1.4)
        return rms

    def _apply_col_map(self, df: pd.DataFrame, col_map: dict, dataset_id: str) -> pd.DataFrame:
        """Map raw dataset columns → AeroTwin 27 parameters."""
        out = pd.DataFrame(index=df.index)

        # Fill all params with nominal defaults first
        for param in self.params:
            out[param] = self.defaults.get(param, 0.0)

        # Apply explicit column mappings
        for src_col, dst_param in col_map.items():
            if src_col == "__rms_col__":
                out["vibration_g"] = self._compute_rms(df)
            elif src_col == "__label_col__":
                pass  # handled separately
            elif src_col in df.columns:
                raw = pd.to_numeric(df[src_col], errors='coerce').fillna(self.defaults.get(dst_param, 0.0))
                # Normalize to AeroTwin units where needed
                out[dst_param] = self._normalize_to_aerotwin(raw, dst_param)

        return out[self.params]

    def _normalize_to_aerotwin(self, series: pd.Series, param: str) -> pd.Series:
        """Soft normalization — brings external sensor ranges into AeroTwin units."""
        s = series.copy()
        # Normalize RPM (CMAPSS RPM is normalized 0-1, scale to 2000-6000)
        if param == "rpm" and s.max() <= 2.0:
            s = 2000 + s * 4000
        # Normalize power (if in watts, convert to kW)
        if param == "power_output_kw" and s.max() > 1000:
            s = s / 1000.0
        # Normalize pressure (if in Pa, convert to hPa)
        if param == "manifold_pressure_hpa" and s.max() > 5000:
            s = s / 100.0
        # Clamp to reasonable ranges
        ranges = {
            "rpm": (0, 8000), "power_output_kw": (0, 200), "torque_nm": (0, 500),
            "manifold_pressure_hpa": (600, 2000), "throttle_pct": (0, 100),
            "combustion_efficiency_pct": (50, 100), "vibration_g": (0.1, 20.0),
            "oil_temperature_c": (20, 200), "oil_pressure_bar": (0, 10),
            "coolant_temperature_c": (20, 200), "fuel_flow_lph": (0, 100),
            "engine_hours_used": (0, 2000), "altitude_m": (0, 15000),
            "ambient_temp_c": (-40, 60), "bus_voltage_v": (20, 35),
            "turbo_rpm": (0, 300000),
        }
        if param in ranges:
            lo, hi = ranges[param]
            s = s.clip(lo, hi)
        return s

    def _extract_fault_label(self, df: pd.DataFrame, fault_col: str, dataset_id: str) -> pd.Series:
        """Extract fault label, mapping to AeroTwin fault classes."""
        FAULT_MAP = {
            # Generic keywords → AeroTwin fault classes
            "normal": "Nominal", "healthy": "Nominal", "0": "Nominal", 0: "Nominal",
            "inner": "Cylinder_Misfire", "inner_race": "Cylinder_Misfire",
            "outer": "Turbo_Degradation", "outer_race": "Turbo_Degradation",
            "ball": "Combustion_Knock", "roller": "Combustion_Knock",
            "cage": "Valve_Leakage",
            "1": "Cylinder_Misfire", 1: "Cylinder_Misfire",
            "2": "Turbo_Degradation", 2: "Turbo_Degradation",
            "3": "Oil_Starvation",    3: "Oil_Starvation",
            "4": "Coolant_Loss",      4: "Coolant_Loss",
            "tampered": "Combustion_Knock", "anomaly": "Cylinder_Misfire",
        }
        if fault_col == "__label_col__":
            # Infer from folder/filename
            return pd.Series(["Nominal"] * len(df))

        if fault_col not in df.columns:
            return pd.Series(["Nominal"] * len(df))

        raw = df[fault_col].astype(str).str.lower().str.strip()
        labels = raw.map(lambda x: FAULT_MAP.get(x, FAULT_MAP.get(x.split('_')[0], "Nominal")))
        return labels

    def stream_dataset(self, dataset_id: str) -> Iterator[pd.DataFrame]:
        """
        Stream a single dataset in chunks.
        Yields DataFrames with 27 AeroTwin params + 'fault_label' + 'rul_hours'.
        """
        config = self.registry.get(dataset_id)
        if not config:
            return

        path = config["path"]
        col_map = config["col_map"]
        fault_col = config.get("fault_col")
        rul_col = config.get("rul_col")
        chunk_size = config.get("chunk_size", 50000)

        # Handle direct CSV path
        if path.endswith('.csv') and os.path.isfile(path):
            data_files = [path]
        else:
            data_files = self._find_data_files(path, limit=30)

        if not data_files:
            print(f"  [LOADER] No data files found for {dataset_id} at {path}")
            return

        for fpath in data_files:
            try:
                ext = os.path.splitext(fpath)[1].lower()

                if ext == '.mat':
                    # Infer fault from filename if needed
                    inferred_label = self._fault_label_from_filename(fpath)
                    for mat_chunk in self._read_mat_file(fpath, chunk_size):
                        processed = self._process_chunk(mat_chunk, col_map, fault_col, rul_col, dataset_id)
                        # Override label with filename-inferred label
                        if '__mat_fault_from_filename__' in col_map:
                            processed['fault_label'] = inferred_label
                        yield processed

                elif ext in ('.h5', '.hdf5'):
                    for h5_chunk in self._read_h5_file(fpath, chunk_size):
                        yield self._process_chunk(h5_chunk, col_map, fault_col, rul_col, dataset_id)

                elif ext == '.parquet':
                    df_full = pd.read_parquet(fpath, engine='pyarrow')
                    for start in range(0, len(df_full), chunk_size):
                        chunk = df_full.iloc[start:start+chunk_size]
                        yield self._process_chunk(chunk, col_map, fault_col, rul_col, dataset_id)

                else:
                    # CSV / TXT / DAT
                    sep = '\t' if ext in ('.txt', '.dat') else ','
                    for chunk in pd.read_csv(fpath, sep=sep, chunksize=chunk_size,
                                             on_bad_lines='skip', low_memory=False):
                        yield self._process_chunk(chunk, col_map, fault_col, rul_col, dataset_id)

            except Exception as e:
                print(f"  [LOADER WARN] {dataset_id}/{os.path.basename(fpath)}: {e}")
                continue

    def _process_chunk(self, chunk: pd.DataFrame, col_map: dict,
                       fault_col: Optional[str], rul_col: Optional[str],
                       dataset_id: str) -> pd.DataFrame:
        """Process one chunk: map columns + add labels."""
        out = self._apply_col_map(chunk, col_map, dataset_id)

        # Fault label
        if fault_col:
            out["fault_label"] = self._extract_fault_label(chunk, fault_col, dataset_id).values
        else:
            out["fault_label"] = "Nominal"

        # RUL
        if rul_col == "__rul_from_end__":
            # FEMTO-style: RUL = (total_len - current_idx)
            n = len(chunk)
            out["rul_hours"] = np.linspace(200, 0, n)
        elif rul_col and rul_col in chunk.columns:
            out["rul_hours"] = pd.to_numeric(chunk[rul_col], errors='coerce').fillna(200.0).values
        else:
            out["rul_hours"] = 875.0  # Default nominal RUL

        # Source tag
        out["source_dataset"] = dataset_id
        return out

    def stream_all_for_expert(self, expert_tag: str) -> Iterator[pd.DataFrame]:
        """
        Stream all datasets relevant to a specific expert.
        Expert tags: E1_performance, E2_fault, E3_health, E4_rul, E5_operating, E6_cross_engine, E7_physics
        """
        for ds_id, config in self.registry.items():
            if ds_id not in self.load_these:
                continue
            if expert_tag in config.get("expert_tags", []):
                print(f"  [LOADER] Streaming {ds_id} for {expert_tag}...")
                yield from self.stream_dataset(ds_id)

    def load_expert_dataset(self, expert_tag: str, max_rows: int = 200000) -> pd.DataFrame:
        """
        Load all data for one expert, capped at max_rows (memory safe).
        Returns unified 27-param DataFrame with fault_label + rul_hours.
        """
        chunks = []
        total = 0
        for chunk in self.stream_all_for_expert(expert_tag):
            chunks.append(chunk)
            total += len(chunk)
            if total >= max_rows:
                break

        if not chunks:
            print(f"  [LOADER] No data found for {expert_tag}, generating synthetic fallback...")
            return self._generate_synthetic_fallback(expert_tag, max_rows // 10)

        df = pd.concat(chunks, ignore_index=True)
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # Shuffle
        return df.head(max_rows)

    def _generate_synthetic_fallback(self, expert_tag: str, n: int = 10000) -> pd.DataFrame:
        """Generate synthetic data as fallback when real dataset unavailable."""
        np.random.seed(42)
        rows = {}
        for param in self.params:
            base = self.defaults.get(param, 1.0)
            rows[param] = np.random.normal(base, base * 0.1, n)
        df = pd.DataFrame(rows)
        df["fault_label"] = "Nominal"
        df["rul_hours"] = np.random.uniform(200, 1000, n)
        df["source_dataset"] = "synthetic_fallback"
        return df

    def get_dataset_summary(self) -> Dict:
        """Quick summary of available datasets."""
        summary = {}
        for ds_id, config in self.registry.items():
            path = config["path"]
            if path.endswith('.csv'):
                files = [path] if os.path.exists(path) else []
            else:
                files = self._find_data_files(path, limit=30)
            summary[ds_id] = {
                "available": len(files) > 0,
                "files_found": len(files),
                "expert_tags": config["expert_tags"],
                "path": path,
            }
        return summary


if __name__ == "__main__":
    print("AeroTwin Streaming Loader — Dataset Availability Check")
    print("=" * 60)
    loader = AeroTwinStreamingLoader()
    summary = loader.get_dataset_summary()
    available = 0
    for ds_id, info in summary.items():
        status = "✅" if info["available"] else "❌"
        print(f"  {status} {ds_id:35} | Files: {info['files_found']:3} | Tags: {', '.join(info['expert_tags'])}")
        if info["available"]:
            available += 1
    print(f"\n  Available: {available}/{len(summary)} datasets")
    print(f"  Parameters: {len(AEROTWIN_27_PARAMS)} unified features")
    print(f"  Parameters: {AEROTWIN_27_PARAMS}")
