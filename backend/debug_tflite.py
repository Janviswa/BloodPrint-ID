import numpy as np
import tensorflow as tf

interp = tf.lite.Interpreter('model.tflite')
interp.allocate_tensors()

inp_det = interp.get_input_details()[0]
out_det = interp.get_output_details()[0]

print("=== INPUT ===")
print("dtype      :", inp_det['dtype'])
print("shape      :", inp_det['shape'])
print("quantization:", inp_det.get('quantization'))

print("\n=== OUTPUT ===")
print("dtype      :", out_det['dtype'])
print("shape      :", out_det['shape'])
print("quantization:", out_det.get('quantization'))

# Test with random input
np.random.seed(42)
dummy = np.random.uniform(-1, 1, (1, 224, 224, 3)).astype(np.float32)

# Handle quantized input
if inp_det['dtype'] == np.uint8:
    scale, zp = inp_det['quantization']
    dummy = np.clip(np.round(dummy / scale + zp), 0, 255).astype(np.uint8)
    print("\n⚠️  Input is UINT8 quantized")
elif inp_det['dtype'] == np.int8:
    scale, zp = inp_det['quantization']
    dummy = np.clip(np.round(dummy / scale + zp), -128, 127).astype(np.int8)
    print("\n⚠️  Input is INT8 quantized")
else:
    print("\n✅ Input is FLOAT32")

interp.set_tensor(inp_det['index'], dummy)
interp.invoke()
raw = interp.get_tensor(out_det['index'])[0]

print("\n=== RAW OUTPUT ===")
print("raw values :", raw)
print("raw dtype  :", raw.dtype)

# Dequantize if needed
if out_det['dtype'] in (np.uint8, np.int8):
    scale, zp = out_det['quantization']
    preds = (raw.astype(np.float32) - zp) * scale
    print("\n⚠️  Output is quantized — dequantized:", preds)
else:
    preds = raw.astype(np.float32)
    print("\n✅ Output is FLOAT32:", preds)

print("\n=== DIAGNOSIS ===")
classes = ['loop', 'whorl', 'arch']
print(f"Predicted class : {classes[np.argmax(preds)]}  ({np.max(preds)*100:.1f}%)")

if all(abs(p - preds[0]) < 0.01 for p in preds):
    print("❌ UNIFORM output — model is broken or conversion failed")
    print("   → Re-run convert_model.py to regenerate model.tflite")
else:
    print("✅ Model output varies — conversion is OK")
    print("   → Check predictor.py dequantization logic")