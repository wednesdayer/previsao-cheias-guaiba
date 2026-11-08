# References

Each reference was checked against a live source (Crossref, the DOI resolver, the publisher page, the USGS Publications Warehouse, Open Library or the agency page). A PDF is included **only when its license allows redistribution** (CC BY 4.0 or US public domain). Everything else is listed with a DOI or link.

The short keys (e.g. `[Chow 1988]`) are the ones used in [docs/METHODOLOGY.md](../docs/METHODOLOGY.md).

## Included PDFs

| File | Reference | License |
|---|---|---|
| `1964_Yevjevich_WSP1690_flood_routing_bibliography.pdf` | [Yevjevich 1964] | US public domain |
| `1982_Rantz_WSP2175_vol2.pdf` | [Rantz 1982], vol. 2, *Computation of discharge* | US public domain |
| `2022_Hawker_FABDEM.pdf` | [Hawker 2022] | CC BY 4.0 |
| `2022_Possa_RBRH_1941_flood_wind.pdf` | [Possa 2022] | CC BY |
| `2025_Collischonn_RBRH_2024_disaster.pdf` | [Collischonn 2025] | CC BY 4.0 |
| `2025_Medeiros_RBRH_Guaiba_emergency_forecasts.pdf` | [Medeiros 2025] | CC BY 4.0 |
| `2026_Laipelt_HESS_2024_flood_mechanisms.pdf` | [Laipelt 2026] | CC BY 4.0 |

Rantz vol. 1 (21 MB) and Reboita et al. (36 MB) are open but were left out to keep the repository small. Their links are below.

## Methods

| Key | Reference | Access | Used for |
|---|---|---|---|
| [Chow 1988] | Chow, V. T., Maidment, D. R., & Mays, L. W. (1988). *Applied Hydrology*. McGraw-Hill. ISBN 0-07-010810-2. | Textbook | Level-pool (storage) routing, the A(h)·dh/dt = Qin − Qout(h) balance; Muskingum method |
| [Puls 1928] | Puls, L. G. (1928). Construction of flood routing curves. *U.S. 70th Congress, 1st session, House Document 185*, 46–52. | No online original; verified via [Yevjevich 1964], entry 207 | Historical origin of storage routing |
| [McCarthy 1938] | McCarthy, G. T. (1938). *The unit hydrograph and flood routing*. Conference of the North Atlantic Division, U.S. Army Corps of Engineers, New London, CT. | Unpublished manuscript; verified via [Yevjevich 1964], entry 342 | Origin of the Muskingum method (K, X) |
| [Yevjevich 1964] | Yevjevich, V. M. (1964). *Bibliography and discussion of flood-routing methods and unsteady flow in channels* (USGS Water-Supply Paper 1690). https://doi.org/10.3133/wsp1690 | PDF included | Review of storage and Muskingum routing; source for Puls and McCarthy |
| [Cunge 1969] | Cunge, J. A. (1969). On the subject of a flood propagation computation method (Muskingum method). *Journal of Hydraulic Research, 7*(2), 205–230. https://doi.org/10.1080/00221686909500264 | Paywalled | Physical meaning of K and X; why the reach is split into sub-reaches |
| [Rantz 1982] | Rantz, S. E., et al. (1982). *Measurement and computation of streamflow* (USGS Water-Supply Paper 2175, vols. 1–2). https://doi.org/10.3133/wsp2175 | Vol. 2 included | Power-law rating curve Q = a·(h − h0)^b and the gauge-height-of-zero-flow h0 |
| [WMO 2010] | World Meteorological Organization (2010). *Manual on Stream Gauging* (WMO-No. 1044), vol. II: Computation of discharge. | WMO copyright | Rating-curve practice |
| [Huber 1964] | Huber, P. J. (1964). Robust estimation of a location parameter. *The Annals of Mathematical Statistics, 35*(1), 73–101. https://doi.org/10.1214/aoms/1177703732 | Project Euclid | Huber loss for the robust rating fit |
| [Nash 1970] | Nash, J. E., & Sutcliffe, J. V. (1970). River flow forecasting through conceptual models part I: A discussion of principles. *Journal of Hydrology, 10*(3), 282–290. https://doi.org/10.1016/0022-1694(70)90255-6 | Paywalled | Nash–Sutcliffe efficiency (routing validation) |
| [Butcher 2016] | Butcher, J. C. (2016). *Numerical Methods for Ordinary Differential Equations* (3rd ed.). Wiley. https://doi.org/10.1002/9781119121534 | Book | Classical 4th-order Runge–Kutta |
| [Poulter 2008] | Poulter, B., & Halpin, P. N. (2008). Raster modelling of coastal flooding from sea-level rise. *International Journal of Geographical Information Science, 22*(2), 167–182. https://doi.org/10.1080/13658810701371858 | Paywalled | Bathtub inundation with hydrological connectivity |
| [Williams 2020] | Williams, L. L., & Lück-Vogel, M. (2020). Comparative assessment of the GIS based bathtub model and an enhanced bathtub model for coastal inundation. *Journal of Coastal Conservation, 24*(2), 23. https://doi.org/10.1007/s11852-020-00735-x | Paywalled | Connected vs plain bathtub |
| [Hawker 2022] | Hawker, L., Uhe, P., Paulo, L., Sosa, J., Savage, J., Sampson, C., & Neal, J. (2022). A 30 m global map of elevation with forests and buildings removed. *Environmental Research Letters, 17*(2), 024016. https://doi.org/10.1088/1748-9326/ac4d4f | PDF included | Why a DSM underestimates flooding; FABDEM as the fix |

## The Guaíba and the 2024 flood

| Key | Reference | Access | Used for |
|---|---|---|---|
| [Collischonn 2025] | Collischonn, W., Fan, F. M., Possantti, I., et al. (2025). The exceptional hydrological disaster of April–May 2024 in southern Brazil. *RBRH, 30*, e1. https://doi.org/10.1590/2318-0331.302520240119 | PDF included | Event description; the validation event |
| [Medeiros 2025] | Medeiros, M. S., Fan, F. M., & Paiva, R. C. D. de (2025). Emergency forecasts for water levels in the Guaíba River during the 2024 unprecedented flood in South Brazil. *RBRH, 30*, e43. https://doi.org/10.1590/2318-0331.302520250025 | PDF included | The operational forecasts made during the event (MGB + wind scenarios); peak of 5.37 m; benchmark for this project |
| [Laipelt 2026] | Laipelt, L., Fan, F. M., Paiva, R. C. D. de, Medeiros, M. S., Collischonn, W., & Ruhoff, A. (2026). Mechanisms and scenarios of the unprecedent flooding event in South Brazil 2024. *Hydrology and Earth System Sciences, 30*, 573–590. https://doi.org/10.5194/hess-30-573-2026 | PDF included | Taquari sets the peak, Jacuí the duration; wind raises or lowers the Guaíba by up to ~50 cm |
| [Possa 2022] | Possa, T. M., Collischonn, W., Jardim, P. F., & Fan, F. M. (2022). Hydrological-hydrodynamic simulation and analysis of the possible influence of the wind in the extraordinary flood of 1941 in Porto Alegre. *RBRH, 27*, e29. https://doi.org/10.1590/2318-0331.272220220028 | PDF included | Wind effect on Guaíba levels; the 1941 flood (4.76 m) |
| [Germano 2024] | Germano, A. O., Lamberty, D., Silva, E. D., Buffon, F. T., & Pedrollo, M. C. R. (2024). *Avaliação indireta do nível máximo das águas do delta do Rio Jacuí na região central de Porto Alegre, entre as estações Cais Mauá C6 e Usina do Gasômetro, na grande cheia de maio de 2024*. Serviço Geológico do Brasil. https://rigeo.sgb.gov.br/handle/doc/24911 | Open repository; license not stated, link only | Relation between the Cais Mauá and Gasômetro gauges at the 2024 peak |
| [Munar 2018] | Munar, A. M., Cavalcanti, J. R., Bravo, J. M., Fan, F. M., da Motta-Marques, D., & Fragoso, C. R. (2018). Coupling large-scale hydrological and hydrodynamic modeling. *Journal of Hydrology, 564*, 424–441. https://doi.org/10.1016/j.jhydrol.2018.07.045 | Paywalled | Wind-driven dynamics of the Patos Lagoon system |
| [Collischonn 2007] | Collischonn, W., Allasia, D., da Silva, B. C., & Tucci, C. E. M. (2007). The MGB-IPH model for large-scale rainfall–runoff modelling. *Hydrological Sciences Journal, 52*(5), 878–895. https://doi.org/10.1623/hysj.52.5.878 | Paywalled | MGB, the reference model for the region |
| [Pontes 2017] | Pontes, P. R. M., Fan, F. M., Fleischmann, A. S., et al. (2017). MGB-IPH model for hydrological and hydraulic simulation of large floodplain river systems coupled with open source GIS. *Environmental Modelling & Software, 94*, 1–20. https://doi.org/10.1016/j.envsoft.2017.03.029 | Paywalled | MGB with hydrodynamic routing |
| [Reboita 2024] | Reboita, M. S., Mattos, E. V., Capucin, B. C., Souza, D. O. de, & Ferreira, G. W. de S. (2024). A multi-scale analysis of the extreme precipitation in southern Brazil in April/May 2024. *Atmosphere, 15*(9), 1123. https://doi.org/10.3390/atmos15091123 | CC BY 4.0 (not included, 36 MB) | Meteorology of the 2024 event |

## Gauges, rating curves and bathymetry after 2024

| Key | Reference | Used for |
|---|---|---|
| [SGB 2024] | Serviço Geológico do Brasil (2024). *Levantamento dos níveis das marcas da grande cheia de maio de 2024 no Rio Grande do Sul* (Nota Técnica, 3ª versão, 10/09/2024). https://rigeo.sgb.gov.br/bitstream/doc/24939.5/3/nota_tecnica_levantamento_cheia_2024_v.3.pdf | Gauges swept away or damaged; Taquari and Caí alert systems "seriamente comprometido"; peak stage at Estrela/Lajeado (86879300) |
| [O Sul 2025] | O Sul (9 Jul 2025). *Cheias dos rios do Estado não foram agravadas por assoreamento, mostra estudo da UFRGS*. Reports a technical note by Portos RS and IPH/UFRGS (bathymetric survey of 26 Dec 2024). https://www.osul.com.br/cheias-rios-nao-foram-agravadas-por-assoreamento/ | No generalised siltation; local erosion and exposed bedrock near the Gasômetro |
| [JC 2025] | Jornal do Comércio (9 Jul 2025). *Governo do RS espera resultados da batimetria para decidir sobre desassoreamento do Guaíba*. https://www.jornaldocomercio.com/geral/2025/07/1209772-governo-do-rs-espera-resultados-da-batimetria-para-decidir-sobre-desassoreamento-do-guaiba.html | Scope of the state bathymetric survey (Desassorear RS) |
| [Sema 2026] | Governo do Estado do RS / Sema (29 Mar 2026). *Governo do Estado apresenta resultados parciais da batimetria nos rios e lagos prioritários do Plano Rio Grande*. https://estado.rs.gov.br/governo-do-estado-apresenta-resultados-parciais-da-batimetria-nos-rios-e-lagos-prioritarios-do-plano-rio-grande | No significant change at the control points compared with 2013/2015 (partial results) |
| [Unisinos 2026] | Unisinos (22 Jul 2026). *Projeto Guaíba consolida primeiro ano de pesquisas sobre os impactos geológicos das enchentes de 2024*. https://www.unisinos.br/noticias/projeto-guaiba-consolida-primeiro-ano-de-pesquisas-sobre-os-impactos-geologicos-das-enchentes-de-2024/ | Localised erosion and deposition in the Jacuí delta and flow corridors |
| [Nova ilha] | *Nova ilha no Guaíba*, Wikipedia (pt), revision 72140419 (27 Apr 2026), which compiles state-government and press sources. https://pt.wikipedia.org/wiki/Nova_ilha_no_Gua%C3%ADba | Sand bank grown after May 2024 (secondary source) |
| [Toldo 2024] | Toldo, E., Rodrigues Nunes, J. C., Castro, N. M. R., Funke, A. J., Nievinski, F. G., Manica, R., Puhl, E., Fick, C., Scottá, F., & Silva da Silva, T. (2024). *Vazões no Rio Guaíba durante os picos da enchente de maio de 2024* (Nota Técnica, PGA POA – Portos RS/UFRGS, 24 Jul 2024). https://www.ufrgs.br/iph/wp-content/uploads/2024/07/05_Nota-Vazoes-no-Rio-Guaiba-durante-os-picos-da-enchente-de-maio-de-2024.pdf ; extended version: https://doi.org/10.5281/zenodo.14526481 | ADCP discharge on the Guaíba: 35,736 m³/s (05/05/2024), 22,070 m³/s (15/05/2024), max. current 4.2 m/s. Used to test the outflow curve |
| [IPH 2025] | IPH/UFRGS and PGA POA (2025). *Nota Técnica: Monitoramento ambiental e cheia no Guaíba e Delta do Jacuí em junho de 2025* (published 3 Jul 2025; authors include F. M. Fan, R. Paiva, W. Collischonn, F. Dornelles, T. Silva da Silva, E. Toldo Jr). https://www.ufrgs.br/iph/wp-content/uploads/2025/07/Nota-Tecnica_Cheia-no-Guaiba-.pdf | ADCP 12,941 m³/s (25/06/2025); bathymetric profiles of Dec 2024 showing erosion at the Gasômetro and the Jacuí channels; ~30 cm slope Navegantes–Mauá; IPH forecasts of June 2025 ran on old bathymetry with 10–20 cm uncertainty; peak discharges of the 2023–2025 floods |
| [IPH site] | IPH/UFRGS news archive, daily "Previsão de níveis do Guaíba" posts (May–July 2024; June–July 2025; last on 04/07/2025). https://www.ufrgs.br/iph/noticias/ ; https://www.ufrgs.br/iph/previsao-de-niveis-do-guaiba-04-07-2025/ | When the IPH published forecasts under its own name |
| [IPH 2026] | IPH/UFRGS (24 Sep 2026). *IPH realiza Workshop sobre sistemas de alerta de cheias no RS em conjunto com o Serviço Geológico do Brasil (SGB)*. https://www.ufrgs.br/iph/iph-realiza-workshop-sobre-sistemas-de-alerta-de-cheias-no-rs-em-conjunto-com-o-servico-geologico-do-brasil-sgb/ | Guaíba forecasts now issued in SGB bulletins using IPH techniques (TED SGB–IPH) |
| Paiva et al. 2025 | Paiva, R. C. D., Fan, F. M., Collischonn, W., Medeiros, M. S., Oliveira, R. C., Lima, S. G., Camargo, P., & Medeiros, P. M. (2025). *Caracterização e modelagem das cheias de 2023 e 2024 no Rio Grande do Sul em escala regional* (Relatório Técnico, IPH/UFRGS–ANA). https://lume.ufrgs.br/handle/10183/293580 ; https://doi.org/10.5281/zenodo.15831242. Cited via [Laipelt 2026] and [IPH 2025]; not read directly. | Rating-curve extrapolation uncertainty at Rio Pardo and the Taquari |
| Lopes et al. 2018 | Source of the 1961–1966 Navy-chart bathymetry, as cited in [Medeiros 2025]. Not read directly. | Age of the reference bathymetry |

## News and bulletins, July 2026

The SGB/IPH bulletins of the July 2026 flood (`sgb.gov.br/sace/boletins/Guaiba/2026072*`) were no longer online on 08 Nov 2026 (HTTP 404). Their content is known only through the press. Quotes in [DISCUSSION.md](../docs/DISCUSSION.md#1-july-2026-a-real-time-test) come from:

| Date | Outlet | Content | URL |
|---|---|---|---|
| 21/07 | Extra Classe / Agência GBC (MetSul) | "perto, ao redor e acima de 2 metros" | https://www.extraclasse.org.br/ambiente/2026/07/nivel-do-guaiba-subira-e-metsul-informa-risco-nas-ilhas-de-porto-alegre/ |
| 22/07 19h50 | Porto Alegre 24 Horas | SGB + IPH + Catavento: Cais Mauá up to 2.50 m; IPH: 2.50–2.60 m | https://poa24horas.com.br/tempo/2026/07/nivel-do-guaiba-pode-atingir-cota-de-alerta-neste-fim-de-semana-em-porto-alegre/ |
| 23/07 | Brasil de Fato | SGB/IPH: 2.5 m alert, 3 m not expected | https://www.brasildefato.com.br/2026/07/23/subida-do-guaiba-prevista-para-o-fim-de-semana-poe-areas-ribeirinhas-de-porto-alegre-em-alerta/ |
| 23/07 15h38 | Jornal do Comércio | "Guaíba pode chegar a 2,70m… diz IPH" | https://www.jornaldocomercio.com/geral/2026/07/1257312-guaiba-pode-chegar-a-270m-em-porto-alegre-no-fim-de-semana-diz-iph.html |
| 23/07 | Rádio Pampa | IPH/SGB: 2.7 m, 30 cm below the Cais Mauá flood level | https://www.radiopampa.com.br/nivel-do-guaiba-pode-ficar-a-30-centimetros-da-cota-de-inundacao-no-cais-de-porto-alegre-neste-fim-de-semana/ |
| 24/07 | Agência GBC / RS Notícias (Dmae) | Earlier scenarios above 3 m; floodgates closed | https://agenciagbc.com/2026/07/24/porto-alegre-entra-em-alerta-apos-alta-do-guaiba-e-comportas-podem-ser-fechadas/ |
| 24/07 | GAZ (MetSul) | 2.3–2.5 m in 48 h | https://www.gaz.com.br/guaiba-alcanca-cota-de-cheia-e-deve-atingir-regiao-das-ilhas-em-porto-alegre/ |
| 29/07 | Porto Alegre 24 Horas | SGB/IPH: may exceed 3 m; adverse scenario ~3.50 m | https://poa24horas.com.br/noticias/2026/07/modelos-hidrologicos-preveem-transbordamento-do-guaiba-em-porto-alegre-ate-o-final-da-semana/ |
| 30/07 | Extra Classe / Brasil de Fato | SGB: between 2.60 and 3.00 m at Cais Mauá | https://www.extraclasse.org.br/ambiente/2026/07/nivel-do-guaiba-sobe-e-novos-temporais-chegam-ao-rs-no-sabado/ |
| 31/07 | Agora RS | Bulletin revised: inundation level no longer expected | https://agorars.com/rs/porto-alegre/guaiba-atinge-cota-alerta-porto-alegre-previsao-inundacao/ |
| 24/07 | Sul21 [Sul21 2026c] | Dmae authorised closing six floodgates on the evening of 23/07; forecast 2.50–2.70 m at Cais Mauá for Saturday 25/07 | https://sul21.com.br/noticias/geral/2026/07/dmae-fechara-comportas-de-porto-alegre-por-prever-elevacao-do-guaiba/ |
| 29/07 | Sul21 [Sul21 2026b] | SGB bulletin with IPH information: flood level of 3 m may be exceeded between 30/07 and 01/08 | https://sul21.com.br/noticias/geral/2026/07/guaiba-pode-superar-cota-de-inundacao-no-final-de-semana-defesa-civil-reforca-ilhas/ |
| 31/07 | Sul21 [Sul21 2026a] | Meirelles (IPH): 2.50–3.00 m; "banda de incerteza"; damaged, unmaintained gauge network; measurement far from the Capital | https://sul21.com.br/noticias/geral/2026/07/guaiba-deve-ficar-abaixo-da-cota-de-inundacao-mas-falta-de-dados-mantem-incerteza-na-capital/ |

## Data sources

| Key | Source | Terms |
|---|---|---|
| [ANA telemetry] | Agência Nacional de Águas e Saneamento Básico, ServiceANA web service, operation `DadosHidrometeorologicos`. https://telemetriaws1.ana.gov.br/ServiceANA.asmx | Public, no login. The SNIRH metadata for the national hydrometric network states: *"É permitida a reprodução de dados e de informações, desde que citada a fonte"* (reproduction allowed with attribution). https://metadados.snirh.gov.br/geonetwork/srv/api/records/f85dbf06-a869-414c-afc5-bb01869e9156 |
| [HidroWeb] | ANA, HidroWeb portal (Sistema Nacional de Informações sobre Recursos Hídricos). https://www.snirh.gov.br/hidroweb | Same as above |
| [Copernicus DEM] | Airbus Defence and Space (2022). *Copernicus DEM Product Handbook* (GEO.2018-1988-2, v5.0). https://dataspace.copernicus.eu/sites/default/files/media/files/2024-06/geo1988-copernicusdem-spe-002_producthandbook_i5.0.pdf | Handbook: no redistribution, link only. Data: *Licence for the use of the Copernicus WorldDEM-30*, free reproduction and modification with the notice below. https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/DEM/resources/license/License-COPDEM-30.pdf |
| [OSM] | © OpenStreetMap contributors | ODbL, basemap only |

Required notice for products derived from the DEM (the stage–area curve and the inundation map):

> produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved
