import streamlit as st

def load_global_style():
    """
    Injects the Bauhaus / Constructivist CSS styles into the Streamlit app.
    Key elements: Geometric forms, Primary Colors (Red, Blue, Yellow), Bold Typography, Hard Edges.
    """
    st.markdown("""
        <!-- Google Fonts: Geometric Sans-Serif -->
        <link href="https://fonts.googleapis.com/css2?family=Jost:wght@400;700;900&family=Space+Grotesk:wght@300;500;700&display=swap" rel="stylesheet">
        <!-- FontAwesome (Minimal use) -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        
        <style>
        /* =============================================================================
           1. BAUHAUS COLOR PALETTE & TYPOGRAPHY
           ============================================================================= */
        :root {
            --bauhaus-red: #D02020;
            --bauhaus-blue: #1E5AA0;
            --bauhaus-yellow: #F0B000;
            --bauhaus-black: #111111;
            --bauhaus-white: #FFFFFF;
            --bauhaus-gray: #F4F4F4;
        }
        
        /* Global Reset */
        .stApp {
            background-color: var(--bauhaus-gray);
            color: var(--bauhaus-black);
            font-family: 'Jost', sans-serif;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            text-transform: uppercase;
            color: var(--bauhaus-black);
            letter-spacing: -1px; /* Tight tracking */
        }
        
        h1 {
            font-size: 3.5rem;
            border-bottom: 5px solid var(--bauhaus-black);
            padding-bottom: 10px;
            display: inline-block;
        }

        /* =============================================================================
           2. SIDEBAR (The Black Column)
           ============================================================================= */
        [data-testid="stSidebar"] {
            background-color: var(--bauhaus-black);
            border-right: 5px solid var(--bauhaus-red); /* Accent Border */
        }
        
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: var(--bauhaus-white);
        }
        
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div {
            color: var(--bauhaus-white);
        }
        
        /* Navigation Links */
        [data-testid="stSidebarNav"] a {
            color: var(--bauhaus-white) !important;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.1rem;
            text-transform: uppercase;
            border-bottom: 1px solid #333;
            padding: 10px 0;
            transition: all 0.2s;
        }
        
        [data-testid="stSidebarNav"] a:hover {
            color: var(--bauhaus-yellow) !important;
            padding-left: 10px;
            background-color: transparent;
        }
        
        /* Hide Icons if possible via primitive CSS targeting, otherwise we rely on app.py removal */
        [data-testid="stSidebarNav"] img, [data-testid="stSidebarNav"] svg {
            display: none !important; /* Force hide icons */
        }

        /* =============================================================================
           3. UI COMPONENTS (The Grid)
           ============================================================================= */
        
        /* Cards: White Box, Black Border, Hard Shadow */
        div.bauhaus-card {
            background-color: var(--bauhaus-white);
            border: 3px solid var(--bauhaus-black);
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 8px 8px 0px var(--bauhaus-black); /* Hard Shadow */
            transition: transform 0.2s;
        }
        div.bauhaus-card:hover {
            transform: translate(-2px, -2px);
            box-shadow: 12px 12px 0px var(--bauhaus-black);
            border-color: var(--bauhaus-blue);
        }
        
        /* Primary Colors for Card Header Accents */
        .b-red { border-top: 10px solid var(--bauhaus-red) !important; }
        .b-blue { border-top: 10px solid var(--bauhaus-blue) !important; }
        .b-yellow { border-top: 10px solid var(--bauhaus-yellow) !important; }

        /* Buttons: Brutalist */
        .stButton > button {
            background-color: var(--bauhaus-white);
            border: 3px solid var(--bauhaus-black);
            color: var(--bauhaus-black);
            border-radius: 0; /* Square */
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 900;
            text-transform: uppercase;
            box-shadow: 4px 4px 0px var(--bauhaus-black);
            transition: all 0.1s;
        }
        .stButton > button:hover {
            background-color: var(--bauhaus-black);
            color: var(--bauhaus-yellow);
            border-color: var(--bauhaus-black);
            box-shadow: 2px 2px 0px var(--bauhaus-yellow);
            transform: translate(2px, 2px);
        }
        
        /* Selectbox */
        .stSelectbox > div > div {
            background-color: var(--bauhaus-white);
            border: 3px solid var(--bauhaus-black);
            border-radius: 0;
            color: var(--bauhaus-black);
            font-family: 'Jost', sans-serif;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 900;
            color: var(--bauhaus-black);
        }
        [data-testid="stMetricLabel"] {
            font-family: 'Jost', sans-serif;
            text-transform: uppercase;
            font-weight: 700;
            color: #555;
        }
        
        /* Plotly Chart Container */
        .js-plotly-plot .plotly .main-svg {
            background: transparent !important;
        }
        
        </style>
    """, unsafe_allow_html=True)
