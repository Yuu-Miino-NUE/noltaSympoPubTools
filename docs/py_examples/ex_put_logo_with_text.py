from PdfStampTools import put_logo_with_text, mm

with open("first_page_overlay.pdf", "wb") as f:
    put_logo_with_text(
        into=f,
        text_lines=[
            "2023 International Symposium on Examples of the SympoPubTools",
            "EXSPT2023, September 26-29, 2023, Tokyo, Japan",
        ],
        logo_file="logo.png",
        pos_x=95.5 * mm,
        pos_y=272 * mm,
        logo_width=15 * mm,
    )
