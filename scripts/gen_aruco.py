#!/usr/bin/env python3
"""
Generate printable ArUco markers for IDs used by the tool guidance.
Usage:
  python scripts/gen_aruco.py --ids 23 42 --size 500 --dict DICT_5X5_250 --out out_dir
"""
import argparse
import importlib
from pathlib import Path

import cv2
import numpy as np


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', type=int, nargs='+', default=[23, 42])
    ap.add_argument('--size', type=int, default=500)
    ap.add_argument('--dict', dest='dict_name', type=str, default='DICT_5X5_250')
    ap.add_argument('--out', type=str, default='markers')
    args = ap.parse_args()

    aruco = importlib.import_module('cv2.aruco')
<<<<<<< HEAD
    dictionary = getattr(aruco, args.dict_name, getattr(aruco, 'DICT_5X5_250'))
    dictionary = aruco.getPredefinedDictionary(dictionary)
=======
    # Resolve dictionary constant and instance across API variants
    dict_const = getattr(aruco, args.dict_name, None)
    if dict_const is None:
        dict_const = getattr(aruco, 'DICT_5X5_250')
    dictionary = None
    if hasattr(aruco, 'getPredefinedDictionary'):
        dictionary = aruco.getPredefinedDictionary(dict_const)
    elif hasattr(aruco, 'Dictionary_get'):
        dictionary = aruco.Dictionary_get(dict_const)
    else:
        raise RuntimeError('cv2.aruco dictionary API not found')
>>>>>>> 3fd54b7223d6d85794d599f6829e5349642b0e6f

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    for mid in args.ids:
<<<<<<< HEAD
        img = np.zeros((args.size, args.size), dtype=np.uint8)
        img = aruco.drawMarker(dictionary, int(mid), args.size)
=======
        # Generate marker image with compatibility across OpenCV builds
        img = None
        if hasattr(aruco, 'drawMarker'):
            img = aruco.drawMarker(dictionary, int(mid), args.size)
        elif hasattr(aruco, 'generateImageMarker'):
            img = aruco.generateImageMarker(dictionary, int(mid), args.size)
        else:
            # Fallback: build a 1x1 GridBoard (single marker) and render
            if hasattr(aruco, 'GridBoard_create') and hasattr(aruco, 'Board'):
                board = aruco.GridBoard_create(1, 1, 1.0, 0.1, dictionary)
                # draw method expects pixels; scale grid cell to desired size
                cell = args.size
                border = max(1, int(round(0.1 * cell)))
                canvas = np.full((cell + 2*border, cell + 2*border), 255, dtype=np.uint8)
                try:
                    board.draw((canvas.shape[1], canvas.shape[0]), canvas, marginSize=0, borderBits=1)
                except Exception:
                    # If draw signature differs, try without kwargs
                    board.draw((canvas.shape[1], canvas.shape[0]), canvas)
                # Attempt to crop central marker area; last resort: use canvas
                img = canvas
            else:
                raise RuntimeError('cv2.aruco draw API not available')
>>>>>>> 3fd54b7223d6d85794d599f6829e5349642b0e6f
        out_path = out_dir / f'aruco_{mid}.png'
        cv2.imwrite(str(out_path), img)
        print(f'Wrote {out_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
