# Fontes de dados

Tudo o que o modelo usa é público e gratuito. Nada é redistribuído neste repositório: a pasta `data/` está no `.gitignore`, e os scripts abaixo a reconstroem a partir das fontes originais.

| Dado | Fornecedor | Uso | Como obter |
|---|---|---|---|
| Telemetria hidrometeorológica (nível, vazão, chuva; 15 min) | ANA (Agência Nacional de Águas e Saneamento Básico); estações da rede hidrometeorológica nacional operadas com o SGB/CPRM e órgãos estaduais | Entradas do modelo e calibração | `python scripts/backfill.py --start 2024-04-01` |
| JSON só de nível | nivelguaiba.com.br (agregador não oficial) | Só reserva, quando a ANA está fora do ar ou atrasada | Buscado automaticamente pelo `ingest/service.py` |
| DEM Copernicus GLO-30 (dois tiles de 1°×1°) | ESA / Copernicus, via AWS Open Data | Curva cota-área e mapa de inundação | `python scripts/build_area_curve.py` (baixa os tiles) |
| Mapa de fundo | © colaboradores do OpenStreetMap | Fundo do mapa no dashboard | Carregado pelo Plotly em tempo de execução |

As licenças e as citações de cada fonte estão em [`papers/README.md`](../papers/README.md#fontes-de-dados).

## 1. Telemetria da ANA

**Endpoint** (aberto, sem autenticação, XML):

```
https://telemetriaws1.ana.gov.br/ServiceANA.asmx/DadosHidrometeorologicos
    ?codEstacao=<CÓDIGO>&dataInicio=DD/MM/AAAA&dataFim=DD/MM/AAAA
```

Do XML retornado, o modelo usa três campos: `Nivel`, o nível em centímetros, convertido para metros; `Vazao`, a vazão em m³/s; e `Chuva`, a precipitação em milímetros.

As leituras chegam a cada 15 min e costumam atrasar. Por isso cada busca incremental relê uma janela de sobreposição de 6 h (`settings.CACHE_OVERLAP_HOURS`). O backfill pede no máximo 30 dias por chamada.

**As vazões não são medidas diretamente.** A ANA as calcula a partir da curva-chave (nível–vazão) de cada estação. Em cheias extremas essas curvas são extrapoladas além da faixa medida, então trate as vazões de pico como números com ±10–20% de incerteza.

### Estações

Cobertura é a fração de horas com pelo menos uma leitura válida, do primeiro registro até 08/11/2026.

| Código | Estação | Rio | Papel no modelo | Nível | Vazão |
|---|---|---|---|---|---|
| 85900000 | Rio Pardo | Jacuí | entrada (v1–v3) | 43% | 41% |
| 85642000 | Cachoeira do Sul | Jacuí | montante / fonte do roteamento (v4) | 96% | 96% |
| 85400000 | Dona Francisca | Jacuí | montante / validação do roteamento | 99% | 99% |
| 86879300 | Lajeado | Taquari | entrada (v1–v3) | 95% | **7%** |
| 86510000 | Muçum | Alto Taquari | montante / validação do roteamento | 99% | 99% |
| 86720000 | Encantado | Alto Taquari | montante / fonte do roteamento (v4) | 90% | 94% |
| 86881000 | Bom Retiro do Sul | Taquari | montante (só nível) | 85% | — |
| 87170000 | São Sebastião do Caí | Caí | entrada | 92% | 92% |
| 87165001 | Feliz | Caí | montante (só nível) | 83% | — |
| 87382000 | São Leopoldo | Sinos | entrada | 100% | 100% |
| 87376000 | Taquara | Sinos / Paranhana | montante (só nível) | 63% | — |
| 87399000 | Gravataí (Passo das Canoas) | Gravataí | entrada | 100% | 100% |
| 87450020 | Porto Alegre, Usina do Gasômetro | Guaíba | **alvo** (base da calibração) | 96% | — |
| 87450004 | Porto Alegre, Cais Mauá (C6) | Guaíba | alvo derivado (offset de datum de +0,44 m) | 47% | — |
| 87450030 | Eldorado do Sul (BR-290) | Guaíba | alvo derivado (sem telemetria pública) | — | — |

Os metadados das estações (coordenadas, áreas de drenagem, cotas de inundação) estão em [`config/stations.yaml`](../config/stations.yaml). As coordenadas vêm do HidroInventário da ANA.

### Peculiaridades dos dados que moldam o modelo

A característica mais determinante dos dados é uma ausência: o Guaíba não tem medição contínua de vazão. Porto Alegre informa apenas nível, e a vazão que segue para a Lagoa dos Patos precisa, por isso, ser inferida, o que constitui o núcleo do método descrito na [METODOLOGIA](METODOLOGIA.md#3-vazão-de-saída-sem-medição-de-vazão). As únicas medições independentes de vazão no Guaíba vêm de campanhas pontuais de ADCP realizadas pela UFRGS, discutidas na [DISCUSSÃO, §4.3](DISCUSSAO.md#43-nenhuma-medição-de-vazão-no-guaíba).

A régua do Gasômetro, que serve de alvo ao modelo, só começa a registrar em 3 de maio de 2024. Ela foi instalada como régua de emergência durante a cheia daquele mês, depois que a régua histórica do Cais Mauá deixou de funcionar perto do pico, e o registro de calibração começa, portanto, no meio do maior evento da série. As duas réguas tampouco compartilham o datum. O recorde oficial de 2024, 5,37 m em 5 de maio [Medeiros 2025], refere-se ao Cais Mauá (C6), enquanto a telemetria do Gasômetro usada aqui atinge 4,17 m às 5h30 do mesmo dia. A relação entre as duas no pico é objeto de estudo específico [Germano 2024], e o deslocamento de +0,44 m medido em nível normal não só deixa de conciliar os dois picos como cresce durante as cheias ([DISCUSSÃO, §4.4](DISCUSSAO.md#44-duas-réguas-dois-datums)). Todos os níveis do modelo estão no datum da telemetria do Gasômetro.

Do lado da entrada, as duas estações mais importantes são também as menos confiáveis. Rio Pardo, que representa o Jacuí, tem dados de vazão em 41% das horas e ficou 41 horas sem transmitir durante a cheia de julho de 2026; como o Jacuí drena cerca de 85% da bacia, cada silêncio dessa estação leva o modelo a subestimar a entrada, e foi para contornar o problema que o v4 passou a rotear a vazão de Cachoeira do Sul. Lajeado, no Taquari, transmite nível de forma contínua, mas vazão em apenas 7% das horas, lacuna que figura entre as principais fontes de erro de entrada nas versões v1 a v3, dado que o Taquari é o segundo maior afluente e o que define os picos.

O controle de qualidade aplicado pelo `model/preprocess.py` procura separar falhas de sensor de variações reais. Saltos de nível superiores a 2 m/h são tratados como picos espúrios e descartados, assim como valores idênticos mantidos por 12 horas ou mais, padrão típico de sensor travado. Lacunas de até seis horas são preenchidas por interpolação temporal (doze horas nas estações marcadas como `sparse`), e as lacunas maiores permanecem vazias, por decisão deliberada de não inventar dados onde a série não os tem.

## 2. DEM Copernicus GLO-30

Dois tiles cobrem o Guaíba e o delta do Jacuí: `Copernicus_DSM_COG_10_S30_00_W052_00_DEM` e `Copernicus_DSM_COG_10_S31_00_W052_00_DEM`. Eles são baixados do bucket público `https://copernicus-dem-30m.s3.amazonaws.com`, sem credenciais.

O DEM tem resolução de 1 segundo de arco, cerca de 30 m, e é um modelo de superfície (DSM), não de terreno: prédios e copas de árvore contam como chão. Isso faz o mapa subestimar a inundação nas áreas urbanas e é a razão pela qual ele deve ser lido como ilustrativo ([METODOLOGIA §6.3](METODOLOGIA.md#63-ressalvas)). O datum vertical do produto é o EGM2008, e o modelo não o converte para o datum da régua; em vez disso, ancora o DEM na régua fazendo coincidir a área conhecida do Guaíba em nível normal, 470 km², com o nível de cerca de 0,9 m no Gasômetro.

Produtos derivados, regenerados localmente:

| Arquivo | Script | Conteúdo |
|---|---|---|
| `config/stage_area.yaml` | `scripts/build_area_curve.py` | Curva A(h), de 470 a 961 km² entre 0 e 6 m (versionada; arquivo pequeno) |
| `data/inundation/region.npz` | `scripts/build_inundation.py` | DEM recortado + raster de "nível de chegada" para o mapa (13 MB; não versionado) |

## 3. Como reconstruir a pasta de dados

```bash
pip install -e ".[dev,geo]"
python scripts/backfill.py --start 2024-04-01   # ~10 MB de parquet, alguns minutos
python scripts/build_area_curve.py              # baixa ~85 MB de tiles do DEM
python scripts/build_inundation.py
```

Os parâmetros calibrados em `config/params/` estão versionados, então o dashboard roda só com o backfill. A etapa do DEM só é necessária para o mapa e para as versões v2–v4.
