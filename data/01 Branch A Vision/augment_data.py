import os
import cv2
import numpy as np

DATASET_ROOT   = r"C:\Data Collection\CycleGAN_Dataset"
TARGET_FOLDERS = ["trainA", "trainB"]
IMAGE_EXTS     = {".png", ".jpg", ".jpeg"}
CANVAS_SIZE    = 256

CB_ALPHA = 1.2
CB_BETA  = -10


def aug_flip(img):
    return cv2.flip(img, 1)


def aug_rotate(img, degrees):
    cx, cy = CANVAS_SIZE // 2, CANVAS_SIZE // 2
    M      = cv2.getRotationMatrix2D((cx, cy), degrees, scale=1.0)
    return cv2.warpAffine(
        img, M, (CANVAS_SIZE, CANVAS_SIZE),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0),
    )


def aug_contrast(img):
    return cv2.convertScaleAbs(img, alpha=CB_ALPHA, beta=CB_BETA)


AUGMENTATIONS = [
    ("_aug_flip",     lambda img: aug_flip(img)),
    ("_aug_rot_p5",   lambda img: aug_rotate(img, +5.0)),
    ("_aug_rot_m5",   lambda img: aug_rotate(img, -5.0)),
    ("_aug_contrast", lambda img: aug_contrast(img)),
]


def collect_originals(folder):
    originals = []
    for fname in sorted(os.listdir(folder)):
        if "_aug_" in fname:
            continue
        if os.path.splitext(fname)[1].lower() not in IMAGE_EXTS:
            continue
        originals.append(os.path.join(folder, fname))
    return originals


def augment_folder(folder):
    originals = collect_originals(folder)
    n_orig    = len(originals)

    if n_orig == 0:
        print(f"  [WARN] No original images found — skipping.")
        return 0, 0

    print(f"  Found {n_orig} original image(s).  "
          f"Generating {n_orig * len(AUGMENTATIONS)} augmented files ...")

    saved   = 0
    skipped = 0

    for src_path in originals:
        img = cv2.imread(src_path, cv2.IMREAD_COLOR)

        if img is None:
            print(f"  [SKIP] Unreadable: {os.path.basename(src_path)}")
            skipped += 1
            continue

        stem, ext = os.path.splitext(os.path.basename(src_path))

        for suffix, transform in AUGMENTATIONS:
            try:
                aug_img  = transform(img)
                out_name = f"{stem}{suffix}.png"
                out_path = os.path.join(folder, out_name)

                if not cv2.imwrite(out_path, aug_img):
                    print(f"  [ERROR] Could not write: {out_name}")
                    continue

                saved += 1

            except Exception as exc:
                print(f"  [ERROR] {suffix} failed for "
                      f"{os.path.basename(src_path)}: {exc}")

    if skipped:
        print(f"  [WARN] {skipped} source file(s) were unreadable and skipped.")

    return n_orig, saved


def main():
    print("=" * 62)
    print("  CycleGAN X-Ray Offline Augmentation")
    print("=" * 62)
    print(f"  Dataset root : {DATASET_ROOT}")
    print(f"  Targets      : {', '.join(TARGET_FOLDERS)}")
    print(f"  Augmentations: {', '.join(s for s, _ in AUGMENTATIONS)}")
    print("=" * 62 + "\n")

    grand_orig = 0
    grand_aug  = 0

    for folder_name in TARGET_FOLDERS:
        folder_path = os.path.join(DATASET_ROOT, folder_name)

        print(f"[FOLDER] {folder_name}  →  {folder_path}")

        if not os.path.isdir(folder_path):
            print(f"  [ERROR] Directory not found — skipping.\n")
            continue

        n_orig, n_aug = augment_folder(folder_path)
        grand_orig   += n_orig
        grand_aug    += n_aug

        print(f"  Done: {n_aug} file(s) written.\n")

    print("=" * 62)
    print("  Augmentation complete!")
    print(f"  Total original images processed : {grand_orig}")
    print(f"  Total augmented images generated: {grand_aug}")
    print(f"  Effective dataset size increase : "
          f"{grand_orig} → {grand_orig + grand_aug} images "
          f"(×{1 + len(AUGMENTATIONS)})")
    print("=" * 62)


if __name__ == "__main__":
    main()