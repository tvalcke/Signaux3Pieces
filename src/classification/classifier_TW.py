"""Classification simple des pièces en TWD à partir des diamètres observés."""

from __future__ import annotations

TWD_DIAMETRES = {
    1   : 20,
    5   : 22,
    10  : 26,
    50  : 28,
}

FAMILY_VALUES = {
    "copper" : (1,),
    "silver" : (10,5),
    "gold"   : (50,)
}

FAMILY_LABELS = {
    "copper" : "cuivrée",
    "silver" : "argentée",
    "gold"   : "dorée",

    None : "Indeterminée"
}

GOLD_REFERENCE_VALUE = 50

GOLD_MIN_HUE = 19.0
GOLD_MIN_SAT = 80.0
COPPER_MAX_HUE = 18.5
COPPER_MIN_SAT = 60.0
MIN_BRIGHTNESS = 40.0

MAX_RELATIVE_ERROR = 0.05


def _relative_error(mesured_diameter: float, expected_diameter: float) -> float:
    """Calcule de l'erreur relative d'un diamètre mesuré et d'un diamètre théorique"""
    if expected_diameter <= 0:
        return float("inf")
    return abs(mesured_diameter - expected_diameter) / expected_diameter



def _candidate_scales(features: list[dict]) -> list[float]: 
    """Calcule les échelles candidates à partir des diamètres détectés."""
    diameters = [float(piece["diameter"]) for piece in features]
    candidate_scales: list[float] = []
    
    for _, reference in TWD_DIAMETRES.items():
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

    for coin_value, reference_diameter in TWD_DIAMETRES.items():
        expected_diameter = reference_diameter * scale
        error = _relative_error(diameter, expected_diameter)

        if error < best_error:
            best_error = error
            best_value = coin_value

    return best_value, best_error

def _hsv_is_gold(hsv: tuple[float, float, float] | None) -> bool:
    """Détecte une zone dorée : teinte élevée et forte saturation."""
    if hsv is None:
        return False

    h, s, v = hsv
    return v >= MIN_BRIGHTNESS and h >= GOLD_MIN_HUE and s >= GOLD_MIN_SAT


def _hsv_is_copper(hsv: tuple[float, float, float] | None) -> bool:
    """Détecte une zone cuivrée : teinte plus rouge (basse) et saturation moyenne."""
    if hsv is None:
        return False

    h, s, v = hsv
    return v >= MIN_BRIGHTNESS and h <= COPPER_MAX_HUE and s >= COPPER_MIN_SAT


def _hsv_is_silver(hsv: tuple[float, float, float] | None) -> bool:
    """Détecte une zone argentée : tout ce qui est lumineux mais ni doré ni cuivré."""
    if hsv is None:
        return False

    _, _, v = hsv
    return v >= MIN_BRIGHTNESS and not _hsv_is_gold(hsv) and not _hsv_is_copper(hsv)


def _mean_hsv(piece: dict) -> tuple[float, float, float] | None:
    """Moyenne HSV du centre et de l'anneau (ceux qui sont disponibles)."""
    values = [hsv for hsv in (piece.get("center_hsv"), piece.get("ring_hsv")) if hsv is not None]
    if not values:
        return None

    count = len(values)
    return (
        sum(v[0] for v in values) / count,
        sum(v[1] for v in values) / count,
        sum(v[2] for v in values) / count,
    )


def detect_color_family(piece: dict) -> str | None:
    """Estime la famille visuelle (doré, cuivré, argenté) à partir de la couleur moyenne HSV.

    L'ordre des tests compte : doré d'abord (le plus saturé), puis cuivré, puis argenté.
    """
    hsv = _mean_hsv(piece)
    if hsv is None:
        return None

    if _hsv_is_gold(hsv):
        return "gold"

    if _hsv_is_copper(hsv):
        return "copper"

    if _hsv_is_silver(hsv):
        return "silver"

    return None


def _estimated_reference_scale(features: list[dict]) -> float | None:
    """Estime l'échelle (px/mm) avec les pièces dorées (50 NT$), sinon par vote des échelles candidates."""
    reference_diameter = TWD_DIAMETRES[GOLD_REFERENCE_VALUE]
    scales: list[float] = []

    for piece in features:
        if detect_color_family(piece) == "gold":
            scales.append(float(piece["diameter"]) / reference_diameter)

    if scales:
        sorted_scales = sorted(scales)
        return sorted_scales[len(sorted_scales) // 2]

    return _scale_by_vote(features)


def _scale_by_vote(features: list[dict]) -> float | None:
    """Sans pièce dorée : l'échelle qui explique le plus de pièces gagne (None si ambigu)."""
    scored: list[tuple[int, float, float]] = []  # (pièces expliquées, erreur totale, échelle)

    for scale in _candidate_scales(features):
        explained = 0
        total_error = 0.0
        for piece in features:
            _, error = _best_match_for_scale(float(piece["diameter"]), scale)
            if error <= MAX_RELATIVE_ERROR:
                explained += 1
                total_error += error
        scored.append((explained, total_error, scale))

    if not scored:
        return None

    best_count = max(item[0] for item in scored)
    if best_count < 2:
        return None  # une seule pièce expliquée = aucune preuve

    top = sorted((item for item in scored if item[0] == best_count), key=lambda item: item[1])
    best_scale = top[0][2]

    for _, _, other_scale in top[1:]:
        if abs(other_scale - best_scale) / best_scale > MAX_RELATIVE_ERROR:
            return None  # deux échelles différentes expliquent autant : on ne tranche pas

    return best_scale


def _candidate_values_for_piece(piece: dict, reference_scale: float | None = None) -> list[tuple[float, float]]:
    """Retourne les valeurs compatibles avec la pièce, triées par erreur géométrique."""
    family = detect_color_family(piece)
    allowed = list(FAMILY_VALUES.get(family, TWD_DIAMETRES.keys())) if family is not None else list(TWD_DIAMETRES.keys())

    if reference_scale is None:
        return []

    candidates: list[tuple[float, float]] = []
    for value in allowed:
        expected_diameter = TWD_DIAMETRES[value] * reference_scale
        error = _relative_error(float(piece["diameter"]), expected_diameter)
        if error <= MAX_RELATIVE_ERROR:
            candidates.append((value, error))

    return sorted(candidates, key=lambda item: item[1])


def _piece_candidates(piece: dict, reference_scale: float | None = None) -> list[tuple[float, float]]:
    """Compare les valeurs candidates d'une pièce en utilisant une échelle commune estimée."""
    if reference_scale is None:
        return []

    return _candidate_values_for_piece(piece, reference_scale)


def _is_plausible_choice(best_error: float, second_error: float | None) -> bool:
    """Vérifie si une meilleure correspondance est suffisamment nette pour être attribuée."""
    if best_error > MAX_RELATIVE_ERROR:
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
    """Construit les classifications distinctes plausibles."""
    return _compatible_classifications(features)


def get_classification_details_twd(features: list[dict]) -> dict:
    """Retourne des informations utiles pour expliquer la classification sans rejeter tout le lot."""
    if not features:
        return {"best_error": None, "distinct_count": 0, "reason": "Aucune pièce détectée."}

    reference_scale = _estimated_reference_scale(features)
    if reference_scale is None:
        return {"best_error": None, "distinct_count": 0, "reason": "Échelle indisponible : aucune pièce dorée (50 NT$) et vote ambigu."}

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
            reasons.append(f"Pièce {piece['id']} : valeur unique {best_value} NT$.")
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


def classify_coins_twd(features: list[dict]) -> list[dict]:
    """Retourne une valeur estimée pour chaque pièce détectée, sans rejeter toutes les pièces pour une seule ambiguïté."""
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
        elif len(values) > 1 and new_piece["family"] in {"gold", "copper", "silver"}:
            best_value, _ = candidates[0]
            new_piece["value"] = best_value if candidates[0][1] <= MAX_RELATIVE_ERROR else None

        new_piece["status"] = _piece_status(new_piece)
        classified.append(new_piece)

    return classified
def _hsv_is_gold(hsv: tuple[float, float, float] | None) -> bool:
    """Détecte une zone dorée : teinte élevée et forte saturation."""
    if hsv is None:
        return False

    h, s, v = hsv
    return v >= MIN_BRIGHTNESS and h >= GOLD_MIN_HUE and s >= GOLD_MIN_SAT


def _hsv_is_copper(hsv: tuple[float, float, float] | None) -> bool:
    """Détecte une zone cuivrée : teinte plus rouge (basse) et saturation moyenne."""
    if hsv is None:
        return False

    h, s, v = hsv
    return v >= MIN_BRIGHTNESS and h <= COPPER_MAX_HUE and s >= COPPER_MIN_SAT


def _hsv_is_silver(hsv: tuple[float, float, float] | None) -> bool:
    """Détecte une zone argentée : tout ce qui est lumineux mais ni doré ni cuivré."""
    if hsv is None:
        return False

    _, _, v = hsv
    return v >= MIN_BRIGHTNESS and not _hsv_is_gold(hsv) and not _hsv_is_copper(hsv)


def _mean_hsv(piece: dict) -> tuple[float, float, float] | None:
    """Moyenne HSV du centre et de l'anneau (ceux qui sont disponibles)."""
    values = [hsv for hsv in (piece.get("center_hsv"), piece.get("ring_hsv")) if hsv is not None]
    if not values:
        return None

    count = len(values)
    return (
        sum(v[0] for v in values) / count,
        sum(v[1] for v in values) / count,
        sum(v[2] for v in values) / count,
    )


def detect_color_family(piece: dict) -> str | None:
    """Estime la famille visuelle (doré, cuivré, argenté) à partir de la couleur moyenne HSV.

    L'ordre des tests compte : doré d'abord (le plus saturé), puis cuivré, puis argenté.
    """
    hsv = _mean_hsv(piece)
    if hsv is None:
        return None

    if _hsv_is_gold(hsv):
        return "gold"

    if _hsv_is_copper(hsv):
        return "copper"

    if _hsv_is_silver(hsv):
        return "silver"

    return None


def _estimated_reference_scale(features: list[dict]) -> float | None:
    """Estime l'échelle (px/mm) avec les pièces dorées (50 NT$), sinon par vote des échelles candidates."""
    reference_diameter = TWD_DIAMETRES[GOLD_REFERENCE_VALUE]
    scales: list[float] = []

    for piece in features:
        if detect_color_family(piece) == "gold":
            scales.append(float(piece["diameter"]) / reference_diameter)

    if scales:
        sorted_scales = sorted(scales)
        return sorted_scales[len(sorted_scales) // 2]

    return _scale_by_vote(features)


def _scale_by_vote(features: list[dict]) -> float | None:
    """Sans pièce dorée : l'échelle qui explique le plus de pièces gagne (None si ambigu)."""
    scored: list[tuple[int, float, float]] = []  # (pièces expliquées, erreur totale, échelle)

    for scale in _candidate_scales(features):
        explained = 0
        total_error = 0.0
        for piece in features:
            _, error = _best_match_for_scale(float(piece["diameter"]), scale)
            if error <= MAX_RELATIVE_ERROR:
                explained += 1
                total_error += error
        scored.append((explained, total_error, scale))

    if not scored:
        return None

    best_count = max(item[0] for item in scored)
    if best_count < 2:
        return None  # une seule pièce expliquée = aucune preuve

    top = sorted((item for item in scored if item[0] == best_count), key=lambda item: item[1])
    best_scale = top[0][2]

    for _, _, other_scale in top[1:]:
        if abs(other_scale - best_scale) / best_scale > MAX_RELATIVE_ERROR:
            return None  # deux échelles différentes expliquent autant : on ne tranche pas

    return best_scale


def _candidate_values_for_piece(piece: dict, reference_scale: float | None = None) -> list[tuple[float, float]]:
    """Retourne les valeurs compatibles avec la pièce, triées par erreur géométrique."""
    family = detect_color_family(piece)
    allowed = list(FAMILY_VALUES.get(family, TWD_DIAMETRES.keys())) if family is not None else list(TWD_DIAMETRES.keys())

    if reference_scale is None:
        return []

    candidates: list[tuple[float, float]] = []
    for value in allowed:
        expected_diameter = TWD_DIAMETRES[value] * reference_scale
        error = _relative_error(float(piece["diameter"]), expected_diameter)
        if error <= MAX_RELATIVE_ERROR:
            candidates.append((value, error))

    return sorted(candidates, key=lambda item: item[1])


def _piece_candidates(piece: dict, reference_scale: float | None = None) -> list[tuple[float, float]]:
    """Compare les valeurs candidates d'une pièce en utilisant une échelle commune estimée."""
    if reference_scale is None:
        return []

    return _candidate_values_for_piece(piece, reference_scale)


def _is_plausible_choice(best_error: float, second_error: float | None) -> bool:
    """Vérifie si une meilleure correspondance est suffisamment nette pour être attribuée."""
    if best_error > MAX_RELATIVE_ERROR:
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
    """Construit les classifications distinctes plausibles."""
    return _compatible_classifications(features)


def get_classification_details_twd(features: list[dict]) -> dict:
    """Retourne des informations utiles pour expliquer la classification sans rejeter tout le lot."""
    if not features:
        return {"best_error": None, "distinct_count": 0, "reason": "Aucune pièce détectée."}

    reference_scale = _estimated_reference_scale(features)
    if reference_scale is None:
        return {"best_error": None, "distinct_count": 0, "reason": "Échelle indisponible : aucune pièce dorée (50 NT$) et vote ambigu."}

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
            reasons.append(f"Pièce {piece['id']} : valeur unique {best_value} NT$.")
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


def classify_coins_twd(features: list[dict]) -> list[dict]:
    """Retourne une valeur estimée pour chaque pièce détectée, sans rejeter toutes les pièces pour une seule ambiguïté."""
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
        elif len(values) > 1 and new_piece["family"] in {"gold", "copper", "silver"}:
            best_value, _ = candidates[0]
            new_piece["value"] = best_value if candidates[0][1] <= MAX_RELATIVE_ERROR else None

        new_piece["status"] = _piece_status(new_piece)
        classified.append(new_piece)

    return classified
