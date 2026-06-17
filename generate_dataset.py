"""
Download the DREBIN-215 Android Malware Dataset.

Source: Figshare (S.Y. Yerima)
DOI: 10.6084/m9.figshare.5854653.v1

Dataset: 15,036 apps (5,560 malware + 9,476 benign) with 215 binary features
extracted via static analysis of Android apps (permissions, API calls, intents, commands).

Citation:
  Yerima, S.Y. and Sezer, S., 2018. DroidFusion: A Novel Multilevel Classifier
  Fusion Approach for Android Malware Detection. IEEE Transactions on Cybernetics.

  Arp, D. et al., 2014. DREBIN: Effective and Explainable Detection of Android
  Malware in Your Pocket. NDSS 2014.
"""

import os
import sys
import time
import hashlib

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CSV_PATH = os.path.join(DATA_DIR, "drebin215.csv")

# Figshare file download URL for the DREBIN-215 CSV
DOWNLOAD_URL = "https://ndownloader.figshare.com/files/10391991"

# Expected dataset properties (for validation)
EXPECTED_MIN_ROWS = 15000
EXPECTED_COLS = 216  # 215 features + 1 class label


def download_dataset():
    """Download the DREBIN-215 dataset from Figshare."""
    import urllib.request

    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(CSV_PATH) and os.path.getsize(CSV_PATH) > 1000:
        print(f"[✓] Dataset already exists at: {CSV_PATH}")
        print(f"    Size: {os.path.getsize(CSV_PATH):,} bytes")
        return True

    print(f"[↓] Downloading DREBIN-215 dataset from Figshare...")
    print(f"    URL: {DOWNLOAD_URL}")
    print(f"    Destination: {CSV_PATH}")

    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(
                DOWNLOAD_URL,
                headers={"User-Agent": "Mozilla/5.0 (AegisML-ThreatShield)"},
            )
            resp = urllib.request.urlopen(req, timeout=60)

            if resp.status == 202:
                print(f"    Attempt {attempt}/{max_retries}: Server is preparing file (HTTP 202), retrying in 5s...")
                time.sleep(5)
                continue

            data = resp.read()
            if len(data) < 1000:
                print(f"    Attempt {attempt}/{max_retries}: Received only {len(data)} bytes, retrying in 5s...")
                time.sleep(5)
                continue

            with open(CSV_PATH, "wb") as f:
                f.write(data)

            print(f"[✓] Downloaded {len(data):,} bytes")
            return True

        except Exception as e:
            print(f"    Attempt {attempt}/{max_retries}: Error - {e}")
            if attempt < max_retries:
                time.sleep(5)

    print(f"\n[!] Could not download automatically after {max_retries} attempts.")
    print(f"    Please download manually from:")
    print(f"    https://figshare.com/articles/dataset/Android_malware_dataset_for_machine_learning_2/5854653")
    print(f"    Save the CSV file as: {CSV_PATH}")
    return False


def validate_dataset():
    """Validate the downloaded dataset."""
    try:
        import pandas as pd
    except ImportError:
        print("[!] pandas not installed. Run: pip install pandas")
        return False

    if not os.path.exists(CSV_PATH):
        print(f"[✗] Dataset file not found: {CSV_PATH}")
        return False

    print(f"\n[*] Validating dataset...")

    df = pd.read_csv(CSV_PATH)
    n_rows, n_cols = df.shape
    class_col = df.columns[-1]
    class_dist = df[class_col].value_counts()

    print(f"    File: {CSV_PATH}")
    print(f"    Size: {os.path.getsize(CSV_PATH):,} bytes")
    print(f"    SHA-256: {hashlib.sha256(open(CSV_PATH, 'rb').read()).hexdigest()[:16]}...")
    print(f"\n    Rows: {n_rows:,}")
    print(f"    Columns: {n_cols}")
    print(f"    Class column: '{class_col}'")
    print(f"\n    Class distribution:")
    for label, count in class_dist.items():
        pct = count / n_rows * 100
        print(f"      {label}: {count:,} ({pct:.1f}%)")

    print(f"\n    Feature columns (first 10):")
    for col in df.columns[:10]:
        print(f"      - {col}")
    print(f"      ... and {n_cols - 11} more features")

    # Validation checks
    issues = []
    if n_rows < EXPECTED_MIN_ROWS:
        issues.append(f"Expected >= {EXPECTED_MIN_ROWS} rows, got {n_rows}")
    if n_cols != EXPECTED_COLS:
        issues.append(f"Expected {EXPECTED_COLS} columns, got {n_cols}")

    if issues:
        print(f"\n[!] Validation warnings:")
        for issue in issues:
            print(f"    - {issue}")
        print(f"    The dataset may still work, but column count differs from expected.")
    else:
        print(f"\n[✓] Dataset validation passed!")

    return True


if __name__ == "__main__":
    print("=" * 60)
    print("  DREBIN-215 Android Malware Dataset Downloader")
    print("  AegisML ThreatShield")
    print("=" * 60)
    print()

    success = download_dataset()
    if success:
        validate_dataset()
    else:
        sys.exit(1)
