
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent

files = [
    ROOT / "app.py",
    *sorted((ROOT / "pages").glob("*.py"))
]

for path in files:
    source = path.read_text(encoding="utf-8")

    if "apply_theme()" in source:
        print(f"Already updated: {path.name}")
        continue

    # Remove old green dashboard CSS
    if path.name == "app.py":
        source = re.sub(
            r'\nst\.markdown\("""\s*<style>.*?</style>\s*""",\s*unsafe_allow_html=True\)\s*',
            "\n",
            source,
            count=1,
            flags=re.S
        )

    # Find page configuration
    match = re.search(
        r"^st\.set_page_config\(.*\)\s*$",
        source,
        flags=re.M
    )

    if not match:
        print(f"Skipped: {path.name}")
        continue

    theme_import = (
        "\nfrom farmcarbon.components.theme import apply_theme\n"
        "apply_theme()\n"
    )

    source = (
        source[:match.end()]
        + theme_import
        + source[match.end():]
    )

    path.write_text(source, encoding="utf-8")
    print(f"Updated: {path.name}")

print("\nFarmCarbon MRV UI update completed.")
