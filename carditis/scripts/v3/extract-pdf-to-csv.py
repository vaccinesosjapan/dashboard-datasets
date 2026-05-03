from spire.pdf import *
from spire.xls import *
import unicodedata


# 1つのPDFに含まれる全てのtableデータを抽出して、1つのcsvファイルに保存する。
# 返り値では保存したデータの行数を返す。
def extract_table_data_to_csv(pdf_path :str, csv_path: str) -> int:
    doc = PdfDocument()
    doc.LoadFromFile(pdf_path)
    extractor = PdfTableExtractor(doc)

    workbook = Workbook()
    workbook.Worksheets.Clear()
    worksheet :Worksheet = workbook.CreateEmptySheet()
    
    row_offset = 0
    for page_index in range(doc.Pages.Count):
        tables = extractor.ExtractTable(page_index)
        if tables is None or len(tables) == 0:
            continue

        for table in tables:
            row_count = table.GetRowCount()
            col_count = table.GetColumnCount()

            for row_index in range(row_count):
                for column_index in range(col_count):
                    if row_offset == 0 and row_index == 0:
                        data = f'{column_index}'
                    else:
                        data = table.GetText(row_index, column_index)
                        data = unicodedata.normalize("NFKC", data.replace("", "").replace(" ", ""))
                    worksheet.Range[row_offset + row_index + 1, column_index + 1].Value = data.strip()
            
            row_offset += row_count

    worksheet.SaveToFile(csv_path, ",", Encoding.get_UTF8())
    return row_offset


pdf_name = sys.argv[1]
pdf_path = os.path.join('..', 'pdf-files', pdf_name)

pdf_name_without_ext = os.path.splitext(pdf_name)[0]
csv_path = os.path.join('..', 'intermediate-files', f'{pdf_name_without_ext}.csv')

try:
    saved_row_count = extract_table_data_to_csv(pdf_path, csv_path)
    print(f'{saved_row_count} 行のデータを {csv_path} に保存しました。')
except Exception as e:
    print(f"Error occurred: {str(e)}")