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
# Sample → matrix mapping
# --------------------------------------------------

SAMPLES = {
    1: "GSM8245469_parental_attached_matrix.mtx.gz",
    2: "GSM8245469_paclitaxel_attached_matrix.mtx.gz",
    3: "GSM8245469_doxorubicin_attached_matrix.mtx.gz",
    4: "GSM8245470_parental_spheroid_matrix.mtx.gz",
    5: "GSM8245470_paclitaxel_spheroid_matrix.mtx.gz",
    6: "GSM8245470_doxorubicin_spheroid_matrix.mtx.gz",
}


# --------------------------------------------------
# Database
# --------------------------------------------------

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()


# --------------------------------------------------
# Load expression
# --------------------------------------------------

print("Loading expression matrices...")

total_records = 0

# Keep global cell offset
cell_offset = 0

with tarfile.open(TAR_FILE, "r") as tar:

    for sample_id, file_name in SAMPLES.items():

        print(f"\nProcessing sample {sample_id}: {file_name}")

        member = tar.getmember(file_name)
        compressed = tar.extractfile(member)

        if compressed is None:
            raise FileNotFoundError(file_name)

        with gzip.GzipFile(fileobj=compressed) as gz:

            reader = io.TextIOWrapper(gz, encoding="utf-8")

            # Skip header comments
            for line in reader:
                if not line.startswith("%"):
                    break

            # First non-comment line = dimensions
            n_genes, n_cells, n_entries = map(int, line.strip().split())

            print(f"Genes: {n_genes}, Cells: {n_cells}, Entries: {n_entries}")

            count = 0

            for line in reader:

                gene_idx, cell_idx, value = line.strip().split()

                gene_id = int(gene_idx)
                cell_id = int(cell_idx) + cell_offset
                expression_value = int(float(value))

                cursor.execute(
                    """
                    INSERT INTO expression (sample_id, cell_id, gene_id, expression_value)
                    VALUES (?, ?, ?, ?)
                    """,
                    (sample_id, cell_id, gene_id, expression_value)
                )

                count += 1
                total_records += 1

                if count % 100000 == 0:
                    print(f"  {count} records processed...")

        cell_offset += n_cells

print(f"\nTotal expression records: {total_records}")

conn.commit()
conn.close()

print("Expression loading complete.")
