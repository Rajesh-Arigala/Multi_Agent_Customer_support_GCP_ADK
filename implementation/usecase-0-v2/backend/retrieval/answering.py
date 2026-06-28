from __future__ import annotations

from backend.retrieval.models import RetrievalDocument, RetrievalResult
from backend.retrieval.text import tokenize_with_ngrams


GREETING_TERMS = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}
IDENTITY_TERMS = {"who are you", "why are you here", "what do you do", "where do you work"}
DEFINITION_TERMS = {"what", "what is", "explain", "meaning", "define", "tell me about"}
TREATMENT_DEFINITIONS = {
    "ivf": "IVF, or in vitro fertilization, is a fertility treatment where eggs are fertilized with sperm outside the body in a laboratory. A suitable embryo may then be transferred into the uterus.",
    "icsi": "ICSI, or intracytoplasmic sperm injection, is an IVF-related technique where a single sperm is injected directly into an egg in the laboratory.",
    "iui": "IUI, or intrauterine insemination, is a fertility treatment where prepared sperm is placed directly into the uterus around ovulation.",
    "fertility preservation": "Fertility preservation means saving eggs, sperm, or embryos for possible future pregnancy planning.",
}


FAQ_ANSWERS = [
    (
        {"how successful is ivf", "ivf success", "success rate", "success rates"},
        "💖 **IVF success** depends on age, egg and sperm quality, underlying health conditions, and the reason for infertility.\n✨ Women under 35 are mentioned as having higher success rates, around 40–50% per cycle.\n🩺 Success can gradually decline in the late 30s and 40s due to reduced egg quality and quantity.\n📅 For a realistic estimate, Dr. Madhu Patil’s Clinic can review your reports and history during consultation.",
        "WEB-DRMADHU-001",
    ),
    (
        {"improve my fertility before treatment", "improve fertility", "before treatment", "prepare body for ivf"},
        "💖 **Before treatment**, lifestyle preparation can support egg and sperm health.\n✨ Dr. Madhu Patil’s Clinic recommends a healthy balanced diet, optimal weight, moderate exercise, good sleep, and stress management.\n🩺 It also mentions avoiding smoking, limiting alcohol/caffeine, taking prenatal vitamins with folic acid, completing screenings, and reducing environmental toxin exposure.\n📅 Dr. Madhu Patil’s Clinic can personalize these steps based on your age, history, and reports.",
        "WEB-DRMADHU-001",
    ),
    (
        {"what age should i start thinking about fertility", "age should i start", "thinking about fertility", "fertility age"},
        "💖 **Fertility planning** is especially important as fertility naturally starts declining with age, particularly after 35.\n✨ Women in the late 20s and early 30s are mentioned as generally having better fertility potential.\n🩺 If pregnancy is being delayed or there are medical concerns, fertility assessment, ovarian reserve testing, or fertility preservation may be considered earlier.\n📅 Dr. Madhu Patil’s Clinic can guide the right timing based on personal goals and health history.",
        "WEB-DRMADHU-001",
    ),
    (
        {"what can be done after a failed ivf cycle", "failed ivf", "after failed ivf", "ivf cycle fails"},
        "💖 **After a failed IVF cycle**, further evaluation can help identify possible reasons.\n✨ Dr. Madhu Patil’s Clinic mentions hysteroscopy, ERA, PGT-A, sperm DNA fragmentation tests, hormonal evaluation, and immunological profile assessment.\n🩺 These tests can help review embryo quality, uterine environment, sperm integrity, hormonal balance, or immune-related factors.\n📅 Dr. Madhu Patil’s Clinic can suggest the next step after reviewing the previous cycle details.",
        "WEB-DRMADHU-001",
    ),
    (
        {"normal pregnancy and delivery after ivf", "normal pregnancy", "delivery after ivf", "pregnancy after ivf"},
        "💖 **Many women who conceive through IVF can have a normal healthy pregnancy and delivery.**\n✨ Dr. Madhu Patil’s Clinic notes that early pregnancy often needs close monitoring and hormonal support.\n🩺 Some risks may be higher depending on age or underlying fertility issues, but overall health and history matter a lot.\n📅 Dr. Madhu Patil’s Clinic can guide monitoring and delivery planning after reviewing your case.",
        "WEB-DRMADHU-001",
    ),
    (
        {"treatment options for men with low sperm count", "low sperm count", "male low sperm"},
        "💖 **Low sperm count** can still have treatment options after proper evaluation.\n✨ Dr. Madhu Patil’s Clinic mentions lifestyle modification, medical therapy for hormonal or underlying conditions, and assisted reproductive techniques.\n🩺 IUI may help in mild cases, while IVF with ICSI can help even when sperm count is very low.\n📅 Dr. Madhu Patil’s Clinic can recommend the right pathway after semen analysis and related tests.",
        "WEB-DRMADHU-001",
    ),
    (
        {"treatment options for men with zero sperm count", "zero sperm count", "azoospermia"},
        "💖 **Zero sperm count**, also called azoospermia, needs evaluation to understand the cause.\n✨ Dr. Madhu Patil’s Clinic mentions obstructive and non-obstructive causes, with options such as medical or hormonal therapy and surgical correction in selected cases.\n🩺 Advanced sperm retrieval options such as TESA, TESE, or micro-TESE may be considered, followed by IVF with ICSI if sperm are retrieved.\n📅 Dr. Madhu Patil’s Clinic can guide this after detailed male fertility evaluation.",
        "WEB-DRMADHU-001",
    ),
    (
        {"what initially drew you toward infertility", "drew you toward infertility", "focused area of practice", "assisted reproductive technology as a focused area"},
        "💖 **At present, I’m not sure about her personal motivation in her own words.**\n✨ Dr. Madhu Patil’s profile highlights 13+ years in obstetrics and gynecology, with 9+ years focused on infertility and ART.\n🩺 Her background includes advanced ART training from KEIL, Germany, and experience guiding more than 10,000 couples.\n📅 For a personal perspective on her journey, Dr. Madhu Patil’s team can help with an appointment or direct interaction.",
        "WEB-DRMADHU-001",
    ),
    (
        {"profile of infertility cases evolve", "urban india infertility", "age lifestyle underlying medical conditions", "infertility cases evolve"},
        "💖 **At present, I’m not sure about broad urban India trends from Dr. Madhu Patil’s Clinic.**\n✨ The clinic does highlight age as important, especially fertility decline after 35.\n🩺 Fertility assessment at the clinic reviews medical history, lifestyle history, ovarian reserve, uterus/tubes, and semen parameters.\n📅 For a doctor-led perspective on changing infertility patterns, Dr. Madhu Patil’s team can help arrange a consultation.",
        "WEB-DRMADHU-002",
    ),
    (
        {"balance expectations with realistic clinical outcomes", "counselling couples", "realistic clinical outcomes", "large number of ivf and icsi cycles"},
        "💖 **Counselling should balance hope with realistic expectations.**\n✨ Dr. Madhu Patil’s Clinic notes that IVF success depends on age, egg/sperm quality, underlying health conditions, and infertility reasons.\n🩺 The clinic also explains risks such as multiple pregnancy, OHSS, procedure risks, emotional stress, and financial considerations.\n📅 A consultation can help map these factors to the couple’s own reports and treatment history.",
        "WEB-DRMADHU-003",
    ),
    (
        {"poor ovarian reserve", "individualize stimulation protocols", "oocyte yield", "cycle cancellation"},
        "💖 **For poor ovarian reserve, Dr. Madhu Patil’s Clinic mentions mild stimulation protocols.**\n✨ Mild stimulation uses lower-dose medications and is described for women with low ovarian reserve.\n🩺 The IVF/ICSI service information also emphasizes treatment plans tailored to each patient’s needs.\n📅 Final protocol selection should be discussed after reviewing ovarian reserve, age, previous response, and reports.",
        "WEB-DRMADHU-003",
    ),
    (
        {"recurrent implantation failure", "uterine embryological immunological factors", "diagnostic framework", "rif"},
        "💖 **For recurrent implantation failure, the clinic describes a stepwise evaluation.**\n✨ Anatomical, genetic, and hormonal causes are ruled out first.\n🩺 Immune and clotting factors may be assessed when appropriate, especially when immunotherapy is being considered.\n📅 Dr. Madhu Patil’s Clinic can personalize the workup after reviewing previous IVF cycles and reports.",
        "WEB-DRMADHU-007",
    ),
    (
        {"transition point from conservative management", "iui to ivf", "pcos and endometriosis-related infertility", "transition from conservative management or iui"},
        "💖 **The exact transition point is personalized.**\n✨ Dr. Madhu Patil’s Clinic offers care for PCOS and endometriosis, and IVF/ICSI is listed for patients with these conditions.\n🩺 The IVF/ICSI service information also notes that multiple unsuccessful IUI attempts can be a reason to consider IVF-based treatment.\n📅 A consultation helps decide timing based on age, duration of infertility, reports, ovarian reserve, semen parameters, and prior treatment response.",
        "WEB-DRMADHU-003",
    ),
]


def special_answer(query: str) -> tuple[str, str] | None:
    if is_greeting(query):
        return (
            "👋 **Hello!** I can help with IVF, ICSI, IUI, PCOS, endometriosis, fertility preservation, and appointments.\n🩺 Tell me what you’d like to know, and I’ll keep it crisp.",
            "",
        )
    if is_identity_question(query):
        return (
            "👋 **I’m Dr. Madhu Patil’s Clinic assistant.**\n✨ I help with clinic services, fertility topics, appointments, and general patient questions.\n🩺 I keep answers short, clear, and grounded in clinic information.\n📅 If you need personal guidance, Dr. Madhu Patil’s team can help with an appointment.",
            "",
        )
    return find_faq_answer(query)


def find_faq_answer(question: str) -> tuple[str, str] | None:
    query_terms = terms(question)
    query_text = " ".join(sorted(query_terms))
    raw = question.lower()
    for patterns, answer, doc_id in FAQ_ANSWERS:
        for pattern in patterns:
            pattern_terms = terms(pattern)
            if pattern in raw or pattern_terms.issubset(query_terms) or pattern in query_text:
                return sanitize_answer(answer), doc_id
    return None


def format_answer(document: RetrievalDocument, query: str = "") -> str:
    metadata = document.metadata or {}
    page_type = str(metadata.get("page_type") or "").lower()
    service_name = str(metadata.get("service_name") or document.title).strip()
    treatments = listify(metadata.get("treatments"))
    conditions = listify(metadata.get("conditions"))
    appointment_eligible = bool(metadata.get("appointment_eligible"))

    if page_type == "service":
        definition = treatment_definition_for(query, treatments)
        focus_parts = []
        if treatments:
            focus_parts.append("treatments such as " + readable_list(treatments[:4]))
        if conditions:
            focus_parts.append("conditions such as " + readable_list(conditions[:4]))
        focus = " and ".join(focus_parts) if focus_parts else "this fertility care topic"
        if definition:
            lines = [
                f"💡 {definition}",
                f"🩺 **Dr. Madhu Patil’s Clinic** offers {service_name}.",
                f"🔎 This is relevant to {focus}.",
            ]
        else:
            lines = [
                f"🩺 **Yes.** Dr. Madhu Patil’s Clinic offers {service_name}.",
                f"🔎 This is relevant to {focus}.",
            ]
        if appointment_eligible:
            lines.append("📅 For personal guidance, __booking a consultation__ is the best next step.")
        else:
            lines.append("📅 For personal medical advice, please discuss directly with Dr. Madhu Patil’s Clinic.")
        return sanitize_answer("\n".join(lines[:4]))

    lines = [
        "ℹ️ **Dr. Madhu Patil’s Clinic** provides gynecology and fertility care across routine women’s health and advanced fertility services.",
        "🩺 Dr. Madhu Patil is described as a Gynecologist and IVF Specialist with 13+ years in obstetrics and gynecology and 9+ years in infertility and ART.",
        "🌟 The clinic highlights fertility assessment, IVF/ICSI, IUI, fertility preservation, PCOS/endometriosis care, and immunotherapy in infertility.",
        "📅 For personal guidance, __booking a consultation__ is the best next step.",
    ]
    return sanitize_answer("\n".join(lines[:4]))


def not_sure_answer() -> str:
    return "🤔 At present, I’m not sure about that.\n📅 Dr. Madhu Patil’s team can help you with a __doctor appointment__ for more information."


def retrieval_for_document(document: RetrievalDocument | None, mode: str) -> dict:
    if document is None:
        return {}
    return {
        "doc_id": document.doc_id,
        "source_type": document.source_type,
        "title": document.title,
        "url": document.url,
        "score": 1.0,
        "keyword_score": 1.0,
        "vector_score": 1.0,
        "rank": 1,
        "metadata": document.metadata,
        "mode": mode,
        "filter_mode": "faq",
        "filters": {},
    }


def sanitize_answer(answer: str) -> str:
    value = " ".join(str(answer or "").split())
    replacements = {
        "The approved clinic information does not specify": "At present, I’m not sure about",
        "the approved clinic information does not specify": "at present, I’m not sure about",
        "The provided information": "Dr. Madhu Patil’s Clinic information",
        "the provided information": "Dr. Madhu Patil’s Clinic information",
        "The website": "Dr. Madhu Patil’s Clinic",
        "the website": "Dr. Madhu Patil’s Clinic",
        "website content": "clinic information",
        "provided context": "clinic information",
        "approved context": "clinic information",
        "retrieved page": "clinic page",
        "retrieved pages": "clinic pages",
        "Dr. Madhu Patil's team covers": "Dr. Madhu Patil’s Clinic offers",
        "Dr. Madhu Patil’s team covers": "Dr. Madhu Patil’s Clinic offers",
        "Dr. Madhu Patil's team offers": "Dr. Madhu Patil’s Clinic offers",
        "Dr. Madhu Patil’s team offers": "Dr. Madhu Patil’s Clinic offers",
        "Dr. Madhu Patil's team can provide personalized": "Dr. Madhu Patil’s Clinic can provide personalized",
        "Dr. Madhu Patil’s team can provide personalized": "Dr. Madhu Patil’s Clinic can provide personalized",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    value = split_icon_bullets(value)
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    if not lines:
        return not_sure_answer()
    return "\n".join(lines[:4])


def split_icon_bullets(value: str) -> str:
    icons = ["💖", "✨", "🩺", "📅", "📞", "😊", "🌟", "🔎", "💡", "👋", "🤔", "☀️", "ℹ️"]
    for icon in icons:
        value = value.replace(f" {icon} ", f"\n{icon} ")
    return value.strip()


def is_identity_question(question: str) -> bool:
    stripped = question.strip().lower().rstrip("?.!")
    query_terms = terms(question)
    if stripped in IDENTITY_TERMS:
        return True
    return bool(query_terms.intersection(IDENTITY_TERMS))


def is_greeting(question: str) -> bool:
    query_terms = terms(question)
    stripped = question.strip().lower()
    return stripped in GREETING_TERMS or bool(query_terms.intersection(GREETING_TERMS)) and len(query_terms) <= 3


def treatment_definition_for(question: str, treatments: list[str]) -> str:
    query_terms = terms(question)
    if not query_terms.intersection(DEFINITION_TERMS):
        return ""
    treatment_terms = set(treatments).intersection(TREATMENT_DEFINITIONS)
    requested_terms = query_terms.intersection(TREATMENT_DEFINITIONS)
    for term in sorted(requested_terms.union(treatment_terms)):
        if term in query_terms:
            return TREATMENT_DEFINITIONS[term]
    return ""


def terms(text: str) -> set[str]:
    return set(tokenize_with_ngrams(text, max_n=4))


def listify(value) -> list[str]:
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    if value:
        return [str(value).strip()]
    return []


def readable_list(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + f", and {items[-1]}"
