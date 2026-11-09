# Discussão

## Summary (English)

We used the model live during the Taquari flood of July 2026, and this document is its post-mortem. Two to three days before each of the two peaks, all four versions predicted between 4.4 and 5.0 m at the Cais Mauá gauge, while the observed maximum was 2.15 m; the forecasts converged only after the upstream crest had passed. The official forecasts issued by SGB and IPH/UFRGS also overshot, though by 0.35 to 0.55 m. Testing the fitted outflow curve against the only three independent discharge measurements on the Guaíba (ADCP campaigns by UFRGS in 2024 and 2025) shows that it yields about half of the measured outflow at flood stages. During calibration, an inflow underestimated by a similar proportion masked this error, and the two biases separate as soon as a flood arrives with complete inflow data. Several of the difficulties we found also appear in the IPH's own published work: gauges damaged in 2024 and left without maintenance, rating curves extrapolated far beyond their measured range at precisely the stations this model depends on, and a bed described by Navy charts surveyed between 1961 and 1966, although post-2024 surveys show local erosion at the Gasômetro section rather than generalised siltation. The IPH stopped publishing forecasts under its own name after July 2025, and SGB bulletins built on IPH techniques now carry them; we found no source linking that change to forecast error. Rain and wind were left out on purpose, since the initial goal was to forecast only from the water already measured in the rivers. The rain gauges at the same stations show that the rain had already stopped, by 5 to 12 hours, when each of the worst forecasts was issued, so the omission hurt through the crest extrapolation, which implicitly assumes more rain than fell, rather than through missing rain volume. Replaying all four versions every six hours over May–June 2024, July 2026 and September–October 2026 (the last one after every calibration) gives the same picture: the error doubles or triples out of sample, it is positive in every period and version, the scenario band contains the observed maximum in at most 12% of the forecasts, and v2 is the least bad version throughout. The full argument, in Portuguese, follows, along with the list of every document consulted and its SHA-256 checksum.

---

Este documento examina onde o modelo falhou, contrapõe essas falhas ao que a equipe do IPH/UFRGS relatou sobre as próprias previsões para as mesmas cheias e discute as lacunas que afetam qualquer tentativa de modelar o Guaíba. A seção 3 trata da decisão de deixar chuva e vento de fora e do que ela revelou. A seção 8 extrai dessa análise uma ordem de prioridade para o desenvolvimento futuro.

As citações seguem o sistema autor-data da ABNT NBR 10520:2023, com a página indicada sempre que a informação vem de um trecho localizável do documento; as referências completas, no formato da NBR 6023:2018, estão na [seção 10](#10-referências). Os níveis estão em metros, e toda comparação com previsões públicas indica a régua de referência, porque as duas réguas de Porto Alegre usam datums diferentes, questão tratada na [seção 6.4](#64-duas-réguas-dois-datums).

**Sumário**

1. [Julho de 2026: um teste em tempo real](#1-julho-de-2026-um-teste-em-tempo-real)
2. [Reprodução das quatro versões em 2024 e 2026](#2-reprodução-das-quatro-versões-em-2024-e-2026)
3. [A escolha de partir apenas da água medida nos rios](#3-a-escolha-de-partir-apenas-da-água-medida-nos-rios)
4. [Problemas encontrados neste modelo](#4-problemas-encontrados-neste-modelo)
5. [Problemas relatados pelo IPH/UFRGS](#5-problemas-relatados-pelo-iphufrgs)
6. [Lacunas comuns a todos os modelos do Guaíba](#6-lacunas-comuns-a-todos-os-modelos-do-guaíba)
7. [Onde este modelo segue a abordagem do IPH](#7-onde-este-modelo-segue-a-abordagem-do-iph)
8. [O que reduziria o erro](#8-o-que-reduziria-o-erro)
9. [Documentos consultados](#9-documentos-consultados)
10. [Referências](#10-referências)

---

## 1. Julho de 2026: um teste em tempo real

O modelo foi construído em 22 de julho de 2026, com uma cheia do Taquari já em curso, e passou a ser usado ao vivo nos dias seguintes. A vazão em Lajeado chegou a cerca de 11.100 m³/s na madrugada de 23 de julho, segundo a telemetria da ANA, e o Guaíba respondeu em duas ondas, com os seguintes máximos:

| Onda | Pico observado, Cais Mauá (C6) | Pico observado, Gasômetro |
|---|---|---|
| 1ª | **2,15 m**, 24/07 15h | 1,53 m, 24/07 20h |
| 2ª | **2,59 m**, 31/07 20h | 1,89 m, 31/07 21h |

Como os registros da sessão de trabalho em que as previsões foram emitidas não sobreviveram, reconstruímos o comportamento do modelo reexecutando cada versão com os dados cortados em instantes sucessivos do evento, de modo que cada previsão use apenas o que estava disponível naquele momento (`scripts/replay_event.py`; saída em [`resultados/reproducao_2026-07_cais-maua.csv`](resultados/reproducao_2026-07_cais-maua.csv)). Os valores da tabela correspondem ao pico do cenário central, convertido para a régua do Cais Mauá com o deslocamento de +0,44 m adotado pelo dashboard, para permitir a comparação direta com as previsões divulgadas na imprensa, todas referidas a essa régua.

| Corte | v1 | v2 | v3 | v4 | Previsões públicas no mesmo período |
|---|---|---|---|---|---|
| 21/07 12h | 1,54 | 1,51 | 1,52 | 1,49 | MetSul: "perto, ao redor e acima de 2 metros" (Aureliano, 2026a) |
| 22/07 00h | 2,96 | 2,84 | 2,98 | 4,78 | |
| 22/07 12h | 4,97 | 4,52 | 4,80 | 6,61 | |
| 22/07 20h | 4,77 | 4,37 | 4,61 | 4,75 | SGB, IPH e Catavento (22/07 19h50): Cais Mauá pode atingir 2,50 m; IPH: 2,50 a 2,60 m prováveis (Ribeiro, 2026a) |
| 23/07 10h | 3,97 | 3,53 | 3,67 | 3,82 | SGB, IPH e Catavento: cota de alerta de 2,5 m no Cais Mauá entre 24 e 25/07; segundo a prefeitura, sem previsão de alcançar a cota de inundação de 3 m (Subida..., 2026). O Dmae informou que cenários técnicos chegaram a indicar a possibilidade de o Guaíba ultrapassar 3 m (Galhardo, 2026) |
| 23/07 16h | 3,70 | 3,31 | 3,40 | 3,38 | IPH, via imprensa: até 2,70 m no Cais Mauá no sábado, 25/07 (Aiquel, 2026; Nível..., 2026) |
| 24/07 00h | 2,87 | 2,48 | 2,50 | 2,38 | |
| 24/07 08h | 2,35 | 2,16 | 2,15 | 2,03 | MetSul: 2,3 a 2,5 m nas 48 h seguintes (Guaíba alcança..., 2026) |
| 24/07 12h | 2,13 | 2,04 | 2,02 | 2,01 | Dmae fecha comportas a partir do meio-dia, com previsão de 2,50 a 2,70 m (Dmae..., 2026) |
| 28/07 12h | 2,44 | 2,15 | 2,21 | 2,51 | |
| 29/07 10h | 4,92 | 4,46 | 4,74 | 4,97 | Boletim SGB/IPH (29/07): pode superar 3 m até 01/08; cenário mais adverso perto de 3,50 m (Ribeiro, 2026b; Guaíba pode..., 2026) |
| 30/07 08h | 3,93 | 3,47 | 3,57 | 3,98 | MetSul: até 2,5 m (Nachtigall, 2026) |
| 30/07 12h | 3,77 | 3,32 | 3,39 | 3,70 | SGB/IPH, revisado: entre 2,60 e 3,00 m (Aureliano, 2026b) |
| 31/07 00h | 3,04 | 2,81 | 2,81 | 3,14 | |
| 31/07 10h | 2,58 | 2,56 | 2,54 | 2,89 | IPH (Meirelles): deve ficar abaixo de 3 m (Azeredo, 2026; Freitas, 2026) |

O resultado central é inequívoco: todas as versões superestimaram as duas ondas enquanto os afluentes ainda subiam, com erros entre 2,3 e 2,8 m (até 4,5 m no v4) cerca de dois dias e meio antes de cada pico, e só convergiram para valores a menos de 15 cm do observado depois que a crista de montante havia passado, em 24 de julho às 8h e em 31 de julho às 10h, poucas horas antes dos respectivos máximos. Uma previsão que acerta apenas quando o evento já está praticamente definido tem pouco valor operacional, e esse é o diagnóstico que orienta o restante do documento.

As previsões oficiais também erraram para cima, mas numa escala muito diferente. Na primeira onda, o SGB e o IPH trabalharam com 2,50 a 2,70 m no Cais Mauá, depois de cenários acima de 3 m que chegaram a circular e foram abandonados (Galhardo, 2026), e o pico real ficou em 2,15 m, o que corresponde a um erro de 0,35 a 0,55 m. Na segunda, o boletim de 29 de julho admitia superar 3 m, com um cenário adverso em torno de 3,50 m (Ribeiro, 2026b), e foi revisado no dia seguinte para a faixa entre 2,60 e 3,00 m (Aureliano, 2026b); o máximo observado foi 2,59 m.

Há, contudo, momentos em que as duas fontes coincidem. Em 23 de julho, as quatro versões do modelo indicavam entre 3,3 e 4,0 m, valores compatíveis com os cenários técnicos acima de 3 m que, segundo o Dmae, justificariam o fechamento preventivo das comportas (Galhardo, 2026). Em 29 e 30 de julho, o modelo indicava de 3,3 a 4,0 m, enquanto o boletim oficial falava em superar 3 m e num cenário adverso próximo de 3,50 m. A coincidência ocorre precisamente nos instantes de maior incerteza, e se desfaz quando a previsão oficial se estabiliza, momento a partir do qual o modelo permanece bem acima dela até a passagem da crista.

O desempenho relativo das versões também contraria o que o hindcast de maio de 2024 sugeria. Ali, o v1 obteve o menor erro de nível; em julho de 2026, a versão menos ruim durante a subida foi o v2. Que nenhuma das versões se mostre consistentemente superior é sinal de sobreajuste aos poucos eventos disponíveis para calibração, problema retomado na seção 4.6. Muitos dos picos da tabela, por fim, coincidem com o último passo do horizonte de 72 horas, o que significa que o modelo ainda previa subida quando a integração terminou e que o máximo implícito seria ainda maior (seção 4.5).

## 2. Reprodução das quatro versões em 2024 e 2026

Os cortes da seção 1 foram escolhidos para coincidir com as previsões divulgadas na imprensa. Para avaliar o modelo de forma sistemática, reexecutamos as quatro versões a cada seis horas ao longo de três períodos: a cheia de maio e junho de 2024, de 29 de abril a 25 de junho (229 cortes); a cheia de julho de 2026, de 19 de julho a 3 de agosto (61 cortes); e o evento de setembro e outubro de 2026, de 18 de setembro a 14 de outubro (105 cortes), que atingiu 1,88 m no Gasômetro e 2,48 m no Cais Mauá em 2 de outubro, segundo a telemetria da ANA. Em cada corte, o modelo usa apenas os dados disponíveis até aquele instante, e o pico previsto é comparado com o máximo que o Gasômetro de fato registrou nas 72 horas seguintes. Todos os níveis desta seção estão no datum do Gasômetro, para evitar a conversão entre réguas discutida na seção 6.4. As tabelas completas estão em [`resultados/`](resultados/), geradas por `scripts/replay_event.py`, e o resumo abaixo sai de `scripts/summarize_replays.py`.

Os três períodos não têm o mesmo valor como teste. A cheia de 2024 está dentro da amostra de calibração de todas as versões, de modo que o desempenho nela é um limite otimista. O v1 foi calibrado em 22 de julho de 2026 e as versões v2 a v4 entre 23 e 24 de julho, com a primeira onda daquele mês já em curso; julho de 2026 é, portanto, um teste apenas parcialmente fora da amostra. Somente o evento de setembro e outubro ocorreu depois de todas as calibrações, e é ele que oferece o teste mais limpo. Há ainda uma limitação própria de 2024: a régua do Gasômetro só voltou a medir na tarde de 3 de maio (Collischonn et al., 2025, p. 16), e a primeira leitura válida da telemetria é das 15h desse dia. Para os cortes anteriores usamos a régua do Cais Mauá subtraída de 0,44 m. Como a diferença entre as réguas cresce durante as cheias (seção 6.4), essa conversão tende a superestimar o nível de partida do modelo nos dias próximos ao pico; entre as 23h de 2 de maio e as 15h de 3 de maio não há leitura alguma, e os cortes desse intervalo partem da última disponível.

| Período | Versão | Erro absoluto médio | Viés nos cortes com subida à frente | Pior erro | Viés nos demais cortes | Faixa de cenários contém o observado | Pico no fim do horizonte |
|---|---|---|---|---|---|---|---|
| 2024 (dentro da amostra) | v1 | 0,35 m | +0,31 m | +2,52 m | +0,09 m | 9% | 25% |
| | v2 | 0,28 m | +0,15 m | +2,04 m | +0,07 m | 11% | 30% |
| | v3 | 0,32 m | +0,24 m | +2,36 m | +0,08 m | 12% | 30% |
| | v4 | 0,45 m | +0,45 m | +3,76 m | +0,11 m | 11% | 26% |
| Julho de 2026 (parcialmente fora) | v1 | 0,84 m | +0,78 m | +3,10 m | +0,28 m | 3% | 67% |
| | v2 | 0,71 m | +0,57 m | +2,61 m | +0,28 m | 0% | 75% |
| | v3 | 0,77 m | +0,67 m | +2,93 m | +0,29 m | 0% | 75% |
| | v4 | 0,96 m | +0,84 m | +4,65 m | +0,40 m | 2% | 79% |
| Set./out. de 2026 (fora da amostra) | v1 | 0,62 m | +0,61 m | +3,10 m | +0,39 m | 3% | 43% |
| | v2 | 0,51 m | +0,44 m | +2,57 m | +0,30 m | 2% | 44% |
| | v3 | 0,57 m | +0,53 m | +2,91 m | +0,33 m | 1% | 43% |
| | v4 | 0,59 m | +0,61 m | +4,16 m | +0,25 m | 3% | 55% |

Fonte: elaborada pelos autores a partir da telemetria da ANA (Agência Nacional de Águas e Saneamento Básico, 2026b). Erro = pico central previsto menos máximo observado nas 72 h seguintes ao corte. Cortes com subida à frente são aqueles em que esse máximo supera em mais de 10 cm o nível do corte.

O erro dobra ou triplica ao sair da amostra de calibração e, em todos os períodos e versões, é positivo: o modelo superestima. O v2 tem o menor erro médio nos três períodos, o que corrige a impressão deixada pelo hindcast de corte único descrito na metodologia, em que o v1 parecia superior (seção 1); o v4 tem o pior erro máximo em todos eles. A separação entre cortes com e sem subida à frente localiza o problema. Quando nenhuma onda se aproxima, o viés em 2024 fica em torno de 10 cm, mas nos dois eventos de 2026 permanece entre +0,25 e +0,40 m, valor que já não depende da extrapolação de crista e que confirma, agora fora da amostra, o exagero estrutural em cheias médias atribuído à curva de saída (seções 4.2 e 4.4). Quando uma onda se aproxima, o viés médio sobe para +0,15 a +0,45 m em 2024 e para +0,44 a +0,84 m em 2026, e os piores casos passam de 2 m em todas as versões.

A faixa entre os cenários otimista e pessimista conteve o máximo observado em no máximo 12% dos cortes, e em quase nenhum fora da amostra. Os três cenários diferem apenas na constante de subida da extrapolação de crista ([METODOLOGIA §4.1](METODOLOGIA.md#41-extrapolação-de-crista-heurística-do-projeto)), variação estreita demais para representar a incerteza real; o dashboard não deveria apresentá-la como intervalo de confiança. A fração de picos que caem no último passo do horizonte, de 43 a 79% em 2026, mostra ainda que o problema descrito na seção 4.5 é a regra durante as cheias, e não a exceção.

A segunda tabela acompanha cada pico observado e mostra o que o v1 previa em cortes feitos 72, 48, 24 e 12 horas antes.

| Pico observado (Gasômetro) | Nível | v1, −72 h | v1, −48 h | v1, −24 h | v1, −12 h |
|---|---|---|---|---|---|
| 14/05/2024 20h | 4,06 m | 3,99 | 5,45 | 4,68 | 4,53 |
| 24/05/2024 19h | 3,14 m | 2,83 | 2,77 | 2,73 | 3,30 |
| 03/06/2024 07h | 2,68 m | 2,52 | 2,41 | 2,32 | 2,27 |
| 24/07/2026 21h | 1,52 m | 1,68 | 4,39 | 3,12 | 2,01 |
| 31/07/2026 21h | 1,88 m | 2,73 | 4,24 | 2,96 | 2,30 |
| 22/09/2026 22h | 1,65 m | 0,73 | 0,83 | 3,55 | 4,58 |
| 02/10/2026 01h | 1,88 m | 3,68 | 4,17 | 2,86 | 2,16 |
| 11/10/2026 19h | 1,67 m | 1,94 | 2,04 | 2,03 | 1,89 |

Fonte: elaborada pelos autores a partir da telemetria da ANA (Agência Nacional de Águas e Saneamento Básico, 2026b). O primeiro pico de 2024, em 5 de maio, ficou de fora porque a régua do Gasômetro começa no meio da subida, e é tratado no texto abaixo. As previsões das demais versões estão nos arquivos de [`resultados/`](resultados/).

O padrão de julho se repetiu em setembro, num evento que nenhuma versão havia visto. Às 6h de 21 de setembro, quando a chuva forte já caía em Lajeado, com 38 mm desde a meia-noite, e começava em Muçum, que registraria 110 mm nas seis horas seguintes, o modelo ainda previa nível estável, porque nada daquela água havia chegado às estações de entrada. Seis horas depois, a previsão do v1 saltou para 2,67 m e, à meia-noite de 22 de setembro, para 4,75 m, com 5,81 m pelo v4, contra um pico de 1,65 m. Nas estações de Muçum, Encantado e Lajeado, a chuva havia parado entre 14h15 e 17h15 de 21 de setembro, de sete a dez horas antes dessa previsão, e a crista de Lajeado, de 10.760 m³/s, passou às 12h15 de 22 de setembro. Na segunda onda, a chuva parou nas três estações entre 10h e 10h45 de 29 de setembro, e a previsão da meia-noite seguinte indicou 4,17 m pelo v1, para um pico de 1,88 m; a crista de Lajeado, de 9.570 m³/s, passou às 6h de 30 de setembro (valores calculados sobre a telemetria da ANA). São quatro ondas, em dois eventos de 2026, com a mesma sequência: o modelo não vê nada enquanto a chuva cai, dispara quando a água chega às estações e só converge quando a crista passa, e no momento das piores previsões a chuva já havia parado fazia horas. A seção 3 discute a origem desse comportamento. A terceira onda do período, alimentada por uma chuva menor, de cerca de 60 mm nas mesmas estações, produziu erros de +0,2 a +0,4 m no v1, próximos do viés de fundo.

Nem na cheia de 2024, dentro da amostra, o modelo acertou a subida principal. Até as 12h de 29 de abril, com a régua do Cais Mauá ainda abaixo de 1,30 m, nenhuma versão previa elevação. Entre as 18h de 30 de abril e o fim de 3 de maio, as previsões do v1 oscilaram entre 4,52 e 6,27 m, as do v2 entre 3,93 e 5,54 m e as do v4 entre 4,71 e 5,93 m, contra um máximo de 4,17 m no Gasômetro às 5h30 de 5 de maio. Parte desse excesso pode vir da conversão do Cais Mauá para o datum do Gasômetro, que superestima o nível de partida perto do pico, mas não todo: entre 30 de abril e a manhã de 1º de maio, com o Cais Mauá abaixo de 2 m e o deslocamento de 0,44 m ainda adequado, o v1 já previa entre 4,5 e 5,7 m. O sinal de alerta teria chegado com mais de quatro dias de antecedência e na ordem de grandeza correta; o valor numérico, não.

Os picos secundários de 2024 mostram o erro inverso. Em 24 de maio e 3 de junho, o nível do Gasômetro subiu de 30 a 40 cm em cerca de um dia, e o v1 ficou abaixo do observado em sete dos oito cortes da tabela que antecedem esses dois picos. Subidas rápidas como essas, na recessão de uma cheia, são compatíveis com o represamento pelo vento, que o IPH apontou como a principal fonte de erro na fase de recessão de 2024 (Medeiros; Fan; Paiva, 2025, p. 14). Como o sistema não baixa dados de vento (seção 3), não pudemos verificar essa hipótese.

## 3. A escolha de partir apenas da água medida nos rios

O modelo deixa de fora a chuva e o vento por decisão de partida, e não por descuido. A proposta inicial era trabalhar somente com a água que já corre nos afluentes e que a rede telemétrica da ANA acompanha a cada 15 minutos, para saber até onde essa informação, sozinha, leva a previsão do nível do Guaíba. A pergunta tinha interesse próprio: separa o que a rede de monitoramento já sabe num dado instante daquilo que depende de previsão meteorológica, e um modelo restrito a dados observados roda apenas com telemetria pública, sem modelos numéricos de tempo, com cada hipótese exposta à verificação direta. A cheia de julho de 2026 permite avaliar o que essa escolha rendeu e o que custou.

A primeira constatação é que a água já medida cobre só o começo do horizonte. Os tempos de viagem calibrados até o Guaíba vão de 6 horas, no Sinos e no Gravataí, a 26 horas, no Taquari ([METODOLOGIA §2.2](METODOLOGIA.md#22-tempos-de-viagem-defasagens-heurística-do-projeto)), e depois desse intervalo a vazão que chegará ao lago ainda não passou por nenhuma estação. Num horizonte de 72 horas, cerca de dois terços da previsão do Taquari, e mais nos rios de viagem curta, dependem, portanto, da extrapolação de crista descrita na seção 4.1, e não de água observada. A regra de leitura proposta na [METODOLOGIA §7.3](METODOLOGIA.md#73-volatilidade-da-previsão-numa-cheia-real), segundo a qual a entrada prevista para as 24 horas seguintes merece confiança e o pico absoluto não, decorre diretamente dessa divisão.

A segunda constatação, a nosso ver a mais importante, é que excluir a chuva não tornou o modelo neutro em relação a ela. A extrapolação de crista supõe que a taxa de subida de cada afluente decai de forma exponencial, com constantes ajustadas em eventos passados ([METODOLOGIA §4.1](METODOLOGIA.md#41-extrapolação-de-crista-heurística-do-projeto)); isso equivale a presumir quanto chove ainda, ou quanto da chuva já caída falta chegar ao rio, sem observar nenhuma das duas coisas. O modelo não produz, assim, uma previsão sem chuva, e sim uma previsão com chuva presumida a partir do histórico. Os pluviômetros das próprias estações que o modelo consulta mostram o custo dessa presunção. Em Muçum, Encantado e Lajeado, no Taquari, a chuva forte de 21 de julho caiu entre as 6h e a meia-noite, somando de 69 a 74 mm nesse intervalo em cada estação, e nas doze horas seguintes nenhuma delas registrou mais de 3 mm. Foi justamente ao meio-dia de 22 de julho, com a chuva forte encerrada havia doze horas, que o modelo emitiu sua pior previsão da primeira onda: 4,97 m no Cais Mauá pelo v1 e 6,61 m pelo v4, para um pico observado de 2,15 m (seção 1). Lajeado atingiu a crista, de 11.100 m³/s, às 0h45 de 23 de julho, cerca de 25 horas depois do fim da chuva forte. A segunda onda repetiu o padrão: depois de 99 a 144 mm desde 27 de julho, a chuva cessou nas três estações entre 3h15 e 5h30 de 29 de julho; a previsão das 10h desse dia indicou 4,92 m pelo v1, contra um pico de 2,59 m, e a crista de Lajeado, de 10.260 m³/s, passou às 20h15 do mesmo dia. Todos esses valores foram calculados sobre a telemetria da ANA (Agência Nacional de Águas e Saneamento Básico, 2026b), cujo campo de chuva o sistema já baixa e armazena junto com o nível e a vazão, sem usá-lo no cálculo. A informação de que a chuva havia parado, suficiente para conter a extrapolação, estava disponível no momento de cada previsão e ficou de fora por construção.

Três pluviômetros pontuais não equivalem à chuva média da bacia, e uma chuva intensa nas cabeceiras, a montante de Muçum, poderia escapar deles. O sinal, no entanto, é consistente nas três estações e se repetiu nas duas ondas de setembro e outubro de 2026, evento posterior a todas as calibrações (seção 2), e concorda com o que a seção 7 mostra a partir de outra direção: as previsões do IPH que desconsideravam chuva e vento subestimaram os níveis em maio de 2024 (Medeiros; Fan; Paiva, 2025, p. 11), ao passo que este modelo superestimou em julho de 2026. Um cenário sem chuva de fato erra para baixo; o nosso errou para cima porque a extrapolação introduziu, sem dizer, mais chuva do que houve.

A terceira constatação diz respeito à própria premissa de que a água relevante está sendo rastreada. Parte dela chega ao Guaíba sem passar por estação alguma. A chuva que cai diretamente sobre o lago é a parcela mais simples de estimar: o pluviômetro do Gasômetro registrou 97,4 mm entre 19 e 23 de julho, o que, sobre os 470 km² do espelho d'água, corresponde a cerca de 46 milhões de m³ e a no máximo uns 10 cm de nível, enquanto a régua do Gasômetro subiu de 0,48 m, em 19 de julho, para 1,53 m no pico (valores calculados sobre a telemetria da ANA). A contribuição direta sobre o lago é, portanto, secundária, embora não desprezível. Maior é a área que drena para o Guaíba a jusante das estações de entrada, cerca de 13.800 km² segundo o inventário da ANA (seção 4.4), quase trinta vezes a superfície do lago, onde as estações do Caí, do Sinos e do Gravataí registraram de 126 a 151 mm no mesmo período. Não sabemos que fração dessa chuva virou escoamento, e o modelo não tem como saber; somada às lacunas de transmissão das estações de entrada (seção 4.7), essa água não rastreada ajuda a explicar a entrada subestimada que mascarou, durante a calibração, a curva de saída subdimensionada (seção 4.4).

O vento, por sua vez, sequer é baixado pelo sistema. Vento de sudoeste pode elevar o nível do Guaíba em até cerca de 50 cm ao dificultar seu escoamento para a Lagoa dos Patos (Laipelt et al., 2026, p. 3), e o próprio IPH atribui às incertezas sobre o efeito do vento as falhas de suas previsões na fase de recessão da cheia de 2024 (Medeiros; Fan; Paiva, 2025, p. 14). Neste modelo, o efeito aparece em dois lugares, ambos indiretos. Na calibração, entra nos resíduos que a perda de Huber atenua no ajuste da curva de saída, sem que se possa separar quanto do expoente encostado no limite (seção 4.4) vem do vento, do remanso da lagoa ou de erros de entrada. Na previsão, entra na correção de viés, calculada sobre as últimas 24 horas e projetada sobre as 72 seguintes ([METODOLOGIA §4.3](METODOLOGIA.md#43-correção-de-viés-heurística-do-projeto)); quando o vento muda de direção dentro do horizonte, a correção passa a empurrar a previsão no sentido errado, e só percebe a mudança horas depois.

A abordagem trouxe, apesar disso, um ganho que justifica tê-la seguido até aqui. Como o modelo tem poucas partes e nenhuma delas depende de previsão meteorológica, cada erro pôde ser atribuído a um componente específico: a volatilidade à extrapolação de crista (seção 4.1), o viés em cheias médias à curva de saída e à falta de armazenamento no delta (seções 4.2 e 4.4). Com chuva e vento previstos misturados à entrada, essas causas teriam ficado indistinguíveis. O passo seguinte coerente com a proposta original nem exige previsão de chuva: basta usar a chuva já observada nas estações do modelo para limitar a extrapolação de crista, como a seção 8 propõe, antes de recorrer a um modelo chuva-vazão completo.

## 4. Problemas encontrados neste modelo

### 4.1 A extrapolação de crista dispara na subida

Para propagar um afluente que ainda está subindo, o modelo precisa estimar até onde ele vai, e o faz com uma hipótese de decaimento exponencial da taxa de subida ([METODOLOGIA §4.1](METODOLOGIA.md#41-extrapolação-de-crista-heurística-do-projeto)). Ao meio-dia de 22 de julho, Lajeado ainda subia cerca de 400 m³/s por hora, depois de ter chegado a 700 m³/s por hora algumas horas antes; alimentada com essas taxas, a hipótese projetou uma crista muito acima dos 11.078 m³/s que o rio de fato atingiu à 01h de 23 de julho (valores calculados sobre a telemetria da ANA). Esse mecanismo explica a maior parte do erro inicial e praticamente toda a volatilidade observada. Nada no modelo limita fisicamente a crista extrapolada, já que ele não dispõe de informação sobre a chuva que alimenta a subida nem utiliza o roteamento a partir das estações de montante para restringir a projeção.

### 4.2 Exagero estrutural em cheias médias

Mesmo depois da passagem da crista do Taquari, no corte de 24 de julho à 0h, o v1 ainda previa 2,87 m no Cais Mauá, contra os 2,15 m observados, e os hindcasts de junho de 2024 e de junho de 2025 exibem o mesmo viés, de cerca de meio metro para cima. Esse componente do erro não depende da extrapolação de crista, e sua causa principal é a curva de saída subdimensionada analisada na seção 4.4. Uma segunda causa provável contribui: o modelo lança a onda inteira do Taquari num único reservatório de 470 km², apenas deslocada no tempo e sem qualquer atenuação, quando na realidade boa parte dessa água se espalha antes pelo delta do Jacuí e pelas várzeas adjacentes. Laipelt et al. (2026, p. 1) mostram que, em 2024, o Taquari determinou o pico em Porto Alegre e o Jacuí respondeu pela maior parte da duração da cheia, o que indica que a forma da onda que chega ao Guaíba depende da interação entre os dois rios no delta; um modelo concentrado, calibrado sobretudo na cheia extrema de 2024, não dispõe de nenhum mecanismo equivalente para amortecer eventos menores.

### 4.3 A premissa de banheira (superfície plana)

A formulação do modelo pressupõe que a superfície da água permanece horizontal em todo o Guaíba, e as observações disponíveis indicam outra coisa. Medeiros, Fan e Paiva (2025, p. 6) caracterizam o comportamento do sistema durante a cheia de maio de 2024 como predominantemente fluvial, apesar das grandes áreas lacustres e de várzea: a onda se propagou como escoamento de rio, com velocidades altas e direção de fluxo bem definida, razão pela qual os autores consideraram adequado um modelo hidrodinâmico unidimensional. A campanha de ADCP de 5 de maio de 2024, na seção da Usina do Gasômetro, registrou corrente máxima de 4,2 m/s (Toldo et al., 2024, p. 1). Na cheia de junho de 2025, o nível no Cais Navegantes chegou a ficar cerca de 30 cm acima do registrado no Cais Mauá, poucos quilômetros a jusante (Universidade Federal do Rio Grande do Sul, 2025a, p. 6). Um modelo de armazenamento não tem como representar essa declividade da superfície entre o delta e Porto Alegre, que também explica por que o mapa de inundação erra cerca de 1,5 m de cota em Eldorado do Sul ([METODOLOGIA §6.3](METODOLOGIA.md#63-ressalvas)).

### 4.4 A curva de saída dá cerca de metade da vazão medida

Ajustada para fechar o balanço hídrico, a curva Qout(h) absorve todos os erros de entrada, de armazenamento e de vento, e dois indícios já apontavam para um ajuste problemático: o expoente encostado no limite superior permitido (b = 4,0), muito acima da faixa de 1,3 a 1,8 que Rantz et al. (1982, p. 330) indicam para controles de canal, e um erro quadrático médio de cerca de 2.000 m³/s. Faltava, porém, um teste independente, e ele se tornou possível com as três medições de vazão por ADCP que a equipe do PGA POA/UFRGS realizou no Guaíba (Toldo et al., 2024, p. 1; Universidade Federal do Rio Grande do Sul, 2025a, p. 9), nenhuma das quais entrou no ajuste do modelo. Avaliando a curva de cada versão no nível registrado pela telemetria do Gasômetro no momento de cada medição, obtém-se:

| Medição | Medido (ADCP) | Nível no Gasômetro | v1 | v2 | v3 | v4 |
|---|---|---|---|---|---|---|
| 05/05/2024 17h45 (seção do Gasômetro, corrigida pelo transbordamento) | 35.736 m³/s | 4,10 m | 16.432 (46%) | 17.178 (48%) | 16.635 (47%) | 6.249 (17%) |
| 15/05/2024 09h50 (Ponta do Dionísio) | 22.070 m³/s | 4,02 m | 15.879 (72%) | 16.599 (75%) | 16.077 (73%) | 6.145 (28%) |
| 25/06/2025 ~11h50 (Usina do Gasômetro) | 12.941 m³/s | 2,26 m | 6.265 (48%) | 6.528 (50%) | 6.361 (49%) | 3.897 (30%) |

Fonte: vazões medidas de Toldo et al. (2024, p. 1) e Universidade Federal do Rio Grande do Sul (2025a, p. 9); níveis da telemetria da ANA; vazões das versões v1 a v4 calculadas pelos autores.

Em cotas de cheia, a saída ajustada nas versões v1 a v3 corresponde a aproximadamente metade da vazão real, e no v4 a fração é ainda menor. O balanço fechou durante a calibração porque a entrada também estava subestimada, e numa proporção semelhante. Duas razões concorrem para isso. As estações de entrada apresentam lacunas longas (seção 4.7), e uma parte da bacia fica a jusante delas: segundo o inventário de estações da ANA, Rio Pardo, Estrela, Barca do Caí, São Leopoldo e Passo das Canoas controlam juntas cerca de 68.700 km², contra 82.500 km² de área de drenagem na estação da Usina do Gasômetro (Agência Nacional de Águas e Saneamento Básico, 2026a), de modo que a vazão gerada nos cerca de 13.800 km² restantes, 17% da bacia, não entra no cálculo. A área não monitorada, sozinha, não explica um déficit de metade da vazão; somada às lacunas das estações, que retiram afluentes inteiros da soma por dias seguidos, torna o déficit plausível.

Com dois erros que se compensam, os hindcasts parecem aceitáveis, e o problema só se manifesta quando um dos erros desaparece. Foi o que ocorreu em julho de 2026, quando Lajeado transmitiu vazão de forma contínua durante a cheia e a entrada chegou ao modelo praticamente completa: diante de uma saída que só escoa metade do que deveria, o nível previsto subiu demais. Excluída a extrapolação de crista, essa é provavelmente a principal causa estrutural do exagero descrito na seção 1. O mesmo resultado confirma, com dados, o problema de identificabilidade apontado na [METODOLOGIA, §3.4](METODOLOGIA.md#34-identificabilidade), e indica também o caminho para superá-lo, que consiste em ancorar a curva de saída nas medições de ADCP (seção 8).

### 4.5 Picos cortados no fim do horizonte

Quando o máximo previsto coincide com o último passo das 72 horas, ele representa um limite inferior e não um pico, porque o modelo ainda estava em subida quando a integração terminou. O `scripts/replay_event.py` identifica esses casos (colunas `*_at_horizon`), mas o dashboard não os sinaliza, e deveria fazê-lo, seja estendendo o horizonte, seja informando ao usuário que o nível continua a subir em +72 h.

### 4.6 Poucos eventos, um extremo

A calibração dispõe de três eventos, e um deles, maio de 2024, situa-se muito fora da faixa dos outros dois. Os parâmetros ajustados sob a influência dominante desse evento, como os do v1, desempenham melhor nele e exageram as cheias menores; o v2, ligeiramente pior em maio de 2024, foi o melhor em julho de 2026. Com tão poucos eventos, qualquer escolha de versão operacional baseada em hindcast carrega o risco de premiar o ajuste a um único episódio.

### 4.7 Estações de entrada com buracos

Ao longo do registro completo, Lajeado tem dados de vazão em apenas 7% das horas, e Rio Pardo em 41% ([DADOS.md](DADOS.md#peculiaridades-dos-dados-que-moldam-o-modelo)). Cada lacuna retira silenciosamente um afluente importante da soma de entrada, e a curva de saída, durante a calibração, compensa a ausência ajustando-se para baixo. É essa compensação que a seção 4.4 quantifica.

## 5. Problemas relatados pelo IPH/UFRGS

O IPH/UFRGS conduziu as previsões operacionais do Guaíba em maio de 2024 e, em parceria com o SGB, em julho de 2026, e os trabalhos publicados pela equipe descrevem várias das dificuldades encontradas aqui. A comparação interessa por dois motivos: mostra quais problemas decorrem dos dados disponíveis, e não das simplificações deste modelo, e oferece uma referência para avaliar o tamanho do erro que se pode esperar mesmo de um sistema muito mais completo.

O primeiro desses problemas é a rede de monitoramento. O modelo MGB dispõe de um esquema de assimilação de vazões observadas, mas Medeiros, Fan e Paiva (2025, p. 6) relatam que ele não foi usado na elaboração das previsões de 2024, porque várias das estações que alimentariam a assimilação estavam danificadas ou fora de operação em consequência das chuvas e cheias. O SGB documenta que estações das bacias do Taquari e do Caí foram levadas pela correnteza ou sofreram danos severos nos equipamentos, e que a operação dos sistemas de alerta dessas bacias ficou "seriamente comprometido" (Marcuzzo et al., 2024, p. 5). Dois anos depois, a situação persistia. Em 31 de julho de 2026, o professor Fernando Meirelles, do IPH, afirmou ao Sul21 que o Guaíba havia subido "no tempo esperado", mas dentro de uma "banda de incerteza", e atribuiu essa incerteza à dificuldade de calcular a vazão dos afluentes, já em descida, porque a rede de estações danificada em 2024 não recebeu manutenção em vários pontos; acrescentou que a medição feita longe da Capital amplia a incerteza natural da previsão (Azeredo, 2026).

Ainda mais diretamente relacionado ao erro deste modelo é o problema das curvas-chave nas estações de que ele depende. Em Estrela/Lajeado, estação 86879300, a mesma que o modelo usa para o Taquari, o pico de 2024 alcançou 33,66 m, enquanto as medições de vazão que sustentam a curva-chave chegam a cerca de 25 m; o pico estimado de 23.472 m³/s é, portanto, uma extrapolação, cuja incerteza Collischonn et al. (2025, p. 14) classificam como alta. Em Muçum, a curva foi definida com medições até 8.380 m³/s, para um pico estimado em 13.241 m³/s (Collischonn et al., 2025, p. 14). Laipelt et al. (2026, p. 12) mencionam um relatório técnico do IPH e da ANA que aponta incerteza na extrapolação das curvas-chave sobretudo em Rio Pardo, no Jacuí, e em pontos do Taquari (Paiva et al., 2025 apud Laipelt et al., 2026, p. 12): as mesmas duas estações em que se concentra o erro de entrada deste modelo.

A modelagem hidrodinâmica enfrenta limitações análogas às nossas. Laipelt et al. (2026, p. 12) reconhecem que as condições de contorno de montante do seu modelo bidimensional não cobrem todos os afluentes da região, por falta de observações em campo, o que pode levar a subestimativas locais; o problema é da mesma natureza do que afeta o v4 quando roteia apenas as estações de montante. O mesmo trabalho mostra que variar somente a rugosidade de Manning no Guaíba entre 0,025 e 0,045 desloca o pico simulado no Cais Mauá entre −0,91 e +0,32 m (Laipelt et al., 2026, p. 13), ou seja, que a representação hidráulica da saída do lago é, também ali, a parte mais incerta do sistema, papel que no nosso modelo cabe à curva de saída.

O vento constitui a principal fonte de erro reconhecida pelo IPH depois que a cheia perde força. Vento de sudoeste dificulta a saída do Guaíba para a Lagoa dos Patos e pode elevar seu nível em até cerca de 50 cm, enquanto o de nordeste produz o efeito contrário (Laipelt et al., 2026, p. 3); para a cheia de 1941, Possa et al. (2022, p. 1) estimaram uma contribuição do vento ao pico da ordem de alguns centímetros a algumas dezenas de centímetros. Medeiros, Fan e Paiva (2025, p. 13) registram previsões de 20 e 21 de junho de 2024 que indicavam queda abaixo da cota de alerta para um fim de semana em que o nível chegou a 3,22 m, e atribuem as falhas dessa fase, em que a cheia já recuava lentamente, às incertezas sobre o efeito do vento (Medeiros; Fan; Paiva, 2025, p. 14). Os mesmos autores insistem que o desempenho do sistema dependeu da interpretação humana: os sinais de subida ou descida em horizontes superiores a 72 horas foram interpretados e discutidos entre os previsores, e os modelos passaram por ajustes e recalibrações ao longo do evento (Medeiros; Fan; Paiva, 2025, p. 14). Os números divulgados ao público são, portanto, saídas de modelo filtradas por julgamento especializado, o que torna a comparação com um modelo automático, como este, apenas parcialmente justa.

A nota técnica sobre a cheia de junho de 2025 traz informações relevantes para a questão da batimetria, retomada na seção 6.1. O IPH elaborou previsões hidrodinâmicas para esse evento com a batimetria anterior, porque o levantamento contratado pelo governo do estado ainda não estava disponível, e as previsões anteciparam com cerca de três dias a subida, a chegada à cota de alerta e a aproximação da cota de inundação (Universidade Federal do Rio Grande do Sul, 2025a, p. 14). A equipe relatou incerteza de 10 a 20 cm entre cenários e não identificou anomalia que sugerisse perda de precisão em consequência das alterações sofridas pelo leito em 2024 (Universidade Federal do Rio Grande do Sul, 2025a, p. 15).

Resta a questão de quem publica as previsões. O IPH divulgou previsões diárias do Guaíba no próprio site durante a cheia de 2024 e novamente em junho de 2025; a última delas, de 4 de julho de 2025, apresenta-se como "a última previsão emitida pela equipe para a cheia de junho de 2025" (Universidade Federal do Rio Grande do Sul, 2025b), e o site não traz nenhuma previsão com a marca do IPH para julho de 2026. Desde então, as previsões do Guaíba circulam nos boletins do SGB, elaborados "utilizando as técnicas desenvolvidas no projeto", isto é, no âmbito de um Termo de Execução Descentralizada entre o SGB e o IPH, com término previsto para novembro de 2026 e aditivo até junho de 2027 em tramitação. Um workshop conjunto realizado em setembro de 2026 discutiu procedimentos de previsão, emissão de boletins e "propostas de interpretação e comunicação de resultados" (Universidade Federal do Rio Grande do Sul, 2026). O IPH deixou, portanto, de publicar previsões em nome próprio, mas o motivo documentado é essa reorganização institucional; nenhuma das fontes consultadas associa a mudança a erros de superestimação.

## 6. Lacunas comuns a todos os modelos do Guaíba

### 6.1 Batimetria dos anos 1960

Os modelos hidrodinâmicos do IPH representam o leito do Guaíba e da Lagoa dos Patos com cartas náuticas digitalizadas da Diretoria de Hidrografia e Navegação da Marinha (Possa et al., 2022, p. 8; Laipelt et al., 2026, p. 5), e o modelo operacional de 2024 informa que essas cartas resultam de levantamentos feitos entre 1961 e 1966 (Lopes et al., 2018 apud Medeiros; Fan; Paiva, 2025, p. 6). No Taquari, onde os dados eram insuficientes, Laipelt et al. (2026, p. 5) rebaixaram manualmente o canal em cerca de 4 m no modelo digital de terreno, e reconhecem que os resultados dependem da precisão desse modelo e da batimetria (Laipelt et al., 2026, p. 12).

A cheia de maio de 2024 mobilizou grande volume de sedimentos, e cabe perguntar se uma batimetria de sessenta anos ainda descreve o leito. As evidências reunidas até aqui são parciais e não apontam todas na mesma direção:

| Fonte | O que encontrou |
|---|---|
| Nota técnica do IPH/UFRGS e do PGA POA: levantamento com sonda de feixe duplo e sonar de varredura lateral em 26/12/2024, três perfis comparados com a base das cartas náuticas anterior a 2022 (Universidade Federal do Rio Grande do Sul, 2025a, p. 10-12; Cheias..., 2025) | Rebaixamento por erosão do canal principal e do talvegue na seção da Usina do Gasômetro e nos dois canais do Jacuí a montante. Sedimento removido e rocha exposta em alguns trechos (a amostragem de sedimento bateu em rocha). Sem assoreamento generalizado. O IPH recomenda "mapeamentos periódicos e mais abrangentes de batimetria" (Universidade Federal do Rio Grande do Sul, 2025a, p. 17). |
| Batimetria do governo do estado, 2025/2026, comparada com levantamentos de 2013 e 2015 em poucos pontos de controle (Tuliszewski, 2026) | Nenhuma alteração significativa nos pontos de amostragem. Resultados parciais. |
| Projeto Guaíba (Unisinos, UFRGS, FEPAM), sísmica comparada com a da FEPAM de 2018 (Vargas, 2026) | "processos localizados de erosão, transporte e deposição de sedimentos", sobretudo no delta do Jacuí e em corredores preferenciais de fluxo. A extensão e a relação com 2024 ainda estão em avaliação; síntese final prevista para julho de 2028. |
| Banco de areia entre o Centro Histórico e Eldorado do Sul (Nova..., 2026) | Já aparecia nos mapas dos levantamentos de 1961–1964; cresceu depois de maio de 2024 para cerca de 1,4 km × 250 m. O governo do estado diz que não afeta as cheias. Fonte secundária. |

O conjunto não sustenta a hipótese de assoreamento em grande escala, mas documenta erosão do canal na seção do Gasômetro e nos canais do Jacuí, além de deposição em partes do delta. Esses trechos são justamente os que controlam a relação entre nível e vazão na régua utilizada por este modelo. A batimetria em que se apoiam os modelos hidrodinâmicos é anterior tanto à cheia de 2024 quanto a essas alterações; ainda assim, segundo o IPH, as previsões de junho de 2025, rodadas com essa batimetria antiga, não perderam precisão (Universidade Federal do Rio Grande do Sul, 2025a, p. 15). O aprofundamento do canal não está, portanto, demonstrado como fonte de erro de previsão, mas continua sem representação em qualquer dos modelos disponíveis, e os próprios autores recomendam levantamentos periódicos para acompanhá-lo.

Este modelo não utiliza batimetria diretamente, o que não o isenta do problema. Sua curva de saída foi ajustada com dados de maio de 2024 em diante e reflete, por isso, o canal posterior à cheia; ao mesmo tempo, mistura no mesmo ajuste a geometria vigente durante o evento e a que se estabeleceu depois dele. Se o leito próximo ao Gasômetro continuar a se modificar, a curva tenderá a derivar, e o deslocamento de datum entre as duas réguas também (seção 6.4). A curva cota-área e o mapa de inundação, por sua vez, derivam de um modelo de superfície produzido entre 2011 e 2015 (Airbus Defence and Space, 2022), igualmente anterior à cheia.

### 6.2 Vazões extrapoladas nos afluentes

Todo modelo do Guaíba obtém a vazão dos afluentes a partir das curvas-chave da ANA e do SGB, curvas que nas grandes cheias operam em regime de extrapolação (seção 5) e que podem ter se deslocado com as alterações do leito do Taquari em 2024. Este modelo não dispõe de nenhum mecanismo capaz de detectar uma curva deslocada: o erro entra diretamente em Qin e acaba absorvido pelo ajuste da curva de saída.

### 6.3 Nenhuma medição de vazão no Guaíba

Não há medição rotineira da vazão que o Guaíba entrega à Lagoa dos Patos. As campanhas de ADCP do PGA POA/UFRGS constituem os únicos dados independentes disponíveis, também utilizados por Laipelt et al. (2026) na validação de seu modelo: 35.736 m³/s em 5 de maio de 2024, na seção da Usina do Gasômetro, valor já corrigido pelo transbordamento sobre a Ilha da Pintada; 22.070 m³/s em 15 de maio de 2024, na Ponta do Dionísio (Toldo et al., 2024, p. 1); e 12.941 m³/s em 25 de junho de 2025, novamente na Usina do Gasômetro (Universidade Federal do Rio Grande do Sul, 2025a, p. 9). Para efeito de comparação, a vazão em condições normais fica entre 1.000 e 2.000 m³/s (Universidade Federal do Rio Grande do Sul, 2025a, p. 9), e o IPH estima os picos das cheias de setembro de 2023, novembro de 2023, maio de 2024 e junho de 2025 em 14,9, 16,0, 28,2 e 15,1 mil m³/s, respectivamente (Universidade Federal do Rio Grande do Sul, 2025a, p. 16). Foram essas três medições que permitiram expor o viés da curva de saída discutido na seção 4.4, e sua escassez é, por si só, uma das lacunas mais sérias para quem pretenda modelar o sistema.

### 6.4 Duas réguas, dois datums

As previsões públicas e as cotas de alerta referem-se à régua do Cais Mauá (C6), enquanto o modelo opera sobre a telemetria do Gasômetro, e a diferença entre as duas não é constante:

| Condição | Cais Mauá − Gasômetro |
|---|---|
| Registro completo, mediana | 0,42 m |
| Cheia de julho/2026, mediana | 0,52 m |
| Pico de 24/07/2026 | 0,62 m |
| Pico de 31/07/2026 | 0,70 m |

Fonte: calculado pelos autores a partir da telemetria da ANA das estações 87450004 e 87450020.

A diferença cresce com o nível, o que é coerente com a declividade da superfície descrita na seção 4.3. Como o modelo aplica um deslocamento fixo de +0,44 m, as previsões convertidas subestimam o nível do Cais Mauá durante as cheias, e o exagero apresentado na seção 1 é, se algo, um pouco maior do que a tabela sugere. Collischonn et al. (2025, p. 16) lembram que as réguas de Porto Alegre têm referências de nível independentes e não podem ser comparadas diretamente, e a relação entre elas no pico de maio de 2024 foi objeto de estudo específico do SGB (Germano et al., 2024); um deslocamento dependente do nível seria mais correto do que o valor fixo atual.

### 6.5 O vento não está no modelo

Os modelos do IPH incluem o vento como forçante, e este não. Como até cerca de 50 cm do nível do Guaíba podem decorrer do vento sobre a Lagoa dos Patos (Laipelt et al., 2026, p. 3), o efeito acaba absorvido pela correção de viés, que só o reconhece com algumas horas de atraso. A seção 3 explica por que o vento ficou de fora e onde, na calibração e na previsão, o seu efeito reaparece.

## 7. Onde este modelo segue a abordagem do IPH

Diversas escolhas de projeto seguem a metodologia publicada pelo IPH ou coincidem com ela, e a comparação lado a lado ajuda a localizar onde as diferenças de desempenho se originam:

| IPH/UFRGS | Este modelo |
|---|---|
| Correções simples de offset, para que cada previsão comece num nível consistente com a observação mais recente (Medeiros; Fan; Paiva, 2025, p. 6) | Correção de viés calculada nas últimas 24 h, aplicada em rampa para que a previsão comece no nível observado ([METODOLOGIA §4.3](METODOLOGIA.md#43-correção-de-viés-heurística-do-projeto)) |
| Conjuntos de cenários, incluindo um de referência sem chuva e sem vento (Medeiros; Fan; Paiva, 2025, p. 2, 11) | Três cenários de crista; sem entrada de chuva, o modelo inteiro equivale ao cenário de referência sem chuva |
| Contribuição de cada afluente e momento do seu pico: o Taquari define o pico, o Jacuí a duração, e picos sincronizados poderiam ter elevado o nível em 0,82 m (Laipelt et al., 2026, p. 1) | Entrada separada por rio, com tempos de viagem por rio |
| Cenários de vento para o represamento pela Lagoa dos Patos (Medeiros; Fan; Paiva, 2025, p. 8; Possa et al., 2022) | Não modelado; listado como limitação |
| Medições de ADCP como validação independente (Laipelt et al., 2026; Toldo et al., 2024) | Usadas aqui para testar a curva de saída (§4.4); o próximo passo é ajustar a curva a elas |

A comparação mais reveladora envolve o cenário sem chuva. Na avaliação que o IPH fez da cheia de maio de 2024, as previsões que desconsideravam chuva e vento subestimaram os níveis em horizontes mais longos, porque deixavam de fora a chuva que continuava a cair, e passaram a perder desempenho a partir de cerca de 24 horas (Medeiros; Fan; Paiva, 2025, p. 11). Este modelo, que na prática é uma previsão sem chuva, fez o oposto em julho de 2026 e superestimou. Se o cenário equivalente do sistema operacional erra para baixo e o nosso erra para cima, a origem do erro não está na ausência de chuva, mas na extrapolação de crista, na curva de saída que escoa metade do que deveria e na falta de armazenamento no delta (seções 4.1, 4.4 e 4.2).

## 8. O que reduziria o erro

A prioridade número um, à luz dos resultados acima, é ancorar a curva de saída nas medições de ADCP (seções 4.4 e 6.3). Isso pode ser feito por ajuste restrito ou pela inclusão de um termo de penalização, transferindo para o lado da entrada o desequilíbrio que restar, sob a forma de um fator de área não monitorada. A medida ataca o maior erro estrutural identificado e, como efeito colateral, reduz a não identificabilidade entre área e saída que a metodologia já apontava.

A extrapolação de crista é o segundo alvo, e três alternativas se apresentam, em ordem crescente de esforço. A primeira, coerente com a proposta de usar apenas dados observados, consiste em encerrar a subida extrapolada quando os pluviômetros das estações de montante indicam que a chuva parou, informação que o sistema já baixa e que, em julho e setembro de 2026, precedeu em 15 a 25 horas as cristas de Lajeado (seções 2 e 3). A segunda consiste em limitar a crista projetada com base nas estações de montante, como Muçum e Encantado, cuja passagem de onda antecede a de Lajeado em várias horas; a terceira, mais completa, em substituir a extrapolação por um modelo chuva-vazão do tipo MGB (Collischonn et al., 2007), que traria para o cálculo a informação que hoje falta. A seguir viria a inclusão de um segundo reservatório representando o delta do Jacuí e suas várzeas, capaz de amortecer as cheias médias que o modelo atual exagera.

As demais melhorias têm alcance menor, embora nenhuma seja trivial. O deslocamento de datum entre o Gasômetro e o Cais Mauá deveria variar com o nível, e o vento deveria entrar como preditor do represamento pela Lagoa dos Patos. O dashboard precisa sinalizar os picos cortados pelo horizonte e passar a registrar cada previsão emitida ao vivo, para que o próximo evento possa ser avaliado sem depender de reconstrução posterior, como foi necessário aqui. Por fim, quando o levantamento batimétrico posterior a 2024 for publicado, convém revisar a topografia e substituir, no mapa de inundação, o modelo de superfície por um modelo de terreno sem edificações, como o FABDEM (Hawker et al., 2022) ou o ANADEM empregado por Laipelt et al. (2026, p. 12).

## 9. Documentos consultados

Relacionamos abaixo todos os PDFs lidos para esta discussão, com a origem e o hash SHA-256 de cada um, para que qualquer leitor possa verificar que consulta o mesmo arquivo. Todos foram obtidos em 8 de novembro de 2026. Os que integram este repositório constam também de [`papers/SHA256SUMS`](../papers/SHA256SUMS), e a verificação pode ser feita executando `sha256sum -c SHA256SUMS` dentro de `papers/`.

### 9.1 Incluídos em `papers/` (licença aberta)

| Citação | Link | Tamanho (bytes) | SHA-256 |
|---|---|---|---|
| Medeiros, Fan e Paiva (2025) | [papers/2025_Medeiros_RBRH_Guaiba_emergency_forecasts.pdf](../papers/2025_Medeiros_RBRH_Guaiba_emergency_forecasts.pdf) · https://doi.org/10.1590/2318-0331.302520250025 | 4.624.444 | `1adeb4b9b373d215b9ec8e29991c4661ffa46a2806ebff7d0be4e6b5695ff212` |
| Laipelt et al. (2026) | [papers/2026_Laipelt_HESS_2024_flood_mechanisms.pdf](../papers/2026_Laipelt_HESS_2024_flood_mechanisms.pdf) · https://doi.org/10.5194/hess-30-573-2026 | 14.034.473 | `07456865174e3d2cc0293584fe31973db26aca86201065b92ee7e51047d6858e` |
| Collischonn et al. (2025) | [papers/2025_Collischonn_RBRH_2024_disaster.pdf](../papers/2025_Collischonn_RBRH_2024_disaster.pdf) · https://doi.org/10.1590/2318-0331.302520240119 | 6.788.699 | `53f671ed1e0976f84f830aba3868b6f73d57fb0304828b2f107cef4dfb9ade33` |
| Possa et al. (2022) | [papers/2022_Possa_RBRH_1941_flood_wind.pdf](../papers/2022_Possa_RBRH_1941_flood_wind.pdf) · https://doi.org/10.1590/2318-0331.272220220028 | 5.003.409 | `ed8b3b5a043d9f3cbadfddfe17bad37607d7819abc9469bd79ea630d6fc7d298` |
| Hawker et al. (2022) | [papers/2022_Hawker_FABDEM.pdf](../papers/2022_Hawker_FABDEM.pdf) · https://doi.org/10.1088/1748-9326/ac4d4f | 2.516.007 | `683ac0dd52233a10ddb2293ebe59e1763aacb6def2323af244aac1559be24321` |
| Rantz et al. (1982), v. 2 | [papers/1982_Rantz_WSP2175_vol2.pdf](../papers/1982_Rantz_WSP2175_vol2.pdf) · https://doi.org/10.3133/wsp2175 | 22.486.605 | `18f758d2cd3d5b136db559bbf2fc46dd9e3327a252393823f5518f8ad6f53eb4` |
| Yevjevich (1964) | [papers/1964_Yevjevich_WSP1690_flood_routing_bibliography.pdf](../papers/1964_Yevjevich_WSP1690_flood_routing_bibliography.pdf) · https://doi.org/10.3133/wsp1690 | 5.412.959 | `1fcabaaabf06f65d3f67bd646b5b3f257818a316b7178ff4ff81f25bc090762a` |

### 9.2 Consultados online, não redistribuídos (licença não declarada)

| Citação / documento | Link do PDF | Tamanho (bytes) | SHA-256 |
|---|---|---|---|
| Toldo et al. (2024), *Vazões no Rio Guaíba durante os picos da enchente de maio de 2024* | https://www.ufrgs.br/iph/wp-content/uploads/2024/07/05_Nota-Vazoes-no-Rio-Guaiba-durante-os-picos-da-enchente-de-maio-de-2024.pdf | 209.861 | `41ef47d53725ec6d83b55aa7e69f0161dbbf5ac83cdf7779cc98c2155531d027` |
| Universidade Federal do Rio Grande do Sul (2025a), *Nota técnica: monitoramento ambiental e cheia no Guaíba e Delta do Jacuí em junho de 2025* | https://www.ufrgs.br/iph/wp-content/uploads/2025/07/Nota-Tecnica_Cheia-no-Guaiba-.pdf | 14.972.315 | `3f4b79716ec6816669fc0bd8fb1dab1f08da647913ac641382161041e5a590a7` |
| Marcuzzo et al. (2024), nota técnica do SGB sobre os níveis máximos da cheia de maio de 2024, 3ª versão | https://rigeo.sgb.gov.br/bitstream/doc/24939.5/3/nota_tecnica_levantamento_cheia_2024_v.3.pdf | 4.103.092 | `93364c95e92576068be8800d1d9b14f580f25baa4a21bd36fe5e70bcbf440f50` |
| Soares e Marcuzzo, *Grandes cheias de 2023 e 2024 do rio Taquari: estudo preliminar das áreas inundadas em Encantado e Muçum* (SGB, pôster). Lido; não citado no texto | https://rigeo.sgb.gov.br/server/api/core/bitstreams/f620f9f9-1cbb-4b14-8c3c-a8eda53d47c2/content | 2.712.521 | `db0a7ee768afc46a4c047b45aca5a8948e5678a075b55b629d71121f1a64d0d7` |

Também lemos na íntegra páginas web que não são PDFs: as matérias de imprensa citadas na seção 1, as páginas do IPH sobre as previsões e o workshop com o SGB e as páginas do governo do estado, do jornal O Sul, da Unisinos e do Jornal do Comércio sobre batimetria. Todas estão na seção 10, com endereço e data de acesso.

### 9.3 Tentados e não obtidos

| Documento | Link | O que aconteceu |
|---|---|---|
| Boletins SGB/IPH da cheia de julho/2026 (SAH Guaíba, 22, 23, 24, 26, 29 e 30/07) | ex.: https://www.sgb.gov.br/sace/boletins/Guaiba/20260723_12-20260723%20-%20115622.pdf | HTTP 404 em 08/11/2026; conteúdo conhecido só pela imprensa |
| Trabalho sobre curvas-chave e as cheias de 2023/2024 (XXVI Simpósio Brasileiro de Recursos Hídricos) | https://lume.ufrgs.br/bitstream/handle/10183/303638/001299077.pdf | Conexão interrompida / HTTP 504; não usado |
| Aiquel (2026), Jornal do Comércio, 23/07/2026 | https://www.jornaldocomercio.com/geral/2026/07/1257312-guaiba-pode-chegar-a-270m-em-porto-alegre-no-fim-de-semana-diz-iph.html | Paywall após o primeiro parágrafo. O valor de 2,70 m no Cais Mauá, atribuído ao IPH, está confirmado em Dmae... (2026) e Nível... (2026) |

## 10. Referências

AGÊNCIA NACIONAL DE ÁGUAS E SANEAMENTO BÁSICO (Brasil). **HidroInventario**: inventário de estações hidrometeorológicas. Brasília, DF: ANA, 2026a. Web service ServiceANA. Consulta às estações 85900000, 86879300, 87170000, 87382000, 87399000 e 87450020. Disponível em: https://telemetriaws1.ana.gov.br/ServiceANA.asmx. Acesso em: 8 nov. 2026.

AGÊNCIA NACIONAL DE ÁGUAS E SANEAMENTO BÁSICO (Brasil). **DadosHidrometeorologicos**: dados telemétricos de nível, vazão e chuva. Brasília, DF: ANA, 2026b. Web service ServiceANA. Disponível em: https://telemetriaws1.ana.gov.br/ServiceANA.asmx. Acesso em: 8 nov. 2026.

AIQUEL, J. Guaíba pode chegar a 2,70m em Porto Alegre no fim de semana, diz IPH. **Jornal do Comércio**, Porto Alegre, 23 jul. 2026. Disponível em: https://www.jornaldocomercio.com/geral/2026/07/1257312-guaiba-pode-chegar-a-270m-em-porto-alegre-no-fim-de-semana-diz-iph.html. Acesso em: 8 nov. 2026.

AIRBUS DEFENCE AND SPACE. **Copernicus DEM**: Copernicus digital elevation model: product handbook. Version 5.0. [S. l.]: Airbus, 2022. Disponível em: https://dataspace.copernicus.eu/sites/default/files/media/files/2024-06/geo1988-copernicusdem-spe-002_producthandbook_i5.0.pdf. Acesso em: 8 nov. 2026.

AURELIANO, N. Nível do Guaíba subirá e MetSul informa risco nas ilhas de Porto Alegre. **Extra Classe**, Porto Alegre, 21 jul. 2026a. Disponível em: https://www.extraclasse.org.br/ambiente/2026/07/nivel-do-guaiba-subira-e-metsul-informa-risco-nas-ilhas-de-porto-alegre/. Acesso em: 8 nov. 2026.

AURELIANO, N. Nível do Guaíba sobe e novos temporais chegam ao RS no sábado. **Extra Classe**, Porto Alegre, 30 jul. 2026b. Disponível em: https://www.extraclasse.org.br/ambiente/2026/07/nivel-do-guaiba-sobe-e-novos-temporais-chegam-ao-rs-no-sabado/. Acesso em: 8 nov. 2026.

AZEREDO, L. Guaíba deve ficar abaixo da cota de inundação, mas falta de dados mantém incerteza na Capital. **Sul21**, Porto Alegre, 31 jul. 2026. Disponível em: https://sul21.com.br/noticias/geral/2026/07/guaiba-deve-ficar-abaixo-da-cota-de-inundacao-mas-falta-de-dados-mantem-incerteza-na-capital/. Acesso em: 8 nov. 2026.

CHEIAS dos rios do Estado não foram agravadas por assoreamento, mostra estudo da UFRGS. **O Sul**, Porto Alegre, 9 jul. 2025. Disponível em: https://www.osul.com.br/cheias-rios-nao-foram-agravadas-por-assoreamento/. Acesso em: 8 nov. 2026.

COLLISCHONN, W.; ALLASIA, D.; SILVA, B. C. da; TUCCI, C. E. M. The MGB-IPH model for large-scale rainfall-runoff modelling. **Hydrological Sciences Journal**, [S. l.], v. 52, n. 5, p. 878-895, 2007. DOI: https://doi.org/10.1623/hysj.52.5.878.

COLLISCHONN, W. et al. The exceptional hydrological disaster of April-May 2024 in southern Brazil. **RBRH**: Revista Brasileira de Recursos Hídricos, Porto Alegre, v. 30, e1, 2025. DOI: https://doi.org/10.1590/2318-0331.302520240119.

DMAE fechará comportas de Porto Alegre por prever elevação do Guaíba. **Sul21**, Porto Alegre, 24 jul. 2026. Disponível em: https://sul21.com.br/noticias/geral/2026/07/dmae-fechara-comportas-de-porto-alegre-por-prever-elevacao-do-guaiba/. Acesso em: 8 nov. 2026.

FREITAS, V. C. de. Guaíba passa dos 2m50cm no Cais Mauá; projeções não indicam cota de inundação. **Agora RS**, [S. l.], 31 jul. 2026. Disponível em: https://agorars.com/rs/porto-alegre/guaiba-atinge-cota-alerta-porto-alegre-previsao-inundacao/. Acesso em: 8 nov. 2026.

GALHARDO, G. Porto Alegre entra em alerta após alta do Guaíba e comportas podem ser fechadas. **Agência GBC**, [S. l.], 24 jul. 2026. Disponível em: https://agenciagbc.com/2026/07/24/porto-alegre-entra-em-alerta-apos-alta-do-guaiba-e-comportas-podem-ser-fechadas/. Acesso em: 8 nov. 2026.

GERMANO, A. de O.; LAMBERTY, D.; SILVA, E. D.; BUFFON, F. T.; PEDROLLO, M. C. R. **Avaliação indireta do nível máximo das águas do delta do Rio Jacuí na região central de Porto Alegre, entre as estações Cais Mauá C6 e Usina do Gasômetro, na grande cheia de maio de 2024**. Porto Alegre: Serviço Geológico do Brasil – CPRM, 2024. Relatório técnico. Disponível em: https://rigeo.sgb.gov.br/handle/doc/24911. Acesso em: 8 nov. 2026.

GUAÍBA alcança cota de cheia e deve atingir região das ilhas em Porto Alegre. **GAZ**, Santa Cruz do Sul, 24 jul. 2026. Disponível em: https://www.gaz.com.br/guaiba-alcanca-cota-de-cheia-e-deve-atingir-regiao-das-ilhas-em-porto-alegre/. Acesso em: 8 nov. 2026.

GUAÍBA pode superar cota de inundação no final de semana; Defesa Civil de Porto Alegre reforça Ilhas. **Sul21**, Porto Alegre, 29 jul. 2026. Disponível em: https://sul21.com.br/noticias/geral/2026/07/guaiba-pode-superar-cota-de-inundacao-no-final-de-semana-defesa-civil-reforca-ilhas/. Acesso em: 8 nov. 2026.

HAWKER, L.; UHE, P.; PAULO, L.; SOSA, J.; SAVAGE, J.; SAMPSON, C.; NEAL, J. A 30 m global map of elevation with forests and buildings removed. **Environmental Research Letters**, Bristol, v. 17, n. 2, 024016, 2022. DOI: https://doi.org/10.1088/1748-9326/ac4d4f.

LAIPELT, L.; FAN, F. M.; PAIVA, R. C. D. de; MEDEIROS, M. S.; COLLISCHONN, W.; RUHOFF, A. Mechanisms and scenarios of the unprecedent flooding event in South Brazil 2024. **Hydrology and Earth System Sciences**, [S. l.], v. 30, p. 573-590, 2026. DOI: https://doi.org/10.5194/hess-30-573-2026.

MARCUZZO, F. F. N. et al. **Nota técnica**: aferição direta e avalição [*sic*] indireta do nível máximo de rios em estações fluviométricas e marcas de inundação no Rio Grande do Sul na grande cheia de maio de 2024: 3. versão. Porto Alegre: Serviço Geológico do Brasil – CPRM, 2024. Disponível em: https://rigeo.sgb.gov.br/bitstream/doc/24939.5/3/nota_tecnica_levantamento_cheia_2024_v.3.pdf. Acesso em: 8 nov. 2026.

MEDEIROS, M. S.; FAN, F. M.; PAIVA, R. C. D. de. Emergency forecasts for water levels in the Guaíba River during the 2024 unprecedented flood in South Brazil. **RBRH**: Revista Brasileira de Recursos Hídricos, Porto Alegre, v. 30, e43, 2025. DOI: https://doi.org/10.1590/2318-0331.302520250025.

NACHTIGALL, L. F. Guaíba sobe mais e pode atingir cota de alerta com inundação nas ilhas. **MetSul Meteorologia**, [S. l.], 30 jul. 2026. Disponível em: https://metsul.com/guaiba-sobe-mais-e-pode-atingir-cota-de-alerta-com-inundacao-nas-ilhas/. Acesso em: 8 nov. 2026.

NÍVEL do Guaíba pode ficar a 30 centímetros da cota de inundação no cais de Porto Alegre neste fim de semana. **Rádio Pampa**, Porto Alegre, 23 jul. 2026. Disponível em: https://www.radiopampa.com.br/nivel-do-guaiba-pode-ficar-a-30-centimetros-da-cota-de-inundacao-no-cais-de-porto-alegre-neste-fim-de-semana/. Acesso em: 8 nov. 2026.

NOVA ilha no Guaíba. In: WIKIPÉDIA: a enciclopédia livre. [S. l.: s. n.], 2026. Revisão 72140419, de 27 abr. 2026. Disponível em: https://pt.wikipedia.org/wiki/Nova_ilha_no_Gua%C3%ADba. Acesso em: 8 nov. 2026.

POSSA, T. M.; COLLISCHONN, W.; JARDIM, P. F.; FAN, F. M. Hydrological-hydrodynamic simulation and analysis of the possible influence of the wind in the extraordinary flood of 1941 in Porto Alegre. **RBRH**: Revista Brasileira de Recursos Hídricos, Porto Alegre, v. 27, e29, 2022. DOI: https://doi.org/10.1590/2318-0331.272220220028.

RANTZ, S. E. et al. **Measurement and computation of streamflow**: volume 2: computation of discharge. Washington, DC: U.S. Geological Survey, 1982. (Water-Supply Paper, 2175). DOI: https://doi.org/10.3133/wsp2175.

RIBEIRO, A. Nível do Guaíba pode atingir cota de alerta neste final de semana em Porto Alegre. **Porto Alegre 24 Horas**, Porto Alegre, 22 jul. 2026a. Disponível em: https://poa24horas.com.br/tempo/2026/07/nivel-do-guaiba-pode-atingir-cota-de-alerta-neste-fim-de-semana-em-porto-alegre/. Acesso em: 8 nov. 2026.

RIBEIRO, A. Modelos hidrológicos preveem transbordamento do Guaíba em Porto Alegre até o final da semana. **Porto Alegre 24 Horas**, Porto Alegre, 29 jul. 2026b. Disponível em: https://poa24horas.com.br/noticias/2026/07/modelos-hidrologicos-preveem-transbordamento-do-guaiba-em-porto-alegre-ate-o-final-da-semana/. Acesso em: 8 nov. 2026.

SUBIDA do Guaíba prevista para o fim de semana põe áreas ribeirinhas de Porto Alegre em alerta. **Brasil de Fato**, Porto Alegre, 23 jul. 2026. Disponível em: https://www.brasildefato.com.br/2026/07/23/subida-do-guaiba-prevista-para-o-fim-de-semana-poe-areas-ribeirinhas-de-porto-alegre-em-alerta/. Acesso em: 8 nov. 2026.

TOLDO, E. et al. **Vazões no Rio Guaíba durante os picos da enchente de maio de 2024**: nota técnica. Porto Alegre: PGA POA – Portos RS/UFRGS, 24 jul. 2024. Disponível em: https://www.ufrgs.br/iph/wp-content/uploads/2024/07/05_Nota-Vazoes-no-Rio-Guaiba-durante-os-picos-da-enchente-de-maio-de-2024.pdf. Acesso em: 8 nov. 2026. Versão estendida: https://doi.org/10.5281/zenodo.14526481.

TULISZEWSKI, T. Governo do Estado apresenta resultados parciais da batimetria nos rios e lagos prioritários do Plano Rio Grande. **Portal do Estado do Rio Grande do Sul**, Porto Alegre, 29 mar. 2026. Disponível em: https://estado.rs.gov.br/governo-do-estado-apresenta-resultados-parciais-da-batimetria-nos-rios-e-lagos-prioritarios-do-plano-rio-grande. Acesso em: 8 nov. 2026.

UNIVERSIDADE FEDERAL DO RIO GRANDE DO SUL. Instituto de Pesquisas Hidráulicas. **Nota técnica**: monitoramento ambiental e cheia no Guaíba e Delta do Jacuí em junho de 2025. Porto Alegre: IPH/UFRGS; PGA POA, 2025a. Disponível em: https://www.ufrgs.br/iph/wp-content/uploads/2025/07/Nota-Tecnica_Cheia-no-Guaiba-.pdf. Acesso em: 8 nov. 2026.

UNIVERSIDADE FEDERAL DO RIO GRANDE DO SUL. Instituto de Pesquisas Hidráulicas. **Previsão de níveis do Guaíba (04/07/2025)**. Porto Alegre: IPH/UFRGS, 4 jul. 2025b. Disponível em: https://www.ufrgs.br/iph/previsao-de-niveis-do-guaiba-04-07-2025/. Acesso em: 8 nov. 2026.

UNIVERSIDADE FEDERAL DO RIO GRANDE DO SUL. Instituto de Pesquisas Hidráulicas. **IPH realiza Workshop sobre sistemas de alerta de cheias no RS em conjunto com o Serviço Geológico do Brasil (SGB)**. Porto Alegre: IPH/UFRGS, 24 set. 2026. Disponível em: https://www.ufrgs.br/iph/iph-realiza-workshop-sobre-sistemas-de-alerta-de-cheias-no-rs-em-conjunto-com-o-servico-geologico-do-brasil-sgb/. Acesso em: 8 nov. 2026.

VARGAS, M. N. Projeto Guaíba consolida primeiro ano de pesquisas sobre os impactos geológicos das enchentes de 2024. **Unisinos**, São Leopoldo, 22 jul. 2026. Disponível em: https://www.unisinos.br/noticias/projeto-guaiba-consolida-primeiro-ano-de-pesquisas-sobre-os-impactos-geologicos-das-enchentes-de-2024/. Acesso em: 8 nov. 2026.

YEVJEVICH, V. M. **Bibliography and discussion of flood-routing methods and unsteady flow in channels**. Washington, DC: U.S. Government Printing Office, 1964. (Geological Survey Water-Supply Paper, 1690). DOI: https://doi.org/10.3133/wsp1690.
