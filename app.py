from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
from supabase import create_client, Client
import os
import json

app = Flask(__name__)
CORS(app)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")

if not SUPABASE_URL or not SUPABASE_KEY or not BUCKET_NAME:
    raise ValueError("Variáveis de ambiente não configuradas corretamente.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

METADATA_FILE = "image_metadata.json"

def get_metadata():
    try:
        metadata_content = supabase.storage.from_(BUCKET_NAME).download(METADATA_FILE)
        return json.loads(metadata_content.decode('utf-8'))
    except:
        return {}

def save_metadata(metadata):
    supabase.storage.from_(BUCKET_NAME).upload(
        METADATA_FILE,
        json.dumps(metadata).encode('utf-8'),
        {"upsert": True}
    )

@app.route('/api/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['image']
    if file:
        try:
            image = Image.open(file.stream)
            width, height = image.size
            image_bytes = io.BytesIO()
            image.save(image_bytes, format=image.format)
            image_bytes = image_bytes.getvalue()
            
            filename = file.filename
            path = f"images/{filename}"
            
            response = supabase.storage.from_(BUCKET_NAME).upload(path, image_bytes)
            if hasattr(response, 'status_code') and response.status_code != 200:
                return jsonify({'error': response.json().get('message', 'Unknown error')}), 500
            
            public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(path)
            
            metadata = get_metadata()
            metadata[filename] = {
                'width': width,
                'height': height,
                'url': public_url,
                'filename': filename
            }
            save_metadata(metadata)
            
            return jsonify(metadata[filename]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'File processing error'}), 500

@app.route('/api/remove_image', methods=['POST'])
def remove_image():
    data = request.json
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    
    try:
        path = f"images/{filename}"
        supabase.storage.from_(BUCKET_NAME).remove([path])
        
        metadata = get_metadata()
        if filename in metadata:
            del metadata[filename]
            save_metadata(metadata)
        
        return jsonify({'success': True, 'message': 'Image removed successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_images', methods=['GET'])
def get_images():
    try:
        metadata = get_metadata()
        images = list(metadata.values())
        return jsonify(images), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from PIL import Image
# import io
# from supabase import create_client, Client
# import os

# app = Flask(__name__)
# CORS(app)

# # Carregar variáveis de ambiente do ambiente de execução
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# BUCKET_NAME = os.getenv("BUCKET_NAME")

# # Verificar se as variáveis foram carregadas corretamente
# if not SUPABASE_URL or not SUPABASE_KEY or not BUCKET_NAME:
#     raise ValueError("Variáveis de ambiente não configuradas corretamente.")

# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# @app.route('/', methods=['GET'])
# def home():
#     return jsonify({'message': 'Server is running!'}), 200

# @app.route('/api/health', methods=['GET'])
# def health_check():
#     return jsonify({'message': 'Backend is running!'}), 200

# @app.route('/api/upload_image', methods=['POST'])
# def upload_image():
#     if 'image' not in request.files:
#         return jsonify({'error': 'No file uploaded'}), 400
    
#     file = request.files['image']
#     if file:
#         try:
#             # Abre a imagem usando PIL
#             image = Image.open(file.stream)
#             width, height = image.size

#             # Converte a imagem para bytes
#             image_bytes = io.BytesIO()
#             image.save(image_bytes, format=image.format)
#             image_bytes = image_bytes.getvalue()

#             # Nome do arquivo e caminho no bucket
#             filename = file.filename
#             path = f"images/{filename}"

#             # Upload para o Supabase
#             response = supabase.storage.from_(BUCKET_NAME).upload(path, image_bytes)
#             if response.status_code != 200:
#                 return jsonify({'error': response.json().get('message', 'Unknown error')}), 500

#             # Obtém a URL pública
#             public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(path)

#             return jsonify({'width': width, 'height': height, 'url': public_url}), 200
#         except Exception as e:
#             return jsonify({'error': str(e)}), 500

#     return jsonify({'error': 'File processing error'}), 500

# if __name__ == '__main__':
#     app.run(debug=True)





# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from PIL import Image
# import io

# app = Flask(__name__)
# CORS(app)

# @app.route('/', methods=['GET'])
# def home():
#     return jsonify({'message': 'Server is running!'}), 200

# @app.route('/api/health', methods=['GET'])
# def health_check():
#     return jsonify({'message': 'Backend is running!'}), 200

# @app.route('/api/upload_image', methods=['POST'])
# def upload_image():
#     if 'image' not in request.files:
#         return jsonify({'error': 'No file uploaded'}), 400
    
#     file = request.files['image']
#     if file:
#         try:
#             # Abre a imagem usando PIL
#             image = Image.open(file.stream)
#             width, height = image.size
#             return jsonify({'width': width, 'height': height}), 200
#         except Exception as e:
#             return jsonify({'error': str(e)}), 500

#     return jsonify({'error': 'File processing error'}), 500

# if __name__ == '__main__':
#     app.run(debug=True)
