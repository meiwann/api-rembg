from flask import Flask, request, send_file, jsonify
from rembg import remove
from PIL import Image
import io
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/rembg', methods=['POST'])
def remove_background():
    try:
        if 'image' not in request.files:
            logger.error('No image provided in request')
            return jsonify({'error': 'No image provided'}), 400

        image_file = request.files['image']
        
        if image_file.filename == '':
            logger.error('Empty filename')
            return jsonify({'error': 'No image selected'}), 400

        logger.info(f'Processing image: {image_file.filename}')
        
        # Step 1: Open image with PIL and convert to RGB
        input_image = Image.open(image_file.stream).convert("RGB")
        
        # Step 2: Convert to bytes (PNG format)
        img_byte_arr = io.BytesIO()
        input_image.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()

        # Step 3: Remove background using rembg (input: bytes)
        img_no_bg_bytes = remove(img_bytes)

        # Step 4: Convert output bytes back to PIL image
        output_image = Image.open(io.BytesIO(img_no_bg_bytes)).convert("RGB")

        # Step 5: Resize to 224x224
        output_image = output_image.resize((224, 224))

        # Step 6: Convert back to bytes for response
        byte_io = io.BytesIO()
        output_image.save(byte_io, 'PNG', optimize=True)
        byte_io.seek(0)

        logger.info('Background removal completed and resized to 224x224')

        return send_file(
            byte_io, 
            mimetype='image/png',
            as_attachment=False,
            download_name='processed_image.png'
        )

    except Exception as e:
        logger.error(f'Error processing image: {str(e)}')
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
