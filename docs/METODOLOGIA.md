# Metodologia

Este documento descreve o modelo etapa por etapa e indica, para cada uma, a referência em que se apoia. Onde o procedimento não segue uma técnica consolidada na literatura e resulta de uma escolha deste projeto, o texto o identifica explicitamente como **heurística do projeto**, para que o leitor possa separar o que herda validação prévia do que ainda depende de avaliação. As citações seguem o sistema autor-data da ABNT NBR 10520:2023, e as referências completas, no formato da NBR 6023:2018, estão na [seção 10](#10-referências); o diretório [papers/](../papers/README.md) guarda os PDFs cuja licença permite redistribuição.

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
10. [Referências](#10-referências)

---

## 1. Contexto e objetivo

O Guaíba é um corpo d'água curto e largo, com cerca de 50 km de extensão e 470 km² de superfície em nível normal (Possa et al., 2022, p. 4), que recebe os rios Jacuí, Taquari, Caí, Sinos e Gravataí através do delta do Jacuí e escoa para o sul, em direção à Lagoa dos Patos (Laipelt et al., 2026, p. 3). Em 5 de maio de 2024 a régua do Cais Mauá registrou 5,37 m, nível que superou a marca de 4,76 m deixada pela cheia de 1941, até então a referência histórica da cidade (Medeiros; Fan; Paiva, 2025, p. 1); Possa et al. (2022, p. 5) e Collischonn et al. (2025, p. 5) registram 4,75 m para o pico de 1941, diferença de um centímetro que não altera a comparação.

A formulação do modelo decorre de três características do sistema. A primeira é a ausência de medição contínua de vazão no próprio Guaíba: Porto Alegre dispõe apenas de réguas de nível, de modo que a vazão que deixa o lago em direção à Lagoa dos Patos precisa ser inferida. A segunda é que a maior parte da água que chega ao Guaíba atravessa antes estações monitoradas, já que a rede telemétrica da ANA informa nível e vazão a cada 15 minutos na última estação de cada afluente (ver [DADOS.md](DADOS.md)). A terceira diz respeito à escala temporal da resposta: a grande área do espelho d'água faz com que a variação de nível corresponda à integral, ao longo de dias, do desequilíbrio entre o que entra e o que sai, e não a uma resposta imediata a cada pulso de vazão.

O objetivo, portanto, é estimar o nível na régua da Usina do Gasômetro (estação ANA 87450020) ao longo das 72 horas seguintes, com base exclusivamente na água que já foi medida a montante. Chuva e vento ficaram de fora por decisão de partida: a proposta era verificar até onde a água já presente nos rios, acompanhada pela telemetria, basta para prever o nível, antes de acrescentar qualquer forçante meteorológica. A seção 9 compara essa escolha com a dos sistemas operacionais que incorporam previsão de chuva, e a [DISCUSSÃO, §2](DISCUSSAO.md#2-a-escolha-de-partir-apenas-da-água-medida-nos-rios) avalia o que ela custou e revelou na cheia de julho de 2026.

## 2. Vazão de entrada

### 2.1 Composição

A vazão total que chega ao Guaíba é tratada como a soma das vazões dos afluentes, cada uma deslocada no tempo pelo respectivo tempo de viagem até o delta:

```
Qin(t) = Σ_rios Q_r(t − L_r)
```

O módulo `model/inflow.py` realiza essa soma numa grade horária, a partir das estações de Rio Pardo (Jacuí), Lajeado (Taquari), São Sebastião do Caí, São Leopoldo (Sinos) e Gravataí. Quando uma dessas estações não tem dado num instante em que outras têm, o modelo atribui zero à estação ausente; quando nenhuma tem dado, o instante permanece vazio. A regra evita interromper a série a cada falha pontual, mas cobra um preço conhecido, pois subestima a entrada sempre que uma estação de grande contribuição deixa de transmitir, problema que a seção 8 e a [DISCUSSÃO](DISCUSSAO.md) retomam com números.

### 2.2 Tempos de viagem (defasagens): heurística do projeto

Segundo o balanço de reservatório apresentado na seção 3, a contribuição de um afluente não se manifesta no nível do Guaíba propriamente dito, mas na sua taxa de variação. Por esse motivo, a defasagem de cada rio é estimada como o deslocamento que maximiza a correlação de Pearson entre a vazão a montante, `Q_r(t)`, e a derivada temporal do nível a jusante, `dh/dt(t + L)` (módulo `model/lags.py`). Trabalhar com a derivada tem uma vantagem adicional: elimina tanto o datum da régua quanto as tendências lentas da série, que contaminariam uma correlação feita diretamente sobre o nível.

Essa primeira estimativa, contudo, carrega um viés, porque dh/dt representa o fluxo líquido `Qin − Qout` e não apenas a entrada. Uma segunda passada, conduzida em `calibrate/run.py`, corrige o problema ao correlacionar `Q_r` com a **entrada reconstruída**, `A·dh/dt + Qout(h)`, definida na seção 3.3. As defasagens resultam de estimativas feitas evento a evento, combinadas pela mediana e limitadas a faixas fisicamente plausíveis para cada rio (`settings.LAG_BOUNDS_HOURS`). Para a versão operacional v1, os valores calibrados foram os seguintes:

| Rio / estação | Defasagem |
|---|---|
| Jacuí / Rio Pardo | 12 h |
| Taquari / Lajeado | 26 h |
| Caí | 12 h |
| Sinos | 6 h |
| Gravataí | 6 h |

O uso de correlação cruzada para estimar tempos de propagação é prática corrente em hidrologia. A contribuição deste trabalho está na aplicação do método à derivada do nível e, numa segunda etapa, à entrada reconstruída, escolha que não encontramos descrita na literatura consultada e que, por isso, tratamos como heurística.

### 2.3 Roteamento Muskingum (v4)

A versão v4 substitui o deslocamento rígido por um roteamento de onda de cheia pelo método Muskingum (McCarthy, 1938 apud Yevjevich, 1964; Chow; Maidment; Mays, 1988, cap. 8). Em cada trecho, o método relaciona a vazão de entrada I e a de saída O por meio de um armazenamento linear, `S = K[X·I + (1 − X)·O]`, que, discretizado, conduz à recorrência

```
O_{t+1} = C0·I_{t+1} + C1·I_t + C2·O_t
C0 = (Δt − 2KX) / D,   C1 = (Δt + 2KX) / D,   C2 = (2K(1 − X) − Δt) / D,   D = 2K(1 − X) + Δt
```

implementada em `model/routing.py` com `scipy.signal.lfilter`. O parâmetro K corresponde ao tempo de viagem e X, restrito ao intervalo de 0 a 0,5, governa a atenuação. Cunge (1969) demonstrou que esse esquema aproxima a equação da onda difusiva, o que confere a K uma interpretação física (K ≈ Δx / c, sendo c a celeridade da onda). Para que os coeficientes permaneçam não negativos e não surjam oscilações espúrias, os trechos longos são divididos numa cascata de n subtrechos com K_sub = K/n ≈ Δt, procedimento que respeita a condição usual de estabilidade, 2KX ≤ Δt ≤ 2K(1 − X) (Chow; Maidment; Mays, 1988).

Os parâmetros de cada trecho foram ajustados de modo a maximizar a eficiência de Nash–Sutcliffe (Nash; Sutcliffe, 1970) entre a vazão roteada e a observada, em pares de estações que medem vazão nas duas extremidades (`calibrate/fit_routing.py`, `config/reaches.yaml`):

| Trecho de validação | NSE |
|---|---|
| Muçum → Encantado (Taquari) | 0,88 |
| Encantado → Lajeado (Taquari) | 0,81 |
| Dona Francisca → Cachoeira do Sul → Rio Pardo (Jacuí) | 0,30–0,49 |

Nos trechos que vão da estação-fonte até o delta, o ajuste produziu comportamentos opostos nos dois afluentes principais. No Taquari, com K = 21,3 h e X = 0,00, o trecho se comporta como um reservatório linear puro, que só atenua; no Jacuí, com K = 26,8 h e X = 0,48, ocorre quase só translação, sem amortecimento apreciável. Os demais rios receberam K igual à defasagem da versão v1 e X = 0,2. O método reproduz bem a onda do Taquari, com celeridade da ordem de 8 km/h, mas falha no Jacuí, cujo trecho inclui a usina hidrelétrica de Dona Francisca, cuja operação um roteamento de canal simples não tem como representar.

## 3. Vazão de saída sem medição de vazão

### 3.1 Balanço de reservatório

O modelo trata o Guaíba como um único reservatório, na tradição do roteamento de reservatório, ou roteamento de nível, que remonta a Puls (1928 apud Yevjevich, 1964) e que Chow, Maidment e Mays (1988) e Yevjevich (1964) sistematizam:

```
A(h) · dh/dt = Qin(t) − Qout(h)
```

Nessa equação, h é o nível na régua do Gasômetro, A(h) é a área do espelho d'água, constante e igual a 470 km² na versão v1 (seção 7), e Qout(h) é a vazão que deixa o lago em direção à Lagoa dos Patos. Ao reduzir o Guaíba a um reservatório único, o modelo supõe que a superfície da água permanece horizontal em toda a sua extensão, o que exclui por construção tanto o empilhamento causado pelo vento quanto a declividade entre o delta e a saída. A seção 8 e a [DISCUSSÃO, §3.3](DISCUSSAO.md#33-a-premissa-de-banheira-superfície-plana) mostram que essa hipótese é mais frágil do que parecia quando o modelo foi formulado.

### 3.2 A saída como curva de descarga

A vazão de saída assume a forma de potência usual das curvas-chave fluviométricas (Rantz et al., 1982, p. 290-291; World Meteorological Organization, 2010):

```
Qout(h) = a · (h − h0)^b
```

em que h0 desempenha o papel de cota de vazão nula. Na prática fluviométrica, os parâmetros a, h0 e b são ajustados a pares (h, Q) obtidos em campanhas de medição. No Guaíba não há esses pares, e é justamente essa ausência que separa o problema tratado aqui de uma calibração convencional de curva-chave.

### 3.3 Ajuste da curva para fechar o balanço

Rearranjando o balanço, obtém-se, para cada hora do registro, a vazão de saída que as observações implicam:

```
Qout_implícita(t) = Qin(t) − A(h) · dh/dt
```

O módulo `model/rating.py` calcula essa série sobre todo o período disponível, de abril de 2024 em diante, e ajusta a, h0 e b por mínimos quadrados com perda de Huber (Huber, 1964), por meio de `scipy.optimize.least_squares(loss="huber")`. A perda de Huber cresce de forma quadrática para resíduos pequenos e de forma linear para os grandes; com isso, as horas dominadas por processos ausentes do modelo, como o empilhamento pelo vento, o remanso da Lagoa dos Patos ou falhas de sensor, perdem peso no ajuste sem que seja preciso identificá-las e descartá-las manualmente. O parâmetro de escala da perda foi fixado em 20% da mediana da saída implícita, com piso de 100 m³/s.

Os parâmetros foram restritos a b ∈ [0,3; 4,0] e a h0 abaixo do menor nível observado. Nas versões v1 a v3, o expoente convergiu para o limite superior, b = 4,0, e o erro quadrático médio do ajuste ficou em torno de 2.000 m³/s. O valor destoa da prática fluviométrica: para controles de canal em rios naturais, Rantz et al. (1982, p. 330) indicam expoentes que variam em geral entre 1,3 e 1,8 e praticamente nunca chegam a 2,0. Um parâmetro encostado no limite costuma indicar que o ajuste tenta compensar algo que a forma funcional não representa, e é assim que a curva deve ser lida: como uma relação efetiva, que absorve todos os processos não modelados, e não como estimativa física da vazão que de fato escoa pelo Guaíba.

A inversão do balanço já ajustado fornece a **entrada reconstruída**, `F(t) = A·dh/dt + Qout(h)`, empregada na segunda passada da estimativa de defasagens descrita na seção 2.2.

### 3.4 Identificabilidade

Na falta de uma medição independente de vazão em Porto Alegre, A(h) e Qout(h) não são identificáveis separadamente: qualquer alteração na área suposta se reflete num reajuste compensatório da curva de saída, de modo que diferentes pares de hipóteses produzem o mesmo ajuste aos dados. A seção 7 mostra esse comportamento empiricamente, e só dados independentes de vazão, como as campanhas de ADCP realizadas no Guaíba, permitem desfazer a ambiguidade. Quando confrontada com essas medições, a curva ajustada fornece aproximadamente a metade da vazão efetivamente medida em cotas de cheia, resultado discutido em detalhe na [DISCUSSÃO, §3.4](DISCUSSAO.md#34-a-curva-de-saída-dá-cerca-de-metade-da-vazão-medida).

## 4. Previsão

O módulo `model/forecast.py` encadeia as etapas descritas a seguir, repetindo-as para cada um de três cenários.

### 4.1 Extrapolação de crista: heurística do projeto

Para propagar um afluente que ainda está subindo, o modelo precisa antes estimar como essa subida vai evoluir nas horas seguintes. O módulo `model/crest.py` supõe que a taxa de subida observada nas últimas seis horas, r0, decai exponencialmente com constante de tempo τ, o que leva a

```
Q(t) = Q0 + r0·τ·(1 − e^(−t/τ))        crista = Q0 + r0·τ
```

Passado um intervalo da ordem de 4τ, o rio entra em recessão exponencial em direção a um nível de base, definido como o percentil 25 da vazão recente. As constantes τ_subida e τ_recessão são ajustadas para cada estação, por regressão log-linear sobre os ramos ascendente e descendente de eventos anteriores (`calibrate/fit_crest.py`), e limitadas ao intervalo de 6 a 120 horas.

Os três cenários diferem apenas no fator aplicado a τ_subida: 0,7 no otimista, 1,0 no central e 1,4 no pessimista, que, além disso, sustenta a crista por seis horas antes da recessão. Trata-se de uma hipótese paramétrica simples, desprovida de qualquer informação sobre a chuva que alimenta a subida, e ela responde pela maior parte da volatilidade das previsões, conforme a seção 7.3 documenta. A alternativa fisicamente fundamentada seria um modelo chuva-vazão como o MGB (Collischonn et al., 2007; Pontes et al., 2017).

### 4.2 Integração

O balanço é integrado pelo método clássico de Runge–Kutta de quarta ordem (Butcher, 2016), com passo de 15 minutos ao longo de 72 horas (`model/balance.py`), interpolando-se Qin(t) linearmente entre os valores horários. Para uma equação diferencial ordinária suave e de uma única variável, o RK4 oferece precisão muito superior à necessária; os erros que efetivamente limitam a previsão estão em Qin e em Qout, não no integrador.

### 4.3 Correção de viés: heurística do projeto

Antes de cada previsão, o modelo é executado novamente sobre as 24 horas anteriores, partindo do nível observado no início dessa janela, e a mediana das diferenças entre observado e simulado passa a constituir um termo de viés. Esse termo entra na previsão em forma de rampa, nulo no instante inicial e com valor pleno após 12 horas, o que garante que a curva prevista parta exatamente do último nível observado e que a correção cresça à medida que a deriva do modelo se acumula. Uma versão anterior aplicava o viés como deslocamento constante, solução que produzia um degrau visível em t = 0 e que, por essa razão, foi abandonada.

### 4.4 Saídas

Para cada cenário, o modelo informa o nível máximo previsto e o horário em que ocorre, indica se esse máximo ultrapassa a cota de inundação de 3,00 m na régua do Gasômetro e calcula por quantas horas o nível permanece acima dela. Duas réguas adicionais derivam da previsão do Gasômetro por meio de um deslocamento de datum: a do Cais Mauá, com +0,44 m, valor obtido a partir de leituras simultâneas em nível normal, e a de Eldorado do Sul, com deslocamento nulo, ainda provisório por falta de referência local.

## 5. Calibração e validação

### 5.1 Eventos

A calibração considera a janela conhecida da cheia de maio de 2024, de 26 de abril a 8 de junho, e acrescenta os eventos que o algoritmo de `calibrate/events.py` detecta automaticamente, definidos como períodos em que o nível do Gasômetro permanece acima de 1,8 m por pelo menos 48 horas. A versão v1 foi calibrada com três eventos: maio de 2024, junho de 2024 e junho de 2025.

### 5.2 Sequência de calibração

O procedimento implementado em `calibrate/run.py` parte das séries brutas, que passam por reamostragem para grade horária e por um controle de qualidade que remove variações de nível superiores a 2 m/h, descarta valores idênticos mantidos por 12 horas ou mais (indício de sensor travado) e interpola lacunas de até seis horas. Sobre essas séries, o algoritmo estima as defasagens numa primeira passada, correlacionando vazão e dh/dt, e ajusta uma curva de saída provisória a partir da saída implícita. Com essa curva, reconstrói a entrada e reestima as defasagens numa segunda passada, livre do viés da primeira, após o que reajusta a curva de saída em definitivo. Restam então o ajuste das constantes de crista de cada estação e a geração do relatório de hindcast; os parâmetros finais são gravados em `config/params/params_vN_<data>.json`.

### 5.3 Hindcast

A validação, implementada em `calibrate/hindcast.py`, corta todas as séries 48 horas antes de cada pico observado e executa a previsão como se o modelo estivesse operando naquele momento, sem acesso a nenhum dado posterior.

| Evento | Pico observado | Pico previsto (central) | Erro |
|---|---|---|---|
| Mai/2024 | 4,14 m (06/05 20h) | 3,81 m (06/05 04h) | −0,33 m / −16 h |
| Jun/2024 | 2,37 m (28/06 23h) | 2,93 m (29/06 23h) | +0,56 m / +24 h |
| Jun/2025 | 2,27 m (25/06 15h) | 2,81 m (26/06 15h) | +0,54 m / +24 h |

O padrão é assimétrico: o modelo subestima ligeiramente o maior evento e superestima os dois menores em mais de meio metro. Ao longo de toda a subida de maio de 2024, o erro absoluto médio das previsões às cegas sucessivas foi de 0,39 m no nível e de 26 horas no horário do pico (v1).

Cabe esclarecer a diferença entre os 4,14 m da tabela e os 5,37 m que a imprensa e a literatura registram para a mesma cheia. O valor oficial refere-se à régua histórica do Cais Mauá (C6), danificada pela cheia na noite de 2 de maio de 2024; a régua do Gasômetro foi instalada em caráter emergencial 2,5 km a jusante e começou a medir na tarde de 3 de maio (Collischonn et al., 2025, p. 16). A série usada pelo modelo é a telemetria da ANA nessa régua, cujo máximo, em 5 de maio, foi 4,17 m. As duas réguas têm referências de nível independentes (Collischonn et al., 2025, p. 16), e a relação entre elas no pico de 2024 motivou um estudo específico do SGB (Germano et al., 2024). O deslocamento de +0,44 m medido por este projeto em nível normal não basta para conciliar os dois picos, razão pela qual todos os números deste repositório estão expressos no datum da telemetria do Gasômetro e não devem ser comparados diretamente com os 5,37 m oficiais.

## 6. Mapa de inundação

### 6.1 Curva cota-área

O script `scripts/build_area_curve.py` deriva a função A(h) do modelo digital de elevação Copernicus GLO-30 (ver [DADOS.md](DADOS.md#2-dem-copernicus-glo-30)). O recorte abrange o Guaíba e o delta do Jacuí e se interrompe ao norte da Lagoa dos Patos, cuja área, se incluída, distorceria a resposta do sistema. Sobre esse recorte, o script constrói a curva hipsométrica, isto é, a área situada abaixo de cada cota, e a ancora no datum da régua admitindo que a cota em que a área acumulada atinge 470 km² corresponde a 0,9 m no Gasômetro, nível típico de águas normais. O resultado varia de 470 km² em 0 m a 961 km² em 6 m (`config/stage_area.yaml`).

### 6.2 Banheira com conectividade

O mapa (`scripts/build_inundation.py`, `model/inundation.py`) emprega um modelo de banheira com conectividade hidrológica (Poulter; Halpin, 2008; Williams; Lück-Vogel, 2020). Para um dado nível na régua, uma célula do DEM é classificada como alagada quando sua cota está abaixo da superfície d'água ancorada e quando, simultaneamente, se conecta ao corpo d'água principal (`scipy.ndimage.label`). Sem o teste de conectividade, depressões isoladas e distantes do rio apareceriam como inundadas, erro comum nas implementações mais simples do método. O script pré-calcula um raster com o nível a partir do qual cada célula alaga, e o controle deslizante do dashboard apenas aplica um limiar sobre esse raster, diretamente no navegador.

### 6.3 Ressalvas

O GLO-30 é um modelo de superfície e não de terreno, o que significa que inclui edificações e copas de árvores (Airbus Defence and Space, 2022). Nas áreas urbanas, os prédios funcionam como barreiras artificiais ao avanço da água, e o mapa tende, por isso, a subestimar a inundação; o FABDEM, que remove edificações e florestas a partir do mesmo DEM, seria a substituição natural (Hawker et al., 2022). A segunda limitação decorre da própria premissa de banheira, que impõe uma superfície d'água plana e ignora tanto a declividade do rio e do delta quanto qualquer dinâmica de escoamento. Numa conferência com um ponto conhecido em Eldorado do Sul, durante a cheia de junho de 2025, o mapa errou ali cerca de 1,5 m de cota. A ancoragem do datum, descrita na seção 6.1, é ela própria aproximada. Pelo conjunto dessas razões, o mapa deve ser lido como ilustrativo, e o dashboard informa isso ao usuário.

## 7. Versões do modelo e o que mostraram

As quatro versões compartilham o balanço, o ajuste da curva de saída, a extrapolação de crista e a correção de viés, e diferem apenas na área de armazenamento e no modo de propagar a entrada. Os parâmetros da versão operacional ficam em `config/params/`, e os das experimentais, em `config/params/experimental/`.

| Modelo | A(h) | Entrada | Curva de saída (a, h0, b) | Situação |
|---|---|---|---|---|
| v1 | constante, 470 km² | defasagens fixas | 3,03; −4,48; 4,00 | operacional |
| v2 | estimada à mão, 470 → 1650 km² | defasagens fixas | 3,21; −4,46; 4,00 | experimental |
| v3 | curva do DEM, 470 → 961 km² | defasagens fixas | 3,03; −4,51; 4,00 | experimental |
| v4 | curva do DEM | Muskingum a partir das estações de montante | 86,3; −4,58; 1,98 | experimental |

### 7.1 A área não muda o pico

Para a subida de maio de 2024, o erro absoluto médio de cada versão foi o seguinte:

| Modelo | Nível | Tempo |
|---|---|---|
| v1 | **0,39 m** | 26 h |
| v3 | 0,59 m | **20 h** |
| v4 | 0,86 m | 39 h |

A expectativa inicial era que uma curva cota-área mais realista melhorasse a previsão do pico, e não foi o que aconteceu. A explicação é matemática: no instante do pico, dh/dt = 0, e a área desaparece do balanço, de modo que o nível máximo fica determinado apenas pela igualdade Qin = Qout(h). Como a curva de saída é reajustada para cada hipótese de área (seção 3.4), uma A(h) mais fiel à topografia altera a forma e o tempo do hidrograma sem alterar a magnitude do pico. O v3 de fato produz uma cheia mais achatada e longa, com horário de pico mais próximo do observado, mas erra o nível máximo mais do que o v1.

### 7.2 O roteamento funciona por trecho, não no conjunto

O resultado do v4 é, à primeira vista, paradoxal. Os trechos de roteamento validam bem no Taquari, com NSE entre 0,81 e 0,88, e ainda assim a previsão integrada é a pior das quatro versões. A razão está na escolha das estações-fonte: ao rotear apenas a estação de montante, o modelo perde a contribuição lateral que o rio recebe entre essa estação e a foz, subestima a entrada total e induz o ajuste da curva de saída a compensar o déficit, com o expoente caindo de 4 para cerca de 2; essa curva distorcida, por sua vez, superestima o pico. No Jacuí, a presença da barragem inviabiliza o roteamento por completo. O uso que se vislumbra para o método é, assim, pontual: preencher a série do Jacuí a partir de Cachoeira do Sul nos períodos em que Rio Pardo deixa de transmitir, escalando a vazão pela razão entre as áreas de drenagem.

### 7.3 Volatilidade da previsão numa cheia real

A cheia do Taquari de julho de 2026 permitiu observar o modelo em operação. A tabela abaixo reúne previsões refeitas com os dados cortados em diferentes momentos do evento:

| Rodada em | Nível observado | Q em Lajeado (m³/s) | Pico v1 | Pico v3 |
|---|---|---|---|---|
| 22/07 12h | 0,95 m | 9.067 | 4,56 m | 4,39 m |
| 22/07 18h | 1,07 m | 10.485 | 4,42 m | 4,25 m |
| 23/07 00h | 1,34 m | 11.070 | 4,21 m | 4,03 m |
| 23/07 12h | 1,37 m | 9.153 | 3,53 m | 3,15 m |
| 24/07 00h | 1,44 m | 5.631 | 2,74 m | 2,29 m |

O pico observado no Gasômetro foi de 1,53 m, por volta das 20h de 24 de julho. As previsões emitidas com dois a três dias de antecedência erraram, portanto, por dois a três metros para cima. Enquanto o Taquari subia, a extrapolação de crista (seção 4.1) projetava a subida adiante; quando a crista real passou por Lajeado, com 11.078 m³/s à 01h de 23 de julho, o pico previsto recuou junto. Desse comportamento se extrai uma regra de leitura: a entrada prevista para as 24 horas seguintes, que corresponde a água já presente nos rios dentro da janela de tempo de viagem, merece confiança, assim como a tendência de subida ou descida; o valor absoluto do pico, enquanto os rios a montante ainda sobem, não merece, pois erra sistematicamente para cima. O modelo funciona, nessas condições, como alerta conservador, mas não como estimativa numérica. A [DISCUSSÃO](DISCUSSAO.md#1-julho-de-2026-um-teste-em-tempo-real) estende essa análise às quatro versões e às duas ondas do evento e a confronta com as previsões oficiais do SGB e do IPH.

## 8. Limitações

A limitação mais evidente é a ausência de previsão de chuva. Como o modelo propaga apenas a água já observada nos rios, o horizonte em que suas previsões têm algum valor se restringe a 48 ou 72 horas, e qualquer chuva que caia depois do instante da previsão fica fora do cálculo.

O vento e a Lagoa dos Patos tampouco estão representados. Vento de sudoeste dificulta o escoamento do Guaíba e pode elevar seu nível em até cerca de 50 cm, enquanto vento de nordeste produz o efeito oposto (Laipelt et al., 2026, p. 3); a circulação da Lagoa dos Patos, que recebe essas águas, é ela própria forçada pelo vento (Munar et al., 2018), e na cheia de 1941 a contribuição do vento ao pico em Porto Alegre foi estimada entre alguns centímetros e algumas dezenas de centímetros (Possa et al., 2022, p. 1); no modelo, esses efeitos acabam diluídos nos resíduos da curva de saída e no termo de correção de viés, que só os percebe com atraso.

A qualidade da entrada depende de estações com cobertura muito irregular. A estação de Rio Pardo, no Jacuí, tem dados de vazão em 41% das horas do registro, e a de Lajeado, no Taquari, em apenas 7%. Como Rio Pardo tem a maior área de drenagem entre as estações de entrada, 38.700 km² dos 82.500 km² que a estação do Gasômetro drena (Agência Nacional de Águas e Saneamento Básico, 2026), e o Taquari define os picos (Laipelt et al., 2026, p. 1), essas lacunas constituem a principal fonte de erro na entrada (ver [DADOS.md](DADOS.md#peculiaridades-dos-dados-que-moldam-o-modelo)). Mesmo quando presentes, as vazões da ANA derivam de curvas-chave e, nas cheias extremas, dependem de extrapolação; em Estrela/Lajeado, a estação que o modelo usa para o Taquari, Collischonn et al. (2025, p. 14) classificam como alta a incerteza do pico estimado em 2024.

A curva de saída, como já discutido nas seções 3.3 e 3.4, é efetiva e não física, e as medições de ADCP indicam que ela fornece cerca de metade da vazão real em cotas de cheia. O mapa de inundação, por fim, herda as restrições de um modelo de banheira estático aplicado a um modelo de superfície (seção 6.3). A [DISCUSSÃO](DISCUSSAO.md) examina cada um desses pontos à luz da cheia de julho de 2026 e dos problemas que o próprio IPH/UFRGS relatou.

## 9. Relação com trabalhos existentes

Durante a cheia de maio de 2024, a equipe do IPH/UFRGS produziu previsões operacionais diárias para o Guaíba, combinando o modelo hidrológico MGB, calibrado para a região, com previsões de chuva dos modelos ECMWF e GEFS e com cenários de vento. Esse sistema antecipou níveis acima de 5 m com três dias de antecedência e identificou um segundo pico com oito dias (Medeiros; Fan; Paiva, 2025, p. 1, 8). Laipelt et al. (2026, p. 1) construíram depois um modelo hidrodinâmico bidimensional do evento, validado também com altimetria do satélite SWOT, e concluíram que o Taquari determinou o pico em Porto Alegre, ao passo que o Jacuí respondeu pela maior parte da duração da cheia.

O presente trabalho adota deliberadamente uma formulação muito mais simples: um único reservatório, alimentado pela vazão observada nos afluentes e drenado por uma curva de saída inferida dos dados, sem representação hidráulica do escoamento. Essa simplicidade tem um custo evidente em precisão, mas permite que o modelo rode apenas com telemetria pública, em segundos, e que cada uma de suas hipóteses fique exposta à verificação. Os desenvolvimentos que reduziriam a distância em relação aos sistemas operacionais estão identificados: um modelo chuva-vazão a montante, nos moldes do MGB e alimentado por previsões como as do Open-Meteo; a inclusão do vento como forçante na saída; o uso do FABDEM (Hawker et al., 2022) no mapa de inundação; e o roteamento pontual para cobrir as lacunas do Jacuí. A [DISCUSSÃO, §7](DISCUSSAO.md#7-o-que-reduziria-o-erro) propõe uma ordem de prioridade para esses passos, informada pelos resultados de julho de 2026.

## 10. Referências

AGÊNCIA NACIONAL DE ÁGUAS E SANEAMENTO BÁSICO (Brasil). **HidroInventario**: inventário de estações hidrometeorológicas. Brasília, DF: ANA, 2026. Web service ServiceANA. Consulta às estações 85900000 e 87450020. Disponível em: https://telemetriaws1.ana.gov.br/ServiceANA.asmx. Acesso em: 8 nov. 2026.

AIRBUS DEFENCE AND SPACE. **Copernicus DEM**: Copernicus digital elevation model: product handbook. Version 5.0. [S. l.]: Airbus, 2022. Disponível em: https://dataspace.copernicus.eu/sites/default/files/media/files/2024-06/geo1988-copernicusdem-spe-002_producthandbook_i5.0.pdf. Acesso em: 8 nov. 2026.

BUTCHER, J. C. **Numerical methods for ordinary differential equations**. 3. ed. Chichester: Wiley, 2016. DOI: https://doi.org/10.1002/9781119121534.

CHOW, V. T.; MAIDMENT, D. R.; MAYS, L. W. **Applied hydrology**. New York: McGraw-Hill, 1988.

COLLISCHONN, W.; ALLASIA, D.; SILVA, B. C. da; TUCCI, C. E. M. The MGB-IPH model for large-scale rainfall-runoff modelling. **Hydrological Sciences Journal**, [S. l.], v. 52, n. 5, p. 878-895, 2007. DOI: https://doi.org/10.1623/hysj.52.5.878.

COLLISCHONN, W. et al. The exceptional hydrological disaster of April-May 2024 in southern Brazil. **RBRH**: Revista Brasileira de Recursos Hídricos, Porto Alegre, v. 30, e1, 2025. DOI: https://doi.org/10.1590/2318-0331.302520240119.

CUNGE, J. A. On the subject of a flood propagation computation method (Muskingum method). **Journal of Hydraulic Research**, [S. l.], v. 7, n. 2, p. 205-230, 1969. DOI: https://doi.org/10.1080/00221686909500264.

GERMANO, A. de O.; LAMBERTY, D.; SILVA, E. D.; BUFFON, F. T.; PEDROLLO, M. C. R. **Avaliação indireta do nível máximo das águas do delta do Rio Jacuí na região central de Porto Alegre, entre as estações Cais Mauá C6 e Usina do Gasômetro, na grande cheia de maio de 2024**. Porto Alegre: Serviço Geológico do Brasil – CPRM, 2024. Relatório técnico. Disponível em: https://rigeo.sgb.gov.br/handle/doc/24911. Acesso em: 8 nov. 2026.

HAWKER, L.; UHE, P.; PAULO, L.; SOSA, J.; SAVAGE, J.; SAMPSON, C.; NEAL, J. A 30 m global map of elevation with forests and buildings removed. **Environmental Research Letters**, Bristol, v. 17, n. 2, 024016, 2022. DOI: https://doi.org/10.1088/1748-9326/ac4d4f.

HUBER, P. J. Robust estimation of a location parameter. **The Annals of Mathematical Statistics**, [S. l.], v. 35, n. 1, p. 73-101, 1964. DOI: https://doi.org/10.1214/aoms/1177703732.

LAIPELT, L.; FAN, F. M.; PAIVA, R. C. D. de; MEDEIROS, M. S.; COLLISCHONN, W.; RUHOFF, A. Mechanisms and scenarios of the unprecedent flooding event in South Brazil 2024. **Hydrology and Earth System Sciences**, [S. l.], v. 30, p. 573-590, 2026. DOI: https://doi.org/10.5194/hess-30-573-2026.

MEDEIROS, M. S.; FAN, F. M.; PAIVA, R. C. D. de. Emergency forecasts for water levels in the Guaíba River during the 2024 unprecedented flood in South Brazil. **RBRH**: Revista Brasileira de Recursos Hídricos, Porto Alegre, v. 30, e43, 2025. DOI: https://doi.org/10.1590/2318-0331.302520250025.

MUNAR, A. M. et al. Coupling large-scale hydrological and hydrodynamic modeling: toward a better comprehension of watershed-shallow lake processes. **Journal of Hydrology**, [S. l.], v. 564, p. 424-441, 2018. DOI: https://doi.org/10.1016/j.jhydrol.2018.07.045.

NASH, J. E.; SUTCLIFFE, J. V. River flow forecasting through conceptual models part I: a discussion of principles. **Journal of Hydrology**, [S. l.], v. 10, n. 3, p. 282-290, 1970. DOI: https://doi.org/10.1016/0022-1694(70)90255-6.

PONTES, P. R. M. et al. MGB-IPH model for hydrological and hydraulic simulation of large floodplain river systems coupled with open source GIS. **Environmental Modelling & Software**, [S. l.], v. 94, p. 1-20, 2017. DOI: https://doi.org/10.1016/j.envsoft.2017.03.029.

POSSA, T. M.; COLLISCHONN, W.; JARDIM, P. F.; FAN, F. M. Hydrological-hydrodynamic simulation and analysis of the possible influence of the wind in the extraordinary flood of 1941 in Porto Alegre. **RBRH**: Revista Brasileira de Recursos Hídricos, Porto Alegre, v. 27, e29, 2022. DOI: https://doi.org/10.1590/2318-0331.272220220028.

POULTER, B.; HALPIN, P. N. Raster modelling of coastal flooding from sea-level rise. **International Journal of Geographical Information Science**, [S. l.], v. 22, n. 2, p. 167-182, 2008. DOI: https://doi.org/10.1080/13658810701371858.

RANTZ, S. E. et al. **Measurement and computation of streamflow**: volume 2: computation of discharge. Washington, DC: U.S. Geological Survey, 1982. (Water-Supply Paper, 2175). DOI: https://doi.org/10.3133/wsp2175.

WILLIAMS, L. L.; LÜCK-VOGEL, M. Comparative assessment of the GIS based bathtub model and an enhanced bathtub model for coastal inundation. **Journal of Coastal Conservation**, [S. l.], v. 24, n. 2, 23, 2020. DOI: https://doi.org/10.1007/s11852-020-00735-x.

WORLD METEOROLOGICAL ORGANIZATION. **Manual on stream gauging**: volume II: computation of discharge. Geneva: WMO, 2010. (WMO-No. 1044).

YEVJEVICH, V. M. **Bibliography and discussion of flood-routing methods and unsteady flow in channels**. Washington, DC: U.S. Government Printing Office, 1964. (Geological Survey Water-Supply Paper, 1690). DOI: https://doi.org/10.3133/wsp1690.
