import os
import random
import cv2
import numpy as np

SOURCE_NORMAL   = r"C:\Data Collection\Normal_Age"
SOURCE_FRACTURE = r"C:\Data Collection\Knee_Fracture"
OUTPUT_ROOT     = r"C:\Data Collection\CycleGAN_Dataset"

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
TARGET_SIZE      = (256, 256)
TRAIN_RATIO      = 0.85
RANDOM_SEED      = 42


def create_output_dirs(root):
    subdirs = ["trainA", "testA", "trainB", "testB"]
    paths = {}
    for name in subdirs:
        path = os.path.join(root, name)
        os.makedirs(path, exist_ok=True)
        paths[name] = path
    print(f"[DIR] Output directories ready under: {root}\n")
    return paths


def collect_image_paths(source_dir):
    found = []
    for dirpath, _, filenames in os.walk(source_dir):
        for fname in filenames:
            if os.path.splitext(fname)[1].lower() in IMAGE_EXTENSIONS:
                found.append(os.path.join(dirpath, fname))
    return found


def load_and_preprocess(filepath):
    try:
        raw = np.fromfile(filepath, dtype=np.uint8)
        img = cv2.imdecode(raw, cv2.IMREAD_UNCHANGED)
    except Exception:
        img = None

    if img is None:
        return None

    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    elif img.shape[2] == 1:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    target_px = TARGET_SIZE[0]
    h, w      = img.shape[:2]
    scale     = target_px / max(h, w)
    new_w     = int(round(w * scale))
    new_h     = int(round(h * scale))

    interp = cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR
    img    = cv2.resize(img, (new_w, new_h), interpolation=interp)

    canvas   = np.zeros((target_px, target_px, 3), dtype=np.uint8)
    pad_top  = (target_px - new_h) // 2
    pad_left = (target_px - new_w) // 2
    canvas[pad_top : pad_top + new_h, pad_left : pad_left + new_w] = img

    return canvas


def split_paths(paths, train_ratio, seed):
    random.seed(seed)
    shuffled = paths[:]
    random.shuffle(shuffled)
    cut = int(len(shuffled) * train_ratio)
    return shuffled[:cut], shuffled[cut:]


def process_domain(source_dir, train_dir, test_dir, prefix):
    print(f"{'─'*60}")
    print(f"[{prefix}] Scanning: {source_dir}")

    all_paths = collect_image_paths(source_dir)
    if not all_paths:
        print(f"[{prefix}] WARNING: No images found in {source_dir}. Skipping.\n")
        return

    print(f"[{prefix}] Found {len(all_paths)} image file(s).")

    train_paths, test_paths = split_paths(all_paths, TRAIN_RATIO, RANDOM_SEED)
    print(f"[{prefix}] Split → train: {len(train_paths)}  |  test: {len(test_paths)}")

    saved_train = _save_batch(train_paths, train_dir, prefix, start_index=1)
    saved_test  = _save_batch(test_paths,  test_dir,  prefix, start_index=saved_train + 1)

    total_saved = saved_train + saved_test
    skipped     = len(all_paths) - total_saved

    print(f"[{prefix}] Saved  → trainA/B: {saved_train}  |  testA/B: {saved_test}")
    if skipped:
        print(f"[{prefix}] Skipped (corrupt / unreadable): {skipped}")
    print()


def _save_batch(paths, dest_dir, prefix, start_index):
    saved = 0
    idx   = start_index

    for src_path in paths:
        try:
            img = load_and_preprocess(src_path)
            if img is None:
                print(f"  [SKIP] Cannot read image: {src_path}")
                continue

            parent_folder = os.path.basename(os.path.dirname(src_path))
            safe_label    = parent_folder.replace(" ", "_")

            if prefix == "B":
                out_name = f"{prefix}_{safe_label}_{idx:04d}.png"
            else:
                out_name = f"{prefix}_{idx:04d}.png"

            out_path = os.path.join(dest_dir, out_name)
            success  = cv2.imwrite(out_path, img)

            if not success:
                print(f"  [SKIP] Failed to write: {out_path}")
                continue

            saved += 1
            idx   += 1

            if saved % 100 == 0:
                print(f"  ... {saved} images processed in this batch so far")

        except Exception as exc:
            print(f"  [ERROR] Unexpected error for {src_path}: {exc}")
            continue

    return saved


def main():
    print("=" * 60)
    print("  CycleGAN Dataset Organizer — Pediatric Knee X-Rays")
    print("=" * 60)
    print(f"  Normal (A)   source : {SOURCE_NORMAL}")
    print(f"  Fracture (B) source : {SOURCE_FRACTURE}")
    print(f"  Output root         : {OUTPUT_ROOT}")
    print(f"  Target size         : {TARGET_SIZE[0]}×{TARGET_SIZE[1]} px")
    print(f"  Train / Test split  : {int(TRAIN_RATIO*100)}% / {int((1-TRAIN_RATIO)*100)}%")
    print("=" * 60 + "\n")

    dirs = create_output_dirs(OUTPUT_ROOT)

    process_domain(
        source_dir=SOURCE_NORMAL,
        train_dir=dirs["trainA"],
        test_dir=dirs["testA"],
        prefix="A",
    )

    process_domain(
        source_dir=SOURCE_FRACTURE,
        train_dir=dirs["trainB"],
        test_dir=dirs["testB"],
        prefix="B",
    )

    print("=" * 60)
    print("  ✓ Dataset organisation complete!")
    print(f"  Output: {OUTPUT_ROOT}")
    for name, path in dirs.items():
        count = len([f for f in os.listdir(path) if f.endswith(".png")])
        print(f"    {name:8s}  →  {count:5d} images")
    print("=" * 60)


if __name__ == "__main__":
    main()