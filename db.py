import sqlite3
from encrypt import hash_password

def start_db():
    try:
        conn = sqlite3.connect("bar_balao.db")
        cursor = conn.cursor()
        # cursor.execute("DROP TABLE IF EXISTS categoria CASCADE;")
        # cursor.execute("DROP TABLE IF EXISTS produto CASCADE")
        # cursor.execute("DROP TABLE IF EXISTS usuario CASCADE")
        # cursor.execute("DROP TABLE IF EXISTS adicionais CASCADE")
        # cursor.execute("DROP TABLE IF EXISTS categoria_has_adicionais CASCADE")
        # cursor.execute("DROP TABLE IF EXISTS banners CASCADE")
        # conn.commit()


        cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS usuario (
                    id_user     SERIAL  PRIMARY  KEY,
                    nome_user   TEXT    NOT NULL UNIQUE,
                    hash        TEXT    NOT NULL
                );
            '''
        )
        
        # cursor.execute(
        #     ''' 
        #         INSERT INTO usuario(nome_user, hash)
        #         VALUES(%s, %s);
        #     ''', ('AdminT', hash_password('Barbalao123'))
        # )

        cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS categoria (
                    id_categoria            SERIAL  PRIMARY KEY,
                    nome_categ              TEXT    NOT NULL,
                    imagm_categ             TEXT    NOT NULL,
                    usuario_id_user         INT,
                    categoria_id_categoria  INT,

                    FOREIGN KEY(categoria_id_categoria) REFERENCES categoria(id_categoria),
                    FOREIGN KEY(usuario_id_user) REFERENCES usuario(id_user)
                )
            '''
        )

        cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS produto (
                    id_prod                 SERIAL  PRIMARY KEY,
                    nome_prod               TEXT    NOT NULL,
                    preco_prod              REAL    NOT NULL,
                    descricao_prod          TEXT    NOT NULL,
                    imagem_prod             TEXT    NOT NULL,
                    categoria_id_categoria  INT     NOT NULL,
                    usuario_id_user         INT,


                    FOREIGN KEY(categoria_id_categoria) REFERENCES categoria(id_categoria),
                    FOREIGN KEY(usuario_id_user) REFERENCES usuario(id_user)
                );
            '''
        )

        cursor.execute (
            '''
                CREATE TABLE IF NOT EXISTS adicionais (
                    id_adic             SERIAL  PRIMARY KEY,
                    nome_adic           TEXT    NOT NULL,
                    imagem_adic         TEXT    NOT NULL,
                    usuario_id_user    INT,

                    FOREIGN KEY(usuario_id_user) REFERENCES usuario(id_user)
                )
            '''
        )

        cursor.execute (
            '''
                CREATE TABLE IF NOT EXISTS categoria_has_adicionais (
                    adicionais_id_adic      INT     NOT NULL,
                    categoria_id_categoria  INT     NOT NULL,
                    preco_adic              REAL,

                    FOREIGN KEY(adicionais_id_adic) REFERENCES adicionais(id_adic),
                    FOREIGN KEY(categoria_id_categoria) REFERENCES categoria(id_categoria)
                )
            '''
        )

        cursor.execute(
            '''
                CREATE TABLE IF NOT EXISTS banners (
                    id_banner               SERIAL  PRIMARY KEY,
                    titulo_banner           TEXT    NOT NULL,
                    sub_titulo_banner       TEXT,
                    imagem_banner           TEXT    NOT NULL,
                    usuario_id_user         INT,
                    categoria_id_categoria  INT,

                    FOREIGN KEY(usuario_id_user) REFERENCES usuario(id_user),
                    FOREIGN KEY(categoria_id_categoria) REFERENCES categoria(id_categoria)
                )
            '''
        )

        
        
        conn.commit()
        conn.close()

    except Exception as e: 
        print(f"Erro não legal: {e}")
        continue
