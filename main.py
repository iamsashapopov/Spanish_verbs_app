import streamlit as st
import json
import os
import unicodedata
import streamlit.components.v1 as components
import base64

LOG_PATH = "/Users/sashapopov/Desktop/spanish_app/.cursor/debug.log"


def _write_log(event: str, data: dict | None = None):
    import time, json
    payload = {"event": event, "data": data or {}, "timestamp": int(time.time() * 1000)}
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    except Exception:
        pass


def _img_to_data(path):
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded_string}"


# Путь к локальной базе данных
VERBS_FILE = "/Users/sashapopov/Desktop/spanish_app/verbs.json"


def load_verbs():
    try:
        with open(VERBS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def ensure_translation_field(db: dict) -> bool:
    """
    Добавляет translation_en всем записям, где его нет.
    Возвращает True, если были изменения.
    """
    changed = False
    for key, data in (db or {}).items():
        if isinstance(data, dict) and "translation_en" not in data:
            data["translation_en"] = ""
            changed = True
    return changed


def save_verbs(verbs: dict):
    os.makedirs(os.path.dirname(VERBS_FILE), exist_ok=True)
    with open(VERBS_FILE, "w", encoding="utf-8") as f:
        json.dump(verbs, f, ensure_ascii=False, indent=2)


verbs_db = load_verbs()
if ensure_translation_field(verbs_db):
    save_verbs(verbs_db)

st.set_page_config(
    page_title="Спряжение испанских глаголов",
    page_icon="🇪🇸",
    layout="wide",
)

_CSS = """
<style>
body { background: linear-gradient(180deg, #f7f9fc 0%, #ffffff 100%); }

/* padding-top для основного контейнера приложения */
[data-testid="stMainBlockContainer"] {
    padding-top: 18px !important;
}
 .card { 
     padding: 18px; 
     border-radius: 12px; 
     background: transparent; 
     box-shadow: none;
     width: 100%;
     max-width: 1200px;
     margin: 0 auto;
     box-sizing: border-box;
 }
.header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.tense-title { margin-top: 12px; margin-bottom: 6px; font-weight: 600; border-bottom: none; display: inline-block; color: #333; text-align: left; }
.custom-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 14px; }
.custom-table th { text-align: left; padding: 6px; border-bottom: 1px solid #eee; color: #666; }
.custom-table td { padding: 6px; border-bottom: 1px solid #f9f9f9; }
.conj-list { list-style: none; padding: 0 !important; margin: 8px 0 0px 0; }
.conj-item { padding: 4px 0 !important; border-bottom: 1px solid #f3f3f3; margin: 0 !important; list-style-type: none; }
.conj-pronoun { color: #888; font-size: 13px; margin-bottom: 0px !important; text-align: left; }
.conj-verb { color: #111; font-size: 16px; font-weight: 400; text-align: left; }
    
    /* Сетка результатов */
    .tenses-container {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 20px !important;
        width: 100% !important;
        margin-top: 20px !important;
        margin-bottom: 40px !important; /* Добавили отступ снизу */
    }

    .tense-block {
        /* По умолчанию 2 в ряд (на экранах < 1200px) */
        flex: 0 0 calc(50% - 20px) !important;
        min-width: 140px !important;
        box-sizing: border-box !important;
    }

    @media (min-width: 900px) {
        
            flex: 0 0 calc(20% - 20px) !important;
            max-width: calc(20% - 20px) !important;
        }
    }

    /* Сохраняем компактность списка внутри блоков */
    .conj-item { 
        padding: 4px 0 !important; 
        border-bottom: 1px solid #f3f3f3 !important; 
        margin: 0 !important; 
        list-style: none !important; 
    }

    /* Убираем рамку формы */
    [data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
    }

    /* Высота контейнера и поля ввода */
    [data-testid="stForm"] div[data-testid="stTextInput"] > div {
        height: 44px !important;
    }
    
    [data-testid="stForm"] input {
        height: 44px !important;
    }

    /* Кнопка 44x44 с цветом #32333f */
    [data-testid="stForm"] button {
        height: 44px !important;
        width: 44px !important;
        min-width: 44px !important;
        max-width: 44px !important;
        padding: 0 !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: #32333f !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        cursor: pointer !important;
    }

    /* Принудительно увеличиваем сам символ внутри кнопки */
    [data-testid="stForm"] button p {
        font-size: 32px !important;
        font-weight: bold !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
    }

    [data-testid="stForm"] button:hover {
        background-color: #434452 !important;
    }
    
    /* Адаптивная сетка */
        width: 100%;
        align-items: flex-start;
    }
    .tense-block {
        flex: 1 1 calc(50% - 32px);
        min-width: 150px;
    }
    @media (min-width: 1200px) {
        .tense-block {
            /* 5 блоков в ряд: 100% / 5 = 20%. Вычитаем увеличенный gap */
            flex: 1 1 calc(20% - 32px);
            max-width: calc(20% - 32px);
        }
    }
    /* Стилизуем контейнер формы */
    [data-testid="stForm"] {
        border: none !important;
        padding: 4px !important; /* Уменьшили паддинг до 4px */
        background-color: #f1f2f6 !important;
        border-radius: 12px !important;
    }

    /* Растягиваем внутренние контейнеры Streamlit */
    [data-testid="stForm"] [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        width: 100% !important;
        gap: 12px !important;
    }

    /* Первая колонка забирает всё свободное место */
    [data-testid="stForm"] [data-testid="stHorizontalBlock"] > div:first-child {
        flex-grow: 1 !important;
        width: 100% !important;
    }

    /* Вторая колонка сжимается под кнопку */
    [data-testid="stForm"] [data-testid="stHorizontalBlock"] > div:last-child {
        flex-grow: 0 !important;
        flex-basis: 44px !important;
        width: 44px !important;
    }

    /* Само текстовое поле растягивается внутри своей колонки */
    [data-testid="stForm"] [data-testid="stTextInput"],
    [data-testid="stForm"] [data-testid="stTextInput"] > div {
        width: 100% !important;
    }

    /* Убираем красную подсветку при фокусе */
    [data-testid="stForm"] div[data-baseweb="input"]:focus-within {
        border-color: transparent !important;
        box-shadow: none !important;
    }
    
    /* Запрещаем перенос элементов внутри формы поиска */
    form[data-testid="stForm"] [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: nowrap !important; /* Кнопка ВСЕГДА в одной строке */
        align-items: center !important;
        width: 100% !important;
        gap: 8px !important;
    }

    /* Растягиваем первую колонку и разрешаем ей сжиматься до нуля */
    form[data-testid="stForm"] [data-testid="stHorizontalBlock"] > div:first-child {
        flex: 1 1 0% !important; /* flex-grow: 1, flex-shrink: 1, flex-basis: 0% */
        min-width: 0 !important;
        width: 100% !important;
    }

    /* Убираем минимальную ширину у самого виджета ввода */
    form[data-testid="stForm"] div[data-testid="stTextInput"],
    form[data-testid="stForm"] div[data-testid="stTextInput"] > div {
        min-width: 0 !important;
        width: 100% !important;
    }

    /* Кнопка остается фиксированной 44x44 */
    form[data-testid="stForm"] [data-testid="stHorizontalBlock"] > div:last-child {
        flex: 0 0 44px !important;
        width: 44px !important;
        min-width: 44px !important;
    }
    
    [data-testid="stForm"] input:focus {
        outline: none !important;
        border-color: transparent !important;
        box-shadow: none !important;
    }

    /* Высота контейнера и поля ввода */
    height: 48px;
</style>
    """
st.markdown(_CSS, unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)

    # Лого сверху слева (как в примере: horizontal container)
    try:
        with st.container(horizontal=True, vertical_alignment="bottom"):
            st.image("logo.svg", width=88)
    except TypeError:
        # Fallback для Streamlit без horizontal/vertical_alignment у container()
        col_logo, _ = st.columns([1, 20], vertical_alignment="bottom")
        with col_logo:
            st.image("logo.svg", width=88)

    if "last_search" not in st.session_state:
        st.session_state["last_search"] = ""

    st.markdown('<div class="search-bar">', unsafe_allow_html=True)
    with st.form("search_form", clear_on_submit=False, border=False):
        try:
            with st.container(horizontal=True, vertical_alignment="bottom"):
                verb_input = st.text_input(
                    "Search",
                    value=st.session_state.get("last_search", ""),
                    placeholder="For example: hablar",
                    label_visibility="collapsed",
                    key="search_text",
                )
                submit = st.form_submit_button(
                    "",
                    icon=":material/search:",
                )
        except TypeError:
            # Fallback для Streamlit без horizontal/vertical_alignment у container()
            col_input, col_btn = st.columns([15, 1], gap="small")
            with col_input:
                verb_input = st.text_input(
                    "Search",
                    value=st.session_state.get("last_search", ""),
                    placeholder="Например: hablar",
                    label_visibility="collapsed",
                    key="search_text",
                )
            with col_btn:
                submit = st.form_submit_button("⌕")

        if submit:
            st.session_state["last_search"] = verb_input.strip()
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    current_query = st.session_state.get("last_search", "").strip()
    persons = ["yo", "tú", "él/ella/Ud.", "nosotros/as", "vosotros/as", "ellos/ellas/Uds."]

    TENSES = [
        ("presente", "Presente"),
        ("preterito_indefinido", "Pretérito Indefinido"),
        ("preterito_perfecto", "Pretérito Perfecto"),
        ("preterito_imperfecto", "Pretérito Imperfecto"),
        ("futuro_simple", "Futuro Simple"),
    ]
    HABER_PRESENTE = ["he", "has", "ha", "hemos", "habéis", "han"]

    def normalize_list_or_dict(value):
        if isinstance(value, list):
            lst = value
        elif isinstance(value, dict):
            keys = ["1s", "2s", "3s", "1p", "2p", "3p"]
            lst = [value.get(k, "") for k in keys]
        else:
            lst = []
        while len(lst) < 6:
            lst.append("")
        return lst[:6]

    def render_tense_from_data(tense_key: str, title: str, data: dict):
        tense_forms = normalize_list_or_dict(data.get(tense_key, []))

        parts = [
            '<div class="tense-block">',
            f'<div class="tense-title">{title}</div>',
            '<ul class="conj-list">',
        ]

        for idx, (person, form) in enumerate(zip(persons, tense_forms)):
            s = str(form).strip()

            if tense_key == "preterito_perfecto":
                if " " in s:
                    display = s
                else:
                    part = s
                    display = f"{HABER_PRESENTE[idx]} {part}" if part else HABER_PRESENTE[idx]
            else:
                display = s.split()[-1] if s.split() else s

            display = unicodedata.normalize("NFC", display)

            parts.append(
                f'<li class="conj-item" style="margin: 0 !important; padding: 4px 0 !important; list-style: none; border-bottom: 1px solid #f3f3f3;">'
                f'<div class="conj-pronoun" style="margin: 0 !important; padding: 0 !important; line-height: 1.2;">{person}</div>'
                f'<div class="conj-verb" style="margin: 0 !important; padding: 0 !important; line-height: 1.2;">{display}</div>'
                f"</li>"
            )

        parts.append("</ul></div>")
        return "".join(parts)

    if current_query:
        data = verbs_db.get(current_query.lower())
        if data:
            all_tenses_html = ['<div class="tenses-container">']
            for tense_key, title in TENSES:
                all_tenses_html.append(render_tense_from_data(tense_key, title, data))
            all_tenses_html.append("</div>")

            st.markdown("".join(all_tenses_html), unsafe_allow_html=True)
        else:
            st.info(f"Глагол '{current_query}' не найден.")

    SHOW_EDITOR = False  # поставь True, чтобы быстро вернуть блок добавления/редактирования
    if SHOW_EDITOR:
        with st.expander("Добавить / редактировать глагол"):
            with st.form("editor_form"):
                edit_inf = st.text_input("Инфинитив:", value=current_query)
                edit_key = edit_inf.strip().lower()
                existing = verbs_db.get(edit_key, {})

                def get_tense_inputs(label, t_key):
                    st.write(f"**{label}**")
                    defaults = normalize_list_or_dict(existing.get(t_key, []))
                    cols = st.columns(6)
                    return [
                        cols[i].text_input(persons[i], value=defaults[i], key=f"inp_{t_key}_{i}")
                        for i in range(6)
                    ]