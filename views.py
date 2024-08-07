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

def conecta_bd(config):  #função de conectar db abreviado
    try:
        conexao = mysql.connector.connect(**configuracao_bd)
        cursor = conexao.cursor()
        return conexao, cursor
    
    except mysql.connector.Error as e:
        return "Erro ao conectar-se ao banco de dados:{}".format(e)
    
def dados_usuario(): #função de receber os dados do usuário
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    bday = request.form['bday']
    return username, password, email, bday

def dados_carta():  #função de receber os dados da carta
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
    return card, preco, artista, tipo, texto, lealdade, cmc, edicao, formato, raridade, cor, pr, custos
    
def comita_conexao(conexao, cursor):  #função fazer commit da conexão, fechar cursor e conexão
    try:
        conexao.commit()
    finally:
        cursor.close()
        conexao.close()

def fecha_conexao(conexao, cursor):  #função de fechar cursor e conexão
    try:
        cursor.close() 
    finally:    
        conexao.close()

@views.route('/redirect_registro', methods=['GET', 'POST'])  #rota para redirecionar à página de registro
def redirect_registro():
    return redirect(url_for('views.registro'))

@views.route('/registro.html', methods=['GET', 'POST'])  #rota de registro de usuário
def registro():
    if request.method == 'POST':
        username, password, email, bday = dados_usuario()

        try:
            conexao, cursor = conecta_bd(configuracao_bd)  
            query = "SELECT * FROM usuarios WHERE username = %s"
            cursor.execute(query, (username,))
            usuario_existente = cursor.fetchone()

            if usuario_existente:
                message = "Nome de usuário já cadastrado. Por favor, escolha outro."
                return render_template('registro.html', message = message)

            query = "INSERT INTO usuarios (username, password, email, bday) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (username, password, email, bday))
            comita_conexao(conexao, cursor) 
            return redirect(url_for('views.index'))
    
        except mysql.connector.Error as error:
            return "Erro ao conectar-se ao banco de dados:{}".format(error)
    
    return render_template('registro.html')

@views.route('/reset.html', methods=['GET', 'POST'])  # rota de reset de senha
def reset():
    if request.method == 'POST':
        username, password, email, bday = dados_usuario() 

        try:
            conexao, cursor = conecta_bd(configuracao_bd)  
            query = "SELECT * FROM usuarios WHERE username = %s AND email = %s AND bday = %s"
            cursor.execute(query, (username, email, bday))
            usuario = cursor.fetchone()
            if not usuario:
                message2 = "Usuário não encontrado. Por favor verifique as informações inseridas."
                return render_template('reset.html', message2 = message2)
            
            query = "UPDATE usuarios SET password =%s WHERE username = %s"
            cursor.execute(query, (password, username))
            comita_conexao(conexao, cursor)  
            return redirect(url_for('views.index'))
        
        except mysql.connector.Error as error:
            return "Erro ao conectar-se ao banco de dados:{}".format(error)

    return render_template('reset.html')

@views.route('/index.html', methods=['GET', 'POST'])   # rota de login
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conexao, cursor = conecta_bd(configuracao_bd)  
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

@views.route('/perfil.html', methods=['GET', 'POST'])  # rota de perfil
def perfil():
    id_usuario = session.get('id_usuario')
    if id_usuario is None:
        return redirect(url_for('views.index'))
    
    conexao = None
    cursor = None

    try:
        conexao, cursor = conecta_bd(configuracao_bd)  
        
        if request.method == 'POST':
            username, password, email, bday = dados_usuario()

            if not username or not password or not email or not bday:
                return "Por favor, preencha todos os campos"
                
            query_update = "UPDATE usuarios SET username =%s, password=%s, email=%s, bday=%s WHERE idUsuarios = %s"
            cursor.execute(query_update, (username, password, email, bday, id_usuario))
            comita_conexao(conexao, cursor)  
            return redirect(url_for('views.perfil', id_usuario = id_usuario)) 
            
        else:
            query_usuario = "SELECT * FROM usuarios WHERE idUsuarios = %s"
            cursor.execute(query_usuario, (id_usuario,))
            usuario = cursor.fetchone()

            if not usuario:
                return "Usuário não encontrado"

            query_decks_cadastrados = "SELECT deck_name FROM decks WHERE idUsuario = %s"
            cursor.execute(query_decks_cadastrados, (id_usuario,))
            decks_cadastrados = [row[0] for row in cursor.fetchall()]
            fecha_conexao(conexao, cursor)
            return render_template ('perfil.html', usuario=usuario, decks_cadastrados=decks_cadastrados)

    except mysql.connector.Error as error:
        if cursor: 
            cursor.close()
        if conexao:
            conexao.close()
        return "Erro ao conectar-se ao banco de dados:{}".format(error)

@views.route('/cartas.html', methods=['GET', 'POST'])  # rota de adicionar cartas
def cartas():
    id_usuario = session.get('id_usuario')
    if id_usuario is None:
        return redirect(url_for('views.index'))
    
    if request.method == 'POST':
        try:
            conexao, cursor = conecta_bd(configuracao_bd)  
            card, preco, artista, tipo, texto, lealdade, cmc, edicao, formato, raridade, cor, pr, custos = dados_carta()

            query = "INSERT INTO cartas (idUsuario, card, preco, artista, tipo, texto, lealdade, CMC, edicao, formato, raridade, cor, pr, custos) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (id_usuario, card, preco, artista, tipo, texto, lealdade, cmc, edicao, formato, raridade, cor, pr, custos))
            comita_conexao(conexao, cursor)
            return redirect(url_for('views.perfil', id_usuario = id_usuario))

        except mysql.connector.Error as error:
            return "Erro ao conectar-se ao banco de dados:{}".format(error)
        
    else:
        return render_template('cartas.html')
 
@views.route('/decks.html', methods = ['GET', 'POST'])  #rota para adicionar decks   
def decks():
    id_usuario = session.get('id_usuario')
    if id_usuario is None:
        return redirect(url_for('views.index'))
    
    lista_cartas = []
    indice_cartas = []

    try:
        conexao, cursor = conecta_bd(configuracao_bd)  

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
                
                query_insert_deck = "INSERT INTO decks (deck_name, idUsuario) VALUES (%s, %s)"
                cursor.execute(query_insert_deck, (deck_name, id_usuario))
                deck_id = cursor.lastrowid

                query_insert_deck_cartas = "INSERT INTO decks_cartas(idDeck, idCarta) VALUES (%s, %s)"
                for carta_nome in cartas_selecionadas:
                    carta_id = next (
                        id for nome, id in zip(lista_cartas, indice_cartas)
                        if nome == carta_nome
                    )
                    cursor.execute(query_insert_deck_cartas, (deck_id, carta_id))    
                    conexao.commit()

                return redirect(url_for('views.perfil'))

            else:
                message5 = "Por favor, insira o nome do deck e selecione pelo menos uma carta."
                return render_template('decks.html', lista_cartas=lista_cartas, message5=message5)

        fecha_conexao(conexao, cursor) 

    except mysql.connector.Error as error:
        return "Erro ao conectar-se ao banco de dados:{}".format(error)

    return render_template('decks.html', lista_cartas = lista_cartas)

@views.route('/delete_deck', methods=['POST'])  #rota para deletar decks
def delete_deck():
    id_usuario = session.get('id_usuario')
    if id_usuario is None:
        return redirect(url_for('views.index'))
    
    deck_name_delete = request.form.get('deck_name_delete')

    if not deck_name_delete:
        return "Nome do deck não fornecido."

    try:
        conexao, cursor = conecta_bd(configuracao_bd)  

        query_delete_deck = "DELETE FROM decks WHERE deck_name = %s AND idUsuario =%s"
        cursor.execute(query_delete_deck, (deck_name_delete, id_usuario))
        comita_conexao(conexao, cursor)  
        return redirect(url_for('views.perfil'))
    
    except mysql.connector.Error as error:
        return "Erro ao conectar-se ao banco de dados:{}".format(error)

@views.route('/edit_deck', methods=['GET','POST'])  #rota para ir para a página de edição de decks
def edit_deck():
    id_usuario = session.get('id_usuario')
    if id_usuario is None:
        return redirect(url_for('views.index'))

    try:
        conexao, cursor = conecta_bd(configuracao_bd)  
        deck_name_edit = request.form.get('deck_name_edit')

        if request.method == 'POST':
            deck_name_edit = request.form.get('deck_name_edit')

            if not deck_name_edit:
               return "Nome do deck não fornecido."
            
            query_find_deck = "SELECT idDeck FROM decks WHERE deck_name= %s AND idUsuario = %s"
            cursor.execute(query_find_deck, (deck_name_edit, id_usuario,))
            id_deck_retornado = cursor.fetchone()

            query_id_cartas_deck = "SELECT idCarta FROM decks_cartas WHERE idDeck = %s"
            cursor.execute(query_id_cartas_deck, (id_deck_retornado[0],))
            id_cartas_deck = [row[0] for row in cursor.fetchall()]

            cartas_existentes = []
            for id_carta in id_cartas_deck:
                query_carta_deck = "SELECT card FROM cartas WHERE idCarta = %s"
                cursor.execute(query_carta_deck,(id_carta,))
                nome_carta = cursor.fetchone()
                if nome_carta:
                    cartas_existentes.append(nome_carta[0])

            query_cartas_usuario = "SELECT card FROM cartas WHERE idUsuario = %s"
            cursor.execute(query_cartas_usuario, (id_usuario,))       
            lista_cartas_usuario = cursor.fetchall()
            fecha_conexao(conexao, cursor)
                
            return render_template('editdeck.html', deck_name_edit=deck_name_edit, 
                                       lista_cartas_usuario=lista_cartas_usuario, 
                                       cartas_no_deck=cartas_existentes, 
                                       id_deck_retornado=id_deck_retornado[0])
    
    except mysql.connector.Error as error:
        return "Erro ao conectar-se ao banco de dados:{}".format(error)

@views.route('/save_edit_deck', methods = ['GET', 'POST']) #rota para incluir as alterações no deck e salvá-las
def save_edit_deck():
    id_usuario = session.get('id_usuario')
    if id_usuario is None:
        return redirect(url_for('views.index'))
    
    try:
        conexao, cursor = conecta_bd(configuracao_bd)  

        if request.method == 'POST':
            save_deckname = request.form.get('deck_name')
            cartas_selecionadas = request.form.getlist('cartas_selecionadas')
            id_deck = request.form.get('id_deck_retornado')

            if id_deck is None:
                return "Deck não encontrado."

            query_remove_cartas = "DELETE FROM decks_cartas WHERE idDeck = %s"
            cursor.execute(query_remove_cartas, (id_deck,))

            query_novo_deckname = "UPDATE decks SET deck_name =%s WHERE idDeck = %s"
            cursor.execute(query_novo_deckname, (save_deckname, id_deck))

            query_find_card_id = "SELECT idCarta FROM cartas WHERE card = %s AND idUsuario = %s"
            for carta in cartas_selecionadas:
                cursor.execute(query_find_card_id, (carta, id_usuario))
                id_carta_retornada = cursor.fetchone()
                if id_carta_retornada:
                    query_add_card = "INSERT INTO decks_cartas (idDeck, idCarta) VALUES (%s, %s)"
                    cursor.execute(query_add_card, (id_deck, id_carta_retornada[0]))

            comita_conexao(conexao, cursor)  
            return redirect(url_for('views.perfil'))

    except mysql.connector.Error as error:
        return "Erro ao conectar-se ao banco de dados:{}".format(error)

@views.route('/editar_cartas', methods = ['GET', 'POST'])  #rota para permitir a alteração das cartas
def editar_cartas():
    id_usuario = session.get('id_usuario')
    if id_usuario is None:
        return redirect(url_for('views.index'))
    
    try:
        conexao, cursor = conecta_bd(configuracao_bd) 
        
        query_cartas_usuario = "SELECT card FROM cartas WHERE idUsuario = %s"
        cursor.execute(query_cartas_usuario, (id_usuario,))       
        lista_cartas_usuario = cursor.fetchall()
        fecha_conexao(conexao, cursor)
        return render_template('editarcartas.html', lista_cartas_usuario=lista_cartas_usuario)
    
    except mysql.connector.Error as error:
        return "Erro ao conectar-se ao banco de dados:{}".format(error)
   
@views.route('delete_card', methods=['POST'])  #rota para exclusão de cartas 
def delete_card():
    id_usuario = session.get('id_usuario')
    if id_usuario is None:
        return redirect(url_for('views.index'))
    
    card_name_delete = request.form.get('card_name_delete')

    if not card_name_delete:
        return "Nome do card não fornecido."

    try:
        conexao, cursor = conecta_bd(configuracao_bd)  
        query_delete_card = "DELETE FROM cartas WHERE card = %s AND idUsuario =%s"
        cursor.execute(query_delete_card, (card_name_delete, id_usuario))
        comita_conexao(conexao, cursor)  
        return redirect(url_for('views.editar_cartas'))
    
    except mysql.connector.Error as error:
        return "Erro ao conectar-se ao banco de dados:{}".format(error)

@views.route('edit_card', methods=['GET', 'POST'])  #rota para alterar cartas
def edit_card():
    id_usuario = session.get('id_usuario')
    if id_usuario is None:
        return redirect(url_for('views.index'))
    
    try:
        conexao, cursor = conecta_bd(configuracao_bd)  

        if request.method == 'POST':
            card_name_edit = request.form.get('card_name_edit')
            query_editar_carta = "SELECT * FROM cartas WHERE card =%s AND idUsuario =%s"
            cursor.execute(query_editar_carta, (card_name_edit, id_usuario))
            card_info = cursor.fetchone()
            fecha_conexao(conexao, cursor)
            return render_template ('editcard.html', card_info = card_info)

    except mysql.connector.Error as error:
        return "Erro ao conectar-se ao banco de dados:{}".format(error)

@views.route('salvar_edit_card', methods=['GET', 'POST'])  #rota para salvar alterações nas cartas
def salvar_edit_card():
    id_usuario = session.get('id_usuario')
    if id_usuario is None:
        return redirect(url_for('views.index'))
    
    try:
        conexao, cursor = conecta_bd(configuracao_bd)  

        if request.method == 'POST':
            id_carta = request.form['id_carta']
            card, preco, artista, tipo, texto, lealdade, cmc, edicao, formato, raridade, cor, pr, custos = dados_carta()
            
            query_atualiza_carta = "UPDATE cartas SET card = %s, preco = %s, artista = %s, tipo = %s, texto = %s, lealdade = %s, CMC = %s, edicao = %s, formato = %s, raridade = %s, cor = %s, pr = %s, custos = %s WHERE idUsuario = %s AND idCarta = %s"
            cursor.execute(query_atualiza_carta, (card, preco, artista, tipo, texto, lealdade, cmc, edicao, formato, raridade, cor, pr, custos, id_usuario, id_carta))
            comita_conexao(conexao, cursor)  
            return redirect(url_for('views.perfil'))

    except mysql.connector.Error as error:
        return "Erro ao conectar-se ao banco de dados:{}".format(error)
    
@views.route('/logout')  #rota para logout do sistema
def logout():
    session.pop('id_usuario', None)  
    return redirect(url_for('views.index'))  