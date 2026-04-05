import pandas as pd
from fpdf import FPDF
from fpdf.fonts import FontFace
import os
import sys
import datetime
import traceback
import urllib.request
import glob

# --- Font Management ---
FONT_DIR = os.path.join(os.path.expanduser("~"), ".cache", "fpdf2_fonts")
FONT_FILE = os.path.join(FONT_DIR, "NotoSansSC.ttf")
FONT_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/notosans/NotoSans%5Bwdth%2Cwght%5D.ttf"

def ensure_font_exists():
    if not os.path.exists(FONT_FILE):
        print("First run: Downloading font... ", end="", flush=True)
        os.makedirs(FONT_DIR, exist_ok=True)
        urllib.request.urlretrieve(FONT_URL, FONT_FILE)
        print("Done.")
    return FONT_FILE

# --- Custom PDF Class ---
class TablePDF(FPDF):
    def __init__(self, font_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_font('UniFont', '', font_path, variations={"wght": 400})
        self.add_font('UniFont', 'B', font_path, variations={"wght": 700})

    def header(self):
        self.set_font('UniFont', '', 8)
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.cell(0, 5, current_date, align='R', new_x="LMARGIN", new_y="NEXT")

    def footer(self):
        self.set_y(-8)
        self.set_font('UniFont', '', 7)
        self.cell(0, 5, f'Page {self.page_no()}/{{nb}}', align='C')

def convert_file(filename, font_path):
    df = pd.read_csv(filename, sep="\t", na_filter=False, index_col=1,
                     lineterminator="\n", encoding="utf-8")
    df = df.fillna('').reset_index()

    pdf_path = os.path.splitext(filename)[0] + '.pdf'

    pdf = TablePDF(font_path, orientation='L', format='A4')
    pdf.alias_nb_pages()
    pdf.set_left_margin(5)
    pdf.set_right_margin(5)
    pdf.set_top_margin(5)
    pdf.set_auto_page_break(auto=True, margin=8)
    pdf.add_page()
    pdf.set_font('UniFont', size=8)

    headers = [str(col) for col in df.columns]
    data_rows = df.astype(str).values.tolist()
    table_data = [headers] + data_rows

    # --- AUTO-WIDTH CALCULATION ---
    available_width = 287
    max_widths = []
    for col_idx in range(len(headers)):
        max_str = max(str(row[col_idx]) for row in table_data)
        width = pdf.get_string_width(max_str) + 2
        max_widths.append(width)

    total_natural_width = sum(max_widths)
    scale_factor = available_width / total_natural_width
    col_widths = [w * scale_factor for w in max_widths]

    # --- STYLES ---
    normal_style = FontFace()
    header_style = FontFace(emphasis="BOLD")

    # --- RENDER TABLE ---
    with pdf.table(col_widths=col_widths, line_height=4) as table:
        for i, data_row in enumerate(table_data):
            row = table.row()
            for cell_text in data_row:
                if i == 0:
                    row.cell(str(cell_text), style=header_style)
                else:
                    row.cell(str(cell_text), style=normal_style)

    pdf.output(pdf_path)
    return pdf_path

# --- MAIN ---
def process_file(args):
    filepath, font_path = args
    name = os.path.basename(filepath)
    try:
        pdf_path = convert_file(filepath, font_path)
        return f"OK:   {name} -> {os.path.basename(pdf_path)}"
    except Exception:
        return f"FAIL: {name}\n{traceback.format_exc()}"

if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor

    script_dir = os.path.dirname(os.path.abspath(__file__))

    files = []
    for ext in ('*.csv', '*.tsv', '*.txt'):
        files.extend(glob.glob(os.path.join(script_dir, ext)))

    if not files:
        print(f"No CSV/TSV/TXT files found in {script_dir}")
        sys.exit(0)

    font_path = ensure_font_exists()
    files = sorted(files)

    with ProcessPoolExecutor() as pool:
        results = pool.map(process_file, [(f, font_path) for f in files])

    for result in results:
        print(result)

    print(f"\nDone. {len(files)} file(s) processed.")