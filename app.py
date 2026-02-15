import os 
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user 
import google.generativeai as genai 



# --- إعدادات Gemini AI ---
GEMINI_API_KEY = "AIzaSyB0xTDwW71QdWdjOR2ykIWw5XwI9-SMWh8" 
try:
    genai.configure(api_key=GEMINI_API_KEY)
    # في ملف app.py سطر 12
    model = genai.GenerativeModel('gemini-flash-latest')
except:
    print("Warning: Gemini API Key is missing.")

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'medstar_secret_key_2025' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'medstar.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app) 

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 
login_manager.login_message_category = 'danger'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ================== (Models) ==================

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(80), unique=True, nullable=False) 
    email = db.Column(db.String(120), unique=True, nullable=False) 
    password = db.Column(db.String(200), nullable=False) 
    is_admin = db.Column(db.Boolean, default=False) 
    def __repr__(self): return f'<User {self.username}>'

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False) 
    icon_url = db.Column(db.String(200), nullable=True, default='default_icon.png') 
    background_url = db.Column(db.String(200), nullable=True, default='default_bg.jpg') 

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) 
    specialty = db.Column(db.String(100)) 
    rank = db.Column(db.String(50), nullable=True) 
    image_url = db.Column(db.String(200), nullable=True, default='default_doctor.png') 
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    department = db.relationship('Department', backref=db.backref('doctors', lazy=True))

class LabTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False) 
    description = db.Column(db.Text, nullable=True) 
    price = db.Column(db.String(50), nullable=True) 
    icon_url = db.Column(db.String(200), nullable=True, default='icon_lab_default.png') 

class RadiologyScan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False) 
    description = db.Column(db.Text, nullable=True) 
    price = db.Column(db.String(50), nullable=True) 
    icon_url = db.Column(db.String(200), nullable=True, default='icon_scan_default.png') 

class TherapySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False) 
    description = db.Column(db.Text, nullable=True) 
    price = db.Column(db.String(50), nullable=True) 
    icon_url = db.Column(db.String(200), nullable=True, default='icon_therapy_default.png') 
    category = db.Column(db.String(50), nullable=False) 

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='Pending') 
    visit_type = db.Column(db.String(100), nullable=True)
    reason = db.Column(db.Text, nullable=True)
    service_type = db.Column(db.String(50), nullable=False) 
    service_name = db.Column(db.String(200), nullable=False)
    service_details = db.Column(db.String(200), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('appointments', lazy=True))

class SiteStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    visits = db.Column(db.Integer, default=0)

# ========================================================



@app.route('/init-db')
def init_db():
    with app.app_context():
        db.create_all() 

        if SiteStats.query.count() == 0:
            db.session.add(SiteStats(visits=0))
            db.session.commit()

        if Department.query.count() == 0:
            dep1 = Department(name="Cardiology", icon_url="icon_cardiology.png", background_url="bg_cardiology.jpg")
            dep2 = Department(name="Orthopedics", icon_url="icon_orthopedics.png", background_url="bg_orthopedics.jpg")
            dep3 = Department(name="Neurology", icon_url="icon_neurology.png", background_url="bg_neurology.jpg")
            dep4 = Department(name="Dermatology", icon_url="icon_dermatology.png", background_url="bg_dermatology.jpg")
            dep5 = Department(name="Pediatrics", icon_url="icon_pediatrics.png", background_url="bg_pediatrics.jpg")
            dep6 = Department(name="ENT", icon_url="icon_ent.png", background_url="bg_ent.jpg")
            dep7 = Department(name="General Practice", icon_url="icon_general.png", background_url="bg_general.jpg")
            db.session.add_all([dep1, dep2, dep3, dep4, dep5, dep6, dep7])
            db.session.commit()

        if Doctor.query.count() == 0:
            dep1 = Department.query.filter_by(name="Cardiology").first()
            dep2 = Department.query.filter_by(name="Orthopedics").first()
            dep3 = Department.query.filter_by(name="Neurology").first()
            dep4 = Department.query.filter_by(name="Dermatology").first()
            dep5 = Department.query.filter_by(name="Pediatrics").first()
            dep6 = Department.query.filter_by(name="ENT").first()
            dep7 = Department.query.filter_by(name="General Practice").first()
            
            doctors_list = [
                Doctor(name="Dr. Sarah Ibrahim", specialty="Heart Surgeon", rank="Consultant", image_url="f_cardio_01.png", department=dep1),
                Doctor(name="Dr. Mahmoud Fathy", specialty="General Cardiology", rank="Specialist", image_url="m_cardio_01.png", department=dep1),
                Doctor(name="Dr. Laila Mostafa", specialty="Pediatric Cardiology", rank="Specialist", image_url="f_cardio_02.png", department=dep1),
                Doctor(name="Dr. Hany Adel", specialty="Interventional Cardiology", rank="Consultant", image_url="m_cardio_02.png", department=dep1),
                Doctor(name="Dr. Amr Diab", specialty="Cardiology Intern", rank="Intern", image_url="m_intern_01.png", department=dep1),
                Doctor(name="Dr. Nora Helmy", specialty="Knee Specialist", rank="Specialist", image_url="f_ortho_01.png", department=dep2),
                Doctor(name="Dr. Karim Ahmed", specialty="Spinal Surgery", rank="Consultant", image_url="m_ortho_01.png", department=dep2),
                Doctor(name="Dr. Tamer Hosny", specialty="Sports Injuries", rank="Specialist", image_url="m_ortho_02.png", department=dep2),
                Doctor(name="Dr. Mona Zaki", specialty="Pediatric Orthopedics", rank="Consultant", image_url="f_ortho_02.png", department=dep2),
                Doctor(name="Dr. Ahmed Helmy", specialty="Orthopedics Intern", rank="Intern", image_url="m_intern_02.png", department=dep2),
                Doctor(name="Dr. Mariam Youssef", specialty="Brain Surgeon", rank="Consultant", image_url="f_neuro_01.png", department=dep3),
                Doctor(name="Dr. Youssef El Sherif", specialty="General Neurology", rank="Specialist", image_url="m_neuro_01.png", department=dep3),
                Doctor(name="Dr. Amina Khalil", specialty="Epilepsy Specialist", rank="Specialist", image_url="f_neuro_02.png", department=dep3),
                Doctor(name="Dr. Fady Boshra", specialty="Movement Disorders", rank="Consultant", image_url="m_neuro_02.png", department=dep3),
                Doctor(name="Dr. Yasmin Raeis", specialty="Neurology Intern", rank="Intern", image_url="f_intern_01.png", department=dep3),
                Doctor(name="Dr. Mohamed Salah", specialty="Cosmetic Dermatology", rank="Consultant", image_url="m_derma_01.png", department=dep4),
                Doctor(name="Dr. Hana El Zahed", specialty="General Dermatology", rank="Specialist", image_url="f_derma_01.png", department=dep4),
                Doctor(name="Dr. Ahmed Ezz", specialty="Skin Cancer Specialist", rank="Consultant", image_url="m_derma_02.png", department=dep4),
                Doctor(name="Dr. Donia Samir", specialty="Pediatric Dermatology", rank="Specialist", image_url="f_derma_02.png", department=dep4),
                Doctor(name="Dr. Hisham Maged", specialty="Dermatology Intern", rank="Intern", image_url="m_intern_03.png", department=dep4),
                Doctor(name="Dr. Akram Hosny", specialty="General Pediatrics", rank="Consultant", image_url="m_peds_01.png", department=dep5),
                Doctor(name="Dr. Menna Shalaby", specialty="Neonatology", rank="Specialist", image_url="f_peds_01.png", department=dep5),
                Doctor(name="Dr. Karim Abdelaziz", specialty="Pediatric Surgery", rank="Consultant", image_url="m_peds_02.png", department=dep5),
                Doctor(name="Dr. Hend Sabry", specialty="Pediatric Nutrition", rank="Specialist", image_url="f_peds_02.png", department=dep5),
                Doctor(name="Dr. Aly Sobhy", specialty="Pediatrics Intern", rank="Intern", image_url="m_intern_04.png", department=dep5),
                Doctor(name="Dr. Khaled El Nabawy", specialty="ENT Surgeon", rank="Consultant", image_url="m_ent_01.png", department=dep6),
                Doctor(name="Dr. Shereen Reda", specialty="Audiology", rank="Specialist", image_url="f_ent_01.png", department=dep6),
                Doctor(name="Dr. Maged El Kedwany", specialty="Laryngology", rank="Specialist", image_url="m_ent_02.png", department=dep6),
                Doctor(name="Dr. Ahmed Fahmy", specialty="Family Medicine", rank="General Practitioner", image_url="m_gp_01.png", department=dep7),
                Doctor(name="Dr. Ruby", specialty="Family Medicine", rank="General Practitioner", image_url="f_gp_01.png", department=dep7),
            ]
            db.session.add_all(doctors_list)
            db.session.commit()

        if LabTest.query.count() == 0:
            tests = [
                LabTest(name="Vitamin D (25-OH)", description="Measures the level of Vitamin D.", price="EGP 800", icon_url="icon_vitamin_d.png"),
                LabTest(name="Complete Blood Count (CBC)", description="Evaluates overall health.", price="EGP 250", icon_url="icon_cbc.png"),
                LabTest(name="Liver Function Tests (LFT)", description="Check liver health.", price="EGP 400", icon_url="icon_liver.png"),
                LabTest(name="Kidney Function Tests (KFT)", description="Checks kidney function.", price="EGP 350", icon_url="icon_kidney.png"),
                LabTest(name="Lipid Profile (Fats)", description="Measures cholesterol.", price="EGP 300", icon_url="icon_lipid.png"),
                LabTest(name="HbA1c", description="Average blood sugar.", price="EGP 280", icon_url="icon_sugar.png"),
                LabTest(name="Thyroid Panel", description="Evaluates thyroid gland.", price="EGP 550", icon_url="icon_thyroid.png"),
                LabTest(name="Iron Profile", description="Checks for iron deficiency.", price="EGP 450", icon_url="icon_iron.png"),
                LabTest(name="Vitamin B12", description="Measures vitamin B12.", price="EGP 600", icon_url="icon_b12.png"),
                LabTest(name="CRP", description="Inflammation marker.", price="EGP 200", icon_url="icon_crp.png"),
                LabTest(name="Uric Acid", description="Gout check.", price="EGP 150", icon_url="icon_uric_acid.png"),
                LabTest(name="Hepatitis C Antibody", description="Screens for HCV.", price="EGP 300", icon_url="icon_hepatitis.png")
            ]
            db.session.add_all(tests)
            db.session.commit()

        if RadiologyScan.query.count() == 0:
            scans = [
                RadiologyScan(name="MRI Scan (Brain)", description="Detailed imaging of the brain.", price="EGP 1500", icon_url="icon_mri.png"),
                RadiologyScan(name="CT Scan (Chest)", description="Cross-sectional X-ray images.", price="EGP 1200", icon_url="icon_ct.png"),
                RadiologyScan(name="X-Ray (Chest/Bone)", description="Basic imaging for fractures.", price="EGP 250", icon_url="icon_xray.png"),
                RadiologyScan(name="Ultrasound (Abdominal)", description="Imaging of internal organs.", price="EGP 400", icon_url="icon_ultrasound.png"),
                RadiologyScan(name="Mammography", description="Breast screening.", price="EGP 800", icon_url="icon_mammo.png"),
                RadiologyScan(name="PET-CT Scan", description="Advanced imaging.", price="EGP 4000", icon_url="icon_pet.png")
            ]
            db.session.add_all(scans)
            db.session.commit()

        if TherapySession.query.count() == 0:
            sessions = [
                TherapySession(name="Physio Rehab", description="Rehabilitation program.", price="EGP 300", icon_url="icon_rehab.png", category="Physical"),
                TherapySession(name="Manual Therapy", description="Hands-on massage.", price="EGP 250", icon_url="icon_manual.png", category="Physical"),
                TherapySession(name="Pediatric PT", description="Therapy for children.", price="EGP 350", icon_url="icon_ped_therapy.png", category="Physical"),
                TherapySession(name="CBT Therapy", description="Mental talk therapy.", price="EGP 500", icon_url="icon_cbt.png", category="Psychotherapy"),
                TherapySession(name="Stress Management", description="Handle stress techniques.", price="EGP 400", icon_url="icon_stress.png", category="Psychotherapy"),
                TherapySession(name="Family Counseling", description="For couples and families.", price="EGP 600", icon_url="icon_family.png", category="Psychotherapy")
            ]
            db.session.add_all(sessions)
            db.session.commit()
            
        if not User.query.filter_by(email="admin@medstar.com").first():
            admin_user = User(username="Admin", email="admin@medstar.com", password=generate_password_hash("admin123"), is_admin=True)
            db.session.add(admin_user)
            db.session.commit()
            
        return "Database initialized with ALL data and Reviews system!"


# ================== (Routes) ==================

# --- (تعديل: عداد الزيارات يستثني الأدمن) ---
@app.route('/')
def home():
    # (الشرط الجديد: لو مش مسجل دخول، أو مسجل دخول بس مش أدمن -> احسب الزيارة)
    if not current_user.is_authenticated or (current_user.is_authenticated and not current_user.is_admin):
        stats = SiteStats.query.first()
        if stats:
            stats.visits += 1
            db.session.commit()
        
    doctors_list = Doctor.query.limit(1).all() 
    return render_template('index.html', doctors=doctors_list)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('admin_dashboard') if user.is_admin else url_for('home'))
        else: flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout(): logout_user(); return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST']) 
def register():
    if request.method == 'POST':
        hashed = generate_password_hash(request.form.get('password'))
        user = User(username=request.form.get('username'), email=request.form.get('email'), password=hashed)
        try: db.session.add(user); db.session.commit(); flash('Account Created!', 'success'); return redirect(url_for('login'))
        except: flash('Error: Username or Email already exists.', 'danger')
    return render_template('register.html')

@app.route('/doctors')
def show_doctors(): return render_template('doctors.html', doctors=Doctor.query.all())
@app.route('/departments')
def show_all_departments(): return render_template('departments.html', departments=Department.query.all())
@app.route('/department/<int:dept_id>')
def show_department(dept_id): return render_template('doctors.html', doctors=Doctor.query.filter_by(department_id=dept_id).all(), department_name=Department.query.get_or_404(dept_id).name)
@app.route('/services')
def show_services(): return render_template('services.html')
@app.route('/about')
def show_about(): return render_template('about.html')
@app.route('/store')
def show_pharmacy(): return render_template('pharmacy.html')

@app.route('/lab-tests')
@login_required 
def show_lab_tests(): return render_template('lab_tests.html', tests=LabTest.query.all())
@app.route('/radiology')
@login_required
def show_radiology(): return render_template('radiology.html', scans=RadiologyScan.query.all())
@app.route('/physical-therapy')
@login_required
def show_physical_therapy(): return render_template('therapy.html', sessions=TherapySession.query.filter_by(category='Physical').all(), title="Physical Therapy")
@app.route('/psychotherapy')
@login_required
def show_psychotherapy(): return render_template('therapy.html', sessions=TherapySession.query.filter_by(category='Psychotherapy').all(), title="Psychotherapy")

@app.route('/book/<int:doctor_id>', methods=['GET', 'POST'])
@login_required 
def book_appointment(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    if request.method == 'POST':
        date = request.form.get('date'); time = request.form.get('time')
        if Appointment.query.filter_by(service_name=doctor.name, date=date, time=time).first():
            flash('Slot unavailable!', 'danger'); return redirect(url_for('book_appointment', doctor_id=doctor.id))
        
        new_appt = Appointment(
            user_id=current_user.id, date=date, time=time,
            visit_type=request.form.get('visit_type'), reason=request.form.get('reason'),
            service_type="Doctor Visit", service_name=doctor.name, service_details=doctor.specialty
        )
        db.session.add(new_appt); db.session.commit()
        flash('Confirmed!', 'success'); return redirect(url_for('my_appointments'))
    return render_template('booking.html', doctor=doctor)

@app.route('/book-service/<service_type>/<int:service_id>', methods=['GET', 'POST'])
@login_required
def book_service(service_type, service_id):
    item = None; sType = ""; sDetails = ""
    if service_type == 'lab':
        item = LabTest.query.get_or_404(service_id); sType="Lab Test"; sDetails=item.price
        class Fake: name=item.name; rank="Lab"; specialty=item.price; image_url=item.icon_url; department=type('o', (object,), {'name': 'Laboratory'})
        display = Fake()
    elif service_type == 'scan':
        item = RadiologyScan.query.get_or_404(service_id); sType="Scan"; sDetails=item.price
        class Fake: name=item.name; rank="Radiology"; specialty=item.price; image_url=item.icon_url; department=type('o', (object,), {'name': 'Imaging'})
        display = Fake()
    elif service_type == 'therapy':
        item = TherapySession.query.get_or_404(service_id); sType="Therapy"; sDetails=item.price
        class Fake: name=item.name; rank="Therapy"; specialty=item.price; image_url=item.icon_url; department=type('o', (object,), {'name': 'Rehab'})
        display = Fake()

    if request.method == 'POST':
        new_appt = Appointment(
            user_id=current_user.id, date=request.form.get('date'), time=request.form.get('time'),
            visit_type=request.form.get('visit_type'), reason=request.form.get('reason'),
            service_type=sType, service_name=item.name, service_details=sDetails
        )
        db.session.add(new_appt); db.session.commit()
        flash('Booked!', 'success'); return redirect(url_for('my_appointments'))
    return render_template('booking.html', doctor=display)

@app.route('/upload-prescription', methods=['POST'])
@login_required
def upload_prescription(): flash('Uploaded successfully!', 'success'); return redirect(url_for('show_pharmacy'))

@app.route('/contact', methods=['GET', 'POST'])
def show_contact():
    if request.method == 'POST':
        rate = request.form.get('rating') if request.form.get('rating') else 5
        db.session.add(Message(name=request.form.get('name'), email=request.form.get('email'), message_text=request.form.get('message'), rating=int(rate)))
        db.session.commit(); flash('Review submitted!', 'success'); return redirect(url_for('show_contact'))
    return render_template('contact.html', reviews=Message.query.order_by(Message.id.desc()).all())

@app.route('/chat-doctor', methods=['GET', 'POST'])
@login_required 
def show_chat_doctor():
    if 'chat_history' not in session: session['chat_history'] = [{'type': 'received', 'text': f'Hello {current_user.username}!'}]
    if request.method == 'POST':
        session['chat_history'].append({'type': 'sent', 'text': request.form.get('message_text')})
        session['chat_history'].append({'type': 'received', 'text': 'We received your message.'})
        session.modified = True; return redirect(url_for('show_chat_doctor'))
    return render_template('chat_doctor.html', chat_history=session['chat_history'])

@app.route('/ai-consult', methods=['GET', 'POST'])
@login_required
def ai_consult():
    if 'ai_chat_history' not in session:
        session['ai_chat_history'] = [{'type': 'received', 'text': "Hello! Describe your symptoms clearly."}]
    
    if request.method == 'POST':
        user_input = request.form.get('symptom_text')
        session['ai_chat_history'].append({'type': 'sent', 'text': user_input})
        
        try:
            prompt = f"""
            Act as a medical receptionist at MedStar Hospital. Departments:
            1: Cardiology (Heart, Chest pain)
            2: Orthopedics (Bones, Joints, Knee, Back)
            3: Neurology (Brain, Headache)
            4: Dermatology (Skin, Rash)
            5: Pediatrics (Children)
            6: ENT (Ear, Nose, Throat)
            7: General Practice (Flu, Fever)

            Patient symptom: "{user_input}"

            Task: Pick BEST Dept ID (1-7) & Advice.
            Reply format:
            ID: [Number]
            Advice: [Short advice]
            """
            
            response = model.generate_content(prompt)
            text_resp = response.text
            
            dept_id = 7
            advice = "Please consult a doctor."
            
            for line in text_resp.split('\n'):
                if 'ID:' in line:
                    try:
                        found = int(''.join(filter(str.isdigit, line.split(':')[1])))
                        if 1 <= found <= 7: dept_id = found
                    except: pass
                if 'Advice:' in line:
                    advice = line.split('Advice:')[1].strip()
            
            dept_link = url_for('show_department', dept_id=dept_id)
            
            # --- التعديل هنا (زرار بشكـل ولون ثابت) ---
            # --- تنسيق الرسالة (الزرار بنفس لون الموقع التركواز) ---
            # --- العودة للكلاس الأصلي للموقع ---
            # --- العودة للكلاس الأصلي للموقع ---
            final_reply = f"""
            {advice}
            <br><br>
            <a href='{dept_link}' class='navbar__btn' style='padding:0.5rem 1rem; font-size:0.9rem; text-decoration:none;'>
                View Recommended Doctors
            </a>
            """
            
            session['ai_chat_history'].append({'type': 'received', 'text': final_reply})
            
        except Exception as e:
            session['ai_chat_history'].append({'type': 'received', 'text': "Service busy. Try again."})
            
        session.modified = True
        return redirect(url_for('ai_consult')) # تعديل صغير لمنع إعادة إرسال النموذج (Resubmission)
    
    return render_template('ai_consult.html', chat_history=session['ai_chat_history'])

@app.route('/reset-chat')
@login_required
def reset_chat():
    session.pop('ai_chat_history', None) # دي بتمسح الشات القديم تماماً
    return redirect(url_for('ai_consult'))

@app.route('/my-appointments')
@login_required
def my_appointments(): return render_template('my_appointments.html', appointments=Appointment.query.filter_by(user_id=current_user.id).all())

@app.route('/cancel/<int:appt_id>')
@login_required
def cancel_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if appt.user_id != current_user.id or appt.status == 'Completed': return redirect(url_for('my_appointments'))
    db.session.delete(appt); db.session.commit(); flash('Cancelled!', 'info'); return redirect(url_for('my_appointments'))

@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin: return redirect(url_for('home'))
    all_appts = Appointment.query.all(); all_reviews = Message.query.all()
    total = len(all_appts); completed = Appointment.query.filter_by(status='Completed').count()
    pos = Message.query.filter(Message.rating >= 4).count(); neg = Message.query.filter(Message.rating <= 3).count()
    stats = SiteStats.query.first(); visit_count = stats.visits if stats else 0
    
    return render_template('admin_dashboard.html', 
                           appointments=all_appts, 
                           messages=all_reviews, 
                           total=total, 
                           completed=completed, 
                           pending=total-completed, 
                           pos_reviews=pos, 
                           neg_reviews=neg, 
                           reviews=all_reviews,
                           visit_count=visit_count)

@app.route('/complete/<int:appt_id>')
@login_required
def complete_appointment(appt_id):
    if not current_user.is_admin: return redirect(url_for('home'))
    appt=Appointment.query.get_or_404(appt_id); appt.status='Completed'; db.session.commit(); return redirect(url_for('admin_dashboard'))

@app.errorhandler(404)
def page_not_found(e): return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)