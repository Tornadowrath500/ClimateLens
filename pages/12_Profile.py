from __future__ import annotations

import streamlit as st

from fairlens.ui import PROFILE_ACCENTS, callout, setup_page


setup_page("Session profile")
if st.session_state.pop("fl_profile_saved", False):
    st.success("Profile updated. Your suggestions and appearance now use these settings.")

logo, intro = st.columns([1, 5], vertical_alignment="center")
with logo:
    st.image("assets/fairlens-mark.svg", width=82)
with intro:
    st.markdown('<div class="fl-eyebrow">FAIRLENS / YOUR SESSION</div>', unsafe_allow_html=True)
    st.title("A clearer view, shaped around you.")
    st.markdown(
        '<p class="fl-lede">Create a lightweight profile to find the FairLens pages most relevant to your interests.</p>',
        unsafe_allow_html=True,
    )

callout(
    "Privacy in this prototype",
    "Profile details are held in Streamlit session state while this browser session is active; this build has no account database and does not write them to disk. Age, sex, and personal status only shape page suggestions and never enter prediction or audit calculations. Persistent accounts and password sign-in are not configured yet.",
)

signup, login, customize = st.tabs(["Create session profile", "Resume this session", "Customize profile"])

with signup:
    st.subheader("Create your profile")
    st.caption("Every field is optional. You can leave sensitive details blank and still use the app.")
    with st.form("profile_signup"):
        display_name = st.text_input("Display name (optional)", max_chars=40)
        share_age = st.checkbox("Include my age for age-fairness learning suggestions")
        age = st.number_input("Age", min_value=13, max_value=120, value=25, step=1) if share_age else None
        sex = st.selectbox(
            "Sex (optional)",
            ["Prefer not to say", "Female", "Male", "Intersex", "Another description"],
            help="FairLens uses this only to point out how sensitive attributes appear in the historical benchmark.",
        )
        personal_status = st.selectbox(
            "Personal / marital status (optional)",
            ["Prefer not to say", "Single", "Married", "Widowed", "Divorced or separated", "Another description"],
        )
        interests = st.multiselect(
            "What would you like to explore? (optional)",
            ["Model performance", "Fairness across groups", "How predictions work", "Hands-on experiments"],
        )
        submitted = st.form_submit_button("Create my profile", type="primary", icon=":material/person_add:")

    if submitted:
        st.session_state["fl_profile"] = {
            "display_name": display_name.strip(),
            "age": age,
            "sex": sex,
            "personal_status": personal_status,
            "interests": interests,
            "avatar": "🔎",
            "accent": "Mint",
        }
        st.session_state["fl_profile_active"] = True
        st.success("Your session profile is ready. Your model and audit settings were not changed.")
        st.page_link("pages/13_Tutorial.py", label="Take the animated tour", icon=":material/play_circle:")
        st.page_link("pages/0_Home.py", label="Go to your FairLens home", icon=":material/arrow_forward:")

with login:
    profile = st.session_state.get("fl_profile")
    if profile:
        label = profile.get("display_name") or "your profile"
        st.write(f"A session profile for **{label}** is available in this browser tab.")
        if st.button("Continue with this session", type="primary", icon=":material/login:"):
            st.session_state["fl_profile_active"] = True
            st.success("You’re back in this FairLens session.")
            st.page_link("pages/13_Tutorial.py", label="Take the animated tour", icon=":material/play_circle:")
            st.page_link("pages/0_Home.py", label="Go to FairLens home", icon=":material/arrow_forward:")
    else:
        st.info("No profile is available in this session. Persistent accounts are not configured yet; create a session profile in the first tab.")

with customize:
    profile = st.session_state.get("fl_profile")
    if not profile:
        st.info("Create a session profile first to customize its appearance and interests.")
    else:
        st.subheader("Make FairLens feel like yours")
        st.caption("Changes apply to this browser session only. All personal details remain optional.")
        sex_options = ["Prefer not to say", "Female", "Male", "Intersex", "Another description"]
        status_options = ["Prefer not to say", "Single", "Married", "Widowed", "Divorced or separated", "Another description"]
        interest_options = ["Model performance", "Fairness across groups", "How predictions work", "Hands-on experiments"]
        avatar_options = ["🔎", "🧭", "📊", "✨", "🌱"]
        accent_options = list(PROFILE_ACCENTS)
        with st.form("profile_customization"):
            edit_name = st.text_input("Display name", value=profile.get("display_name", ""), max_chars=40)
            left, right = st.columns(2)
            with left:
                avatar = st.selectbox("Avatar", avatar_options, index=avatar_options.index(profile.get("avatar", "🔎")))
                share_age = st.checkbox("Include age in page suggestions", value=profile.get("age") is not None)
                age = st.number_input("Age", min_value=13, max_value=120, value=int(profile.get("age") or 25), step=1, disabled=not share_age)
                sex = st.selectbox("Sex", sex_options, index=sex_options.index(profile.get("sex", "Prefer not to say")))
            with right:
                accent = st.selectbox("Accent color", accent_options, index=accent_options.index(profile.get("accent", "Mint")))
                personal_status = st.selectbox(
                    "Personal / marital status",
                    status_options,
                    index=status_options.index(profile.get("personal_status", "Prefer not to say")),
                )
                interests = st.multiselect("Interests", interest_options, default=profile.get("interests", []))
            saved = st.form_submit_button("Save my changes", type="primary", icon=":material/check:")
        if saved:
            st.session_state["fl_profile"] = {
                **profile,
                "display_name": edit_name.strip(),
                "avatar": avatar,
                "accent": accent,
                "age": age if share_age else None,
                "sex": sex,
                "personal_status": personal_status,
                "interests": interests,
            }
            st.session_state["fl_profile_saved"] = True
            st.rerun()

st.caption("You can also use FairLens without a profile. Demographic details are never used to evaluate a real applicant.")

