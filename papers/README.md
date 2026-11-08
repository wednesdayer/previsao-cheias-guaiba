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

## Data sources

| Key | Source | Terms |
|---|---|---|
| [ANA telemetry] | Agência Nacional de Águas e Saneamento Básico, ServiceANA web service, operation `DadosHidrometeorologicos`. https://telemetriaws1.ana.gov.br/ServiceANA.asmx | Public, no login. The SNIRH metadata for the national hydrometric network states: *"É permitida a reprodução de dados e de informações, desde que citada a fonte"* (reproduction allowed with attribution). https://metadados.snirh.gov.br/geonetwork/srv/api/records/f85dbf06-a869-414c-afc5-bb01869e9156 |
| [HidroWeb] | ANA, HidroWeb portal (Sistema Nacional de Informações sobre Recursos Hídricos). https://www.snirh.gov.br/hidroweb | Same as above |
| [Copernicus DEM] | Airbus Defence and Space (2022). *Copernicus DEM Product Handbook* (GEO.2018-1988-2, v5.0). https://dataspace.copernicus.eu/sites/default/files/media/files/2024-06/geo1988-copernicusdem-spe-002_producthandbook_i5.0.pdf | Handbook: no redistribution, link only. Data: *Licence for the use of the Copernicus WorldDEM-30*, free reproduction and modification with the notice below. https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/DEM/resources/license/License-COPDEM-30.pdf |
| [OSM] | © OpenStreetMap contributors | ODbL, basemap only |

Required notice for products derived from the DEM (the stage–area curve and the inundation map):

> produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved
