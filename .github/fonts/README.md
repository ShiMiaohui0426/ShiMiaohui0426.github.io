# CV typography

The downloadable English and Chinese CVs use embedded CV Sans SC fonts,
subset from Noto Sans SC (SIL Open Font License 1.1; see `OFL.txt`). The regular
face is weight 400 and the heading face is weight 650. Both have unique font
names so PDF readers keep the weights distinct.

Original source: [Google Fonts / Noto Sans SC](https://github.com/google/fonts/tree/809e4d8b8d7e9364a914909bb777679606c178b8/ofl/notosanssc).
Source file: `NotoSansSC[wght].ttf`, revision
`809e4d8b8d7e9364a914909bb777679606c178b8`.

## Rebuild the PDFs

From the repository root, with Python 3, ReportLab and PyYAML installed:

```sh
python3 .github/scripts/build-cv.py
```

The script reads employment summaries (`cv_details`), education, skills and
academic experience from `_data/profile.yml`, papers from `_data/papers.yml`,
and the remaining CV copy in `build-cv.py`. Full web descriptions and concise
PDF employment summaries are maintained together in the profile data.
It writes both `files/Miaohui_Shi_CV_EN.pdf` and `files/Miaohui_Shi_CV_ZH.pdf`,
then refreshes `files/SMH_RESUME.pdf` as an identical Chinese compatibility copy.
No network access or system font installation is required to rebuild.

Both versions use two A4 pages. The builder stops on page overflow or a missing
font character. PDF text remains searchable and selectable; publication titles
link to their DOI, and the profile and patent links are clickable.

## Add characters after a content change

The bundled font subsets cover the current CV and profile data plus the Latin
alphabet and punctuation. If the builder reports a missing glyph, download the
original variable TTF from the pinned source above, install `fonttools`, then run:

```sh
python3 .github/scripts/prepare-cv-fonts.py '/path/to/NotoSansSC[wght].ttf'
python3 .github/scripts/build-cv.py
```

Commit both regenerated font files and PDFs together. After changing the CV,
update `UPDATED`, both footer labels, and the download version in
`_includes/profile/cv.html`. Render and inspect all four PDF pages before
publishing; confirm two pages per language and matching legacy PDF bytes.
