"""
Formula comparison helpers for formula-aware evaluation.

- Loads page-wise formula OCR output
- Normalizes LaTeX-like strings
- Uses SymPy to compare mathematical equivalence when possible
- Falls back to string similarity when parsing fails
"""

import json
import os
import re
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple

try:
    import sympy as sp
    from sympy.parsing.latex import parse_latex
    from sympy.parsing.sympy_parser import parse_expr
except ImportError:  # optional until formula-aware evaluation is used
    sp = None
    parse_latex = None
    parse_expr = None


def load_formula_page(base_name: str, page_no: int, formula_root: str) -> List[Dict[str, Any]]:
    path = os.path.join(formula_root, f"{base_name}_page{page_no}_formulas.json")
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return list(data.get("formulas", []) or [])


def _normalize_formula_text(text: str) -> str:
    text = (text or "").strip()
    text = text.replace("$", "")
    text = text.replace("\\left", "")
    text = text.replace("\\right", "")
    text = text.replace("\\,", "")
    text = text.replace("\\!", "")
    text = re.sub(r"\s+", "", text)
    return text


def _latexish_to_sympy(text: str) -> str:
    converted = _normalize_formula_text(text)

    replacements = {
        "\\cdot": "*",
        "\\times": "*",
        "\\div": "/",
        "\\pi": "pi",
        "\\theta": "theta",
        "\\alpha": "alpha",
        "\\beta": "beta",
        "\\gamma": "gamma",
        "\\lambda": "lambda",
        "\\mu": "mu",
        "\\sigma": "sigma",
        "\\Delta": "Delta",
    }
    for src, dest in replacements.items():
        converted = converted.replace(src, dest)

    frac_pattern = re.compile(r"\\frac\{([^{}]+)\}\{([^{}]+)\}")
    while frac_pattern.search(converted):
        converted = frac_pattern.sub(r"(\1)/(\2)", converted)

    sqrt_pattern = re.compile(r"\\sqrt\{([^{}]+)\}")
    while sqrt_pattern.search(converted):
        converted = sqrt_pattern.sub(r"sqrt(\1)", converted)

    converted = converted.replace("{", "(").replace("}", ")")
    converted = converted.replace("^", "**")
    return converted


def _parse_formula(text: str):
    if sp is None:
        return None

    normalized = _normalize_formula_text(text)
    if not normalized:
        return None

    if parse_latex is not None:
        try:
            return parse_latex(normalized)
        except Exception:
            pass

    if parse_expr is not None:
        try:
            return parse_expr(_latexish_to_sympy(normalized), evaluate=True)
        except Exception:
            return None

    return None


def _are_equivalent(expr_a, expr_b) -> bool:
    if sp is None or expr_a is None or expr_b is None:
        return False

    try:
        if isinstance(expr_a, sp.Equality) and isinstance(expr_b, sp.Equality):
            lhs_diff = sp.simplify((expr_a.lhs - expr_a.rhs) - (expr_b.lhs - expr_b.rhs))
            rhs_diff = sp.simplify((expr_a.lhs - expr_a.rhs) + (expr_b.lhs - expr_b.rhs))
            if lhs_diff == 0 or rhs_diff == 0:
                return True
    except Exception:
        pass

    try:
        if sp.simplify(expr_a - expr_b) == 0:
            return True
    except Exception:
        pass

    try:
        equals_result = expr_a.equals(expr_b)
        if equals_result is True:
            return True
    except Exception:
        pass

    return False


def compare_formula_pair(ideal_formula: str, student_formula: str) -> Tuple[float, str]:
    ideal_norm = _normalize_formula_text(ideal_formula)
    student_norm = _normalize_formula_text(student_formula)

    if not ideal_norm and not student_norm:
        return 1.0, "No formula was expected and none was detected."
    if ideal_norm and not student_norm:
        return 0.0, "Expected formula is missing from the student answer."
    if not ideal_norm and student_norm:
        return 0.25, "Student wrote an additional formula not found in the reference."
    if ideal_norm == student_norm:
        return 1.0, "Formula matches the reference exactly."

    expr_a = _parse_formula(ideal_norm)
    expr_b = _parse_formula(student_norm)
    if expr_a is not None and expr_b is not None and _are_equivalent(expr_a, expr_b):
        return 1.0, "Formula is mathematically equivalent to the reference."

    ratio = SequenceMatcher(None, ideal_norm, student_norm).ratio()
    if ratio >= 0.9:
        return 0.8, "Formula is close to the reference but not provably equivalent."
    if ratio >= 0.75:
        return 0.6, "Formula is partially correct but differs in some terms or symbols."
    if ratio >= 0.55:
        return 0.35, "Formula captures only part of the reference expression."
    return 0.0, "Formula is substantially different from the reference."


def score_formula_sets(
    ideal_formulas: List[Dict[str, Any]],
    student_formulas: List[Dict[str, Any]],
) -> Tuple[Optional[float], str]:
    if not ideal_formulas:
        return None, "No reference formula was detected for this question."

    if not student_formulas:
        return 0.0, "Reference formula detected, but no student formula was found."

    scores: List[float] = []
    feedback_parts: List[str] = []

    for index, ideal_item in enumerate(ideal_formulas):
        ideal_latex = ideal_item.get("latex") or ideal_item.get("ocr_text") or ""
        if index >= len(student_formulas):
            scores.append(0.0)
            feedback_parts.append("A required formula is missing from the student's answer.")
            continue

        student_item = student_formulas[index]
        student_latex = student_item.get("latex") or student_item.get("ocr_text") or ""
        score, feedback = compare_formula_pair(ideal_latex, student_latex)
        scores.append(score)
        feedback_parts.append(feedback)

    if len(student_formulas) > len(ideal_formulas):
        feedback_parts.append("Additional student formulas were detected beyond the reference set.")

    similarity = sum(scores) / len(scores) if scores else 0.0
    return similarity, " ".join(feedback_parts[:3])
