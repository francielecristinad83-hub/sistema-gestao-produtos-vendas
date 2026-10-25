import sqlite3

conexao = sqlite3.connect("sistema_gestao.db")
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS vendas
( id INTEGER PRIMARY KEY AUTOINCREMENT,
produto TEXT NOT NULL,
quantidade INTEGER NOT NULL,
total REAL NOT NULL)""")

conexao.commit()

produtos = []
vendas = []

print("SISTEMA DE GESTÃO")

def cadastrar_produto():
    nome = input("Digite o nome do produto: ").strip()

    if not nome:
        print("O nome do produto não pode ficar vazio.")
        return

    cursor.execute(
        "SELECT nome FROM produtos WHERE nome = ? COLLATE NOCASE",
        (nome,)
    )

    if cursor.fetchone():
        print("Esse produto já está quadastrado.")
        return

    for produto in produtos:
        if produto["nome"].lower() == nome.strip().lower():
            print("Esse produto já está cadastrado.")
            return

    try:
        preco = float(input("Digite o preço do produto: "))

        quantidade = int(input("Digite a quantidade em estoque: "))

        if preco <= 0:
            print("O preço deve ser maior que zero.")
            return

        if quantidade < 0:
            print("A quantidade não pode ser negativa.")
            return

    except ValueError:
        print("Erro! Digite números válidos para preço e quantidade.")
        return

    cursor.execute("INSERT INTO produtos (nome, preco, quantidade) VALUES (?, ?, ?)",
                  (nome, preco, quantidade)
    )
    conexao.commit()
    print("Produto cadastrado com sucesso!")

def listar_produtos():
    print("\nPRODUTOS CADASTRADOS")

    cursor.execute("SELECT nome, preco, quantidade FROM produtos")
    produtos_banco = cursor.fetchall()

    if not produtos_banco:
        print("Nenhum produto cadastrado.")
        return

    for numero, produto in enumerate(produtos_banco, start=1):
        print(f"\n{numero}. {produto[0]}")
        print(f"Preço: R${produto[1]:.2f}")
        print(f"Estoque: {produto[2]}")

def buscar_produto():
    nome_busca = input("Digite o nome do produto: ").strip()

    cursor.execute("SELECT nome, preco, quantidade FROM produtos WHERE nome = ? COLLATE NOCASE",
(nome_busca,)
    )
    produto = cursor.fetchone()

    if produto:
        print("\nProduto encontrado!")
        print(f"Nome: {produto[0]}")
        print(f"Preço: R${produto[1]:.2f}")
        print(f"Estoque: {produto[2]}")
    else:
        print("Produto não encontrado.")

def editar_produto():
   nome_editar = input("Digite o nome do produto que deseja editar: ").strip()

   cursor.execute(
       "SELECT nome, preco, quantidade FROM produtos WHERE nome = ? COLLATE NOCASE",
         (nome_editar,)
  )
   produto = cursor.fetchone()

   if not produto:
       print("Produto não encontrado.")
       return
   print("\nProduto encontrado!")
   print(f"Nome: {produto[0]}")
   print(f"Preço atual: R${produto[1]:.2f}")
   print(f"Estoque atual: {produto[2]}")

   try:
       novo_preco = float(input("Digite o novo preço: "))
       nova_quantidade = int(input("Digite  nova quantidade em estoque: "))

       if novo_preco <= 0:
           print("O preço deve ser maior que zero.")
           return

   except ValueError:
       print("Erro! Digite números válidos para preço e quantidade.")
       return

   cursor.execute(
       "UPDATE produtos SET preco = ?, quantidade = ? WHERE nome = ? COLLATE NOCASE",
                  (novo_preco, nova_quantidade, produto[0]))

   conexao.commit()
   print("Produto alterado com sucesso!")

def excluir_produto():
    nome_excluir = input("Digite o nome do produto que deseja excluir: ").strip()

    if not nome_excluir:
        print("O nome do produto não pode ficar vazio.")
        return

    cursor.execute(
        "SELECT nome FROM produtos WHERE nome = ? COLLATE NOCASE",
        (nome_excluir,)
    )
    produto = cursor.fetchone()

    if not produto:
        print("Produto não encontrado.")
        return

    cursor.execute(
        "DELETE FROM produtos WHERE nome = ? COLLATE NOCASE",
        (produto[0],)
    )
    conexao.commit()

    print("Produto excluído com sucesso!")

def registrar_venda():
    nome_venda = input("Digite o nome do produto vendido: ").strip()

    if not nome_venda:
        print("O nome do produto não pode ficar vazio.")
        return

    cursor.execute(
        "SELECT nome, preco, quantidade FROM produtos WHERE nome = ? COLLATE NOCASE",
        (nome_venda,)
    )
    produto = cursor.fetchone()

    if produto is None:
        print("Produto não encontrado.")
        return

    nome, preco, quantidade = produto

    print("\nProduto encontrado!")
    print("Nome:", nome)
    print(f"Preço: R$ {preco:.2f}")
    print("Estoque disponível:", quantidade)

    try:
        quantidade_venda = int(input("Digite a quantidade vendida: "))

    except ValueError:
        print("Erro! Digite uma quantidade válida.")
        return

    if quantidade_venda <= 0:
        print("A quantidade deve ser maior que zero.")
        return

    if quantidade_venda > quantidade:
        print("Estoque insuficiente!")
        return

    total = preco * quantidade_venda
    estoque_restante = quantidade - quantidade_venda

    try:
        cursor.execute(
            "UPDATE produtos SET quantidade = ? WHERE nome = ? COLLATE NOCASE",
            (estoque_restante, nome)
        )

        cursor.execute(
            "INSERT INTO vendas (produto, quantidade, total) VALUES (?, ?, ?)",
            (nome, quantidade_venda, total)
        )

        conexao.commit()

    except sqlite3.Error:
        conexao.rollback()
        print("Erro ao registrar a venda. Nenhuma alteração foi salva.")
        return

    conexao.commit()

    print("\nVenda realizada com sucesso!")
    print(f"Total da venda: R$ {total:.2f}")
    print("Estoque restante:", estoque_restante)

def mostrar_historico():
    cursor.execute(
        "SELECT id, produto, quantidade, total FROM vendas ORDER BY id"
    )
    vendas_banco = cursor.fetchall()
    cursor.execute("SELECT SUM(total) FROM vendas")
    faturamento = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*) FROM vendas")
    quantidade_vendas = cursor.fetchone()[0]

    cursor.execute("""
        SELECT produto, SUM(quantidade) AS total_vendido
        FROM vendas 
        GROUP BY produto
        ORDER BY total_vendido DESC""")
    produtos_mais_vendidos = cursor.fetchall()

    if not vendas_banco:
        print("Nenhuma venda registrada!")
        return

    print("\n--- HISTÓRICO DE VENDAS ---")
    print(f"Faturamento total: R${faturamento:.2f}")
    print(f"Quantidade de vendas: {quantidade_vendas}")

    for venda in vendas_banco:
        print(f"\nVenda número: {venda[0]}")
        print(f"Produto: {venda[1]}")
        print(f"Quantidade: {venda[2]}")
        print(f"Total: R${venda[3]:.2f}")

    print("\n --- PRODUTOS MAIS VENDIDOS ---")

    for produto in produtos_mais_vendidos:
        unidade = "unidade" if produto[1] == 1 else "unidades"
        print(f"{produto[0]}: {produto[1]} {unidade}")


while True:
    print("\nMENU PRINCIPAL")
    print("1 - Cadastrar produto")
    print("2 - Listar produtos")
    print("3 - Buscar produto")
    print("4 - Editar produto")
    print("5 - Excluir produto")
    print("6 - Registrar venda")
    print("7 - Relatórios")
    print("0 - Sair")

    opcao = input("\nEscolha uma opção: ")

    if opcao == "1":
       cadastrar_produto()

    elif opcao == "2":
        listar_produtos()

    elif opcao == "3":
        buscar_produto()

    elif opcao == "4":
         editar_produto()

    elif opcao == "5":
       excluir_produto()

    elif opcao == "6":
        registrar_venda()


    elif opcao == "7":
        mostrar_historico()


    elif opcao == "0":
        conexao.close()
        print("Sistema encerrado. Até mais!")
        break

    else:
        print("Opção inválida!")

