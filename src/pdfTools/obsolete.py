from PdfStampTools import put_logo_with_text, mm, put_image, put_text


def make_overlay_pdf(
    output: str, logo_texts_config: dict, pi_args: dict = {}, pt_args: dict = {}
):
    with open(output, "wb") as f:
        put_logo_with_text(f, **logo_texts_config)

    with open(output, "rb+") as f:
        if pi_args:
            put_image(f, **pi_args)
        if pt_args:
            put_text(f, **pt_args)


plwt_args = {
    "text_lines": [
        "2023 International Symposium on Nonlinear Theory and Its Applications",
        "NOLTA2023, September 26-29, 2023, Catania and Online",
    ],
    "logo_file": "../open_data/img/nolta_logo.png",
    "pos_x": 89.5 * mm,
    "pos_y": 272 * mm,
    "logo_width": 15 * mm,
}
pi_args = {
    "img_file": "../open_data/img/cc_logo.png",
    "img_width": 17 * mm,
    "x": 19.75 * mm,
    "y": 20 * mm,
}
pt_args = {
    "text_lines": [
        "This work is licensed under a Creative Commons",
        "Attribution-NonCommercial-NoDerivatives 4.0 International.",
    ],
    "x": pi_args["x"] + pi_args["img_width"] + 2 * mm,
    "y": pi_args["y"] + 3.5 * mm,
}
