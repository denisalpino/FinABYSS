![logo](docs/finabyss_dark.svg)

FinABYSS (Financial Aspect-Based Hybrid Semantic System)
--

- [FinABYSS (Financial Aspect-Based Hybrid Semantic System)](#finabyss-financial-aspect-based-hybrid-semantic-system)
- [🌏 Semantic Map](#-semantic-map)
  - [💻 Installation](#-installation)
  - [🛠 How to Use](#-how-to-use)
- [⚙️ Architecture](#️-architecture)
- [⭐️ Key Features](#️-key-features)
  - [🌀 Local \& Global Structure](#-local--global-structure)
  - [📚 Long Context](#-long-context)
  - [🚀 Speed up](#-speed-up)
- [✍️ Notes](#️-notes)
  - [❗️ Key Dependencies](#️-key-dependencies)
  - [🌳 Project Structure](#-project-structure)
  - [🚧 Future Works](#-future-works)
  - [📝 Corpus](#-corpus)
  - [📞 Contacts](#-contacts)


This project aims to review the existing approach to financial forecasting and analysis, taking a step towards the analysis of multimodal data. We offer 2 key concepts:
1. Aspect-based sentiment analysis (ABSA), in the context of which aspects are considered as topics;
2. Considering financial sentiment as the strength and direction of information's influence on the price of a particular asset, rather than as an emotional coloring.

These assumptions have 3 key implications:
1. each document is represented by a set of topics from a predefined set without human involvement;
2. each publication has $k$ sentiments corresponding to each topic;
3. sentiments of one publication will vary depending on the asset.

The study details and **partially develops an architecture** that implements the described approach. The developed alpha version of the system is called FinABYSS (Financial Aspect-Based hybrid Semantic System) and is based on the Embedding Model, MoE, Feature Synchronization Mechanism (FSM), CNN-LSTM with slow fusion mechanism and analytical GUI.

## 🌏 Semantic Map

### 💻 Installation
1. Just download [HTML file](semantic_map.html), right-click and open it in Microsoft Edge or Google Chrome (both gives the fastest response).
2. First, open the web-page and wait for it to fully load. You can determine whether the system is fully booted or not by the **pop-up windows when you hover over the dots**. If they pop up, the system is ready to function.
3. When the loading is complete, press the SHIFT key once. This is to speed up zooming in/out of the camera.

### 🛠 How to Use
* The map shows the **Dots**, each one a financial news article:
  * the **size** of the dot reflects the number of characters in the article;
  * the **color** of the dot corresponds to the main topic of the article.
  * when you hover over a dot, a **pop-up window** appears, containing the title of the news article, the tickers to which the article belongs, the original source of the article, as well as the time and date of publication;
  * **clicking** on the dot redirects to the original web-page of the article.
* A **Search Bar** is available in the upper right corner below the logo, implementing search functionality. The search is performed on all texts of articles.
* A **Histogram** is available in the lower right corner, which realizes the possibility of filtering news by time range. Each bar is a month. When you hover over a bar, all articles for the month are highlighted. To select the time range, you should click on the desired initial bar and drag the mouse to the expected end of the period.
* Along the left side is the **Filter Menu**. Cross-interaction of filters by three categories is allowed: Source, Topic, and Ticker. User can check the boxes of sources, topics and tickers that the user wants to find:
  * Since there are quite a few items in each category, a **Search Box** is available in each category.
  * After selecting items, the corresponding names are placed under the Search Box, from where they **can later be removed** by clicking on the cross.
* Semantic Map also offers functionality to build a **Word Cloud** for any group of articles. The word cloud is constructed from the texts of the highlighted articles. The user can select an arbitrary group of articles by pressing the SHIFT key and starting to circle the area of interest. After selecting the objects, the Word Cloud will appear on the left side of the Map. Once the Word Cloud is built, the user can immediately select another group. **To delete a Word Cloud, you must reset all filters and press the SHIFT key once**.

![overview](docs/overview.gif)

## ⚙️ Architecture
This system is not at all limited to the Semantic Map, which in fact was developed as a simple visual method for interpreting the financial semantic space and represents an interface to a more closed process — predicting the value of financial assets using thematic tone scores.

1. The first block includes a domain-adapted financial embedding system. The adaptation is done by pre-training on domain-specific financial texts with a `BERT`-like model with long context. Then, the model is fine-tuned to the Semantic Textual Similarity (STS) task to extract denser vector representations. The text is passed through this block and the output extracts token embeddings from the last layer, which are then averaged to obtain a vector representation of the text, as a whole.

![architecture](docs/architecture.png)

2. The `MoTE` block consists of a **pre-trained router** and **backpropagation trained topic experts**. The router is designed based on classical models.
    - The goal of `UMAP` is to reduce the sparse embeddings by reflecting onto an intermediate latent space of lower dimensionality, striking a balance between preserving local and global structure. `ParametricUMAP`, `AlignedUMAP`, `PaCMAP` and other `MAP` family models can be considered instead of `UMAP`.
    - The task of `HDBSCAN` is to find a **granular but time generalizable topic hierarchical cluster structure** based on compacted semantic vectors without a teacher. `HDBSCAN` is indispensable because based on densities, this algorithm doesn't have the assumption of sphericity of clusters, and also allows to obtain a **soft probability distribution** of vector membership across clusters.
    - Next, a gating mechanism is used to select Top-$k$ topic experts, which are shallow `MLP` regressors trained for the SA task, based on the underlying embedding model. Each expert produces a sentiment score from -1 to 1.
    - Given the specifics of the task, it is worth noting that a particular news item has different intensity and direction of influence on different tickers. To obtain ticker-like tones, it is suggested to use the `FiLM` (Feature-wise Linear Modulation) method by adding one more input to each expert (ticker embedding), followed by its `MLP` with two outputs — shift and scale — which then transforms the tone at the output. As a more budget-friendly alternative, a global adapter training approach is possible.
    - At the output of the block, the tones are weighted and sent to the analysis interface.
3. Also, the tones received from each Expert Advisor are separately processed in `FSM` (Feature Synchronizing Mechanism), which is designed to synchronize irregular data from the media space with tick-based OHLCV and indicators. The cache of this block stores thematic tones, which are initialized with zeros, then the cache is incrementally filled and stores cumulative thematic tones. During the filling process, an exponential decay formula is applied with respect to the previous state in the cache, which takes into account the fading influence of news.
4. Together with OHLCVs and indicators, tones are fed into the predictive model. Each of the data types is treated as a separate modality (however, indicators and OHLCVs can be combined into one by converting cost data into returns).
    - Each modality has its own branch consisting of `CNNs` and `LSTMs`. After passing the branches, the modalities are concatenated, realizing a slow merge, and then processed together.
    - Also, the predictive model provides a surrogate model that implements LIME interpretation and is trained based on small undulations in the input features.
5. Figure above shows that the analytical GUI receives information from different blocks. It's designed for convenient and efficient analytics of the financial media space and its impact on the value of various assets. The block is divided into 3 components:
    - The **Core Preprocessor** is responsible for lexical and semantic text processing followed by topic generation, including normalized c-TF-IDF with BM25 and MMR.
    - The **Semantic Map** component is responsible for projecting embeddings from the intermediate latent space onto the 2D plane, via a `MAP` family model, and assigning hierarchical labels via a linkage function with Ward's variance minimization method and cosine distance metric. After that, the two-dimensional reflection with the assigned thematic hierarchy is displayed on an interactive semantic map.
    - The unit also provides access to a variety of supporting tools for financial analysis, including monitoring of topic dynamics over time, multi-asset value forecasts, topic deep learning tools, and LIME charts.

This architecture requires sufficient computational resources, so for now the current system is based just on the embedding system, router and GUI. As the project develops, the `FSM` will be developed and the Predictive Model and Experts will be trained. Only those parts of the architecture that are currently implemented are left in the figure below.

![architecture_current_state](docs/architecture_current_state.png)

## ⭐️ Key Features
### 🌀 Local & Global Structure
This map preserves the semantic relationship of both the clusters and the texts themselves to each other quite well. In the problem of dimensionality reduction, the **local structure refers to the dots and determines how accurately they are located relative to the nearest dots**. This absolutely true for our Semantic Map. Let's take a look at an example related to an Electric Vehicles cluster on a Semantic Map. After we have selected this cluster, we can see that it is somewhat fragmented, that is, it consists of several microclusters scattered over different parts of the map.

![local_structure](docs/local_structure.gif)

The subcluster in the lower right corner contains articles more about the safety of autonomous transport. If we look at the cluster on the upper right side of the map, we can find that it's more about Europe vehicles industry. The same can be observed for the Cultural Tourism cluster, but in a more restrained form. Thus, mainland and island China can be observed in the upper part of the cluster, the Middle East from the bottom left, and South Asia on the bend.

Little differance lays in global structure that always determines as a represented variance of data. In our case, the **global structure mostly means the ability to continuously reflect a hierarchical structure**, that is, meso- and macro-clusters. It can be observed that such topical clusters as Hospitality Industry, Restaurant Industry, Alcohol Industry, Cannabis Industry, Cultural Tourism are quite close to each other, in fact forming the extended HoReCa industry.

![global_structure](docs/global_structure.gif)

The same can be observed with the clusters of National Security, Cryptocurrency Regulation and Cybersecurity.

So, on the Semantic Map, one can find some rather entertaining connections. For example, there is an area where the Electric Vehicle cluster is adjacent to the Mining Exploration, which we have been considering recently. If the word "lithium" is quite obvious, "gold" may surprise an unloaded user, however, the fact is that many times more gold is used for the production of electric cars than for cars with internal combustion engines. That is, the Semantic Map allows users who are not immersed in the specifics to discover rather deep inter-topic patterns.

![golden_finding](docs/golden_finding.png)

This is absolutely amazing, because even the marginally immersed person can now extremely quickly test hypotheses and explore areas and connections of interest at an accelerated pace.

Another version of the Semantic Map is also available (PaCMAP-based), which, unlike the current one, prioritizes the global structure, but makes it difficult to trace local relationships.

### 📚 Long Context

Previously, the `BERT` model or its improved versions were most commonly used for embedding tasks, but all were limited to contexts of 512 tokens, which did not allow processing long texts. Sliding contex window type methods are costly and lose long term contextual relationships.

This project focuses on "budget" LMs designed to extract embeddings from long texts. The current solution is based on [`gte-modernbert-base`](https://huggingface.co/Alibaba-NLP/gte-modernbert-base), which can handle up to 8192 tokens. However, this is still not enough, so in the near future it is planned to switch to the newly released [`Qwen3-Embedding-4B`](https://huggingface.co/Qwen/Qwen3-Embedding-4B), which is capable of processing up to 32k tokens.

Thus, the current solution allows us to reach a **new level** — to process not only short posts in social networks and news headlines, but also press releases, news, transcripts of financial events and much more.

### 🚀 Speed up

1. Comparing our own implementation of the embedding extraction pipeline with presented in [`SBERT`](https://sbert.net/), **our version is 9 times faster**. The key differences are the use of mixed precision (fp16), automation of CPU and GPU load balancing, inference mode activation, removal of unnecessary converting operations, and periodic manual cache flushing.
2. Moreover, referring to the `UMAP` and `HDBSCAN` models used, their **training was accelerated by about 80 times** by switching to GPU versions from `cuML`.
3. The acceleration also applies to the manual labor required for classic topic markup. We **reduced the time of experts to assign labels to generated clusters 3 times** using MMR and GPT4o-mini for this purpose. **The most time-consuming step of manual document labeling as a classification task was eliminated altogether**.

## ✍️ Notes

### ❗️ Key Dependencies

To reproduce the experiments, you need to create `Python 3.10` environment in which all the dependencies from `requirements.txt`, as well as `CUDA 12.1` and `cuML 25.06.00` for UMAP and HDBSCAN training. Core dependencies include:
- [`BERTopic`](https://github.com/MaartenGr/BERTopic) — a convenient API for vizualizing generated topics, working with topic texts, and hierarchical structure;
- [`PyTorch`](https://github.com/pytorch/pytorch) — to speed up the process of embedding extraction and mean pooling;
- [`Transformers`](https://github.com/huggingface/transformers) & [`SBERT`](https://sbert.net/) — to speed up the process of embedding extraction and mean pooling;
- [`alpha_vantage`](https://github.com/RomelTorres/alpha_vantage) — API for collecting minute-long OHLCV data;
- [`Polars`](https://docs.pola.rs/) — for lazy data preprocessing.


### 🌳 Project Structure
<details>
<summary>
FinABYSS
</summary>

```bash
├── data/
│   ├── preprocessed/
│   │   ├── articles.parquet    # Fully preprocessed articles by texts and its metadata
│   │   ├── embeddings_mp.npy   # Mean pooled embeddings for each article in the corpus
│   ├── raw/
│   │   ├── articles.parquet    # Parsed news articles with their metadata
│   │   ├── news_urls.parquet   # Scrapped urls leading to rhe news pages on Yahoo! Finance
│   │   └── ohlcv.parquet
│   └── sample/                 # Training sample of 126.000 articles + their embeddings
│       ├── articles.parquet
│       ├── embeddings.npy
│       └── embeddings_l2.npy
├── docs/                       # Images and gifs for README
├── notebooks/
│   ├── 01_data_collecting/     # Data collecting pipelines
│   │   ├── ohlcv.ipynb
│   │   └── yahoo_articles.ipynb
│   ├── 02_data_preprocessing/  # Data prep, viz, feature extraction and sampling pipelines
│   │   ├── img/
│   │   ├── 01_articles_preprocessing.ipynb
│   │   ├── 02_articles_vizualization.ipynb
│   │   ├── 03_feature_extraction.ipynb
│   │   └── 04_data_sampling.ipynb
│   ├── 03_topic_modeling/
│   │   ├── img/                # Images from model analysis and topic viz (L2-based model)
│   │   ├── models/
│   │   │   ├── v1/             # Exploratory first version of topic model
│   │   │   ├── v2/             # Topic model based on L2-Euclidean dist metric
│   │   │   ├── v3/             # Topic model based on Cosine & Euclidean dist metrics
│   │   │   └── summary.md
│   │   ├── 01_hpo.ipynb
│   │   ├── 02_topic_modeing.ipynb
│   │   ├── 03_model_analysis.ipynb
│   │   └── 04_topic_vizualization.ipynb
│   └── 04_semantic_map_dev/
│       ├── data/                # Embeddings from the intermediate space and 2D + labels
│       ├── semantic_map.ipynb   # HTML/CSS/JS + Python wrapper for Semantic Map
│       └── semantic_map_l2.html # Semantic Map based on L2-Euclidean dist metric
├── paper/
│   ├── eng/    # English thesis with bibliography and LaTeX
│   └── ru/     # Russian version of thesis (badly adapted)
├── parsers/    # Still class for parsing URLs and news from only Yahoo! Finance
├── utils/
│   ├── api_key_manager.py     # API-key rotator class
│   ├── custom_tqdm.py         # TQDM-wrapper for monitoring parsing process
│   ├── metrics.py             # Metrics for HPO (finally unused)
│   ├── proxy_manager.py       # Proxy-rotator for parsing articles
│   ├── pruner.py              # 3 pruners for HPO with Optuna
│   └── vizualization.py       # Functions for viz parallel coordinates & feature importance
├── README.md
├── requirements.txt
└── semantic_map.html # Main Semantic Map based on Cosine + Euclidean dist metric
```
</details>

### 🚧 Future Works
| Task                                                                           | Complexity | Priority | Current Status | Finished  |
|--------------------------------------------------------------------------------|------------|----------|----------------|-----------|
| ~~Additional Corpus Cleaning~~                                                     | Easy       | High     | done           | &#x2611; Formalize rules
| ~~Improve c-TF-IDF implementation~~                                                | Easy       | High     | done           | &#x2611; Configure MinimalMarginalRate from KeyBERT
| ~~Improve Representation of Topics~~                                               | Normal     | High     | done           | &#x2611; Plug in the GPT-4o<br>&#x2611; Figure out how to account for the hierarchical structure
| ~~Develop Hierarchical Structure Processing Logic Inspiring by BERTopic~~          | Normal     | Medium   | in progress    | &#x2611; Explore the BERTopic source code<br>&#x2611; Develop logic for assigning topic names to each level in the hierarchy
| Full-body Training (all corpus)                                                             | Normal     | High     | done           | &#x2610; Find and rent infrastructure with GPUs<br>&#x2610; Customize the environment<br>&#x2610; Adapt training code
| ModernBERT Domain Adaptive Pre-Training                                        | Hard       | High     | planning       | &#x2610; (optional) Expand the corpus<br>&#x2610; Find and rent infrastructure with GPUs<br>&#x2610; Write training code
| Evaluate and compare ModernBERT (DAPT) & FinBERT on GLUE & FLUE benchmarks     | Hard       | High     | planning       | &#x2610; Find and gather all datasets from benchmarks<br>&#x2610; Write code to fine-tune for each of the tasks
| ~~Refine the Semantic Map~~                                                        | Normal     | Medium   | done       | &#x2611; Rework hover labels<br>&#x2611; Write custom code to build a word cloud using the native TF-IDF<br>&#x2611; Implement filtering by source<br>&#x2611; Improve the visual design<br>&#x2611; Develop more diverse infographics
| Refine the Text Search in the Semantic Map                                     | Normal     | Low      | planning       | &#x2610; Create the vector DB (FAISS) for texts<br>&#x2611; Remove the texts from hover labels and migrate them into the database<br>&#x2610; Connect search system in the semantic map wit database
| Fine-tuning ModernBERT (DAPT) for Dense Embeddings                                    | Hard       | High     | planning       | &#x2610; ...
| Experimentation with Leiden Сlustering on kNN Graphs                           | Normal     | Low      | backlog        | &#x2610; ...
| Companys' Semantic Graph                                                       | Hard       | Low      | backlog        | &#x2610; ...
| Graph-based News Representation                                                | Hard       | Low      | backlog        | &#x2610; ...

### 📝 Corpus
The corpus with all articles is located at private [repository](https://huggingface.co/datasets/denisalpino/YahooFinanceNewsRaw) on HuggingFace. Raw data before preprocessing has 1,304,717 financial articles and takes up 6.4Gb. Example of data structure:
|title|source|datetime|assets|text|url|
|--|--|--|--|--|--|
EquipmentShare Announces Successful Closing of Upsized Bond Offering|ACCESS Newswire|2023-09-21T16:15:00.000Z|[]|COLUMBIA, MO / ACCESSWIRE / September 21, 2023 / EquipmentShare.com Inc ("EquipmentShare"), one of the fastest-growing...|https://finance.yahoo.com/news/equipmentshare-announces-successful-closing-upsized-161500942.html
Top Stock Reports for Walmart, Adobe & Caterpillar|Zacks|2024-10-04T21:18:00.000Z|["ADBE", "CAT", "EBGEF", "HOVVB", "WMT"]|Friday, October 4, 2024The Zacks Research Daily presents the best research output of our analyst team. Today's Research Daily features new research reports on 16 major stocks...|https://finance.yahoo.com/news/top-stock-reports-walmart-adobe-211800073.html

### 📞 Contacts

Email: denis.tomin.alpino@gmail.com

Telegram: [@denisalpino](https://t.me/denisalpino)