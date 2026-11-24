"""Data protocol for deterministic screening and whole-matrix regression rejection."""

import hashlib
import json
import math


def default_cases(protocol="standard"):
    static = {
        "stand": [0, 0, 0], "forward": [0.4, 0, 0], "backward": [-0.4, 0, 0],
        "left": [0, 0.3, 0], "right": [0, -0.3, 0],
        "turn_left": [0, 0, 0.4], "turn_right": [0, 0, -0.4],
        "forward_turn": [0.35, 0, 0.35], "lateral_turn": [0, 0.22, 0.35],
        "right_turn": [0, -0.22, -0.35], "diagonal": [0.35, 0.22, 0],
    }
    cases = [{"name": name, "profile": [[20.0, command]], "protected": True} for name, command in static.items()]
    cases += [
        {"name": "start_stop", "profile": [[2, [0, 0, 0]], [8, [0.3, 0, 0]], [20, [0, 0, 0]]], "protected": False},
        {"name": "reverse", "profile": [[6, [0.3, 0, 0]], [12, [-0.3, 0, 0]], [20, [0, 0, 0]]], "protected": False},
        {"name": "combination_switch", "profile": [[5, [0, 0.2, 0]], [12, [0, 0.2, 0.3]], [20, [0, 0, 0]]], "protected": False},
    ]
    if protocol == "lateral_grid":
        for name, command in (("left_low", [0, .1, 0]), ("left_mid", [0, .2, 0]),
                              ("right_low", [0, -.1, 0]), ("right_mid", [0, -.2, 0])):
            cases.append({"name": name, "profile": [[20.0, command]], "protected": True})
    elif protocol != "standard":
        raise ValueError("Unknown evaluation protocol")
    return cases


def profile_at(profile, seconds):
    if not profile or seconds < 0:
        raise ValueError("Invalid command profile or time")
    start = 0.0
    for end, command in profile:
        if end <= start or len(command) != 3 or not all(math.isfinite(x) for x in command):
            raise ValueError("Profiles need increasing end times and finite three-axis commands")
        if seconds < end:
            return command, seconds - start
        start = end
    return profile[-1][1], seconds - (profile[-2][0] if len(profile) > 1 else 0)


def protocol_hash(cases, steps, dt, environments_per_case, seed=42):
    value = {"cases": cases, "steps": steps, "dt": dt, "environments_per_case": environments_per_case,
             "steady_excludes_first_s_after_each_change": 1.0, "schema_version": 2, "seed": seed}
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def regression_gate(candidate, reference):
    reasons = []
    if not candidate.get("complete") or not reference.get("complete"):
        reasons.append("incomplete_report")
    if candidate.get("protocol_sha256") != reference.get("protocol_sha256"):
        reasons.append("evaluation_protocol_mismatch")
    if candidate.get("physics_contract") != reference.get("physics_contract"):
        reasons.append("physics_contract_mismatch")
    actual = {x["name"]: x for x in candidate.get("cases", [])}
    previous = {x["name"]: x for x in reference.get("cases", [])}
    if not actual or set(actual) != set(previous):
        reasons.append("missing_or_extra_cases")
    if len(actual) != len(candidate.get("cases", [])):
        reasons.append("duplicate_case_names")
    if len(previous) != len(reference.get("cases", [])):
        reasons.append("duplicate_reference_case_names")
    for name, value in actual.items():
        old = previous.get(name, {})
        protected = old.get("protected", True)
        if not value.get("finite", False) or value.get("failures", 1) != 0:
            reasons.append(f"{name}:nonfinite_or_failure")
        if value.get("target_limit_violations", -1) != 0:
            reasons.append(f"{name}:joint_target_limit")
        if name not in previous:
            continue
        if value.get("protected", True) != protected:
            reasons.append(f"{name}:protection_policy_changed")
        if not protected:
            continue
        rmse = value.get("steady_rmse", [])
        baseline = old.get("steady_rmse", [])
        if (len(rmse) != 3 or len(baseline) != 3 or value.get("steady_samples", 0) <= 0
                or old.get("steady_samples", 0) <= 0 or not all(math.isfinite(x) for x in baseline)):
            reasons.append(f"{name}:missing_steady_metrics")
            continue
        for axis, tolerance in enumerate((0.02, 0.02, 0.03)):
            if not math.isfinite(rmse[axis]) or rmse[axis] > baseline[axis] + tolerance:
                reasons.append(f"{name}:tracking_axis_{axis}")
        clipping = value.get("action_clip_fraction", float("nan"))
        old_clipping = old.get("action_clip_fraction", float("nan"))
        if (not math.isfinite(clipping) or not math.isfinite(old_clipping)
                or clipping > max(old_clipping + 0.05, 0.20)):
            reasons.append(f"{name}:action_clipping")
        # Loose regression tolerances, not the eventual gait-quality targets.
        for metric, tolerance in (("body_tilt_rms_deg", 3.0), ("body_height_std_m", 0.005),
                                  ("action_change_rms_per_step", 0.02), ("contact_slide_speed_proxy_mps", 0.03)):
            current = value.get(metric, float("nan"))
            previous_value = old.get(metric, float("nan"))
            if not math.isfinite(current) or not math.isfinite(previous_value) or current > previous_value + tolerance:
                reasons.append(f"{name}:{metric}")
    return {"status": "PASS" if not reasons else "FAIL", "reasons": reasons,
            "meaning": "old-skill regression screen, not full capability or reliability certification"}
