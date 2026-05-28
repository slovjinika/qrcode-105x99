![image](qrcode-105x99-rotate-20260528.jpg)

## A4 sticker sheet generator (6 stickers per sheet — 105×99 mm blocks)

Short README — generates printable PDF for self-adhesive paper with 6 sticker blocks (block size 105×99 mm) containing QR and numeric label.

Requirements
- Python 3.8+
- qrcode, pillow
Install:
```bash
python -m pip install qrcode[pil] pillow
```

What it does
- Produces A4 PDF (300 DPI) for self-adhesive sheets with 6 blocks (each block 105×99 mm), each block contains 4 stickers (2×2) sized 42×38 mm.
- Generates QR codes and centered 8-digit numeric labels.
- Minimizes internal paddings, increases QR size, shifts bottom row up 10 mm for printer alignment.

Quick setup
1. Place a font and set FONT_PATH in the script (fallback to PIL default if not found).
2. Edit START_NUM / END_NUM as needed.
3. Run:
```bash
python3 generate_labels.py
```
Output: print/labels_a4.pdf

![image](screen.jpg)

Notes
- Adjust QR_SCALE_FACTOR or TEXT_ZONE_RATIO to change QR/text balance.
- Margins and BOTTOM_ROW_SHIFT_MM tuned for typical printers — tweak if needed.

![image](qrcode-105x99-20260528.jpg)
