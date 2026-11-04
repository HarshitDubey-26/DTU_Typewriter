"""Colour palettes for dark and light themes."""

DARK = {
    "bg":           "#1b2838",
    "fg":           "#e0e0e0",
    "accent":       "#26c6da",
    "select_bg":    "#37474f",
    "status_bg":    "#0f1b27",
    "status_fg":    "#90caf9",
    "toolbar_bg":   "#162231",
    "entry_bg":     "#263545",
    "entry_fg":     "#e0e0e0",
    "button_bg":    "#1e88e5",
    "button_fg":    "#ffffff",
    "ref_bg":       "#1a2636",
    "ref_fg":       "#b0bec5",
    "correct_fg":   "#66bb6a",
    "error_fg":     "#ef5350",
    "cursor":       "#26c6da",
}

LIGHT = {
    "bg":           "#f5f5f5",
    "fg":           "#212121",
    "accent":       "#0288d1",
    "select_bg":    "#bbdefb",
    "status_bg":    "#e0e0e0",
    "status_fg":    "#37474f",
    "toolbar_bg":   "#e8e8e8",
    "entry_bg":     "#ffffff",
    "entry_fg":     "#212121",
    "button_bg":    "#1565c0",
    "button_fg":    "#ffffff",
    "ref_bg":       "#eceff1",
    "ref_fg":       "#455a64",
    "correct_fg":   "#2e7d32",
    "error_fg":     "#c62828",
    "cursor":       "#0288d1",
}

def get_theme(name: str) -> dict:
    return DARK if name == "dark" else LIGHT
