# Harmony API

API for Harmony.

Harmony is a tool using AI and natural language processing, which allows you to compare items from questionnaires and
identify similar content.

The API is live at https://api.harmonydata.org and you can try the docs at https://api.harmonydata.org/docs

You can try Harmony at https://app.harmonydata.org and you can read our blog at https://harmonydata.org/blog/.

Contact: Thomas Wood, thomas@fastdatascience.com, https://fastdatascience.com

## Harmonising Mental Health Data

Do you need to compare questionnaire data across studies? Do you want to find the best match for a set of items? Are
there are different versions of the same questionnaire floating around and you want to make sure how compatible they
are? Are the questionnaires written in different languages that you would like to compare?

Harmony is a data harmonisation project that uses Natural Language Processing to help researchers make better use of
existing data from different studies by supporting them with the harmonisation of various measures and items used in
different studies. Harmony is a collaboration project between the University of Ulster, University College London, the
Universidade Federal de Santa Maria in Brazil, and Fast Data Science Ltd.

## Running the API

If you have Mental Health Catalogue data, put it in a data folder e.g. `/data` and set environment variable `DATA_PATH`.

## API Reference

# Harmony API

API Version: 2.

There is an interactive version of the API docs available at https://api.harmonydata.org/docs. Please also refer to the
PDF at [/docs/API_reference.pdf](/docs/API_reference.pdf).

## INDEX

-
    1. HEALTH CHECK
- 1.1 GET /health-check
-
    2. INFO
- 2.1 GET /info/version
-
    3. TEXT
- 3.1 POST /text/parse
- 3.2 POST /text/match

## API

## 1. HEALTH CHECK

## 1.1 GET /health-check

Health Check

REQUEST

```
No request parameters
```

RESPONSE

```
STATUS CODE - 200: Successful Response
```

```
RESPONSE MODEL - application/json
undefined
```

## 2. INFO

## 2.1 GET /info/version

Show Version

REQUEST

```
No request parameters
```

RESPONSE

```
STATUS CODE - 200: Successful Response
```

```
RESPONSE MODEL - application/json
undefined
```

## 3. TEXT

## 3.1 POST /text/parse

Parse Instruments

Parse PDFs or Excels or text files into Instruments, and identifies the language.

If the file is binary (Excel or PDF), you must supply each file with the content in MIME format and
the bytes in base64 encoding, like the example RawFile in the schema.

If the file is plain text, supply the file content as a standard string.

REQUEST

```
REQUEST BODY - application/json
[{
Array of object:
file_id* string Unique identifier for the file (UUID-4)
file_name* string The name of the input file
file_type* enum ALLOWED:pdf, xlsx, txt
The file type (pdf, xlsx, txt)
content* string The raw file contents
}]
```

RESPONSE

```
STATUS CODE - 200: Successful Response
```

```
RESPONSE MODEL - application/json
[{
Array of object:
file_id* string Unique identifier for the file (UUID-4)
instrument_id* string Unique identifier for the instrument (UUID-4)
instrument_name* string Human-readable name of the instrument
file_name* string The name of the input file
file_type* enum ALLOWED:pdf, xlsx, txt
The file type (pdf, xlsx, txt)
file_section* string The sub-section of the file, e.g. Excel tab
language* enum ALLOWED:de, el, en, es, fr, it, he, ja, ko, pt, ru,
uk, zh, ar, la, tr, af, ak, am, as, ay, az, be, bg,
bho, bm, bn, bs, ca, ceb, ckb, co, cs, cy, da, doi,
dv, ee, eo, et, eu, fa, fi, fil, fy, ga, gd, gl,
gn, gom, gu, ha, haw, hi, hmn, hr, ht, hu, hy, id,
ig, ilo, is, jv, ka, kk, km, kn, kri, ku, ky, lb,
lg, ln, lo, lt, lus, lv, mai, mg, mi, mk, ml, mn,
mni-mtei, mr, ms, mt, my, ne, nl, no, nso, ny, om,
or, pa, pl, ps, qu, ro, rw, sa, sd, si, sk, sl, sm,
sn, so, sq, sr, st, su, sv, sw, ta, te, tg, th, ti,
tk, tl, ts, tt, ug, ur, uz, vi, xh, yi, yo, zh-tw,
zu, yue
The ISO 639-2 (alpha-2) encoding of the instrument language
questions* [{
Array of object:
```

```
question_no* string Number of the question
question_intro* string Introductory text applying to the question
question_text* string Text of the question
options* [string]
source_page* integer The page of the PDF on which the question was located, zero-indexed
}]
}]
```

```
STATUS CODE - 422: Validation Error
```

```
RESPONSE MODEL - application/json
{
detail [{
Array of object:
loc*
ANY OF
prop
string
prop
integer
msg* string
type* string
}]
}
```

## 3.2 POST /text/match

Match

Match instruments

REQUEST

```
REQUEST BODY - application/json
[{
Array of object:
file_id* string Unique identifier for the file (UUID-4)
instrument_id* string Unique identifier for the instrument (UUID-4)
instrument_name* string Human-readable name of the instrument
file_name* string The name of the input file
file_type* enum ALLOWED:pdf, xlsx, txt
The file type (pdf, xlsx, txt)
file_section* string The sub-section of the file, e.g. Excel tab
language* enum ALLOWED:de, el, en, es, fr, it, he, ja, ko, pt, ru, uk, zh,
ar, la, tr, af, ak, am, as, ay, az, be, bg, bho, bm, bn,
bs, ca, ceb, ckb, co, cs, cy, da, doi, dv, ee, eo, et, eu,
fa, fi, fil, fy, ga, gd, gl, gn, gom, gu, ha, haw, hi,
hmn, hr, ht, hu, hy, id, ig, ilo, is, jv, ka, kk, km, kn,
kri, ku, ky, lb, lg, ln, lo, lt, lus, lv, mai, mg, mi, mk,
ml, mn, mni-mtei, mr, ms, mt, my, ne, nl, no, nso, ny, om,
or, pa, pl, ps, qu, ro, rw, sa, sd, si, sk, sl, sm, sn,
so, sq, sr, st, su, sv, sw, ta, te, tg, th, ti, tk, tl,
ts, tt, ug, ur, uz, vi, xh, yi, yo, zh-tw, zu, yue
The ISO 639-2 (alpha-2) encoding of the instrument language
questions* [{
Array of object:
```

```
question_no* string Number of the question
question_intro* string Introductory text applying to the question
question_text* string Text of the question
options* [string]
source_page* integer The page of the PDF on which the question was located, zero-indexed
}]
}]
```

RESPONSE

```
STATUS CODE - 200: Successful Response
```

```
RESPONSE MODEL - application/json
[undefined]
```

```
STATUS CODE - 422: Validation Error
```

```
RESPONSE MODEL - application/json
{
detail [{
Array of object:
loc*
ANY OF
prop
string
prop
integer
msg* string
type* string
}]
}
```
