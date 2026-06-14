import os
import re
import sys
import cv2
import numpy as np
import pandas as pd

ROOT_DIR   = r"C:\Data Collection\CycleGAN_Dataset"
SUBFOLDERS = ["trainA", "trainB", "testA", "testB"]
OUTPUT_CSV = "dataset_labels.csv"

COLOR_FEMUR   = (0,   0,   255)
COLOR_TIBIA   = (255, 0,   0  )
COLOR_TEXT    = (0,   255, 0  )
COLOR_GOLD    = (0,   215, 255)
COLOR_DIM     = (180, 180, 180)
COLOR_SHADOW  = (0,   0,   0  )
COLOR_DRAG    = (255, 255, 0  )

BOX_THICKNESS      = 2
CENTROID_RADIUS    = 5
CENTROID_THICKNESS = -1

FONT           = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE     = 0.55
FONT_THICKNESS = 1

WINDOW_NAME = "Physis Annotator"

CSV_COLUMNS = [
    "folder_name", "filename", "bone_type", "side",
    "X_Min", "Y_Min", "X_Max", "Y_Max", "X_Bar", "Y_Bar",
    "Salter_Type",
]

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def get_domain(filename):
    return "B" if filename.startswith("B_") else "A"


def extract_salter_type(filename):
    m = re.search(r"(SH_Type_[^_]+(?:_[IVXivx\d]+)?)", filename)
    if m:
        return m.group(1)
    m2 = re.match(r"^B_(.+)_\d{4}\.png$", filename, re.IGNORECASE)
    if m2:
        return m2.group(1)
    return "Unknown"


def make_box(x0, y0, x1, y1):
    x_min = min(x0, x1)
    y_min = min(y0, y1)
    x_max = max(x0, x1)
    y_max = max(y0, y1)
    return {
        "X_Min": x_min,
        "Y_Min": y_min,
        "X_Max": x_max,
        "Y_Max": y_max,
        "X_Bar": int((x_min + x_max) / 2),
        "Y_Bar": int((y_min + y_max) / 2),
    }


class AnnotationState:
    def __init__(self):
        self.base_img      = None
        self.domain        = "A"
        self.salter_type   = "Normal"
        self.boxes         = []
        self.selected_bone = None
        self.is_drawing    = False
        self.drag_start    = (0, 0)
        self.drag_current  = (0, 0)

    def set_image(self, img, filename):
        self.base_img    = img.copy()
        self.domain      = get_domain(filename)
        self.salter_type = extract_salter_type(filename) if self.domain == "B" else "Normal"
        self.reset()

    def reset(self):
        self.boxes         = []
        self.selected_bone = None
        self.is_drawing    = False
        self.drag_start    = (0, 0)
        self.drag_current  = (0, 0)

    @property
    def required_boxes(self):
        return 1 if self.domain == "B" else 2

    @property
    def box_ready(self):
        return len(self.boxes) >= self.required_boxes

    @property
    def current_display(self):
        canvas = self.base_img.copy()
        for i, box in enumerate(self.boxes):
            if self.domain == "A":
                color = COLOR_FEMUR if i == 0 else COLOR_TIBIA
            elif self.selected_bone == "Femur":
                color = COLOR_FEMUR
            elif self.selected_bone == "Tibia":
                color = COLOR_TIBIA
            else:
                color = COLOR_GOLD
            pt1 = (box["X_Min"], box["Y_Min"])
            pt2 = (box["X_Max"], box["Y_Max"])
            ctr = (box["X_Bar"], box["Y_Bar"])
            cv2.rectangle(canvas, pt1, pt2, color, BOX_THICKNESS)
            cv2.circle(canvas, ctr, CENTROID_RADIUS, color, CENTROID_THICKNESS)
        if self.is_drawing and len(self.boxes) < self.required_boxes:
            x0, y0 = self.drag_start
            x1, y1 = self.drag_current
            cv2.rectangle(canvas, (x0, y0), (x1, y1), COLOR_DRAG, BOX_THICKNESS)
        return canvas


state = AnnotationState()


def mouse_callback(event, x, y, flags, param):
    if len(state.boxes) >= state.required_boxes:
        return
    if event == cv2.EVENT_LBUTTONDOWN:
        state.is_drawing   = True
        state.drag_start   = (x, y)
        state.drag_current = (x, y)
    elif event == cv2.EVENT_MOUSEMOVE:
        if state.is_drawing:
            state.drag_current = (x, y)
            redraw()
    elif event == cv2.EVENT_LBUTTONUP:
        if not state.is_drawing:
            return
        state.is_drawing = False
        x0, y0 = state.drag_start
        if abs(x - x0) < 3 and abs(y - y0) < 3:
            return
        state.boxes.append(make_box(x0, y0, x, y))
        redraw()


def put_text_with_shadow(img, text, pos, scale=FONT_SCALE, color=COLOR_TEXT, thickness=FONT_THICKNESS):
    sx, sy = pos[0] + 1, pos[1] + 1
    cv2.putText(img, text, (sx, sy), FONT, scale, COLOR_SHADOW, thickness + 1, cv2.LINE_AA)
    cv2.putText(img, text, pos,      FONT, scale, color,        thickness,     cv2.LINE_AA)


def redraw():
    canvas  = state.current_display
    h       = canvas.shape[0]
    n_boxes = len(state.boxes)

    if state.domain == "A":
        if n_boxes == 0:
            put_text_with_shadow(canvas, "1. Draw Femur box", (8, 22))
            put_text_with_shadow(canvas, "2. Draw Tibia box", (8, 42), color=COLOR_DIM)
        elif n_boxes == 1:
            put_text_with_shadow(canvas, "Femur: done",       (8, 22), color=COLOR_FEMUR)
            put_text_with_shadow(canvas, "2. Draw Tibia box", (8, 42))
        else:
            put_text_with_shadow(canvas, "Femur: done",       (8, 22), color=COLOR_FEMUR)
            put_text_with_shadow(canvas, "Tibia: done",       (8, 42), color=COLOR_TIBIA)
        put_text_with_shadow(canvas, "ENTER/SPACE=save  R=reset  Q/ESC=quit", (8, h - 8), scale=0.45)

    else:
        sh_label = state.salter_type
        if n_boxes == 0:
            put_text_with_shadow(canvas, f"[{sh_label}] Draw a box around the fracture.", (8, 22))
            put_text_with_shadow(canvas, "Then press F=Femur  or  T=Tibia", (8, 42), color=COLOR_DIM)
        elif n_boxes == 1 and state.selected_bone is None:
            put_text_with_shadow(canvas, f"[{sh_label}] Box drawn!", (8, 22))
            put_text_with_shadow(canvas, "Press  F = Femur   or   T = Tibia", (8, 42), color=COLOR_GOLD)
        else:
            bone_color = COLOR_FEMUR if state.selected_bone == "Femur" else COLOR_TIBIA
            put_text_with_shadow(canvas, f"[{sh_label}] Selected: {state.selected_bone}", (8, 22), color=bone_color)
            put_text_with_shadow(canvas, "Press  M=Medial   L=Lateral   U=Unknown  to save", (8, 42), color=COLOR_GOLD)
        put_text_with_shadow(canvas, "R=reset  Q/ESC=quit", (8, h - 8), scale=0.45)

    cv2.imshow(WINDOW_NAME, canvas)


def load_existing_csv():
    if not os.path.exists(OUTPUT_CSV):
        return pd.DataFrame(columns=CSV_COLUMNS), set()
    try:
        df = pd.read_csv(OUTPUT_CSV)
        if "X_Min" not in df.columns or "side" not in df.columns:
            print(
                f"[WARN] '{OUTPUT_CSV}' uses an old schema (missing 'X_Min' or 'side').\n"
                f"       Starting fresh. The original file has NOT been deleted."
            )
            return pd.DataFrame(columns=CSV_COLUMNS), set()
        if not set(CSV_COLUMNS).issubset(df.columns):
            missing = set(CSV_COLUMNS) - set(df.columns)
            print(f"[WARN] '{OUTPUT_CSV}' is missing columns: {missing}. Starting fresh.")
            return pd.DataFrame(columns=CSV_COLUMNS), set()
        df = df[CSV_COLUMNS]
        done = set(zip(df["folder_name"], df["filename"]))
        print(f"[INFO] Resuming — {len(done)} image(s) already annotated.")
        return df, done
    except Exception as exc:
        print(f"[WARN] Could not read existing CSV ({exc}) — starting fresh.")
        return pd.DataFrame(columns=CSV_COLUMNS), set()


def _build_row(folder_name, filename, bone_type, side, box, salter_type):
    return {
        "folder_name": folder_name,
        "filename":    filename,
        "bone_type":   bone_type,
        "side":        side,
        "X_Min":       box["X_Min"],
        "Y_Min":       box["Y_Min"],
        "X_Max":       box["X_Max"],
        "Y_Max":       box["Y_Max"],
        "X_Bar":       box["X_Bar"],
        "Y_Bar":       box["Y_Bar"],
        "Salter_Type": salter_type,
    }


def append_rows(df, folder_name, filename, salter_type, bone_type, side, boxes):
    if len(boxes) == 2:
        new_rows = pd.DataFrame([
            _build_row(folder_name, filename, "Femur", "N/A", boxes[0], salter_type),
            _build_row(folder_name, filename, "Tibia", "N/A", boxes[1], salter_type),
        ])
    else:
        new_rows = pd.DataFrame([
            _build_row(folder_name, filename, bone_type, side, boxes[0], salter_type),
        ])
    return pd.concat([df, new_rows], ignore_index=True)


def _do_save_domain_b(df, folder_name, filename, side, already_done):
    box = state.boxes[0]
    df = append_rows(df, folder_name, filename,
                     salter_type=state.salter_type,
                     bone_type=state.selected_bone,
                     side=side,
                     boxes=state.boxes)
    df.to_csv(OUTPUT_CSV, index=False)
    already_done.add((folder_name, filename))
    print(
        f"[SAVED] {folder_name}/{filename}  bone={state.selected_bone}  side={side}  "
        f"box=({box['X_Min']},{box['Y_Min']})-({box['X_Max']},{box['Y_Max']})  "
        f"centroid=({box['X_Bar']},{box['Y_Bar']})  Salter_Type={state.salter_type}  →  {OUTPUT_CSV}"
    )
    return df


def collect_images(root, subfolders):
    items = []
    for sf in subfolders:
        folder_path = os.path.join(root, sf)
        if not os.path.isdir(folder_path):
            print(f"[WARN] Subfolder not found, skipping: {folder_path}")
            continue
        for fname in sorted(os.listdir(folder_path)):
            if "_aug_" in fname:
                continue
            if os.path.splitext(fname)[1].lower() not in SUPPORTED_EXTS:
                continue
            items.append((sf, os.path.join(folder_path, fname)))
    return items


def main():
    if not os.path.isdir(ROOT_DIR):
        print(f"[ERROR] Root directory not found: {ROOT_DIR}")
        sys.exit(1)

    all_images = collect_images(ROOT_DIR, SUBFOLDERS)
    if not all_images:
        print("[ERROR] No valid images found. Check ROOT_DIR and SUBFOLDERS.")
        sys.exit(1)

    total = len(all_images)
    print(f"[INFO] Found {total} valid image(s) across {len(SUBFOLDERS)} subfolder(s).")

    df, already_done = load_existing_csv()

    folder_totals   = {}
    folder_counters = {}
    for sf, _ in all_images:
        folder_totals[sf]   = folder_totals.get(sf, 0) + 1
        folder_counters[sf] = 0

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 512, 512)
    cv2.setMouseCallback(WINDOW_NAME, mouse_callback)

    global_idx     = 0
    quit_requested = False

    for folder_name, full_path in all_images:
        filename = os.path.basename(full_path)
        folder_counters[folder_name] += 1
        f_idx   = folder_counters[folder_name]
        f_total = folder_totals[folder_name]

        if (folder_name, filename) in already_done:
            print(f"[SKIP] {folder_name}/{filename}  (already annotated)")
            continue

        try:
            raw = np.fromfile(full_path, dtype=np.uint8)
            img = cv2.imdecode(raw, cv2.IMREAD_COLOR)
        except Exception as exc:
            print(f"[WARN] Exception reading {full_path}: {exc}")
            img = None
        if img is None:
            print(f"[WARN] Cannot decode image, skipping: {full_path}")
            continue

        global_idx += 1
        domain = get_domain(filename)
        print(
            f"\n[INFO] [{domain}] Processing {folder_name}: {f_idx}/{f_total}  |  "
            f"Global {global_idx}/{total}  —  {filename}"
        )

        state.set_image(img, filename)
        redraw()

        while True:
            key = cv2.waitKey(20) & 0xFF

            if key == 255:
                if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                    quit_requested = True
                    break
                continue

            if key in (ord('r'), ord('R')):
                state.reset()
                print("[INFO] Reset: all boxes and bone selection cleared.")
                redraw()
                continue

            if key in (ord('q'), ord('Q'), 27):
                print("\n[INFO] Quit requested — all progress already saved.")
                quit_requested = True
                break

            if domain == "A" and key in (13, 32):
                if not state.box_ready:
                    needed    = state.required_boxes - len(state.boxes)
                    next_bone = "Femur" if len(state.boxes) == 0 else "Tibia"
                    print(f"[WARN] Need {needed} more box(es). Next: draw the {next_bone} bounding box.")
                    continue
                df = append_rows(df, folder_name, filename,
                                 salter_type="Normal", bone_type=None,
                                 side="N/A", boxes=state.boxes)
                df.to_csv(OUTPUT_CSV, index=False)
                already_done.add((folder_name, filename))
                fb, tb = state.boxes[0], state.boxes[1]
                print(
                    f"[SAVED] {folder_name}/{filename}  "
                    f"Femur=({fb['X_Bar']},{fb['Y_Bar']})  "
                    f"Tibia=({tb['X_Bar']},{tb['Y_Bar']})  "
                    f"side=N/A  Salter_Type=Normal  →  {OUTPUT_CSV}"
                )
                break

            if domain == "B" and key in (ord('f'), ord('F')):
                if not state.box_ready:
                    print("[WARN] Draw a bounding box first, then press F or T.")
                    continue
                state.selected_bone = "Femur"
                print("[INFO] Bone → Femur. Now press M (Medial), L (Lateral), or U (Unknown) to save.")
                redraw()
                continue

            if domain == "B" and key in (ord('t'), ord('T')):
                if not state.box_ready:
                    print("[WARN] Draw a bounding box first, then press F or T.")
                    continue
                state.selected_bone = "Tibia"
                print("[INFO] Bone → Tibia. Now press M (Medial), L (Lateral), or U (Unknown) to save.")
                redraw()
                continue

            if domain == "B" and key in (ord('m'), ord('M')):
                if state.selected_bone is None:
                    print("[WARN] Select a bone first (F or T), then press M, L, or U.")
                    continue
                df = _do_save_domain_b(df, folder_name, filename, side="Medial", already_done=already_done)
                break

            if domain == "B" and key in (ord('l'), ord('L')):
                if state.selected_bone is None:
                    print("[WARN] Select a bone first (F or T), then press M, L, or U.")
                    continue
                df = _do_save_domain_b(df, folder_name, filename, side="Lateral", already_done=already_done)
                break

            if domain == "B" and key in (ord('u'), ord('U')):
                if state.selected_bone is None:
                    print("[WARN] Select a bone first (F or T), then press M, L, or U.")
                    continue
                df = _do_save_domain_b(df, folder_name, filename, side="Unknown", already_done=already_done)
                break

        if quit_requested:
            break

    cv2.destroyAllWindows()
    total_annotated = len(df["filename"].unique()) if not df.empty else 0
    print(f"\n[DONE] Session ended.  Total annotated images in CSV: {total_annotated}  |  File: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()