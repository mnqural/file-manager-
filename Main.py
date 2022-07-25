import flask, os, shutil
from flask import Flask, render_template, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

from news.NewsBlueprint import news



"""начало"""
app = Flask(__name__)

app.config['SECRET_KEY'] = 'e072a07589e2f937689389b5266dd6f1e6e113bd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# СОЗДАНИЕ ТАБЛИЦЫ В DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
# db.create_all()

default_path = "D:\\coolder"
os.chdir(default_path)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

@app.route("/")
def index():
    return render_template('index.html',
                           current_working_directory=os.getcwd(),
                           itemList=os.listdir(),
                           logged_in=current_user.is_authenticated)

# Функция комманды 'cd'
@app.route('/cd')
def cd():
    path = os.path.abspath(request.args.get('path'))
    # Проверка пути
    if path < default_path:
        return redirect('/')

    os.chdir(path)
    # redirect to file manager
    return redirect('/')

@app.route('/rm')
def rm():
    # Удаление папки
    shutil.rmtree(os.getcwd() + '/' + request.args.get('dir'))

    # redirect to file manager
    return redirect('/')

@app.route('/md')
def md():
    # Содание новой папки
    folder = request.args.get('folder')
    os.mkdir(folder)

    # redirect to file manager
    return redirect('/')

# Функция проверки расширения файла
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Загрузка файлов
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Не могу прочитать файл')
            return redirect('/')
        file = request.files['file']
        if file.filename == '':
            flash('Нет выбранного файла')
            return redirect('/')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # сохраняем файл
            file.save(os.path.join(os.getcwd(), filename))
            return redirect('/')

#Скачивание файла
@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return flask.send_from_directory(directory=os.getcwd(),path=os.getcwd(), filename=filename, as_attachment=True)



"""авторизация"""
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":

        if User.query.filter_by(email=request.form.get('email')).first():
            flash("Email уже существует, войдите!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=request.form.get('email'),
            name=request.form.get('name'),
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("profile"))
    return render_template("register.html", logged_in=current_user.is_authenticated)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Неправильно введен email, попробуйте еще раз.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash("Неправильно введен пароль, попробуйте еще раз.")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('profile'))
    return render_template("login.html", logged_in=current_user.is_authenticated)

@app.route('/profile')
@login_required
def profile():
    print(current_user.name)
    return render_template("profile.html", name=current_user.name, logged_in=True)

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

app.register_blueprint(news, url_prefix='/news')
if __name__ == "__main__":
    app.run(debug=True, threaded=True)