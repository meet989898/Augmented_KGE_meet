# Knowledge Graph Qrels Generator & IR Evaluation Framework

This repository contains the complete pipeline for generating qrels and evaluating knowledge graph embeddings using IR metrics. The system supports multiple corruption strategies, compatibility-based filtering, and full IR analysis using `ir_measures`.

---

## 📌 Project Scope

- Generation of `qrels` using various corruption strategies (LCWA, sensical, nonsensical, 1-hop)
- Relevance resolution via multiple policies (min, max, avg_floor, avg_ceil)
- Evaluation using [`ir_measures`](https://ir-measur.es)
- Structured JSON outputs for reproducibility
- Metadata cube structure for relevance aggregation
- Handles different scales

---

## 🏗️ Project Structure

- `main.py` — Entry point for the full pipeline
- `DataLoader.py` — Loads and parses triples from dataset splits
- `TripleManager.py` — Manages triples and generates compatible relations
- `GenerateQrels.py` — Builds qrels for each corruption strategy
- `IrMeasure.py` — Computes IR metrics using the ir_measures library
- `PathUtils.py` — All filepath logic is abstracted here

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

- **Standard IR**: `AP`, `RR`, `Bpref`, `MAP`, etc
- **Cutoff Metrics**: `P@k`, `nDCG@k`, `Recall@k`, `Success@k`  , etc
- **k values**: `1, 5, 10, 25, 50, 100, 250, 500`

Rel threshold (`rel=1`) is passed explicitly to all supported metrics.

---

## 🚀 How to Use

Everything runs from `main.py`.  
Once filepaths are properly configured, run:

```bash
python main.py
```

The system will:
1. Load reshuffled and original datasets
2. Generate qrels using multiple strategies (Max, Min, Avg_Floor, Avg_Ceil)
3. Evaluate multiple model run files using IR metrics
4. Output results to JSON and TSV, with flags to control if they need to be printed to a file

---

## ⚙️ Configuration

All global parameters are set at the top of `main.py`:
- `main_folder`: base directory for everything, even the main file is in this
- `thresholds_to_run`: list of thresholds (e.g., `[0.75]`)
- `methods_to_run`: similarity methods (e.g., `["overlap"]`)
- `models`: list of model names to evaluate (empty = all)
- all the other folder paths that can be seen in the global parameters in main.py need to be edited
- Run scored for a partical dataset need to be stored inside a folder with its name being the dataset number, according to the datasetutils.py file, for eg: Nell in number 3 (this logic can be changed at line 68 in main.py)

Other flags:
- `WRITE_QREL_TO_FILE`: if True, write qrels to TSV
- `WRITE_JSON_TO_FILE`: if True, save JSON IR logs

---

## 📤 Output

- All qrels are saved under: `Generated_Qrels_TSV/`
- IR metrics are saved under: `IR_Measures/`, only if the flags are true else default is false
- Console logs are tagged with `METADATA` and `RESULT` for parsing
- Example console logs
  
- Metadata: {"dataset":"NELL-995","test_file":"0_resplit_test2id.txt","reshuffle_id":"0","rel_threshold":1,"k_values":[1,5,10,15,20,25,30,40,50,60,70,80,90,100,150,200,250,300,350,400,450,500],"metrics":["AP","Bpref","AP","RR","RR","P@1","nDCG@1","R@1","Success@1","R@1","P@5","nDCG@5","R@5","Success@5","R@5","P@10","nDCG@10","R@10","Success@10","R@10","P@15","nDCG@15","R@15","Success@15","R@15","P@20","nDCG@20","R@20","Success@20","R@20","P@25","nDCG@25","R@25","Success@25","R@25","P@30","nDCG@30","R@30","Success@30","R@30","P@40","nDCG@40","R@40","Success@40","R@40","P@50","nDCG@50","R@50","Success@50","R@50","P@60","nDCG@60","R@60","Success@60","R@60","P@70","nDCG@70","R@70","Success@70","R@70","P@80","nDCG@80","R@80","Success@80","R@80","P@90","nDCG@90","R@90","Success@90","R@90","P@100","nDCG@100","R@100","Success@100","R@100","P@150","nDCG@150","R@150","Success@150","R@150","P@200","nDCG@200","R@200","Success@200","R@200","P@250","nDCG@250","R@250","Success@250","R@250","P@300","nDCG@300","R@300","Success@300","R@300","P@350","nDCG@350","R@350","Success@350","R@350","P@400","nDCG@400","R@400","Success@400","R@400","P@450","nDCG@450","R@450","Success@450","R@450","P@500","nDCG@500","R@500","Success@500","R@500"],"relevance":{"LCWA":0,"nonsensical":1,"one-hop nonsensical":2,"one-hop sensical":3,"sensical":4,"positive":5},"hyperparameters":{"compatible_threshold":0.75,"similarity_method":"overlap","alpha":0.5,"beta":0.5}}

- Results_Max_boxe_resplit__0_bottom.tsv: {"filename":"boxe_resplit__0_bottom.tsv","model":"boxe","resplit":"0","partition":"bottom","policy":"Max","metrics":{"nDCG@30":0.0119,"R@90":0.0003,"R@5":0.0001,"Success@40":0.2665,"P@70":0.0058,"R@25":0.0003,"P@500":0.0008,"P@25":0.0161,"R@1":0.0001,"Success@25":0.2663,"R@40":0.0003,"P@15":0.025,"P@30":0.0135,"P@60":0.0067,"nDCG@20":0.0153,"AP":0.0001,"R@350":0.0003,"P@20":0.0199,"P@250":0.0016,"Success@20":0.2663,"Success@300":0.2665,"nDCG@450":0.0018,"nDCG@5":0.0257,"R@400":0.0003,"nDCG@10":0.0215,"nDCG@25":0.0133,"R@500":0.0003,"nDCG@80":0.0062,"nDCG@15":0.0176,"Success@80":0.2665,"R@70":0.0003,"nDCG@250":0.0027,"Success@400":0.2665,"R@100":0.0003,"P@350":0.0012,"Success@15":0.2657,"R@60":0.0003,"nDCG@1":0.0399,"R@50":0.0003,"Success@60":0.2665,"P@450":0.0009,"nDCG@300":0.0024,"P@80":0.0051,"nDCG@70":0.0068,"P@150":0.0027,"P@100":0.004,"Success@350":0.2665,"R@450":0.0003,"R@30":0.0003,"R@80":0.0003,"Success@1":0.0573,"R@300":0.0003,"RR":0.1027,"P@200":0.002,"nDCG@350":0.0022,"Success@5":0.1497,"nDCG@500":0.0017,"nDCG@200":0.0032,"P@10":0.0339,"R@15":0.0003,"P@400":0.001,"Success@500":0.2665,"P@90":0.0045,"P@50":0.0081,"R@150":0.0003,"R@250":0.0003,"nDCG@50":0.0085,"nDCG@40":0.0099,"Success@10":0.259,"P@300":0.0013,"Success@100":0.2665,"nDCG@150":0.004,"Success@30":0.2665,"P@1":0.0573,"R@10":0.0002,"Success@250":0.2665,"P@40":0.0101,"nDCG@60":0.0075,"Success@90":0.2665,"nDCG@100":0.0053,"R@200":0.0003,"Success@50":0.2665,"P@5":0.0361,"Success@150":0.2665,"R@20":0.0003,"Success@70":0.2665,"nDCG@90":0.0057,"nDCG@400":0.002,"Success@450":0.2665,"Bpref":0.0003,"Success@200":0.2665}}


---

## 📝 Notes

- No manual editing is needed inside any logic file.
- Everything is parameterized through the `main.py` globals.
- Clean logs are generated for later processing.

## 📄 License

MIT License

---

## 🔗 Citation & Acknowledgment

This work was developed at Rochester Institute of Technology under the guidance of Professor Carlos Rivero as part of NSF-funded research.

If used, please cite accordingly or reach out via the GitHub repository.
