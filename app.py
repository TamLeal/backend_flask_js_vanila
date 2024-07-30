from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
from supabase import create_client, Client
import os

app = Flask(__name__)
CORS(app)

# Carregar variáveis de ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")

if not SUPABASE_URL or not SUPABASE_KEY or not BUCKET_NAME:
    raise ValueError("Variáveis de ambiente não configuradas corretamente.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Server is running!'}), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'message': 'Backend is running!'}), 200

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
            if response.status_code != 200:
                return jsonify({'error': response.json().get('message', 'Unknown error')}), 500
            
            public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(path)
            return jsonify({'width': width, 'height': height, 'url': public_url}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'File processing error'}), 500

@app.route('/api/remove_image', methods=['POST'])
def remove_image():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        # Extract the path from the URL
        path = url.split(f"{BUCKET_NAME}/")[-1]
        
        # Remove the file from Supabase storage
        response = supabase.storage.from_(BUCKET_NAME).remove([path])
        
        if response:
            return jsonify({'success': True, 'message': 'Image removed successfully'}), 200
        else:
            return jsonify({'error': 'Failed to remove image'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_images', methods=['GET'])
def get_images():
    try:
        # List all files in the bucket
        response = supabase.storage.from_(BUCKET_NAME).list()
        
        images = []
        for item in response:
            if item['name'].lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                url = supabase.storage.from_(BUCKET_NAME).get_public_url(item['name'])
                images.append({
                    'url': url,
                    'name': item['name'],
                    # Note: We can't get dimensions here without downloading each image,
                    # which would be inefficient. You might want to store this metadata
                    # separately when uploading.
                })
        
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
