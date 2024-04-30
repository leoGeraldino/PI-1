from flask import Blueprint, render_template, request, redirect, url_for, session
import mysql.connector

views = Blueprint("views", __name__)

configuracao_bd = {
    'user': 'root',
    'password': '123456',
    'host': 'localhost',
    'database': 'deck_digital',
    'raise_on_warnings': True
}

#rota de registro de usuário

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

# rota de reset de senha

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

# rota de login

@views.route('/index.html', methods=['GET', 'POST']) 
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conexao = mysql.connector.connect(**configuracao_bd)
            cursor = conexao.cursor()

            query = "SELECT idUsuarios FROM usuarios WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            usuario = cursor.fetchone()

            if usuario:
                id_usuario = usuario[0] 
                session['id_usuario'] = id_usuario
                return redirect(url_for('views.perfil', id_usuario = id_usuario))
            else:
                message3 = "Nome de usuário ou senha incorretos. Por favor, tente novamente."
                return render_template('index.html', message3 = message3)
        
        except mysql.connector.Error as error:
            return "Erro ao conectar-se ao banco de dados:{}".format(error)
    return render_template('index.html')

# rota de perfil

@views.route('/perfil.html', methods=['GET', 'POST'])
def perfil():
    id_usuario = session.get('id_usuario')
    if id_usuario is None:
        return redirect(url_for('views.index'))
    
    if request.method == 'POST':
        try:
            conexao = mysql.connector.connect(**configuracao_bd)
            cursor = conexao.cursor()

            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            bday = request.form['bday']

            if not username or not password or not email or not bday:
                return "Por favor, preencha todos os campos"
                
            query = "UPDATE usuarios SET username =%s, password=%s, email=%s, bday=%s WHERE idUsuarios = %s"
            cursor.execute(query, (username, password, email, bday, id_usuario))
            conexao.commit()

            cursor.close()
            conexao.close()

            return redirect(url_for('views.perfil', id_usuario = id_usuario)) 
        
        except mysql.connector.Error as error:
                return "Erro ao conectar-se ao banco de dados:{}".format(error)
    
    else:
        try:
            conexao = mysql.connector.connect(**configuracao_bd)
            cursor = conexao.cursor()

            query = "SELECT * FROM usuarios WHERE idUsuarios = %s"
            cursor.execute(query, (id_usuario,))
            usuario = cursor.fetchone()

            if usuario:
                return render_template ('perfil.html', usuario=usuario)
            else:
                return "Usuário não encontrado"
            
        except mysql.connector.Error as error:
            return "Erro ao conectar-se ao banco de dados:{}".format(error)
        
        
# rota de adicionar cartas

@views.route('/cartas.html', methods=['GET', 'POST'])
def cartas():
    id_usuario = session.get('id_usuario')
    if id_usuario is None:
        return redirect(url_for('views.index'))
    
    if request.method == 'POST':
        try:
            conexao = mysql.connector.connect(**configuracao_bd)
            cursor = conexao.cursor()

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

            query = "INSERT INTO cartas (idUsuario, card, preco, artista, tipo, texto, lealdade, CMC, edicao, formato, raridade, cor, pr, custos) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (id_usuario, card, preco, artista, tipo, texto, lealdade, cmc, edicao, formato, raridade, cor, pr, custos))
            conexao.commit()

            cursor.close()
            conexao.close()

            return redirect(url_for('views.perfil', id_usuario = id_usuario))

        except mysql.connector.Error as error:
            return "Erro ao conectar-se ao banco de dados:{}".format(error)
        
    else:
        return render_template('cartas.html')
    
@views.route('/decks.html', methods = ['GET', 'POST'])
def decks():
    id_usuario = session.get('id_usuario')
    if id_usuario is None:
        return redirect(url_for('views.index'))
    
    lista_cartas = []
    indice_cartas = []

    try:
        conexao = mysql.connector.connect(**configuracao_bd)
        cursor = conexao.cursor()

        query = "SELECT idCarta, card FROM cartas WHERE idUsuario = %s"
        cursor.execute(query, (id_usuario,))       
        resultados = cursor.fetchall()

        indice_cartas = [row [0] for row in resultados]
        lista_cartas = [row[1] for row in resultados]

        if not lista_cartas:
            message4 = "Para cadastrar um deck, você precisa cadastrar uma carta. "
            return render_template('decks.html', message4 = message4)

        if request.method == 'POST':
            deck_name = request.form['deck_name']
            cartas_selecionadas = request.form.getlist('cartas_selecionadas')

            if deck_name and cartas_selecionadas:
                
                ids_cartas_selecionadas = [
                        id for id, nome in zip(indice_cartas, lista_cartas)
                        if nome in cartas_selecionadas 
                    ]
                
                for carta_id in ids_cartas_selecionadas:
                    
                    query = "INSERT INTO decks (deck_name, idUsuario, idCarta) VALUES (%s, %s, %s)"
                    cursor.execute(query, (deck_name, id_usuario, carta_id))

                    conexao.commit()

            else:
                message5 = "Por favor, insira o nome do deck e selecione pelo menos uma carta."
                return render_template('decks.html', lista_cartas=lista_cartas, message5=message5)

        cursor.close()
        conexao.close()    

    except mysql.connector.Error as error:
        return "Erro ao conectar-se ao banco de dados:{}".format(error)

    return render_template('decks.html', lista_cartas = lista_cartas)