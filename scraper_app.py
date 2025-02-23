import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get
import streamlit.components.v1 as components

# --- Configuration de la page avec un titre neutre et moderne ---
st.set_page_config(page_title="Smart Fashion Scraper", page_icon=":bar_chart:", layout="wide")


# --- Fonction pour définir un fond d'écran en dégradé neutre et fixer la couleur du texte ---
def set_background():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(to top, #090909, #0c0c0c);
            background-attachment: fixed;
        }
        .stApp * {
            color: #ffffff;  /* Texte en noir pour un meilleur contraste */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

set_background()

# --- En-tête principal ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Caveat&display=swap');
    h1 {
        font-family: 'Caveat', cursive !important;
        color: #1a5276 !important;  /* Couleur plus foncée pour un meilleur contraste */
        text-align: center;
        font-size: 70px !important;
    }
    </style>
    <h1>
        Smart Fashion Scraper
    </h1>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style='text-align: center; font-size: 16px;'>
       This application scrapes data on men's clothing and footwear from CoinAfrique.
       It retrieves variables such as type of clothing, price, address, and image link.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("""
* **Python libraries:** base64, pandas, streamlit, requests, bs4
* **Data source:** [CoinAfrique (vetements hommes)](https://sn.coinafrique.com/categorie/vetements-homme) -- [CoinAfrique (chaussures hommes)](https://sn.coinafrique.com/categorie/chaussures-homme)
""")
# --- Navigation multi-pages dans la sidebar ---
page_option = st.sidebar.selectbox("Select Page", ["Data Scraping", "KoboToolbox Form", "Google Form"])

if page_option == "Data Scraping":
    with st.sidebar:
        st.markdown("<h2 style='color: #1a5276;'>Scraping Options</h2>", unsafe_allow_html=True)
        scrape_method = st.radio(
            "Choose scraping method:",
            ("Cleaned Data (BeautifulSoup)", "Raw Data (Web Scraper)")
        )
        num_pages = st.number_input("Select number of pages to scrape (max 119)", min_value=1, max_value=119, value=10, step=1)

    # --- Fonction pour convertir un DataFrame en CSV ---
    @st.cache_data
    def convert_df(df):
        return df.to_csv().encode("utf-8")

    # --- Fonction pour afficher les données avec un bouton de téléchargement ---
    def display_data(df, title, key):
        st.subheader(title)
        st.write("Data dimensions: {} rows and {} columns.".format(df.shape[0], df.shape[1]))
        st.dataframe(df, use_container_width=True)
        csv = convert_df(df)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f"{title.replace(' ', '_')}.csv",
            mime="text/csv",
            key=key,
        )

    # --- Fonction générique pour scraper les données ---
    def load_data(category, num_pages):
        """
        Scrape les données pour une catégorie donnée (vêtements ou chaussures).
        :param category: La catégorie à scraper ("vetements-homme" ou "chaussures-homme").
        :param num_pages: Le nombre de pages à scraper.
        :return: Un DataFrame contenant les données scrapées.
        """
        df = pd.DataFrame()
        for i in range(num_pages):
            url = f"https://sn.coinafrique.com/categorie/{category}?page={i}"
            try:
                code_html = get(url)
                soup = bs(code_html.text, 'html.parser')
                containers = soup.find_all("div", class_="col s6 m4 l3")
                data = []
                for container in containers:
                    try:
                        type_item = container.find("p", class_="ad__card-description").text
                        prix = container.find("p", class_="ad__card-price").text.replace("CFA", "")
                        adresse = container.find("p", class_="ad__card-location").text.replace("location_on", "")
                        img_link = container.find('img', class_="ad__card-img")['src']
                        dic = {
                            'type_item': type_item,
                            'prix': prix,
                            'adresse': adresse,
                            'img_link': img_link
                        }
                        data.append(dic)
                    except Exception as e:
                        st.error(f"Erreur lors de l'extraction des données : {e}")
                DF = pd.DataFrame(data)
                df = pd.concat([df, DF], axis=0).reset_index(drop=True)
            except Exception as e:
                st.error(f"Erreur lors du scraping de la page {i} : {e}")
        return df

    # --- Fonctions spécifiques pour les vêtements et les chaussures ---
    def load_clothes_data(num_pages):
        """
        Scrape les données de vêtements pour hommes et renomme la colonne 'type_item' en 'habits'.
        """
        df = load_data("vetements-homme", num_pages)
        df = df.rename(columns={'type_item': 'type_habits'})  # Renommer la colonne
        return df

    def load_shoes_data(num_pages):
        """
        Scrape les données de chaussures pour hommes et renomme la colonne 'type_item' en 'chaussures'.
        """
        df = load_data("chaussures-homme", num_pages)
        df = df.rename(columns={'type_item': 'type_chaussures'})  # Renommer la colonne
        return df

    # --- Fonctions pour charger les données brutes (raw data) ---
    def load_raw_clothes_data():
        """
        Charge les données brutes de vêtements d'hommes.
        Exemple : lecture d'un fichier CSV.
        """
        df_v = pd.read_csv("coinafrique_habits.csv")
        return df_v

    def load_raw_shoes_data():
        """
        Charge les données brutes de chaussures d'hommes.
        Exemple : lecture d'un fichier CSV.
        """
        df_c = pd.read_csv("coinafrique_chaussures.csv")
        return df_c

    # --- Affichage selon la méthode choisie ---
    if scrape_method == "Cleaned Data (BeautifulSoup)":
        st.markdown("<h2 style='text-align: center; color: #1a5276;'>Scraping Cleaned Data</h2>", unsafe_allow_html=True)
        df_vet = load_clothes_data(num_pages)  # Données nettoyées pour les vêtements
        df_ch = load_shoes_data(num_pages)     # Données nettoyées pour les chaussures
        # Affichage l'un au-dessus de l'autre
        display_data(df_vet, "Men's Clothing Data", "clothes")
        display_data(df_ch, "Men's Footwear Data", "shoes")
        
    elif scrape_method == "Raw Data (Web Scraper)":
        st.markdown("<h2 style='text-align: center; color: #1a5276;'>Download Raw Data</h2>", unsafe_allow_html=True)
        raw_clothes_df = load_raw_clothes_data()  # Base de données brute pour les vêtements
        raw_shoes_df = load_raw_shoes_data()      # Base de données brute pour les chaussures
        # Affichage l'un au-dessus de l'autre
        display_data(raw_clothes_df, "Raw Men's Clothing Data", "raw_clothes")
        display_data(raw_shoes_df, "Raw Men's Footwear Data", "raw_shoes")

elif page_option == "KoboToolbox Form":
    st.markdown("<h2 style='text-align: center; color: #1a5276;'>KoboToolbox Form</h2>", unsafe_allow_html=True)
    components.html(
        """
        <iframe src="https://ee.kobotoolbox.org/i/y3pfGxMz" width="100%" height="600"></iframe>
        """,
        height=600,
        scrolling=True
    )

elif page_option == "Google Form":
    st.markdown("<h2 style='text-align: center; color: #1a5276;'>Google Form</h2>", unsafe_allow_html=True)
    components.html(
        """
        <iframe src="https://forms.gle/CeUo3e7aA3F417Lp8" width="100%" height="600"></iframe>
        """,
        height=600,
        scrolling=True
    )

