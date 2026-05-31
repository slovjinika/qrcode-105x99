#!/usr/bin/env python3
import os
import qrcode
from PIL import Image, ImageDraw, ImageFont

# ==========================================
# 1. MAIN SETTINGS AND PATHS
# ==========================================
FONT_PATH = "/home/node17/.fonts/002-Inter/Inter/static/Inter-Bold.otf"
OUTPUT_PDF = "print/labels_a4.pdf"
DPI = 300

# Range of numbers for generation
START_NUM = 1
END_NUM = 54  # 6 blocks * 9 stickers = 54 stickers max per page

# ==========================================
# 2. COLOR AND FONT CONFIGURATION
# ==========================================
COLOR_BACKGROUND = "white"   
COLOR_ELEMENTS = "#4D4D4D"     

# OpenType features set for Inter font
FONT_FEATURES = ["tnum", "cv01", "cv05", "cv06", "calt"]

# ==========================================
# 3. STRICT STICKER GEOMETRY (IN MILLIMETERS)
# ==========================================
PAGE_W_MM = 210
PAGE_H_MM = 297
BLOCK_W_MM = 105
BLOCK_H_MM = 99

STICKER_W_MM = 25
STICKER_H_MM = 28
BORDER_MM = 0.5

GAP_X_MM = 1.5
GAP_Y_MM = 1.5

# --- MAXIMUM FILLING (REMOVING EMPTY SPACE) ---
TEXT_ZONE_RATIO = 0.16   
FONT_SIZE_PT = 10        # Slightly reduced font size for smaller 28mm sticker
TEXT_Y_SHIFT_MM = -1.7   

QR_PADDING_MM = 1.5      
QR_SCALE_FACTOR = 1   

# --- INDIVIDUAL ROW VERTICAL SHIFTS (IN MILLIMETERS) ---
ROW_1_SHIFT_MM = -5
ROW_2_SHIFT_MM = -5
ROW_3_SHIFT_MM = 0.0 

# ==========================================
# AUTOMATIC CONVERSION TO PIXELS
# ==========================================
MM_TO_PX = DPI / 25.4
PT_TO_PX = DPI / 72.0

A4_WIDTH = int(PAGE_W_MM * MM_TO_PX)
A4_HEIGHT = int(PAGE_H_MM * MM_TO_PX)
BLOCK_W = int(BLOCK_W_MM * MM_TO_PX)
BLOCK_H = int(BLOCK_H_MM * MM_TO_PX)

STICKER_W = int(STICKER_W_MM * MM_TO_PX)
STICKER_H = int(STICKER_H_MM * MM_TO_PX)
BORDER_PX = int(BORDER_MM * MM_TO_PX)

FONT_SIZE_PX = int(FONT_SIZE_PT * PT_TO_PX)
Y_SHIFT_PX = int(TEXT_Y_SHIFT_MM * MM_TO_PX)
QR_PADDING_PX = int(QR_PADDING_MM * MM_TO_PX)

TEXT_ZONE_H = int(STICKER_H * TEXT_ZONE_RATIO)
QR_ZONE_H = STICKER_H - TEXT_ZONE_H

QR_SIZE = min(STICKER_W - (BORDER_PX * 2) - (QR_PADDING_PX * 2), 
              QR_ZONE_H - BORDER_PX - QR_PADDING_PX)
QR_SIZE = int(QR_SIZE * QR_SCALE_FACTOR)

# ==========================================
# GENERATION FUNCTIONS
# ==========================================
def create_sticker(text, font_path):
    """Creates a single compact sticker and rotates it 90 degrees"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=1  
    )
    qr.add_data(text)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color=COLOR_ELEMENTS, back_color=COLOR_BACKGROUND).convert('RGB')
    qr_img = qr_img.resize((QR_SIZE, QR_SIZE), Image.Resampling.LANCZOS)
    
    sticker = Image.new("RGB", (STICKER_W, STICKER_H), COLOR_BACKGROUND)
    draw = ImageDraw.Draw(sticker)
    
    qr_x = (STICKER_W - QR_SIZE) // 2
    qr_y = BORDER_PX + QR_PADDING_PX
    sticker.paste(qr_img, (qr_x, qr_y))
    
    try:
        font = ImageFont.truetype(font_path, FONT_SIZE_PX)
    except IOError:
        font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]
    
    text_x = (STICKER_W - text_w) // 2
    text_y = QR_ZONE_H + ((TEXT_ZONE_H - text_h) // 2) + Y_SHIFT_PX
    
    try:
        draw.text((text_x, text_y), text, fill=COLOR_ELEMENTS, font=font, features=FONT_FEATURES)
    except ValueError:
        draw.text((text_x, text_y), text, fill=COLOR_ELEMENTS, font=font)
    
    draw.rectangle(
        [(0, 0), (STICKER_W - 1, STICKER_H - 1)], 
        outline=COLOR_ELEMENTS, 
        width=BORDER_PX
    )
    
    return sticker.rotate(90, expand=True)

# ==========================================
# A4 SHEET ASSEMBLY
# ==========================================
os.makedirs("print", exist_ok=True)
data_list = [f"{i:08d}" for i in range(START_NUM, END_NUM + 1)]

pages = []
current_page = Image.new("RGB", (A4_WIDTH, A4_HEIGHT), "white")
draw_page = ImageDraw.Draw(current_page)

BLOCKS_X = 2
BLOCKS_Y = 3
STICKERS_PER_BLOCK = 9  # Changed from 4 to 9 (3x3 grid)

sticker_idx = 0

# For a 28x28 square sticker, rotated size remains identical
ROTATED_STICKER_W = STICKER_H
ROTATED_STICKER_H = STICKER_W
ROTATED_STICKER_W_MM = STICKER_H_MM
ROTATED_STICKER_H_MM = STICKER_W_MM

for idx, text in enumerate(data_list):
    block_idx = sticker_idx % (BLOCKS_X * BLOCKS_Y * STICKERS_PER_BLOCK)
    
    if block_idx == 0 and idx > 0:
        pages.append(current_page)
        current_page = Image.new("RGB", (A4_WIDTH, A4_HEIGHT), "white")
        draw_page = ImageDraw.Draw(current_page)
        sticker_idx = 0
    
    inside_page_block_idx = sticker_idx // STICKERS_PER_BLOCK
    bx = inside_page_block_idx % BLOCKS_X
    by = inside_page_block_idx // BLOCKS_X
    
    block_left = bx * BLOCK_W
    block_top = by * BLOCK_H
    
    # 3x3 layout calculations inside the block
    inside_sticker_idx = sticker_idx % STICKERS_PER_BLOCK
    sx = inside_sticker_idx % 3  # Column 0, 1, 2
    sy = inside_sticker_idx // 3  # Row 0, 1, 2
    
    # Calculate group width to center or align it properly
    group_w_mm = (ROTATED_STICKER_W_MM * 3) + (GAP_X_MM * 2)
    
    if bx == 0:
        margin_x_mm = BLOCK_W_MM - group_w_mm - 5.0 
    else:
        margin_x_mm = 5.0 

    margin_y_mm = 5.0  # Slightly adjusted top margin to accommodate 3 rows
    
    sticker_x = int(block_left + (margin_x_mm * MM_TO_PX) + (sx * (ROTATED_STICKER_W + GAP_X_MM * MM_TO_PX)))
    sticker_y = int(block_top + (margin_y_mm * MM_TO_PX) + (sy * (ROTATED_STICKER_H + GAP_Y_MM * MM_TO_PX)))
    
    if by == 0:
        sticker_y -= int(ROW_1_SHIFT_MM * MM_TO_PX)
    elif by == 1:
        sticker_y -= int(ROW_2_SHIFT_MM * MM_TO_PX)
    elif by == 2:
        sticker_y -= int(ROW_3_SHIFT_MM * MM_TO_PX)
    
    sticker_img = create_sticker(text, FONT_PATH)
    current_page.paste(sticker_img, (sticker_x, sticker_y))
    
    sticker_idx += 1

# ==========================================
# DEBUG GRID ADDITION AND PDF SAVING
# ==========================================
pages.append(current_page)

DEBUG_GRID = True

if DEBUG_GRID:
    for page in pages:
        overlay = Image.new("RGBA", page.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        line_color = (255, 0, 255, 100)  # Purple transparent line
        
        # --- VERTICAL LINES (105 mm and 210 mm) ---
        x_105mm = int(105 * MM_TO_PX)
        x_210mm = int(210 * MM_TO_PX) - 1
        
        draw.line([(x_105mm, 0), (x_105mm, A4_HEIGHT)], fill=line_color, width=3)
        draw.line([(x_210mm, 0), (x_210mm, A4_HEIGHT)], fill=line_color, width=3)
        
        # --- HORIZONTAL LINES (Block rows: 99 mm and 198 mm) ---
        y_block1 = int(99 * MM_TO_PX)
        y_block2 = int(198 * MM_TO_PX)
        
        draw.line([(0, y_block1), (A4_WIDTH, y_block1)], fill=line_color, width=2)
        draw.line([(0, y_block2), (A4_WIDTH, y_block2)], fill=line_color, width=2)
        
        page.paste(Image.alpha_composite(page.convert("RGBA"), overlay).convert("RGB"))

if pages:
    pages[0].save(
        OUTPUT_PDF, 
        format="PDF",
        save_all=True, 
        append_images=pages[1:], 
        resolution=DPI,
        save_format="pdf",
        encoder_name="raw"
    )
    print(f"Done! PDF generated successfully with 9 stickers per block. Debug lines active: {DEBUG_GRID}")
