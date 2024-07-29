from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

@app.route('/api/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['image']
    if file:
        try:
            # Abre a imagem usando PIL
            image = Image.open(file.stream)
            width, height = image.size
            return jsonify({'width': width, 'height': height}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'File processing error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
