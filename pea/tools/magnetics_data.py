"""
Magnetic core and material data for inductor and transformer design.

Core dimensions are in mm/mm² unless noted.  Steinmetz parameters use
the *improved* generalized form: Pv = k · f^α · ΔB^β  (W/m³) where
f is in Hz and ΔB in mT.  Values are approximate datasheet fits for
the dominant frequency range listed.

Sources:
- TDK/EPCOS ferrite datasheets (N87, N97)
- Ferroxcube datasheets (3C90, 3C95, 3F3)
- TDK PC-series datasheets (PC40, PC95)
- Standard core dimension tables from manufacturer catalogs

Core dict keys:
    Ae   – effective cross-section area (mm²)
    le   – effective magnetic path length (mm)
    Ve   – effective volume (mm³)
    Aw   – window area (mm²)
    Al   – inductance factor (nH/turn²), ungapped
"""

from __future__ import annotations

CORE_DATA: dict[str, dict] = {
    "EE": {
        "sizes": [
            {"name": "EE16",  "Ae": 20.1, "le": 34.7, "Ve": 697,   "Aw": 19.3, "Al": 1600},
            {"name": "EE19",  "Ae": 22.6, "le": 39.4, "Ve": 890,   "Aw": 26.4, "Al": 1750},
            {"name": "EE25",  "Ae": 39.4, "le": 57.8, "Ve": 2278,  "Aw": 47.4, "Al": 2100},
            {"name": "EE30",  "Ae": 58.1, "le": 67.2, "Ve": 3904,  "Aw": 74.8, "Al": 2400},
            {"name": "EE40",  "Ae": 81,   "le": 96,   "Ve": 7776,  "Aw": 121,  "Al": 2800},
            {"name": "EE42",  "Ae": 178,  "le": 97,   "Ve": 17266, "Aw": 213,  "Al": 4000},
            {"name": "EE55",  "Ae": 250,  "le": 124,  "Ve": 31000, "Aw": 362,  "Al": 4700},
            {"name": "EE65",  "Ae": 330,  "le": 147,  "Ve": 48510, "Aw": 495,  "Al": 5200},
        ],
    },
    "PQ": {
        "sizes": [
            {"name": "PQ20/20", "Ae": 62,  "le": 46, "Ve": 2852,  "Aw": 40,  "Al": 3100},
            {"name": "PQ26/25", "Ae": 119, "le": 56, "Ve": 6664,  "Aw": 69,  "Al": 4600},
            {"name": "PQ32/30", "Ae": 162, "le": 70, "Ve": 11340, "Aw": 104, "Al": 5300},
            {"name": "PQ40/40", "Ae": 202, "le": 88, "Ve": 17776, "Aw": 145, "Al": 5900},
        ],
    },
    "RM": {
        "sizes": [
            {"name": "RM8",  "Ae": 52,  "le": 38, "Ve": 1976, "Aw": 26, "Al": 2700},
            {"name": "RM10", "Ae": 83,  "le": 44, "Ve": 3652, "Aw": 44, "Al": 3400},
            {"name": "RM12", "Ae": 116, "le": 52, "Ve": 6032, "Aw": 61, "Al": 4200},
            {"name": "RM14", "Ae": 157, "le": 60, "Ve": 9420, "Aw": 83, "Al": 4800},
        ],
    },
    "toroid": {
        "sizes": [
            {"name": "T25/15/10", "Ae": 45,  "le": 62,  "Ve": 2790,  "Aw": 177, "Al": 2300},
            {"name": "T36/23/15", "Ae": 98,  "le": 92,  "Ve": 9016,  "Aw": 415, "Al": 3200},
            {"name": "T50/30/19", "Ae": 154, "le": 125, "Ve": 19250, "Aw": 707, "Al": 3800},
        ],
    },
    "EI": {
        "sizes": [
            {"name": "EI30", "Ae": 48, "le": 68, "Ve": 3264, "Aw": 55,  "Al": 2200},
            {"name": "EI40", "Ae": 80, "le": 96, "Ve": 7680, "Aw": 110, "Al": 2700},
        ],
    },
    "EP": {
        "sizes": [
            {"name": "EP13", "Ae": 17.1, "le": 30, "Ve": 513,  "Aw": 12.4, "Al": 1500},
            {"name": "EP17", "Ae": 24.5, "le": 37, "Ve": 907,  "Aw": 17.7, "Al": 1800},
            {"name": "EP20", "Ae": 31.2, "le": 43, "Ve": 1342, "Aw": 23.8, "Al": 2000},
        ],
    },
    "ETD": {
        "sizes": [
            {"name": "ETD29", "Ae": 76,  "le": 72,  "Ve": 5472,  "Aw": 90,  "Al": 3100},
            {"name": "ETD34", "Ae": 97,  "le": 78,  "Ve": 7566,  "Aw": 119, "Al": 3600},
            {"name": "ETD39", "Ae": 125, "le": 92,  "Ve": 11500, "Aw": 177, "Al": 4200},
            {"name": "ETD44", "Ae": 173, "le": 103, "Ve": 17819, "Aw": 214, "Al": 4900},
            {"name": "ETD49", "Ae": 211, "le": 114, "Ve": 24054, "Aw": 268, "Al": 5300},
        ],
    },
    "EFD": {
        "sizes": [
            {"name": "EFD15", "Ae": 14.8, "le": 33, "Ve": 488,  "Aw": 14, "Al": 1400},
            {"name": "EFD20", "Ae": 31,   "le": 47, "Ve": 1457, "Aw": 22, "Al": 2100},
            {"name": "EFD25", "Ae": 40,   "le": 57, "Ve": 2280, "Aw": 33, "Al": 2500},
            {"name": "EFD30", "Ae": 69,   "le": 68, "Ve": 4692, "Aw": 52, "Al": 3200},
        ],
    },
}

MAT_DATA: dict[str, dict] = {
    "N87": {
        "bsat": 390,
        "f_range": "25k-500k",
        "mu_i": 2200,
        "steinmetz": {"k": 1.2e-6, "alpha": 1.46, "beta": 2.75},
        "description": "General-purpose MnZn ferrite, good from 25 kHz to 500 kHz.",
    },
    "N97": {
        "bsat": 410,
        "f_range": "25k-500k",
        "mu_i": 2300,
        "steinmetz": {"k": 0.8e-6, "alpha": 1.52, "beta": 2.73},
        "description": "Low-loss MnZn ferrite, suited for high-power converters.",
    },
    "3C90": {
        "bsat": 380,
        "f_range": "25k-200k",
        "mu_i": 2300,
        "steinmetz": {"k": 1.5e-6, "alpha": 1.36, "beta": 2.86},
        "description": "Ferroxcube general-purpose, 25-200 kHz.",
    },
    "3C95": {
        "bsat": 410,
        "f_range": "25k-500k",
        "mu_i": 3000,
        "steinmetz": {"k": 0.9e-6, "alpha": 1.48, "beta": 2.78},
        "description": "Ferroxcube low-loss, wide frequency range.",
    },
    "3F3": {
        "bsat": 380,
        "f_range": "100k-1M",
        "mu_i": 2000,
        "steinmetz": {"k": 0.6e-6, "alpha": 1.64, "beta": 2.68},
        "description": "Ferroxcube high-frequency ferrite (100 kHz–1 MHz).",
    },
    "PC40": {
        "bsat": 390,
        "f_range": "25k-500k",
        "mu_i": 2300,
        "steinmetz": {"k": 1.1e-6, "alpha": 1.44, "beta": 2.8},
        "description": "TDK general-purpose MnZn ferrite.",
    },
    "PC95": {
        "bsat": 380,
        "f_range": "100k-1M",
        "mu_i": 2500,
        "steinmetz": {"k": 0.5e-6, "alpha": 1.7, "beta": 2.6},
        "description": "TDK high-frequency low-loss ferrite.",
    },
}


def get_available_core_shapes() -> list[str]:
    """Return list of available core shape names."""
    return list(CORE_DATA.keys())


def get_available_materials() -> list[str]:
    """Return list of available material names."""
    return list(MAT_DATA.keys())


def get_material_info(name: str) -> dict | None:
    """Return material properties or None."""
    return MAT_DATA.get(name)


def get_core_sizes(shape: str) -> list[dict] | None:
    """Return list of core sizes for a given shape, or None."""
    info = CORE_DATA.get(shape)
    return info["sizes"] if info else None
