from flask import Blueprint, render_template, request, redirect, url_for
import mysql.connector

views = Blueprint("views", __name__)

configuracao_bd = {
    'user': 'root',
    'password': 'Pedirrato10@',
    'host': 'localhost',
    'database': 'deck_digital',
    'raise_on_warnings': True
}

@views.route('/index.html')
def index():
    return render_template('index.html')

@views.route('/registro.html', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        bday = request.form['bday']

        try:
            conexao = mysql.connector.connect(**configuracao_bd)
            cursor = conexao.cursor()
            query = "SELECT * FROM usuarios WHERE username = %s"
            cursor.execute(query, (username,))
            usuario_existente = cursor.fetchone()

            if usuario_existente:
                message = "Nome de usuário já cadastrado. Por favor, escolha outro."
                return render_template('registro.html', message = message)

            query = "INSERT INTO usuarios (username, password, email, bday) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (username, password, email, bday))
            conexao.commit()
            cursor.close()
            conexao.close()

            return redirect(url_for('views.index'))
    
        except mysql.connector.Error as error:
            return "Erro ao conectar-se ao banco de dados:{}". format(error)
    
    return render_template('registro.html')

@views.route('/cartas.html')
def cartas():
    return render_template('cartas.html')

@views.route('/perfil.html', methods=['GET', 'POST'])
def perfil():
    if request.method == 'POST':
        #lógica do bd
        return redirect(url_for('views.perfil'))
    return render_template('perfil.html')

@views.route('/reset.html', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        bday = request.form['bday']

        try:
            conexao = mysql.connector.connect(**configuracao_bd)
            cursor = conexao.cursor()

            query = "SELECT * FROM usuarios WHERE username = %s AND email = %s AND bday = %s"
            cursor.execute(query, (username, email, bday))
            usuario = cursor.fetchone()

            if not usuario:
                message2 = "Usuário não encontrado. Por favor verifique as informações inseridas."
                return render_template('reset.html', message2 = message2)
            
            query = "UPDATE usuarios SET password =%s WHERE username = %s"
            cursor.execute(query, (password, username))
            conexao.commit()

            cursor.close()
            conexao.close()
            return redirect(url_for('views.index'))
        
        except mysql.connector.Error as error2:
            return "Erro ao conectar-se ao banco de dados:{}", format(error2)

    return render_template('reset.html')