"""Classification simple des pièces en euros à partir des diamètres observés."""

from __future__ import annotations

EURO_DIAMETERS = {
    0.01: 16.25,
    0.02: 18.75,
    0.05: 21.25,
    0.10: 19.75,
    0.20: 22.25,
    0.50: 24.25,
    1.00: 23.25,
    2.00: 25.75,
}

FAMILY_VALUES = {
    "copper": (0.01, 0.02, 0.05),
    "gold": (0.10, 0.20, 0.50),
    "bicolor_1": (1.00,),
    "bicolor_2": (2.00,),
}

FAMILY_LABELS = {
    "copper": "Cuivrée",
    "gold": "Dorée",
    "bicolor_1": "Bicolore (1 €)",
    "bicolor_2": "Bicolore (2 €)",
    None: "Indéterminée",
}

MAX_RELATIVE_ERROR = 0.05


def _relative_error(measured_diameter: float, expected_diameter: float) -> float:
    """Calcule l'erreur relative entre un diamètre mesuré et un diamètre théorique."""
    if expected_diameter <= 0:
        return float("inf")
    return abs(measured_diameter - expected_diameter) / expected_diameter


def _candidate_scales(features: list[dict]) -> list[float]:
    """Calcule les échelles candidates à partir des diamètres détectés."""
    diameters = [float(piece["diameter"]) for piece in features]
    candidate_scales: list[float] = []

    for _, reference in EURO_DIAMETERS.items():
        for diameter in diameters:
            if reference > 0:
                candidate_scales.append(diameter / reference)

    unique_scales: list[float] = []
    for scale in candidate_scales:
        rounded_scale = round(scale, 6)
        if rounded_scale not in [round(item, 6) for item in unique_scales]:
            unique_scales.append(scale)

    return unique_scales


def _best_match_for_scale(diameter: float, scale: float) -> tuple[float | None, float]:
    """Retourne la valeur monétaire la plus proche et son erreur relative."""
    best_value = None
    best_error = float("inf")

    for coin_value, reference_diameter in EURO_DIAMETERS.items():
        expected_diameter = reference_diameter * scale
        error = _relative_error(diameter, expected_diameter)

        if error < best_error:
            best_error = error
            best_value = coin_value

    return best_value, best_error


def _bgr_is_silver(bgr: tuple[float, float, float]) -> bool:
    """Détecte une zone argentée à partir des canaux BGR, même si la saturation est faible."""
    b, g, r = bgr
    channel_spread = max(abs(b - g), abs(g - r), abs(b - r))
    brightness = (b + g + r) / 3
    return channel_spread < 25 and brightness > 80


def _bgr_is_gold(bgr: tuple[float, float, float]) -> bool:
    """Détecte une zone dorée à partir du BGR, sans se baser sur une teinte H incertaine."""
    b, g, r = bgr
    brightness = (b + g + r) / 3
    return r > g > b and (r - g) >= 10 and (r - b) > 35 and brightness > 80 and g > 90


def _bgr_is_copper(bgr: tuple[float, float, float]) -> bool:
    """Détecte une zone cuivrée à partir du BGR sans se baser sur la teinte H."""
    b, g, r = bgr
    brightness = (b + g + r) / 3
    return r > g and g > b and (r - g) >= 10 and (r - b) > 20 and brightness > 50 and g < 120


def _hsv_is_gold(hsv: tuple[float, float, float] | None) -> bool:
    """Détecte une zone dorée si une mesure HSV utile est disponible."""
    if hsv is None:
        return False

    h, s, v = hsv
    return v >= 35 and s > 10 and 15 <= h <= 45


def _hsv_is_copper(hsv: tuple[float, float, float] | None) -> bool:
    """Détecte une zone cuivrée si une mesure HSV utile est disponible."""
    if hsv is None:
        return False

    h, s, v = hsv
    return v >= 25 and s > 12 and 0 <= h <= 18


def _hsv_is_silver(hsv: tuple[float, float, float] | None) -> bool:
    """Détecte une zone argentée à partir d'une saturation faible, sans utiliser H comme preuve."""
    if hsv is None:
        return False

    h, s, v = hsv
    return v > 40 and s <= 35


def detect_color_family(piece: dict) -> str | None:
    """Estime la famille visuelle en comparant centre et anneau, avec une logique simple et cohérente."""
    center_bgr = piece.get("center_bgr")
    ring_bgr = piece.get("ring_bgr")
    center_hsv = piece.get("center_hsv")
    ring_hsv = piece.get("ring_hsv")

    if center_bgr is None or ring_bgr is None:
        return None

    center_silver = _bgr_is_silver(center_bgr) or _hsv_is_silver(center_hsv)
    ring_silver = _bgr_is_silver(ring_bgr) or _hsv_is_silver(ring_hsv)
    center_gold = _bgr_is_gold(center_bgr) or _hsv_is_gold(center_hsv)
    ring_gold = _bgr_is_gold(ring_bgr) or _hsv_is_gold(ring_hsv)
    center_copper = _bgr_is_copper(center_bgr) or _hsv_is_copper(center_hsv)
    ring_copper = _bgr_is_copper(ring_bgr) or _hsv_is_copper(ring_hsv)

    if center_silver and ring_gold:
        return "bicolor_1"

    if center_gold and ring_silver:
        return "bicolor_2"

    if center_gold or ring_gold:
        return "gold"

    if center_copper or ring_copper:
        return "copper"

    return None


def _estimated_reference_scale(features: list[dict]) -> float | None:
    """Estime une échelle à partir des pièces bicolores, avec une tolérance raisonnable."""
    scales: list[float] = []

    for piece in features:
        family = detect_color_family(piece)
        if family == "bicolor_1":
            scales.append(float(piece["diameter"]) / 23.25)
        elif family == "bicolor_2":
            scales.append(float(piece["diameter"]) / 25.75)

    if not scales:
        return None

    sorted_scales = sorted(scales)
    return sorted_scales[len(sorted_scales) // 2]


def _candidate_values_for_piece(piece: dict, reference_scale: float | None = None) -> list[tuple[float, float]]:
    """Retourne les valeurs compatibles avec la pièce, triées par erreur géométrique."""
    family = detect_color_family(piece)
    allowed = list(FAMILY_VALUES.get(family, EURO_DIAMETERS.keys())) if family is not None else list(EURO_DIAMETERS.keys())

    if reference_scale is None:
        return []

    candidates: list[tuple[float, float]] = []
    for value in allowed:
        expected_diameter = EURO_DIAMETERS[value] * reference_scale
        error = _relative_error(float(piece["diameter"]), expected_diameter)
        if error <= 0.15:
            candidates.append((value, error))

    return sorted(candidates, key=lambda item: item[1])


def _piece_candidates(piece: dict, reference_scale: float | None = None) -> list[tuple[float, float]]:
    """Compare les valeurs candidates d'une pièce en utilisant une échelle commune estimée."""
    if reference_scale is None:
        return []

    return _candidate_values_for_piece(piece, reference_scale)


def _is_plausible_choice(best_error: float, second_error: float | None) -> bool:
    """Vérifie si une meilleure correspondance est suffisamment nette pour être attribuée."""
    if best_error > 0.10:
        return False

    if second_error is None:
        return True

    return (second_error - best_error) > 0.03


def _compatible_classifications(features: list[dict]) -> dict[tuple[float, ...], float]:
    """Construit les classifications plausibles, sans rejeter tout le lot pour une seule pièce ambiguë."""
    reference_scale = _estimated_reference_scale(features)
    if reference_scale is None:
        return {}

    plausible_classifications: dict[tuple[float, ...], float] = {}
    values: list[float] = []
    total_error = 0.0

    for piece in features:
        candidates = _piece_candidates(piece, reference_scale)
        if not candidates:
            return {}

        best_value, best_error = candidates[0]
        values.append(best_value)
        total_error += best_error

    plausible_classifications[tuple(values)] = total_error / len(features)
    return plausible_classifications


def _plausible_classifications(features: list[dict]) -> dict[tuple[float, ...], float]:
    """Construit les classifications distinctes plausibles à partir des échelles candidates."""
    return _compatible_classifications(features)


def get_classification_details(features: list[dict]) -> dict:
    """Retourne des informations utiles pour expliquer la classification sans rejeter tout le lot."""
    if not features:
        return {"best_error": None, "distinct_count": 0, "reason": "Aucune pièce détectée."}

    if len(features) == 1:
        return {"best_error": None, "distinct_count": 0, "reason": "Une pièce seule ne permet pas de fixer l'échelle."}

    reference_scale = _estimated_reference_scale(features)
    if reference_scale is None:
        return {"best_error": None, "distinct_count": 0, "reason": "Échelle indisponible : aucune pièce bicolore assez fiable."}

    reasons = []
    best_error = 0.0
    candidate_values_per_piece: list[set[float]] = [set() for _ in features]

    for index, piece in enumerate(features):
        family = detect_color_family(piece)
        if family is None:
            reasons.append(f"Pièce {piece['id']} : famille de couleur inconnue.")
            continue

        candidates = _piece_candidates(piece, reference_scale)
        if not candidates:
            reasons.append(f"Pièce {piece['id']} : aucune valeur compatible avec l'échelle.")
            continue

        values = [value for value, _ in candidates]
        candidate_values_per_piece[index].update(values)
        best_value, best_error_piece = candidates[0]
        best_error += best_error_piece

        if len(candidates) == 1:
            reasons.append(f"Pièce {piece['id']} : valeur unique {best_value} €.")
        else:
            reasons.append(f"Pièce {piece['id']} : plusieurs valeurs plausibles : {values}.")

    if not any(candidate_values_per_piece):
        return {"best_error": None, "distinct_count": 0, "reason": "Aucune valeur compatible avec l'échelle courante."}

    return {
        "best_error": best_error / max(1, len(features)),
        "distinct_count": len({tuple(sorted(values)) for values in candidate_values_per_piece if values}),
        "reason": " ; ".join(reasons),
        "reason_by_piece": reasons,
    }


def _piece_status(piece: dict) -> str:
    """Détermine si la pièce est identifiée, incertaine ou inconnue."""
    possible_values = piece.get("possible_values") or []
    value = piece.get("value")

    if value is not None and len(possible_values) <= 1:
        return "identified"

    if value is not None and len(possible_values) > 1:
        return "uncertain"

    return "unknown"


def classify_coins(features: list[dict]) -> list[dict]:
    """Retourne une valeur estimée pour chaque pièce détectée, sans rejeter toutes les pièces pour une seule ambigüité."""
    if not features:
        return []

    reference_scale = _estimated_reference_scale(features)

    classified = []
    for piece in features:
        new_piece = dict(piece)
        new_piece["family"] = detect_color_family(new_piece)
        new_piece["possible_values"] = []
        new_piece["value"] = None
        new_piece["status"] = "unknown"

        if reference_scale is None:
            if new_piece["family"] == "bicolor_1":
                new_piece["value"] = 1.00
            elif new_piece["family"] == "bicolor_2":
                new_piece["value"] = 2.00
            new_piece["status"] = _piece_status(new_piece)
            classified.append(new_piece)
            continue

        candidates = _piece_candidates(new_piece, reference_scale)
        if not candidates:
            classified.append(new_piece)
            continue

        values = [value for value, _ in candidates]
        new_piece["possible_values"] = values
        if len(values) == 1:
            new_piece["value"] = values[0]
        elif len(values) > 1 and new_piece["family"] in {"gold", "copper", "bicolor_1", "bicolor_2"}:
            best_value, _ = candidates[0]
            new_piece["value"] = best_value if candidates[0][1] <= 0.08 else None

        new_piece["status"] = _piece_status(new_piece)
        classified.append(new_piece)

    return classified
