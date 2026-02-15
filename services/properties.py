from services.ab_helper import get_variant

variant = get_variant("cta_button_test")

if variant == "A":
    button_label = "AI 매칭"
else:
    button_label = "AI 추천 받기"

if st.button(button_label, key=f"match_{i}"):
    track("click_ai_matching", {
        "variant": variant,
        "property_name": name
    })
