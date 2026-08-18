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
DATABASE = PROJECT_ROOT / "database" / "gene_expression_v2.db"

FEATURE_FILE = (
    "GSM8245469_doxorubicin_attached_features.tsv.gz"
)


# --------------------------------------------------
# Open database
# --------------------------------------------------

connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()


# --------------------------------------------------
# Read features.tsv.gz directly from TAR archive
# --------------------------------------------------

print("Reading gene features...")

with tarfile.open(TAR_FILE, "r") as tar:

    member = tar.getmember(FEATURE_FILE)

    compressed_file = tar.extractfile(member)

    if compressed_file is None:
        raise FileNotFoundError(
            f"Could not extract {FEATURE_FILE}"
        )

    with gzip.GzipFile(fileobj=compressed_file) as gz:

        for line in io.TextIOWrapper(gz, encoding="utf-8"):

            line = line.strip()

            if not line:
                continue

            fields = line.split("\t")

            gene_id = fields[0]
            gene_symbol = fields[1]
            feature_type = fields[2] if len(fields) > 2 else None

            cursor.execute(
                """
                INSERT INTO genes (
                    gene_symbol,
                    feature_type
                )
                VALUES (?, ?)
                """,
                (
                    gene_symbol,
                    feature_type
                )
            )


# --------------------------------------------------
# Save changes
# --------------------------------------------------

connection.commit()


# --------------------------------------------------
# Report results
# --------------------------------------------------

cursor.execute("SELECT COUNT(*) FROM genes")

gene_count = cursor.fetchone()[0]

print(f"Genes loaded successfully: {gene_count}")


# --------------------------------------------------
# Close database
# --------------------------------------------------

connection.close()

print("Database updated successfully.")
