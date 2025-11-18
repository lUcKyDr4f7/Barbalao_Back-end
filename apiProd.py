from flask import Flask, request, jsonify, session, Blueprint
from encrypt import verify_password, hash_password
from datetime import timedelta
from flask_cors import CORS
import psycopg2
import os

class Database:
    def __init__(self):
        self.config = {
            "dbname": "banco_barbalao",
            "user": "root",
            "password": "DdDLJr8BYykOf9hJL9TWXP2eDsF2A8S6",
            "host": "dpg-d42kp3i4d50c739qr750-a.oregon-postgres.render.com",
            "port": "5432",
        }

    def get_conn(self):
        return psycopg2.connect(**self.config)

class AuthController:
    def __init__(self, db: Database):
        self.db = db
        self.bp = Blueprint('auth', __name__, url_prefix='/api')

        self.bp.route('/login/', methods=['POST', 'OPTIONS'])(self.login)
        self.bp.route('/check_session/', methods=['GET'])(self.check_session)

    def login(self):
        if request.method == 'OPTIONS':
            return jsonify({"message": "CORS preflight OK"}), 200
        data = request.get_json()
        if data is None:
            return jsonify({"message": "JSON inválido ou ausente na requisição"}), 400

        nome = data.get('nome')
        senha = data.get('senha')

        try:
            conn = self.db.get_conn()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM usuario WHERE nome_user = %s', (nome,))
            usuario = cursor.fetchone()
            cursor.close()
            conn.close()

            if usuario and verify_password(usuario[2], senha):
                session['user'] = usuario[1]
                session['id'] = usuario[0]
                session.permanent = True
                return jsonify({"message": "OK", "user": usuario[1]}), 200

            return jsonify({"message": "Usuário ou senha incorretos"}), 401

        except Exception as e:
            print(f"Erro no login: {e}")
            return jsonify({"message": "Erro no servidor, tente mais tarde"}), 500

    def check_session(self):
        if 'user' in session:
            return jsonify({"authenticated": True}), 200
        else:
            return jsonify({"authenticated": False}), 401


class ProductController:
    def __init__(self, db: Database):
        self.db = db
        self.bp = Blueprint('products', __name__, url_prefix='/api/products')

        self.bp.route('/', methods=['POST'])(self.create_product)
        self.bp.route('/', methods=['GET'])(self.list_products)
        self.bp.route('/atualizar/<int:product_id>/', methods=['POST'])(self.update_product)
        self.bp.route('/remove/<int:product_id>/', methods=['DELETE'])(self.remove_product)

    def create_product(self):
        data = request.get_json()
        if data is None:
            return jsonify({"message": "JSON inválido ou ausente"}), 400

        nome = data.get('nome')
        preco = data.get('preco')
        descricao = data.get('descricao')
        imagem = data.get('imagem')
        categoria = data.get('categoria')
        usuario = data.get('usuario')

        if not nome or preco is None:
            return jsonify({"message": "Campos obrigatórios: nome e preco"}), 400

        try:
            conn = self.db.get_conn()
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO produto(nome_prod, preco_prod, descricao_prod, imagem_prod, categoria_id_categoria, usuario_id_user)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id_prod
                ''', (nome, float(preco), descricao, imagem, categoria, usuario)
            )
            new_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({"message": "Produto Criado", "ID": new_id}), 201

        except Exception as e:
            print(f"Erro ao criar produto: {e}")
            return jsonify({"message": f"Erro interno: {str(e)}"}), 500

    def list_products(self):
        try:
            conn = self.db.get_conn()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id_prod, nome_prod, preco_prod, descricao_prod, imagem_prod, categoria_id_categoria 
                FROM produto;
            ''')
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            products = [
                {
                    'id_prod': row[0],
                    'nome': row[1],
                    'preco': float(row[2]),
                    'descricao': row[3],
                    'imagem': row[4],
                    'categoria': row[5]
                } for row in rows
            ]

            return jsonify(products), 200

        except Exception as e:
            print(f"Erro ao listar produtos: {e}")
            return jsonify({"message": "Erro Interno"}), 500

    def update_product(self, product_id):
        data = request.get_json()
        return self._update(product_id, "produto", "id_prod", data)

    def remove_product(self, product_id):
        return self._remove(product_id, "produto", "id_prod")

    def _update(self, id_value, table, id_column, update_data):
        try:
            conn = self.db.get_conn()
            cursor = conn.cursor()

            set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
            values = list(update_data.values())
            values.append(id_value)

            query = f"UPDATE {table} SET {set_clause} WHERE {id_column} = %s"
            cursor.execute(query, values)
            conn.commit()

            if cursor.rowcount == 0:
                cursor.close()
                conn.close()
                return jsonify({"message": f"{table} não encontrado"}), 404

            cursor.close()
            conn.close()
            return jsonify({"message": f"{table} atualizado com sucesso"}), 200

        except Exception as e:
            print(f"Erro ao atualizar {table}: {e}")
            return jsonify({"message": f"Erro interno: {str(e)}"}), 500

    def _remove(self, id, table, idEspecifico):
        try:
            conn = self.db.get_conn()
            cursor = conn.cursor()
            cursor.execute(f'DELETE FROM {table} WHERE {idEspecifico} = %s', (id,))
            conn.commit()

            if cursor.rowcount == 0:
                cursor.close()
                conn.close()
                return jsonify({"message": f"{table} não encontrado"}), 404

            cursor.close()
            conn.close()
            return jsonify({"message": f"{table} id {idEspecifico} removido com sucesso"}), 200

        except Exception as e:
            print(f"Erro ao remover {table}: {e}")
            return jsonify({"message": f"Erro interno: {str(e)}"}), 500


class CategoryController:
    def __init__(self, db: Database):
        self.db = db
        self.bp = Blueprint('categories', __name__, url_prefix='/api/categoria')

        self.bp.route('/', methods=['POST'])(self.create_categ)
        self.bp.route('/', methods=['GET'])(self.list_categ)
        self.bp.route('/principais/', methods=['GET'])(self.list_categ_principais)
        self.bp.route('/atualizar/<int:categoria_id>/', methods=['POST'])(self.update_categoria)
        self.bp.route('/remove/<int:categoria_id>/', methods=['DELETE'])(self.remove_categoria)

    def create_categ(self):
        data = request.get_json()
        if data is None:
            return jsonify({"message": "JSON inválido ou ausente"}), 400

        nome = data.get('nome')
        imagem = data.get('imagem')
        usuario = data.get('usuario')
        categoria = data.get('sub')

        if nome is None or imagem is None:
            return jsonify({"message": "Campos obrigatórios: nome e imagem"}), 400

        try:
            conn = self.db.get_conn()
            cursor = conn.cursor()

            if categoria is None:
                cursor.execute(
                    '''
                    INSERT INTO categoria (nome_categ, imagm_categ, usuario_id_user)
                    VALUES(%s, %s, %s)
                    RETURNING id_categoria
                    ''', (nome, imagem, usuario)
                )
            else:
                cursor.execute(
                    '''
                    INSERT INTO categoria (nome_categ, imagm_categ, usuario_id_user, categoria_id_categoria)
                    VALUES(%s, %s, %s, %s)
                    RETURNING id_categoria
                    ''', (nome, imagem, usuario, categoria)
                )
            new_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"message": "Categoria Criada", "ID": new_id}), 201

        except Exception as e:
            print(f"Erro ao criar categoria: {e}")
            return jsonify({"message": f"Erro interno: {str(e)}"}), 500

    def list_categ(self):
        try:
            conn = self.db.get_conn()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    id_categoria, 
                    nome_categ,
                    usuario_id_user,
                    categoria_id_categoria
                FROM categoria 
                WHERE categoria_id_categoria IS NOT NULL;
            ''')
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            categories = [
                {
                    'id_categoria': row[0],
                    'nome': row[1],
                    'usuario': row[2],
                    'sub_categoria_de': row[3]
                } for row in rows
            ]

            return jsonify(categories), 200

        except Exception as e:
            print(f"Erro ao listar categorias: {e}")
            return jsonify({"message": "Erro Interno"}), 500

    def list_categ_principais(self):
        try:
            conn = self.db.get_conn()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id_categoria, nome_categ, imagm_categ, usuario_id_user
                FROM categoria 
                WHERE categoria_id_categoria IS NULL;
            ''')
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            categories = [
                {
                    'id_categoria': row[0],
                    'nome': row[1],
                    'imagem': row[2],
                    'usuario': row[3]
                } for row in rows
            ]

            return jsonify(categories), 200

        except Exception as e:
            print(f"Erro ao listar categorias principais: {e}")
            return jsonify({"message": "Erro Interno"}), 500

    def update_categoria(self, categoria_id):
        data = request.get_json()
        return self._update(categoria_id, "categoria", "id_categoria", data)

    def remove_categoria(self, categoria_id):
        return self._remove(categoria_id, "categoria", "id_categoria")

    def _update(self, id_value, table, id_column, update_data):
        try:
            conn = self.db.get_conn()
            cursor = conn.cursor()

            set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
            values = list(update_data.values())
            values.append(id_value)

            query = f"UPDATE {table} SET {set_clause} WHERE {id_column} = %s"
            cursor.execute(query, values)
            conn.commit()

            if cursor.rowcount == 0:
                cursor.close()
                conn.close()
                return jsonify({"message": f"{table} não encontrado"}), 404

            cursor.close()
            conn.close()
            return jsonify({"message": f"{table} atualizado com sucesso"}), 200

        except Exception as e:
            print(f"Erro ao atualizar {table}: {e}")
            return jsonify({"message": f"Erro interno: {str(e)}"}), 500

    def _remove(self, id, table, idEspecifico):
        try:
            conn = self.db.get_conn()
            cursor = conn.cursor()
            cursor.execute(f'DELETE FROM {table} WHERE {idEspecifico} = %s', (id,))
            conn.commit()

            if cursor.rowcount == 0:
                cursor.close()
                conn.close()
                return jsonify({"message": f"{table} não encontrado"}), 404

            cursor.close()
            conn.close()
            return jsonify({"message": f"{table} id {idEspecifico} removido com sucesso"}), 200

        except Exception as e:
            print(f"Erro ao remover {table}: {e}")
            return jsonify({"message": f"Erro interno: {str(e)}"}), 500


class BannerController:
    def __init__(self, db: Database):
        self.db = db
        self.bp = Blueprint('banners', __name__, url_prefix='/api/banner')

        self.bp.route('/', methods=['POST'])(self.create_banner)
        self.bp.route('/', methods=['GET'])(self.list_banner)
        self.bp.route('/atualizar/<int:banner_id>/', methods=['POST'])(self.update_banner)
        self.bp.route('/remove/<int:banner_id>/', methods=['DELETE'])(self.remove_banner)

    def create_banner(self):
        data = request.get_json()
        if data is None:
            return jsonify({"message": "JSON inválido ou ausente"}), 400

        titulo = data.get('titulo')
        sub_titulo = data.get('sub_titulo')
        imagem = data.get('imagem')
        usuario = data.get('usuario')

        if titulo is None or imagem is None:
            return jsonify({"message": "Campos obrigatórios: titulo e imagem"}), 400

        try:
            conn = self.db.get_conn()
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO banners (titulo_banner, sub_titulo_banner, imagem_banner, usuario_id_user)
                VALUES(%s, %s, %s, %s)
                RETURNING id_banner
                ''', (titulo, sub_titulo, imagem, usuario)
            )
            new_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({"message": "Banner Criado", "ID": new_id}), 201

        except Exception as e:
            print(f"Erro ao criar banner: {e}")
            return jsonify({"message": f"Erro interno: {str(e)}"}), 500

    def list_banner(self):
        try:
            conn = self.db.get_conn()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id_banner, titulo_banner, sub_titulo_banner, imagem_banner, usuario_id_user 
                FROM banners;
            ''')
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            banners = [
                {
                    'id_banner': row[0],
                    'titulo': row[1],
                    'sub_titulo': row[2],
                    'imagem': row[3],
                    'usuario': row[4]
                } for row in rows
            ]

            return jsonify(banners), 200

        except Exception as e:
            print(f"Erro ao listar banners: {e}")
            return jsonify({"message": "Erro Interno"}), 500

    def update_banner(self, banner_id):
        data = request.get_json()
        return self._update(banner_id, "banners", "id_banner", data)

    def remove_banner(self, banner_id):
        return self._remove(banner_id, "banners", "id_banner")

    def _update(self, id_value, table, id_column, update_data):
        try:
            conn = self.db.get_conn()
            cursor = conn.cursor()

            set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
            values = list(update_data.values())
            values.append(id_value)

            query = f"UPDATE {table} SET {set_clause} WHERE {id_column} = %s"
            cursor.execute(query, values)
            conn.commit()

            if cursor.rowcount == 0:
                cursor.close()
                conn.close()
                return jsonify({"message": f"{table} não encontrado"}), 404

            cursor.close()
            conn.close()
            return jsonify({"message": f"{table} atualizado com sucesso"}), 200

        except Exception as e:
            print(f"Erro ao atualizar {table}: {e}")
            return jsonify({"message": f"Erro interno: {str(e)}"}), 500

    def _remove(self, id, table, idEspecifico):
        try:
            conn = self.db.get_conn()
            cursor = conn.cursor()
            cursor.execute(f'DELETE FROM {table} WHERE {idEspecifico} = %s', (id,))
            conn.commit()

            if cursor.rowcount == 0:
                cursor.close()
                conn.close()
                return jsonify({"message": f"{table} não encontrado"}), 404

            cursor.close()
            conn.close()
            return jsonify({"message": f"{table} id {idEspecifico} removido com sucesso"}), 200

        except Exception as e:
            print(f"Erro ao remover {table}: {e}")
            return jsonify({"message": f"Erro interno: {str(e)}"}), 500


class App:
    def __init__(self):
        self.app = Flask(__name__)
        self.db = Database()
        self.configure_app()
        self.register_routes()

    def configure_app(self):
        self.app.secret_key = '4af61d297ff9bcb7358f01f9ae61a6fc'
        self.app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
        self.app.config.update(
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SECURE=True,  # Mudar para True em produção
            SESSION_COOKIE_SAMESITE='None',
        )
        CORS(self.app,
             origins=[
                 "http://localhost:5173",
                 "http://localhost:5174",
                 "https://barbalao.vercel.app",
                 "https://supreme-carnival-x5xvwq7494qxh6r7j-5173.app.github.dev",
                 "https://dark-sorcery-q76pqgjx9r6q2xqrj-5173.app.github.dev",
                 "https://dark-sorcery-q76pqgjx9r6q2xqrj-5174.app.github.dev",
                 "https://fantastic-memory-wr9xwxpqx4wvf95jv.github.dev"
             ],
             supports_credentials=True,
             allow_headers=["Content-Type", "Authorization"])

    def register_routes(self):
        auth_controller = AuthController(self.db)
        product_controller = ProductController(self.db)
        category_controller = CategoryController(self.db)
        banner_controller = BannerController(self.db)

        self.app.register_blueprint(auth_controller.bp)
        self.app.register_blueprint(product_controller.bp)
        self.app.register_blueprint(category_controller.bp)
        self.app.register_blueprint(banner_controller.bp)

    def run(self):
        port = int(os.environ.get("PORT", 5000))
        self.app.run(host="0.0.0.0", port=port)


if __name__ == '__main__':
    app_instance = App()
    app_instance.run()
