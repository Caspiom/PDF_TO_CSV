# Como Abrir Arquivos CSV Corretamente no Excel

## ⚠️ Problema Comum
Ao abrir arquivos CSV no Excel com duplo clique, os dados podem aparecer formatados incorretamente quando:
- O arquivo usa ponto e vírgula (`;`) como delimitador
- O arquivo contém vírgulas como parte do texto

## ✅ Solução Recomendada

### Método de Importação Correta
Siga estes passos para garantir que o arquivo CSV seja aberto corretamente no Excel:

1. **Abra o Excel** (não dê duplo clique no arquivo CSV diretamente)
2. Navegue até: Dados > Obter Dados > De Arquivo > De Texto/CSV
3. Selecione o arquivo CSV que deseja abrir
4. Na janela de importação:
- Em "Origem do arquivo": Selecione **65001: Unicode (UTF-8)**
- Em "Delimitador": Escolha **Ponto e vírgula (;)**
- Marque **"Meus dados têm cabeçalhos"** (se aplicável)
5. Clique em **Carregar**

## ℹ️ Por Que Isso Acontece?
O Excel assume por padrão que:
- Arquivos CSV usam vírgula (`,`) como delimitador
- O formato segue as configurações regionais do sistema
