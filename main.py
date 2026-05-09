from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
import html
import http.cookiejar
import json
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from typing import Any

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt


DEFAULT_LINKS = [
    "https://drive.google.com/file/d/1QfwCIca1C-OY1RNjdILvVWUJlT5yhEiK/view?usp=drive_link",
    "https://drive.google.com/file/d/1CnyF4lFuNle0oLACn2uZWe5x0wKGbwBj/view?usp=drive_link",
    "https://drive.google.com/file/d/1AfFFDeJukhhasL-SvGvfD-6PC-6bzw9N/view?usp=drive_link",
    "https://drive.google.com/file/d/1lK1U_FiTj5p0YFB8RhVKGkJkoehQcHD0/view?usp=drive_link",
    "https://drive.google.com/drive/folders/1fagK1TSIi8Q7RWPLhX7YLNwVhc2KrqPd?usp=sharing",
    "https://drive.google.com/drive/folders/1aQL83JsN2-unaWwa0nep_EF5bGDTVIUh?usp=sharing",
    "https://drive.google.com/drive/folders/1Em1ocxAfOkyrU464a1s62TB8YNoCht9q?usp=sharing",
    "https://drive.google.com/drive/folders/1xI67J6aba7gKoDkmOVEKW0yKhePgRclJ?usp=sharing",
]

SUPPORTED_DATA_EXTENSIONS = {".csv", ".tsv", ".txt", ".xlsx", ".xls", ".json"}
SUPPORTED_ARCHIVE_EXTENSIONS = {".zip"}
DOWNLOAD_CHUNK_SIZE = 1024 * 1024
REQUEST_TIMEOUT_SECONDS = 60
FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"


@dataclass(frozen=True)
class DriveItem:
    file_id: str
    name: str
    mime_type: str


def extract_file_id(link_or_id: str) -> str:
    """Extract a Google Drive file id from a share URL or return a raw id."""
    parsed = urllib.parse.urlparse(link_or_id)
    query = urllib.parse.parse_qs(parsed.query)

    if "id" in query:
        return query["id"][0]

    match = re.search(r"/file/d/([^/]+)", parsed.path)
    if match:
        return match.group(1)

    if re.fullmatch(r"[\w-]{20,}", link_or_id):
        return link_or_id

    raise ValueError(f"Could not find a Google Drive file id in: {link_or_id}")


def extract_folder_id(link: str) -> str:
    """Extract a Google Drive folder id from a folder share URL."""
    parsed = urllib.parse.urlparse(link)
    match = re.search(r"/drive/folders/([^/?#]+)", parsed.path)
    if match:
        return match.group(1)

    raise ValueError(f"Could not find a Google Drive folder id in: {link}")


def is_drive_folder_link(link: str) -> bool:
    parsed = urllib.parse.urlparse(link)
    return bool(re.search(r"/drive/folders/[^/?#]+", parsed.path))


def drive_folder_url(folder_id: str) -> str:
    return f"https://drive.google.com/drive/folders/{folder_id}?usp=sharing"


def open_text_url(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return response.read().decode("utf-8", errors="ignore")


def clean_filename(filename: str) -> str:
    filename = pathlib.PurePath(filename).name
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", filename).strip()
    return filename or "downloaded_file"


def safe_stem(path: pathlib.Path) -> str:
    return re.sub(r"[^0-9A-Za-z_.-]+", "_", path.stem).strip("_") or "dataset"


def make_unique_path(path: pathlib.Path) -> pathlib.Path:
    if not path.exists():
        return path

    counter = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def filename_from_headers(headers: Any, fallback: str) -> str:
    content_disposition = headers.get("Content-Disposition", "")

    utf8_match = re.search(r"filename\*=UTF-8''([^;]+)", content_disposition)
    if utf8_match:
        return clean_filename(urllib.parse.unquote(utf8_match.group(1)))

    ascii_match = re.search(r'filename="?([^\";]+)"?', content_disposition)
    if ascii_match:
        return clean_filename(ascii_match.group(1))

    return clean_filename(fallback)


def confirm_token_from_response(body: bytes, cookie_jar: http.cookiejar.CookieJar) -> str | None:
    for cookie in cookie_jar:
        if cookie.name.startswith("download_warning"):
            return cookie.value

    html_text = html.unescape(body.decode("utf-8", errors="ignore"))
    match = re.search(r"[?&]confirm=([0-9A-Za-z_-]+)", html_text)
    if match:
        return match.group(1)

    return None


def save_response(response: Any, destination: pathlib.Path, first_chunk: bytes = b"") -> None:
    total_size = response.headers.get("Content-Length")
    total_size_int = int(total_size) if total_size and total_size.isdigit() else None
    downloaded = len(first_chunk)

    with destination.open("wb") as file:
        if first_chunk:
            file.write(first_chunk)

        while True:
            chunk = response.read(DOWNLOAD_CHUNK_SIZE)
            if not chunk:
                break

            file.write(chunk)
            downloaded += len(chunk)

            if total_size_int:
                percent = downloaded * 100 / total_size_int
                print(
                    f"\r  {downloaded / 1_048_576:.1f} MB / "
                    f"{total_size_int / 1_048_576:.1f} MB ({percent:.1f}%)",
                    end="",
                )
            else:
                print(f"\r  {downloaded / 1_048_576:.1f} MB", end="")

    print()


def open_drive_response(file_id: str, opener: urllib.request.OpenerDirector, cookie_jar: http.cookiejar.CookieJar) -> tuple[Any, bytes]:
    base_url = "https://drive.google.com/uc"
    params = {"export": "download", "id": file_id}
    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    response = opener.open(url, timeout=REQUEST_TIMEOUT_SECONDS)
    first_chunk = response.read(32768)
    content_type = response.headers.get("Content-Type", "").lower()

    if "text/html" not in content_type:
        return response, first_chunk

    token = confirm_token_from_response(first_chunk, cookie_jar)
    if not token:
        raise RuntimeError(
            "Google Drive returned a web page instead of the file. "
            "Check that the file is shared as 'Anyone with the link can view'."
        )

    params["confirm"] = token
    confirmed_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return opener.open(confirmed_url, timeout=REQUEST_TIMEOUT_SECONDS), b""


def download_drive_file(
    link_or_id: str,
    output_dir: pathlib.Path,
    filename_hint: str | None = None,
) -> pathlib.Path:
    file_id = extract_file_id(link_or_id)
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

    response, first_chunk = open_drive_response(file_id, opener, cookie_jar)

    output_dir.mkdir(parents=True, exist_ok=True)
    fallback_name = filename_hint or f"{file_id}.download"
    filename = filename_from_headers(response.headers, fallback_name)
    destination = make_unique_path(output_dir / filename)

    print(f"Downloading {file_id} -> {destination}")
    save_response(response, destination, first_chunk)
    return destination


def decode_javascript_string(raw: str) -> str:
    def replace_escape(match: re.Match[str]) -> str:
        escape = match.group(1)
        if escape.startswith("x"):
            return chr(int(escape[1:], 16))
        if escape.startswith("u"):
            return chr(int(escape[1:], 16))

        escape_map = {
            "\\": "\\",
            "'": "'",
            '"': '"',
            "/": "/",
            "b": "\b",
            "f": "\f",
            "n": "\n",
            "r": "\r",
            "t": "\t",
        }
        return escape_map.get(escape, escape)

    return re.sub(r"\\(x[0-9A-Fa-f]{2}|u[0-9A-Fa-f]{4}|.)", replace_escape, raw)


def folder_name_from_html(html_text: str, folder_id: str) -> str:
    match = re.search(r"<title>(.*?)\s+[\u2013-]\s+Google Drive</title>", html_text, flags=re.IGNORECASE)
    if match:
        return clean_filename(html.unescape(match.group(1)))
    return f"folder_{folder_id}"


def parse_drive_folder_items(html_text: str) -> list[DriveItem]:
    match = re.search(r"window\['_DRIVE_ivd'\]\s*=\s*'((?:\\.|[^'])*)'", html_text)
    if not match:
        raise RuntimeError(
            "Could not read the Google Drive folder listing. "
            "Make sure the folder is shared as 'Anyone with the link can view'."
        )

    decoded = decode_javascript_string(match.group(1))
    folder_data = json.loads(decoded)
    item_rows = folder_data[0] if folder_data and isinstance(folder_data[0], list) else []

    items = []
    for row in item_rows:
        if not isinstance(row, list) or len(row) < 4:
            continue

        file_id, name, mime_type = row[0], row[2], row[3]
        if isinstance(file_id, str) and isinstance(name, str) and isinstance(mime_type, str):
            items.append(DriveItem(file_id=file_id, name=clean_filename(name), mime_type=mime_type))

    return items


def list_drive_folder(folder_id: str) -> tuple[str, list[DriveItem]]:
    html_text = open_text_url(drive_folder_url(folder_id))
    return folder_name_from_html(html_text, folder_id), parse_drive_folder_items(html_text)


def optional_pandas():
    # Pandas and matplotlib are imported at the top now.
    # This function is kept for structural consistency or if it needs to check for installation later.
    return pd


def read_dataset(path: pathlib.Path):
    df = None
    if not path.is_file():
        print(f"Skipping analysis for {path.name}: not a file.")
        return None

    pd = optional_pandas()
    if pd is None:
        return None

    suffix = path.suffix.lower()

    try:
        if suffix == ".csv":
            df = pd.read_csv(path)
        elif suffix == ".tsv":
            df = pd.read_csv(path, sep="\t")
        elif suffix == ".txt":
            df = pd.read_csv(path, sep=None, engine="python")
        elif suffix in {".xlsx", ".xls"}:
            df = pd.read_excel(path)
        elif suffix == ".json":
            # Attempt to read as a common JSON format, e.g., list of records
            df = pd.read_json(path)
        else:
            print(f"Skipping analysis for {path.name}: unsupported file type '{suffix or 'unknown'}'.")

    except Exception as exc:
        print(f"Could not read {path.name} as tabular data: {exc}")
        return None

    if df is not None and df.empty:
        print(f"Skipping analysis for {path.name}: dataset is empty.")
        return None

    return df


def dataset_structure_report(df: Any, path: pathlib.Path, sample_rows: int) -> str:
    missing_counts = df.isna().sum()
    missing_percent = (missing_counts / max(len(df), 1) * 100).round(2)
    missing_table = df.__class__(
        {"missing_count": missing_counts, "missing_percent": missing_percent}
    )

    lines = [
        f"Dataset: {path.name}",
        f"Path: {path}",
        f"File size: {path.stat().st_size / 1_048_576:.2f} MB",
        f"Shape: {df.shape[0]} rows x {df.shape[1]} columns",
        "",
        "Columns and data types:",
        df.dtypes.to_string(),
        "",
        "Missing values:",
        missing_table.to_string(),
        "",
        f"First {sample_rows} rows:",
        df.head(sample_rows).to_string(index=False),
    ]

    numeric_columns = df.select_dtypes(include="number").columns
    if len(numeric_columns) > 0:
        lines.extend(
            [
                "",
                "Numeric summary:",
                df[numeric_columns].describe().transpose().to_string(),
            ]
        )

    return "\n".join(lines)


def save_matplotlib_visualization(
    df: Any,
    dataset_path: pathlib.Path,
    analysis_dir: pathlib.Path,
    numeric_columns: list[str],
    categorical_columns: list[str],
) -> pathlib.Path | None:
    matplotlib.use("Agg")

    if numeric_columns:
        plot_path = analysis_dir / f"{safe_stem(dataset_path)}_histograms.png"
        columns_to_plot = numeric_columns[:4]
        if len(columns_to_plot) == 0: return None

        fig, axes = plt.subplots(1, len(columns_to_plot), figsize=(4 * len(columns_to_plot), 4))
        if len(columns_to_plot) == 1:
            axes = [axes]

        for i, col in enumerate(columns_to_plot):
            df[col].hist(bins=20, ax=axes[i], grid=False)
            axes[i].set_title(col)
            axes[i].set_ylabel("Count")
        plt.suptitle(f"Numeric distributions: {dataset_path.name}")
        plt.tight_layout()
        plt.savefig(plot_path, dpi=140)
        plt.close(fig) # Close the figure to free up memory
        return plot_path

    if categorical_columns:
        column = categorical_columns[0]
        counts = df[column].astype(str).value_counts().head(10).sort_values()
        if counts.empty: return None

        plot_path = analysis_dir / f"{safe_stem(dataset_path)}_bar_chart.png"
        fig, ax = plt.subplots(figsize=(10, 6))
        counts.plot(kind="barh", ax=ax)
        ax.set_xlabel("Count")
        ax.set_title(f"Top values in {column}: {dataset_path.name}")
        plt.tight_layout()
        plt.savefig(plot_path, dpi=140)
        plt.close(fig) # Close the figure to free up memory
        return plot_path

    return None


def save_svg_visualization(
    df: Any,
    dataset_path: pathlib.Path,
    analysis_dir: pathlib.Path,
    numeric_columns: list[str],
    categorical_columns: list[str],
) -> pathlib.Path | None:
    plot_path = analysis_dir / f"{safe_stem(dataset_path)}_visualization.svg"

    if numeric_columns:
        column = numeric_columns[0]
        values = df[column].dropna().astype(float).tolist()
        if not values:
            return None

        labels, counts = histogram_counts(values)
        title = f"Distribution of {column} in {dataset_path.name}"
        write_svg_bar_chart(plot_path, title, labels, counts)
        return plot_path

    if categorical_columns:
        column = categorical_columns[0]
        counts = df[column].astype(str).value_counts().head(10).sort_values()
        if counts.empty:
            return None

        title = f"Top values in {column} for {dataset_path.name}"
        write_svg_bar_chart(plot_path, title, list(counts.index), list(counts.values))
        return plot_path

    return None


def save_visualization(df: Any, dataset_path: pathlib.Path, analysis_dir: pathlib.Path) -> pathlib.Path | None:
    numeric_columns = list(df.select_dtypes(include="number").columns)
    categorical_columns = list(df.select_dtypes(exclude="number").columns)

    # Try to use matplotlib first, fall back to SVG if it fails (e.g., if matplotlib not available)
    # The imports are already at the top, so this try-except might not be strictly needed now,
    # but it's a robust pattern if matplotlib installation is uncertain.
    try:
        return save_matplotlib_visualization(
            df, dataset_path, analysis_dir, numeric_columns, categorical_columns
        )
    except Exception as e:
        print(f"Warning: Matplotlib visualization failed ({e}). Falling back to SVG.", file=sys.stderr)
        return save_svg_visualization(
            df, dataset_path, analysis_dir, numeric_columns, categorical_columns
        )


def histogram_counts(values: list[float], bins: int = 10) -> tuple[list[str], list[int]]:
    if not values:
        return [], []

    minimum = min(values)
    maximum = max(values)

    if minimum == maximum:
        return [f"{minimum:.3g}"], [len(values)]

    step = (maximum - minimum) / bins
    if step == 0: # Handle cases where all values are the same but not zero
        return [f"{minimum:.3g}"], [len(values)]

    counts = [0] * bins

    for value in values:
        index = min(int((value - minimum) / step), bins - 1)
        counts[index] += 1

    labels = []
    for index in range(bins):
        start = minimum + index * step
        end = start + step
        labels.append(f"{start:.3g} to {end:.3g}")

    return labels, counts


def write_svg_bar_chart(path: pathlib.Path, title: str, labels: list[str], values: list[int]) -> None:
    width = 900
    row_height = 36
    top_margin = 70
    left_margin = 250
    right_margin = 70
    height = top_margin + len(labels) * row_height + 40
    max_value = max(values) if values else 1
    bar_max_width = width - left_margin - right_margin

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="24" y="36" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#222">{html.escape(title)}</text>',
    ]

    for index, (label, value) in enumerate(zip(labels, values)):
        y = top_margin + index * row_height
        bar_width = 0 if max_value == 0 else (value / max_value) * bar_max_width
        parts.extend(
            [
                f'<text x="24" y="{y + 19}" font-family="Arial, sans-serif" font-size="13" fill="#333">{html.escape(str(label)[:34])}</text>',
                f'<rect x="{left_margin}" y="{y}" width="{bar_width:.1f}" height="22" rx="3" fill="#3b82f6"/>',
                f'<text x="{left_margin + bar_width + 8:.1f}" y="{y + 16}" font-family="Arial, sans-serif" font-size="13" fill="#222">{value}</text>',
            ]
        )

    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def analyze_dataset(path: pathlib.Path, analysis_dir: pathlib.Path, sample_rows: int, output_stem: str | None = None) -> None:
    if path.suffix.lower() not in SUPPORTED_DATA_EXTENSIONS:
        print(f"Skipping analysis for {path.name}: unsupported file type.")
        return

    df = read_dataset(path)
    if df is None:
        return

    analysis_dir.mkdir(parents=True, exist_ok=True)
    report = dataset_structure_report(df, path, sample_rows)

    report_filename = f"{output_stem or safe_stem(path)}_structure.txt"
    report_path = analysis_dir / report_filename
    report_path.write_text(report, encoding="utf-8")

    print()
    print(report)
    print()
    print(f"Saved structure report -> {report_path}")

    plot_path = save_visualization(df, path, analysis_dir)
    if plot_path:
        # Rename plot path if output_stem is provided
        if output_stem:
            new_plot_filename = f"{output_stem}{plot_path.suffix}"
            new_plot_path = analysis_dir / new_plot_filename
            plot_path.rename(new_plot_path)
            print(f"Saved visualization -> {new_plot_path}")
        else:
            print(f"Saved visualization -> {plot_path}")
    else:
        print("No suitable columns found for visualization.")


def safe_extract_member(zip_file: zipfile.ZipFile, member: zipfile.ZipInfo, extract_dir: pathlib.Path) -> pathlib.Path:
    # Prevent directory traversal vulnerability
    member_path = pathlib.Path(member.filename)
    if member_path.is_absolute() or ".." in member_path.parts:
        raise ValueError(f"Invalid zip file member path: {member.filename}")
    
    # If the member is a directory, create it and return its path
    if member.is_dir():
        (extract_dir / member.filename).mkdir(parents=True, exist_ok=True)
        return extract_dir / member.filename

    # Ensure parent directory exists for the file
    (extract_dir / member.filename).parent.mkdir(parents=True, exist_ok=True)
    
    # Extract the file
    extracted_path = zip_file.extract(member, extract_dir)
    return pathlib.Path(extracted_path)


def analyze_zip_file(
    path: pathlib.Path,
    analysis_dir: pathlib.Path,
    sample_rows: int,
    output_prefix: str | None = None,
) -> None:
    try:
        with zipfile.ZipFile(path, "r") as zip_file:
            extract_dir = analysis_dir / f"{safe_stem(path)}_extracted"
            extract_dir.mkdir(parents=True, exist_ok=True)
            print(f"Extracting {path.name} to {extract_dir}/")

            for member in zip_file.infolist():
                if member.is_dir():
                    continue
                
                extracted_path = safe_extract_member(zip_file, member, extract_dir)
                
                # Only analyze if it's a supported data extension
                if extracted_path.suffix.lower() in SUPPORTED_DATA_EXTENSIONS:
                    stem_parts = [part for part in [output_prefix, safe_stem(path), safe_stem(extracted_path)] if part]
                    combined_output_stem = "_".join(stem_parts)
                    print(f"  Analyzing extracted file: {extracted_path.name}")
                    analyze_dataset(extracted_path, analysis_dir, sample_rows, output_stem=combined_output_stem)
                else:
                    print(f"  Skipping analysis for extracted file {extracted_path.name}: unsupported type.")
    except zipfile.BadZipFile:
        print(f"Failed to analyze {path.name}: not a valid zip file.", file=sys.stderr)
    except Exception as exc:
        print(f"An error occurred while analyzing zip file {path.name}: {exc}", file=sys.stderr)


def analyze_downloaded_file(
    path: pathlib.Path,
    analysis_dir: pathlib.Path,
    sample_rows: int,
    output_prefix: str | None = None,
) -> None:
    suffix = path.suffix.lower()

    if suffix in SUPPORTED_ARCHIVE_EXTENSIONS:
        analyze_zip_file(path, analysis_dir, sample_rows, output_prefix=output_prefix)
    elif suffix in SUPPORTED_DATA_EXTENSIONS:
        analyze_dataset(path, analysis_dir, sample_rows, output_stem=output_prefix)
    else:
        print(f"Skipping analysis for {path.name}: unsupported file type for analysis ('{suffix or 'unknown'}').")


def process_drive_file(
    link_or_id: str,
    output_dir: pathlib.Path,
    analysis_dir: pathlib.Path,
    sample_rows: int,
    skip_analysis: bool,
    filename_hint: str | None = None,
    output_prefix: str | None = None,
) -> pathlib.Path:
    downloaded_path = download_drive_file(link_or_id, output_dir, filename_hint=filename_hint)
    if not skip_analysis:
        analyze_downloaded_file(downloaded_path, analysis_dir, sample_rows, output_prefix=output_prefix)
    return downloaded_path


def process_drive_folder(
    folder_link: str,
    output_dir: pathlib.Path,
    analysis_dir: pathlib.Path,
    sample_rows: int,
    skip_analysis: bool,
    visited_folder_ids: set[str] | None = None,
) -> int:
    folder_id = extract_folder_id(folder_link)
    visited_folder_ids = visited_folder_ids or set()
    if folder_id in visited_folder_ids:
        print(f"Skipping already visited folder {folder_id}.")
        return 0

    visited_folder_ids.add(folder_id)
    folder_name, items = list_drive_folder(folder_id)
    folder_stem = safe_stem(pathlib.Path(folder_name))
    folder_output_dir = output_dir / folder_name

    print(f"Folder: {folder_name} (ID: {folder_id})")
    print(f"Found {len(items)} item(s) inside.")

    downloaded_count = 0
    for item_index, item in enumerate(items, start=1):
        print(f"\n  [{item_index}/{len(items)}] Processing item: {item.name}")

        if item.mime_type == FOLDER_MIME_TYPE:
            child_link = drive_folder_url(item.file_id)
            child_count = process_drive_folder(
                child_link,
                folder_output_dir,
                analysis_dir,
                sample_rows,
                skip_analysis,
                visited_folder_ids=visited_folder_ids,
            )
            downloaded_count += child_count
            continue

        if item.mime_type.startswith("application/vnd.google-apps."):
            print(f"  Skipping Google Workspace file type: {item.mime_type}")
            continue

        try:
            process_drive_file(
                item.file_id,
                folder_output_dir,
                analysis_dir,
                sample_rows,
                skip_analysis,
                filename_hint=item.name,
                output_prefix=folder_stem,
            )
            downloaded_count += 1
        except (urllib.error.URLError, ValueError, RuntimeError) as exc:
            print(f"  Failed to download/process {item.name} (ID: {item.file_id}): {exc}", file=sys.stderr)

    print(f"\nFinished processing folder {folder_name}: downloaded {downloaded_count} file(s) directly from this folder.")
    return downloaded_count


def process_drive_link(
    link: str,
    output_dir: pathlib.Path,
    analysis_dir: pathlib.Path,
    sample_rows: int,
    skip_analysis: bool,
) -> int:
    if is_drive_folder_link(link):
        return process_drive_folder(link, output_dir, analysis_dir, sample_rows, skip_analysis)
    else:
        process_drive_file(link, output_dir, analysis_dir, sample_rows, skip_analysis)
        return 1


def parse_args(arg_list: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download Google Drive files or folders, inspect tabular data, and save visualizations."
    )
    parser.add_argument("links", nargs="*", help="Google Drive file/folder links or raw file ids.")
    parser.add_argument("-o", "--output-dir", default="downloads", help="Folder for downloaded files.")
    parser.add_argument("--analysis-dir", default="analysis", help="Folder for reports and plots.")
    parser.add_argument("--sample-rows", type=int, default=5, help="Rows to show in each structure report.")
    parser.add_argument("--no-analysis", action="store_true", help="Download only; skip reports and plots.")

    # In Colab, sys.argv often contains kernel-related arguments.
    # We want to ignore these unless the user explicitly provides arguments.
    # If arg_list is None, we determine the actual list to parse.
    if arg_list is None:
        # Check if running in an IPython environment (like Colab)
        if 'ipykernel' in sys.modules or hasattr(sys, 'ps1'):
            # In IPython, we typically don't want to parse sys.argv, so pass an empty list
            args, unknown = parser.parse_known_args(args=[])
        else:
            # If not IPython, parse command line arguments
            args, unknown = parser.parse_known_args()
    else:
        # If arg_list is provided, use it directly
        args, unknown = parser.parse_known_args(args=arg_list)

    return args


def main() -> int:
    args = parse_args()
    links = args.links or DEFAULT_LINKS
    output_dir = pathlib.Path(args.output_dir)
    analysis_dir = pathlib.Path(args.analysis_dir)
    sample_rows = max(1, args.sample_rows)

    total_processed_items = 0
    for index, link in enumerate(links, start=1):
        print(f"\n[{index}/{len(links)}] Processing Google Drive link: {link}")
        try:
            processed_count = process_drive_link(
                link,
                output_dir,
                analysis_dir,
                sample_rows,
                skip_analysis=args.no_analysis,
            )
            total_processed_items += processed_count
        except (OSError, urllib.error.URLError, ValueError, RuntimeError) as exc:
            print(f"Failed to process {link}: {exc}", file=sys.stderr)
            # Do not exit, try to process next link

    print(f"\nDone. Total items processed: {total_processed_items} (including files inside folders).")
    return 0


if __name__ == "__main__":
    # In a notebook, running the main function directly is generally preferred
    # over exiting the system, as SystemExit causes the cell to terminate with an error.
    try:
        main()
    except SystemExit as e:
        # Catch SystemExit to prevent it from stopping the entire Colab runtime,
        # but still indicate an exit code.
        if e.code != 0:
            print(f"Script exited with error code {e.code}", file=sys.stderr)
