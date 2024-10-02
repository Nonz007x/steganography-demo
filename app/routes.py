from flask import Flask, request, jsonify, send_file  # type: ignore
from flask_cors import CORS  # type: ignore
from functions import lsb_encode, lsb_decode, itoa
from io import BytesIO

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}) 

@app.route("/")
def hello_world():
  return "<h1>Hello, World!</h1>"

@app.route("/lsb-encode", methods=['POST'])
def lsb_encode_route():
  data = request.get_json()
  text = data.get("message")
  image_data = data.get("image")

  result_image = lsb_encode(text, image_data)

  img_byte_arr = BytesIO()
  result_image.save(img_byte_arr, format='PNG') 
  img_byte_arr.seek(0)

  return send_file(img_byte_arr, mimetype='image/png')
  
@app.route("/lsb-decode", methods=['POST'])
def lsb_decode_route():
  data = request.get_json()
  image = data.get('image')
  
  int_arr = lsb_decode(image)
  decoded_message = itoa(int_arr)
  
  return jsonify({'message': decoded_message})

if __name__ == "__main__":
  app.run(debug=True)
