import rsa, os, xml.etree.ElementTree as ET
from sqlalchemy import func, Column, Integer, String, BigInteger, Date, Time
from datetime import datetime
from werkzeug.utils import secure_filename

from flask import Flask, request, jsonify, current_app, Response, send_file
from flask_sqlalchemy import SQLAlchemy #, Column, Integer, String, BigInteger, Date, Time, func
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_bcrypt import Bcrypt

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DEVELOPMENT_DATABASE_URI')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY') 

db = SQLAlchemy(app)
jwt = JWTManager(app)

(pubkey, privkey) = rsa.newkeys(512)

class User(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    plan_id = Column(Integer, nullable=True)
    password = Column(String(256), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone_number = data.get('phone_number')
    plan_id = data.get('plan_id')  
    password = data.get('password')
    
    if not all([name, email, phone_number, password]):
        return jsonify({'message': 'name, email, phone_number, and password are required fields'}), 400

    user_exists = User.query.filter_by(email=email).first()
    if user_exists:
        return jsonify({'message': 'A user with this email already exists'}), 400

    # Hash the password before saving it to the database
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    user = User(name=name, email=email, phone_number=phone_number, plan_id=plan_id, password=hashed_password)

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Registration successful'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')  # Assuming this is the plaintext password sent from the client

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Use bcrypt to check the password against its hashed version
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Incorrect password'}), 401

    # Create a new token and send it as a response
    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token), 200



@app.route('/plan_selection', methods=['POST'])
@jwt_required()  # Protect this route so only users with valid tokens can access it
def plan_selection():
    current_user_email = get_jwt_identity()  # Getting the user's email from the token
    
    # Parsing XML from the request data
    try:
        root = ET.fromstring(request.data)
    except ET.ParseError:
        return jsonify({"message": "Invalid XML provided"}), 400
    
    # Extracting plan_id from the XML
    plan_id = root.find('plan_id').text if root.find('plan_id') is not None else None
    
    if not plan_id:
        return jsonify({"message": "plan_id is required in the XML body"}), 400
    
    # Fetching the user and updating the plan using the email from the token
    user = User.query.filter_by(email=current_user_email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    user.plan_id = plan_id
    db.session.commit()

    return Response("<message>Plan selection successful</message>", mimetype='text/xml')  # Responding with XML

@app.route('/update_email', methods=['POST'])
@jwt_required()
def update_email():
    current_user_email = get_jwt_identity()

    try:
        root = ET.fromstring(request.data)
    except ET.ParseError:
        return jsonify({"message": "Invalid XML provided"}), 400

    new_email = root.find('new_email').text if root.find('new_email') is not None else None

    if not new_email:
        return jsonify({"message": "new_email is required in the XML body"}), 400

    user = User.query.filter_by(email=current_user_email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    # Check if the new email is already in use
    existing_user_with_new_email = User.query.filter_by(email=new_email).first()
    if existing_user_with_new_email:
        return jsonify({"message": "The new email is already in use"}), 400

    user.email = new_email
    db.session.commit()

    return Response("<message>Email updated successfully</message>", mimetype='text/xml')

@app.route('/update_password', methods=['POST'])
@jwt_required()
def update_password():
    current_user_email = get_jwt_identity()

    try:
        root = ET.fromstring(request.data)
    except ET.ParseError:
        return jsonify({"message": "Invalid XML provided"}), 400

    new_password = root.find('new_password').text if root.find('new_password') is not None else None

    if not new_password:
        return jsonify({"message": "new_password is required in the XML body"}), 400

    user = User.query.filter_by(email=current_user_email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Hash the new password before saving it to the database, consistent with the register method
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    user.password = hashed_password

    db.session.commit()

    return Response("<message>Password updated successfully</message>", mimetype='text/xml')

@app.route('/download_call_records/<file_size>', methods=['GET'])
@jwt_required()
def download_call_records(file_size):
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    # Map the user input to the corresponding filename
    file_name = f"{file_size}.zip"

    # Create the full path to the file
    file_path = os.path.join(current_app.root_path, 'files', 'download', file_name)

    # Check if the file exists
    if not os.path.exists(file_path):
        return jsonify({"message": f"File {file_name} not found"}), 404

    # Get current timestamp and format it
    current_time = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    download_name = f'{user.id}_call_records_{current_time}_{file_size}.zip'

    return send_file(file_path, as_attachment=True, download_name=download_name)



UPLOAD_FOLDER = 'files/uploaded_files'  # folder where you save the files
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip'}  # allowed file extensions
#app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Function to check if the file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['file']

    # if user does not select file, browser might submit an empty part without filename
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    if file:
        # Generate a unique filename using timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        filename = secure_filename(file.filename)
        new_filename = f"{timestamp}_{filename}"
        
        # Save the file to the upload directory
        file.save(os.path.join(UPLOAD_FOLDER, new_filename))
        
        return jsonify({"message": "File uploaded successfully", "filename": new_filename}), 200



class MobileTraffic(db.Model):
    id_0 = Column(BigInteger, primary_key=True)
    id_a = Column(BigInteger)
    id_b = Column(BigInteger)
    start_time_local = Column(Time)
    time_zone = Column(Integer)
    duration = Column(Integer)
    forward = Column(Integer)
    zero_call_flg = Column(Integer)
    source_b = Column(Integer)
    source_f = Column(Integer)
    num_b_length = Column(Integer)
    time_key = Column(Date)

@app.route('/get_random_mobile_traffic', methods=['GET'])
def get_random_mobile_traffic():
    random_rows = MobileTraffic.query.order_by(func.random()).limit(200).all()
    results = [
        {
            "id_0": row.id_0,
            "id_a": row.id_a,
            "id_b": row.id_b,
            "start_time_local": str(row.start_time_local),
            "time_zone": row.time_zone,
            "duration": row.duration,
            "forward": row.forward,
            "zero_call_flg": row.zero_call_flg,
            "source_b": row.source_b,
            "source_f": row.source_f,
            "num_b_length": row.num_b_length,
            "time_key": str(row.time_key)
        }
        for row in random_rows
    ]
    return jsonify(results)


HOST = os.getenv('HOST', '0.0.0.0') # Default to '0.0.0.0' if not set
DEBUG_MODE = os.getenv('DEBUG', 'False').lower() == 'true' # Convert to boolean, default to False
PORT = int(os.getenv('PORT', 5000)) # Default to 5000 if not set

if __name__ == "__main__":
    app.run(host=HOST, debug=DEBUG_MODE, port=PORT)

