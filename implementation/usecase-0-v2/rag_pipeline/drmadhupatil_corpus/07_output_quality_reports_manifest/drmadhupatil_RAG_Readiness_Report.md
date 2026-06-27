# Dr. Madhu Patil Website RAG Readiness Report

Generated at: 2026-06-26T21:10:01.056378+00:00

## Summary

- Pages crawled: 14
- Pages failed: 0
- Raw RAG documents: 14
- Approved RAG documents: 8
- Duplicate documents excluded: 6
- URLs skipped: 6

## Approved Documents

- WEB-DRMADHU-001 | 00_Homepage | 3053 words | Dr. Madhu Patil | Gynecologist & IVF Specialist | https://drmadhupatil.com/
- WEB-DRMADHU-002 | service1 | 1208 words | Fertility Assessment - Advanced Fertility Solutions | https://drmadhupatil.com/service1
- WEB-DRMADHU-003 | service2 | 1120 words | IVF & ICSI Treatments - Advanced Fertility Solutions | https://drmadhupatil.com/service2
- WEB-DRMADHU-004 | service3 | 1159 words | IUI Treatment - Advanced Fertility Solutions | https://drmadhupatil.com/service3
- WEB-DRMADHU-005 | service4 | 1046 words | Fertility Preservation - Advanced Fertility Solutions | https://drmadhupatil.com/service4
- WEB-DRMADHU-006 | service5 | 1486 words | Endometriosis & PCOS - Advanced Fertility Care | https://drmadhupatil.com/service5
- WEB-DRMADHU-007 | service6 | 1263 words | Immunotherapy in Infertility - Advanced Fertility Care | https://drmadhupatil.com/service6
- WEB-DRMADHU-008 | blog | 89 words | Blog | Coming Soon | https://drmadhupatil.com/blog

## Excluded Duplicate URL Variants

- service1_html | https://drmadhupatil.com/service1.html -> https://drmadhupatil.com/service1
- service2_html | https://drmadhupatil.com/service2.html -> https://drmadhupatil.com/service2
- service3_html | https://drmadhupatil.com/service3.html -> https://drmadhupatil.com/service3
- service4_html | https://drmadhupatil.com/service4.html -> https://drmadhupatil.com/service4
- service5_html | https://drmadhupatil.com/service5.html -> https://drmadhupatil.com/service5
- service6_html | https://drmadhupatil.com/service6.html -> https://drmadhupatil.com/service6

## Retrieval Input

`06_output_rag_documents_ready/drmadhupatil_rag_corpus.jsonl`

## Next Step

Build the BM25 + FAISS hybrid index from the approved JSONL corpus before allowing fallback to `web_search_agent`.
