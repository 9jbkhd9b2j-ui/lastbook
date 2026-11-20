# Mapas detalhados para o Brasil: uma proposta

Esta é uma proposta para discussão, não uma decisão. Ela responde, para o Brasil, as perguntas que [MAPS.md](MAPS.md)
faz antes de a cobertura poder ir além dos Estados Unidos: qual fonte aberta substitui cada lista federal, sob qual
licença, o que é um "estado" ali e como os endereços são escritos. Segue a estrutura de
[REGIONS-MX.md](REGIONS-MX.md) e [REGIONS-AR.md](REGIONS-AR.md) e busca alimentar a mesma discussão de desenho (issues
#23, #25, #31 e #54). A versão legível por máquina é [regions-br-proposed.json](regions-br-proposed.json), e a versão
em inglês, que é a referência, é [REGIONS-BR.md](REGIONS-BR.md).

Nada aqui muda o aplicativo, o motor ou uma compilação. Nenhum código lê o JSON, e nada disto é empacotado: as
compilações só empacotam `web/` e `content/`.

**Como foi verificado.** A pesquisa foi feita em 20 de novembro de 2026. Cada fonte tem uma de três marcas:

- **aberta**: o conjunto de dados ou a página de licença foi aberta e lida;
- **só busca**: o fato apareceu em um resultado de busca ou trecho de busca, mas a página não foi aberta;
- **não verificada**: a página não pôde ser acessada ou lida, ou não foi examinada nesta proposta; a linha diz o que falta.

As caixas dos estados foram calculadas a partir dos próprios polígonos estaduais do IBGE, lidos pela API pública de
malhas do IBGE (aberta). A licença desses polígonos **não** está resolvida (veja "Notas sobre licença"), então as caixas
são uma proposta até que isso seja resolvido.

## Por que o Brasil é um caso útil

O Brasil tem um esquema nacional próprio de números de emergência (190, 192, 193 e 199, veja "Pontos de ajuda"), e seus
estados usam códigos de duas letras que, em um caso, coincidem com códigos dos EUA neste repositório. Não foi verificada
nesta proposta uma camada aberta de áreas de CEP. Duas coisas são diferentes dos EUA e vale decidi-las uma vez, porque
outros países de língua portuguesa e espanhola vão levantar o mesmo ponto:

- **Códigos de duas letras coincidem com códigos dos EUA.** Sete códigos brasileiros também são códigos de estado dos EUA
  em `STATE_CODES` (`engine/address_search.py`). É o principal motivo dos códigos com hífen abaixo.
- **Sem tabela CEP-estado verificada.** O CEP de oito dígitos é o que a busca de endereços precisa, mas nenhuma tabela
  oficial CEP-estado foi verificada, então os endereços ainda não podem ser separados por estado.

## O que é uma região

O Brasil tem 26 estados e o Distrito Federal (DF). A proposta é uma região por unidade, 27 no total, no mesmo nível de um
estado dos EUA. O DF é uma unidade federativa com governo próprio, então aqui ele é uma região separada; veja a nota
sobre DF e Goiás abaixo.

### Códigos

A ISO 3166-2:BR dá a cada unidade o prefixo `BR-` e duas letras: `BR-SP` São Paulo, `BR-RJ` Rio de Janeiro, `BR-DF`
Distrito Federal, e assim por diante (não conferido no site da ISO, como as outras propostas também observam para seus
códigos).

- **Sete códigos de duas letras coincidem com códigos dos EUA.** Os códigos brasileiros `AL` (Alagoas), `MA` (Maranhão),
  `MS` (Mato Grosso do Sul), `MT` (Mato Grosso), `PA` (Pará), `PR` (Paraná) e `SC` (Santa Catarina) também estão em
  `STATE_CODES` (`engine/address_search.py`), para Alabama, Massachusetts, Mississippi, Montana, Pensilvânia, Porto Rico
  e Carolina do Sul. Um `PA` sozinho já significa Pensilvânia na busca de endereços. Um `PA` brasileiro seria lido do
  mesmo jeito, então os códigos brasileiros não podem ser usados sozinhos.
- **O código com hífen também é necessário para o nome do arquivo.** `carry_over()` em `engine/setup/install.py` mantém
  só os índices de endereço com nome `[A-Z]{2}.sqlite` ou `.json` (linha 335). Um índice chamado `BR-SP.sqlite` ficaria
  para trás na biblioteca antiga, sem aviso, como o REGIONS-MX.md também observa para `MX-AGU`. Mudar `carry_over` seria
  uma decisão dos mantenedores.

### Caixas

As caixas foram calculadas a partir dos polígonos estaduais do IBGE (malhas territoriais, camada estadual, "malha
estadual"), lidos pela API pública de malhas do IBGE na qualidade máxima (`qualidade=maxima`) em 20 de novembro de 2026
(aberta). A API devolve uma feição por unidade: 27 feições, com de 1 a 17 polígonos cada (o Pará tem 17, e o Rio de
Janeiro, 15). Cada vértice de cada polígono foi lido; a caixa foi então alargada em 0,15° e arredondada para fora em
0,01°, a mesma margem que `map_sets.state` usa para estados dos EUA.

Como conferência, as bordas externas batem com os extremos conhecidos do Brasil, lembrados de memória (não conferidos
contra uma lista publicada nesta etapa): o extremo norte de Roraima (cerca de 5,27° N), o extremo sul do Rio Grande do
Sul (cerca de 33,75° S), o extremo leste da Paraíba (cerca de 34,79° O) e a borda oeste do Acre (cerca de 73,99° O).
Essas quatro bordas são definidas por esses estados, e a tabela coincide com elas.

| Código | IBGE | Nome | Caixa (oeste, sul, leste, norte) | Caixa com margem de 0,15° |
|---|---|---|---|---|
| `BR-RO` | 11 | Rondônia | -66,8103, -13,6937, -59,7744, -7,9759 | -66,97, -13,85, -59,62, -7,82 |
| `BR-AC` | 12 | Acre | -73,9904, -11,1456, -66,6239, -7,1118 | -74,15, -11,30, -66,47, -6,96 |
| `BR-AM` | 13 | Amazonas | -73,8016, -9,8180, -56,0976, 2,2466 | -73,96, -9,97, -55,94, 2,40 |
| `BR-RR` | 14 | Roraima | -64,8253, -1,5806, -58,8869, 5,2718 | -64,98, -1,74, -58,73, 5,43 |
| `BR-PA` | 15 | Pará | -58,8983, -9,8412, -46,0618, 2,5910 | -59,05, -10,00, -45,91, 2,75 |
| `BR-AP` | 16 | Amapá | -54,8763, -1,2362, -49,8758, 4,5088 | -55,03, -1,39, -49,72, 4,66 |
| `BR-TO` | 17 | Tocantins | -50,7421, -13,4682, -45,6993, -5,1684 | -50,90, -13,62, -45,54, -5,01 |
| `BR-MA` | 21 | Maranhão | -48,7552, -10,2596, -41,7967, -1,0495 | -48,91, -10,41, -41,64, -0,89 |
| `BR-PI` | 22 | Piauí | -46,0282, -10,9288, -40,3705, -2,7499 | -46,18, -11,08, -40,22, -2,59 |
| `BR-CE` | 23 | Ceará | -41,4233, -7,8576, -37,2527, -2,7843 | -41,58, -8,01, -37,10, -2,63 |
| `BR-RN` | 24 | Rio Grande do Norte | -38,5821, -6,9827, -34,9685, -4,8314 | -38,74, -7,14, -34,81, -4,68 |
| `BR-PB` | 25 | Paraíba | -38,7652, -8,3030, -34,7932, -6,0259 | -38,92, -8,46, -34,64, -5,87 |
| `BR-PE` | 26 | Pernambuco | -41,3583, -9,4829, -32,3971, -3,8358 | -41,51, -9,64, -32,24, -3,68 |
| `BR-AL` | 27 | Alagoas | -38,2376, -10,4986, -35,1527, -8,8161 | -38,39, -10,65, -35,00, -8,66 |
| `BR-SE` | 28 | Sergipe | -38,2450, -11,5685, -36,3959, -9,5150 | -38,40, -11,72, -36,24, -9,36 |
| `BR-BA` | 29 | Bahia | -46,5768, -18,3372, -37,3411, -8,5328 | -46,73, -18,49, -37,19, -8,38 |
| `BR-MG` | 31 | Minas Gerais | -51,0461, -22,9228, -39,8568, -14,2333 | -51,20, -23,08, -39,70, -14,08 |
| `BR-ES` | 32 | Espírito Santo | -41,8796, -21,3011, -29,2990, -17,8919 | -42,03, -21,46, -29,14, -17,74 |
| `BR-RJ` | 33 | Rio de Janeiro | -44,8893, -23,3676, -40,9579, -20,7632 | -45,04, -23,52, -40,80, -20,61 |
| `BR-SP` | 35 | São Paulo | -53,1101, -25,3089, -44,1614, -19,7799 | -53,27, -25,46, -44,01, -19,62 |
| `BR-PR` | 41 | Paraná | -54,6199, -26,7171, -48,0235, -22,5163 | -54,77, -26,87, -47,87, -22,36 |
| `BR-SC` | 42 | Santa Catarina | -53,8371, -29,3551, -48,3585, -25,9558 | -53,99, -29,51, -48,20, -25,80 |
| `BR-RS` | 43 | Rio Grande do Sul | -57,6497, -33,7508, -49,6914, -27,0823 | -57,80, -33,91, -49,54, -26,93 |
| `BR-MS` | 50 | Mato Grosso do Sul | -58,1686, -24,0682, -50,9242, -17,1663 | -58,32, -24,22, -50,77, -17,01 |
| `BR-MT` | 51 | Mato Grosso | -61,6334, -18,0416, -50,2248, -7,3490 | -61,79, -18,20, -50,07, -7,19 |
| `BR-GO` | 52 | Goiás | -53,2485, -19,4981, -45,9072, -12,3954 | -53,40, -19,65, -45,75, -12,24 |
| `BR-DF` | 53 | Distrito Federal | -48,2857, -16,0500, -47,3085, -15,5018 | -48,44, -16,20, -47,15, -15,35 |

Notas:

- **DF dentro de Goiás.** A caixa do DF fica inteiramente dentro da caixa `BR-GO`, o mesmo caso de CABA dentro de Buenos
  Aires em REGIONS-AR.md. A região metropolitana de Brasília cruza a fronteira entre DF e Goiás, então quem mora ali e
  instala só um dos dois mapas perde parte da sua área. Opções: manter os dois mapas separados (simples), ou fazer o mapa
  `BR-GO` incluir `BR-DF` (acompanha como as pessoas se deslocam na região, como o REGIONS-AR.md sugere para CABA). Esta
  proposta não decide isso.
- **Caixas grandes.** Amazonas, Pará e Mato Grosso são as maiores caixas. Os mapas deles serão grandes, e o tamanho do
  download não foi estimado nesta proposta.
- **Fernando de Noronha** pertence a Pernambuco, e a caixa `BR-PE` vai até -32,40° O para incluí-la.
- **Caixas sobrepostas.** As caixas seguem o contorno de cada estado, então estados vizinhos se sobrepõem ao longo das
  fronteiras. A sobreposição é esperada e é a mesma dos EUA e do México.

## Fontes, camada por camada

| Camada (arquivo) | Fonte dos EUA hoje | Proposta para o Brasil | Publicador | Licença | Verificado |
|---|---|---|---|---|---|
| Relevo (`terrain.sqlite`) | USGS 3DEP | Copernicus DEM GLO-30, como alternativa em REGIONS-AR.md e REGIONS-MX.md; nenhum produto nacional de altitude específico do Brasil foi verificado aqui | ESA / Airbus | licença Copernicus | Copernicus como em REGIONS-AR.md; produto do Brasil não verificado |
| Água (`water.sqlite`) | NHD | Vias e áreas de água do OSM, do extrato do Brasil da Geofabrik; hidrografia do IBGE não verificada nesta proposta | colaboradores do OSM | ODbL | OSM como nos EUA; IBGE não verificado |
| Barragens | NID | Nenhuma lista nacional aberta de barragens foi identificada nesta etapa. `waterway=dam` do OSM como alternativa, não contada | colaboradores do OSM | ODbL | não verificado |
| Culturas (`crops.sqlite`) | USDA Cropland Data Layer | O MapBiomas é candidato, porque cobre as classes de cultivo do Brasil, mas a licença e a lista de classes não foram verificadas | MapBiomas | não verificada | não verificado |
| Edifícios (`buildings.sqlite`) | Microsoft, contornos dos EUA, alturas do OSM | Google Open Buildings V3, como em REGIONS-MX.md; cobertura do Brasil não reconferida aqui; OSM para preencher lacunas | Google; colaboradores do OSM | CC BY 4.0; ODbL | como em REGIONS-MX.md; não reaberta para o Brasil |
| Lugares (`places.sqlite`) | GNIS, gazetteers do Census, OSM | Malhas do IBGE para estados, municípios e localidades (a camada estadual foi usada para as caixas); lugares nomeados do OSM | IBGE; colaboradores do OSM | termos do IBGE pouco claros (veja Notas sobre licença); ODbL | camada estadual aberta; licença não confirmada |
| Endereços (`addresses/<código>.sqlite`) | endereços Overture | Endereços Overture do Brasil não foram contados nem verificados aqui; nenhuma tabela aberta de área de CEP foi encontrada | Overture Maps Foundation; Correios (CEP) | não verificada | não verificado |
| Pontos de interesse (linhas `poi`) | OSM | OSM, como hoje, mais as listas de "Pontos de ajuda" | colaboradores do OSM | ODbL | não contado aqui |

### Notas sobre licença

- **Conteúdo do gov.br.** O rodapé das páginas do gov.br diz que todo o conteúdo é publicado sob a *Creative Commons
  Atribuição-SemDerivações 3.0 Não Adaptada* (CC BY-ND 3.0 Brasil) (aberta; lida em 20 de novembro de 2026 na página
  "Sobre o portal" do gov.br e na página federal do SAMU). A parte "sem derivações" significa que uma página não pode ser
  adaptada para um guia da biblioteca, então as páginas do gov.br não são propostas como fonte de cópia. Citar um número
  único com a fonte é uma questão para os mantenedores, não uma decisão tomada aqui.
- **IBGE.** Nenhuma licença aberta explícita foi encontrada para as malhas. O IBGE publica uma nota técnica e legal com
  cada produto ("Informações técnicas e legais para a utilização dos dados publicados") (só busca, não aberta). Os termos
  da base cartográfica BC250 descrevem um uso restrito ao apoio a projetos de trabalho, não uma licença aberta (só busca,
  não aberta). Até que a nota da malha estadual seja lida, as camadas do IBGE **não são propostas para uma compilação**.
  As caixas deste arquivo são números calculados a partir dos dados e devem ser conferidas de novo contra a licença antes
  que alguém dependa delas.

## Pontos de ajuda

Os números de emergência são a parte de que as pessoas mais precisam, e são os mesmos no país inteiro. Eles são definidos
pela Anatel (o regulador de telecomunicações), não por cada estado.

| Serviço | Número | Fonte do número | Dados de localização |
|---|---|---|---|
| Ambulância (SAMU) | 192 | gov.br, "SAMU 192: saiba quando acionar o serviço de urgência", publicado em 29 de agosto de 2022, atualizado em 26 de outubro de 2026 (aberta) | não verificados |
| Incêndio (Corpo de Bombeiros) | 193 | Listagem da Anatel dos códigos de utilidade pública e emergência (só trecho de busca; a página da Anatel não mostrou os números quando lida) | serviços estaduais de bombeiros: não verificados |
| Polícia (Polícia Militar) | 190 | igual ao 193 (só trecho de busca) | polícia estadual: não verificada |
| Defesa civil (Defesa Civil) | 199 | igual ao 193 (só trecho de busca) | não verificados |

Notas:

- A designação desses códigos pela Anatel vem do ato de numeração de 2004 (só trecho de busca; a página do ato não foi
  encontrada no endereço retornado, então não foi lida).
- Estabelecimentos de saúde com coordenadas (o cadastro nacional, CNES) e postos de bombeiros ou polícia não foram
  verificados nesta proposta, então não há contagens para eles.
- A tabela de números em si pertence à [issue #261](https://github.com/Immortal-Protocols/lastbook/issues/261), não a esta
  proposta de mapa. Ela aparece aqui para que o mapa e a tabela de números coincidam.

## Como conferir uma mudança de mapa

- Uma mudança em uma camada de `web/map.js` é uma mudança visível: inclua capturas de tela no modo claro e escuro.
- Uma mudança em uma ferramenta de pacote ou de mapa: `packaging/test_pack_tools.py` e `packaging/scan_pack.py` conferem o
  que um conjunto de mapas pode ter, e `scan_pack.py` lista os arquivos permitidos em `derived/geo/` (`GEO_FILES`).
- Nada que um colaborador adicione pode fazer o aplicativo abrir uma conexão. Dados novos entram por uma ferramenta de
  compilação e chegam como arquivo.

## Perguntas em aberto para os mantenedores

1. **DF e Goiás:** mapas separados, ou o mapa de Goiás deve incluir o DF (como a proposta da Argentina sugere para CABA)?
2. **Códigos com hífen:** os códigos `BR-` devem virar nome de arquivo e de manifesto, e `carry_over` em
   `engine/setup/install.py` deve ser ampliado para aceitá-los (a mudança toca o caminho de atualização, então precisa de
   revisão)?
3. **Licença do IBGE:** a nota técnica da malha estadual permite copiar na compilação? Até ela ser lida, as caixas
   continuam sendo uma proposta.
4. **CEP:** existe fonte aberta para áreas de CEP no Brasil? Sem ela, a busca de endereços não separa por estado.
