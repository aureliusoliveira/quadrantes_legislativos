# Testes de contrato com as fontes da Câmara

O PRD promete que qualquer número exibido é rastreável até o dado bruto. Essa
promessa depende de uma fonte que o projeto não controla: se a Câmara renomear
uma coluna, mudar um tipo ou reorganizar um arquivo, o pipeline pode continuar
rodando e entregando número errado. Os testes de contrato existem para que essa
mudança apareça como um teste vermelho, e não como um ranking estranho no
dashboard.

Eles ficam em `tests/test_contrato_api.py` e rodam no CI a cada push.

## Duas fontes, dois contratos

**Cadastro de deputados — API REST, JSON.** O contrato é o envelope `dados` e os
sete campos de `ultimoStatus` que a padronização extrai. Dois deles decidem quem
entra no ranking: `situacao` (só entra quem está em "Exercício") e
`idLegislatura`.

**Bases anuais — arquivos CSV consolidados.** Proposições, temas e autores vêm
de arquivo anual, não da API. Aqui o contrato é o cabeçalho: nome de coluna,
separador `;` e o formato do conteúdo. As colunas que o pipeline lê estão
declaradas em `COLUNAS_DA_FONTE`, em cada carregador, e o teste de contrato lê
essa mesma lista — não há como uma passar sem a outra.

## Por que fixture e não rede

Teste que faz requisição falha por instabilidade da fonte, não por defeito do
código, e vira ruído que se aprende a ignorar. As fixtures em
`tests/fixtures/api/` são amostras reais e minúsculas: três proposições, cinco
temas, sete autorias, um deputado.

O que importa nelas é a forma, não o volume — e os casos de borda que o pipeline
precisa tratar:

- proposição **sem** `ultimoStatus_descricaoSituacao`, que o cálculo descarta em
  vez de classificar como "em andamento";
- autoria de órgão (Senado, comissão) **sem** `idDeputadoAutor`, que é o recorte
  que define o escopo do produto.

Uma fixture que perde esses casos deixa de proteger contra a regressão que
importa. Ao recapturar, confira se eles continuam lá.

## Recapturar

```
uv run python scripts/capturar_fixtures.py
```

O script baixa só o início de cada arquivo consolidado — os originais passam de
50 MB — e escolhe as linhas por critério, porque as primeiras nem sempre trazem
o caso de borda.

**Leia o diff antes de commitar.** Se uma coluna mudou de nome, o teste vai
passar de novo — sobre a fixture nova — e a mudança de contrato terá sido
apagada em vez de tratada. Recapture depois de entender a mudança, não para
fazer o teste ficar verde.
