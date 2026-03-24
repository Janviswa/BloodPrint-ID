import h5py
import numpy as np

H5_PATH = 'bloodprint_efficientnet.h5'

def inspect_h5(path):
    with h5py.File(path, 'r') as f:
        print("=== TOP LEVEL KEYS ===")
        print(list(f.keys()))

        print("\n=== ATTRIBUTES ===")
        for k, v in f.attrs.items():
            print(f"  {k}: {v}")

        print("\n=== STRUCTURE (first 3 levels) ===")
        def print_tree(name, obj):
            depth = name.count('/')
            if depth > 3:
                return
            indent = '  ' * depth
            if isinstance(obj, h5py.Dataset):
                print(f"{indent}📄 {name}  shape={obj.shape}  dtype={obj.dtype}")
            else:
                print(f"{indent}📁 {name}/")
        f.visititems(print_tree)

        print("\n=== WEIGHT COUNT CHECK ===")
        total_arrays = [0]
        total_params = [0]
        def count_weights(name, obj):
            if isinstance(obj, h5py.Dataset) and len(obj.shape) > 0:
                total_arrays[0] += 1
                total_params[0] += int(np.prod(obj.shape))
        f.visititems(count_weights)
        print(f"  Total weight arrays : {total_arrays[0]}")
        print(f"  Total parameters    : {total_params[0]:,}")

        if total_params[0] > 1_000_000:
            print("  ✅ File contains real weights (>1M params)")
        else:
            print("  ❌ File has almost no weights — model was saved without weights")

inspect_h5(H5_PATH)