import sqlite3
import tarfile
import gzip
import io
from pathlib import Path


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

TAR_FILE = PROJECT_ROOT / "data" / "GSE266356_RAW.tar"
DATABASE = PROJECT_ROOT / "database" / "gene_expression.db"

BARCODE_FILE = (
    "GSM8245469_doxorubicin_attached_barcodes.tsv.gz"
)

# Doxorubicin + Attached sample
SAMPLE_ID = 2


# --------------------------------------------------
# Open database
# --------------------------------------------------

connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()


print("Loading cell barcodes...")


# --------------------------------------------------
# Read barcode file directly from TAR
# --------------------------------------------------

cells = []

with tarfile.open(TAR_FILE, "r") as tar:

    member = tar.getmember(BARCODE_FILE)

    compressed_file = tar.extractfile(member)

    if compressed_file is None:
        raise FileNotFoundError(
            f"Could not find {BARCODE_FILE}"
        )

    with gzip.GzipFile(fileobj=compressed_file) as gz:

        for line in io.TextIOWrapper(gz, encoding="utf-8"):

            barcode = line.strip()

            if barcode:
                cells.append(
                    (barcode, SAMPLE_ID)
                )


# --------------------------------------------------
# Insert cells efficiently
# --------------------------------------------------

cursor.executemany(
    """
    INSERT INTO cells (
        barcode,
        sample_id
    )
    VALUES (?, ?)
    """,
    cells
)


# --------------------------------------------------
# Save changes
# --------------------------------------------------

connection.commit()


# --------------------------------------------------
# Report
# --------------------------------------------------

cursor.execute(
    "SELECT COUNT(*) FROM cells WHERE sample_id = ?",
    (SAMPLE_ID,)
)

cell_count = cursor.fetchone()[0]

print(f"Cells loaded successfully: {cell_count}")


# --------------------------------------------------
# Close database
# --------------------------------------------------

connection.close()

print("Database updated successfully.")
