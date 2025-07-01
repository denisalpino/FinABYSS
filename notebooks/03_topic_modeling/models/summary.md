Overview
---
All details of HPO process is availible in the correspondant PostgreSQL **DB used for experiment management with Optuna**. DB contains all trials for:
- Metrics:
  - Silohuette coefficient - not chosen because of assumption about spherical clusters;
  - DBCV Index - chosen because of its direct connection with the HDBSCAN clustering method used and the absence of assumptions about the shape of clusters;
  - Weighted DBCV Index - used for optimization with pruners.
- HPO algos:
  - TPE sampler (chosen for GLOBAL optimization);
  - CMA-ES sampler (chosen for LOCAL optimization);
  - NormalPruner;
  - AdaptiveStablePercentilePruner;
  - CustomPatientPruner.
- Distance metrics:
  - cosine for UMAP & euclidean for HDBSCAN;
  - $L_2$-Euclidean for both models.
- Embedding models:
  - $ModernBERT_{BASE}$ - SOTA basic embedding model with 8192 tokens context window;
  - $GTE-ModernBERT_{BASE}$ - previous model fine-tuned on MTEB-based tasks for the accurate working with a large texts.

Finally, we made decision to not use resource-based approach with a custom pruners in order to save time, since setting optimal percentiles and steps is time-consuming, which is very limited within the framework of the study.

Main experiments summary
---
|№| 1            | 2 | 3 |
|-|--------------|-----------------|--------------------------|
|**Definition**|Exploratory first version of topic model **trained on 10,000 mean pooled embeddings** of the **minimally preprocessed articles**. Available as the `BERTopic` model, containing results of HPO (random_state=42) in CSV. |Topic model **trained on 126,000 mean pooled embeddings** of the **fully preprocessed articles**. Available as the `BERTopic`, `UMAP`, `HDBSCAN` models with **states of samplers** and **2 checkpoints (global and local)** for each basic model, trials info locating in the DB.|Topic model **trained on 126,000 mean pooled embeddings** of the **fully preprocessed articles**. Available as the `BERTopic`, `UMAP`, `HDBSCAN` models without samplers' states and with only **last checkpoint** because of Linux (WSL 2) kernel crush, but all trials info still locating in the DB.|
|**Embedding Model**|$ModernBERT_{BASE}$|$GTE\text{-}ModernBERT_{BASE}$|$GTE\text{-}ModernBERT_{BASE}$|
|**DimRed Model**|`UMAP` (CPU) with cosine distance|`UMAP` (GPU) with $L_2$-Euclidean distance|`UMAP` (GPU) with cosine distance|
|**Clustering Model**|`HDSCAN` (CPU) with cosine distance|`HDSCAN` (GPU) with $L_2$-Euclidean distance|`HDSCAN` (GPU) with euclidean distance|
|**2D Mapper**|`PaCMAP` with angular distance|`UMAP` (GPU) with $L_2$-Euclidean distance|`UMAP` (GPU) with cosine distance + PaCMAP with angular distance|
|**Representator**|`YandexGPT Lite`|`MMR` + `GPT4o-mini` + human corrections|`MMR` + `GPT4o-mini`|
|**Metric**|Silohuette = 0.712 \| DBCV = 0.011|DBCV = 0.397|**DBCV = 0.407**|
|**Findings**|1. Deep cleaning of texts is necessary, as legal and marketing information makes so much **noise** that they form a separate cluster.<br>2. The silhouette coefficient should be changed to a **density metric**.<br>3. **Insufficient training data**.<br>4. CPU-versions of algos are **too slow** for larger data.<br>5. On a 2D semantic map, we'd like to see **more localized relationships** of topics.<br>6. `YandexGPT` gives **overly general**, and quite often completely **incorrect labels** to clusters.|1. The GPU version of `UMAP` is **extremely unstable**, which leads to a huge number of outliers and, as a result, makes clustering difficult, which leads to a high percentage of the resulting noise. This is addressed in Issues [#6454](https://github.com/rapidsai/cuml/issues/6454) and [#6539](https://github.com/rapidsai/cuml/issues/6539) (PRs [#6662](https://github.com/rapidsai/cuml/pull/6662) and [#6592](https://github.com/rapidsai/cuml/pull/6595), respectively).<br>3. The problem with spectral initialization and random state makes the implementation of `UMAP` **unreproducible** and generates **additional outliers** ([#6750](https://github.com/rapidsai/cuml/pull/6750))<br>4. It turned out to achieve a **more local structure**, but it has **difficulty displaying real semantic connections**.<br>5. `GPT4o-mini` labeled topics **much better** than `YandexGPT Lite` and even `GPT4o`.<br>6. Using MMR to select key terms is not always enough, and this is especially noticeable for semi-automated sources (Zacks, Simply Wall St., etc) whose **texts are too formulaic**, so we should manually adjust the names of highly specialized topics.|1. Using the Euclidean distance metric, we got **twice as many topics** (139 clusters), and due to their **fine-grainedness**, they are much **more unambiguous**.<br>2. For `HDBSCAN`, the `min_samples` and `min_cluster_size` values decreased by about 2.5 times, which should have led to less noise relative to `HDBSCAN` with the Euclidean metric, but the **noise increased** from 39.5% to 43.4%.<br>3. `UMAP` (for dimensionallity reduction) **hyperparameters converged** to the optimum for the $L_2$-Euclidean distance metric, which was expected.<br>4. The found 2D `UMAP` mapping model **perfectly describes local relationships**, however, **clusters can often overlap** greatly due to the excellent representation of intracluster variance. 5. The additional `PaCMAP`-based model **perfectly conveys the global structure** at the megacluster level, which has an extremely positive effect on visualizing the hierarchical cluster structure, but for this reason, **too dense clusters** and **large voids** are formed.|
