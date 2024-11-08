from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bcrypt import Bcrypt  # Importar o Bcrypt corretamente
import psycopg2

app = Flask(__name__)
app.secret_key = 'secret_key'  # Alterar para algo mais seguro em produção
bcrypt = Bcrypt(app)  # Inicializar o Bcrypt

# Configurações do banco de dados PostgreSQL
DATABASE_URL = "postgresql://postgres:root@127.0.0.1:4325/your_database"



# Conectar ao banco de dados
def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_client_encoding('UTF8')  # Garantir que a conexão usa UTF-8
        print("Conexão com o banco de dados bem-sucedida!")  # Mensagem para verificar
        return conn
    except Exception as e:
        print(f"Erro de conexão com o banco de dados: {e}")  # Mensagem de erro
        return None


# Rota para a tela principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota para a tela de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Consultar o banco de dados para verificar o email
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()

        if user:
            # Verificar a senha com bcrypt
            stored_password = user[2]  # Supondo que a senha esteja na terceira coluna
            if bcrypt.check_password_hash(stored_password, password):
                return redirect(url_for('dashboard'))
            else:
                flash('E-mail ou senha incorretos', 'danger')
        else:
            flash('E-mail ou senha incorretos', 'danger')

        return redirect(url_for('login'))

    return render_template('login.html')

# Rota para a tela de cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        # Verificar se os dados estão sendo recebidos corretamente
        if not nome or not email or not senha:
            flash('Por favor, preencha todos os campos.', 'danger')
            return render_template('cadastro.html')

        # Hash da senha antes de armazenar no banco
        try:
            hashed_password = bcrypt.generate_password_hash(senha).decode('utf-8')
        except Exception as e:
            flash(f'Erro ao gerar hash da senha: {e}', 'danger')
            return render_template('cadastro.html')

        # Conectar ao banco de dados
        conn = get_db_connection()
        if conn is None:
            flash('Erro de conexão com o banco de dados. Tente novamente mais tarde.', 'danger')
            return render_template('cadastro.html')

        cursor = conn.cursor()

        try:
            # Inserir dados no banco de dados
            cursor.execute("INSERT INTO users (nome, email, password) VALUES (%s, %s, %s)", (nome, email, hashed_password))
            conn.commit()
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('login'))  # Redirecionar para login após sucesso
        except Exception as e:
            flash(f'Erro ao cadastrar usuário: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('cadastro.html')

# Rota para o dashboard (informações do usuário após login)
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Rodando o servidor
if __name__ == '__main__':
    app.run(debug=True)
