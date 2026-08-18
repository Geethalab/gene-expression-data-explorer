import matplotlib

# Use a non-interactive backend for Flask
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PLOT_DIR = PROJECT_ROOT / "app" / "static"

PLOT_DIR.mkdir(parents=True, exist_ok=True)


def create_gene_plot(gene_name, gene_samples):

    labels = []
    means = []

    for row in gene_samples:
        population = row[1]
        treatment = row[2]
        culture = row[3]
        mean_expression = row[5]

        labels.append(
            f"{population}\n{treatment}\n{culture}"
        )

        means.append(mean_expression)

    plt.figure(figsize=(10, 5))

    plt.bar(labels, means)

    plt.xlabel("Sample")
    plt.ylabel("Mean Expression")
    plt.title(
        f"{gene_name} Expression Across Samples"
    )

    plt.xticks(rotation=0)

    plt.tight_layout()

    plot_file = f"{gene_name}_plot.png"
    plot_path = PLOT_DIR / plot_file

    plt.savefig(plot_path, dpi=150)
    plt.close()

    print(f"Plot created: {plot_path}")

    return plot_file
