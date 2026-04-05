# csv2pdftable
 
Converts all CSV/TSV/TXT files in the script directory to formatted PDF tables. Auto-detects delimiters, supports Unicode, runs in parallel.
 
Originally built for data curation work at a company where Word couldn't handle large datasets — the document would grow to hundreds of pages and become completely unusable. This script bypasses that limitation entirely.
 
## Setup
 
```bash
git clone https://github.com/snk0911/csv2pdftable.git
cd csv2tablepdf
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
 
## Usage
 
Place your data files next to `csv2pdftable.py`, then:
 
```bash
python csv2pdf-table.py
```
 
PDFs appear in the same directory.
 
## Note
 
On first run, [Noto Sans](https://fonts.google.com/noto/specimen/Noto+Sans) is downloaded and cached at `~/.cache/fpdf2_fonts/`.
