# Prompt de abertura — Claude Code / Quadrantes

> Copie o bloco abaixo e cole como primeira mensagem no Claude Code, com o repositório aberto.

---

## Contexto

Estou retomando um projeto pessoal de dados chamado **Quadrantes da Produtividade Legislativa**. Ele nasceu como TCC de MBA e hoje está parado. Minha intenção agora é **reconstruí-lo como um produto de dados real**, com padrão profissional — tratando-o como se fosse trabalho remunerado, não exercício acadêmico.

O projeto cruza duas dimensões dos deputados federais brasileiros a partir de dados públicos da Câmara: **produtividade legislativa** (score ponderado de proposições) e **custo de mandato** (gastos com CEAP). Classifica os parlamentares em quatro quadrantes e gera rankings.

**Usuário primário:** jornalista de dados.
**Escopo:** plataforma contínua, com legislatura como dimensão — não retrato de uma única legislatura.

Existe um PRD no repositório (`docs/PRD.md`). **Leia-o antes de propor qualquer coisa.** Ele define escopo, não-objetivos, métricas de sucesso e as fases planejadas.

## Estado atual do código

Hoje o projeto vive em dois repositórios:

- `quadrantes_legislativos` — coleta e análise. Scripts Python orientados a objetos em `quadrantes_produtividade/legisdata/` (subpastas `coleta` e `indicadores`, mais `config.py`), com `main_coleta.py` como entrypoint. Consome a API oficial da Câmara (`dadosabertos.camara.leg.br`) e arquivos de CEAP.
- `dashboard-quadrantes` — app Streamlit servido no Streamlit Cloud, lendo um CSV de resultados versionado no Git.

### Problemas que já identifiquei

1. **Range de anos hardcoded** em `main_coleta.py` (`for ano in range(2023, 2026)`) — exclui o ano corrente, então mesmo rodando hoje o pipeline não traz dado novo.
2. **Coletor de deputados desativado** — a chamada `coletor_deputados.baixar()` está comentada. Isso importa porque suplentes e substituições não são refletidos.
3. **`requests` ausente do `requirements.txt`**, embora o código de coleta dependa dele.
4. **Duplicação de dashboard** — existe uma cópia do código do dashboard dentro de `quadrantes_legislativos`, além do repositório próprio. Editar um e esquecer o outro é questão de tempo.
5. **CSV como camada de persistência** — a saída da coleta vira CSV commitado no Git, sem separação entre dado bruto e tratado, sem histórico e sem rastreabilidade.

## Restrições

- **Custo:** o projeto deve operar dentro de camadas gratuitas. Nada de Cloud Composer ou serviços com cobrança por tempo de ambiente ligado. GitHub Actions com cron é orquestração aceitável para um batch mensal.
- **Tempo:** 5 a 10 horas por semana. Cada incremento precisa terminar em algo funcionando — o projeto não pode virar canteiro de obras.
- **Cadência do produto:** mensal. Não há caso de uso para streaming ou tempo real.
- **Sem resume-driven development.** Adote uma ferramenta porque o problema pede, não porque a palavra é boa no currículo.

## O que quero desta sessão (Fase 1 — Fundação)

1. Ler o PRD e o código atual, e me devolver um diagnóstico com o que você encontrou além do que listei.
2. Propor um plano para a Fase 1 antes de escrever código — quero revisar e aprovar antes.
3. A Fase 1 deve cobrir: consolidação dos dois repositórios em um só, ambiente reproduzível, correção dos cinco problemas acima, e a fundação de testes automatizados descrita abaixo, rodando em CI.

## Testes automatizados

Testes não são item opcional deste projeto — são requisito de produto. A credibilidade do Quadrantes depende de que qualquer número exibido seja reproduzível e rastreável até o dado bruto. Sem testes, isso é promessa; com testes, é garantia.

Quero cobertura em quatro frentes distintas:

**1. Testes unitários da lógica de indicadores.** O cálculo de produtividade ponderada, a lógica de ranking composto e a classificação por quadrante são regra de negócio pura e devem ser testados isoladamente, com casos de borda explícitos: produtividade zero, gasto próximo de zero, empates no ranking, outliers extremos.

**2. Testes de qualidade de dados.** Diferentes dos unitários — validam o dado, não o código. Contagem esperada de parlamentares por legislatura, unicidade de chaves, ausência de nulos em campos críticos, faixas plausíveis de valores, integridade referencial entre proposições e parlamentares.

**3. Testes de contrato com a fonte.** A API da Câmara pode mudar schema, renomear campo ou ficar indisponível. Quero testes que falhem alto e cedo quando a fonte mudar, em vez de dado silenciosamente errado chegando ao dashboard.

**4. Testes de regressão dos indicadores.** Um conjunto pequeno de dados de referência com resultados conhecidos, garantindo que refatorações não alterem números já publicados sem que isso seja uma decisão consciente. Se um número mudar, o teste deve quebrar e me obrigar a justificar.

Expectativas de processo:

- Testes rodando em CI a cada push, bloqueando merge quando falham.
- Fixtures com respostas reais da API salvas localmente — nenhum teste deve depender de rede.
- Ao corrigir qualquer um dos cinco problemas listados acima, escreva primeiro o teste que reproduz a falha.
- Estudei TDD e quero praticá-lo de verdade aqui. Quando fizer sentido, proponha o ciclo teste-primeiro em vez de código-primeiro.

Não quero meta de percentual de cobertura. Quero os caminhos críticos de transformação cobertos e testes que documentem intenção.

## Como quero trabalhar

- Explique decisões de arquitetura antes de implementá-las. Se houver mais de um caminho razoável, apresente as opções com os trade-offs.
- Prefira mudanças incrementais e revisáveis a refatorações grandes de uma vez.
- Commits pequenos, com mensagens que expliquem o porquê.
- Se algo que eu pedir for tecnicamente questionável, me diga. Não quero concordância automática.
- Assuma que estou usando este projeto também para aprender práticas de engenharia de dados que ainda não pratiquei em produção — orquestração, camadas de dados, testes de dados, auditoria e reprocessamento. Quando essas oportunidades aparecerem, aponte.

Comece lendo o PRD e o código, e me traga o diagnóstico. Não escreva código ainda.
