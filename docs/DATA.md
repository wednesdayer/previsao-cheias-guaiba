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

Campos usados:
- `Nivel`: nível, em cm, convertido para m;
- `Vazao`: vazão, em m³/s;
- `Chuva`: chuva, em mm.

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

- **O Guaíba não tem medição de vazão.** Porto Alegre só informa nível, então a saída para a Lagoa dos Patos precisa ser inferida. Esse é o núcleo do método (ver [METHODOLOGY.md](METHODOLOGY.md#3-vazão-de-saída-sem-medição-de-vazão)). As únicas medições independentes de vazão no Guaíba são campanhas pontuais de ADCP da UFRGS (ver [DISCUSSION §4.3](DISCUSSION.md#43-nenhuma-medição-de-vazão-no-guaíba)).
- **A régua do Gasômetro começa em 03/05/2024.** Foi instalada como régua de emergência durante a cheia de maio/2024, depois que a régua histórica do Cais Mauá falhou perto do pico. O registro de calibração começa, portanto, no meio do evento.
- **Os datums das réguas são diferentes.**
  - O recorde oficial da cheia de 2024 (5,37 m em 05/05/2024 [Medeiros 2025]) se refere à régua histórica do Cais Mauá (C6). A série de telemetria do Gasômetro usada aqui chega a 4,17 m (05/05/2024, 05h30).
  - As duas réguas não estão no mesmo datum; a relação entre elas no pico é analisada em [Germano 2024]. O offset de +0,44 m medido em nível normal não concilia os dois picos e cresce durante as cheias (ver [DISCUSSION §4.4](DISCUSSION.md#44-duas-réguas-dois-datums)).
  - Todos os níveis do modelo estão no datum da telemetria do Gasômetro.
- **Rio Pardo, a estação de entrada do Jacuí, fica muda com frequência.** Tem 41% de cobertura de vazão e ficou 41 h sem transmitir durante a cheia de julho/2026. O Jacuí drena cerca de 85% da bacia, então um Rio Pardo mudo faz o modelo subestimar a entrada. O v4 roteia Cachoeira do Sul para contornar isso.
- **Lajeado transmite nível continuamente, mas vazão raramente** (7% das horas). O Taquari é o segundo maior afluente, e essa lacuna é uma das principais fontes de erro de entrada no v1–v3.
- **Controle de qualidade.** O `model/preprocess.py`:
  - descarta saltos de nível acima de 2 m/h (picos espúrios);
  - descarta valores idênticos mantidos por 12 h ou mais (sensor travado);
  - interpola lacunas de até 6 h (12 h nas estações marcadas como `sparse`) e deixa vazias as lacunas maiores.

## 2. DEM Copernicus GLO-30

Dois tiles cobrem o Guaíba e o delta do Jacuí: `Copernicus_DSM_COG_10_S30_00_W052_00_DEM` e `Copernicus_DSM_COG_10_S31_00_W052_00_DEM`. Eles são baixados do bucket público `https://copernicus-dem-30m.s3.amazonaws.com`, sem credenciais.

- **Resolução:** 1 segundo de arco, cerca de 30 m.
- **É um modelo de superfície (DSM), não de terreno.** Prédios e copas de árvore contam como chão. Por isso a inundação urbana é subestimada, e o mapa de inundação deve ser lido como ilustrativo (ver [METHODOLOGY §6](METHODOLOGY.md#63-ressalvas)).
- **Datum vertical:** EGM2008. O modelo não converte para o datum da régua. Em vez disso, ancora o DEM na régua casando a área conhecida do Guaíba em nível normal: 470 km² a cerca de 0,9 m na régua do Gasômetro.

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
