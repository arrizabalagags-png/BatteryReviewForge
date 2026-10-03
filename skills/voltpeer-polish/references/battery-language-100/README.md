# Battery language evidence for VoltPeer

This reference set supports editing an existing battery manuscript. It contains 100 verified journal-article DOI records, independent reading observations, an editorial guide, a terminology ledger starter and original evaluation fixtures.

The reading scope is **100 complete indexed author abstracts and 31 selected body paragraphs from 15 lawful open-access articles**. No complete article or supplement was read as part of this work. Downloading an article is not counted as reading its full text.

The set has 10 topic buckets with 10 unique papers each: lithium ion, lithium metal, sodium, aqueous zinc, solid state, solvation, interfaces, performance, redox flow, and sulfur/multivalent chemistry. It includes 11 journals and 8 reviews. The earliest publication years in the selected metadata are 2022–2025; some issue records are dated 2026 after online publication in 2025. Both dates are retained in the index. This is a purposive sample biased toward accessible recent papers, with substantial concentration in Nature Communications, Chemical Science, Advanced Science and Science Advances. It is not a systematic review, a representative sample of all battery writing, or a frequency benchmark.

Read [DOMAIN_GUIDE.md](DOMAIN_GUIDE.md) for the editing contract. Consult [GLOSSARY.md](GLOSSARY.md) when terms occur in the supplied manuscript, and [PHRASE_FUNCTIONS.md](PHRASE_FUNCTIONS.md) when a sentence needs a clearer scientific function. Load relevant passages rather than the entire corpus during routine polishing.

The evidence index is [corpus.csv](corpus.csv) for browsing and [corpus.json](corpus.json) for exact retrieval dates, hashes, DOI checks and paragraph locators. The `year` field describes first publication; `issue_year` preserves the separately indexed issue year. Every record identifies the publisher's primary URL, the abstract batch-query endpoint actually fetched, its PMID within that response, the Crossref metadata endpoint and exactly which additional paragraphs were inspected. A separate `abstract_record_lookup_url` is a convenient individual-record URL, not an assertion of an additional retrieval. The row observations are original editorial notes, not quotations or endorsements of the papers' scientific claims.

No abstracts, paper paragraphs, figures, original numerical datasets, PDFs or full-text XML are distributed here. Raw source responses and the reading cache remain in the private website project. Titles, DOI metadata, links, digests and brief original observations establish provenance without making a second article collection public.

This guidance was independently written after consulting the locally installed `nature-polishing` routing/core guidance. [GUIDANCE_ADAPTATION.md](GUIDANCE_ADAPTATION.md) records the adopted principles and deliberate adaptations. This reference does not require that skill to be installed and does not reproduce its fragments.

Run the conservative engineering checks from any working directory:

```text
python validate_polish.py --self-test --report evaluation-report.json
python validate_polish.py --check-corpus
python validate_polish.py --responses candidate-responses.json --report candidate-report.json
```

[evaluation_cases.json](evaluation_cases.json) contains original synthetic manuscript passages, acceptable examples and deliberately corrupted outputs. The self-test exercises fact-preservation checks; it does not certify model quality. To evaluate an assistant, run the actual polishing task on the source passages, save its responses in the documented format and run the checker. Human review must still assess scientific meaning, edit scope and the adequacy of the prose.
