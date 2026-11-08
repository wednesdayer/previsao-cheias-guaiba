# Metodologia

Este documento descreve cada etapa do modelo e a referência em que cada uma se apoia. Também marca os pontos em que o método é uma **heurística própria do projeto**, e não uma técnica estabelecida. As chaves de referência, como [Chow 1988], apontam para [papers/README.md](../papers/README.md), que traz as citações completas, os DOIs e os PDFs quando a licença permite.

**Sumário**

1. [Contexto e objetivo](#1-contexto-e-objetivo)
2. [Vazão de entrada](#2-vazão-de-entrada)
3. [Vazão de saída sem medição de vazão](#3-vazão-de-saída-sem-medição-de-vazão)
4. [Previsão](#4-previsão)
5. [Calibração e validação](#5-calibração-e-validação)
6. [Mapa de inundação](#6-mapa-de-inundação)
7. [Versões do modelo e o que mostraram](#7-versões-do-modelo-e-o-que-mostraram)
8. [Limitações](#8-limitações)
9. [Relação com trabalhos existentes](#9-relação-com-trabalhos-existentes)

---

## 1. Contexto e objetivo

O Guaíba é um corpo d'água curto e largo, com cerca de 470 km² em nível normal. Recebe os rios Jacuí, Taquari, Caí, Sinos e Gravataí pelo delta do Jacuí e escoa para o sul, para a Lagoa dos Patos [Laipelt 2026]. Em 05/05/2024 chegou a **5,37 m**, superando o recorde de 4,76 m de 1941 [Medeiros 2025; Possa 2022; Collischonn 2025].

Três fatos definem o método:

- **O Guaíba não tem medição de vazão.** Porto Alegre só mede nível, então a saída precisa ser inferida.
- **A maior parte da água passa antes por rios monitorados.** A telemetria da ANA fornece nível e vazão a cada 15 min na última estação de cada afluente (ver [DADOS.md](DADOS.md)).
- **O Guaíba responde devagar.** A área grande faz com que a variação de nível seja a integral, ao longo de dias, do desequilíbrio entre entrada e saída.

O objetivo é prever o nível na régua da Usina do Gasômetro (ANA 87450020) nas próximas 72 h, usando só a água que já foi medida a montante. Não há previsão de chuva; a [§9](#9-relação-com-trabalhos-existentes) compara isso com os sistemas operacionais.

## 2. Vazão de entrada

### 2.1 Composição

A entrada total é a soma das vazões dos afluentes, cada uma deslocada pelo tempo de viagem até o delta:

```
Qin(t) = Σ_rios Q_r(t − L_r)
```

O `model/inflow.py` faz isso numa grade horária. As estações de entrada são Rio Pardo (Jacuí), Lajeado (Taquari), São Sebastião do Caí, São Leopoldo (Sinos) e Gravataí.

Uma estação sem dado conta como zero **só** quando outra estação cobre aquele instante. Instantes sem nenhuma estação válida ficam vazios. Essa escolha subestima a entrada quando uma estação importante fica muda, como discutido na [§8](#8-limitações).

### 2.2 Tempos de viagem (defasagens): heurística do projeto

O balanço de reservatório (§3) diz que a entrada aparece na **taxa de variação** do nível, não no nível em si. Por isso, a defasagem de cada rio é o deslocamento que maximiza a correlação de Pearson entre a vazão a montante `Q_r(t)` e o `dh/dt(t + L)` a jusante (`model/lags.py`). Usar dh/dt também elimina o datum da régua e as tendências lentas.

Essa primeira estimativa tem viés, porque dh/dt reflete o fluxo líquido `Qin − Qout`. Uma segunda passada (`calibrate/run.py`) correlaciona `Q_r` com a **entrada reconstruída** `A·dh/dt + Qout(h)` (§3.3), que não tem esse viés.

As defasagens são estimadas por evento de cheia, combinadas pela mediana e limitadas a faixas fisicamente plausíveis (`settings.LAG_BOUNDS_HOURS`).

Defasagens calibradas (v1):

| Rio / estação | Defasagem |
|---|---|
| Jacuí / Rio Pardo | 12 h |
| Taquari / Lajeado | 26 h |
| Caí | 12 h |
| Sinos | 6 h |
| Gravataí | 6 h |

Correlação cruzada para estimar defasagem é prática corrente. Aplicá-la ao dh/dt e à entrada reconstruída é a adaptação deste projeto.

### 2.3 Roteamento Muskingum (v4)

O v4 troca o deslocamento fixo pelo roteamento Muskingum [McCarthy 1938; Chow 1988, cap. 8]. Cada trecho relaciona a vazão de entrada I e a de saída O pelo armazenamento `S = K[X·I + (1 − X)·O]`, que discretizado fica:

```
O_{t+1} = C0·I_{t+1} + C1·I_t + C2·O_t
C0 = (Δt − 2KX) / D,   C1 = (Δt + 2KX) / D,   C2 = (2K(1 − X) − Δt) / D,   D = 2K(1 − X) + Δt
```

O `model/routing.py` implementa isso com `scipy.signal.lfilter`. K é o tempo de viagem e X (0–0,5) controla a atenuação. Cunge mostrou que o esquema aproxima a equação da onda difusiva, o que dá a K um significado físico (K ≈ Δx / c, com c a celeridade da onda) [Cunge 1969].

Para manter os coeficientes não negativos e evitar oscilação espúria, um trecho longo é dividido numa **cascata de n subtrechos**, com K_sub = K/n ≈ Δt. É a condição de estabilidade usual, 2KX ≤ Δt ≤ 2K(1 − X) [Chow 1988].

K e X são ajustados por trecho, maximizando a eficiência de Nash–Sutcliffe [Nash 1970] entre a vazão roteada e a observada, em pares de estações que medem vazão nas duas pontas (`calibrate/fit_routing.py`, `config/reaches.yaml`):

| Trecho de validação | NSE |
|---|---|
| Muçum → Encantado (Taquari) | 0,88 |
| Encantado → Lajeado (Taquari) | 0,81 |
| Dona Francisca → Cachoeira do Sul → Rio Pardo (Jacuí) | 0,30–0,49 |

Nos trechos da fonte até o delta usados na previsão:
- **Taquari:** K = 21,3 h, X = 0,00 (só atenuação por armazenamento).
- **Jacuí:** K = 26,8 h, X = 0,48 (quase só translação).
- **Demais rios:** K igual à defasagem e X = 0,2.

No Taquari o método reproduz bem a onda de cheia, com celeridade de cerca de 8 km/h. No Jacuí não: o trecho tem a usina hidrelétrica de Dona Francisca, que o roteamento simples de canal não representa.

## 3. Vazão de saída sem medição de vazão

### 3.1 Balanço de reservatório

O Guaíba é tratado como um único reservatório (roteamento de reservatório, ou de nível [Puls 1928; Chow 1988; Yevjevich 1964]):

```
A(h) · dh/dt = Qin(t) − Qout(h)
```

Nessa equação:
- h é o nível no Gasômetro;
- A(h) é a área da superfície da água (constante, 470 km², no v1; ver §7);
- Qout(h) é a saída para a Lagoa dos Patos.

Um reservatório único supõe a superfície da água horizontal em todo o Guaíba. Por isso ignora o empilhamento pelo vento e a declividade entre o delta e a saída; a §8 lista as consequências.

### 3.2 A saída como curva de descarga

A saída é escrita na forma de potência usual da relação nível–vazão (curva-chave) [Rantz 1982, vol. 2; WMO 2010]:

```
Qout(h) = a · (h − h0)^b
```

h0 faz o papel da cota de vazão nula. Em fluviometria, a, h0 e b são ajustados a pares (h, Q) medidos. **Aqui não há Q medido**, e essa é a diferença essencial.

### 3.3 Ajuste da curva para fechar o balanço

Rearranjando o balanço, obtém-se a saída implícita nas observações a cada hora:

```
Qout_implícita(t) = Qin(t) − A(h) · dh/dt
```

O `model/rating.py` calcula isso no registro inteiro (de abril/2024 em diante) e ajusta a, h0 e b por mínimos quadrados com **perda de Huber** [Huber 1964] (`scipy.optimize.least_squares(loss="huber")`).

A perda de Huber é quadrática para resíduos pequenos e linear para resíduos grandes. Assim, as horas dominadas por processos que o modelo não representa não dominam o ajuste: empilhamento pelo vento, remanso da Lagoa dos Patos, falhas de sensor. O parâmetro de escala é 20% da mediana da saída implícita, com mínimo de 100 m³/s.

Os parâmetros são limitados: b ∈ [0,3; 4,0] e h0 abaixo do menor nível observado.
- **No v1–v3, o expoente fica encostado no limite superior (b = 4,0)**, e o RMSE do ajuste é de cerca de 2.000 m³/s.
- Por isso a curva é **efetiva**: absorve todo processo não modelado e não deve ser lida como medição física de vazão.

Invertendo o balanço ajustado, obtém-se a **entrada reconstruída** `F(t) = A·dh/dt + Qout(h)`, usada na segunda passada das defasagens (§2.2).

### 3.4 Identificabilidade

Sem medição independente de vazão em Porto Alegre, A(h) e Qout(h) **não são identificáveis separadamente**: qualquer mudança na área suposta é compensada pela curva reajustada. A §7 mostra isso na prática.

Para quebrar esse compromisso são necessários dados independentes de saída, como as campanhas de ADCP no Guaíba. Comparada com essas medições, a curva ajustada dá cerca de **metade** da vazão real em cotas de cheia ([DISCUSSÃO §2.4](DISCUSSAO.md#24-a-curva-de-saída-dá-cerca-de-metade-da-vazão-medida)).

## 4. Previsão

O `model/forecast.py` orquestra as etapas abaixo para cada um de três cenários.

### 4.1 Extrapolação de crista: heurística do projeto

Se um afluente ainda está subindo, as próximas horas dele precisam ser estimadas antes de serem propagadas. O `model/crest.py` supõe que a taxa de subida atual r0 (medida nas últimas 6 h) **decai exponencialmente**, com constante de tempo τ:

```
Q(t) = Q0 + r0·τ·(1 − e^(−t/τ))        crista = Q0 + r0·τ
```

Depois de cerca de 4τ, o rio entra em **recessão exponencial** rumo a um nível de base (o percentil 25 da vazão recente). τ_subida e τ_recessão são ajustados por estação, com regressão log-linear nos ramos de subida e de descida de eventos passados (`calibrate/fit_crest.py`), e limitados a 6–120 h.

Os três cenários multiplicam τ_subida por:
- 0,7 (otimista);
- 1,0 (central);
- 1,4 (pessimista, que também mantém a crista por 6 h).

Essa extrapolação é a **maior fonte de volatilidade da previsão** (§7.3). É uma hipótese paramétrica simples, não um modelo hidrológico. A substituição com base física é um modelo chuva-vazão como o MGB [Collischonn 2007; Pontes 2017].

### 4.2 Integração

O balanço é integrado pelo método clássico de Runge–Kutta de quarta ordem [Butcher 2016], com passo de 15 min ao longo de 72 h (`model/balance.py`). Qin(t) é interpolada linearmente entre os valores horários. Para essa equação diferencial suave, de uma variável, o RK4 é mais do que suficiente: os erros dominantes estão em Qin e Qout, não no integrador.

### 4.3 Correção de viés: heurística do projeto

Antes de prever, o modelo roda de novo nas últimas 24 h a partir do nível observado, e a mediana de `observado − simulado` vira um termo de viés.

Esse viés é aplicado **em rampa**: zero no início da previsão e valor cheio após 12 h. Assim a previsão começa exatamente no nível observado, e a correção cresce do mesmo jeito que a deriva do modelo.

Uma versão anterior usava um offset constante, que criava um "degrau" visível em t = 0; por isso foi substituída.

### 4.4 Saídas

Para cada cenário, o modelo informa:
- o nível de pico e o horário;
- se ele supera a cota de inundação (3,00 m no Gasômetro);
- quantas horas fica acima dela.

Outras duas réguas são derivadas da previsão do Gasômetro por um offset de datum:
- **Cais Mauá:** +0,44 m, medido com telemetria simultânea em nível normal;
- **Eldorado do Sul:** offset 0, provisório.

## 5. Calibração e validação

### 5.1 Eventos

Os eventos de calibração são a janela conhecida de maio/2024 (26/04 a 08/06/2024) mais os detectados automaticamente sempre que o nível do Gasômetro fica acima de 1,8 m por pelo menos 48 h (`calibrate/events.py`). A calibração do v1 usou maio/2024, junho/2024 e junho/2025.

### 5.2 Sequência de calibração

`calibrate/run.py`:

1. Grade horária e controle de qualidade: remove picos acima de 2 m/h e valores repetidos por 12 h ou mais, e interpola lacunas de até 6 h.
2. Primeira passada das defasagens, com Q contra dh/dt.
3. Curva de saída provisória a partir da saída implícita.
4. Segunda passada das defasagens, contra a entrada reconstruída.
5. Reajuste final da curva de saída.
6. τ de crista por estação.
7. Relatório de hindcast. Os parâmetros são gravados em `config/params/params_vN_<data>.json`.

### 5.3 Hindcast

O `calibrate/hindcast.py` corta todas as séries **48 h antes** de cada pico observado e roda a previsão como se fosse ao vivo.

| Evento | Pico observado | Pico previsto (central) | Erro |
|---|---|---|---|
| Mai/2024 | 4,14 m (06/05 20h) | 3,81 m (06/05 04h) | −0,33 m / −16 h |
| Jun/2024 | 2,37 m (28/06 23h) | 2,93 m (29/06 23h) | +0,56 m / +24 h |
| Jun/2025 | 2,27 m (25/06 15h) | 2,81 m (26/06 15h) | +0,54 m / +24 h |

O modelo **superestima cheias pequenas**. Na subida de maio/2024, o erro absoluto médio das previsões às cegas sucessivas foi de 0,39 m no nível e 26 h no tempo (v1).

**Sobre a diferença entre 4,14 m e 5,37 m.**
- Os 5,37 m oficiais se referem à régua histórica do Cais Mauá (C6).
- A série do modelo é a telemetria da ANA na régua do Gasômetro, que começa em 03/05/2024 e chega a 4,17 m em 05/05.
- As duas réguas não compartilham o datum. A relação entre elas no pico de 2024 foi objeto de um estudo específico do SGB [Germano 2024], e o offset de +0,44 m que este projeto mediu em nível normal não concilia os dois picos.
- Todos os números deste repositório estão no datum da telemetria do Gasômetro e não devem ser comparados diretamente com os 5,37 m oficiais.

## 6. Mapa de inundação

### 6.1 Curva cota-área

O `scripts/build_area_curve.py` deriva A(h) do DEM Copernicus GLO-30 (ver [DADOS.md](DADOS.md#2-dem-copernicus-glo-30)):

1. Recorta o Guaíba e o delta do Jacuí, parando ao norte da Lagoa dos Patos.
2. Monta a curva hipsométrica (a área abaixo de cada cota).
3. **Ancora** a curva no datum da régua: a cota em que a área acumulada chega a 470 km² é tomada como 0,9 m na régua.

O resultado vai de 470 km² em 0 m a 961 km² em 6 m (`config/stage_area.yaml`).

### 6.2 Banheira com conectividade

O mapa (`scripts/build_inundation.py`, `model/inundation.py`) usa um **modelo de banheira com conectividade hidrológica** [Poulter 2008; Williams 2020]. Para um nível h na régua, uma célula do DEM fica alagada se a cota dela estiver abaixo da superfície ancorada **e** se ela estiver conectada ao corpo d'água (`scipy.ndimage.label`). Sem o teste de conectividade, depressões isoladas longe do rio apareceriam como alagadas.

O script pré-calcula um raster de "nível de chegada", e o controle deslizante do dashboard só aplica um limiar sobre ele, direto no navegador.

### 6.3 Ressalvas

- **O DEM é um modelo de superfície.** O GLO-30 inclui prédios e copa das árvores [Copernicus DEM]. Os prédios funcionam como paredes, então a inundação urbana é subestimada. O FABDEM remove prédios e florestas do mesmo DEM e é a melhoria natural [Hawker 2022].
- **A superfície da água é plana.** A banheira ignora a declividade do rio e do delta e qualquer dinâmica. Conferido com um ponto conhecido em Eldorado do Sul na cheia de junho/2025, o mapa errou ali cerca de 1,5 m de cota.
- **A ancoragem do datum é aproximada** (§6.1).

O mapa é ilustrativo, e o dashboard avisa isso.

## 7. Versões do modelo e o que mostraram

Todas as versões compartilham o balanço, o ajuste da curva de saída, a extrapolação de crista e a correção de viés. Elas diferem na área de armazenamento e na forma de propagar a entrada. Os parâmetros ficam em `config/params/` (operacional) e `config/params/experimental/`.

| Modelo | A(h) | Entrada | Curva de saída (a, h0, b) | Situação |
|---|---|---|---|---|
| v1 | constante, 470 km² | defasagens fixas | 3,03; −4,48; 4,00 | operacional |
| v2 | estimada à mão, 470 → 1650 km² | defasagens fixas | 3,21; −4,46; 4,00 | experimental |
| v3 | curva do DEM, 470 → 961 km² | defasagens fixas | 3,03; −4,51; 4,00 | experimental |
| v4 | curva do DEM | Muskingum a partir das estações de montante | 86,3; −4,58; 1,98 | experimental |

### 7.1 A área não muda o pico

Maio/2024, erro absoluto médio ao longo da subida:

| Modelo | Nível | Tempo |
|---|---|---|
| v1 | **0,39 m** | 26 h |
| v3 | 0,59 m | **20 h** |
| v4 | 0,86 m | 39 h |

No pico, dh/dt = 0: A(h) sai do balanço, e o nível de pico fica definido por Qin = Qout(h). Como a curva de saída é reajustada para cada hipótese de área (§3.4), uma A(h) mais realista muda a forma e o tempo do hidrograma, mas **não a magnitude do pico**. O v3 tem tempo melhor e uma cheia mais achatada e longa, mas um nível de pico pior que o v1.

### 7.2 O roteamento funciona por trecho, não no conjunto

Os trechos Muskingum do v4 validam bem no Taquari (NSE 0,81–0,88), mas a previsão integrada é a pior das quatro. Por quê:
- Rotear só a estação **de montante** perde a contribuição lateral entre ela e a foz, então a entrada total fica subestimada.
- O ajuste da curva de saída compensa (o expoente cai de 4 para cerca de 2) e depois superestima o pico.
- No Jacuí, a barragem quebra o roteamento por completo.

O uso previsto do roteamento é cirúrgico: preencher o Jacuí a partir de Cachoeira do Sul quando Rio Pardo fica mudo, escalando pela área de drenagem.

### 7.3 Volatilidade da previsão numa cheia real

Previsões refeitas com os dados cortados em cada momento da cheia do Taquari de julho/2026:

| Rodada em | Nível observado | Q em Lajeado (m³/s) | Pico v1 | Pico v3 |
|---|---|---|---|---|
| 22/07 12h | 0,95 m | 9.067 | 4,56 m | 4,39 m |
| 22/07 18h | 1,07 m | 10.485 | 4,42 m | 4,25 m |
| 23/07 00h | 1,34 m | 11.070 | 4,21 m | 4,03 m |
| 23/07 12h | 1,37 m | 9.153 | 3,53 m | 3,15 m |
| 24/07 00h | 1,44 m | 5.631 | 2,74 m | 2,29 m |

**O pico observado no Gasômetro foi 1,53 m** (24/07, por volta das 20h). As previsões feitas com 2–3 dias de antecedência ficaram, portanto, 2–3 m acima. O [DISCUSSAO.md](DISCUSSAO.md#1-julho-de-2026-um-teste-em-tempo-real) compara as quatro versões com as previsões oficiais do SGB/IPH nas duas ondas do evento.

Enquanto o Taquari subia, a extrapolação de crista (§4.1) projetava a subida para a frente. Quando a crista real passou por Lajeado (11.078 m³/s em 23/07 01h), o pico previsto caiu junto. Na prática:

- **Confiável:** a entrada nas próximas ~24 h, que é água já dentro dos rios, na janela do tempo de viagem, e a tendência.
- **Não confiável enquanto os rios a montante ainda sobem:** o valor absoluto do pico, que erra para cima. Isso faz do modelo um alerta conservador, mas um número ruim.

## 8. Limitações

1. **Sem previsão de chuva.** Só a água já observada é propagada; o horizonte útil é de 48–72 h.
2. **Vento e Lagoa dos Patos não são modelados.** O vento sudoeste represa a saída e pode elevar o Guaíba em até cerca de 50 cm; o nordeste faz o contrário [Laipelt 2026; Possa 2022; Munar 2018]. Neste modelo, esses efeitos acabam nos resíduos da curva de saída e no termo de viés.
3. **Lacunas nas estações de entrada.** Rio Pardo (Jacuí) tem 41% de cobertura de vazão e Lajeado (Taquari), 7%. O Jacuí drena cerca de 85% da bacia e o Taquari define os picos [Laipelt 2026], então essas lacunas são a principal fonte de erro na entrada (ver [DADOS.md](DADOS.md#peculiaridades-dos-dados-que-moldam-o-modelo)).
4. **As vazões vêm de curvas-chave.** As vazões da ANA são extrapoladas em cheias extremas (±10–20%).
5. **A curva de saída é efetiva, não física,** e dá cerca de metade da vazão medida por ADCP em cotas de cheia (§3.3, §3.4).
6. **O mapa de inundação é uma banheira estática sobre um modelo de superfície** (§6.3).

Uma discussão completa das falhas, com a comparação com as previsões oficiais e com os problemas relatados pelo IPH/UFRGS, está em [DISCUSSAO.md](DISCUSSAO.md).

## 9. Relação com trabalhos existentes

Na cheia de maio/2024, a equipe do IPH/UFRGS fez previsões operacionais diárias do Guaíba.
- **Como:** combinou o modelo hidrológico MGB, calibrado para a região, com previsões de chuva do ECMWF/GEFS e cenários de vento.
- **Resultado:** o sistema antecipou níveis acima de 5 m com três dias de antecedência e um segundo pico com oito dias [Medeiros 2025].

Depois, Laipelt et al. [2026] construíram um modelo hidrodinâmico detalhado do evento, validado com dados do satélite SWOT, e mostraram que o Taquari definiu o pico em Porto Alegre e o Jacuí, a duração.

Este projeto é deliberadamente muito mais simples: um único reservatório alimentado pela vazão observada nos afluentes, com uma curva de saída inferida dos dados em vez da hidráulica. O valor dele é rodar só com telemetria pública, em segundos, e ser transparente em cada hipótese.

Os próximos passos óbvios aproximam o modelo daqueles sistemas operacionais:

- chuva-vazão a montante (tipo MGB, com previsões do Open-Meteo);
- forçante de vento na saída;
- FABDEM [Hawker 2022] no mapa;
- roteamento cirúrgico para as lacunas do Jacuí.
