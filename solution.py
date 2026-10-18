import os
import requests
from dotenv import load_dotenv
import folium  

# 1. Carrega as variáveis de ambiente do ficheiro .env
load_dotenv(".env")

# 2. Inicia a sessão HTTP e realiza a autenticação na API da SPTrans
s = requests.Session()
res = s.post(
    f"http://api.olhovivo.sptrans.com.br/v2.1/Login/Autenticar?token={os.getenv('SPTRANS_TOKEN')}"
)
print("Autenticação:", res.text)

# 3. Procura linhas com o termo "Lapa"
linhas_lapa = s.get(
    "http://api.olhovivo.sptrans.com.br/v2.1/Linha/Buscar?termosBusca=Lapa"
).json()

# 4. Procura as paragens da linha 2506
paradas = s.get(
    "http://api.olhovivo.sptrans.com.br/v2.1/Parada/BuscarParadasPorLinha?codigoLinha=2506"
).json()

# 5. Cria o mapa do UNASP (com tiles="Cartodb Positron" para evitar o erro 403)
m_unasp = folium.Map(
    location=[-22.8773542, -47.2280647],
    zoom_start=14,
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    attr="Esri",
)
folium.Marker(
    location=[-22.8773542, -47.2280647],
    popup=folium.Popup("Estudo aqui!", max_width=100, show=True)
).add_to(m_unasp)
m_unasp.save("unasp.html")

# 6. Define a localização inicial com base na primeira paragem (ou coordenada padrão caso esteja vazia)
if isinstance(paradas, list) and len(paradas) > 0:
    localizacao_inicial = [paradas[0]["py"], paradas[0]["px"]]
else:
    localizacao_inicial = [-23.550520, -46.633308]

# 7. Cria o mapa principal das paragens e autocarros
m = folium.Map(
    location=localizacao_inicial,
    zoom_start=14,
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    attr="Esri",
)

# Adiciona os marcadores das paragens (cor Laranja)
if isinstance(paradas, list):
    for parada in paradas:
        folium.Marker(
            location=[parada["py"], parada["px"]],
            popup=parada["np"],
            icon=folium.Icon(color="orange")
        ).add_to(m)

# 8. Consulta a posição em tempo real dos autocarros da linha 2506
pos_response = s.get(
    "http://api.olhovivo.sptrans.com.br/v2.1/Posicao/Linha?codigoLinha=2506"
)
pos_dados = pos_response.json()

# Adiciona os autocarros em tempo real (cor Vermelha com ícone de autocarro)
if isinstance(pos_dados, dict) and "vs" in pos_dados:
    for onibus in pos_dados["vs"]:
        folium.Marker(
            location=[onibus["py"], onibus["px"]],
            popup=f"Veículo: {onibus['p']}",
            icon=folium.Icon(color="red", icon="bus", prefix="fa")
        ).add_to(m)

# 9. Guarda o mapa final
m.save("mapa_sptrans.html")
print("Mapas 'unasp.html' e 'mapa_sptrans.html' gerados com sucesso!")
