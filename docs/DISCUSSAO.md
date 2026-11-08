# Discussão

## Summary (English)

We used the model live during the Taquari flood of July 2026, and this document is its post-mortem. Two to three days before each of the two peaks, all four versions predicted between 4.4 and 5.0 m at the Cais Mauá gauge, while the observed maximum was 2.15 m; the forecasts converged only after the upstream crest had passed. The official forecasts issued by SGB and IPH/UFRGS also overshot, though by 0.35 to 0.55 m. Testing the fitted outflow curve against the only three independent discharge measurements on the Guaíba (ADCP campaigns by UFRGS in 2024 and 2025) shows that it yields about half of the measured outflow at flood stages. During calibration, an inflow underestimated by a similar proportion masked this error, and the two biases separate as soon as a flood arrives with complete inflow data. Several of the difficulties we found also appear in the IPH's own published work: gauges damaged in 2024 and left without maintenance, rating curves extrapolated far beyond their measured range at precisely the stations this model depends on, and a bed described by Navy charts surveyed between 1961 and 1966, although post-2024 surveys show local erosion at the Gasômetro section rather than generalised siltation. The IPH stopped publishing forecasts under its own name after July 2025, and SGB bulletins built on IPH techniques now carry them; we found no source linking that change to forecast error. The full argument, in Portuguese, follows, along with the list of every document consulted and its SHA-256 checksum.

---

Este documento examina onde o modelo falhou, contrapõe essas falhas ao que a equipe do IPH/UFRGS relatou sobre as próprias previsões para as mesmas cheias e discute as lacunas que afetam qualquer tentativa de modelar o Guaíba. A seção 6 extrai dessa análise uma ordem de prioridade para o desenvolvimento futuro.

As chaves de referência, como [Medeiros 2025], remetem a [papers/README.md](../papers/README.md). Os níveis estão em metros, e toda comparação com previsões públicas indica a régua de referência, porque as duas réguas de Porto Alegre usam datums diferentes, questão tratada na [seção 4.4](#44-duas-réguas-dois-datums).

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

O modelo foi construído em 22 de julho de 2026, com uma cheia do Taquari já em curso, e passou a ser usado ao vivo nos dias seguintes. A vazão em Lajeado chegou a cerca de 11.100 m³/s na madrugada de 23 de julho, e o Guaíba respondeu em duas ondas, com os seguintes máximos:

| Onda | Pico observado, Cais Mauá (C6) | Pico observado, Gasômetro |
|---|---|---|
| 1ª | **2,15 m**, 24/07 15h | 1,53 m, 24/07 20h |
| 2ª | **2,59 m**, 31/07 20h | 1,89 m, 31/07 21h |

Como os registros da sessão de trabalho em que as previsões foram emitidas não sobreviveram, reconstruímos o comportamento do modelo reexecutando cada versão com os dados cortados em instantes sucessivos do evento, de modo que cada previsão use apenas o que estava disponível naquele momento (`scripts/replay_event.py`; saída em [`resultados/reproducao_2026-07_cais-maua.csv`](resultados/reproducao_2026-07_cais-maua.csv)). Os valores da tabela correspondem ao pico do cenário central, convertido para a régua do Cais Mauá com o deslocamento de +0,44 m adotado pelo dashboard, para permitir a comparação direta com as previsões divulgadas na imprensa, todas referidas a essa régua.

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

As fontes das previsões públicas estão em [papers/README.md](../papers/README.md#notícias-e-boletins-julho-de-2026).

O resultado central é inequívoco: todas as versões superestimaram as duas ondas enquanto os afluentes ainda subiam, com erros entre 2,3 e 2,8 m (até 4,5 m no v4) cerca de dois dias e meio antes de cada pico, e só convergiram para valores a menos de 15 cm do observado depois que a crista de montante havia passado, em 24 de julho às 8h e em 31 de julho às 10h, poucas horas antes dos respectivos máximos. Uma previsão que acerta apenas quando o evento já está praticamente definido tem pouco valor operacional, e esse é o diagnóstico que orienta o restante do documento.

As previsões oficiais também erraram para cima, mas numa escala muito diferente. Na primeira onda, o SGB e o IPH trabalharam com 2,50 a 2,70 m no Cais Mauá, depois de cenários acima de 3 m que chegaram a circular e foram abandonados, e o pico real ficou em 2,15 m, o que corresponde a um erro de 0,35 a 0,55 m. Na segunda, o boletim de 29 de julho admitia superar 3 m, com um cenário adverso em torno de 3,50 m, e foi revisado no dia seguinte para a faixa entre 2,60 e 3,00 m; o máximo observado foi 2,59 m.

Há, contudo, momentos em que as duas fontes coincidem. Em 23 de julho, as quatro versões do modelo indicavam entre 3,3 e 4,0 m, valores compatíveis com os cenários acima de 3 m que o Dmae relatou ter considerado ao redigir o pedido de fechamento das comportas. Em 29 e 30 de julho, o modelo indicava de 3,3 a 4,0 m, enquanto o boletim oficial falava em superar 3 m e num cenário adverso próximo de 3,50 m. A coincidência ocorre precisamente nos instantes de maior incerteza, e se desfaz quando a previsão oficial se estabiliza, momento a partir do qual o modelo permanece bem acima dela até a passagem da crista.

O desempenho relativo das versões também contraria o que o hindcast de maio de 2024 sugeria. Ali, o v1 obteve o menor erro de nível; em julho de 2026, a versão menos ruim durante a subida foi o v2. Que nenhuma das versões se mostre consistentemente superior é sinal de sobreajuste aos poucos eventos disponíveis para calibração, problema retomado na seção 2.6. Muitos dos picos da tabela, por fim, coincidem com o último passo do horizonte de 72 horas, o que significa que o modelo ainda previa subida quando a integração terminou e que o máximo implícito seria ainda maior (seção 2.5).

## 2. Problemas encontrados neste modelo

### 2.1 A extrapolação de crista dispara na subida

Para propagar um afluente que ainda está subindo, o modelo precisa estimar até onde ele vai, e o faz com uma hipótese de decaimento exponencial da taxa de subida ([METODOLOGIA §4.1](METODOLOGIA.md#41-extrapolação-de-crista-heurística-do-projeto)). Ao meio-dia de 22 de julho, Lajeado ainda subia cerca de 400 m³/s por hora, depois de ter chegado a 700 m³/s por hora algumas horas antes; alimentada com essas taxas, a hipótese projetou uma crista muito acima dos 11.078 m³/s que o rio de fato atingiu à 01h de 23 de julho. Esse mecanismo explica a maior parte do erro inicial e praticamente toda a volatilidade observada. Nada no modelo limita fisicamente a crista extrapolada, já que ele não dispõe de informação sobre a chuva que alimenta a subida nem utiliza o roteamento a partir das estações de montante para restringir a projeção.

### 2.2 Exagero estrutural em cheias médias

Mesmo depois da passagem da crista do Taquari, no corte de 24 de julho à 0h, o v1 ainda previa 2,87 m no Cais Mauá, contra os 2,15 m observados, e os hindcasts de junho de 2024 e de junho de 2025 exibem o mesmo viés, de cerca de meio metro para cima. Esse componente do erro não depende da extrapolação de crista, e sua causa principal é a curva de saída subdimensionada analisada na seção 2.4. Uma segunda causa contribui: o modelo lança a onda inteira do Taquari num único reservatório de 470 km², apenas deslocada no tempo e sem qualquer atenuação, quando na realidade boa parte dessa água se espalha antes pelo delta do Jacuí e pelas várzeas adjacentes. Laipelt et al. [2026] mostram que as várzeas do Jacuí governam a duração das cheias do Guaíba, e um modelo concentrado, calibrado sobretudo na cheia extrema de 2024, não dispõe de nenhum mecanismo equivalente para amortecer eventos menores.

### 2.3 A premissa de banheira (superfície plana)

A formulação do modelo pressupõe que a superfície da água permanece horizontal em todo o Guaíba, e as observações disponíveis indicam outra coisa. A equipe do IPH descreve a cheia de maio de 2024 como "predominantly fluvial", com a onda propagando-se como escoamento de rio, em alta velocidade [Medeiros 2025], e a campanha de ADCP de 5 de maio de 2024, na seção da Usina do Gasômetro, registrou corrente máxima de 4,2 m/s [Toldo 2024]. Na cheia de junho de 2025, o nível no Cais Navegantes chegou a ficar cerca de 30 cm acima do registrado no Cais Mauá, poucos quilômetros a jusante [IPH 2025]. Um modelo de armazenamento não tem como representar essa declividade da superfície entre o delta e Porto Alegre, que também explica por que o mapa de inundação erra cerca de 1,5 m de cota em Eldorado do Sul ([METODOLOGIA §6.3](METODOLOGIA.md#63-ressalvas)).

### 2.4 A curva de saída dá cerca de metade da vazão medida

Ajustada para fechar o balanço hídrico, a curva Qout(h) absorve todos os erros de entrada, de armazenamento e de vento, e dois indícios já apontavam para um ajuste problemático: o expoente encostado no limite superior permitido (b = 4,0) e um erro quadrático médio de cerca de 2.000 m³/s. Faltava, porém, um teste independente, e ele se tornou possível com as três medições de vazão por ADCP que a equipe do PGA POA/UFRGS realizou no Guaíba [Toldo 2024; IPH 2025], nenhuma das quais entrou no ajuste do modelo. Avaliando a curva de cada versão no nível registrado pela telemetria do Gasômetro no momento de cada medição, obtém-se:

| Medição | Medido (ADCP) | Nível no Gasômetro | v1 | v2 | v3 | v4 |
|---|---|---|---|---|---|---|
| 05/05/2024 17h45 (seção do Gasômetro, corrigida pelo transbordamento) | 35.736 m³/s | 4,10 m | 16.432 (46%) | 17.178 (48%) | 16.635 (47%) | 6.249 (17%) |
| 15/05/2024 09h50 (Ponta do Dionísio) | 22.070 m³/s | 4,02 m | 15.879 (72%) | 16.599 (75%) | 16.077 (73%) | 6.145 (28%) |
| 25/06/2025 ~11h50 (Usina do Gasômetro) | 12.941 m³/s | 2,26 m | 6.265 (48%) | 6.528 (50%) | 6.361 (49%) | 3.897 (30%) |

Em cotas de cheia, a saída ajustada nas versões v1 a v3 corresponde a aproximadamente metade da vazão real, e no v4 a fração é ainda menor. O balanço fechou durante a calibração porque a entrada também estava subestimada, e numa proporção semelhante. Duas razões concorrem para isso. As estações de entrada apresentam lacunas longas (seção 2.7), e a área de drenagem situada a jusante delas não é monitorada; Rio Pardo, por exemplo, controla cerca de 71.000 dos 84.763 km² que drenam para Porto Alegre, e a vazão gerada no restante da bacia simplesmente não entra no cálculo.

Com dois erros que se compensam, os hindcasts parecem aceitáveis, e o problema só se manifesta quando um dos erros desaparece. Foi o que ocorreu em julho de 2026, quando Lajeado transmitiu vazão de forma contínua durante a cheia e a entrada chegou ao modelo praticamente completa: diante de uma saída que só escoa metade do que deveria, o nível previsto subiu demais. Excluída a extrapolação de crista, essa é provavelmente a principal causa estrutural do exagero descrito na seção 1. O mesmo resultado confirma, com dados, o problema de identificabilidade apontado na [METODOLOGIA, §3.4](METODOLOGIA.md#34-identificabilidade), e indica também o caminho para superá-lo, que consiste em ancorar a curva de saída nas medições de ADCP (seção 6).

### 2.5 Picos cortados no fim do horizonte

Quando o máximo previsto coincide com o último passo das 72 horas, ele representa um limite inferior e não um pico, porque o modelo ainda estava em subida quando a integração terminou. O `scripts/replay_event.py` identifica esses casos (colunas `*_at_horizon`), mas o dashboard não os sinaliza, e deveria fazê-lo, seja estendendo o horizonte, seja informando ao usuário que o nível continua a subir em +72 h.

### 2.6 Poucos eventos, um extremo

A calibração dispõe de três eventos, e um deles, maio de 2024, situa-se muito fora da faixa dos outros dois. Os parâmetros ajustados sob a influência dominante desse evento, como os do v1, desempenham melhor nele e exageram as cheias menores; o v2, ligeiramente pior em maio de 2024, foi o melhor em julho de 2026. Com tão poucos eventos, qualquer escolha de versão operacional baseada em hindcast carrega o risco de premiar o ajuste a um único episódio.

### 2.7 Estações de entrada com buracos

Ao longo do registro completo, Lajeado tem dados de vazão em apenas 7% das horas, e Rio Pardo em 41% ([DADOS.md](DADOS.md#peculiaridades-dos-dados-que-moldam-o-modelo)). Cada lacuna retira silenciosamente um afluente importante da soma de entrada, e a curva de saída, durante a calibração, compensa a ausência ajustando-se para baixo. É essa compensação que a seção 2.4 quantifica.

## 3. Problemas relatados pelo IPH/UFRGS

O IPH/UFRGS conduziu as previsões operacionais do Guaíba em maio de 2024 e, em parceria com o SGB, em julho de 2026, e os trabalhos publicados pela equipe descrevem várias das dificuldades encontradas aqui. A comparação interessa por dois motivos: mostra quais problemas decorrem dos dados disponíveis, e não das simplificações deste modelo, e oferece uma referência para avaliar o tamanho do erro que se pode esperar mesmo de um sistema muito mais completo.

O primeiro desses problemas é a rede de monitoramento. O modelo MGB dispõe de um esquema de assimilação de vazões observadas, mas, segundo Medeiros et al. [2025], o esquema "was not used during the forecast's elaboration since several gauging stations… [were] damaged or not properly operating". O SGB documenta que estações do Taquari e do Caí foram levadas pela correnteza ou tiveram os sensores de nível danificados, e que a operação dos sistemas de alerta dessas bacias ficou "seriamente comprometido" [SGB 2024]. Dois anos depois, a situação persistia: em 31 de julho de 2026, o professor Fernando Meirelles, do IPH, afirmou à Sul21 que o Guaíba havia subido "no tempo esperado", mas dentro de uma "banda de incerteza", e atribuiu essa incerteza à dificuldade de calcular a vazão dos afluentes, que já estavam baixando, porque a rede de estações danificada em 2024 não recebeu manutenção em vários pontos. Acrescentou que a medição "feita ainda longe da Capital" amplia a incerteza natural da previsão e que, "se instalasse [pontos de observação] onde deveria ter, já se poderia saber com maior precisão" [Sul21 2026a].

Ainda mais diretamente relacionado ao erro deste modelo é o problema das curvas-chave nas estações de que ele depende. Em Estrela/Lajeado, estação 86879300, a mesma que o modelo usa para o Taquari, o pico de 2024 alcançou 33,66 m, enquanto as medições de vazão que sustentam a curva-chave chegam a cerca de 25 m; o pico estimado de 23.472 m³/s é, portanto, uma extrapolação, cuja incerteza Collischonn et al. [2025] classificam como "high". Em Muçum, a curva foi definida com medições até 8.380 m³/s, para um pico estimado em 13.241 m³/s [Collischonn 2025]. Laipelt et al. [2026] mencionam um relatório de Paiva et al. (2025) sobre a incerteza dessa extrapolação, "particularly in locations such as Rio Pardo on the Jacuí River and at points along the Taquari River": as mesmas duas estações em que se concentra o erro de entrada deste modelo.

A modelagem hidrodinâmica enfrenta limitações análogas às nossas. As condições de contorno de montante do modelo bidimensional de Laipelt et al. [2026] "do not cover all the tributaries… due to lack of in situ observations, which may lead to local underestimations", problema da mesma natureza do que afeta o v4 quando roteia apenas as estações de montante. O mesmo trabalho mostra que variar somente a rugosidade de Manning no Guaíba entre 0,025 e 0,045 desloca o pico simulado no Cais Mauá entre −0,91 e +0,32 m, ou seja, que a representação hidráulica da saída do lago é, também ali, a parte mais incerta do sistema, papel que no nosso modelo cabe à curva de saída.

O vento constitui a principal fonte de erro reconhecida pelo IPH depois que a cheia perde força. Vento de sudoeste sobre a Lagoa dos Patos dificulta a saída do Guaíba e pode elevar seu nível em até cerca de 50 cm [Laipelt 2026; Possa 2022], e Medeiros et al. [2025] relatam previsões de junho de 2024 que indicavam queda abaixo da cota de alerta para um fim de semana em que o nível chegou a 3,22 m, erro que os autores associam às incertezas sobre o efeito do vento. Os mesmos autores insistem que o desempenho do sistema dependeu da interpretação humana: os sinais de subida ou descida em horizontes superiores a 72 horas "were interpreted and discussed among the forecasters", e os modelos foram recalibrados ao longo do evento [Medeiros 2025]. Os números divulgados ao público são, portanto, saídas de modelo filtradas por julgamento especializado, o que torna a comparação com um modelo automático, como este, apenas parcialmente justa.

A nota técnica sobre a cheia de junho de 2025 traz informações relevantes para a questão da batimetria, retomada na seção 4.1. O IPH elaborou previsões hidrodinâmicas para esse evento com a batimetria antiga, porque o levantamento contratado pelo governo do estado ainda não estava disponível, e relatou incerteza de 10 a 20 cm entre cenários; as previsões anteciparam com cerca de três dias a subida, a chegada à cota de alerta e a aproximação da cota de inundação, e a equipe não identificou anomalia que sugerisse perda de precisão em consequência das alterações sofridas pelo leito em 2024 [IPH 2025].

Resta a questão de quem publica as previsões. O IPH divulgou previsões diárias do Guaíba no próprio site durante a cheia de 2024 e novamente em junho de 2025; a última delas, de 4 de julho de 2025, apresenta-se como "a última previsão emitida pela equipe para a cheia de junho de 2025" [IPH site], e o site não traz nenhuma previsão com a marca do IPH para julho de 2026. Desde então, as previsões do Guaíba circulam nos boletins do SGB, elaborados "utilizando as técnicas desenvolvidas no projeto", isto é, no âmbito de um Termo de Execução Descentralizada entre o SGB e o IPH, com término previsto para novembro de 2026 e aditivo até junho de 2027 em tramitação. Um workshop conjunto realizado em setembro de 2026 discutiu procedimentos de previsão, emissão de boletins e "propostas de interpretação e comunicação de resultados" [IPH 2026]. O IPH deixou, portanto, de publicar previsões em nome próprio, mas o motivo documentado é essa reorganização institucional; nenhuma das fontes consultadas associa a mudança a erros de superestimação.

## 4. Lacunas comuns a todos os modelos do Guaíba

### 4.1 Batimetria dos anos 1960

Os modelos hidrodinâmicos do IPH representam o leito do Guaíba e da Lagoa dos Patos com cartas náuticas da Marinha [Possa 2022; Laipelt 2026], e o modelo operacional de 2024 informa que essas cartas resultam de levantamentos feitos entre 1961 e 1966 [Medeiros 2025]. No Taquari, onde os dados eram insuficientes, o canal foi rebaixado manualmente em cerca de 4 m no modelo de Laipelt et al. [2026], cujos autores reconhecem que os resultados "are depended on the DTM model data and bathymetry accuracy".

A cheia de maio de 2024 mobilizou grande volume de sedimentos, e cabe perguntar se uma batimetria de sessenta anos ainda descreve o leito. As evidências reunidas até aqui são parciais e não apontam todas na mesma direção:

| Fonte | O que encontrou |
|---|---|
| Nota técnica do IPH/UFRGS e do PGA POA: levantamento com sonda de feixe duplo e sonar de varredura lateral em 26/12/2024, três perfis comparados com a base das cartas náuticas anterior a 2022 [IPH 2025; O Sul 2025] | Rebaixamento por erosão do canal principal e do talvegue na seção da Usina do Gasômetro e nos dois canais do Jacuí a montante. Sedimento removido e rocha exposta em alguns trechos (a amostragem de sedimento bateu em rocha). Sem assoreamento generalizado. O IPH recomenda "mapeamentos periódicos e mais abrangentes de batimetria". |
| Batimetria do governo do estado, 2025/2026, comparada com levantamentos de 2013 e 2015 em poucos pontos de controle [Sema 2026] | "não foram identificadas… alterações significativas nos pontos de amostragem". Resultados parciais. |
| Projeto Guaíba (Unisinos, UFRGS, FEPAM), sísmica comparada com a FEPAM de 2018 [Unisinos 2026] | "processos localizados de erosão, transporte e deposição de sedimentos… especialmente na região do Delta do Jacuí e em corredores preferenciais de fluxo". A extensão e a relação com 2024 ainda estão em avaliação; síntese final prevista para julho/2028. |
| Banco de areia entre o Centro Histórico e Eldorado do Sul [Nova ilha] | Já aparecia nos mapas dos levantamentos de 1961–1964; cresceu depois de maio/2024 para cerca de 1,4 km × 250 m. O governo do estado diz que não afeta as cheias. |

O conjunto não sustenta a hipótese de assoreamento em grande escala, mas documenta erosão do canal na seção do Gasômetro e nos canais do Jacuí, além de deposição em partes do delta. Esses trechos são justamente os que controlam a relação entre nível e vazão na régua utilizada por este modelo. A batimetria em que se apoiam os modelos hidrodinâmicos é anterior tanto à cheia de 2024 quanto a essas alterações; ainda assim, segundo o IPH, as previsões de junho de 2025, rodadas com essa batimetria antiga, não perderam precisão [IPH 2025]. O aprofundamento do canal não está, portanto, demonstrado como fonte de erro de previsão, mas continua sem representação em qualquer dos modelos disponíveis, e os próprios autores recomendam levantamentos periódicos para acompanhá-lo.

Este modelo não utiliza batimetria diretamente, o que não o isenta do problema. Sua curva de saída foi ajustada com dados de maio de 2024 em diante e reflete, por isso, o canal posterior à cheia; ao mesmo tempo, mistura no mesmo ajuste a geometria vigente durante o evento e a que se estabeleceu depois dele. Se o leito próximo ao Gasômetro continuar a se modificar, a curva tenderá a derivar, e o deslocamento de datum entre as duas réguas também (seção 4.4). A curva cota-área e o mapa de inundação, por sua vez, derivam de um modelo de superfície produzido entre 2011 e 2015, igualmente anterior à cheia.

### 4.2 Vazões extrapoladas nos afluentes

Todo modelo do Guaíba obtém a vazão dos afluentes a partir das curvas-chave da ANA e do SGB, curvas que nas grandes cheias operam em regime de extrapolação (seção 3) e que podem ter se deslocado com as alterações do leito do Taquari em 2024. Este modelo não dispõe de nenhum mecanismo capaz de detectar uma curva deslocada: o erro entra diretamente em Qin e acaba absorvido pelo ajuste da curva de saída.

### 4.3 Nenhuma medição de vazão no Guaíba

Não há medição rotineira da vazão que o Guaíba entrega à Lagoa dos Patos. As campanhas de ADCP do PGA POA/UFRGS constituem os únicos dados independentes disponíveis [Toldo 2024; IPH 2025], também utilizados por Laipelt et al. [2026] na validação de seu modelo: 35.736 m³/s em 5 de maio de 2024, na seção da Usina do Gasômetro, valor já corrigido pelo transbordamento sobre a Ilha da Pintada; 22.070 m³/s em 15 de maio de 2024, na Ponta do Dionísio; e 12.941 m³/s em 25 de junho de 2025, novamente na Usina do Gasômetro. Para efeito de comparação, a vazão em condições normais fica entre 1.000 e 2.000 m³/s, e o IPH estima os picos das cheias de setembro de 2023, novembro de 2023, maio de 2024 e junho de 2025 em 14,9, 16,0, 28,2 e 15,1 mil m³/s, respectivamente [IPH 2025]. Foram essas três medições que permitiram expor o viés da curva de saída discutido na seção 2.4, e sua escassez é, por si só, uma das lacunas mais sérias para quem pretenda modelar o sistema.

### 4.4 Duas réguas, dois datums

As previsões públicas e as cotas de alerta referem-se à régua do Cais Mauá (C6), enquanto o modelo opera sobre a telemetria do Gasômetro, e a diferença entre as duas não é constante:

| Condição | Cais Mauá − Gasômetro |
|---|---|
| Registro completo, mediana | 0,42 m |
| Cheia de julho/2026, mediana | 0,52 m |
| Pico de 24/07/2026 | 0,62 m |
| Pico de 31/07/2026 | 0,70 m |

A diferença cresce com o nível, o que é coerente com a declividade da superfície descrita na seção 2.3. Como o modelo aplica um deslocamento fixo de +0,44 m, as previsões convertidas subestimam o nível do Cais Mauá durante as cheias, e o exagero apresentado na seção 1 é, se algo, um pouco maior do que a tabela sugere. A relação entre as duas réguas no pico de maio de 2024 foi estudada pelo SGB [Germano 2024]; um deslocamento dependente do nível seria mais correto do que o valor fixo atual.

### 4.5 O vento não está no modelo

Os modelos do IPH incluem o vento como forçante, e este não. Como até cerca de 50 cm do nível do Guaíba podem decorrer do vento sobre a Lagoa dos Patos (seção 3), o efeito acaba absorvido pela correção de viés, que só o reconhece com algumas horas de atraso.

## 5. Onde este modelo segue a abordagem do IPH

Diversas escolhas de projeto seguem a metodologia publicada pelo IPH ou coincidem com ela, e a comparação lado a lado ajuda a localizar onde as diferenças de desempenho se originam:

| IPH/UFRGS | Este modelo |
|---|---|
| Correções simples de offset, para que cada previsão comece num nível consistente com a observação mais recente [Medeiros 2025] | Correção de viés calculada nas últimas 24 h, aplicada em rampa para que a previsão comece no nível observado ([METODOLOGIA §4.3](METODOLOGIA.md#43-correção-de-viés-heurística-do-projeto)) |
| Conjuntos de cenários, incluindo um de referência "zero rainfall and zero wind" [Medeiros 2025] | Três cenários de crista; sem entrada de chuva, o modelo inteiro equivale ao cenário de referência sem chuva |
| Contribuição de cada afluente e momento do seu pico: o Taquari define o pico, o Jacuí a duração, e picos sincronizados somariam 0,82 m [Laipelt 2026; Medeiros 2025] | Entrada separada por rio, com tempos de viagem por rio |
| Cenários de vento para o represamento pela Lagoa dos Patos [Medeiros 2025; Possa 2022] | Não modelado; listado como limitação |
| Medições de ADCP como validação independente [Laipelt 2026; Toldo 2024] | Usadas aqui para testar a curva de saída (§2.4); o próximo passo é ajustar a curva a elas |

A comparação mais reveladora envolve o cenário sem chuva. Na avaliação que o IPH fez da cheia de maio de 2024, as previsões que desconsideravam chuva e vento subestimaram os níveis em horizontes superiores a 24 horas, porque a chuva que continuava a cair seguia acrescentando água ao sistema [Medeiros 2025]. Este modelo, que na prática é uma previsão sem chuva, fez o oposto em julho de 2026 e superestimou. Se o cenário equivalente do sistema operacional erra para baixo e o nosso erra para cima, a origem do erro não está na ausência de chuva, mas na extrapolação de crista, na curva de saída que escoa metade do que deveria e na falta de armazenamento no delta (seções 2.1, 2.4 e 2.2).

## 6. O que reduziria o erro

A prioridade número um, à luz dos resultados acima, é ancorar a curva de saída nas medições de ADCP (seções 2.4 e 4.3). Isso pode ser feito por ajuste restrito ou pela inclusão de um termo de penalização, transferindo para o lado da entrada o desequilíbrio que restar, sob a forma de um fator de área não monitorada. A medida ataca o maior erro estrutural identificado e, como efeito colateral, reduz a não identificabilidade entre área e saída que a metodologia já apontava.

A extrapolação de crista é o segundo alvo, e duas alternativas se apresentam. A mais simples consiste em limitar a crista projetada com base nas estações de montante, como Muçum e Encantado, cuja passagem de onda antecede a de Lajeado em várias horas; a mais completa, em substituir a extrapolação por um modelo chuva-vazão do tipo MGB, que traria para o cálculo a informação que hoje falta. A seguir viria a inclusão de um segundo reservatório representando o delta do Jacuí e suas várzeas, capaz de amortecer as cheias médias que o modelo atual exagera.

As demais melhorias têm alcance menor, embora nenhuma seja trivial. O deslocamento de datum entre o Gasômetro e o Cais Mauá deveria variar com o nível, e o vento deveria entrar como preditor do represamento pela Lagoa dos Patos. O dashboard precisa sinalizar os picos cortados pelo horizonte e passar a registrar cada previsão emitida ao vivo, para que o próximo evento possa ser avaliado sem depender de reconstrução posterior, como foi necessário aqui. Por fim, quando o levantamento batimétrico posterior a 2024 for publicado, convém revisar a topografia e substituir, no mapa de inundação, o modelo de superfície por um modelo de terreno sem edificações, como o FABDEM ou o ANADEM empregado por Laipelt et al. [2026].

## 7. Documentos consultados

Relacionamos abaixo todos os PDFs lidos para esta discussão, com a origem e o hash SHA-256 de cada um, para que qualquer leitor possa verificar que consulta o mesmo arquivo. Todos foram obtidos em 8 de novembro de 2026. Os que integram este repositório constam também de [`papers/SHA256SUMS`](../papers/SHA256SUMS), e a verificação pode ser feita executando `sha256sum -c SHA256SUMS` dentro de `papers/`.

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

Também lemos na íntegra páginas web que não são PDFs: as três matérias da Sul21 [Sul21 2026a–c], as páginas de notícias do IPH [IPH site; IPH 2026] e as páginas do governo do estado, do jornal O Sul, da Unisinos e do Jornal do Comércio sobre batimetria. Os endereços estão em [papers/README.md](../papers/README.md).

### 7.3 Tentados e não obtidos

| Documento | Link | O que aconteceu |
|---|---|---|
| Boletins SGB/IPH da cheia de julho/2026 (SAH Guaíba, 22, 23, 24, 26, 29 e 30/07) | ex.: https://www.sgb.gov.br/sace/boletins/Guaiba/20260723_12-20260723%20-%20115622.pdf | HTTP 404 em 08/11/2026; conteúdo conhecido só pela imprensa |
| Trabalho sobre curvas-chave e as cheias de 2023/2024 (XXVI Simpósio Brasileiro de Recursos Hídricos) | https://lume.ufrgs.br/bitstream/handle/10183/303638/001299077.pdf | Conexão interrompida / HTTP 504; não usado |
| Jornal do Comércio, 23/07/2026, "Guaíba pode chegar a 2,70m… diz IPH" | https://www.jornaldocomercio.com/geral/2026/07/1257312-guaiba-pode-chegar-a-270m-em-porto-alegre-no-fim-de-semana-diz-iph.html | Paywall após o primeiro parágrafo. O valor de 2,70 m (Cais Mauá, IPH) está confirmado por Sul21 [2026c], Rádio Pampa e Serra e Litoral |
