from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os, datetime
from cv_processor import analyze_cv
from pdf_report import generate_pdf_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "../frontend"), template_folder=os.path.join(BASE_DIR, "../frontend"))
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'cv_screenings.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Screening(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jd_name = db.Column(db.String(255))
    must_haves = db.Column(db.String(1000))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    total_cvs = db.Column(db.Integer)
    results = db.relationship('CVResult', backref='screening', lazy=True)

class CVResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    screening_id = db.Column(db.Integer, db.ForeignKey('screening.id'), nullable=False)
    cv_name = db.Column(db.String(255))
    percentage = db.Column(db.Float)
    emoji = db.Column(db.String(10))
    missing_skills = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/screen', methods=['POST'])
def screen():
    jd_file = request.files.get('jd')
    if not jd_file:
        return jsonify({'error':'JD file required'}), 400
    must_haves_raw = request.form.get('must_haves', '')
    must_haves = [m.strip() for m in must_haves_raw.split(',') if m.strip()]

    cvs = request.files.getlist('cvs')
    if not cvs:
        return jsonify({'error':'At least one CV required'}), 400

    jd_filename = secure_filename(jd_file.filename)
    jd_path = os.path.join(app.config['UPLOAD_FOLDER'], jd_filename)
    jd_file.save(jd_path)

    cv_paths = []
    for cv in cvs:
        if cv and allowed_file(cv.filename):
            fn = secure_filename(cv.filename)
            p = os.path.join(app.config['UPLOAD_FOLDER'], fn)
            cv.save(p)
            cv_paths.append(p)

    results = analyze_cv(jd_path, must_haves, cv_paths)

    screening = Screening(jd_name=jd_filename, must_haves=','.join(must_haves), total_cvs=len(cv_paths))
    db.session.add(screening)
    db.session.commit()

    for r in results:
        rec = CVResult(screening_id=screening.id,
                       cv_name=r['cv_name'],
                       percentage=r['percentage'],
                       emoji=r['emoji'],
                       missing_skills=','.join(r['missing_skills']))
        db.session.add(rec)
    db.session.commit()

    return jsonify({'screening_id': screening.id, 'results': results})

@app.route('/records', methods=['GET'])
def records():
    out = []
    screenings = Screening.query.order_by(Screening.date.desc()).all()
    for s in screenings:
        cvs = CVResult.query.filter_by(screening_id=s.id).all()
        out.append({
            'screening_id': s.id,
            'jd_name': s.jd_name,
            'must_haves': s.must_haves,
            'date': s.date.isoformat(),
            'total_cvs': s.total_cvs,
            'cvs': [{'cv_name':c.cv_name,'percentage':c.percentage,'emoji':c.emoji,'missing_skills':c.missing_skills} for c in cvs]
        })
    return jsonify(out)

@app.route('/download_report/<int:screening_id>', methods=['GET'])
def download_report(screening_id):
    screening = Screening.query.get(screening_id)
    if not screening:
        return 'Not found', 404
    cvs = CVResult.query.filter_by(screening_id=screening_id).all()
    pdf_path = generate_pdf_report(screening, cvs)
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
