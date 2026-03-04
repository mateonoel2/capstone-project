from pathlib import Path


def get_pdf_files(directory: Path) -> list[Path]:
    return sorted(directory.glob("*.pdf"))


def get_image_files(directory: Path) -> list[Path]:
    extensions = ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.webp"]
    files = []
    for ext in extensions:
        files.extend(directory.glob(ext))
    return sorted(files)


def ensure_directory(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def get_all_files(directory: Path, extensions: list[str] | None = None) -> list[Path]:
    if extensions is None:
        return sorted([f for f in directory.iterdir() if f.is_file()])

    files = []
    for ext in extensions:
        if not ext.startswith("*"):
            ext = f"*.{ext}"
        files.extend(directory.glob(ext))
    return sorted(files)
