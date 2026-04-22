# 🗳️ Graf Data Politikus Indonesia

> Analisis jaringan hubungan politikus Indonesia menggunakan data dari **Wikidata** dan **DBpedia**, divisualisasikan sebagai graf di **Neo4j**.

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://python.org)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.x-green?logo=neo4j)](https://neo4j.com)
[![Wikidata](https://img.shields.io/badge/Data-Wikidata-red?logo=wikidata)](https://wikidata.org)
[![DBpedia](https://img.shields.io/badge/Data-DBpedia-orange)](https://dbpedia.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📌 Deskripsi Proyek

Proyek ini membangun **graf jaringan politik Indonesia** yang menghubungkan entitas:
- 🧑‍💼 **Politikus** — 52.295 politikus warga negara Indonesia
- 🏛️ **Partai Politik** — 156 partai
- 🎓 **Tempat Pendidikan** — 881 universitas & institusi
- 👨‍👩‍👧 **Kerabat** — 1.746 relasi keluarga (549 sesama politikus, 1.197 non-politikus)

Data utama diambil dari **Wikidata** via SPARQL, diperkaya (*enriched*) dengan data dari **DBpedia**, lalu diimport ke **Neo4j** untuk analisis graf dan visualisasi.

---

## 📁 Struktur Folder

```
Graf-Data-Politikus-Indonesia/
│
├── dataset_wikipedia/              ← Data mentah hasil kueri Wikidata (SPARQL)
│   ├── politikus.csv
│   ├── partai_politik.csv
│   ├── tempat_pendidikan.csv
│   ├── relasi_politikus_partai.csv
│   ├── relasi_tempatPendidikan_politikus.csv
│   └── relasi_politikus_kerabat.csv
│
├── dataset_dbpedia/                ← Data hasil kueri DBpedia (enrichment)
│   ├── dbpedia_politikus.csv
│   ├── dbpedia_partai.csv
│   └── dbpedia_pendidikan.csv
│   |__dll
├── dataset_load_to_neo4j/          ← File siap import ke Neo4j
│   ├── nodes_politikus.csv         (node :Politikus)
│   ├── nodes_partai.csv            (node :Partai)
│   ├── nodes_pendidikan.csv        (node :Pendidikan)
│   ├── nodes_person.csv            (node :Person — kerabat non-politikus)
│   ├── edges_anggota_partai.csv    (relasi ANGGOTA_PARTAI)
│   ├── edges_alumni.csv            (relasi ALUMNI)
│   ├── edges_kerabat_politikus.csv (relasi KERABAT → Politikus)
│   └── edges_kerabat_person.csv    (relasi KERABAT → Person)
└── README.md
```

---

## ⚙️ Instalasi

### Prasyarat

| Tools | Versi |
|---|---|
| Python | 3.8+ |
| Neo4j Desktop | 5.x |
| Neo4j GDS Plugin | 2.x |

### 1. Clone Repository

```bash
git clone https://github.com/ibrahimamar07/Graf-Data-Politikus-Indonesia.git
cd Graf-Data-Politikus-Indonesia
```

### 2. Install Dependencies Python

```bash
pip install pandas networkx python-louvain matplotlib SPARQLWrapper
```

### 3. Install Neo4j Desktop

1. Download di [https://neo4j.com/download](https://neo4j.com/download)
2. Buat database baru → **New → Local DBMS**
3. Install plugin **Graph Data Science Library** dari tab **Plugins**
4. Start database

---

## 🔄 Alur Penggunaan

```
Wikidata SPARQL ──→ dataset_wikipedia/
                         │
DBpedia SPARQL  ──→ dataset_dbpedia/
                         │
                    integrasi_dbpedia_per_entitas.py
                         │ (LEFT JOIN per entitas)
                         ▼
                  entitas_*_enriched.csv
                         │
                    dataset_load_to_neo4j/
                         │ (LOAD CSV Cypher)
                         ▼
                       Neo4j Graph
                         │
                    analisis_graf_politikus.py
                    (NetworkX + Louvain)
```

---

## 📥 Import Data ke Neo4j

> File CSV diambil langsung dari GitHub — **tidak perlu download manual**. Cukup jalankan Cypher di bawah secara berurutan di Neo4j Browser.

### STEP 1 — Buat Constraint

```cypher
CREATE CONSTRAINT FOR (p:Politikus)  REQUIRE p.kodeId IS UNIQUE;
CREATE CONSTRAINT FOR (p:Partai)     REQUIRE p.kodeId IS UNIQUE;
CREATE CONSTRAINT FOR (p:Pendidikan) REQUIRE p.kodeId IS UNIQUE;
CREATE CONSTRAINT FOR (p:Person)     REQUIRE p.kodeId IS UNIQUE;
```

### STEP 2 — Import Node Politikus

```cypher
LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/ibrahimamar07/Graf-Data-Politikus-Indonesia/main/dataset_load_to_neo4j/nodes_politikus.csv' AS row
WITH row WHERE row.`kodeId:ID` IS NOT NULL AND row.`kodeId:ID` <> ''
MERGE (p:Politikus {kodeId: row.`kodeId:ID`})
SET p.nama = REPLACE(row.nama, "'", '');
```

### STEP 3 — Import Node Partai

```cypher
LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/ibrahimamar07/Graf-Data-Politikus-Indonesia/main/dataset_load_to_neo4j/nodes_partai.csv' AS row
WITH row WHERE row.`kodeId:ID` IS NOT NULL AND row.`kodeId:ID` <> ''
MERGE (p:Partai {kodeId: row.`kodeId:ID`})
SET p.nama = row.nama;
```

### STEP 4 — Import Node Pendidikan

```cypher
LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/ibrahimamar07/Graf-Data-Politikus-Indonesia/main/dataset_load_to_neo4j/nodes_pendidikan.csv' AS row
WITH row WHERE row.`kodeId:ID` IS NOT NULL AND row.`kodeId:ID` <> ''
MERGE (p:Pendidikan {kodeId: row.`kodeId:ID`})
SET p.nama = row.nama;
```

### STEP 5 — Import Node Person *(kerabat non-politikus)*

```cypher
LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/ibrahimamar07/Graf-Data-Politikus-Indonesia/main/dataset_load_to_neo4j/nodes_person.csv' AS row
WITH row WHERE row.`kodeId:ID` IS NOT NULL AND row.`kodeId:ID` <> ''
MERGE (p:Person {kodeId: row.`kodeId:ID`})
SET p.nama = row.nama;
```

### STEP 6 — Import Edge: ANGGOTA\_PARTAI

```cypher
:auto LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/ibrahimamar07/Graf-Data-Politikus-Indonesia/main/dataset_load_to_neo4j/edges_anggota_partai.csv' AS row
WITH row WHERE row.`:START_ID` IS NOT NULL AND row.`:END_ID` IS NOT NULL
AND row.`:START_ID` <> '' AND row.`:END_ID` <> ''
CALL { WITH row
  MATCH (a:Politikus {kodeId: row.`:START_ID`})
  MATCH (b:Partai    {kodeId: row.`:END_ID`})
  MERGE (a)-[:ANGGOTA_PARTAI]->(b)
} IN TRANSACTIONS OF 1000 ROWS;
```

### STEP 7 — Import Edge: ALUMNI

```cypher
:auto LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/ibrahimamar07/Graf-Data-Politikus-Indonesia/main/dataset_load_to_neo4j/edges_alumni.csv' AS row
WITH row WHERE row.`:START_ID` IS NOT NULL AND row.`:END_ID` IS NOT NULL
AND row.`:START_ID` <> '' AND row.`:END_ID` <> ''
CALL { WITH row
  MATCH (a:Politikus  {kodeId: row.`:START_ID`})
  MATCH (b:Pendidikan {kodeId: row.`:END_ID`})
  MERGE (a)-[:ALUMNI]->(b)
} IN TRANSACTIONS OF 500 ROWS;
```

### STEP 8 — Import Edge: KERABAT → Politikus

```cypher
:auto LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/ibrahimamar07/Graf-Data-Politikus-Indonesia/main/dataset_load_to_neo4j/edges_kerabat_politikus.csv' AS row
WITH row WHERE row.`:START_ID` IS NOT NULL AND row.`:END_ID` IS NOT NULL
AND row.`:START_ID` <> '' AND row.`:END_ID` <> ''
CALL { WITH row
  MATCH (a:Politikus {kodeId: row.`:START_ID`})
  MATCH (b:Politikus {kodeId: row.`:END_ID`})
  MERGE (a)-[:KERABAT {tipe: row.tipe}]->(b)
} IN TRANSACTIONS OF 500 ROWS;
```

### STEP 9 — Import Edge: KERABAT → Person

```cypher
:auto LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/ibrahimamar07/Graf-Data-Politikus-Indonesia/main/dataset_load_to_neo4j/edges_kerabat_person.csv' AS row
WITH row WHERE row.`:START_ID` IS NOT NULL AND row.`:END_ID` IS NOT NULL
AND row.`:START_ID` <> '' AND row.`:END_ID` <> ''
CALL { WITH row
  MATCH (a:Politikus {kodeId: row.`:START_ID`})
  MATCH (b:Person    {kodeId: row.`:END_ID`})
  MERGE (a)-[:KERABAT {tipe: row.tipe}]->(b)
} IN TRANSACTIONS OF 500 ROWS;
```

### STEP 10 — Verifikasi

```cypher
MATCH (n) RETURN labels(n) AS label, count(n) AS jumlah ORDER BY jumlah DESC;
MATCH ()-[r]->() RETURN type(r) AS relasi, count(r) AS jumlah;
```

---

## 🔬 Analisis Graf (GDS)

Pastikan plugin **Graph Data Science** sudah terinstall, lalu jalankan:

```cypher
// ── Proyeksi Graf ─────────────────────────────────────────
CALL gds.graph.project(
  'graf_politik',
  ['Politikus', 'Partai', 'Pendidikan', 'Person'],
  {
    ANGGOTA_PARTAI: { orientation: 'UNDIRECTED' },
    ALUMNI:         { orientation: 'UNDIRECTED' },
    KERABAT:        { orientation: 'UNDIRECTED' }
  }
)
YIELD graphName, nodeCount, relationshipCount;

// ── Betweenness Centrality ────────────────────────────────
CALL gds.betweenness.write('graf_politik', { writeProperty: 'betweenness' })
YIELD centralityDistribution, nodePropertiesWritten;

// ── PageRank ──────────────────────────────────────────────
CALL gds.pageRank.write('graf_politik', {
  maxIterations: 20, dampingFactor: 0.85, writeProperty: 'pagerank'
})
YIELD ranIterations, didConverge;

// ── Louvain Community Detection ───────────────────────────
CALL gds.louvain.write('graf_politik', { writeProperty: 'community' })
YIELD communityCount, modularity;

// ── Jaccard Similarity ────────────────────────────────────
CALL gds.nodeSimilarity.write('graf_politik', {
  writeRelationshipType: 'MIRIP',
  writeProperty: 'jaccardScore',
  similarityCutoff: 0.01,
  topK: 5
})
YIELD nodesCompared, relationshipsWritten;
```

---

## 💡 Contoh Query Insight

```cypher
// Top 10 partai paling berpengaruh (Betweenness)
MATCH (n:Partai)
WHERE n.betweenness IS NOT NULL
RETURN n.nama AS partai, n.betweenness AS betweenness
ORDER BY betweenness DESC LIMIT 10;

// Dinasti politik — politikus dengan kerabat politikus terbanyak
MATCH (p:Politikus)-[:KERABAT]->(k:Politikus)
WHERE p.nama <> ''
RETURN p.nama AS politikus, count(k) AS jumlah_kerabat_politikus
ORDER BY jumlah_kerabat_politikus DESC LIMIT 10;

// Visualisasi jaringan keluarga
MATCH path = (a:Politikus)-[:KERABAT*1..3]-(b:Politikus)
WHERE a.nama <> '' AND b.nama <> ''
WITH a, count(DISTINCT b) AS jaringan_keluarga
WHERE jaringan_keluarga >= 3
ORDER BY jaringan_keluarga DESC LIMIT 10
WITH collect(a.kodeId) AS tokoh_ids
MATCH path = (a:Politikus)-[:KERABAT*1..3]-(b:Politikus)
WHERE a.kodeId IN tokoh_ids AND b.nama <> ''
RETURN path LIMIT 150;

// Universitas yang paling banyak mencetak politikus
MATCH (p:Politikus)-[:ALUMNI]->(u:Pendidikan)
RETURN u.nama AS universitas, count(p) AS jumlah_alumni
ORDER BY jumlah_alumni DESC LIMIT 15;
```

---

## 📊 Hasil Analisis

| Metrik | Nilai |
|---|---|
| Total Node | 54.357 |
| Total Edge | 55.161 |
| Komunitas (Louvain) | 44 |
| Modularity Score | 0.895 |
| Partai Betweenness Tertinggi | Partai Amanat Nasional (0.1613) |
| Partai PageRank Tertinggi | Partai Golongan Karya (0.0289) |
| Pasangan Partai Paling Mirip | PKS ↔ Gelora (Jaccard: 0.0081) |
| Politikus Kerabat Terbanyak | Megawati Soekarnoputri (7 kerabat politikus) |

---

## 🔗 Sumber Data

| Sumber | URL | Keterangan |
|---|---|---|
| Wikidata SPARQL | [query.wikidata.org](https://query.wikidata.org) | Sumber utama |
| DBpedia SPARQL | [dbpedia.org/sparql](https://dbpedia.org/sparql) | Sumber pendukung (enrichment) |

### Properti Wikidata yang Digunakan
- `wdt:P27` — kewarganegaraan (Indonesia `Q252`)
- `wdt:P106` — pekerjaan (politikus `Q82955`)
- `wdt:P102` — anggota partai politik
- `wdt:P69` — tempat pendidikan
- `wdt:P1038` — relasi keluarga

### Properti DBpedia yang Digunakan
- `dbo:nationality` — kebangsaan
- `dbo:party` — partai politik
- `dbo:almaMater` — tempat pendidikan
- `dbo:birthDate` — tanggal lahir
- `dbo:abstract` — deskripsi singkat
- `owl:sameAs` — link ke Wikidata QID

---

## 📄 Lisensi

MIT License © 2024 [ibrahimamar07](https://github.com/ibrahimamar07)
