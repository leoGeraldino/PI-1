from flask import Blueprint, render_template, request, redirect, url_for
import mysql.connector

views = Blueprint("views", __name__)

configuracao_bd = {
    'user': 'root',
    'password': 'senha',
    'host': 'localhost',
    'database': 'deck_digital',
    'raise_on_warnings': True
}

@views.route('/index.html', methods=['GET', 'POST']) #falta funcionar a autenticação -> verificar se o usuário e senha inseridos estão corretos
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conexao = mysql.connector.connect(**configuracao_bd)
            cursor = conexao.cursor()

            query = "SELECT * FROM usuarios WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            usuario = cursor.fetchone()

            if usuario:
                return redirect(url_for('views.perfil'))
            else:
                message3 = "Nome de usuário ou senha incorretos. Por favor, tente novamente."
                return render_template('index.html', message3 = message3)
        
        except mysql.connector.Error as error:
            return "Erro ao conectar-se ao banco de dados:{}".format(error)
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
            return "Erro ao conectar-se ao banco de dados:{}".format(error)
    
    return render_template('registro.html')

@views.route('/cartas.html', methods=['GET', 'POST'])
def cartas():
    if request.method == 'POST':
        return render_template('cartas.html')
    return render_template('cartas.html')

'''if user_id in session:
    user_id = session['user_id']

        card = request.form['card']
        preco = request.form['preco']
        artista = request.form['artista']
        tipo = request.form['tipo']
        texto = request.form['texto']
        lealdade = request.form['lealdade']
        cmc = request.form['cmc']
        edicao = request.form['edicao']
        formato = request.form['formato']
        raridade = request.form['raridade']
        cor = request.form['cor']
        pr = request.form['pr']
        custos = request.form['custos']

        try: 
            conexao = mysql.connector.connect(**configuracao_bd)
            cursor = conexao.cursor()

            query = "INSERT INTO cartas (idUsuario, card, preco, artista, tipo, texto, lealdade, CMC, edicao, formato, raridade, cor, pr, custos) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            
            cursor.execute(query, (user_id, card, preco, artista, tipo, texto, lealdade, cmc, edicao, formato, raridade, cor, pr, custos ))
            conexao.commit()

            cursor.close()
            conexao.close()

            return redirect(url_for('views.perfil'))
        
        except mysql.connector.Error as error:
            return "Erro ao conectar-se ao banco de dados:{}".format(error)'''    


@views.route('/perfil.html', methods=['GET', 'POST'])
def perfil():
    if request.method == 'POST':
        #return redirect(url_for('views.perfil'))
        if 'username' in request.form and 'password' in request.form and 'email' in request.form and 'bday' in request.form:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            bday = request.form['bday']

            if not username or not password or not email or not bday:
                return "Por favor, preencha todos os campos"

            try:
                conexao = mysql.connector.connect(**configuracao_bd)
                cursor = conexao.cursor()

                user_id = 1

                query = "UPDATE usuarios SET username = %s, password = %s, email = %s, bday = %s WHERE idUsuarios = %s"
                cursor.execute(query,(username, password, email, bday, user_id))
                conexao.commit()

                cursor.close()
                conexao.close()

                return redirect(url_for('views.perfil'))
            
            except mysql.connector.Error as error:
                return "Erro ao conectar-se ao banco de dados:{}".format(error)
    
    else:
        try:
            conexao = mysql.connector.connect(**configuracao_bd)
            cursor = conexao.cursor()

            user_id = 1

            query = "SELECT * FROM usuarios WHERE idUsuarios = %s"
            cursor.execute(query, (user_id,))
            usuario = cursor.fetchone()

            if usuario: 
                return render_template('perfil.html', usuario=usuario)
            else:
                return "Usuário não encontrado no banco de dados."
            
        except mysql.connector.Error as error:
            return "Erro ao conectar-se ao banco de dados:{}".format(error)

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
        
        except mysql.connector.Error as error:
            return "Erro ao conectar-se ao banco de dados:{}".format(error)

    return render_template('reset.html')