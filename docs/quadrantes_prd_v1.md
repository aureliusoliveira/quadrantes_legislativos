# PRD — Quadrantes da Produtividade Legislativa

**Versão:** 0.1 (rascunho para revisão)
**Autor:** Aurelius Oliveira
**Data:** julho de 2026
**Status:** em definição

---

## 1. Problema

Dados legislativos brasileiros são abertos, mas não são utilizáveis. A Câmara dos Deputados publica proposições, tramitações, gastos de CEAP e dados cadastrais em APIs e arquivos CSV — mas transformá-los em algo interpretável exige coleta, tratamento, integração e modelagem que estão fora do alcance da maior parte de quem precisaria usá-los.

O resultado prático: jornalistas que cobrem política dependem de rankings de terceiros (DIAP, Congresso em Foco, Atlas Político) cujas metodologias variam e nem sempre são auditáveis, ou fazem apuração manual caso a caso — o que não escala e não permite comparação sistemática.

Existe também um problema de continuidade: as análises disponíveis costumam ser retratos pontuais. Não há uma base que permita perguntar "esse deputado melhorou ou piorou em relação à legislatura anterior?".

## 2. Usuários

**Primário: jornalista de dados / repórter de política.**
Precisa de um ponto de partida confiável para apuração: quem está fora da curva, em que direção, e com que dado por trás. Tem repertório para lidar com nuance metodológica e responsabilidade editorial sobre o que publica. É também quem amplifica — uma matéria baseada no Quadrantes alcança mais gente do que o dashboard alcançaria sozinho.

**Secundários:**
- Pesquisador de ciência política (precisa da base bruta e da metodologia aberta)
- Cidadão engajado (chega via imprensa, não via consulta direta)
- Organizações de controle social e transparência

O produto é desenhado para o primário. Os secundários são atendidos por consequência, não por adaptação de interface.

## 3. Proposta de valor

Uma plataforma pública e contínua que cruza **custo de mandato** e **produtividade legislativa** de deputados federais, com metodologia aberta e auditável, permitindo identificar assimetrias e acompanhar sua evolução ao longo de legislaturas.

O diferencial em relação aos rankings existentes:
- **Metodologia explícita e versionada** — qualquer número pode ser rastreado até o dado bruto
- **Código e dados abertos** — reprodutível por terceiros
- **Continuidade histórica** — comparação entre legislaturas, não retrato pontual
- **Acesso programático** — dados exportáveis para quem quer fazer a própria análise

## 4. Escopo da v1

**Entra:**
- Cobertura da 57ª legislatura (2023-2026), com modelo preparado para legislaturas anteriores e futuras
- Indicadores: produtividade legislativa ponderada, custo CEAP ajustado, classificação por quadrante, ranking composto
- Métricas de eficácia de tramitação (taxas de sucesso, fracasso e tramitação em aberto)
- Atualização automática mensal
- Dashboard público com filtros por UF, partido e legislatura
- Exportação de dados (CSV/JSON) e metodologia documentada
- Domínio próprio

**Fica para depois:**
- IAPD (Indicador de Atuação Parlamentar Democrática) — ver seção 7
- Cobertura do Senado
- Retroalimentação de legislaturas anteriores à 57ª
- API pública documentada
- Análise semântica de proposições e discursos

## 5. Não-objetivos

Esta seção existe para impedir que o produto derive para algo que ele não pode sustentar.

**O Quadrantes não é um detector de corrupção ou de má conduta.** O modelo mede volume ponderado de proposições e gasto de cota. Não mede ética, integridade, ou aderência a valores democráticos. Deputados envolvidos em escândalos podem aparecer bem posicionados — e isso é uma limitação conhecida e documentada do modelo, não um erro.

**O Quadrantes não emite juízo sobre parlamentares individuais.** Ele expõe posição relativa em duas dimensões mensuráveis. A interpretação e a apuração são responsabilidade de quem usa.

**O Quadrantes não é uma ferramenta de tempo real.** Dado legislativo tem cadência mensal ou menor. Não há caso de uso que justifique streaming.

**O Quadrantes não substitui apuração jornalística.** É ponto de partida, não conclusão.

## 6. Métricas de sucesso

**Produto:**
- Pipeline executa mensalmente sem intervenção manual (taxa de sucesso das cargas)
- Dado disponível no dashboard em até 7 dias após publicação na fonte
- Zero divergência entre número exibido e dado bruto rastreável
- Citações ou uso do projeto por veículos de imprensa ou pesquisadores

**Aprendizado (PBL):**
- Cada camada da plataforma construída com prática defensável em entrevista técnica
- Cobertura de testes de dados nas transformações críticas
- Documentação de arquitetura que sustente uma conversa técnica sem consulta ao código

## 7. Evolução planejada: IAPD

O modelo atual tem uma limitação conceitual reconhecida: produtividade medida por volume não captura qualidade nem conduta. O **Indicador de Atuação Parlamentar Democrática** é a resposta proposta, incorporando dimensões como participação efetiva em comissões, transparência e prestação de contas, e conduta no uso de recursos públicos.

O IAPD não entra na v1 porque exige fontes de dados adicionais e decisões metodológicas que precisam de validação. Mas a arquitetura da v1 deve ser desenhada para acomodá-lo — indicadores como módulos plugáveis, não lógica acoplada ao pipeline.

## 8. Riscos

| Risco | Mitigação |
|---|---|
| Interpretação equivocada dos rankings como juízo moral | Comunicação explícita das limitações no próprio dashboard, não só na documentação |
| Exposição jurídica ao associar parlamentares a irregularidades | Nunca afirmar irregularidade; apenas exibir dado público e, quando houver, citar fonte jornalística estabelecida |
| Mudança de schema ou indisponibilidade da API da Câmara | Testes de contrato na ingestão, alertas de falha, camada raw preservada para reprocessamento |
| Projeto abandonado por falta de tempo | Fases curtas e independentes; cada fase entrega algo funcional |
| Custo de infraestrutura | Restrição de projeto: operar dentro de camadas gratuitas |

## 9. Fases

Cada fase termina com algo funcionando e demonstrável.

**Fase 1 — Fundação.** Consolidação dos repositórios, ambiente reproduzível, CI, testes. Correção dos bugs conhecidos (range de anos fixo, coletor de deputados desativado, dependências incompletas).

**Fase 2 — Plataforma de dados.** Camadas raw/staged/marts, storage em nuvem, transformações com testes, legislatura como dimensão, orquestração automatizada.

**Fase 3 — Produto.** Dashboard reformulado, domínio próprio, exportação de dados, documentação pública de metodologia.

**Fase 4 — Operação e conteúdo.** Monitoramento, alertas, cadência de publicação de análises.

---

## Questões em aberto

- Nome final e domínio
- O dashboard permanece em Streamlit ou migra para outra stack?
- Cobertura retroativa: quantas legislaturas para trás vale a pena?
- Licença do código e dos dados
