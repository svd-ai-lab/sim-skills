---
name: research-paper-data
description: Search scholarly literature and research data through discoverable providers, including public metadata APIs, optional user-configured sources, legal open-access full-text discovery, identifier resolution, and citation/reference triage. Use when the user asks for paper search, topic or author literature discovery, DOI/arXiv/PMID/PMCID lookup, dataset DOI metadata, legal OA PDF or full-text locations, references, citations, related work, paper metadata, or evidence-backed literature triage.
---

# Research Paper Data

## Overview

Use this skill to search scholarly metadata, resolve persistent identifiers,
and find legal open-access full text using providers that are visible in the
current runtime. Prefer capability discovery and provenance over assuming a
specific service, credential, or edition.

When `OPENCODE_CONFIG_DIR` is set, first look for
`$OPENCODE_CONFIG_DIR/research-capabilities.json`. Treat that file as the
edition's provider declaration. If it is missing, continue with public defaults
listed below.

Read `references/public-apis.md` when making direct API requests or debugging a
source-specific response. Use `scripts/academic_search.py` for broad topic,
author, affiliation, ORCID, or OpenAlex/Crossref discovery when Python is
available.

## Provider Policy

Provider declarations use:

- `public`: no user secret required.
- `user-configured`: requires a visible user-provided setting, usually an
  environment variable.
- `managed`: an edition-provided provider; use only when its declared base URL
  and auth requirements are visible in the current runtime.

Default public sources:

- Crossref for article, book, proceedings, and reference metadata.
- arXiv for preprints and arXiv PDFs.
- Europe PMC for PMID, PMCID, biomedical metadata, and OA links.
- DataCite for dataset, software, preprint, and non-article DOI metadata.
- OpenAlex discovery through `scripts/academic_search.py` for broad topic,
  author, affiliation, ORCID, and citation-aware search. Treat OpenAlex results
  as discovery candidates; resolve selected DOI/arXiv/PMID records through an
  authoritative source before claiming final metadata or OA availability.

Optional user-configured sources:

- Use Unpaywall only when `UNPAYWALL_EMAIL` is visible.
- Use a visible `OPENALEX_API_KEY` for a higher OpenAlex request budget; the
  search script supports it for work, author, and ORCID lookups. Basic anonymous
  queries remain available within the source's current limits.
- For Crossref polite-pool access, pass `--mailto` to
  `scripts/academic_search.py` or use `OPENALEX_MAILTO`, `CROSSREF_MAILTO`, or
  `RESEARCH_CONTACT_EMAIL` when visible.
- Use enhanced citation, graph, or full-text providers only when declared in
  `research-capabilities.json` and their required configuration is visible.

Use legal open-access/source-discovery paths only. Do not use paywall bypass,
credential sharing, scraped account credentials, or undeclared hidden secrets.

## Workflow

1. Discover providers.
   - Read `research-capabilities.json` when present.
   - Check required environment variables or local configuration before using a
     `user-configured` or `managed` provider.
   - If a declared provider is unavailable, skip it and say why when it affects
     coverage.
2. Classify the request.
   - Natural-language topic search: run `scripts/academic_search.py` first for
     ranked discovery when Python is available; then resolve selected
     identifiers through Crossref, arXiv, Europe PMC, or DataCite.
   - Author search or disambiguation: use `--author`, `--affiliation`,
     `--orcid`, `--author-id`, or `--list-authors`; report ambiguity instead
     of guessing.
   - DOI: normalize and query Crossref; if the item looks like a dataset,
     software, preprint, or Crossref fails, fall back to DataCite.
   - arXiv ID: query arXiv and construct canonical abstract and PDF URLs.
   - PMID or PMCID: query Europe PMC.
   - Citation/reference graph: use declared reference-capable providers and
     source-specific reference fields; do not present citation relationships as
     exhaustive unless a source proves them.
3. Find legal full text.
   - Prefer arXiv PDFs for arXiv records.
   - Prefer Europe PMC OA links for PMCID/biomedical records.
   - Use Unpaywall only when configured.
   - Otherwise report legal OA links found in source metadata, or state that no
     legal open full text was found.
4. Return compact, auditable results.
   - Include title, authors, year, venue/container, identifier, source name,
     source URL, OA URL/PDF URL when found, and confidence notes.
   - Mark ambiguous matches and do not collapse multiple plausible papers into
     one answer.
   - Cite provider provenance and source failures when they affect trust,
     coverage, or next steps.

## Query Hygiene

- Use conservative result limits first, usually 5 to 10 records.
- Prefer `python scripts/academic_search.py "<query>" --limit 5 --compact` for
  broad discovery smoke tests and quick triage. Use JSON output for downstream
  parsing.
- URL-encode user queries and identifiers.
- Respect rate limits and retry-after headers.
- Prefer HTTPS JSON APIs. For arXiv, parse Atom/XML carefully and preserve the
  `id`, `published`, `updated`, authors, categories, and PDF link.
- For DOI comparisons, normalize by removing URL prefixes and lowercasing the
  DOI string.

## Response Shape

For searches, provide:

- `Best matches`: short ranked list with title, year, authors, venue, DOI or
  other identifier, and source.
- `Full text`: legal PDF/full-text candidates or a clear not-found statement.
- `Coverage notes`: skipped optional sources, ambiguity, rate limits, or source
  failures.
- `Next step`: one focused recommendation, such as resolving one DOI, searching
  arXiv variants, or downloading an OA PDF with user approval.

For identifier resolution, provide one record when confident, or a small
candidate set when not confident. Never fabricate abstracts, citations, PDFs,
or author names when the source does not provide them.
