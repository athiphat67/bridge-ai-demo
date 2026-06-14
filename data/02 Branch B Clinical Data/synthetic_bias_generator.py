import random
import math
import json
import pandas as pd

RANDOM_SEED = 42
N_RECORDS   = 1000

random.seed(RANDOM_SEED)

MATURITY_LIMIT = {"M": 16.0, "F": 14.0}
G0_RATES = {
    "distal_femur":    0.9,
    "proximal_tibia":  0.6,
}

FUSION_STAGE_MULTIPLIERS = {
    "Stage_I":   1.00,
    "Stage_II":  0.50,
    "Stage_III": 0.00,
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
    "E54":  0.95, "D50.9": 0.95, "E66.0": 0.95, "Q90.9": 0.95,
    "G47.3": 0.95, "M41.9": 0.95,
    "NSAID-01": 0.95, "GAS-01": 0.95, "PSY-02": 0.95,
    "NONE": 1.00,
}

PATHOLOGY_SEVERITY_MAP = {
    0.70: "Critical", 0.80: "High",
    0.90: "Moderate", 0.95: "Low", 1.00: "Baseline",
}

PATHOLOGY_POOL = [k for k in PATHOLOGY_WEIGHTS if k != "NONE"]
BAR_LOCATIONS  = ["Central", "Peripheral"]
BONE_SITES     = ["distal_femur", "proximal_tibia"]
GENDERS        = ["M", "F"]


def base_remaining_growth(bone_age, gender, g0_rate):
    limit    = MATURITY_LIMIT[gender]
    years_remaining = max(0.0, limit - bone_age)
    return round(years_remaining * g0_rate, 4)


def apply_fusion_stage(g_basal, stage):
    return round(g_basal * FUSION_STAGE_MULTIPLIERS[stage], 4)


def resolve_pathology_modifier(code, a_bar_pct):
    base_weight = PATHOLOGY_WEIGHTS.get(code, 1.00)
    if a_bar_pct >= 50.0:
        base_weight = round(base_weight * 0.85, 4)
    return base_weight


def compute_g_undamaged(g_fused, mod_value):
    return round(g_fused * mod_value, 4)


def hueter_volkmann_growth(g0_rate, beta, sigma):
    g = g0_rate * (1.0 - beta * sigma)
    return round(max(0.0, g), 4)


def angular_deformity_rate(g_undamaged_mm_yr, d_mm):
    if d_mm <= 0:
        return 0.0
    delta_theta_rad = g_undamaged_mm_yr / d_mm
    delta_theta_deg = delta_theta_rad * (180.0 / math.pi)
    return round(delta_theta_deg, 4)


def project_outcomes(g_basal_annual, g_undamaged_annual,
                     delta_theta_deg, location, years=(1, 3, 5)):
    projections = {}
    for t in years:
        lld = round((g_basal_annual - g_undamaged_annual) * t, 4)
        if location == "Peripheral":
            angle = round(delta_theta_deg * t, 4)
        else:
            angle = 0.0
        projections[f"year_{t}"] = {
            "projected_LLD_cm":      lld,
            "projected_deformity_deg": angle,
        }
    return projections


def generate_record(record_id):
    gender       = random.choice(GENDERS)
    maturity     = MATURITY_LIMIT[gender]
    min_bone_age = max(1.0, maturity - 12.0)
    bone_age     = round(random.uniform(min_bone_age, maturity), 2)
    bone_site    = random.choice(BONE_SITES)
    g0_rate      = G0_RATES[bone_site]
    g0_mm        = g0_rate * 10.0

    fusion_stage = random.choices(
        ["Stage_I", "Stage_II", "Stage_III"],
        weights=[0.50, 0.35, 0.15], k=1
    )[0]

    use_none = random.random() < 0.30
    if use_none:
        pathology_code = "NONE"
    else:
        pathology_code = random.choice(PATHOLOGY_POOL)

    base_weight = PATHOLOGY_WEIGHTS[pathology_code]
    a_bar_pct   = round(random.uniform(0.0, 80.0), 2)
    bar_location = random.choice(BAR_LOCATIONS)

    pixel_spacing = round(random.uniform(0.15, 0.40), 4)
    d_px          = round(random.uniform(20.0, 120.0), 2)
    d_mm          = round(d_px * pixel_spacing, 4)

    beta  = round(random.uniform(0.05, 0.25), 4)
    sigma = round(random.uniform(-0.30, 0.30), 4)

    g_basal_cm     = base_remaining_growth(bone_age, gender, g0_rate)
    g_basal_annual = g0_rate

    g_fused        = apply_fusion_stage(g_basal_cm, fusion_stage)
    mod_value      = resolve_pathology_modifier(pathology_code, a_bar_pct)
    g_undamaged_cm = compute_g_undamaged(g_fused, mod_value)

    g_undamaged_annual_cm = round(g0_rate * mod_value * FUSION_STAGE_MULTIPLIERS[fusion_stage], 4)
    g_undamaged_mm        = round(g_undamaged_annual_cm * 10.0, 4)

    g_hv = hueter_volkmann_growth(g0_mm, beta, sigma)

    if bar_location == "Peripheral" and fusion_stage != "Stage_III":
        delta_theta = angular_deformity_rate(g_undamaged_mm, d_mm)
    else:
        delta_theta = 0.0

    projections = project_outcomes(
        g_basal_annual, g_undamaged_annual_cm,
        delta_theta, bar_location
    )

    lld_severity = (
        "None"     if projections["year_5"]["projected_LLD_cm"] < 1.0  else
        "Mild"     if projections["year_5"]["projected_LLD_cm"] < 2.0  else
        "Moderate" if projections["year_5"]["projected_LLD_cm"] < 4.0  else
        "Severe"
    )

    deformity_severity = (
        "None"     if projections["year_5"]["projected_deformity_deg"] == 0.0 else
        "Mild"     if projections["year_5"]["projected_deformity_deg"] < 10.0 else
        "Moderate" if projections["year_5"]["projected_deformity_deg"] < 25.0 else
        "Severe"
    )

    damage_intersect_applied = a_bar_pct >= 50.0

    record = {
        "record_id": f"REC_{record_id:04d}",
        "patient": {
            "gender":              gender,
            "bone_age_years":      bone_age,
            "maturity_limit_years": maturity,
            "years_to_maturity":   round(max(0.0, maturity - bone_age), 4),
        },
        "imaging": {
            "bone_site":          bone_site,
            "fusion_stage":       fusion_stage,
            "physeal_bar_area_pct": a_bar_pct,
            "bar_location":       bar_location,
            "pixel_spacing_mm":   pixel_spacing,
            "d_px":               d_px,
            "d_mm":               d_mm,
        },
        "pathology": {
            "code":                  pathology_code,
            "base_weight":           base_weight,
            "severity_tier":         PATHOLOGY_SEVERITY_MAP[base_weight],
            "damage_intersect_applied": damage_intersect_applied,
            "final_modifier":        mod_value,
        },
        "biomechanics": {
            "g0_rate_cm_per_year":           g0_rate,
            "g0_rate_mm_per_year":           g0_mm,
            "beta_biological_sensitivity":   beta,
            "sigma_mechanical_stress":       sigma,
            "g_hueter_volkmann_mm_per_year": g_hv,
        },
        "growth_pipeline": {
            "G_basal_remaining_cm":       g_basal_cm,
            "G_fused_cm":                 g_fused,
            "G_undamaged_remaining_cm":   g_undamaged_cm,
            "G_undamaged_annual_cm":      g_undamaged_annual_cm,
            "G_undamaged_annual_mm":      g_undamaged_mm,
        },
        "deformity": {
            "delta_theta_deg_per_year":   delta_theta,
            "deformity_applicable":       bar_location == "Peripheral" and fusion_stage != "Stage_III",
        },
        "projections": projections,
        "clinical_summary": {
            "lld_5yr_severity":       lld_severity,
            "deformity_5yr_severity": deformity_severity,
            "intervention_flag":      lld_severity in ("Moderate", "Severe") or
                                      deformity_severity in ("Moderate", "Severe"),
        },
    }
    return record


def flatten_record(rec):
    p   = rec["patient"]
    img = rec["imaging"]
    pat = rec["pathology"]
    bio = rec["biomechanics"]
    gp  = rec["growth_pipeline"]
    dev = rec["deformity"]
    cs  = rec["clinical_summary"]
    pr  = rec["projections"]

    row = {
        "record_id":                       rec["record_id"],
        "gender":                          p["gender"],
        "bone_age_years":                  p["bone_age_years"],
        "maturity_limit_years":            p["maturity_limit_years"],
        "years_to_maturity":               p["years_to_maturity"],
        "bone_site":                       img["bone_site"],
        "fusion_stage":                    img["fusion_stage"],
        "physeal_bar_area_pct":            img["physeal_bar_area_pct"],
        "bar_location":                    img["bar_location"],
        "pixel_spacing_mm":                img["pixel_spacing_mm"],
        "d_px":                            img["d_px"],
        "d_mm":                            img["d_mm"],
        "pathology_code":                  pat["code"],
        "pathology_base_weight":           pat["base_weight"],
        "pathology_severity_tier":         pat["severity_tier"],
        "damage_intersect_applied":        pat["damage_intersect_applied"],
        "final_modifier":                  pat["final_modifier"],
        "g0_rate_cm_per_year":             bio["g0_rate_cm_per_year"],
        "g0_rate_mm_per_year":             bio["g0_rate_mm_per_year"],
        "beta_biological_sensitivity":     bio["beta_biological_sensitivity"],
        "sigma_mechanical_stress":         bio["sigma_mechanical_stress"],
        "g_hueter_volkmann_mm_per_year":   bio["g_hueter_volkmann_mm_per_year"],
        "G_basal_remaining_cm":            gp["G_basal_remaining_cm"],
        "G_fused_cm":                      gp["G_fused_cm"],
        "G_undamaged_remaining_cm":        gp["G_undamaged_remaining_cm"],
        "G_undamaged_annual_cm":           gp["G_undamaged_annual_cm"],
        "G_undamaged_annual_mm":           gp["G_undamaged_annual_mm"],
        "delta_theta_deg_per_year":        dev["delta_theta_deg_per_year"],
        "deformity_applicable":            dev["deformity_applicable"],
        "projected_LLD_cm_yr1":            pr["year_1"]["projected_LLD_cm"],
        "projected_deformity_deg_yr1":     pr["year_1"]["projected_deformity_deg"],
        "projected_LLD_cm_yr3":            pr["year_3"]["projected_LLD_cm"],
        "projected_deformity_deg_yr3":     pr["year_3"]["projected_deformity_deg"],
        "projected_LLD_cm_yr5":            pr["year_5"]["projected_LLD_cm"],
        "projected_deformity_deg_yr5":     pr["year_5"]["projected_deformity_deg"],
        "lld_5yr_severity":                cs["lld_5yr_severity"],
        "deformity_5yr_severity":          cs["deformity_5yr_severity"],
        "intervention_flag":               cs["intervention_flag"],
    }
    return row


def main():
    print(f"Generating {N_RECORDS} synthetic clinical records ...")

    records = [generate_record(i + 1) for i in range(N_RECORDS)]

    with open("dataset_labels.json", "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4)
    print(f"Saved  →  dataset_labels.json  ({len(records)} records)")

    rows = [flatten_record(r) for r in records]
    df   = pd.DataFrame(rows)
    df.to_csv("dataset_labels.csv", index=False)
    print(f"Saved  →  dataset_labels.csv   ({len(df)} rows × {len(df.columns)} columns)")

    print("\n--- Dataset Summary ---")
    print(f"  Gender distribution   :  {df['gender'].value_counts().to_dict()}")
    print(f"  Fusion stage dist.    :  {df['fusion_stage'].value_counts().to_dict()}")
    print(f"  Bar location dist.    :  {df['bar_location'].value_counts().to_dict()}")
    print(f"  Severity tier dist.   :  {df['pathology_severity_tier'].value_counts().to_dict()}")
    print(f"  LLD 5yr severity      :  {df['lld_5yr_severity'].value_counts().to_dict()}")
    print(f"  Deformity 5yr severity:  {df['deformity_5yr_severity'].value_counts().to_dict()}")
    print(f"  Intervention flagged  :  {df['intervention_flag'].sum()} / {N_RECORDS}")
    print("-----------------------")


if __name__ == "__main__":
    main()
