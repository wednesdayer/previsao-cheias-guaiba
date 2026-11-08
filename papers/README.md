# Referências

Cada referência foi conferida numa fonte real: Crossref, resolvedor de DOI, página da editora, USGS Publications Warehouse, Open Library ou página do órgão. Um PDF só é incluído **quando a licença permite redistribuir** (CC BY 4.0 ou domínio público dos EUA). As demais referências aparecem com DOI ou link.

As chaves curtas (por exemplo `[Chow 1988]`) são as usadas em [docs/METHODOLOGY.md](../docs/METHODOLOGY.md) e [docs/DISCUSSION.md](../docs/DISCUSSION.md). Os títulos das obras ficam no idioma original.

## PDFs incluídos

| Arquivo | Referência | Licença |
|---|---|---|
| `1964_Yevjevich_WSP1690_flood_routing_bibliography.pdf` | [Yevjevich 1964] | Domínio público (EUA) |
| `1982_Rantz_WSP2175_vol2.pdf` | [Rantz 1982], vol. 2, *Computation of discharge* | Domínio público (EUA) |
| `2022_Hawker_FABDEM.pdf` | [Hawker 2022] | CC BY 4.0 |
| `2022_Possa_RBRH_1941_flood_wind.pdf` | [Possa 2022] | CC BY |
| `2025_Collischonn_RBRH_2024_disaster.pdf` | [Collischonn 2025] | CC BY 4.0 |
| `2025_Medeiros_RBRH_Guaiba_emergency_forecasts.pdf` | [Medeiros 2025] | CC BY 4.0 |
| `2026_Laipelt_HESS_2024_flood_mechanisms.pdf` | [Laipelt 2026] | CC BY 4.0 |

Rantz vol. 1 (21 MB) e Reboita et al. (36 MB) também são abertos, mas ficaram de fora para manter o repositório leve. Os links estão abaixo.

Os checksums SHA-256 dos PDFs incluídos estão em [`SHA256SUMS`](SHA256SUMS); para conferir, rode `sha256sum -c SHA256SUMS`. Os checksums dos PDFs consultados online e não redistribuídos estão na [DISCUSSION.md §7](../docs/DISCUSSION.md#7-documentos-consultados).

## Métodos

| Chave | Referência | Acesso | Usada para |
|---|---|---|---|
| [Chow 1988] | Chow, V. T., Maidment, D. R., & Mays, L. W. (1988). *Applied Hydrology*. McGraw-Hill. ISBN 0-07-010810-2. | Livro-texto | Roteamento de reservatório, o balanço A(h)·dh/dt = Qin − Qout(h); método Muskingum |
| [Puls 1928] | Puls, L. G. (1928). Construction of flood routing curves. *U.S. 70th Congress, 1st session, House Document 185*, 46–52. | Sem original online; conferida via [Yevjevich 1964], item 207 | Origem histórica do roteamento de reservatório |
| [McCarthy 1938] | McCarthy, G. T. (1938). *The unit hydrograph and flood routing*. Conference of the North Atlantic Division, U.S. Army Corps of Engineers, New London, CT. | Manuscrito não publicado; conferida via [Yevjevich 1964], item 342 | Origem do método Muskingum (K, X) |
| [Yevjevich 1964] | Yevjevich, V. M. (1964). *Bibliography and discussion of flood-routing methods and unsteady flow in channels* (USGS Water-Supply Paper 1690). https://doi.org/10.3133/wsp1690 | PDF incluído | Revisão do roteamento de reservatório e Muskingum; fonte para Puls e McCarthy |
| [Cunge 1969] | Cunge, J. A. (1969). On the subject of a flood propagation computation method (Muskingum method). *Journal of Hydraulic Research, 7*(2), 205–230. https://doi.org/10.1080/00221686909500264 | Pago | Significado físico de K e X; por que dividir o trecho em subtrechos |
| [Rantz 1982] | Rantz, S. E., et al. (1982). *Measurement and computation of streamflow* (USGS Water-Supply Paper 2175, vols. 1–2). https://doi.org/10.3133/wsp2175 | Vol. 2 incluído | Curva-chave em potência Q = a·(h − h0)^b e cota de vazão nula h0 |
| [WMO 2010] | World Meteorological Organization (2010). *Manual on Stream Gauging* (WMO-No. 1044), vol. II: Computation of discharge. | Direitos da OMM | Prática de curvas-chave |
| [Huber 1964] | Huber, P. J. (1964). Robust estimation of a location parameter. *The Annals of Mathematical Statistics, 35*(1), 73–101. https://doi.org/10.1214/aoms/1177703732 | Project Euclid | Perda de Huber no ajuste robusto da curva de saída |
| [Nash 1970] | Nash, J. E., & Sutcliffe, J. V. (1970). River flow forecasting through conceptual models part I: A discussion of principles. *Journal of Hydrology, 10*(3), 282–290. https://doi.org/10.1016/0022-1694(70)90255-6 | Pago | Eficiência de Nash–Sutcliffe (validação do roteamento) |
| [Butcher 2016] | Butcher, J. C. (2016). *Numerical Methods for Ordinary Differential Equations* (3ª ed.). Wiley. https://doi.org/10.1002/9781119121534 | Livro | Runge–Kutta clássico de 4ª ordem |
| [Poulter 2008] | Poulter, B., & Halpin, P. N. (2008). Raster modelling of coastal flooding from sea-level rise. *International Journal of Geographical Information Science, 22*(2), 167–182. https://doi.org/10.1080/13658810701371858 | Pago | Inundação por banheira com conectividade hidrológica |
| [Williams 2020] | Williams, L. L., & Lück-Vogel, M. (2020). Comparative assessment of the GIS based bathtub model and an enhanced bathtub model for coastal inundation. *Journal of Coastal Conservation, 24*(2), 23. https://doi.org/10.1007/s11852-020-00735-x | Pago | Banheira conectada × banheira simples |
| [Hawker 2022] | Hawker, L., Uhe, P., Paulo, L., Sosa, J., Savage, J., Sampson, C., & Neal, J. (2022). A 30 m global map of elevation with forests and buildings removed. *Environmental Research Letters, 17*(2), 024016. https://doi.org/10.1088/1748-9326/ac4d4f | PDF incluído | Por que um DSM subestima a inundação; o FABDEM como correção |

## O Guaíba e a cheia de 2024

| Chave | Referência | Acesso | Usada para |
|---|---|---|---|
| [Collischonn 2025] | Collischonn, W., Fan, F. M., Possantti, I., et al. (2025). The exceptional hydrological disaster of April–May 2024 in southern Brazil. *RBRH, 30*, e1. https://doi.org/10.1590/2318-0331.302520240119 | PDF incluído | Descrição do evento; evento de validação; curvas-chave extrapoladas em Estrela/Lajeado e Muçum |
| [Medeiros 2025] | Medeiros, M. S., Fan, F. M., & Paiva, R. C. D. de (2025). Emergency forecasts for water levels in the Guaíba River during the 2024 unprecedented flood in South Brazil. *RBRH, 30*, e43. https://doi.org/10.1590/2318-0331.302520250025 | PDF incluído | Previsões operacionais feitas durante o evento (MGB + HEC-RAS + cenários de vento); pico de 5,37 m; batimetria de 1961–1966; referência de comparação para este projeto |
| [Laipelt 2026] | Laipelt, L., Fan, F. M., Paiva, R. C. D. de, Medeiros, M. S., Collischonn, W., & Ruhoff, A. (2026). Mechanisms and scenarios of the unprecedent flooding event in South Brazil 2024. *Hydrology and Earth System Sciences, 30*, 573–590. https://doi.org/10.5194/hess-30-573-2026 | PDF incluído | O Taquari define o pico e o Jacuí a duração; o vento eleva ou baixa o Guaíba em até ~50 cm; sensibilidade ao Manning; incerteza das curvas-chave |
| [Possa 2022] | Possa, T. M., Collischonn, W., Jardim, P. F., & Fan, F. M. (2022). Hydrological-hydrodynamic simulation and analysis of the possible influence of the wind in the extraordinary flood of 1941 in Porto Alegre. *RBRH, 27*, e29. https://doi.org/10.1590/2318-0331.272220220028 | PDF incluído | Efeito do vento no nível do Guaíba; a cheia de 1941 (4,76 m) |
| [Germano 2024] | Germano, A. O., Lamberty, D., Silva, E. D., Buffon, F. T., & Pedrollo, M. C. R. (2024). *Avaliação indireta do nível máximo das águas do delta do Rio Jacuí na região central de Porto Alegre, entre as estações Cais Mauá C6 e Usina do Gasômetro, na grande cheia de maio de 2024*. Serviço Geológico do Brasil. https://rigeo.sgb.gov.br/handle/doc/24911 | Repositório aberto; licença não declarada, só link | Relação entre as réguas do Cais Mauá e do Gasômetro no pico de 2024 |
| [Munar 2018] | Munar, A. M., Cavalcanti, J. R., Bravo, J. M., Fan, F. M., da Motta-Marques, D., & Fragoso, C. R. (2018). Coupling large-scale hydrological and hydrodynamic modeling. *Journal of Hydrology, 564*, 424–441. https://doi.org/10.1016/j.jhydrol.2018.07.045 | Pago | Dinâmica da Lagoa dos Patos forçada pelo vento |
| [Collischonn 2007] | Collischonn, W., Allasia, D., da Silva, B. C., & Tucci, C. E. M. (2007). The MGB-IPH model for large-scale rainfall–runoff modelling. *Hydrological Sciences Journal, 52*(5), 878–895. https://doi.org/10.1623/hysj.52.5.878 | Pago | O MGB, modelo de referência da região |
| [Pontes 2017] | Pontes, P. R. M., Fan, F. M., Fleischmann, A. S., et al. (2017). MGB-IPH model for hydrological and hydraulic simulation of large floodplain river systems coupled with open source GIS. *Environmental Modelling & Software, 94*, 1–20. https://doi.org/10.1016/j.envsoft.2017.03.029 | Pago | MGB com propagação hidrodinâmica |
| [Reboita 2024] | Reboita, M. S., Mattos, E. V., Capucin, B. C., Souza, D. O. de, & Ferreira, G. W. de S. (2024). A multi-scale analysis of the extreme precipitation in southern Brazil in April/May 2024. *Atmosphere, 15*(9), 1123. https://doi.org/10.3390/atmos15091123 | CC BY 4.0 (não incluído, 36 MB) | Meteorologia do evento de 2024 |

## Estações, curvas-chave e batimetria depois de 2024

| Chave | Referência | Usada para |
|---|---|---|
| [SGB 2024] | Serviço Geológico do Brasil (2024). *Levantamento dos níveis das marcas da grande cheia de maio de 2024 no Rio Grande do Sul* (Nota Técnica, 3ª versão, 10/09/2024). https://rigeo.sgb.gov.br/bitstream/doc/24939.5/3/nota_tecnica_levantamento_cheia_2024_v.3.pdf | Estações levadas pela correnteza ou danificadas; sistemas de alerta do Taquari e do Caí "seriamente comprometido"; nível de pico em Estrela/Lajeado (86879300) |
| [Toldo 2024] | Toldo, E., Rodrigues Nunes, J. C., Castro, N. M. R., Funke, A. J., Nievinski, F. G., Manica, R., Puhl, E., Fick, C., Scottá, F., & Silva da Silva, T. (2024). *Vazões no Rio Guaíba durante os picos da enchente de maio de 2024* (Nota Técnica, PGA POA – Portos RS/UFRGS, 24/07/2024). https://www.ufrgs.br/iph/wp-content/uploads/2024/07/05_Nota-Vazoes-no-Rio-Guaiba-durante-os-picos-da-enchente-de-maio-de-2024.pdf ; versão estendida: https://doi.org/10.5281/zenodo.14526481 | Vazão no Guaíba medida por ADCP: 35.736 m³/s (05/05/2024) e 22.070 m³/s (15/05/2024), corrente máxima de 4,2 m/s. Usada para testar a curva de saída |
| [IPH 2025] | IPH/UFRGS e PGA POA (2025). *Nota Técnica: Monitoramento ambiental e cheia no Guaíba e Delta do Jacuí em junho de 2025* (publicada em 03/07/2025; autores incluem F. M. Fan, R. Paiva, W. Collischonn, F. Dornelles, T. Silva da Silva e E. Toldo Jr). https://www.ufrgs.br/iph/wp-content/uploads/2025/07/Nota-Tecnica_Cheia-no-Guaiba-.pdf | ADCP de 12.941 m³/s (25/06/2025); perfis batimétricos de dez/2024 com erosão no Gasômetro e nos canais do Jacuí; desnível de ~30 cm entre Navegantes e Mauá; previsões de junho/2025 rodadas com batimetria antiga e incerteza de 10–20 cm; vazões de pico das cheias de 2023 a 2025 |
| [IPH site] | Arquivo de notícias do IPH/UFRGS, posts diários "Previsão de níveis do Guaíba" (maio–julho/2024; junho–julho/2025; o último em 04/07/2025). https://www.ufrgs.br/iph/noticias/ ; https://www.ufrgs.br/iph/previsao-de-niveis-do-guaiba-04-07-2025/ | Período em que o IPH publicou previsões em nome próprio |
| [IPH 2026] | IPH/UFRGS (24/09/2026). *IPH realiza Workshop sobre sistemas de alerta de cheias no RS em conjunto com o Serviço Geológico do Brasil (SGB)*. https://www.ufrgs.br/iph/iph-realiza-workshop-sobre-sistemas-de-alerta-de-cheias-no-rs-em-conjunto-com-o-servico-geologico-do-brasil-sgb/ | Previsões do Guaíba hoje emitidas nos boletins do SGB com técnicas do IPH (TED SGB–IPH) |
| [O Sul 2025] | O Sul (09/07/2025). *Cheias dos rios do Estado não foram agravadas por assoreamento, mostra estudo da UFRGS*. Noticia uma nota técnica da Portos RS com o IPH/UFRGS (batimetria de 26/12/2024). https://www.osul.com.br/cheias-rios-nao-foram-agravadas-por-assoreamento/ | Sem assoreamento generalizado; erosão local e rocha exposta perto do Gasômetro |
| [JC 2025] | Jornal do Comércio (09/07/2025). *Governo do RS espera resultados da batimetria para decidir sobre desassoreamento do Guaíba*. https://www.jornaldocomercio.com/geral/2025/07/1209772-governo-do-rs-espera-resultados-da-batimetria-para-decidir-sobre-desassoreamento-do-guaiba.html | Escopo do levantamento batimétrico do estado (Desassorear RS) |
| [Sema 2026] | Governo do Estado do RS / Sema (29/03/2026). *Governo do Estado apresenta resultados parciais da batimetria nos rios e lagos prioritários do Plano Rio Grande*. https://estado.rs.gov.br/governo-do-estado-apresenta-resultados-parciais-da-batimetria-nos-rios-e-lagos-prioritarios-do-plano-rio-grande | Sem mudança significativa nos pontos de controle em relação a 2013/2015 (resultados parciais) |
| [Unisinos 2026] | Unisinos (22/07/2026). *Projeto Guaíba consolida primeiro ano de pesquisas sobre os impactos geológicos das enchentes de 2024*. https://www.unisinos.br/noticias/projeto-guaiba-consolida-primeiro-ano-de-pesquisas-sobre-os-impactos-geologicos-das-enchentes-de-2024/ | Erosão e deposição localizadas no delta do Jacuí e em corredores de fluxo |
| [Nova ilha] | *Nova ilha no Guaíba*, Wikipédia (pt), revisão 72140419 (27/04/2026), que reúne fontes do governo do estado e da imprensa. https://pt.wikipedia.org/wiki/Nova_ilha_no_Gua%C3%ADba | Banco de areia que cresceu depois de maio/2024 (fonte secundária) |
| Paiva et al. 2025 | Paiva, R. C. D., Fan, F. M., Collischonn, W., Medeiros, M. S., Oliveira, R. C., Lima, S. G., Camargo, P., & Medeiros, P. M. (2025). *Caracterização e modelagem das cheias de 2023 e 2024 no Rio Grande do Sul em escala regional* (Relatório Técnico, IPH/UFRGS–ANA). https://lume.ufrgs.br/handle/10183/293580 ; https://doi.org/10.5281/zenodo.15831242. Citado via [Laipelt 2026] e [IPH 2025]; não lido diretamente. | Incerteza da extrapolação das curvas-chave em Rio Pardo e no Taquari |
| Lopes et al. 2018 | Fonte da batimetria das cartas da Marinha de 1961–1966, conforme citado em [Medeiros 2025]. Não lido diretamente. | Idade da batimetria de referência |

## Notícias e boletins, julho de 2026

Os boletins SGB/IPH da cheia de julho/2026 (`sgb.gov.br/sace/boletins/Guaiba/2026072*`) não estavam mais online em 08/11/2026 (HTTP 404); o conteúdo deles só é conhecido pela imprensa. As citações da [DISCUSSION.md](../docs/DISCUSSION.md#1-julho-de-2026-um-teste-em-tempo-real) vêm de:

| Data | Veículo | Conteúdo | URL |
|---|---|---|---|
| 21/07 | Extra Classe / Agência GBC (MetSul) | "perto, ao redor e acima de 2 metros" | https://www.extraclasse.org.br/ambiente/2026/07/nivel-do-guaiba-subira-e-metsul-informa-risco-nas-ilhas-de-porto-alegre/ |
| 22/07 19h50 | Porto Alegre 24 Horas | SGB + IPH + Catavento: Cais Mauá até 2,50 m; IPH: 2,50–2,60 m | https://poa24horas.com.br/tempo/2026/07/nivel-do-guaiba-pode-atingir-cota-de-alerta-neste-fim-de-semana-em-porto-alegre/ |
| 23/07 | Brasil de Fato | SGB/IPH: alerta de 2,5 m; 3 m não previstos | https://www.brasildefato.com.br/2026/07/23/subida-do-guaiba-prevista-para-o-fim-de-semana-poe-areas-ribeirinhas-de-porto-alegre-em-alerta/ |
| 23/07 15h38 | Jornal do Comércio | "Guaíba pode chegar a 2,70m… diz IPH" (paywall após o 1º parágrafo) | https://www.jornaldocomercio.com/geral/2026/07/1257312-guaiba-pode-chegar-a-270m-em-porto-alegre-no-fim-de-semana-diz-iph.html |
| 23/07 | Rádio Pampa | IPH/SGB: 2,7 m, 30 cm abaixo da cota de inundação do Cais Mauá | https://www.radiopampa.com.br/nivel-do-guaiba-pode-ficar-a-30-centimetros-da-cota-de-inundacao-no-cais-de-porto-alegre-neste-fim-de-semana/ |
| 24/07 | Sul21 [Sul21 2026c] | Dmae autorizou o fechamento de seis comportas no fim da tarde de 23/07; previsão de 2,50–2,70 m no Cais Mauá para sábado, 25/07 | https://sul21.com.br/noticias/geral/2026/07/dmae-fechara-comportas-de-porto-alegre-por-prever-elevacao-do-guaiba/ |
| 24/07 | Agência GBC / RS Notícias (Dmae) | Cenários anteriores acima de 3 m; comportas fechadas | https://agenciagbc.com/2026/07/24/porto-alegre-entra-em-alerta-apos-alta-do-guaiba-e-comportas-podem-ser-fechadas/ |
| 24/07 | GAZ (MetSul) | 2,3–2,5 m em 48 h | https://www.gaz.com.br/guaiba-alcanca-cota-de-cheia-e-deve-atingir-regiao-das-ilhas-em-porto-alegre/ |
| 29/07 | Porto Alegre 24 Horas | SGB/IPH: pode superar 3 m; cenário adverso ~3,50 m | https://poa24horas.com.br/noticias/2026/07/modelos-hidrologicos-preveem-transbordamento-do-guaiba-em-porto-alegre-ate-o-final-da-semana/ |
| 29/07 | Sul21 [Sul21 2026b] | Boletim do SGB com informações do IPH: a cota de inundação de 3 m pode ser superada entre 30/07 e 01/08 | https://sul21.com.br/noticias/geral/2026/07/guaiba-pode-superar-cota-de-inundacao-no-final-de-semana-defesa-civil-reforca-ilhas/ |
| 30/07 | Extra Classe / Brasil de Fato | SGB: entre 2,60 e 3,00 m no Cais Mauá | https://www.extraclasse.org.br/ambiente/2026/07/nivel-do-guaiba-sobe-e-novos-temporais-chegam-ao-rs-no-sabado/ |
| 31/07 | Agora RS | Boletim revisado: cota de inundação não mais prevista | https://agorars.com/rs/porto-alegre/guaiba-atinge-cota-alerta-porto-alegre-previsao-inundacao/ |
| 31/07 | Sul21 [Sul21 2026a] | Meirelles (IPH): 2,50–3,00 m; "banda de incerteza"; rede de estações danificada e sem manutenção; medição longe da Capital | https://sul21.com.br/noticias/geral/2026/07/guaiba-deve-ficar-abaixo-da-cota-de-inundacao-mas-falta-de-dados-mantem-incerteza-na-capital/ |

## Fontes de dados

| Chave | Fonte | Termos |
|---|---|---|
| [ANA telemetry] | Agência Nacional de Águas e Saneamento Básico, web service ServiceANA, operação `DadosHidrometeorologicos`. https://telemetriaws1.ana.gov.br/ServiceANA.asmx | Público, sem login. Os metadados do SNIRH para a rede hidrometeorológica nacional dizem: *"É permitida a reprodução de dados e de informações, desde que citada a fonte"*. https://metadados.snirh.gov.br/geonetwork/srv/api/records/f85dbf06-a869-414c-afc5-bb01869e9156 |
| [HidroWeb] | ANA, portal HidroWeb (Sistema Nacional de Informações sobre Recursos Hídricos). https://www.snirh.gov.br/hidroweb | Iguais aos acima |
| [Copernicus DEM] | Airbus Defence and Space (2022). *Copernicus DEM Product Handbook* (GEO.2018-1988-2, v5.0). https://dataspace.copernicus.eu/sites/default/files/media/files/2024-06/geo1988-copernicusdem-spe-002_producthandbook_i5.0.pdf | Manual: sem redistribuição, só link. Dados: *Licence for the use of the Copernicus WorldDEM-30*, que permite reprodução e modificação livres com o aviso abaixo. https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/DEM/resources/license/License-COPDEM-30.pdf |
| [OSM] | © colaboradores do OpenStreetMap | ODbL; só mapa de fundo |

Aviso obrigatório para produtos derivados do DEM (a curva cota-área e o mapa de inundação), mantido no original em inglês, como a licença exige:

> produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved
