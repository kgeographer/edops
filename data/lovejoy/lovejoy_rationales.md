# Lovejoy pre-colonial African subregions — article rationales

Verbatim spans from *Defining Regions of Pre-Colonial Africa* (Lovejoy et al., **History in Africa** 48, 2021), pp. 8–22, extracted by `scripts/edop/workbench/build_lovejoy_rationale.py`. Mechanical cleanup only (de-ligature, footnote-marker strip, line-wrap hyphenation, whitespace); line-wrap repair sometimes fuses a real hyphen — those are listed per entry as `hyphen-joins`. `ethnonyms` is a best-effort list pulled from the span's "Ethnonyms included …" sentences — curate freely. **Review target:** the rationale paragraph, the `page` value, and `ethnonyms`. After review this file is the source of truth — `build_lovejoy_geojson.py` folds `text` + `page` + `ethnonyms` per `src_id` into the served geojson.

<!-- PARSER CONTRACT (build_lovejoy_geojson.py):
     entry heading = '## <src_id> · <name>'          (keep verbatim)
     '- page:'      = string, e.g. 11  or  11–12 (en-dash)   — editable
     '- ethnonyms:' = comma-delimited list, may be empty     — editable
     body          = the paragraph(s) after the blank line below the last
                     '- ' line, up to the next '## ' — the rationale, verbatim
     '_missing_' body or MISSING flag => no rationale; needs hand-entry -->

## Summary

| src_id | subregion | macro | page | chars | ethn | flags |
|--------|-----------|-------|------|-------|------|-------|
| hc_43 | Comoros | East Africa | 20–21 | 166 | 0 | SHORT, NO_BOUNDARY_LANGUAGE, CROSS_PAGE |
| hc_21 | East Central | East Africa | 20 | 659 | 7 | — |
| hc_20 | East Coast | East Africa | 20 | 688 | 6 | — |
| hc_18 | Eastern Interior | East Africa | 19 | 411 | 4 | — |
| hc_14 | Eastern Savanna | East Africa | 20 | 278 | 5 | SHORT |
| hc_19 | Great Lakes | East Africa | 20 | 387 | 6 | — |
| hc_16 | Horn | East Africa | 19 | 194 | 0 | SHORT |
| hc_29 | Madagascar | East Africa | 20 | 525 | 2 | NO_BOUNDARY_LANGUAGE |
| hc_44 | Mascarenes | East Africa | 21 | 527 | 0 | — |
| hc_15 | Northeast | East Africa | 19 | 819 | 0 | — |
| hc_30 | Canarias | North Africa | 11 | 506 | 1 | — |
| hc_11 | Nile Valley | North Africa | 10–11 | 909 | 0 | CROSS_PAGE |
| hc_10 | North Coast | North Africa | 10 | 641 | 0 | — |
| hc_01 | Northwest | North Africa | 8–10 | 899 | 0 | CROSS_PAGE |
| hc_12 | Central Sahara | Saharan Africa | 11–12 | 682 | 0 | CROSS_PAGE |
| hc_02 | Western Sahara | Saharan Africa | 11 | 808 | 0 | HYPHEN_JOIN |
| hc_25 | Kalahari | Southern Africa | 22 | 177 | 0 | SHORT |
| hc_26 | South Central | Southern Africa | 21–22 | 1000 | 6 | CROSS_PAGE |
| hc_27 | Southeast | Southern Africa | 22 | 696 | 5 | — |
| hc_28 | Southern Grasslands | Southern Africa | 21 | 547 | 0 | — |
| hc_40 | Cabo Verde | West Africa | 16 | 358 | 0 | NO_BOUNDARY_LANGUAGE |
| hc_13 | Central Savanna | West Africa | 13 | 942 | 7 | — |
| hc_09 | Eastern Bight | West Africa | 15–16 | 925 | 6 | CROSS_PAGE |
| hc_06 | Forests | West Africa | 14–15 | 829 | 4 | CROSS_PAGE |
| hc_67 | Gulf Islands | West Africa | 16 | 354 | 0 | — |
| hc_05 | Rivers | West Africa | 14 | 2172 | 13 | LONG |
| hc_07 | Voltaic | West Africa | 15 | 1225 | 3 | — |
| hc_08 | Western Bight | West Africa | 15 | 901 | 5 | — |
| hc_04 | Western Savanna | West Africa | 13 | 1309 | 4 | — |
| hc_17 | Rainforest | West Central Africa | 17–18 | 777 | 4 | CROSS_PAGE |
| hc_22 | Southern Savanna | West Central Africa | 18 | 809 | 7 | — |
| hc_45 | St. Helena | West Central Africa | 18 | 363 | 0 | — |
| hc_23 | West Central North | West Central Africa | 16–17 | 1612 | 18 | LONG, CROSS_PAGE |
| hc_24 | West Central South | West Central Africa | 17 | 988 | 18 | — |

_median span length: 692 chars; 0 missing_

---

## hc_43 · Comoros

- macro: East Africa
- page: 20–21
- flags: SHORT, NO_BOUNDARY_LANGUAGE, CROSS_PAGE
- ethnonyms: 

The Comoros are located in the Mozambique Channel and consist of Grande Comore (Ngazidja), Anjouan (Ndzuwani or Nzwani), Mohéli (Mwali) and Mayotte (Maore or Mahori).

## hc_21 · East Central

- macro: East Africa
- page: 20
- flags: none
- ethnonyms: Makonde, Makua, Manganja, Ngindo, Nyasa, Sena, Yao

East Central lies between the Rufiji and Zambezi Rivers, including the Kilwa coast. Inland boundaries run along the Rufiji River to the Luwegu confluence, after which it extends westward along the southern shores of Lake Tanganyika and then the Luapula River southward until Zumbo. It includes Lake Nyasa (Malawi) and the Zambezi valley. For the most part captives boarded slave ships through Angoche, Kilwa Kivinje, Mozambique Island, and Quelimane, which mostly engaged in trade to Brazil in the early nineteenth century. Ethnonyms included Makonde, Makua, Manganja, Ngindo, Nyasa, Sena, and Yao. It was also the location of Portuguese land grants (prazos).

## hc_20 · East Coast

- macro: East Africa
- page: 20
- flags: none
- ethnonyms: Bagamoyo, Nyika, Somali, Swahili, Zaramo, Zigula
- hyphen-joins (verify — some are real hyphens): participated

East Coast, or Swahili coast, is a relatively thin strip of territory stretching from the Shabelle River and extending to the Rufiji River and Mafia Island to the south of Zanzibar. It extends no more than about 200 kilometers inland; beyond which is a low population, except in highland areas of the eastern interior. Numerous trading towns did not develop strong territorial empires, but rather ports and places, such as Mogadishu and Mombasa, which participated in the monsoons of the trans-Indian Ocean trade. It includes the Zanzibar archipelago, and especially the main islands of Pemba and Unguja (Zanzibar). Ethnonyms included Bagamoyo, Nyika, Somali, Swahili, Zaramo, and Zigula.

## hc_18 · Eastern Interior

- macro: East Africa
- page: 19
- flags: none
- ethnonyms: Kamba, Nyamwezi, Maasai, Turkana

Eastern Interior includes the plains and mountains of eastern Africa that dominate the eastern hinterland as far as the Great Lakes. To the north it abuts with the Ethiopian highlands and blends into the semi-desert of the Horn. Different pastoral societies populated the sub-region’s northern reaches, while the south was a source of slaves at Zanzibar. Ethnonyms included Kamba, Nyamwezi, Maasai, and Turkana.

## hc_14 · Eastern Savanna

- macro: East Africa
- page: 20
- flags: SHORT
- ethnonyms: Wadai, Darfur, Nuer, Sara, Shilluk

Eastern Savanna incorporates Wadai, Darfur, and Kordofan west of the Nile valley. It includes the Sudd region and sources of the Congo River’s northern tributaries. Besides the inhabitants of Wadai and Darfur, it included nomadic Arabs as well as Dinka, Nuer, Sara, and Shilluk.

## hc_19 · Great Lakes

- macro: East Africa
- page: 20
- flags: none
- ethnonyms: Baganda, Banyarwanda, Banyoro, Barundi, Bashi, Manyema
- hyphen-joins (verify — some are real hyphens): northeast

Great Lakes form around the large lakes of Albert, Kivu, Kyoga, Edward, Rukwa, Victoria, Tanganyika, but not Bangwela, Bangweulu, Kisale, Mweru, and Malawi. This sub-region was a source of enslaved people into the northeast, eastern savanna, and Nile valley. Most arrived at the east coast opposite Zanzibar. Ethnonyms included Baganda, Banyarwanda, Banyoro, Barundi, Bashi, and Manyema.

## hc_16 · Horn

- macro: East Africa
- page: 19
- flags: SHORT
- ethnonyms: 

Due to its distinct geographic shape, the Horn sub-region contains the Somali desert and environs. It borders the Ethiopian highlands and Rift valley. Its sparse population was primarily Somali.

## hc_29 · Madagascar

- macro: East Africa
- page: 20
- flags: NO_BOUNDARY_LANGUAGE
- ethnonyms: Merina, Sakalava
- hyphen-joins (verify — some are real hyphens): ethnonyms

Madagascar was both a source and destination for enslaved captives of diverse cultures. It is grouped into East Africa due to the nature of trade across the Mozambique Channel and into the Indian Ocean world. Malagasy ethnonyms consisted of Merina, also called Hova by slave traders, and Sakalava. Southwest Indian Ocean island clusters have always been connected to the broad East Africa region, and served both as a destination and departure point for enslaved people, especially in the eighteenth and nineteenth centuries.

## hc_44 · Mascarenes

- macro: East Africa
- page: 21
- flags: none
- ethnonyms: 
- hyphen-joins (verify — some are real hyphens): geopolitical, worthwhile

The Mascarenes are centered around Mauritius, in particular, and Réunion, which different Europeans variously occupied, were connected in the East India trade, and were the geopolitical-economic center of the southwest Indian Ocean islands. It is worthwhile to lump into the Mascarenes archipelagos, including the Seychelles, which contain over one hundred islands such as, Mahé, Praslin, and La Digue. We also include Agalega, Chagos, Rodrigues, and Tromelin because a slave trade went to those small, mostly isolated islands.

## hc_15 · Northeast

- macro: East Africa
- page: 19
- flags: none
- ethnonyms: 
- hyphen-joins (verify — some are real hyphens): commercial

The Northeast sub-region encompasses most of modern-day Eritrea, Ethiopia, Djibouti, and most of Somalia. In a certain sense, this region is among the more difficult to define due to its connection to the Nile valley, Great Lakes, eastern savanna, Somali desert, and Indian Ocean world. Since pre-Aksumite times, people from this sub-region engaged in far-flung commercial exchanges with the Nile valley, Red Sea, Persian Gulf, and Indian Ocean. The northern border sits around the Aswan line, and extends toward the Great Lakes. South of Aswan, various kingdoms flourished, such as Dinka, Meroe-Kush, Funj, Nubia, Nuer, and Shilluk. At different points in time, commercial hubs included Adulis, Berbera, Dahlak al-Kabīr, Massawa, Tajura, and Zeila. Enslaved Africans from this region were collectively labeled habasha.

## hc_30 · Canarias

- macro: North Africa
- page: 11
- flags: none
- ethnonyms: Guanches
- hyphen-joins (verify — some are real hyphens): Fuerteventura, However

Canarias are an archipelago of islands centered at Tenerife, Fuerteventura, and Gran Canaria, among other smaller islands and islets. Long after the Almoravid, Almohad, and other Muslim states occupied parts of the Iberian Peninsula, Spanish kingdoms conquered the islands in 1402. However, indigenous groups, collectively known as Guanches, already inhabited the island and perhaps share a common ancestry with Amazigh groups, and later, with other peoples from Europe, most especially Portugal and Spain.

## hc_11 · Nile Valley

- macro: North Africa
- page: 10–11
- flags: CROSS_PAGE
- ethnonyms: 

Nile Valley includes modern Egypt, the Sudan, and part of South Sudan. The Sinai Peninsula, which is part of modern-day Egypt, is often considered to be the desert boundary between Africa and Asia. The Mediterranean is the northern border, with its major port of Alexandria, and the eastern Sahara between the Nile and Red Sea. To the west of the Nile lies the Western Desert, also known as the Libyan Desert, with its oases of Abu, Bahariya, Dakhla, Farafra, Kharga, Minqar, Mut, and Selima. It has the oldest trans-Saharan donkey and camel caravans, and riverine routes, including a well-known forty-day trail (darb al-arbaʿīn). The valley extends to the Red Sea, just south of Sawakin, which was a major port to the Arabian Peninsula and beyond. The Nile runs beyond Dongola in the southwest to around Aswan near the fifth cataract, which has been a political and linguistic border from very ancient times.

## hc_10 · North Coast

- macro: North Africa
- page: 10
- flags: none
- ethnonyms: 
- hyphen-joins (verify — some are real hyphens): southcentral

North Coast begins to the west of the Mediterranean Island of Djerba, on the boundary between modern-day Tunisia and Libya. To the southwest, it is bordered by the town of Wazin on edge of the Nafusa Mountains; the southcentral oasis of Waddan, on the border of the Sirt Desert to the north, and the Black Mountain to the south; the Great Sand Sea to the south; and the Qattara Depression in the east. The region features the port of Tripoli, and on the eastern coast, a region encompassing the Green Mountains known as Cyrenaica and the port of Benghazi. Tripoli was one of the most important centers of the trans-Mediterranean slave trade.

## hc_01 · Northwest

- macro: North Africa
- page: 8–10
- flags: CROSS_PAGE
- ethnonyms: 

The Northwest sub-region overlaps with the Maghreb and extends along the northern coast of Africa to the west of Tripoli. As the most important destination and transit zone of enslaved Africans via trans-Saharan traffic, it included the High Atlas mountains in modern-day Morocco to the Tell Atlas range, which extend into western Tunisia. The southern border includes the ruins of Sijilmasa located in the large oasis of Tafilalt, which was once a thriving terminus of trans-Saharan caravans. Its numerous ports on the Atlantic include Agadir, Essaouira, Salé; and on the Mediterranean, they extend from Tangiers to Tunis. These ports, which are too numerous to list here, were centers of transit of enslaved Africans across the Mediterranean into Europe. Since the time of Roman occupation, the region has been predominately Amazigh (Berber) including Almoravids, Almohad, and other Muslim states.

## hc_12 · Central Sahara

- macro: Saharan Africa
- page: 11–12
- flags: CROSS_PAGE
- ethnonyms: 
- hyphen-joins (verify — some are real hyphens): northeastern

Central Sahara includes the desert’s mountain ranges of Ahaggar, Aïr, and Tibesti; and extends westward to the Gilf Kebir plateau. The northeastern border holds the oasis of Siwa, an ancient gateway to Egypt, and the markets Awjila and Jalu. The Tuareg heartland included the Fezzan region, a historic desert epicenter of trans-Saharan traffic, circulating in all directions at least since the time of the Garamantes. Oases include, Ghat, Khufra, Murzuk, Ubari, Zawila, and in the north, Ghadames which absorbed enslaved laborers from the Sahel. To the south, key centers of trade are Agadez, Takedda, and the salt and date export region of Kawar, with its main oasis town at Bilma.

## hc_02 · Western Sahara

- macro: Saharan Africa
- page: 11
- flags: HYPHEN_JOIN
- ethnonyms: 
- hyphen-joins (verify — some are real hyphens): EssoukTadmekka

Western Sahara borders the Atlantic to the west. The northern border encompasses the two large desert plains of the western and eastern Grand Erg; and near the Oued Noun with its market of Guelmim, which is known as the westernmost “door of the Sahara.” This region includes the oases of Ghardaïa, Gourara, Ouargla, Touat, and Tidikelt. Like most Saharan oases, these were centers of date palm cultivation, and significant destinations or transit zones for enslaved Africans originating in the Sahel and savannas. Its eastern border lies just to the west of the Ahaggar Mountain range. The southeastern limits include the city of Kidal and nearby ruins of EssoukTadmekka, now in northern Mali. It also included the salt mines of Idjil, Taodenni, and Teghazza, which generated currency for slave transactions.

## hc_25 · Kalahari

- macro: Southern Africa
- page: 22
- flags: SHORT
- ethnonyms: Gkana, Haikom, ǃKung, Khoekhoe, Naro, Tshu–Khwe

The Kalahari sub-region includes both the Kalahari and Namib deserts, which had low populations of hunter-gatherers, such as Gkana, Haikom, ǃKung, Khoekhoe, Naro, and Tshu–Khwe.

## hc_26 · South Central

- macro: Southern Africa
- page: 21–22
- flags: CROSS_PAGE
- ethnonyms: Shona, Karanga, Korekore, Manyika, Ndau, Zezuru
- hyphen-joins (verify — some are real hyphens): subgroups, expansion

South Central is the Zimbabwe plateau and mostly consists of wide-open grasslands. The Highveld constitutes the other major geographic feature of this area and is separated from the southeast by the Drakensberg Mountains. The area around the so-called copper belt forms the northern border. The major ethnic group was identified as Shona after c.1800, and includes the subgroups of Karanga, Korekore, Manyika, Ndau, and Zezuru. Given the historic connections between Mapungubwe, Tswana and Sotho areas, it included the Mutapa kingdom, and its earlier Zimbabwe kingdom; and Swazi. Venda inhabited both sides of the Limpopo River; and the Tonga on both sides of the Zambezi. It connects directly to the Mozambique Channel via Kiteve, Manica, and Mutapa with a coastal outlet for the interior at Sofala. It was an area with pockets of Nguni speakers, including Ndebele who moved from the Highveld northward after the 1830s, and it was a destination of Boer expansion from Cape Town, among other peoples.

## hc_27 · Southeast

- macro: Southern Africa
- page: 22
- flags: none
- ethnonyms: Bitonga, Chope, Ronga, Tsonga, Southern Nguni

Southeast refers to the coastal belt from Sofala Bay south to Maputo Bay, formerly known as Delagoa Bay or Lourenço Marques, and separated from the Highveld in the interior by the Drakensberg Mountains. Inhabitants included Bitonga, Chope, Ronga, and Tsonga. The principal slaving port was Inhambane, while Delagoa Bay had Austrian, Dutch, and Portuguese establishments from the eighteenth century onward. The area south of Maputo represents the historic and current heartland of Nguni-speaking people with most of them in that area speaking IsiZulu. The Zulu once were referred to as the “Northern Nguni” to distinguish them from the Xhosa, or “Southern Nguni,” but these terms have fallen away.

## hc_28 · Southern Grasslands

- macro: Southern Africa
- page: 21
- flags: none
- ethnonyms: 

Southern Grasslands extends from the Cape of Good Hope, along the coast and inland east of the Kalahari Desert. It included many of the Khoisan speaking areas from the Cape to the Nguni region, and Mpondo. The Xhosa used to be called the “Southern Nguni.” Nguni-speakers, specifically the Xhosa, predominate in the southern areas, including in the present-day province of Eastern Cape in South Africa, and cities of East London and Port Elizabeth. Other ethnolinguistic groups included European descendants at Cape Town, who became known as Boers.

## hc_40 · Cabo Verde

- macro: West Africa
- page: 16
- flags: NO_BOUNDARY_LANGUAGE
- ethnonyms: 
- hyphen-joins (verify — some are real hyphens): windward

The Cabo Verde islands were uninhabited until their discovery by the Portuguese in 1456. They are divided into two groups: Barlavento or windward islands with Boa Vista, Santo Antão, Santa Luzia, São Vicente, São Nicolau, and Sal; and Sotavento or leeward islands with Brava, Fogo, Maio, and Santiago. They had ties to the mainland through Bissau and Cacheu.

## hc_13 · Central Savanna

- macro: West Africa
- page: 13
- flags: none
- ethnonyms: Fulani, Fellata, Agusa (Jausa), Bornu, Fula, Gwari, Tapa

Central Savanna is landlocked and does not connect to the Atlantic. It includes the Sahel and savanna downstream to the east of the great bend in the Niger River, south of Gao to the confluence with the Benue River, and eastward to the Lake Chad basin. We avoid using the historical term “Central Sudan” due to modern-day countries. Areas around Lake Chad include the Yadrem and Yobe rivers, Mandara Mountains, Gongola basin and northern Adamawa plateau. It includes the various Hausa states, which consolidated into the Sokoto Caliphate after 1804; Jos Plateau, Kanem-Borno, Gwari, parts of Nupe and Borgu, among others. Hausa and Kanuri were among the most widely spoken languages, although Fulfulde was also widespread because of nomadic Fulbe pastoralists, known locally as Fulani or Fellata. People from this region reached the Americas via the bights and occasionally classified as Agusa (Jausa), Bornu, Fula, Gwari, Tapa, among others.

## hc_09 · Eastern Bight

- macro: West Africa
- page: 15–16
- flags: CROSS_PAGE
- ethnonyms: Fang, Efik, Ijaw, Tiv, Igala, Carabali
- hyphen-joins (verify — some are real hyphens): Formoso

Eastern Bight refers to the interior of the Bight of Biafra and incorporates the central and eastern Niger Delta and Cross River region northward to the Benue River. Geographically, the coastal boundary extends from Cape Formoso to Cape St. John in modern-day Equatorial Guinea. We, however, limit its extent to a point south of Douala in modern-day Cameroon because it conforms to patterns in slave ship departures. There was little slave-trading activity to the south of Doula, which include peoples associated with Bantu languages of West Central Africa. In terms of the trans-Atlantic slave trade, Igbo and Ibibio supplied most of the enslaved to the coast. Other ethnonyms included Fang, Efik, Ijaw, Tiv, Igala, among others; and various people on the interior grasslands north of Mount Cameroon. The three main slave ports were Bonny, Calabar, and Elem Kalabari. In the Americas, people were mostly designated Carabali.

## hc_06 · Forests

- macro: West Africa
- page: 14–15
- flags: CROSS_PAGE
- ethnonyms: Bete, Gouro, Kissi, Kru
- hyphen-joins (verify — some are real hyphens): ecosystem

Forests refers to an area that comprises a seasonal tropical forest ecosystem, which are protected rainforests in modern-day Liberia and Cote d’Ivoire. Slave traders knew this region as the “Windward Coast,” which included sub-sections they variously called the Grain, Ivory, Kru, and Quaqua coasts. Despite many types of rainforests on the continent, we elected to use this simplified, neutral terminology to distinguish it from the much larger equatorial rainforest in the central interior. This forest is distinguished as a principal source of kola nuts traded into the savanna. Our proposed coastal boundaries stretch from Cape Mesurado to the Bandama River, and beyond Cape Lahou toward Grand Bassam. Key ethnonyms included Bete, Gouro, Kissi, Kru, and others sometimes classified as Mandingo more broadly, or Ganga in Cuba.

## hc_67 · Gulf Islands

- macro: West Africa
- page: 16
- flags: none
- ethnonyms: 

Gulf Islands are part of a line of volcanoes emerging offshore from modern-day Cameroon. They include Anobom, Fernando Po (now Bioko), Príncipe, and São Tomé. As stopping points for slave traders, these islands had connections with both West and West Central Africa. To maintain cohesion with Voyages, we include these two island clusters in West Africa.

## hc_05 · Rivers

- macro: West Africa
- page: 14
- flags: LONG
- ethnonyms: Baga, Balanta, Biafada, Bijago, Brame (Bran), Bullom, Diola, Mende, Nalu, Papel, Susu, Temne, Vai
- hyphen-joins (verify — some are real hyphens): characterize, kilometers, interior, Corubal

Rivers is an awkward way to refer to an African sub-region since there are rivers everywhere on the continent, but due to a lack of alternative names, we use it to replace “Upper Guinea Coast.” Of the people we consulted, some thought it formed part of the western savanna, but we elected to keep it separate due to its association with the Atlantic slave trade which is arguably distinct from Senegambia networks. Some slave traders referred to this area as the “Rivers of Guinea.” While we seek to avoid using slave trading terms, we felt that “Upper Coast” referred more closely to Africa’s northwest, while “Rivers” was still neutral enough despite its sordid historical connections. In addition, Boubacar Barry defined it as “Southern Senegambia” or “Southern Rivers region,” which relate to the noticeable riverine systems that characterize this area. At mangrove swamps along the coast, rivers meet tidal incursions, while rapids descend from a plateau rising a few hundred kilometers inland; and the terrain rises further again to the Futa Jallon highlands. Moreover, heavier rains occur in lower elevation areas, which provide a distinctive ecosystem where rice cultivation predominated and whose interior supplied slaves into the savanna and Atlantic world. Before the era of the Atlantic slave trade, the Mali empire likely incorporated large sections of this sub-region into its southern territorial possessions. The coastline spans from the Casamance River to about Cape Mesurado. Key rivers include the Corubal, Geba, Nuñez, Pongo, and Sierra Leone. Embarkation points for the enslaved consisted of the Bissau, Bunce Island, Cacheu, Gallinhas, Îles de Los, Nuñez, Pongo, and Sherbro. Ethnolinguistic groups included Baga, Balanta, Biafada, Bijago, Brame (Bran), Bullom, Diola, Mende, Nalu, Papel, Susu, Temne, and Vai. By the late eighteenth century, this area was a receiving zone of enslaved Africans, when Freetown absorbed an estimated 100,000 Africans and their descendants, who came from Nova Scotia following the American Revolutionary War, and then directly from West and West Central Africa during the British campaign to abolish slavery after 1807.

## hc_07 · Voltaic

- macro: West Africa
- page: 15
- flags: none
- ethnonyms: Akan, Akwamu, Fante
- hyphen-joins (verify — some are real hyphens): encompassing, Christiansborg, Americas

For lack of a better term, we use Voltaic to describe the basin encompassing the Black, Red, and White Volta rivers, which extend into the interior as far as modern Burkina Faso. The area also includes the Comoé River valley, which flows into the Atlantic at Grand Bassam through a lagoon system near Abidjan. Due to the gold and slave trade, dozens of fortified castles dotted the coastline, such as at Elmina, Cape Coast, Anomabu, Koromantse, Christiansborg, among others. Besides gold and slaves, the area was important for kola production. In the early eighteenth century, the Asante kingdom emerged, dominated the region, and controlled the slave trade until colonization. Ethnonyms included Akan, Akwamu, Fante, among others; and in the Americas, people consisted of Cormanti, Mina, and Popo. The bights found in the Gulf of Africa extend northward into two recognizable sub-regions from the Atakora mountains to the Adamawa Plateau and grasslands of Cameroon; and refers to an area to the east and west of the Niger-Benue confluence in the lower Niger valley. Except for their relative location west and east of the confluence, we realize “bight” is more seaward facing than not, but we could not find easy alternates.

## hc_08 · Western Bight

- macro: West Africa
- page: 15
- flags: none
- ethnonyms: Lucumi, Nago, Aku, Arará, Mina
- hyphen-joins (verify — some are real hyphens): contemporary

Western Bight typically conflates onto the “Slave Coast,” which in contemporary European sources described the section of coast and lagoons between Little Popo and Lagos, including Ouidah, Porto Novo, among others. In a broader sense, it extends from the Volta River eastward to the western Niger River delta and was bounded by the Atakora Mountains in the west; and in the east by the Niger River below the Benue confluence. This highly populated region included the kingdoms of Allada and later Dahomey, along with Yoruba-speaking states, such as Ife, Ijebu, Oyo, among others. It also includes the southern Borgu and Nupe; and peoples who spoke Gbe, the most widespread being Ewe and Fon. Toward the Niger delta was the kingdom of Benin, among other groups in the Niger Delta, such as Isoko, Warri, among many others. Major ethnonyms across the Atlantic included Lucumi, Nago, Aku, Arará, and Mina.

## hc_04 · Western Savanna

- macro: West Africa
- page: 13
- flags: none
- ethnonyms: Mandingo, Mandinga, Mandinka, Susu
- hyphen-joins (verify — some are real hyphens): commercial, Mandinga

Western Savanna is anchored in the Fuuta Jalon highlands, which are the source of the Niger, among other rivers extending eastward to the inner Niger River Delta. It is also the source of the Senegal and Gambia Rivers, which flowed toward Gorée, St. Louis, among other key slave trading forts. This expansive territory extends northward to the cities from the ancient kingdom of Wagadu/Ghana; and eastward across the Sahel beyond the Niger River Bend to include Gao, which has been an historically important commercial and political center, especially when the Sahel’s vegetation extended further north before desertification. The bulk of this territory was formerly the center of Mali and was later incorporated into Songhay, which collapsed in the 1590s, after which the Bambara states of Segu and Kaarta dominated the region. The area was largely Muslim and witnessed the earliest jihads in West Africa spanning the late seventeenth century through the nineteenth centuries. In the Americas enslaved people identified as Mandingo or Mandinga, that is, Mandinka, although others were referred to as Bambara (Bamana) who were not generally considered to be Muslims but spoke the same language. Other ethnolinguistic groups include Susu, as well as pastoral Fulbe, who are known locally as Ful, Fula, or Peul.

## hc_17 · Rainforest

- macro: West Central Africa
- page: 17–18
- flags: CROSS_PAGE
- ethnonyms: Aduma, Bobangi, Nunu, Okande
- hyphen-joins (verify — some are real hyphens): subregion

The equatorial Rainforest comprises the enormous watershed of the Congo River and its tributaries. The Ubangi and Uele Rivers frame the north and around the Kasai River in the south. In the east it touches the Atlantic from south of Douala to above Cape Lopez, in modern-day Cameroon and Gabon, respectively. Only small numbers of slaves originating from this subregion went into Atlantic networks in the early sixteenth century, and when they did, they were usually brought from the middle Congo River by Tio middlemen through the Kongo kingdom. By the eighteenth century, the rainforest became a major source of enslaved people via networks of Bobangi merchants, who transported people from as far as the upper Congo bend. Ethnonyms included Aduma, Bobangi, Nunu, and Okande.

## hc_22 · Southern Savanna

- macro: West Central Africa
- page: 18
- flags: none
- ethnonyms: Bisa, Bemba, Imbangala, Soso, Vili, Yaka, Zombo
- hyphen-joins (verify — some are real hyphens): northern

Southern Savanna extends from the rainforests southward as far as the Zambezi River. The Kwango and upper Kwanza rivers form its western border, while the east extends to around Lake Malawi. Its northern border resides along the rainforest and eastward as far as the Great Lakes. This sub-region includes lakes Bangwela, Kisale, and Mweru. The southern end lies around the copper belt, which spans the modern-day border between northern Zambia and Democratic Republic of Congo. Kingdoms include Kazembe, Luba, Lunda, and Luyana/Lozi. Captives acquired in war or tribute were sold to Imbangala and Yaka intermediaries supplying the northern ports of West Central Africa, while Luba sent captives to Atlantic ports and to the Indian Ocean. Ethnonyms included Bisa, Bemba, Imbangala, Soso, Vili, Yaka, and Zombo.

## hc_45 · St. Helena

- macro: West Central Africa
- page: 18
- flags: none
- ethnonyms: 

St. Helena, which is over 3,000 kilometers from the mainland in the southern Atlantic, had historical connections with South Atlantic trade, especially following British abolition after 1807. To maintain cohesion with Voyages, we include St. Helena in West Central Africa, although there are equally deep connections to southern Africa and the Indian Ocean world.

## hc_23 · West Central North

- macro: West Central Africa
- page: 16–17
- flags: LONG, CROSS_PAGE
- ethnonyms: Angola, Hako, Kakongo, Kalandula, Kongo, Libolo, Matamba, Mboma, Muburi, Ndembu, Ndongo, Ngoyo, Njinga, Songo, Dongo, Teke, Vungu, Yaka
- hyphen-joins (verify — some are real hyphens): Kimbundu

West Central North incorporates the stretch of coast from Cape Lopez at the Gabon estuary to the Kwanza River basin, including some areas to the south of the river depending on the time period. This southern border is very fluid. The sub-region is more or less anchored on the Kongo kingdom, but includes the Mayombe region too. Other kingdoms included: Bengo, Bolia, Loango, Kakongo, Loge, Ngoyo, Ndongo, Matamba, Kassanje, among other smaller ones. People from this sub-region mostly spoke Kikongo and Kimbundu, but the degree of cultural and linguistic unity is unclear. Dense rainforest and northern Congo River tributaries characterize this area, and it includes the Malebo Pool. It extends as far east as Lake Mai Ndombe, which was the border with Lunda and a major commercial zone to the lower reaches of the Kasai River. The eastern border is shaky because the Lunda empire expanded westward to incorporate the Yaka kingdom. The eastern border falls along the Kwango River and extends southward along the flat highlands of the Songo and Kuba regions. The southernmost border is at the northern edge of the central Angolan highlands. The main Atlantic ports include: Cape Lopez, Mayumba, Kilongo River, Loango, Cabinda, Congo River, Ambriz, and Luanda. In the Americas, Congo sub-groups included Angola, Hako, Kakongo, Kalandula, Kongo, Libolo, Matamba, Mboma, Muburi, Ndembu, Ndongo, Ngoyo, Njinga, Songo, Dongo, Teke, Vungu, Yaka, among many more. It should be noted that Kasanje, who reside in this sub-region, mostly entered Atlantic network via the eastern side of the central highlands and Benguela.

## hc_24 · West Central South

- macro: West Central Africa
- page: 17
- flags: none
- ethnonyms: Benguela, Bihe (Viye), Ciyaka, Fende, Hanya, Kakonda, Kilengues, Kingolo, Kipeyo, Kitata, Nano, Ndombe, Nganguela, Mocoando, Mocorocas, Mucuancalas, Sokoval, Wambu
- hyphen-joins (verify — some are real hyphens): highlands, distinction, reorganize

West Central South includes the region from the central Angolan highlands to the towns of Huila and Moçamedes, formerly Namibe, on the northern fringes of the Kalahari and Namib deserts. A geographic distinction is the “rough highlands” closer to the coast and “flat highlands” on the broad plains to the east. Kisama, who organized into smaller political units and decentralized societies, resided on the south side of the Kwanza river. In the seventeenth century, Bembe and Mujumbo dominated the region. By the early eighteenth century, centralized and militarized states started to reorganize, such as Bihe, Kakonda, Mbailundu, and Wambu. Sources refer to Khoe and Kung groups in the south, while Ovimbundu emerged by the end of the nineteenth century. The key port was Benguela and key ethnonyms included: Benguela, Bihe (Viye), Ciyaka, Fende, Hanya, Kakonda, Kilengues, Kingolo, Kipeyo, Kitata, Nano, Ndombe, Nganguela, Mocoando, Mocorocas, Mucuancalas, Sokoval, Wambu, among others.

---

## Appendix — broad-region lead-in text

_Context between a broad-region heading and its first subregion. Not a map feature; here so the review can see boundary language that belongs to the first child region._

### North Africa

- page: 8

This broad region includes the northern-most territories of the continent from the Atlantic along the shores of the Mediterranean to the Nile Valley. From our previous attempts, we have made substantial revisions to this broad region based on the separation of the Sahara desert, dividing the northern coast into two areas, adjusting boundaries of the Nile valley; and adding the Sinai Peninsula, and Canary Islands.

### Saharan Africa

- page: 11

In the 2019 article, we had grouped the world’s largest desert into North Africa. However, the Sahara is a vast region unto itself and represents about a quarter of the entire continent’s total land mass. It can be split in two for organizing data related to trans-Saharan trade.

### West Africa

- page: 12–13

This broad region incorporates much of Curtin’s coastal distribution for aggregating trans-Atlantic slave trade data from around the Senegal River southward to the Bight of Biafra; and includes Cabo Verde and Gulf islands. Our labels, for the most part, maintain a short character limit for timeconsuming data entry processes. It has been difficult to determine neutral terms for sub-regions of West Africa everyone might easily agree upon. In fact, it was far simpler to identify terms we did not want to use, such as “Guinea,” which was of Amazigh origins. Since 1140, az-Zuhri, an Arab historian, used Janawa to refer to a “land of the blacks,” and whose capital was Ghana. In Tamazight, “land of the blacks” translates as akal n-guinamen (sing. aguinaw), which is synonymous with bilad as-sudan. In Sanhaja, the root word gnw means “black”; and in Zenaga, Guinawn (sing. Ignwi) means Serer and Wolof in particular. In Tuareg, iguinawin means a “mass of dark clouds.” Since the fourteenth century when the Iberian peninsula was occupied by Africans, the Portuguese adopted and mapped the term pervasively to refer to the continent; and by the fifteenth century in Rome, al-Ḥasan ibn Muhammad _ al-Wazzaˉn al-Faˉsī used the words “Jinni” and “Jenne” interchangeably with “Guinea” and “Djenné,” a former kingdom and city located on a tributary of the Niger River, now present-day Mali. Today, three modern-day countries use the term too. In the Americas, “Guiné” generally identified enslaved people as coming from anywhere in Africa. In a similar vein, we have eliminated usages of “Windward” and “Gold Coast,” which were longstanding slave trading terms describing stretches of coastline; the former being windward of the later and where Europeans built forts for the gold and slave trades. Likewise, “Benin” causes confusion because it was a kingdom at the western end of the Niger delta and now a country to the west of Nigeria with historical roots in Dahomey. “Biafra” was the name given to a territory in Nigeria that attempted to assert its independence in the Nigerian civil war (1967–1970); and modern-day Senegal and the Gambia creates misunderstandings about “Senegambia.” Therefore, amendments of the broad West African sub-regions have required deeper contemplation and finding a more neutral nomenclature, which is difficult. Again, we neither assume everyone will agree on these terms, but we could not easily devise alternatives.

### West Central Africa

- page: 16

This broad region is predominately Bantu in terms of linguistic identification. The area covers Angola, Republic of Congo, Democratic Republic of the Congo, Central African Republic, southern Gabon and eastward to Zambia. Nearly half of all enslaved people in the transatlantic slave trade, or approximately 5.7 million people, boarded slave ships at ports between the Gabon estuary and north of the Namib Desert. In most historical data, “Congo” or “Angola” were common, but these designations suggest nothing more than an individual originated somewhere in this broader region and must be treated as such. However, there are a vast array of other ethnonyms and designations associated with the region. Amendments from our earlier map involved amalgamating most of the “Loango Coast” into the equatorial rainforest, eliminating usages of “Kwanza North” and “Kwanza South” which are modern-day provinces in Angola, and dividing the large “Central Interior” into two distinct sub-regions.

### East Africa

- page: 18–19

This broad region is interconnected with the cyclical monsoons of the Indian Ocean world, as well as Atlantic networks. Voyages datasets oversimplify this broad region as “Southeast Africa and Indian Ocean Islands.” It relates to the modern-day countries of Burundi, Djibouti, Kenya, Madagascar, Malawi, Rwanda, Somalia, South Sudan, Tanzania, and Uganda, as well as parts of the Democratic Republic of Congo, Ethiopia, Mozambique, and Zambia. The coastal belt begins approximately at the Bab-el-Mandeb Strait in the Horn and stretches to the Zambezi River. Revisions from 2019 include dividing the horn into two, shrinking boundaries around the Great Lakes, and including Madagascar and the southwest Indian Ocean islands and archipelagos.

### Southern Africa

- page: 21

The southern continental cone begins at the northern Kalahari Desert around the Cape of Good Hope until the Zambezi River. It relates to modern-day Botswana, Lesotho, Namibia, South Africa, Swaziland, and Zimbabwe, as well as parts of Angola, Mozambique, and Zambia. Except for Cape Town and around Maputo Bay, most of the coast was sparsely populated until Inhambane, which sent captives to the Mascarenes and the Americas in the late eighteenth and early nineteenth centuries. The Kalahari and Namib deserts had low populations. Amendments to the map include dividing the grasslands into two sub-regions and shifting the northern section of the southeast coast into a new, southcentral region.
