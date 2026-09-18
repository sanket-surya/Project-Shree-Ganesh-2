import pypdf

def extract_pdf_info(pdf_path, out_txt_path, max_pages=5):
    try:
        reader = pypdf.PdfReader(pdf_path)
        with open(out_txt_path, "w", encoding="utf-8") as out:
            out.write(f"PDF: {pdf_path}\nTotal Pages: {len(reader.pages)}\n\n")
            for i in range(min(max_pages, len(reader.pages))):
                out.write(f"=== PAGE {i+1} ===\n")
                text = reader.pages[i].extract_text() or ""
                out.write(text + "\n\n")
        print(f"Extracted {pdf_path} to {out_txt_path}")
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")

extract_pdf_info("Real-time monitoring and evaluation method for aero-engine performance degradation based on performance digital twin.pdf", r"C:\Users\Asus\.gemini\antigravity-ide\brain\10ccc355-5f51-432e-b3f9-817b7bebff39\scratch\paper1_summary.txt", 6)
extract_pdf_info("FulltextThesis.pdf", r"C:\Users\Asus\.gemini\antigravity-ide\brain\10ccc355-5f51-432e-b3f9-817b7bebff39\scratch\paper2_thesis.txt", 6)
