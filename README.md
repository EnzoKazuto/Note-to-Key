# Note-to-Key — Controle por Som em Tempo Real

O **Note-to-Key** detecta notas musicais pelo microfone e **pressiona teclas automaticamente**, conforme um mapeamento configurado.  
Ideal para criar automações, tocar jogos com instrumentos ou controlar ações via som.

---

## ⚙️ Requisitos do Sistema

- **Python 3.11.8**
- **Microfone funcional**
- **Windows (recomendado)**  
  *(O módulo `keyboard` precisa de privilégios de administrador no Windows)*

---

## Instalação e Execução — Passo a Passo

### Alterar as teclas do jogo

Antes de usar o programa, altere as teclas de setas do jogo para

| Direção | Tecla |
|----------|--------|
| Cima | **O** |
| Baixo | **L** |
| Esquerda | **N** |
| Direita | **M** |

### Baixar o projeto

Abra o **Prompt de Comando (CMD)** ou **terminal do VS Code** e execute:

```bash
git clone https://github.com/seu-usuario/Note-to-Key.git
cd Note-to-Key
```

### Instalar as dependências

```bash
pip install -r requirements.txt
```
### Executar o programa

Use o comando abaixo no terminal para iniciar a detecção de notas:
```bash
python main.py
```

### Dica

Você pode alterar as notas e teclas dentro do código:

Abra o arquivo main.py com o Bloco de Notas ou VS Code.

Procure o dicionário note_to_key.

Edite conforme quiser (por exemplo, mude "C5": "n" para outra tecla).


