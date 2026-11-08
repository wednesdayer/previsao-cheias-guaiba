# Discussão

## Summary (English)

The model was used live during the July 2026 Taquari flood, and this document is its post-mortem.

- **Every version overshot while the tributaries were still rising.** Two to three days ahead, they predicted 4.4–5.0 m at the Cais Mauá gauge against an observed 2.15 m. They converged only after the upstream crest had passed. The official SGB/IPH forecasts also overshot, but by +0.35 to +0.55 m.
- **The main structural cause is the outflow curve.** Tested against the three independent ADCP discharge measurements on the Guaíba (UFRGS, 2024–2025), the curve fitted by closing the water balance gives only about **half** the real outflow at flood stages. During calibration it was compensated by an equally underestimated inflow.
- **The same data problems are reported by IPH/UFRGS:** gauges damaged in 2024 and not maintained, rating curves extrapolated at the key stations (Lajeado, Rio Pardo), and a bed described by Navy charts from 1961–1966.
- **The bed has changed since 2024.** Surveys show erosion at the Gasômetro section and in the Jacuí channels, though no generalised siltation.
- **The IPH stopped publishing forecasts under its own name after July 2025.** Since then, Guaíba forecasts come out in SGB bulletins using IPH techniques. No source links this change to forecast error.

Next steps, all documents consulted (with SHA-256 checksums) and every quote with its source are below, in Portuguese.

---

Este documento discute onde o modelo falhou, o que a equipe do IPH/UFRGS relatou sobre as próprias previsões das mesmas cheias e quais lacunas afetam os dois. A seção 6 lista o que de fato reduziria o erro.

As chaves de referência, como [Medeiros 2025], apontam para [papers/README.md](../papers/README.md). Níveis estão em metros. Quando um nível é comparado com previsões públicas, a régua é sempre indicada, porque as duas réguas de Porto Alegre têm datums diferentes (ver [§4.4](#44-duas-réguas-dois-datums)).

**Sumário**

1. [Julho de 2026: um teste em tempo real](#1-julho-de-2026-um-teste-em-tempo-real)
2. [Problemas encontrados neste modelo](#2-problemas-encontrados-neste-modelo)
3. [Problemas relatados pelo IPH/UFRGS](#3-problemas-relatados-pelo-iphufrgs)
4. [Lacunas comuns a todos os modelos do Guaíba](#4-lacunas-comuns-a-todos-os-modelos-do-guaíba)
5. [Onde este modelo segue a abordagem do IPH](#5-onde-este-modelo-segue-a-abordagem-do-iph)
6. [O que reduziria o erro](#6-o-que-reduziria-o-erro)
7. [Documentos consultados](#7-documentos-consultados)

---

## 1. Julho de 2026: um teste em tempo real

O modelo foi construído em 22/07/2026, durante uma cheia do Taquari, e usado ao vivo nos dias seguintes. A vazão em Lajeado atingiu cerca de 11.100 m³/s na madrugada de 23/07. O Guaíba subiu em duas ondas:

| Onda | Pico observado, Cais Mauá (C6) | Pico observado, Gasômetro |
|---|---|---|
| 1ª | **2,15 m**, 24/07 15h | 1,53 m, 24/07 20h |
| 2ª | **2,59 m**, 31/07 20h | 1,89 m, 31/07 21h |

A tabela abaixo reproduz cada versão do modelo como se estivesse rodando ao vivo. Em cada corte, só são usados os dados disponíveis naquele momento (`scripts/replay_event.py`; saída em [`results/replay_2026-07_cais-maua.csv`](results/replay_2026-07_cais-maua.csv)). Os valores são o pico do cenário central convertido para a régua do Cais Mauá (+0,44 m), a mesma das previsões públicas, para que dê para comparar.

| Corte | v1 | v2 | v3 | v4 | Previsões públicas no mesmo período |
|---|---|---|---|---|---|
| 21/07 12h | 1,54 | 1,51 | 1,52 | 1,49 | MetSul: "perto, ao redor e acima de 2 metros" |
| 22/07 00h | 2,96 | 2,84 | 2,98 | 4,78 | |
| 22/07 12h | 4,97 | 4,52 | 4,80 | 6,61 | |
| 22/07 20h | 4,77 | 4,37 | 4,61 | 4,75 | SGB + IPH + Catavento (22/07 19h50): Cais Mauá "pode atingir 2,50 m"; IPH: "2,50 a 2,60 m prováveis" |
| 23/07 10h | 3,97 | 3,53 | 3,67 | 3,82 | SGB/IPH: cota de alerta de 2,5 m; 3 m "não há previsão de que seja alcançada". Dmae, sobre os cenários disponíveis quando redigiu o ofício: o Guaíba "poderia ultrapassar a cota dos 3 metros" |
| 23/07 16h | 3,70 | 3,31 | 3,40 | 3,38 | IPH, via imprensa: até 2,70 m no Cais Mauá no sábado (25/07) |
| 24/07 00h | 2,87 | 2,48 | 2,50 | 2,38 | |
| 24/07 08h | 2,35 | 2,16 | 2,15 | 2,03 | MetSul: 2,3–2,5 m nas próximas 48 h |
| 24/07 12h | 2,13 | 2,04 | 2,02 | 2,01 | Dmae fecha seis comportas ao meio-dia com previsão de 2,50–2,70 m |
| 28/07 12h | 2,44 | 2,15 | 2,21 | 2,51 | |
| 29/07 10h | 4,92 | 4,46 | 4,74 | 4,97 | Boletim SGB/IPH (29/07): pode superar 3 m até 01/08; cenário mais adverso perto de 3,50 m |
| 30/07 08h | 3,93 | 3,47 | 3,57 | 3,98 | MetSul: até 2,5 m |
| 30/07 12h | 3,77 | 3,32 | 3,39 | 3,70 | SGB/IPH (revisado): entre 2,60 e 3,00 m |
| 31/07 00h | 3,04 | 2,81 | 2,81 | 3,14 | |
| 31/07 10h | 2,58 | 2,56 | 2,54 | 2,89 | IPH (Meirelles): deve ficar abaixo de 3 m |

As fontes das previsões públicas estão em [papers/README.md](../papers/README.md#news-and-bulletins-july-2026).

O que a reprodução mostra:

- **Todas as versões exageraram as duas ondas enquanto os afluentes ainda subiam.** O exagero foi de 2,3 a 2,8 m (até 4,5 m no v4), com cerca de 2,5 dias de antecedência. Elas só convergiram para 0 a 15 cm do real depois que a crista de montante passou (24/07 08h e 31/07 10h), poucas horas antes do pico.
- **As previsões oficiais também exageraram, mas bem menos.**
  - 1ª onda: diziam 2,50–2,70 m, depois de terem circulado cenários acima de 3 m, que foram abandonados. O pico real foi 2,15 m, um erro de +0,35 a +0,55 m.
  - 2ª onda: foram de "pode superar 3 m, pior cenário ~3,50 m" para 2,60–3,00 m. O pico foi 2,59 m.
- **Nos momentos de maior incerteza, as nossas previsões ficaram na mesma faixa dos cenários oficiais mais altos.** Em 23/07 as versões davam 3,3–4,0 m, contra os cenários acima de 3 m citados pelo Dmae. Em 29–30/07 davam 3,3–4,0 m, contra o boletim de "supera 3 m / ~3,50 m". Depois que a previsão pública se estabilizou, a nossa continuou muito acima dela até a crista passar.
- **O v2 foi o menos ruim na subida de julho/2026,** mas não foi o melhor no hindcast de maio/2024, onde venceu o v1. Nenhuma versão é melhor de forma consistente, sinal de sobreajuste aos poucos eventos de calibração (§2.6).
- **Muitos desses picos estão cortados no fim do horizonte de 72 h.** Na maioria das células da tabela o modelo ainda estava subindo quando parou de integrar, então o pico real do modelo seria ainda maior. O dashboard ainda não sinaliza isso (§2.5).

## 2. Problemas encontrados neste modelo

### 2.1 A extrapolação de crista dispara na subida

A previsão precisa estimar até onde cada afluente vai subir antes de propagá-lo ([METHODOLOGY §4.1](METHODOLOGY.md#41-crest-extrapolation-project-heuristic)). Ao meio-dia de 22/07, Lajeado ainda subia cerca de 400 m³/s por hora (700 m³/s por hora algumas horas antes). Alimentada com essa taxa, a hipótese de decaimento exponencial projetou uma crista muito acima dos 11.078 m³/s de fato atingidos à 01h de 23/07.

Isso explica a maior parte do erro inicial e toda a volatilidade. Não existe limite físico para a crista extrapolada: nenhuma informação de chuva nem de roteamento de montante a restringe.

### 2.2 Exagero estrutural em cheias médias

Mesmo depois que a crista do Taquari passou (corte de 24/07 00h), o v1 ainda previa 2,87 m no Cais Mauá, contra 2,15 m observados. Os hindcasts de junho/2024 e junho/2025 mostram o mesmo viés de +0,5 m.

Há duas causas:
- **A principal é o viés da curva de saída** (§2.4).
- **A outra é a falta de amortecimento:** o modelo joga a onda inteira do Taquari num único reservatório de 470 km², deslocada no tempo mas sem atenuação. Na realidade, boa parte dela se espalha antes pelo delta do Jacuí e suas várzeas; Laipelt et al. [2026] mostram que as várzeas do Jacuí governam a duração das cheias do Guaíba. Um modelo concentrado de "banheira", calibrado na cheia extrema de maio/2024, não tem esse amortecedor para eventos menores.

### 2.3 A premissa de banheira (superfície plana)

O modelo trata o Guaíba como um reservatório de superfície plana. Os dados mostram outra coisa:
- A equipe do IPH descreve a cheia de maio/2024 como "predominantly fluvial", com a onda se propagando como escoamento de rio, em alta velocidade [Medeiros 2025].
- A campanha de ADCP de 05/05/2024, na Usina do Gasômetro, mediu corrente máxima de 4,2 m/s [Toldo 2024].
- Em junho/2025, o nível no Cais Navegantes ficou cerca de 30 cm acima do Cais Mauá, poucos quilômetros a jusante [IPH 2025].

Um modelo de armazenamento não representa essa declividade da superfície entre o delta e Porto Alegre. É também por causa dela que o mapa de inundação erra cerca de 1,5 m de cota em Eldorado do Sul ([METHODOLOGY §6.3](METHODOLOGY.md#63-caveats)).

### 2.4 A curva de saída dá cerca de metade da vazão medida

A curva Qout(h) é ajustada para fechar o balanço hídrico, então absorve todos os erros de entrada, armazenamento e vento. O expoente está encostado no limite superior (b = 4,0) e o RMSE do ajuste é de cerca de 2.000 m³/s.

A equipe do PGA POA/UFRGS fez três medições de vazão por ADCP no Guaíba [Toldo 2024; IPH 2025]. Elas são independentes de tudo o que entrou no ajuste do modelo. A curva de cada versão, avaliada no nível da telemetria do Gasômetro no momento de cada medição, dá:

| Medição | Medido (ADCP) | Nível no Gasômetro | v1 | v2 | v3 | v4 |
|---|---|---|---|---|---|---|
| 05/05/2024 17h45 (seção do Gasômetro, corrigida pelo transbordamento) | 35.736 m³/s | 4,10 m | 16.432 (46%) | 17.178 (48%) | 16.635 (47%) | 6.249 (17%) |
| 15/05/2024 09h50 (Ponta do Dionísio) | 22.070 m³/s | 4,02 m | 15.879 (72%) | 16.599 (75%) | 16.077 (73%) | 6.145 (28%) |
| 25/06/2025 ~11h50 (Usina do Gasômetro) | 12.941 m³/s | 2,26 m | 6.265 (48%) | 6.528 (50%) | 6.361 (49%) | 3.897 (30%) |

**Em cotas de cheia, a saída ajustada é cerca de metade da saída real** (no v4, bem menos).

Por que o balanço fechou mesmo assim na calibração: **a entrada estava subestimada numa proporção parecida.** As estações de entrada têm lacunas longas (§2.7), e a área de drenagem a jusante delas não é medida. Rio Pardo, por exemplo, cobre cerca de 71.000 dos 84.763 km² a montante de Porto Alegre.

Com dois erros que se compensam, os hindcasts parecem aceitáveis. Quando a entrada vem completa, como em julho/2026 com Lajeado transmitindo sem parar, a saída pequena demais faz o nível subir demais. Fora a extrapolação de crista, esta é provavelmente a principal causa estrutural do exagero da §1.

Isso também confirma o problema de identificabilidade ([METHODOLOGY §3.4](METHODOLOGY.md#34-identifiability)) e mostra a saída: ajustar a curva de saída aos pontos do ADCP (§6).

### 2.5 Picos cortados no fim do horizonte

Quando o pico previsto cai no último passo do horizonte de 72 h, ele é um limite inferior, não um pico. O `scripts/replay_event.py` marca esses casos (colunas `*_at_horizon`). O dashboard deveria fazer o mesmo, estendendo o horizonte ou avisando "ainda subindo em +72 h".

### 2.6 Poucos eventos, um extremo

A calibração usa três eventos, e um deles (maio/2024) está muito fora da faixa dos outros. Os parâmetros ajustados sobretudo nesse evento (v1) vão melhor nele e exageram cheias menores. Uma versão um pouco pior em maio/2024 (v2) foi a melhor em julho/2026.

### 2.7 Estações de entrada com buracos

No registro completo, Lajeado (Taquari) tem vazão em só 7% das horas, e Rio Pardo (Jacuí) em 41% ([DATA.md](DATA.md#data-quirks-that-shape-the-model)). Cada lacuna tira silenciosamente um afluente importante da entrada, e a curva de saída compensa durante a calibração.

## 3. Problemas relatados pelo IPH/UFRGS

O IPH/UFRGS rodou as previsões operacionais do Guaíba em maio/2024 e, junto com o SGB, em julho/2026. Os trabalhos publicados pela equipe descrevem várias das mesmas dificuldades.

- **Estações danificadas e assimilação de dados desligada.** O modelo MGB tem um esquema de assimilação de vazões, mas ele "was not used during the forecast's elaboration since several gauging stations… [were] damaged or not properly operating" [Medeiros 2025]. O SGB relata que estações do Taquari e do Caí foram levadas pela correnteza ou tiveram os sensores de nível danificados, e que a operação dos sistemas de alerta dessas bacias foi "seriamente comprometido" [SGB 2024].
- **Curvas-chave extrapoladas nas estações-chave.**
  - Estrela/Lajeado (86879300, a estação do Taquari que este modelo usa): o pico de 2024 foi 33,66 m, mas as medições de vazão só chegam a cerca de 25 m. O pico de 23.472 m³/s é uma extrapolação, com incerteza "high" [Collischonn 2025].
  - Muçum: a curva foi definida com medições até 8.380 m³/s, para um pico estimado de 13.241 m³/s [Collischonn 2025].
  - Laipelt et al. [2026] citam um relatório de Paiva et al. (2025) sobre a incerteza da extrapolação "particularly in locations such as Rio Pardo on the Jacuí River and at points along the Taquari River". São as mesmas duas estações que concentram o erro de entrada deste modelo.
- **Afluentes sem condição de contorno.** As condições de contorno de montante do modelo 2D "do not cover all the tributaries… due to lack of in situ observations, which may lead to local underestimations" [Laipelt 2026]. Este modelo tem o mesmo problema quando roteia só as estações de montante (v4).
- **Sensibilidade à hidráulica do Guaíba.** Variar só a rugosidade de Manning do Guaíba entre 0,025 e 0,045 muda o pico simulado no Cais Mauá entre −0,91 e +0,32 m [Laipelt 2026]. É o equivalente físico da curva de saída incerta deste modelo.
- **Vento.** Vento sudoeste sobre a Lagoa dos Patos represa a saída e pode elevar o Guaíba em até cerca de 50 cm [Laipelt 2026; Possa 2022]. Medeiros et al. [2025] relatam erros de previsão em junho/2024 ligados ao vento: a previsão era de queda abaixo da cota de alerta, e o nível chegou a 3,22 m.
- **A interpretação pesa tanto quanto o modelo.** Sinais de subida ou descida em horizontes acima de 72 h "were interpreted and discussed among the forecasters", com recalibrações durante o evento [Medeiros 2025]. Os números publicados são saída de modelo filtrada por julgamento de especialistas.
- **A cheia de junho/2025.** O IPH fez previsões hidrodinâmicas para essa cheia usando a **batimetria antiga**, porque o levantamento novo do estado ainda não estava disponível. Reportou incerteza de 10–20 cm nos cenários. Antecipou com cerca de 3 dias a subida, a cota de alerta e a aproximação da cota de inundação, e não viu anomalia que sugerisse perda de precisão por causa das mudanças no leito em 2024 [IPH 2025].
- **Quem publica as previsões.**
  - **O que mudou:** o IPH publicou previsões diárias do Guaíba no próprio site em 2024 e na cheia de junho/2025. A última, de 04/07/2025, diz ser "a última previsão emitida pela equipe para a cheia de junho de 2025" [IPH site], e não há previsão com a marca do IPH no site em julho/2026.
  - **Como é hoje:** as previsões do Guaíba saem nos **boletins do SGB, "utilizando as técnicas desenvolvidas no projeto"**, um Termo de Execução Descentralizada (TED) entre SGB e IPH com término previsto para novembro/2026 e aditivo até junho/2027 em andamento. Um workshop conjunto em setembro/2026 discutiu procedimentos de previsão, emissão de boletins e "propostas de interpretação e comunicação de resultados" [IPH 2026].
  - **Conclusão:** o IPH de fato parou de publicar previsões em nome próprio, mas o motivo documentado é essa mudança institucional. **Nenhuma fonte atribui a mudança a superestimação.**
- **Julho/2026.** Em 31/07/2026, o professor Fernando Meirelles (IPH) disse que o Guaíba subiu "no tempo esperado", mas dentro de uma "banda de incerteza".
  - **A dificuldade, segundo ele:** calcular a vazão dos afluentes, que já estavam baixando, porque a rede de estações danificada em 2024 não recebeu manutenção em vários pontos.
  - **A distância da medição:** a medição "feita ainda longe da Capital" aumenta a incerteza. "Se instalasse [pontos de observação] onde deveria ter, já se poderia saber com maior precisão" [Sul21 2026a].

## 4. Lacunas comuns a todos os modelos do Guaíba

### 4.1 Batimetria dos anos 1960

Os modelos hidrodinâmicos do IPH representam o leito do Guaíba e da Lagoa dos Patos com **cartas náuticas da Marinha** [Possa 2022; Laipelt 2026]. O modelo operacional de 2024 informa que essas cartas vêm de **levantamentos de 1961–1966** [Medeiros 2025]. No Taquari não havia dados suficientes, e o canal foi rebaixado manualmente em cerca de 4 m [Laipelt 2026]. Laipelt et al. afirmam que os resultados "are depended on the DTM model data and bathymetry accuracy".

A cheia de maio/2024 movimentou muito sedimento, então é razoável perguntar se essa batimetria de 60 anos ainda vale. As evidências até agora são mistas e parciais:

| Fonte | O que encontrou |
|---|---|
| Nota técnica do IPH/UFRGS e do PGA POA: levantamento com sonda de feixe duplo e sonar de varredura lateral em 26/12/2024, três perfis comparados com a base das cartas náuticas anterior a 2022 [IPH 2025; O Sul 2025] | Rebaixamento por erosão do canal principal e do talvegue na seção da Usina do Gasômetro e nos dois canais do Jacuí a montante. Sedimento removido e rocha exposta em alguns trechos (a amostragem de sedimento bateu em rocha). Sem assoreamento generalizado. O IPH recomenda "mapeamentos periódicos e mais abrangentes de batimetria". |
| Batimetria do governo do estado, 2025/2026, comparada com levantamentos de 2013 e 2015 em poucos pontos de controle [Sema 2026] | "não foram identificadas… alterações significativas nos pontos de amostragem". Resultados parciais. |
| Projeto Guaíba (Unisinos, UFRGS, FEPAM), sísmica comparada com a FEPAM de 2018 [Unisinos 2026] | "processos localizados de erosão, transporte e deposição de sedimentos… especialmente na região do Delta do Jacuí e em corredores preferenciais de fluxo". A extensão e a relação com 2024 ainda estão em avaliação; síntese final prevista para julho/2028. |
| Banco de areia entre o Centro Histórico e Eldorado do Sul [Nova ilha] | Já aparecia nos mapas dos levantamentos de 1961–1964; cresceu depois de maio/2024 para cerca de 1,4 km × 250 m. O governo do estado diz que não afeta as cheias. |

**Em resumo:** não há evidência de assoreamento em grande escala. Há evidência de **erosão do canal na seção do Gasômetro e nos canais do Jacuí, e de deposição em partes do delta**. São justamente as áreas que controlam a relação nível–vazão na régua usada por este modelo.

A batimetria dos modelos hidrodinâmicos é anterior tanto à cheia de 2024 quanto a essas mudanças. O IPH informa que as previsões de junho/2025, rodadas com a batimetria antiga, não perderam precisão [IPH 2025]. Ou seja, o canal aprofundado não é uma fonte demonstrada de erro de previsão, mas continua sem estar representado.

**Como isso afeta este modelo:**
- Ele não usa batimetria diretamente.
- A curva de saída é ajustada com dados de maio/2024 em diante. Ela já reflete o canal pós-cheia, mas mistura a geometria durante a cheia com a geometria depois dela. Se o leito perto do Gasômetro continuar mudando, a curva vai derivar, e o offset de datum entre as duas réguas também (§4.4).
- A curva cota-área e o mapa de inundação vêm de um modelo de superfície de 2011–2015 (GLO-30), também anterior à cheia.

### 4.2 Vazões extrapoladas nos afluentes

Todo modelo do Guaíba tira a vazão dos afluentes das curvas-chave da ANA/SGB. Essas curvas são extrapoladas nas grandes cheias (§3) e podem ter mudado com as alterações do leito do Taquari em 2024. Este modelo não tem como detectar uma curva deslocada: o erro vai direto para Qin e é absorvido pelo ajuste da saída.

### 4.3 Nenhuma medição de vazão no Guaíba

A saída para a Lagoa dos Patos não é medida de forma rotineira. As campanhas de ADCP do PGA POA/UFRGS são os únicos dados independentes de vazão do Guaíba [Toldo 2024; IPH 2025; usados também por Laipelt 2026]:

- 35.736 m³/s em 05/05/2024 (seção da Usina do Gasômetro, corrigida pelo transbordamento sobre a Ilha da Pintada);
- 22.070 m³/s em 15/05/2024 (Ponta do Dionísio);
- 12.941 m³/s em 25/06/2025 (Usina do Gasômetro).

Para referência: a vazão normal fica entre 1.000 e 2.000 m³/s. O IPH estima os picos de vazão das cheias de set/2023, nov/2023, mai/2024 e jun/2025 em 14,9, 16,0, 28,2 e 15,1 mil m³/s [IPH 2025]. Foram essas medições que expuseram o viés da curva de saída deste modelo (§2.4).

### 4.4 Duas réguas, dois datums

As previsões públicas e as cotas de alerta se referem à régua do Cais Mauá (C6). O modelo trabalha com a telemetria do Gasômetro. A diferença entre as duas não é constante:

| Condição | Cais Mauá − Gasômetro |
|---|---|
| Registro completo, mediana | 0,42 m |
| Cheia de julho/2026, mediana | 0,52 m |
| Pico de 24/07/2026 | 0,62 m |
| Pico de 31/07/2026 | 0,70 m |

O modelo usa +0,44 m fixo. Por isso, as previsões convertidas **subestimam** o nível do Cais Mauá durante as cheias, e o exagero mostrado na §1 é, se muito, um pouco maior do que aparece. A relação entre as duas réguas no pico de maio/2024 foi estudada pelo SGB [Germano 2024]. Um offset que dependa do nível seria mais correto.

### 4.5 O vento não está no modelo

Os modelos do IPH incluem vento; este não. Até cerca de 50 cm do nível do Guaíba podem vir do vento sobre a Lagoa dos Patos (§3), e este modelo absorve isso com atraso, na correção de viés.

## 5. Onde este modelo segue a abordagem do IPH

Várias escolhas de projeto seguem a metodologia publicada pelo IPH, ou coincidem com ela:

| IPH/UFRGS | Este modelo |
|---|---|
| Correções simples de offset, para que cada previsão comece num nível consistente com a observação mais recente [Medeiros 2025] | Correção de viés calculada nas últimas 24 h, aplicada em rampa para que a previsão comece no nível observado ([METHODOLOGY §4.3](METHODOLOGY.md#43-bias-correction-project-heuristic)) |
| Conjuntos de cenários, incluindo um de referência "zero rainfall and zero wind" [Medeiros 2025] | Três cenários de crista. Sem entrada de chuva, o modelo inteiro equivale ao cenário de referência sem chuva |
| Contribuição de cada afluente e momento do seu pico: o Taquari define o pico, o Jacuí a duração, e picos sincronizados somariam 0,82 m [Laipelt 2026; Medeiros 2025] | Entrada separada por rio, com tempos de viagem por rio |
| Cenários de vento para o represamento pela Lagoa dos Patos [Medeiros 2025; Possa 2022] | Não modelado; listado como limitação |
| Medições de ADCP como validação independente [Laipelt 2026; Toldo 2024] | Usadas aqui para testar a curva de saída (§2.4); o próximo passo é ajustar a curva a elas |

**A comparação com o cenário sem chuva é a mais reveladora.** Na avaliação do IPH para maio/2024, as previsões sem chuva *subestimaram* os níveis depois de 24 h, porque chuva nova continuava trazendo água [Medeiros 2025]. Este modelo, que na prática é uma previsão sem chuva, *superestimou* em julho/2026. Então o erro dele não vem da falta de chuva. Vem da extrapolação de crista, de uma curva de saída com metade do valor medido e da falta de armazenamento no delta (§2.1, §2.4, §2.2).

## 6. O que reduziria o erro

Em ordem aproximada de ganho esperado:

1. **Ancorar a curva de saída nas medições de ADCP** (§2.4, §4.3), por exemplo com ajuste restrito ou termo de penalização, deixando o lado da entrada absorver o desequilíbrio restante como um fator de área não monitorada. Ataca o maior erro estrutural encontrado.
2. **Limitar ou substituir a extrapolação de crista.** Usar as estações de montante (Muçum, Encantado) ou um modelo chuva-vazão do tipo MGB para limitar quanto um afluente ainda pode subir.
3. **Acrescentar armazenamento de delta/várzea entre os afluentes e o Guaíba**, por exemplo um segundo reservatório para o delta do Jacuí.
4. **Usar um offset de datum que dependa do nível** entre Gasômetro e Cais Mauá.
5. **Incluir o vento** como preditor do represamento pela Lagoa dos Patos.
6. **Sinalizar picos cortados no horizonte e registrar toda previsão feita ao vivo**, para que o próximo evento possa ser avaliado sem reprocessamento.
7. **Revisar a topografia quando a batimetria pós-2024 for publicada,** e usar um modelo de terreno sem prédios (FABDEM, ou ANADEM como em [Laipelt 2026]) no mapa.

## 7. Documentos consultados

Todos os PDFs lidos para esta discussão, com origem e SHA-256, para que qualquer pessoa confira que está olhando o mesmo arquivo. Todos foram obtidos em **08/11/2026**. Os que estão neste repositório também constam em [`papers/SHA256SUMS`](../papers/SHA256SUMS); para verificar, rode `sha256sum -c SHA256SUMS` dentro de `papers/`.

### 7.1 Incluídos em `papers/` (licença aberta)

| Chave | Link | Tamanho (bytes) | SHA-256 |
|---|---|---|---|
| [Medeiros 2025] | [papers/2025_Medeiros_RBRH_Guaiba_emergency_forecasts.pdf](../papers/2025_Medeiros_RBRH_Guaiba_emergency_forecasts.pdf) · https://doi.org/10.1590/2318-0331.302520250025 | 4.624.444 | `1adeb4b9b373d215b9ec8e29991c4661ffa46a2806ebff7d0be4e6b5695ff212` |
| [Laipelt 2026] | [papers/2026_Laipelt_HESS_2024_flood_mechanisms.pdf](../papers/2026_Laipelt_HESS_2024_flood_mechanisms.pdf) · https://doi.org/10.5194/hess-30-573-2026 | 14.034.473 | `07456865174e3d2cc0293584fe31973db26aca86201065b92ee7e51047d6858e` |
| [Collischonn 2025] | [papers/2025_Collischonn_RBRH_2024_disaster.pdf](../papers/2025_Collischonn_RBRH_2024_disaster.pdf) · https://doi.org/10.1590/2318-0331.302520240119 | 6.788.699 | `53f671ed1e0976f84f830aba3868b6f73d57fb0304828b2f107cef4dfb9ade33` |
| [Possa 2022] | [papers/2022_Possa_RBRH_1941_flood_wind.pdf](../papers/2022_Possa_RBRH_1941_flood_wind.pdf) · https://doi.org/10.1590/2318-0331.272220220028 | 5.003.409 | `ed8b3b5a043d9f3cbadfddfe17bad37607d7819abc9469bd79ea630d6fc7d298` |
| [Hawker 2022] | [papers/2022_Hawker_FABDEM.pdf](../papers/2022_Hawker_FABDEM.pdf) · https://doi.org/10.1088/1748-9326/ac4d4f | 2.516.007 | `683ac0dd52233a10ddb2293ebe59e1763aacb6def2323af244aac1559be24321` |
| [Rantz 1982] vol. 2 | [papers/1982_Rantz_WSP2175_vol2.pdf](../papers/1982_Rantz_WSP2175_vol2.pdf) · https://doi.org/10.3133/wsp2175 | 22.486.605 | `18f758d2cd3d5b136db559bbf2fc46dd9e3327a252393823f5518f8ad6f53eb4` |
| [Yevjevich 1964] | [papers/1964_Yevjevich_WSP1690_flood_routing_bibliography.pdf](../papers/1964_Yevjevich_WSP1690_flood_routing_bibliography.pdf) · https://doi.org/10.3133/wsp1690 | 5.412.959 | `1fcabaaabf06f65d3f67bd646b5b3f257818a316b7178ff4ff81f25bc090762a` |

### 7.2 Consultados online, não redistribuídos (licença não declarada)

| Chave / documento | Link do PDF | Tamanho (bytes) | SHA-256 |
|---|---|---|---|
| [Toldo 2024] Vazões no Rio Guaíba durante os picos da enchente de maio de 2024 (PGA POA/UFRGS, 24/07/2024) | https://www.ufrgs.br/iph/wp-content/uploads/2024/07/05_Nota-Vazoes-no-Rio-Guaiba-durante-os-picos-da-enchente-de-maio-de-2024.pdf | 209.861 | `41ef47d53725ec6d83b55aa7e69f0161dbbf5ac83cdf7779cc98c2155531d027` |
| [IPH 2025] Monitoramento ambiental e cheia no Guaíba e Delta do Jacuí em junho de 2025 (IPH/UFRGS e PGA POA, jul/2025) | https://www.ufrgs.br/iph/wp-content/uploads/2025/07/Nota-Tecnica_Cheia-no-Guaiba-.pdf | 14.972.315 | `3f4b79716ec6816669fc0bd8fb1dab1f08da647913ac641382161041e5a590a7` |
| [SGB 2024] Levantamento dos níveis das marcas da grande cheia de maio de 2024 no RS (Nota Técnica, 3ª versão, 10/09/2024) | https://rigeo.sgb.gov.br/bitstream/doc/24939.5/3/nota_tecnica_levantamento_cheia_2024_v.3.pdf | 4.103.092 | `93364c95e92576068be8800d1d9b14f580f25baa4a21bd36fe5e70bcbf440f50` |
| Soares, D. M. & Marcuzzo, F. F. N. *Grandes cheias de 2023 e 2024 do rio Taquari: estudo preliminar das áreas inundadas em Encantado e Muçum* (SGB, pôster). Lido; não citado acima | https://rigeo.sgb.gov.br/server/api/core/bitstreams/f620f9f9-1cbb-4b14-8c3c-a8eda53d47c2/content | 2.712.521 | `db0a7ee768afc46a4c047b45aca5a8948e5678a075b55b629d71121f1a64d0d7` |

Também foram lidas na íntegra páginas web (não PDF): as três matérias da Sul21 [Sul21 2026a–c], as páginas de notícias do IPH [IPH site; IPH 2026] e as páginas do governo do estado, O Sul, Unisinos e Jornal do Comércio sobre batimetria. Os links estão em [papers/README.md](../papers/README.md).

### 7.3 Tentados e não obtidos

| Documento | Link | O que aconteceu |
|---|---|---|
| Boletins SGB/IPH da cheia de julho/2026 (SAH Guaíba, 22, 23, 24, 26, 29 e 30/07) | ex.: https://www.sgb.gov.br/sace/boletins/Guaiba/20260723_12-20260723%20-%20115622.pdf | HTTP 404 em 08/11/2026; conteúdo conhecido só pela imprensa |
| Trabalho sobre curvas-chave e as cheias de 2023/2024 (XXVI Simpósio Brasileiro de Recursos Hídricos) | https://lume.ufrgs.br/bitstream/handle/10183/303638/001299077.pdf | Conexão interrompida / HTTP 504; não usado |
| Jornal do Comércio, 23/07/2026, "Guaíba pode chegar a 2,70m… diz IPH" | https://www.jornaldocomercio.com/geral/2026/07/1257312-guaiba-pode-chegar-a-270m-em-porto-alegre-no-fim-de-semana-diz-iph.html | Paywall após o primeiro parágrafo. O valor de 2,70 m (Cais Mauá, IPH) está confirmado por Sul21 [2026c], Rádio Pampa e Serra e Litoral |
