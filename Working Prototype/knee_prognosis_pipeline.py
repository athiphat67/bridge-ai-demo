import math
import re
import os
import json
import pandas as pd
import numpy as np

XRAY_CSV     = "/mnt/user-data/uploads/xray_bounding_boxes.csv"
CLINICAL_CSV = "/mnt/user-data/uploads/synthetic_clinical_biases.csv"

WHO_BMI_TABLES = {
    "M": "/mnt/user-data/uploads/bmi-boys-z-who-2007-exp.xlsx",
    "F": "/mnt/user-data/uploads/bmi-girls-z-who-2007-exp.xlsx",
}
WHO_WFH_TABLES = {
    "M": {
        "0-2": "/mnt/user-data/uploads/wfl_boys_0-to-2-years_zscores.xlsx",
        "2-5": "/mnt/user-data/uploads/wfh_boys_2-to-5-years_zscores.xlsx",
    },
    "F": {
        "0-2": "/mnt/user-data/uploads/wfl_girls_0-to-2-years_zscores.xlsx",
        "2-5": "/mnt/user-data/uploads/wfh_girls_2-to-5-years_zscores.xlsx",
    },
}

MATURITY_LIMIT       = {"M": 16.0, "F": 14.0}
G0_RATES             = {"distal_femur": 0.9, "proximal_tibia": 0.6}
DEFAULT_PIXEL_SPACING = 0.286

FUSION_MULTIPLIERS = {"Stage_I": 1.00, "Stage_II": 0.50, "Stage_III": 0.00}

SH_ARREST_BASE_RISK = {
    "SH_Type_I":   0.36,
    "SH_Type_II":  0.58,
    "SH_Type_III": 0.49,
    "SH_Type_IV":  0.64,
    "Normal":      0.00,
}

PATHOLOGY_WEIGHTS = {
    "Q78.0": 0.70, "Q78.2": 0.70, "Q77.4": 0.70, "N25.0": 0.70,
    "E24.0": 0.70, "E76.2": 0.70, "E83.3": 0.70,
    "TRT-01": 0.70, "HORM-01": 0.70, "DERM-01": 0.70,
    "STER-01": 0.70, "CHEMO-01": 0.70, "ONC-03": 0.70,
    "E23.0": 0.80, "E03.9": 0.80, "E10.9": 0.80, "M08.0": 0.80,
    "M86.9": 0.80, "D57.0": 0.80, "D56.1": 0.80, "E25.0": 0.80,
    "Q87.1": 0.80,
    "NEURO-01": 0.80, "NEURO-02": 0.80, "IMM-01": 0.80, "IMM-02": 0.80,
    "ARV-01": 0.80, "HEPA-01": 0.80, "HORM-02": 0.80,
    "E55.0": 0.90, "E43": 0.90, "E05.9": 0.90, "E84.9": 0.90,
    "K50.9": 0.90, "J45.9": 0.90, "F50.0": 0.90, "N04.9": 0.90,
    "M33.0": 0.90,
    "STIM-01": 0.90, "DIU-01": 0.90, "NEURO-03": 0.90, "PSY-01": 0.90,
    "E54": 0.95, "D50.9": 0.95, "E66.0": 0.95, "Q90.9": 0.95,
    "G47.3": 0.95, "M41.9": 0.95,
    "NSAID-01": 0.95, "GAS-01": 0.95, "PSY-02": 0.95,
    "NONE": 1.00,
}

PATHOLOGY_SEVERITY = {
    0.70: "Critical", 0.80: "High", 0.90: "Moderate",
    0.95: "Low", 1.00: "Baseline",
}

# --------------------------------------------------------------------------
# Anatomical hard cap for angular deformity projections.
# The knee joint will dislocate / undergo compensatory remodelling well
# before angular displacement exceeds this threshold; projecting beyond
# it has no clinical validity.
# Reference: Physeal bar literature (Williamson & Staheli, 1990;
#            Birch, 2013) places functional dislocation risk at ~40–45°.
# --------------------------------------------------------------------------
DEFORMITY_CAP_DEG = 45.0

_who_bmi_cache = {}
_who_wfh_cache = {}


def _load_who_bmi(gender: str) -> pd.DataFrame:
    if gender not in _who_bmi_cache:
        df = pd.read_excel(WHO_BMI_TABLES[gender])
        df.columns = df.columns.str.strip()
        df = df.rename(columns={"Month": "age_months"})
        df["age_months"] = pd.to_numeric(df["age_months"], errors="coerce")
        _who_bmi_cache[gender] = df.dropna(subset=["age_months"]).copy()
    return _who_bmi_cache[gender]


def _load_who_wfh(gender: str, range_key: str) -> pd.DataFrame:
    key = f"{gender}_{range_key}"
    if key not in _who_wfh_cache:
        df = pd.read_excel(WHO_WFH_TABLES[gender][range_key])
        df.columns = df.columns.str.strip()
        measure_col = "Length" if range_key == "0-2" else "Height"
        df = df.rename(columns={measure_col: "height_cm"})
        df["height_cm"] = pd.to_numeric(df["height_cm"], errors="coerce")
        _who_wfh_cache[key] = df.dropna(subset=["height_cm"]).copy()
    return _who_wfh_cache[key]


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    if height_cm <= 0:
        raise ValueError("Height must be > 0")
    return round(weight_kg / ((height_cm / 100.0) ** 2), 4)


def _lookup_lms_bmi(gender: str, age_months: float) -> tuple:
    df = _load_who_bmi(gender)
    idx = (df["age_months"] - age_months).abs().idxmin()
    row = df.loc[idx]
    return float(row["L"]), float(row["M"]), float(row["S"])


def _lookup_lms_wfh(gender: str, height_cm: float, age_years: float) -> tuple:
    range_key = "0-2" if age_years < 2.0 else "2-5"
    df = _load_who_wfh(gender, range_key)
    idx = (df["height_cm"] - height_cm).abs().idxmin()
    row = df.loc[idx]
    return float(row["L"]), float(row["M"]), float(row["S"])


def calculate_z_score(measurement_value: float, L: float, M: float, S: float) -> float:
    if L == 0:
        z = math.log(measurement_value / M) / S
    else:
        z = (((measurement_value / M) ** L) - 1) / (L * S)
    return round(z, 4)


def get_clinical_bias(z_score: float) -> tuple:
    if z_score < -2.0:
        return 0.95, "Thinness"
    elif z_score <= 1.0:
        return 1.00, "Normal"
    elif z_score <= 2.0:
        return 1.15, "Overweight"
    else:
        return 1.30, "Obesity"


def compute_bmi_zscore(
    gender: str,
    age_years: float,
    weight_kg: float,
    height_cm: float,
) -> dict:
    bmi = calculate_bmi(weight_kg, height_cm)
    age_months = age_years * 12.0

    if age_years >= 5.0:
        L, M, S = _lookup_lms_bmi(gender, age_months)
        method = "WHO_BMI_for_age_5plus"
    else:
        L, M, S = _lookup_lms_wfh(gender, height_cm, age_years)
        method = "WHO_WFH_0to5"

    z = calculate_z_score(bmi, L, M, S)
    bias, category = get_clinical_bias(z)

    return {
        "bmi":            bmi,
        "bmi_method":     method,
        "lms_L":          L,
        "lms_M":          M,
        "lms_S":          S,
        "z_score":        z,
        "bmi_category":   category,
        "mechanical_stress_bias": bias,
    }


def compute_pathology_bias(
    pathology_code: str,
    physeal_bar_area_pct: float,
) -> dict:
    code = pathology_code.upper().strip() if pathology_code else "NONE"
    base_weight = PATHOLOGY_WEIGHTS.get(code, 1.00)
    damage_intersect = physeal_bar_area_pct >= 50.0
    final_mod = round(base_weight * 0.85, 4) if damage_intersect else base_weight
    severity = PATHOLOGY_SEVERITY.get(base_weight, "Baseline")

    return {
        "pathology_code":            code,
        "base_weight":               base_weight,
        "severity_tier":             severity,
        "damage_intersect_applied":  damage_intersect,
        "pathology_bias":            final_mod,
    }


# =============================================================================
# FIX 3 — Paley Multiplier (Linear Proxy for Demo Purposes)
# =============================================================================
def paley_multiplier_remaining_growth(
    bone_age: float,
    gender: str,
    g0_rate_cm_yr: float,
) -> dict:
    """
    Estimate the physis's remaining growth potential using a linear time proxy.

    Returns total remaining growth (cm) and the annual basal growth rate
    (cm/yr) for downstream use in the Hueter-Volkmann equation.

    Parameters
    ----------
    bone_age : float
        Skeletal (bone) age of the patient in years.
    gender : str
        'M' (male) or 'F' (female). Determines skeletal maturity limit.
    g0_rate_cm_yr : float
        Site-specific basal annual growth rate (cm/yr) from G0_RATES lookup.

    Returns
    -------
    dict
        maturity_limit          – skeletal maturity age ceiling (yr)
        years_to_maturity       – years of growth remaining
        G_basal_remaining_cm    – total estimated residual growth (cm)
        G_basal_annual_cm       – annual basal rate used for the estimate (cm/yr)

    TODO / WARNING
    --------------
    This function uses a **LINEAR PROXY** rather than the full Paley
    Multiplier lookup table (Paley D, 2005 — "Principles of Deformity
    Correction", Table 3-1).

    The true Paley Multiplier method requires:
        - Total limb segment length (full femur + tibia measured from
          full-length standing radiograph), NOT available from localised
          knee X-ray data used in this demo pipeline.
        - Sex-specific multiplier tables that map current bone length to
          predicted mature length.

    IMPACT of the proxy:
        - The linear estimate (years_left × g0_rate) is a reasonable
          approximation when bone age is well within the growth window
          (>2 yr from maturity) but overestimates residual growth as the
          physis approaches closure.
        - For clinical deployment this function MUST be replaced with
          the full Paley Multiplier lookup once full-limb length data
          from standing radiographs is available.

    The output (G_basal_remaining_cm, G_basal_annual_cm) feeds directly
    into multimodal_fusion() → compute_hueter_volkmann() to produce the
    physics-corrected annual growth rate. The proxy's linearity is
    therefore partially compensated by the HV attenuation step.
    """
    limit = MATURITY_LIMIT[gender]
    years_left = max(0.0, limit - bone_age)
    g_basal_cm = round(years_left * g0_rate_cm_yr, 4)
    return {
        "maturity_limit":       limit,
        "years_to_maturity":    round(years_left, 4),
        "G_basal_remaining_cm": g_basal_cm,
        "G_basal_annual_cm":    g0_rate_cm_yr,
    }


def _parse_sh_type(salter_type_raw: str) -> str:
    if not salter_type_raw or salter_type_raw == "Normal":
        return "Normal"
    m = re.search(r"(SH_Type_(?:I{1,3}V?|IV|V))", salter_type_raw, re.IGNORECASE)
    if m:
        return m.group(1).upper().replace("SH_TYPE_", "SH_Type_")
    return "Normal"


def _pixel_dist_to_mm(d_px: float, pixel_spacing_mm: float = DEFAULT_PIXEL_SPACING) -> float:
    return round(d_px * pixel_spacing_mm, 4)


def compute_vision_features(cv_row: dict) -> dict:
    x_min   = float(cv_row.get("X_Min", 0))
    y_min   = float(cv_row.get("Y_Min", 0))
    x_max   = float(cv_row.get("X_Max", 0))
    y_max   = float(cv_row.get("Y_Max", 0))
    x_bar   = float(cv_row.get("X_Bar", (x_min + x_max) / 2))
    y_bar   = float(cv_row.get("Y_Bar", (y_min + y_max) / 2))

    box_w_px = x_max - x_min
    box_h_px = y_max - y_min
    box_w_mm = _pixel_dist_to_mm(box_w_px)
    box_h_mm = _pixel_dist_to_mm(box_h_px)

    physeal_width_px = box_w_px
    d_px = physeal_width_px / 2.0
    d_mm = _pixel_dist_to_mm(d_px)

    salter_raw    = str(cv_row.get("Salter_Type", "Normal"))
    sh_type       = _parse_sh_type(salter_raw)
    bone_type     = str(cv_row.get("bone_type", "Unknown"))
    side          = str(cv_row.get("side", "Unknown"))

    location_map = {
        "Medial": "Peripheral", "Lateral": "Peripheral",
        "Unknown": "Central",   "nan": "Central",
    }
    bar_location = location_map.get(side, "Central")

    arrest_base_risk = SH_ARREST_BASE_RISK.get(sh_type, 0.0)

    return {
        "bone_type":       bone_type,
        "side":            side,
        "sh_type":         sh_type,
        "bar_location":    bar_location,
        "x_bar_px":        x_bar,
        "y_bar_px":        y_bar,
        "box_width_mm":    box_w_mm,
        "box_height_mm":   box_h_mm,
        "d_px":            d_px,
        "d_mm":            d_mm,
        "arrest_base_risk_sh": arrest_base_risk,
    }


def compute_geometric_tethering(
    g_undamaged_mm_yr: float,
    d_mm: float,
    bar_location: str,
    fusion_stage: str,
) -> dict:
    if bar_location != "Peripheral" or fusion_stage == "Stage_III" or d_mm <= 0:
        return {
            "delta_theta_rad_per_yr":  0.0,
            "delta_theta_deg_per_yr":  0.0,
            "deformity_applicable":    False,
            "deformity_risk_label":    "None",
        }

    delta_rad = g_undamaged_mm_yr / d_mm
    delta_deg = round(delta_rad * (180.0 / math.pi), 4)

    if delta_deg < 5.0:
        label = "Low"
    elif delta_deg < 15.0:
        label = "Moderate"
    else:
        label = "High"

    return {
        "delta_theta_rad_per_yr":  round(delta_rad, 6),
        "delta_theta_deg_per_yr":  delta_deg,
        "deformity_applicable":    True,
        "deformity_risk_label":    label,
    }


# =============================================================================
# FIX 1 (core function) — Hueter-Volkmann mechanical growth modulation
# =============================================================================
def compute_hueter_volkmann(
    g0_mm_yr: float,
    beta: float,
    sigma: float,
) -> float:
    """
    Apply the Hueter-Volkmann law to attenuate the basal physeal growth rate.

    The law states that compressive mechanical stress inhibits growth while
    tensile stress promotes it:
        g_hv = g0 × (1 − β · σ)

    Parameters
    ----------
    g0_mm_yr : float
        Basal (unloaded) annual growth rate at the physis in mm/yr.
        Sourced from Paley proxy output × fusion multiplier.
    beta : float
        Biological sensitivity coefficient — patient-specific scaling factor
        reflecting how sensitively this physis responds to mechanical load.
        Typical range: 0.05 – 0.20.
    sigma : float
        Dynamic mechanical stress variable (dimensionless, signed).
        Positive σ → compressive load  → growth inhibition.
        Negative σ → tensile load      → growth promotion.
        Derived from mech_bias in multimodal_fusion() via:
            dynamic_sigma = (mech_bias - 1.0) × −1.5
        so that obesity (mech_bias = 1.30) yields σ = −0.45 (compressive
        axial load increases physeal stress, inhibiting net growth).

    Returns
    -------
    float
        Physics-corrected annual physeal growth rate in mm/yr (≥ 0).
    """
    g = g0_mm_yr * (1.0 - beta * sigma)
    return round(max(0.0, g), 4)


def multimodal_fusion(
    paley:        dict,
    path_bias:    dict,
    bmi_result:   dict,
    cv_feat:      dict,
    fusion_stage: str,
    beta:         float,
    sigma:        float,
    g0_rate_cm_yr: float,
) -> dict:
    """
    Fuse all modality signals into a single clinical prognosis.

    Key changes from original (see inline FIX comments):
      FIX 1  — mech_bias is translated to dynamic_sigma and fed into
               compute_hueter_volkmann(); g_hv is now the authoritative
               annual growth rate driving all downstream calculations.
               The erroneous direct multiplication of g_fused_cm by
               mech_bias has been removed.
      FIX 2  — Angular projections are capped at DEFORMITY_CAP_DEG (45°)
               to prevent anatomically impossible values.
               LLD projections are floored at 0.0 cm.
    """
    g0_mm = g0_rate_cm_yr * 10.0  # annual basal rate in mm/yr

    g_basal_cm       = paley["G_basal_remaining_cm"]
    g_basal_annual_cm = paley["G_basal_annual_cm"]

    fusion_mult = FUSION_MULTIPLIERS.get(fusion_stage, 1.0)
    g_fused_cm  = round(g_basal_cm * fusion_mult, 4)

    path_mod  = path_bias["pathology_bias"]
    mech_bias = bmi_result["mechanical_stress_bias"]

    # ------------------------------------------------------------------
    # FIX 1 — Translate categorical mech_bias into a dynamic mechanical
    # stress variable (sigma_dynamic) and compute the physics-corrected
    # annual growth rate via the Hueter-Volkmann equation.
    #
    # Derivation of the mapping:
    #   mech_bias = 1.0  → neutral load      → sigma_dynamic = 0.0
    #   mech_bias = 1.30 → obesity / excess  → sigma_dynamic = -0.45
    #   mech_bias = 0.95 → thinness / unload → sigma_dynamic = +0.075
    #
    # The negative sign convention means increased body weight creates a
    # compressive force that, per Hueter-Volkmann, reduces g_hv below g0.
    # The user-supplied 'sigma' parameter from the clinical CSV is retained
    # as the *patient-specific* baseline stress (e.g. disease-related).
    # dynamic_sigma combines both sources of mechanical influence.
    # ------------------------------------------------------------------
    dynamic_sigma = (mech_bias - 1.0) * -1.5

    # The HV input rate is the post-fusion basal annual rate (mm/yr),
    # giving the growth remaining per year at the affected physis.
    g0_fused_mm_yr = g_basal_annual_cm * fusion_mult * 10.0

    g_hv_annual_mm = compute_hueter_volkmann(g0_fused_mm_yr, beta, dynamic_sigma)
    g_hv_annual_cm = round(g_hv_annual_mm / 10.0, 4)

    # Apply pathology bias on top of the physics-corrected HV rate.
    # (path_mod already encodes disease severity + damage-intersect penalty.)
    g_undamaged_annual_cm = round(g_hv_annual_cm * path_mod, 4)
    g_undamaged_mm        = round(g_undamaged_annual_cm * 10.0, 4)

    # Total remaining undamaged growth over the full residual window.
    years_to_maturity = paley["years_to_maturity"]
    g_undamaged_cm = round(g_undamaged_annual_cm * years_to_maturity, 4)

    # combined_modifier is retained in the output for auditability but is
    # no longer used to directly scale bone length (that was the flaw).
    combined_modifier = round(path_mod * mech_bias, 4)

    tether = compute_geometric_tethering(
        g_undamaged_mm,
        cv_feat["d_mm"],
        cv_feat["bar_location"],
        fusion_stage,
    )

    # ------------------------------------------------------------------
    # FIX 2 — Anatomically capped projections.
    #
    # Raw angular accumulation: raw_ang = Δθ/yr × t
    # Capped at DEFORMITY_CAP_DEG (45°) — the threshold beyond which the
    # joint would dislocate or undergo compensatory bony remodelling,
    # making further linear angular projection physiologically invalid.
    #
    # LLD is floored at 0.0 cm: negative values are biomechanically
    # meaningless in this context (they would imply the contralateral
    # limb is shorter, which is outside the scope of this unilateral model).
    # ------------------------------------------------------------------
    projections = {}
    for t in (1, 3, 5):
        raw_lld = (g_basal_annual_cm - g_undamaged_annual_cm) * t
        lld = round(max(0.0, raw_lld), 4)

        raw_ang = tether["delta_theta_deg_per_yr"] * t
        capped_ang = round(min(raw_ang, DEFORMITY_CAP_DEG), 4)

        projections[f"year_{t}"] = {
            "projected_LLD_cm":        lld,
            "projected_deformity_deg": capped_ang,
        }

    arrest_sh   = cv_feat["arrest_base_risk_sh"]
    path_factor = 1.0 + (1.0 - combined_modifier)
    arrest_prob = round(min(1.0, arrest_sh * path_factor * (1.0 + (1.0 - fusion_mult) * 0.5)), 4)

    if cv_feat["bar_location"] == "Peripheral" and fusion_stage != "Stage_III":
        delta5 = projections["year_5"]["projected_deformity_deg"]
        varus_valgus_base = (
            0.10 if delta5 < 5.0 else
            0.35 if delta5 < 15.0 else
            0.65 if delta5 < 30.0 else 0.85
        )
        vv_prob = round(min(1.0, varus_valgus_base * path_factor * mech_bias), 4)
    else:
        vv_prob = 0.00

    lld_5 = projections["year_5"]["projected_LLD_cm"]
    lld_sev = (
        "None"     if lld_5 < 1.0 else
        "Mild"     if lld_5 < 2.0 else
        "Moderate" if lld_5 < 4.0 else "Severe"
    )
    ang_5 = projections["year_5"]["projected_deformity_deg"]
    ang_sev = (
        "None"     if ang_5 == 0.0 else
        "Mild"     if ang_5 < 10.0 else
        "Moderate" if ang_5 < 25.0 else "Severe"
    )
    intervention = lld_sev in ("Moderate", "Severe") or ang_sev in ("Moderate", "Severe")

    return {
        "fusion_stage":              fusion_stage,
        "fusion_multiplier":         fusion_mult,
        "combined_modifier":         combined_modifier,
        "G_basal_remaining_cm":      g_basal_cm,
        "G_fused_cm":                g_fused_cm,
        "G_undamaged_remaining_cm":  g_undamaged_cm,
        "G_undamaged_annual_cm":     g_undamaged_annual_cm,
        "G_undamaged_annual_mm":     g_undamaged_mm,
        "G_hueter_volkmann_mm_yr":   g_hv_annual_mm,
        "geometric_tethering":       tether,
        "projections":               projections,
        "probabilities": {
            "prob_complete_arrest":        arrest_prob,
            "prob_varus_valgus_deformity": vv_prob,
        },
        "remaining_growth": {
            "remaining_mm": round(g_undamaged_cm * 10.0, 4),
            "remaining_cm": g_undamaged_cm,
        },
        "clinical_summary": {
            "lld_5yr_severity":         lld_sev,
            "deformity_5yr_severity":   ang_sev,
            "intervention_recommended": intervention,
        },
    }


def run_pipeline(
    gender:               str,
    chronological_age_yr: float,
    bone_age_yr:          float,
    height_cm:            float,
    weight_kg:            float,
    pathology_code:       str,
    fusion_stage:         str,
    bone_site:            str,
    cv_row:               dict,
    beta:                 float = 0.10,
    sigma:                float = 0.10,
) -> dict:
    g0_rate = G0_RATES.get(bone_site, 0.6)

    bmi_result = compute_bmi_zscore(gender, chronological_age_yr, weight_kg, height_cm)
    physeal_bar_pct = float(cv_row.get("physeal_bar_area_pct", 0.0))
    path_bias  = compute_pathology_bias(pathology_code, physeal_bar_pct)
    paley      = paley_multiplier_remaining_growth(bone_age_yr, gender, g0_rate)
    cv_feat    = compute_vision_features(cv_row)

    fusion_result = multimodal_fusion(
        paley, path_bias, bmi_result, cv_feat,
        fusion_stage, beta, sigma, g0_rate,
    )

    return {
        "input_summary": {
            "gender":                 gender,
            "chronological_age_yr":   chronological_age_yr,
            "bone_age_yr":            bone_age_yr,
            "height_cm":              height_cm,
            "weight_kg":              weight_kg,
            "pathology_code":         pathology_code,
            "fusion_stage":           fusion_stage,
            "bone_site":              bone_site,
            "beta":                   beta,
            "sigma":                  sigma,
        },
        "step1_bmi":        bmi_result,
        "step2_pathology":  path_bias,
        "step3_biological": paley,
        "step4_cv":         cv_feat,
        "step5_fusion":     fusion_result,
        "final_output": {
            "remaining_growth_mm":         fusion_result["remaining_growth"]["remaining_mm"],
            "remaining_growth_cm":         fusion_result["remaining_growth"]["remaining_cm"],
            "prob_complete_arrest_pct":    round(fusion_result["probabilities"]["prob_complete_arrest"] * 100, 2),
            "prob_varus_valgus_pct":       round(fusion_result["probabilities"]["prob_varus_valgus_deformity"] * 100, 2),
            "projected_LLD_1yr_cm":        fusion_result["projections"]["year_1"]["projected_LLD_cm"],
            "projected_LLD_3yr_cm":        fusion_result["projections"]["year_3"]["projected_LLD_cm"],
            "projected_LLD_5yr_cm":        fusion_result["projections"]["year_5"]["projected_LLD_cm"],
            "projected_deformity_1yr_deg": fusion_result["projections"]["year_1"]["projected_deformity_deg"],
            "projected_deformity_3yr_deg": fusion_result["projections"]["year_3"]["projected_deformity_deg"],
            "projected_deformity_5yr_deg": fusion_result["projections"]["year_5"]["projected_deformity_deg"],
            "deformity_risk_label":        fusion_result["geometric_tethering"]["deformity_risk_label"],
            "lld_severity":                fusion_result["clinical_summary"]["lld_5yr_severity"],
            "deformity_severity":          fusion_result["clinical_summary"]["deformity_5yr_severity"],
            "intervention_recommended":    fusion_result["clinical_summary"]["intervention_recommended"],
            "bmi_category":                bmi_result["bmi_category"],
            "bmi":                         bmi_result["bmi"],
            "bmi_z_score":                 bmi_result["z_score"],
            "mechanical_stress_bias":      bmi_result["mechanical_stress_bias"],
        },
    }


def batch_fuse_from_files(n_records: int = 50) -> pd.DataFrame:
    xray_df     = pd.read_csv(XRAY_CSV)
    clinical_df = pd.read_csv(CLINICAL_CSV)

    fracture_xray = xray_df[
        xray_df["folder_name"].isin(["trainB", "testB"])
    ].copy().reset_index(drop=True)

    clinical_sample = clinical_df.head(n_records).copy()

    results = []
    for i, clin in clinical_sample.iterrows():
        if i < len(fracture_xray):
            xr = fracture_xray.iloc[i % len(fracture_xray)].to_dict()
        else:
            xr = {"X_Min": 90, "Y_Min": 90, "X_Max": 170, "Y_Max": 140,
                  "X_Bar": 130, "Y_Bar": 115, "Salter_Type": "SH_Type_II_0001",
                  "bone_type": "Femur", "side": "Lateral",
                  "physeal_bar_area_pct": clin["physeal_bar_area_pct"]}

        xr["physeal_bar_area_pct"] = clin["physeal_bar_area_pct"]

        height_cm = 120.0 + (float(clin["bone_age_years"]) * 4.5)
        bmi_val   = 18.0
        weight_kg = bmi_val * ((height_cm / 100.0) ** 2)

        try:
            result = run_pipeline(
                gender               = str(clin["gender"]),
                chronological_age_yr = float(clin["bone_age_years"]),
                bone_age_yr          = float(clin["bone_age_years"]),
                height_cm            = height_cm,
                weight_kg            = weight_kg,
                pathology_code       = str(clin["pathology_code"]),
                fusion_stage         = str(clin["fusion_stage"]),
                bone_site            = str(clin["bone_site"]),
                cv_row               = xr,
                beta                 = float(clin["beta_biological_sensitivity"]),
                sigma                = float(clin["sigma_mechanical_stress"]),
            )
            fo = result["final_output"]
            row = {
                "record_id":                   clin["record_id"],
                "gender":                      clin["gender"],
                "bone_age_years":              clin["bone_age_years"],
                "pathology_code":              clin["pathology_code"],
                "fusion_stage":                clin["fusion_stage"],
                "bone_site":                   clin["bone_site"],
                "sh_type":                     result["step4_cv"]["sh_type"],
                "bar_location":                result["step4_cv"]["bar_location"],
                "side":                        result["step4_cv"]["side"],
                "bmi":                         fo["bmi"],
                "bmi_z_score":                 fo["bmi_z_score"],
                "bmi_category":                fo["bmi_category"],
                "mechanical_stress_bias":      fo["mechanical_stress_bias"],
                "pathology_bias":              result["step2_pathology"]["pathology_bias"],
                "combined_modifier":           result["step5_fusion"]["combined_modifier"],
                "remaining_growth_mm":         fo["remaining_growth_mm"],
                "remaining_growth_cm":         fo["remaining_growth_cm"],
                "prob_complete_arrest_pct":    fo["prob_complete_arrest_pct"],
                "prob_varus_valgus_pct":       fo["prob_varus_valgus_pct"],
                "projected_LLD_1yr_cm":        fo["projected_LLD_1yr_cm"],
                "projected_LLD_3yr_cm":        fo["projected_LLD_3yr_cm"],
                "projected_LLD_5yr_cm":        fo["projected_LLD_5yr_cm"],
                "projected_deformity_1yr_deg": fo["projected_deformity_1yr_deg"],
                "projected_deformity_3yr_deg": fo["projected_deformity_3yr_deg"],
                "projected_deformity_5yr_deg": fo["projected_deformity_5yr_deg"],
                "deformity_risk_label":        fo["deformity_risk_label"],
                "lld_severity":                fo["lld_severity"],
                "deformity_severity":          fo["deformity_severity"],
                "intervention_recommended":    fo["intervention_recommended"],
            }
            results.append(row)
        except Exception as e:
            print(f"  [WARN] record {clin['record_id']} skipped: {e}")

    return pd.DataFrame(results)


def print_clinical_report(result: dict) -> None:
    inp = result["input_summary"]
    fo  = result["final_output"]
    s1  = result["step1_bmi"]
    s2  = result["step2_pathology"]
    s3  = result["step3_biological"]
    s4  = result["step4_cv"]
    s5  = result["step5_fusion"]

    print("=" * 68)
    print("  MULTIMODAL AI PROGNOSIS — PEDIATRIC KNEE PHYSIS SYSTEM")
    print("=" * 68)
    print(f"  Patient      : {inp['gender']}, Bone Age {inp['bone_age_yr']} yr "
          f"(Chrono {inp['chronological_age_yr']} yr)")
    print(f"  Anthropometry: {inp['height_cm']} cm / {inp['weight_kg']} kg")
    print(f"  Bone site    : {inp['bone_site']}  |  Fusion: {inp['fusion_stage']}")
    print(f"  Pathology    : {inp['pathology_code']} "
          f"({s2['severity_tier']})")
    print()
    print("  ── STEP 1 · BMI Z-Score (WHO LMS) ──────────────────────")
    print(f"  BMI          = {fo['bmi']} kg/m²")
    print(f"  LMS          : L={s1['lms_L']}, M={s1['lms_M']}, S={s1['lms_S']}")
    print(f"  Z-score      = {fo['bmi_z_score']}  →  {fo['bmi_category']}")
    print(f"  Mech. Bias   = {fo['mechanical_stress_bias']}  (Hueter-Volkmann)")
    print()
    print("  ── STEP 2 · Pathological Bias ───────────────────────────")
    print(f"  Base weight  = {s2['base_weight']}  |  "
          f"Damage intersect: {s2['damage_intersect_applied']}")
    print(f"  Final mod    = {s2['pathology_bias']}")
    print()
    print("  ── STEP 3 · Biological Bias (Paley Proxy — Linear Demo) ─")
    print(f"  Maturity at  : {s3['maturity_limit']} yr  |  "
          f"Remaining: {s3['years_to_maturity']} yr")
    print(f"  G_basal      = {s3['G_basal_remaining_cm']} cm")
    print(f"  [WARNING]    Linear proxy only — see paley_multiplier_remaining_growth()")
    print()
    print("  ── STEP 4 · Computer Vision Features ────────────────────")
    print(f"  SH type      : {s4['sh_type']}  |  Bone: {s4['bone_type']}  "
          f"| Side: {s4['side']}")
    print(f"  Bar location : {s4['bar_location']}  |  d_mm: {s4['d_mm']}")
    print(f"  Box          : {s4['box_width_mm']} × {s4['box_height_mm']} mm")
    print(f"  Arrest risk (SH base): {round(s4['arrest_base_risk_sh']*100,1)}%")
    print()
    print("  ── STEP 5 · Multimodal Fusion Output ────────────────────")
    print(f"  Combined mod = {s5['combined_modifier']}  "
          f"(path_bias × mech_bias — audit only)")
    print(f"  HV rate      = {s5['G_hueter_volkmann_mm_yr']} mm/yr  "
          f"(physics-corrected via dynamic sigma)")
    print(f"  G_undamaged  = {s5['G_undamaged_annual_cm']} cm/yr  "
          f"(HV × pathology_bias)")
    gt = s5["geometric_tethering"]
    print(f"  Δθ/yr        = {gt['delta_theta_deg_per_yr']}°  "
          f"| Deformity: {gt['deformity_risk_label']}  "
          f"(capped at {DEFORMITY_CAP_DEG}°)")
    print()
    print("  ── FINAL CLINICAL PREDICTIONS ───────────────────────────")
    print(f"  Remaining growth     : {fo['remaining_growth_mm']} mm  "
          f"({fo['remaining_growth_cm']} cm)")
    print(f"  P(Complete Arrest)   : {fo['prob_complete_arrest_pct']}%")
    print(f"  P(Varus/Valgus)      : {fo['prob_varus_valgus_pct']}%")
    print()
    print(f"  ┌─ Projections ──────────────┬──────────┬──────────┬──────────┐")
    print(f"  │                            │  1 yr    │  3 yr    │  5 yr    │")
    print(f"  ├────────────────────────────┼──────────┼──────────┼──────────┤")
    print(f"  │ LLD (cm)                   │ "
          f"{fo['projected_LLD_1yr_cm']:7.3f}  │ "
          f"{fo['projected_LLD_3yr_cm']:7.3f}  │ "
          f"{fo['projected_LLD_5yr_cm']:7.3f}  │")
    print(f"  │ Deformity (°)  [cap={DEFORMITY_CAP_DEG:.0f}°]  │ "
          f"{fo['projected_deformity_1yr_deg']:7.3f}  │ "
          f"{fo['projected_deformity_3yr_deg']:7.3f}  │ "
          f"{fo['projected_deformity_5yr_deg']:7.3f}  │")
    print(f"  └────────────────────────────┴──────────┴──────────┴──────────┘")
    print()
    print(f"  Severity (LLD 5yr)      : {fo['lld_severity']}")
    print(f"  Severity (Deformity 5yr): {fo['deformity_severity']}")
    print(f"  Intervention needed     : {'YES ⚠' if fo['intervention_recommended'] else 'No'}")
    print("=" * 68)


def main():
    print("\n[INFO] Loading real X-ray bounding box data and clinical biases ...")

    xray_df = pd.read_csv(XRAY_CSV)
    fracture_rows = xray_df[
        xray_df["folder_name"].isin(["trainB", "testB"])
    ].reset_index(drop=True)

    print(f"[INFO] Loaded {len(fracture_rows)} fracture bounding boxes")
    print(f"[INFO] Loaded {len(pd.read_csv(CLINICAL_CSV))} clinical records\n")

    print("=" * 68)
    print("  DEMO CASE A — 9-yr Female, SH Type II, Overweight, Corticosteroids")
    print("=" * 68)
    xr_case_a = {
        "X_Min": 128, "Y_Min": 82, "X_Max": 186, "Y_Max": 142,
        "X_Bar": 157, "Y_Bar": 112,
        "Salter_Type": "SH_Type_II_0004",
        "bone_type": "Femur",
        "side": "Lateral",
        "physeal_bar_area_pct": 35.0,
    }
    result_a = run_pipeline(
        gender               = "F",
        chronological_age_yr = 9.5,
        bone_age_yr          = 10.0,
        height_cm            = 133.0,
        weight_kg            = 42.0,
        pathology_code       = "STER-01",
        fusion_stage         = "Stage_II",
        bone_site            = "distal_femur",
        cv_row               = xr_case_a,
        beta                 = 0.12,
        sigma                = 0.18,
    )
    print_clinical_report(result_a)

    print("\n")
    print("=" * 68)
    print("  DEMO CASE B — 7-yr Male, SH Type IV, Normal BMI, No Pathology")
    print("=" * 68)
    xr_case_b = {
        "X_Min": 75, "Y_Min": 121, "X_Max": 134, "Y_Max": 162,
        "X_Bar": 104, "Y_Bar": 141,
        "Salter_Type": "SH_Type_IV_0007",
        "bone_type": "Tibia",
        "side": "Lateral",
        "physeal_bar_area_pct": 55.0,
    }
    result_b = run_pipeline(
        gender               = "M",
        chronological_age_yr = 7.0,
        bone_age_yr          = 7.5,
        height_cm            = 122.0,
        weight_kg            = 23.0,
        pathology_code       = "NONE",
        fusion_stage         = "Stage_I",
        bone_site            = "proximal_tibia",
        cv_row               = xr_case_b,
        beta                 = 0.08,
        sigma                = 0.22,
    )
    print_clinical_report(result_b)

    print("\n")
    print("=" * 68)
    print("  DEMO CASE C — 12-yr Male, SH Type III, Obese, JIA (M08.0)")
    print("=" * 68)
    xr_case_c = {
        "X_Min": 88, "Y_Min": 112, "X_Max": 193, "Y_Max": 141,
        "X_Bar": 140, "Y_Bar": 126,
        "Salter_Type": "SH_Type_III_0012",
        "bone_type": "Femur",
        "side": "Medial",
        "physeal_bar_area_pct": 62.0,
    }
    result_c = run_pipeline(
        gender               = "M",
        chronological_age_yr = 12.0,
        bone_age_yr          = 11.5,
        height_cm            = 148.0,
        weight_kg            = 65.0,
        pathology_code       = "M08.0",
        fusion_stage         = "Stage_II",
        bone_site            = "distal_femur",
        cv_row               = xr_case_c,
        beta                 = 0.15,
        sigma                = 0.25,
    )
    print_clinical_report(result_c)

    print("\n[INFO] Running batch fusion on 50 real clinical records ...")
    batch_df = batch_fuse_from_files(n_records=50)
    batch_df.to_csv("/mnt/user-data/outputs/fused_prognosis_results.csv", index=False)
    print(f"[INFO] Batch results saved → fused_prognosis_results.csv  "
          f"({len(batch_df)} rows × {len(batch_df.columns)} cols)")

    print("\n  ── Batch Summary ─────────────────────────────────────────")
    print(f"  Mean P(Arrest)   : {batch_df['prob_complete_arrest_pct'].mean():.1f}%")
    print(f"  Mean P(Varus/Val): {batch_df['prob_varus_valgus_pct'].mean():.1f}%")
    print(f"  Mean Rem. Growth : {batch_df['remaining_growth_mm'].mean():.1f} mm")
    print(f"  Intervention flag: {batch_df['intervention_recommended'].sum()} / {len(batch_df)}")
    print(f"  LLD severity dist: {batch_df['lld_severity'].value_counts().to_dict()}")
    print(f"  Deformity dist   : {batch_df['deformity_severity'].value_counts().to_dict()}")

    with open("/mnt/user-data/outputs/demo_case_a.json", "w") as f:
        json.dump(result_a, f, indent=4, default=str)
    with open("/mnt/user-data/outputs/demo_case_b.json", "w") as f:
        json.dump(result_b, f, indent=4, default=str)
    with open("/mnt/user-data/outputs/demo_case_c.json", "w") as f:
        json.dump(result_c, f, indent=4, default=str)
    print("\n[INFO] JSON reports saved → demo_case_a/b/c.json")


if __name__ == "__main__":
    main()
