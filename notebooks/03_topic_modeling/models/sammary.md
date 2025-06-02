All details of HPO process is availible in the correspondant PostgreSQL DB used for experimentation management with Optuna.

Experiments summary:
* v1 — demo version of BERTopic model trained on 10,000 articles' embeeddings:
  * Raw only pretrained $ModernBERT_{BASE}$
  * UMAP cosine (CPU)
  * HDBSCAN euclidean (CPU)
* v2 — version of UMAP + HDBSCAN + BERTopic models trained on 125,000 articles' embeeddings (with samplers' states and 2 checkpoints):
  * $ModernBERT_{BASE}$ fine-tuned on STS task
  * UMAP l2-euclidean (GPU)
  * HDBSCAN l2-euclidean (GPU)
* v3 — also version of UMAP + HDBSCAN + BERTopic models trained on 125,000 articles' embeeddings (but without samplers' states and with only one final local checkpoint):
  * $ModernBERT_{BASE}$ fine-tuned on STS task
  * UMAP cosine (GPU)
  * HDBSCAN euclidean (GPU)