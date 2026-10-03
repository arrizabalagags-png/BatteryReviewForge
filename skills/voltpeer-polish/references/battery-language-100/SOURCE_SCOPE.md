# Retrieval, reading and source-text boundaries

Recorded on 2026-10-02. The [corpus](corpus.json) distinguishes access, metadata corroboration and reading. Its primary article URLs are registered by the publishers in Crossref. The inspected author abstracts were retrieved in Europe PMC MED/core search responses. Selected original article bodies were retrieved through Europe PMC's open-access `fullTextXML` route.

| Evidence operation | Actual result |
|---|---|
| Selected journal articles | 100 unique DOI records; all Crossref type `journal-article` |
| DOI identity and title corroboration | 100 exact DOI matches; normalized titles all at least 0.95 similarity |
| Author abstracts read | 100 complete indexed abstracts |
| OA article XML retrieved | 15 |
| Body text read | 31 listed paragraphs from those 15 articles |
| Complete article bodies / supplements read | 0 / 0 |
| Correction notices | Three indexed; two notice texts inspected; one notice indexed without content inspection |
| Final unresolved abstract/metadata/XML retrieval failures | 0 |
| Recovered API failures | Six Crossref HTTP 429 responses, each followed by a successful retry |

The query window concerns **first publication** before the end of 2025, not the eventual issue year. The selected issue records include 2026 papers first published online in 2025. This distinction is retained rather than forcing both dates into one year.

Each JSON record has an actual batch-query URL and response digest, record ID, normalized abstract digest and retrieval date. The individual lookup URL is supplied separately for convenience. Additional reading is identified by the OA XML digest, exact XML locator, section path and paragraph digest. The normalization strips XML/HTML formatting; raw responses remain private. Hashes locate the cached evidence and do not independently certify the reader's interpretation.

The inspected OA notices use several license labels. The following table records the labels actually seen for the **15 selected full-text samples**, rather than claiming a license audit of all 100 papers:

| Notice label | Sample IDs |
|---|---|
| CC BY 4.0 | BL003, BL031, BL050, BL068, BL069, BL084, BL094, BL100 |
| CC BY 3.0 | BL055 |
| CC BY-NC 3.0 | BL059 |
| CC BY-NC-ND 4.0 | BL013, BL024, BL042, BL086 |
| CC BY-NC, version not stated in the inspected notice | BL082 |

The source license statements and original XML are retained in the private reading cache. This public reference distributes bibliographic metadata, links, digests, ordinary terminology and original editorial rules/examples. It does not distribute article abstracts, article paragraphs, adapted article passages, paper figures, PDFs or raw XML. Inclusion in the corpus does not grant permission to republish an article or its figures.

The locally installed `nature-polishing` guidance was consulted for editorial principles. [GUIDANCE_ADAPTATION.md](GUIDANCE_ADAPTATION.md) records the exact relative paths and adaptations. No redistribution license was inferred from the local installation, and no source skill fragments are redistributed here.

Corrections can matter even when studying language. [BL012's author correction](https://www.nature.com/articles/s41467-026-71811-3) describes figure-axis and image-label amendments. [BL042's publisher correction](https://www.nature.com/articles/s41467-025-62939-9) restores a caption and missing plotted simulation interval. BL037's [indexed correction](https://doi.org/10.1038/s41467-026-70148-1) was recorded, but its content was not inspected because the publisher browser request failed. These notices are not counted as additional members of the 100-paper corpus.

Supplementary browser requests to some publisher pages and the Europe PMC documentation failed, while the API routes used for the actual corpus succeeded. Browser availability does not imply corpus reading, and API success does not imply that an entire article was read. All direct failures and recovered retries are described in the private audit without replacing the successful evidence.
