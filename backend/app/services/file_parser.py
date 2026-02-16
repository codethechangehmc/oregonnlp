"""Parse uploaded files into a list of text responses."""

import io

import pandas as pd


def parse_upload(content: bytes, filename: str) -> list[dict]:
    """Read file bytes and return [{"id": int, "text": str}, ...]."""
    if filename.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(content))
    elif filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(content))
    elif filename.endswith(".json"):
        df = pd.read_json(io.BytesIO(content))
    elif filename.endswith(".txt"):
        lines = content.decode("utf-8", errors="replace").strip().splitlines()
        return [{"id": i, "text": line.strip()} for i, line in enumerate(lines) if line.strip()]
    else:
        raise ValueError(f"Unsupported file type: {filename}")

    text_col = _detect_text_column(df)
    texts = df[text_col].dropna().astype(str).tolist()
    return [{"id": i, "text": t} for i, t in enumerate(texts)]


def _detect_text_column(df: pd.DataFrame) -> str:
    str_cols = df.select_dtypes(include="object").columns
    if len(str_cols) == 0:
        raise ValueError("No text columns found in file")
    if len(str_cols) == 1:
        return str_cols[0]
    avg_lens = {col: df[col].dropna().astype(str).str.len().mean() for col in str_cols}
    return max(avg_lens, key=avg_lens.get)  # type: ignore[arg-type]
