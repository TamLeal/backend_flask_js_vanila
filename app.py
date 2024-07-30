from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

# # Configuração do Supabase
# SUPABASE_URL = "SUA_SUPABASE_URL"  # Substitua pela sua URL do Supabase
# SUPABASE_KEY = "SUA_SUPABASE_CHAVE_API"  # Substitua pela sua chave API do Supabase
# BUCKET_NAME = "nome_do_seu_bucket"  # Substitua pelo nome do seu bucket no Supabase

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
            # Abre a imagem usando PIL
            image = Image.open(file.stream)
            width, height = image.size

            # Converte a imagem para bytes
            image_bytes = io.BytesIO()
            image.save(image_bytes, format=image.format)
            image_bytes = image_bytes.getvalue()

            # Nome do arquivo e caminho no bucket
            filename = file.filename
            path = f"images/{filename}"

            # Upload para o Supabase
            response = supabase.storage().from_(BUCKET_NAME).upload(path, image_bytes)
            if response.get('error'):
                return jsonify({'error': response['error']['message']}), 500

            # Obtém a URL pública ou assinada
            public_url = supabase.storage().from_(BUCKET_NAME).get_public_url(path)

            return jsonify({'width': width, 'height': height, 'url': public_url}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'File processing error'}), 500


if __name__ == '__main__':
    app.run(debug=True)






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
