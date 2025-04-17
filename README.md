# Knowledge Graph Qrels Generator & IR Evaluation Framework

This repository contains a complete research pipeline for evaluating knowledge graph embedding models using IR-based relevance metrics.

---

## 📌 Project Scope

- Generation of `qrels` using various corruption strategies (LCWA, sensical, nonsensical, 1-hop)
- Relevance resolution via multiple policies (min, max, avg_floor, avg_ceil)
- Evaluation using [`ir_measures`](https://ir-measur.es)
- Structured JSON outputs for reproducibility
- Metadata cube structure for relevance aggregation
- Handles different scales

---

[//]: # (## 📂 Repository Structure)

[//]: # ()
[//]: # (| Folder/File       | Description |)

[//]: # (|-------------------|-------------|)

[//]: # (| `src/`            | All core logic and data processing modules |)

[//]: # (| `data/`           |  |)

[//]: # (| `output/`         |  |)

[//]: # (| `configs/`        | Optional YAML/JSON configurations for future use |)

[//]: # (| `main.py`         | Entry point |)

[//]: # (| `requirements.txt`| Python dependencies |)

[//]: # ()
[//]: # (---)

## 🧠 Features

- TripleManager with compatible relation handling
- In-memory qrel computation (no writing until fully computed)
- Vectorized NumPy operations for speed and scale
- Conflict resolution across multiple strategies
- 3D relevance cube structure: `[strategy][triple][curroption]`
- JSON output format including:
  - evaluation results
  - relevance mapping
  - hyperparameters used

---

## ⚙️ Example Hyperparameters

- `compatible_threshold`: 0.75
- `similarity_method`: overlap / dice / tversky
- `alpha`, `beta`: Tversky params
- `positive_score`: 5 ...etc

---

## 📊 Metrics Evaluated

- **Standard IR**: `AP`, `RR`, `Bpref`, `MAP`
- **Cutoff Metrics**: `P@k`, `nDCG@k`, `Recall@k`, `Success@k`  
- **k values**: `1, 5, 10, 25, 50, 100, 250, 500`

Rel threshold (`rel=1`) is passed explicitly to all supported metrics.

---

## 🚀 Running the Pipeline

1. Install dependencies
```bash
pip install -r requirements.txt
```

2. Run the main evaluation pipeline
```bash
python main.py
```

---

## 📄 License

MIT License

---

## 🔗 Citation & Acknowledgment

This work was developed at Rochester Institute of Technology under the guidance of Professor Carlos Rivero as part of NSF-funded research.

If used, please cite accordingly or reach out via the GitHub repository.
