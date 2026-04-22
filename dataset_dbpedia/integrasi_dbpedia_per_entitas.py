"""
================================================================
INTEGRASI DBPEDIA → WIKIDATA (LEFT JOIN per Entitas)
================================================================
Wikidata = sumber utama (base)
DBpedia  = sumber pendukung (enrichment)

Strategi:
- LEFT JOIN: semua baris Wikidata tetap ada
- DBpedia hanya menambah kolom baru (tidak menghapus baris)
- Dipisah per entitas: Politikus, Partai, Pendidikan

LANGKAH:
1. Jalankan 3 kueri SPARQL DBpedia di https://dbpedia.org/sparql
2. Simpan masing-masing sebagai CSV
3. Jalankan script ini
================================================================
"""

import pandas as pd

# ════════════════════════════════════════════════════════════
# KUERI SPARQL DBPEDIA — SALIN & JALANKAN DI dbpedia.org/sparql
# ════════════════════════════════════════════════════════════

SPARQL_POLITIKUS = """
# ── KUERI 1: Politikus Indonesia dari DBpedia ──────────────
# Simpan sebagai: dbpedia_politikus.csv
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>

SELECT DISTINCT
  ?wikidataURI
  ?nama
  ?tanggalLahir
  ?tempatLahir
  ?abstrak
WHERE {
  ?person a dbo:Politician ;
          dbo:nationality <http://dbpedia.org/resource/Indonesia> ;
          foaf:name ?nama .
  OPTIONAL { ?person dbo:birthDate  ?tanggalLahir }
  OPTIONAL { ?person dbo:birthPlace ?birthPlaceRes .
             ?birthPlaceRes rdfs:label ?tempatLahir
             FILTER(LANG(?tempatLahir) = "en") }
  OPTIONAL { ?person dbo:abstract ?abstrak
             FILTER(LANG(?abstrak) = "en") }
  OPTIONAL { ?person owl:sameAs ?wikidataURI
             FILTER(CONTAINS(STR(?wikidataURI), "wikidata.org/entity/")) }
  FILTER(LANG(?nama) = "en" || LANG(?nama) = "")
}
ORDER BY ?nama
"""

SPARQL_PARTAI = """
# ── KUERI 2: Partai Politik Indonesia dari DBpedia ─────────
# Simpan sebagai: dbpedia_partai.csv
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>

SELECT DISTINCT
  ?wikidataURI
  ?namaPartai
  ?ideologi
  ?namaIdeologi
  ?tanggalBerdiri
  ?abstrak
WHERE {
  ?partai dct:subject <http://dbpedia.org/resource/Category:Political_parties_in_Indonesia> ;
          rdfs:label ?namaPartai .
  OPTIONAL { ?partai dbo:ideology ?ideologi .
             ?ideologi rdfs:label ?namaIdeologi
             FILTER(LANG(?namaIdeologi) = "en") }
  OPTIONAL { ?partai dbo:foundingDate ?tanggalBerdiri }
  OPTIONAL { ?partai dbo:abstract ?abstrak
             FILTER(LANG(?abstrak) = "en") }
  OPTIONAL { ?partai owl:sameAs ?wikidataURI
             FILTER(CONTAINS(STR(?wikidataURI), "wikidata.org/entity/")) }
  FILTER(LANG(?namaPartai) = "en" || LANG(?namaPartai) = "")
}
ORDER BY ?namaPartai
"""

SPARQL_PENDIDIKAN = """
# ── KUERI 3: Universitas Indonesia dari DBpedia ────────────
# Simpan sebagai: dbpedia_pendidikan.csv
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>

SELECT DISTINCT
  ?wikidataURI
  ?namaUniversitas
  ?tanggalBerdiri
  ?jumlahMahasiswa
  ?kota
  ?abstrak
WHERE {
  ?univ a dbo:University ;
        dbo:country <http://dbpedia.org/resource/Indonesia> ;
        rdfs:label ?namaUniversitas .
  OPTIONAL { ?univ dbo:established ?tanggalBerdiri }
  OPTIONAL { ?univ dbo:numberOfStudents ?jumlahMahasiswa }
  OPTIONAL { ?univ dbo:city ?kotaRes .
             ?kotaRes rdfs:label ?kota
             FILTER(LANG(?kota) = "en") }
  OPTIONAL { ?univ dbo:abstract ?abstrak
             FILTER(LANG(?abstrak) = "en") }
  OPTIONAL { ?univ owl:sameAs ?wikidataURI
             FILTER(CONTAINS(STR(?wikidataURI), "wikidata.org/entity/")) }
  FILTER(LANG(?namaUniversitas) = "en" || LANG(?namaUniversitas) = "")
}
ORDER BY ?namaUniversitas
"""

print("=" * 60)
print("KUERI SPARQL DBPEDIA")
print("=" * 60)
print("Jalankan 3 kueri di atas di: https://dbpedia.org/sparql")
print("Simpan masing-masing sebagai:")
print("  → dbpedia_politikus.csv")
print("  → dbpedia_partai.csv")
print("  → dbpedia_pendidikan.csv")
print()


# ════════════════════════════════════════════════════════════
# HELPER: Ekstrak QID dari URI Wikidata
# ════════════════════════════════════════════════════════════
def ekstrak_qid(uri_series):
    return uri_series.fillna('').str.extract(r'(Q\d+)$')[0]


# ════════════════════════════════════════════════════════════
# LOAD DATA WIKIDATA (BASE)
# ════════════════════════════════════════════════════════════
print("=" * 60)
print("LOAD DATA WIKIDATA (BASE)")
print("=" * 60)

wk_politikus   = pd.read_csv('politikus.csv', sep=';', dtype=str)
wk_partai      = pd.read_csv('partai_politik.csv', sep=';', dtype=str)
wk_pendidikan  = pd.read_csv('tempat_pendidikan.csv', sep=';', dtype=str)

# Normalisasi nama kolom
wk_partai  = wk_partai.rename(columns={'kode_Partai': 'kode_partai'})

print(f"  Wikidata Politikus  : {len(wk_politikus):,}")
print(f"  Wikidata Partai     : {len(wk_partai):,}")
print(f"  Wikidata Pendidikan : {len(wk_pendidikan):,}")


# ════════════════════════════════════════════════════════════
# ENTITAS 1: POLITIKUS
# LEFT JOIN Wikidata Politikus ← DBpedia Politikus
# ════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("ENTITAS 1: POLITIKUS")
print("=" * 60)

import os
if os.path.exists('dbpedia_politikus.csv'):
    dbp_pol = pd.read_csv('dbpedia_politikus.csv', dtype=str)
    # Ekstrak QID dari wikidataURI
    dbp_pol['kode_politikus'] = ekstrak_qid(dbp_pol['wikidataURI'])
    dbp_pol = dbp_pol[dbp_pol['kode_politikus'].notna()].drop_duplicates('kode_politikus')

    # Rename kolom agar jelas sumber DBpedia
    dbp_pol = dbp_pol.rename(columns={
        'nama'         : 'nama_dbpedia',
        'tanggalLahir' : 'tgl_lahir_dbpedia',
        'tempatLahir'  : 'tempat_lahir_dbpedia',
        'abstrak'      : 'abstrak_dbpedia'
    })[['kode_politikus','nama_dbpedia','tgl_lahir_dbpedia',
        'tempat_lahir_dbpedia','abstrak_dbpedia']]

    # LEFT JOIN: semua baris Wikidata tetap ada
    politikus_enriched = wk_politikus.merge(dbp_pol, on='kode_politikus', how='left')

    match = politikus_enriched['nama_dbpedia'].notna().sum()
    print(f"  Wikidata  : {len(wk_politikus):,}")
    print(f"  DBpedia   : {len(dbp_pol):,}")
    print(f"  Match     : {match:,} ({match/len(wk_politikus)*100:.1f}%)")
    print(f"  No match  : {len(politikus_enriched)-match:,} (tetap ada, kolom DBpedia = NaN)")
    print(f"\n  Sample hasil:")
    print(politikus_enriched[politikus_enriched['nama_dbpedia'].notna()]
          [['kode_politikus','politikus','nama_dbpedia','tgl_lahir_dbpedia',
            'tempat_lahir_dbpedia']].head(5).to_string())
else:
    politikus_enriched = wk_politikus.copy()
    politikus_enriched[['nama_dbpedia','tgl_lahir_dbpedia',
                         'tempat_lahir_dbpedia','abstrak_dbpedia']] = None
    print("  ⚠ dbpedia_politikus.csv belum ada — kolom DBpedia diisi NaN")

politikus_enriched.to_csv('entitas_politikus_enriched.csv', index=False)
print(f"\n  ✓ Disimpan: entitas_politikus_enriched.csv ({len(politikus_enriched):,} baris)")


# ════════════════════════════════════════════════════════════
# ENTITAS 2: PARTAI POLITIK
# LEFT JOIN Wikidata Partai ← DBpedia Partai
# ════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("ENTITAS 2: PARTAI POLITIK")
print("=" * 60)

if os.path.exists('dbpedia_partai.csv'):
    dbp_partai = pd.read_csv('dbpedia_partai.csv', dtype=str)
    dbp_partai['kode_partai'] = ekstrak_qid(dbp_partai['wikidataURI'])
    dbp_partai = dbp_partai[dbp_partai['kode_partai'].notna()].drop_duplicates('kode_partai')

    dbp_partai = dbp_partai.rename(columns={
        'namaPartai'    : 'nama_partai_dbpedia',
        'namaIdeologi'  : 'ideologi_dbpedia',
        'tanggalBerdiri': 'tgl_berdiri_dbpedia',
        'abstrak'       : 'abstrak_partai_dbpedia'
    })[['kode_partai','nama_partai_dbpedia','ideologi_dbpedia',
        'tgl_berdiri_dbpedia','abstrak_partai_dbpedia']]

    partai_enriched = wk_partai.merge(dbp_partai, on='kode_partai', how='left')

    match = partai_enriched['nama_partai_dbpedia'].notna().sum()
    print(f"  Wikidata  : {len(wk_partai):,}")
    print(f"  DBpedia   : {len(dbp_partai):,}")
    print(f"  Match     : {match:,} ({match/len(wk_partai)*100:.1f}%)")
    print(f"\n  Sample hasil:")
    print(partai_enriched[partai_enriched['nama_partai_dbpedia'].notna()]
          [['kode_partai','partai','nama_partai_dbpedia',
            'ideologi_dbpedia','tgl_berdiri_dbpedia']].head(5).to_string())
else:
    partai_enriched = wk_partai.copy()
    partai_enriched[['nama_partai_dbpedia','ideologi_dbpedia',
                      'tgl_berdiri_dbpedia','abstrak_partai_dbpedia']] = None
    print("  ⚠ dbpedia_partai.csv belum ada — kolom DBpedia diisi NaN")

partai_enriched.to_csv('entitas_partai_enriched.csv', index=False)
print(f"\n  ✓ Disimpan: entitas_partai_enriched.csv ({len(partai_enriched):,} baris)")


# ════════════════════════════════════════════════════════════
# ENTITAS 3: TEMPAT PENDIDIKAN
# LEFT JOIN Wikidata Pendidikan ← DBpedia Universitas
# ════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("ENTITAS 3: TEMPAT PENDIDIKAN")
print("=" * 60)

if os.path.exists('dbpedia_pendidikan.csv'):
    dbp_pend = pd.read_csv('dbpedia_pendidikan.csv', dtype=str)
    dbp_pend['kode_pendidikan'] = ekstrak_qid(dbp_pend['wikidataURI'])
    dbp_pend = dbp_pend[dbp_pend['kode_pendidikan'].notna()].drop_duplicates('kode_pendidikan')

    dbp_pend = dbp_pend.rename(columns={
        'namaUniversitas' : 'nama_univ_dbpedia',
        'tanggalBerdiri'  : 'tgl_berdiri_univ_dbpedia',
        'jumlahMahasiswa' : 'jml_mahasiswa_dbpedia',
        'kota'            : 'kota_dbpedia',
        'abstrak'         : 'abstrak_univ_dbpedia'
    })[['kode_pendidikan','nama_univ_dbpedia','tgl_berdiri_univ_dbpedia',
        'jml_mahasiswa_dbpedia','kota_dbpedia','abstrak_univ_dbpedia']]

    pendidikan_enriched = wk_pendidikan.merge(dbp_pend, on='kode_pendidikan', how='left')

    match = pendidikan_enriched['nama_univ_dbpedia'].notna().sum()
    print(f"  Wikidata  : {len(wk_pendidikan):,}")
    print(f"  DBpedia   : {len(dbp_pend):,}")
    print(f"  Match     : {match:,} ({match/len(wk_pendidikan)*100:.1f}%)")
    print(f"\n  Sample hasil:")
    print(pendidikan_enriched[pendidikan_enriched['nama_univ_dbpedia'].notna()]
          [['kode_pendidikan','pendidikan','nama_univ_dbpedia',
            'tgl_berdiri_univ_dbpedia','kota_dbpedia']].head(5).to_string())
else:
    pendidikan_enriched = wk_pendidikan.copy()
    pendidikan_enriched[['nama_univ_dbpedia','tgl_berdiri_univ_dbpedia',
                          'jml_mahasiswa_dbpedia','kota_dbpedia',
                          'abstrak_univ_dbpedia']] = None
    print("  ⚠ dbpedia_pendidikan.csv belum ada — kolom DBpedia diisi NaN")

pendidikan_enriched.to_csv('entitas_pendidikan_enriched.csv', index=False)
print(f"\n  ✓ Disimpan: entitas_pendidikan_enriched.csv ({len(pendidikan_enriched):,} baris)")


# ════════════════════════════════════════════════════════════
# RINGKASAN HASIL
# ════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("RINGKASAN — KOLOM YANG DITAMBAHKAN DARI DBPEDIA")
print("=" * 60)
print("""
  entitas_politikus_enriched.csv
  ├── [Wikidata] politikus, kode_politikus
  └── [DBpedia]  nama_dbpedia, tgl_lahir_dbpedia,
                 tempat_lahir_dbpedia, abstrak_dbpedia

  entitas_partai_enriched.csv
  ├── [Wikidata] partai, kode_partai
  └── [DBpedia]  nama_partai_dbpedia, ideologi_dbpedia,
                 tgl_berdiri_dbpedia, abstrak_partai_dbpedia

  entitas_pendidikan_enriched.csv
  ├── [Wikidata] pendidikan, kode_pendidikan
  └── [DBpedia]  nama_univ_dbpedia, tgl_berdiri_univ_dbpedia,
                 jml_mahasiswa_dbpedia, kota_dbpedia,
                 abstrak_univ_dbpedia

  JOIN KEY: kode QID Wikidata ← owl:sameAs → DBpedia wikidataURI
  STRATEGI: LEFT JOIN (baris Wikidata tidak berkurang)
""")
print("✅ SELESAI")
