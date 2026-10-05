"""Create a reproducible Lambda ZIP using only the Python standard library."""
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
output = ROOT / "build" / "lambda.zip"
output.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    for source in sorted((ROOT / "app").glob("*.py")):
        info = zipfile.ZipInfo(source.relative_to(ROOT).as_posix(), (2026, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        archive.writestr(info, source.read_bytes())
print(output)
