import sqlite3
import tarfile
import gzip
import io
from pathlib import Path


# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

TAR_FILE = PROJECT_ROOT / "data" / "GSE266356_RAW.tar"
DATABASE = PROJECT_ROOT / "database" / "gene_expression_v2.db"


# --------------------------------------------------
# Sample → file mapping
# --------------------------------------------------

SAMPLES = {
    1: "GSM8245469_parental_attached_barcodes.tsv.gz",
    2: "GSM8245469_paclitaxel_attached_barcodes.tsv.gz",
    3: "GSM8245469_doxorubicin_attached_barcodes.tsv.gz",
    4: "GSM8245470_parental_spheroid_barcodes.tsv.gz",
    5: "GSM8245470_paclitaxel_spheroid_barcodes.tsv.gz",
    6: "GSM8245470_doxorubicin_spheroid_barcodes.tsv.gz",
}


# --------------------------------------------------
# Database
# --------------------------------------------------

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()


# --------------------------------------------------
# Load cells
# --------------------------------------------------

print("Loading cells for all samples...")

total_cells = 0

with tarfile.open(TAR_FILE, "r") as tar:

    for sample_id, file_name in SAMPLES.items():

        print(f"Processing sample {sample_id}: {file_name}")

        member = tar.getmember(file_name)
        compressed = tar.extractfile(member)

        if compressed is None:
            raise FileNotFoundError(file_name)

        with gzip.GzipFile(fileobj=compressed) as gz:

            for line in io.TextIOWrapper(gz, encoding="utf-8"):

                barcode = line.strip()

                if not barcode:
                    continue

                cursor.execute(
                    """
                    INSERT INTO cells (barcode, sample_id)
                    VALUES (?, ?)
                    """,
                    (barcode, sample_id)
                )

                total_cells += 1

print(f"Total cells loaded: {total_cells}")

conn.commit()
conn.close()

print("Cells loaded successfully.")
