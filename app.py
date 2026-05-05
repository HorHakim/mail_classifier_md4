import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time
from agent_mail import classify_mail
from mail_reader import read_mails_from_gmail

st.set_page_config(page_title="Classificateur de mails", page_icon="📧", layout="wide")

st.title("📧 Classificateur de mails")
st.markdown("Analyse et classe vos emails par **urgence** et **importance** grâce à l'IA.")

# --- Sidebar : paramètres ---
with st.sidebar:
    st.header("Paramètres")

    start_date = st.date_input("Date de début", value=datetime(2025, 11, 16).date())
    start_time = st.time_input("Heure de début", value=time(0, 0))

    end_date = st.date_input("Date de fin", value=datetime(2025, 11, 18).date())
    end_time = st.time_input("Heure de fin", value=time(23, 59))

    start_datetime = datetime.combine(start_date, start_time)
    end_datetime = datetime.combine(end_date, end_time)

    if start_datetime >= end_datetime:
        st.error("La date de début doit être antérieure à la date de fin.")
        st.stop()

    lancer = st.button("🚀 Lancer la classification", use_container_width=True)

# --- Zone principale ---
if lancer:
    with st.spinner("Récupération des emails depuis Gmail…"):
        try:
            emails = read_mails_from_gmail(start_datetime, end_datetime)
        except Exception as e:
            st.error(f"Erreur lors de la lecture des emails : {e}")
            st.stop()

    if not emails:
        st.warning("Aucun email trouvé pour cette période.")
        st.stop()

    st.info(f"{len(emails)} email(s) récupéré(s). Classification en cours…")

    progress_bar = st.progress(0, text="Classification…")
    status_text = st.empty()

    emails_urgence = []
    emails_importance = []

    for i, email in enumerate(emails):
        status_text.text(f"Email {i + 1} / {len(emails)}")
        try:
            classification = classify_mail(email)
            emails_urgence.append(classification.get("urgence", 0))
            emails_importance.append(classification.get("importance", 0))
        except Exception as e:
            st.warning(f"Erreur sur l'email {i + 1} : {e}")
            emails_urgence.append(None)
            emails_importance.append(None)
        progress_bar.progress((i + 1) / len(emails), text=f"Email {i + 1} / {len(emails)}")

    status_text.empty()
    progress_bar.empty()

    df = pd.DataFrame({
        "id": range(len(emails)),
        "email": emails,
        "urgence": emails_urgence,
        "importance": emails_importance,
    })

    csv_name = f"emails_classification_{start_datetime:%Y-%m-%d}.csv"
    df.to_csv(csv_name, index=False)

    st.success(f"Classification terminée ! Résultats sauvegardés dans `{csv_name}`.")

    # --- Statistiques ---
    st.subheader("Statistiques")
    col1, col2, col3 = st.columns(3)
    col1.metric("Emails analysés", len(df))
    col2.metric("Urgence moyenne", f"{df['urgence'].mean():.1f} / 100")
    col3.metric("Importance moyenne", f"{df['importance'].mean():.1f} / 100")

    # --- Graphique ---
    st.subheader("Carte urgence / importance")
    fig = px.scatter(
        df,
        x="urgence",
        y="importance",
        hover_data={"email": True, "id": True},
        color="urgence",
        color_continuous_scale="RdYlGn_r",
        range_x=[0, 100],
        range_y=[0, 100],
        labels={"urgence": "Urgence", "importance": "Importance"},
    )
    fig.add_hline(y=50, line_dash="dot", line_color="grey")
    fig.add_vline(x=50, line_dash="dot", line_color="grey")
    fig.update_traces(marker=dict(size=12))
    st.plotly_chart(fig, use_container_width=True)

    # --- Tableau ---
    st.subheader("Tableau des résultats")

    def color_score(val):
        if val is None:
            return ""
        if val >= 75:
            return "background-color: #f28b82"
        if val >= 50:
            return "background-color: #fbbc04"
        return "background-color: #81c995"

    df_display = df[["id", "urgence", "importance", "email"]].copy()
    df_display["email"] = df_display["email"].str[:200] + "…"

    styled = df_display.style.applymap(color_score, subset=["urgence", "importance"])
    st.dataframe(styled, use_container_width=True)

    # --- Téléchargement ---
    st.download_button(
        label="⬇️ Télécharger le CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=csv_name,
        mime="text/csv",
    )

else:
    st.info("Configurez la plage de dates dans le panneau latéral, puis cliquez sur **Lancer la classification**.")
