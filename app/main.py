import streamlit as st
import pandas as pd
import sqlite3
import os
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Analytical Product (BI) Governance Hub")

# --- DATABASE CONNECTION (LOCAL SQLITE) ---
DB_PATH = os.path.join(os.path.dirname(__file__), "local_governance.db")

def get_db_connection():
    """Returns a local SQLite connection"""
    return sqlite3.connect(DB_PATH)

# --- TABLE NAMES ---
CATALOG_TABLE = "tbl_bi_catalog"
INPUTS_TABLE = "tbl_governance_inputs"
FAVORITES_TABLE = "tbl_user_favorites"
IFRAMES_TABLE = "tbl_user_iframes"

STEWARD_EMAILS = ["t1.nlsvara@vanderlande.com", "t1.nlgjv@vanderlande.com", "dev_user"]

def get_current_user_email():
    try:
        headers = st.context.headers
        email = headers.get("X-Forwarded-Email", "dev_user")
        return email.strip()
    except:
        return "dev_user"

def format_name(email):
    if not email or "@" not in email: 
        return email.title()
    return email.split("@")[0].replace(".", " ").replace("_", " ").title()

current_user_email = get_current_user_email()
current_user_name = format_name(current_user_email)
is_steward = current_user_email in STEWARD_EMAILS

# --- 1. DATA FUNCTIONS ---
def load_user_favorites(email):
    try:
        query = f"SELECT app_id FROM {FAVORITES_TABLE} WHERE user_email = '{email}'"
        with get_db_connection() as conn:
            df = pd.read_sql(query, conn)
        return set(df['app_id'].tolist())
    except Exception as e:
        print(f"Error loading favorites: {e}")
        return set()

def toggle_favorite_db(email, app_id, is_adding):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if is_adding:
            query = f"""
                INSERT INTO {FAVORITES_TABLE} (user_email, app_id, added_at) 
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """
            cursor.execute(query, (email, app_id))
        else:
            query = f"""
                DELETE FROM {FAVORITES_TABLE} 
                WHERE user_email = ? AND app_id = ?
            """
            cursor.execute(query, (email, app_id))
        conn.commit()

# --- IFRAME DB FUNCTIONS ---
def load_user_iframes(email):
    try:
        query = f"""
            SELECT iframe_code, COALESCE(grid_width, 'Half') as grid_width, COALESCE(height_px, 400) as height_px 
            FROM {IFRAMES_TABLE} 
            WHERE user_email = ? ORDER BY added_at ASC
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (email,))
            rows = cursor.fetchall()
            return [{"code": r[0], "width": r[1], "height": r[2]} for r in rows]
    except Exception as e:
        print(f"Error loading iframes: {e}")
        return []

def add_user_iframe_db(email, iframe_code):
    query = f"""
        INSERT INTO {IFRAMES_TABLE} (user_email, iframe_code, added_at, grid_width, height_px) 
        VALUES (?, ?, CURRENT_TIMESTAMP, 'Half', 400)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (email, iframe_code))
        conn.commit()

def update_iframe_size_db(email, iframe_code, width, height):
    query = f"""
        UPDATE {IFRAMES_TABLE} 
        SET grid_width = ?, height_px = ? 
        WHERE user_email = ? AND iframe_code = ?
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (width, height, email, iframe_code))
        conn.commit()

def remove_user_iframe_db(email, iframe_code):
    query = f"""
        DELETE FROM {IFRAMES_TABLE} 
        WHERE user_email = ? AND iframe_code = ?
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (email, iframe_code))
        conn.commit()

def get_filter_options(column="space_name", steward=False):
    query = f"""
        SELECT DISTINCT {column} 
        FROM {CATALOG_TABLE} 
        WHERE {column} IS NOT NULL 
          AND {column} != 'None' 
          AND trim({column}) != ''
    """
    if not steward and column == "space_name":
        query += " AND space_name NOT LIKE '%[ACC]%' AND space_name NOT LIKE '%[DEV]%'"
        
    query += f" ORDER BY {column}"
    
    with get_db_connection() as conn:
        df = pd.read_sql(query, conn)
    return df[column].tolist()

def get_data(selected_space="All", selected_platform="All", steward=False, user_name=""):
    base_query = f"""
    SELECT 
        a.app_id,
        a.platform,
        a.app_name,
        a.space_name,
        COALESCE(a.app_owner_name, 'Unknown Owner') as app_owner_name,
        CASE 
            WHEN a.platform = 'Power BI' THEN 'https://app.powerbi.com/groups/' || a.workspace_id || '/reports/' || a.app_id
            ELSE 'https://vanderlande.eu.qlikcloud.com/sense/app/' || a.app_id
        END as app_link,
        COALESCE(b.approved_status, 'Pending') as approved_status,
        COALESCE(b.governance_comments, '') as governance_comments,
        COALESCE(b.documentation_link, '') as documentation_link,
        COALESCE(b.kpi_definitions_link, '') as kpi_definitions_link,
        COALESCE(b.work_instructions_link, '') as work_instructions_link,
        b.last_updated
    FROM {CATALOG_TABLE} a
    LEFT JOIN {INPUTS_TABLE} b
    ON a.app_id = b.app_id
    WHERE 1=1
    """
    
    if not steward:
        base_query += f""" 
            AND (
                (a.space_name IS NOT NULL 
                 AND a.space_name NOT LIKE '%[ACC]%' 
                 AND a.space_name NOT LIKE '%[DEV]%') 
                OR LOWER(a.app_owner_name) = LOWER('{user_name}')
            )
        """
    
    if selected_space and selected_space != "All":
        base_query += f" AND a.space_name = '{selected_space}'"
        
    if selected_platform and selected_platform != "All":
        base_query += f" AND a.platform = '{selected_platform}'"
    
    base_query += " ORDER BY b.last_updated DESC"
    
    with get_db_connection() as conn:
        df = pd.read_sql(base_query, conn)
        
    df['last_updated'] = pd.to_datetime(df['last_updated'])
    return df

# --- INITIALIZE SESSION STATE ---
if 'save_success' not in st.session_state:
    st.session_state.save_success = False

if 'favorites' not in st.session_state:
    st.session_state.favorites = load_user_favorites(current_user_email)

if 'user_iframes' not in st.session_state:
    st.session_state.user_iframes = load_user_iframes(current_user_email)

# --- GLOBAL STYLES & HEADER ---
st.markdown("""
<style>
div[data-testid="stLinkButton"] p { font-weight: 500 !important; }
div[data-testid="stLinkButton"] a {
    background-color: #009845 !important;
    color: white !important;
    border: none !important;
    width: 100% !important; 
    height: 60px !important;
    margin: 5px 0px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    white-space: normal !important;
    line-height: 1.2 !important;
    padding: 10px !important;
    border-radius: 8px !important;
}
div[data-testid="stLinkButton"] a:hover { background-color: #007535 !important; color: white !important; }
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display: none !important; }
[data-testid="stSidebar"] div[role="radiogroup"] > label { padding: 12px 16px; border-radius: 8px; margin-bottom: 4px; transition: 0.2s; cursor: pointer; width: 100%; background-color: transparent; }
[data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background-color: #f0f2f6; }
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) { background-color: #e6e9ef !important; }
[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p { color: #31333F !important; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ Analytical Product (BI) Governance Hub")

if is_steward:
    st.info(f"👋 Welcome, **{current_user_name}**. You are logged in as a **Data Steward** (Edit Mode).")
else:
    st.warning(f"👋 Welcome, **{current_user_name}**. You are in **Viewer Mode** (Read Only).")

if st.session_state.save_success:
    st.success("✅ Changes saved successfully!")
    st.session_state.save_success = False

def show_empty_state(text):
    st.markdown(f"""
        <div style="background-color: #f0f2f6; border-radius: 8px; padding: 16px; color: #555; font-size: 15px; border: 1px solid #e6e9ef; margin-bottom: 15px;">
            {text}
        </div>
    """, unsafe_allow_html=True)

column_config_settings = {
    "favorite": st.column_config.CheckboxColumn("Fav", default=False, width="small"),
    "app_id": None, 
    "app_link": st.column_config.LinkColumn("App", display_text="Open 🔗", width="small"),
    "platform": st.column_config.TextColumn("Platform", width="small"),
    "documentation_link": st.column_config.LinkColumn("Docs", display_text="PDF 📄", validate="^https://.*", width="small"),
    "kpi_definitions_link": st.column_config.LinkColumn("KPIs", display_text="View 📑", validate="^https://.*", width="small"),
    "work_instructions_link": st.column_config.LinkColumn("Instructions", display_text="View 📋", validate="^https://.*", width="small"),
    "app_name": st.column_config.TextColumn("Dashboard Name"), 
    "space_name": st.column_config.TextColumn("Workspace"), 
    "app_owner_name": st.column_config.TextColumn("Owner"), 
    "last_updated": st.column_config.DatetimeColumn("Last Actioned", format="D MMM YYYY", disabled=True),
    "approved_status": st.column_config.SelectboxColumn("Status", options=["Pending", "Yes", "No", "Needs Review"], width="small"),
    "governance_comments": st.column_config.TextColumn("Comments", width="large")
}

def process_updates(editor_key, reference_df):
    edited_rows = st.session_state[editor_key]["edited_rows"]
    for idx, changes in edited_rows.items():
        if "favorite" in changes:
            app_id = reference_df.iloc[idx]['app_id']
            is_fav = changes["favorite"]
            toggle_favorite_db(current_user_email, app_id, is_fav)
            if is_fav:
                st.session_state.favorites.add(app_id)
            else:
                st.session_state.favorites.discard(app_id)

def prep_display_df(df, search_term=""):
    if search_term:
        df_disp = df[df['app_name'].str.contains(search_term, case=False, na=False) | 
                     df['app_id'].str.contains(search_term, case=False, na=False)].copy()
    else:
        df_disp = df.copy()
    cols = ['favorite'] + [c for c in df_disp.columns if c != 'favorite']
    return df_disp[cols].reset_index(drop=True)

# --- NAVIGATION ROUTING ---
st.sidebar.title("🧭 Navigation")
menu_selection = st.sidebar.radio("Go to:", ["🏠 Home", "🔍 Find Dashboards"])
st.sidebar.divider()

df_original = get_data("All", "All", is_steward, current_user_name)
df_original['favorite'] = df_original['app_id'].isin(st.session_state.favorites)

# ==========================================
# PAGE 1: HOME
# ==========================================
if menu_selection == "🏠 Home":
    
    fav_head_col, fav_add_col = st.columns([9, 1], vertical_alignment="center")
    with fav_head_col: st.subheader("⭐ Your Favorite Dashboards")
    with fav_add_col:
        with st.popover("➕ Add", use_container_width=True):
            home_search = st.text_input("🔎 Search App Name", key="home_search")
            df_home_display = prep_display_df(df_original, home_search)
            cols_to_keep = ['favorite', 'app_id', 'platform', 'app_name', 'space_name', 'app_link']
            df_home_display = df_home_display[cols_to_keep]
            cols_to_disable = [c for c in df_home_display.columns if c != 'favorite']
            
            st.data_editor(
                df_home_display, column_config=column_config_settings, hide_index=True,
                use_container_width=True, disabled=cols_to_disable, key="home_editor",
                on_change=process_updates, args=("home_editor", df_home_display)
            )

    if st.session_state.favorites:
        fav_df = df_original[df_original['favorite'] == True]
        cols = st.columns(8, gap="small")
        for index, (i, row) in enumerate(fav_df.iterrows()):
            with cols[index % 5]:
                platform_emoji = "📊" if row['platform'] == 'Power BI' else "📈"
                st.link_button(label=f"{platform_emoji} {row['app_name']}", url=row['app_link'])
    else:
        show_empty_state("No favorites pinned yet. Click the '+ Add' button above to select some!")

    st.divider()

    vis_head_col, vis_add_col = st.columns([9, 1], vertical_alignment="center")
    with vis_head_col:
        st.subheader("📊 Tracked Visuals")
        st.caption("Live views from your BI Platforms")
    with vis_add_col:
        with st.popover("➕ Add", use_container_width=True):
            new_iframe = st.text_area("Paste iFrame HTML:", placeholder="<iframe src='...'></iframe>", height=100)
            if st.button("Save Visual", type="primary"):
                if "<iframe" in new_iframe.lower():
                    add_user_iframe_db(current_user_email, new_iframe)
                    st.session_state.user_iframes = load_user_iframes(current_user_email)
                    st.success("Visual saved!")
                    st.rerun()

    if st.session_state.user_iframes:
        current_row = st.columns(2)
        col_idx = 0
        for i, item in enumerate(st.session_state.user_iframes):
            code, w_setting, h_setting = item["code"], item["width"], item["height"]
            target_col = st.columns(1)[0] if w_setting == "Full" else current_row[col_idx % 2]
            if w_setting != "Full": col_idx += 1

            with target_col:
                with st.container(border=True):
                    spacer, btn_col = st.columns([15, 2])
                    with btn_col:
                        with st.popover("⚙️", use_container_width=True):
                            new_w = st.select_slider("Width", options=["Half", "Full"], value=w_setting, key=f"w_{i}")
                            new_h = st.slider("Height (px)", 200, 800, h_setting, step=50, key=f"h_{i}")
                            if st.button("💾 Save", key=f"sv_{i}"):
                                update_iframe_size_db(current_user_email, code, new_w, new_h)
                                st.session_state.user_iframes = load_user_iframes(current_user_email)
                                st.rerun()
                            if st.button("🗑️ Remove", key=f"rm_{i}"):
                                remove_user_iframe_db(current_user_email, code)
                                st.session_state.user_iframes = load_user_iframes(current_user_email)
                                st.rerun()
                    clean_code = code.replace("height:100%", f"height:{h_setting}px")
                    html_wrapper = f"<div style='margin-top:-15px; height:{h_setting}px; width:100%; overflow:hidden;'>{clean_code}</div>"
                    components.html(html_wrapper, height=h_setting)

            if col_idx % 2 == 0 or w_setting == "Full":
                current_row = st.columns(2)
    else:
        show_empty_state("No visuals tracked yet. Click the '+ Add' button above.")

# ==========================================
# PAGE 2: FIND DASHBOARDS (GOVERNANCE)
# ==========================================
elif menu_selection == "🔍 Find Dashboards":
    st.subheader("Catalog & Governance")
    
    st.sidebar.title("🔍 Filters")
    available_platforms = ["All"] + get_filter_options("platform", is_steward)
    selected_platform = st.sidebar.selectbox("Select Platform", available_platforms)
    
    available_spaces = ["All"] + get_filter_options("space_name", is_steward)
    selected_space = st.sidebar.selectbox("Select Workspace", available_spaces)

    df_filtered = get_data(selected_space, selected_platform, is_steward, current_user_name)
    df_filtered['favorite'] = df_filtered['app_id'].isin(st.session_state.favorites)

    total_apps = len(df_filtered)
    pending_apps = len(df_filtered[df_filtered['approved_status'] == 'Pending'])
    
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Dashboards", total_apps)
    k2.metric("Pending Review", pending_apps)
    k3.metric("Reviewed", total_apps - pending_apps)
    st.divider()

    search_term = st.text_input("🔎 Search App Name", placeholder="Type to search...")
    df_display = prep_display_df(df_filtered, search_term)

    base_disabled = ["app_name", "platform", "space_name", "app_owner_name", "last_updated", "app_link"]

    if is_steward:
        edited_df = st.data_editor(
            df_display, column_config=column_config_settings, hide_index=True,
            use_container_width=True, disabled=base_disabled, key="gov_editor",
            on_change=process_updates, args=("gov_editor", df_display)
        )
        
        cols_to_compare = ['app_id', 'approved_status', 'governance_comments', 'documentation_link', 'kpi_definitions_link', 'work_instructions_link']
        df_compare = df_display[cols_to_compare].astype(str)
        edited_compare = edited_df[cols_to_compare].astype(str)
        
        if df_compare.ne(edited_compare).any().any():
            if st.button("💾 Save Governance Changes", type="primary"):
                rows_to_upload = edited_df[df_compare.ne(edited_compare).any(axis=1)]
                
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    for _, row in rows_to_upload.iterrows():
                        # SQLite Upsert Syntax
                        upsert_sql = f"""
                        INSERT INTO {INPUTS_TABLE} 
                            (app_id, approved_status, governance_comments, documentation_link, kpi_definitions_link, work_instructions_link, last_updated) 
                        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        ON CONFLICT(app_id) DO UPDATE SET
                            approved_status = excluded.approved_status,
                            governance_comments = excluded.governance_comments,
                            documentation_link = excluded.documentation_link,
                            kpi_definitions_link = excluded.kpi_definitions_link,
                            work_instructions_link = excluded.work_instructions_link,
                            last_updated = CURRENT_TIMESTAMP
                        """
                        params = (
                            str(row['app_id']), str(row['approved_status']), str(row['governance_comments']),
                            str(row['documentation_link']), str(row['kpi_definitions_link']), str(row['work_instructions_link'])
                        )
                        cursor.execute(upsert_sql, params)
                    conn.commit()
                
                st.session_state.save_success = True
                st.rerun()
    else:
        cols_to_disable = [c for c in list(df_display.columns) if c != 'favorite']
        st.data_editor(
            df_display, column_config=column_config_settings, hide_index=True,
            use_container_width=True, disabled=cols_to_disable, key="gov_editor",
            on_change=process_updates, args=("gov_editor", df_display)
        )