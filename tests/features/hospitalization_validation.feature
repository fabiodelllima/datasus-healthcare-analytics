# language: pt
Funcionalidade: Validação de Internações SIH/DataSUS
  Como analista de saúde
  Eu quero processar apenas internações válidas
  Para garantir qualidade das análises e KPIs

  Contexto:
    Dado que o pipeline ETL está configurado
    E os dados brutos do DataSUS foram extraídos

  Cenário: Aceitar internação válida
    Dado uma internação com os seguintes dados:
      | campo      | valor      |
      | N_AIH      | 1224100061118 |
      | DT_INTER   | 2024-01-15 |
      | DT_SAIDA   | 2024-01-20 |
      | IDADE      | 45         |
      | VAL_TOT    | 1500.00    |
    Quando o pipeline de validação executa
    Então o registro deve ser aceito
    E deve calcular stay_days como 5
    E deve calcular daily_cost como 300.00

  Cenário: Rejeitar data saída anterior à entrada
    Dado uma internação com DT_INTER "2024-01-20"
    E DT_SAIDA "2024-01-15"
    Quando o pipeline de validação executa
    Então o registro deve ser rejeitado
    E o log deve conter "validação de datas falhou"

  Cenário: Rejeitar idade inválida (negativa)
    Dado uma internação com IDADE "-5"
    Quando o pipeline de validação executa
    Então o registro deve ser rejeitado
    E o log deve conter "idade fora do range válido"

  Cenário: Rejeitar idade inválida (acima de 120)
    Dado uma internação com IDADE "150"
    Quando o pipeline de validação executa
    Então o registro deve ser rejeitado
    E o log deve conter "idade fora do range válido"

  Cenário: Rejeitar valor total negativo
    Dado uma internação com VAL_TOT "-100.50"
    Quando o pipeline de validação executa
    Então o registro deve ser rejeitado
    E o log deve conter "valor monetário negativo"

  Cenário: Rejeitar internação com campo crítico nulo
    Dado uma internação com N_AIH "NULL"
    Quando o pipeline de validação executa
    Então o registro deve ser rejeitado
    E o log deve conter "campo crítico ausente"

  Cenário: Remover duplicatas
    Dado 3 internações com os mesmos dados:
      | N_AIH         | DT_INTER   | DT_SAIDA   |
      | 1224100061118 | 2024-01-15 | 2024-01-20 |
      | 1224100061118 | 2024-01-15 | 2024-01-20 |
      | 1224100061118 | 2024-01-15 | 2024-01-20 |
    Quando o pipeline de limpeza executa
    Então apenas 1 registro deve permanecer

  Esquema do Cenário: Calcular faixa etária corretamente
    Dado uma internação com IDADE "<idade>"
    Quando o enriquecimento de dados executa
    Então age_group deve ser "<faixa_esperada>"

    Exemplos:
      | idade | faixa_esperada |
      | 10    | 0-17           |
      | 18    | 18-29          |
      | 25    | 18-29          |
      | 30    | 30-44          |
      | 45    | 45-59          |
      | 60    | 60+            |
      | 85    | 60+            |

  Cenário: Calcular tempo permanência
    Dado uma internação com DT_INTER "2024-01-10"
    E DT_SAIDA "2024-01-15"
    Quando o enriquecimento de dados executa
    Então stay_days deve ser 5

  Cenário: Evitar divisão por zero no custo diário
    Dado uma internação com VAL_TOT "1000.00"
    E stay_days "0"
    Quando o enriquecimento de dados executa
    Então daily_cost deve usar stay_days mínimo de 1
    E daily_cost deve ser 1000.00

  Cenário: Marcar óbito corretamente
    Dado uma internação com MORTE "1"
    Quando o enriquecimento de dados executa
    Então death deve ser True

  Cenário: Marcar alta corretamente
    Dado uma internação com MORTE "0"
    Quando o enriquecimento de dados executa
    Então death deve ser False
