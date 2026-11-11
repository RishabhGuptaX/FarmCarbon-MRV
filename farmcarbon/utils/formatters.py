"""Display formatting helpers."""
def fmt(value, digits=2, suffix=""):
    if value is None:
        return "—"
    try:
        return f"{float(value):,.{digits}f}{suffix}"
    except (TypeError, ValueError):
        return f"{value}{suffix}"
