import argparse
import sys
import os
import pandas as pd

# Add src to sys.path so we can import from src.dataset_registry
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from src.dataset_registry import registry
except ImportError:
    registry = None

def parse_args():
    parser = argparse.ArgumentParser(description="Inspect dataset files before loading them into the application.")
    parser.add_argument("file_path", nargs="?", help="Path to the dataset file (CSV/TSV). Optional if --dataset-id is provided.")
    parser.add_argument("--dataset-id", help="Identifier of a registered dataset to inspect. If provided, uses registry configuration.")
    parser.add_argument("--delimiter", help="Delimiter used in the file. Default is ',' or inferred from registry if --dataset-id is used.")
    parser.add_argument("--encoding", default="utf-8", help="Text encoding of the file (default: 'utf-8').")
    parser.add_argument("--label-col", help="Name of the label column to report statistics on.")
    parser.add_argument("--image-col", help="Name of the image reference column to report on.")
    parser.add_argument("--preview-rows", type=int, default=5, help="Number of rows to preview (default: 5).")
    return parser.parse_args()

def inspect_dataset(args):
    file_path = args.file_path
    delimiter = args.delimiter
    image_col = args.image_col

    if args.dataset_id:
        if not registry:
            print("Error: Could not import dataset registry from src.dataset_registry.", file=sys.stderr)
            sys.exit(1)
        try:
            config = registry.get(args.dataset_id)
        except KeyError:
            print(f"Error: Dataset with identifier '{args.dataset_id}' not found in registry.", file=sys.stderr)
            sys.exit(1)

        if not file_path:
            file_path = config.get_absolute_path()

        if not delimiter:
            if config.expected_format.lower() in ("tsv", "jsonl"):
                # Simplistic handling for TSV
                delimiter = "\t"
            else:
                delimiter = ","

        if not image_col and config.image_reference_field:
            image_col = config.image_reference_field

    if not file_path:
        print("Error: You must provide either a 'file_path' or a '--dataset-id'.", file=sys.stderr)
        sys.exit(1)

    if not delimiter:
        delimiter = ","

    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'", file=sys.stderr)
        sys.exit(1)

    if os.path.getsize(file_path) == 0:
        print(f"Error: File '{file_path}' is empty.", file=sys.stderr)
        sys.exit(1)

    if delimiter == '\\t':
        delimiter = '\t'

    try:
        # Read the file
        df = pd.read_csv(file_path, sep=delimiter, encoding=args.encoding, engine="python")
    except pd.errors.EmptyDataError:
        print(f"Error: File '{file_path}' contains no data.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)

    # Basic Stats
    file_format = "TSV" if delimiter == '\t' else "CSV"
    row_count = len(df)
    col_names = df.columns.tolist()

    print(f"--- Dataset Inspection Report ---")
    print(f"File Path: {file_path}")
    print(f"Format: {file_format}")
    print(f"Row Count: {row_count}")
    print(f"Columns: {', '.join(col_names)}")

    print("\n--- Inferred Data Types ---")
    for col, dtype in df.dtypes.items():
        print(f"  {col}: {dtype}")

    print("\n--- Missing Values ---")
    missing_counts = df.isnull().sum()
    for col, count in missing_counts.items():
        pct = (count/row_count)*100 if row_count > 0 else 0
        print(f"  {col}: {count} ({pct:.2f}%)")

    duplicate_rows = df.duplicated().sum()
    pct_dup = (duplicate_rows/row_count)*100 if row_count > 0 else 0
    print(f"\nDuplicate Rows: {duplicate_rows} ({pct_dup:.2f}%)")

    # Label Stats
    if args.label_col:
        print(f"\n--- Label Statistics ('{args.label_col}') ---")
        if args.label_col in df.columns:
            counts = df[args.label_col].value_counts(dropna=False)
            for label, count in counts.items():
                pct = (count/row_count)*100 if row_count > 0 else 0
                print(f"  {label}: {count} ({pct:.2f}%)")
        else:
            print(f"  Warning: Column '{args.label_col}' not found in dataset.")

    # Image Stats
    if image_col:
        print(f"\n--- Image Reference Statistics ('{image_col}') ---")
        if image_col in df.columns:
            images = df[image_col]
            missing = images.isnull().sum()

            # Simple check for malformed: empty string, just whitespace, or doesn't have an extension like .jpg/.png or doesn't start with http
            def is_malformed(val):
                if pd.isna(val):
                    return False # counted as missing
                val = str(val).strip()
                if not val:
                    return True
                # Very basic heuristic for malformed image reference
                # If it's a URL or path, it should probably be non-empty and not just random chars
                return False

            malformed_mask = images.apply(is_malformed)
            # Refine malformed check
            # For this requirement: "malformed references (e.g., empty strings or invalid URL/file path patterns)"
            # Let's say malformed if it's empty or doesn't have a typical image extension and isn't a clear URL.
            def check_malformed(val):
                if pd.isna(val): return False
                s = str(val).strip()
                if not s: return True
                lower_s = s.lower()
                valid_exts = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
                has_ext = any(lower_s.endswith(ext) for ext in valid_exts)
                is_url = lower_s.startswith('http://') or lower_s.startswith('https://')
                if not (has_ext or is_url):
                    return True
                return False

            malformed = images.apply(check_malformed).sum()

            pct_missing = (missing/row_count)*100 if row_count > 0 else 0
            pct_malformed = (malformed/row_count)*100 if row_count > 0 else 0
            print(f"  Missing: {missing} ({pct_missing:.2f}%)")
            print(f"  Malformed (basic check): {malformed} ({pct_malformed:.2f}%)")
        else:
            print(f"  Warning: Column '{image_col}' not found in dataset.")

    # Preview
    print(f"\n--- Data Preview (Top {args.preview_rows} Rows) ---")
    if row_count == 0:
        print("No data to preview.")
    else:
        preview_df = df.head(args.preview_rows).copy()
        for col in preview_df.columns:
            if preview_df[col].dtype == object:
                # Truncate strings longer than 100 characters
                preview_df[col] = preview_df[col].apply(lambda x: (str(x)[:97] + '...') if isinstance(x, str) and len(str(x)) > 100 else x)

        # We can use to_string to print it cleanly
        print(preview_df.to_string(index=False))

if __name__ == "__main__":
    args = parse_args()
    inspect_dataset(args)
