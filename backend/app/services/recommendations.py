"""
PlantSathi AI Backend - Rule-Based Recommendation Engine
Provides evidence-based plant care advice based on identification and
disease classification results.  No fabricated data.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------
Recommendation = Dict[str, str]
"""Keys: category, title, description, urgency ('high' | 'medium' | 'low')."""


# ---------------------------------------------------------------------------
# Knowledge base: disease-specific recommendations
# ---------------------------------------------------------------------------
_DISEASE_RULES: Dict[str, List[Recommendation]] = {
    # ------- Tomato -------
    "tomato___early_blight": [
        {
            "category": "Treatment",
            "title": "Apply copper-based fungicide",
            "description": (
                "Spray copper hydroxide or copper oxychloride fungicide on all "
                "leaf surfaces at 7–10 day intervals.  Begin at first sign of "
                "lesions and continue through wet periods."
            ),
            "urgency": "high",
        },
        {
            "category": "Sanitation",
            "title": "Remove infected foliage",
            "description": (
                "Prune and destroy lower leaves showing the characteristic "
                "brown concentric-ring lesions.  Do not compost infected "
                "material; bag and discard to prevent spore spread."
            ),
            "urgency": "high",
        },
        {
            "category": "Cultural Practice",
            "title": "Improve air circulation",
            "description": (
                "Stake or cage plants to keep foliage off the soil.  Maintain "
                "adequate spacing (45–60 cm) between plants to reduce humidity "
                "around leaves."
            ),
            "urgency": "medium",
        },
        {
            "category": "Irrigation",
            "title": "Switch to drip or base watering",
            "description": (
                "Water at the base of the plant early in the morning so leaves "
                "dry quickly.  Avoid overhead irrigation, which keeps foliage "
                "wet and favours Alternaria sporulation."
            ),
            "urgency": "medium",
        },
        {
            "category": "Prevention",
            "title": "Mulch and rotate crops",
            "description": (
                "Apply 5–8 cm of organic mulch around plants to reduce soil-splash "
                "inoculum.  Rotate tomatoes with non-solanaceous crops for at "
                "least 2 years to break the disease cycle."
            ),
            "urgency": "low",
        },
    ],
    "tomato___late_blight": [
        {
            "category": "Treatment",
            "title": "Apply systemic fungicide immediately",
            "description": (
                "Use a fungicide containing mancozeb, chlorothalonil, or a "
                "systemic like metalaxyl-M at label rates.  Late blight spreads "
                "rapidly in cool wet conditions – treat within 24 hours of "
                "detection."
            ),
            "urgency": "high",
        },
        {
            "category": "Sanitation",
            "title": "Remove and destroy all affected tissue",
            "description": (
                "Cut off and bag infected stems, leaves, and fruit.  Late "
                "blight lesions release millions of sporangia; even brief "
                "contact with healthy tissue can infect it."
            ),
            "urgency": "high",
        },
        {
            "category": "Monitoring",
            "title": "Scout daily during cool, wet weather",
            "description": (
                "Phytophthora infestans thrives at 10–25 °C with high humidity. "
                "Inspect upper and lower leaf surfaces every day and act at the "
                "first appearance of water-soaked lesions."
            ),
            "urgency": "high",
        },
        {
            "category": "Irrigation",
            "title": "Reduce leaf wetness duration",
            "description": (
                "Avoid overhead watering.  If using sprinklers, water early so "
                "foliage dries before evening.  Consider plastic mulch to reduce "
                "soil moisture evaporation."
            ),
            "urgency": "medium",
        },
        {
            "category": "Prevention",
            "title": "Plant certified disease-free seed/transplants",
            "description": (
                "Start with pathogen-free transplants from a reputable nursery. "
                "Choose resistant varieties such as Mountain Magic, Defiant, or "
                "Legend where available."
            ),
            "urgency": "low",
        },
    ],
    "tomato___bacterial_spot": [
        {
            "category": "Treatment",
            "title": "Copper bactericide application",
            "description": (
                "Apply copper-based bactericide (e.g., copper octanoate or "
                "copper hydroxide) preventively and after rain events.  "
                "Combine with mancozeb to slow resistance development."
            ),
            "urgency": "high",
        },
        {
            "category": "Sanitation",
            "title": "Remove heavily infected leaves",
            "description": (
                "Prune leaves with numerous water-soaked or dark raised lesions. "
                "Work when foliage is dry to avoid spreading the bacterium on "
                "wet hands or tools."
            ),
            "urgency": "high",
        },
        {
            "category": "Cultural Practice",
            "title": "Disinfect tools between plants",
            "description": (
                "Wipe pruning shears and stakes with 70 % isopropanol or a 10 % "
                "bleach solution between every plant.  Xanthomonas spreads "
                "readily on contaminated surfaces."
            ),
            "urgency": "medium",
        },
    ],
    "tomato___leaf_mold": [
        {
            "category": "Environment",
            "title": "Reduce greenhouse humidity below 85 %",
            "description": (
                "Leaf mold (Passalora fulva) thrives in humid conditions. "
                "Increase ventilation, use fans, and space plants to reduce "
                "relative humidity below 85 %."
            ),
            "urgency": "high",
        },
        {
            "category": "Treatment",
            "title": "Apply contact fungicide",
            "description": (
                "Chlorothalonil or mancozeb applied to leaf undersides will "
                "suppress sporulation.  Repeat every 7 days during humid periods."
            ),
            "urgency": "medium",
        },
    ],
    "tomato___septoria_leaf_spot": [
        {
            "category": "Treatment",
            "title": "Fungicide rotation",
            "description": (
                "Rotate between chlorothalonil, mancozeb, and copper fungicides "
                "on a 7–10 day schedule to delay resistance build-up in "
                "Septoria lycopersici populations."
            ),
            "urgency": "high",
        },
        {
            "category": "Sanitation",
            "title": "Remove lower infected leaves",
            "description": (
                "Septoria infections begin on the lowest leaves. Remove and "
                "dispose of affected foliage to slow upward spread through the "
                "canopy."
            ),
            "urgency": "high",
        },
    ],
    "tomato___spider_mites two-spotted_spider_mite": [
        {
            "category": "Treatment",
            "title": "Apply miticide or insecticidal soap",
            "description": (
                "Spray the undersides of leaves with insecticidal soap, neem "
                "oil, or a registered miticide.  Spider mites develop resistance "
                "quickly; rotate active ingredients each generation."
            ),
            "urgency": "high",
        },
        {
            "category": "Biological Control",
            "title": "Introduce predatory mites",
            "description": (
                "Release Phytoseiulus persimilis or Neoseiulus californicus at "
                "the first sign of infestation.  Predatory mites provide "
                "long-term suppression under moderate temperatures."
            ),
            "urgency": "medium",
        },
    ],
    "tomato___target_spot": [
        {
            "category": "Treatment",
            "title": "Fungicide application",
            "description": (
                "Apply azoxystrobin or chlorothalonil at 7-day intervals. "
                "Target spot (Corynespora cassiicola) responds well to "
                "QoI-class fungicides."
            ),
            "urgency": "high",
        },
    ],
    "tomato___tomato_yellow_leaf_curl_virus": [
        {
            "category": "Vector Control",
            "title": "Control whitefly populations",
            "description": (
                "TYLCV is transmitted by Bemisia tabaci whiteflies. Apply "
                "systemic insecticides (imidacloprid or spirotetramat) and use "
                "yellow sticky traps to monitor and reduce vector populations."
            ),
            "urgency": "high",
        },
        {
            "category": "Cultural Practice",
            "title": "Remove infected plants and use reflective mulch",
            "description": (
                "Remove and destroy symptomatic plants promptly – they are "
                "permanent inoculum sources.  Silver reflective mulch repels "
                "whiteflies and reduces landing rates."
            ),
            "urgency": "high",
        },
        {
            "category": "Prevention",
            "title": "Use resistant cultivars",
            "description": (
                "Plant TYLCV-resistant tomato varieties (e.g., Hazera 3402, "
                "Shanty) when available in your region."
            ),
            "urgency": "low",
        },
    ],
    "tomato___tomato_mosaic_virus": [
        {
            "category": "Sanitation",
            "title": "Strict hygiene protocols",
            "description": (
                "ToMV spreads mechanically via hands, clothing, and tools. "
                "Wash hands with soap and water before entering the field. "
                "Disinfect tools with 10 % bleach after every plant."
            ),
            "urgency": "high",
        },
        {
            "category": "Cultural Practice",
            "title": "Remove and destroy infected plants",
            "description": (
                "There is no cure for ToMV infection.  Remove symptomatic "
                "plants promptly, seal in bags, and dispose of them away "
                "from the growing area."
            ),
            "urgency": "high",
        },
    ],
    # ------- Potato -------
    "potato___early_blight": [
        {
            "category": "Treatment",
            "title": "Apply protectant fungicide",
            "description": (
                "Mancozeb or chlorothalonil applied before and after first "
                "symptom appearance protects foliage from Alternaria solani. "
                "Repeat at 7–14 day intervals."
            ),
            "urgency": "high",
        },
        {
            "category": "Nutrition",
            "title": "Ensure adequate nitrogen levels",
            "description": (
                "Early blight is more severe in nitrogen-stressed plants. "
                "Conduct a soil test and maintain balanced N-P-K nutrition "
                "throughout the season."
            ),
            "urgency": "medium",
        },
    ],
    "potato___late_blight": [
        {
            "category": "Treatment",
            "title": "Emergency systemic fungicide application",
            "description": (
                "Apply metalaxyl-M or cymoxanil + mancozeb immediately. "
                "Potato late blight (P. infestans) can destroy an entire crop "
                "within days in cool, wet weather."
            ),
            "urgency": "high",
        },
        {
            "category": "Sanitation",
            "title": "Destroy infected haulm and tubers",
            "description": (
                "Do not harvest during active infection.  Kill infected haulm "
                "with desiccant herbicide 2 weeks before harvest to allow "
                "tuber skin to set and prevent tuber blight."
            ),
            "urgency": "high",
        },
    ],
    # ------- Pepper -------
    "pepper,_bell___bacterial_spot": [
        {
            "category": "Treatment",
            "title": "Copper bactericide spray",
            "description": (
                "Apply copper hydroxide or copper sulfate at label rates. "
                "Begin preventively and intensify during warm, wet, and "
                "stormy weather when Xanthomonas spread is greatest."
            ),
            "urgency": "high",
        },
    ],
    # ------- Apple -------
    "apple___apple_scab": [
        {
            "category": "Treatment",
            "title": "Fungicide application during primary season",
            "description": (
                "Apply myclobutanil, captan, or mancozeb from green tip through "
                "petal fall – the critical primary infection period. "
                "Maintain spray intervals of 5–10 days during wet spring weather."
            ),
            "urgency": "high",
        },
        {
            "category": "Sanitation",
            "title": "Rake and destroy fallen leaves",
            "description": (
                "Venturia inaequalis overwinters on infected leaf litter. "
                "Collect and bury or compost fallen leaves to reduce primary "
                "inoculum for the following spring."
            ),
            "urgency": "medium",
        },
    ],
    "apple___black_rot": [
        {
            "category": "Sanitation",
            "title": "Remove mummified fruit and dead wood",
            "description": (
                "Botryosphaeria obtusa overwinters in mummified fruit and "
                "dead branches.  Prune out cankers to healthy wood, remove "
                "mummies, and destroy all debris."
            ),
            "urgency": "high",
        },
        {
            "category": "Treatment",
            "title": "Captan or thiophanate-methyl fungicide",
            "description": (
                "Apply from pink bud through first cover sprays.  Black rot "
                "infection of fruit primarily occurs during petal fall when "
                "calyx ends are exposed."
            ),
            "urgency": "high",
        },
    ],
    "apple___cedar_apple_rust": [
        {
            "category": "Cultural Practice",
            "title": "Remove nearby juniper/cedar hosts",
            "description": (
                "Gymnosporangium juniperi-virginianae requires both apple and "
                "eastern red cedar (or other juniper species) to complete its "
                "life cycle.  Remove or relocate susceptible junipers within "
                "300 m if feasible."
            ),
            "urgency": "medium",
        },
        {
            "category": "Treatment",
            "title": "Apply myclobutanil or propiconazole",
            "description": (
                "Apply DMI-class fungicides from pink through second cover to "
                "protect young tissue during the narrow infection window in spring."
            ),
            "urgency": "high",
        },
    ],
    # ------- Grape -------
    "grape___black_rot": [
        {
            "category": "Treatment",
            "title": "Myclobutanil or mancozeb fungicide",
            "description": (
                "Protect young berries from capstone to one-half inch shoot "
                "growth through bunch closure.  This is the critical infection "
                "window for Guignardia bidwellii."
            ),
            "urgency": "high",
        },
        {
            "category": "Sanitation",
            "title": "Remove mummified berries",
            "description": (
                "Mummies on the vine are the primary overwintering source. "
                "Remove them during pruning and destroy them off-site."
            ),
            "urgency": "high",
        },
    ],
    # ------- Corn -------
    "corn_(maize)___cercospora_leaf_spot gray_leaf_spot": [
        {
            "category": "Cultural Practice",
            "title": "Improve field air circulation",
            "description": (
                "Gray leaf spot (Cercospora zeae-maydis) is worst in fields "
                "with poor drainage or dense canopy.  Reduce plant density "
                "where possible and rotate away from corn for 1–2 seasons."
            ),
            "urgency": "medium",
        },
        {
            "category": "Treatment",
            "title": "Foliar fungicide at early tassel",
            "description": (
                "Apply strobilurin (azoxystrobin) or triazole fungicide at VT "
                "(tasseling) stage when disease pressure is moderate to high. "
                "Economic return is greatest on susceptible hybrids."
            ),
            "urgency": "medium",
        },
    ],
    "corn_(maize)___common_rust_": [
        {
            "category": "Treatment",
            "title": "Foliar fungicide application",
            "description": (
                "Apply triazole or strobilurin fungicide at first pustule "
                "detection, especially in sweet corn or seed corn production "
                "where common rust (Puccinia sorghi) causes economic loss."
            ),
            "urgency": "medium",
        },
        {
            "category": "Prevention",
            "title": "Plant resistant hybrids",
            "description": (
                "Select commercially available corn hybrids with Rp resistance "
                "genes that provide race-specific resistance to Puccinia sorghi."
            ),
            "urgency": "low",
        },
    ],
    "corn_(maize)___northern_leaf_blight": [
        {
            "category": "Treatment",
            "title": "Strobilurin fungicide at tasseling",
            "description": (
                "Apply azoxystrobin or pyraclostrobin at VT stage under high "
                "disease pressure.  Northern leaf blight (Exserohilum turcicum) "
                "reduces yield most when lesions appear before silking."
            ),
            "urgency": "high",
        },
        {
            "category": "Cultural Practice",
            "title": "Crop rotation and residue management",
            "description": (
                "Rotate with non-host crops and till under corn residue after "
                "harvest to reduce overwintering conidia in the field."
            ),
            "urgency": "medium",
        },
    ],
    # ------- General powdery mildew -------
    "cherry_(including_sour)___powdery_mildew": [
        {
            "category": "Treatment",
            "title": "Sulfur or potassium bicarbonate spray",
            "description": (
                "Apply wettable sulfur or potassium bicarbonate at 7-day "
                "intervals.  Powdery mildews (Podosphaera spp.) are highly "
                "sensitive to sulfur-based products."
            ),
            "urgency": "high",
        },
    ],
    "squash___powdery_mildew": [
        {
            "category": "Treatment",
            "title": "Potassium bicarbonate or neem oil",
            "description": (
                "Apply potassium bicarbonate (e.g., Kaligreen) or neem oil at "
                "7-day intervals.  These products disrupt powdery mildew "
                "(Podosphaera xanthii) colonies on leaf surfaces."
            ),
            "urgency": "high",
        },
        {
            "category": "Cultural Practice",
            "title": "Increase spacing and airflow",
            "description": (
                "Ensure plants have 90–120 cm between centres and train vines "
                "to maximise air movement through the canopy."
            ),
            "urgency": "medium",
        },
    ],
    # ------- Strawberry -------
    "strawberry___leaf_scorch": [
        {
            "category": "Treatment",
            "title": "Captan fungicide application",
            "description": (
                "Apply captan at 10–14 day intervals during wet spring weather. "
                "Leaf scorch (Diplocarpon earlianum) spreads rapidly through "
                "rain-splash."
            ),
            "urgency": "high",
        },
        {
            "category": "Cultural Practice",
            "title": "Renovate planting after harvest",
            "description": (
                "Mow, thin, and fertilise the bed after harvest to remove "
                "infected older leaves and promote fresh, healthy regrowth."
            ),
            "urgency": "medium",
        },
    ],
    # ------- Peach -------
    "peach___bacterial_spot": [
        {
            "category": "Treatment",
            "title": "Copper hydroxide spray schedule",
            "description": (
                "Apply copper hydroxide at delayed dormant, then weekly from "
                "petal fall through shuck split.  Bacterial spot (Xanthomonas "
                "arboricola pv. pruni) is most damaging on fruit and leaves in "
                "warm rainy weather."
            ),
            "urgency": "high",
        },
        {
            "category": "Prevention",
            "title": "Plant resistant varieties",
            "description": (
                "Choose moderately resistant peach cultivars such as Contender, "
                "Redhaven, or Harrow Beauty to reduce spray requirements."
            ),
            "urgency": "low",
        },
    ],
    # ------- Orange -------
    "orange___haunglongbing_(citrus_greening)": [
        {
            "category": "Vector Control",
            "title": "Control Asian citrus psyllid immediately",
            "description": (
                "HLB (caused by Candidatus Liberibacter asiaticus) has no cure. "
                "The Asian citrus psyllid (Diaphorina citri) transmits the "
                "pathogen.  Apply systemic insecticide (imidacloprid soil drench) "
                "to slow psyllid populations."
            ),
            "urgency": "high",
        },
        {
            "category": "Sanitation",
            "title": "Remove infected trees",
            "description": (
                "Infected trees are permanent inoculum sources.  Remove and "
                "destroy symptomatic trees according to local regulatory "
                "guidelines to protect neighbouring orchards."
            ),
            "urgency": "high",
        },
        {
            "category": "Nutrition",
            "title": "Nutritional therapy to prolong tree productivity",
            "description": (
                "Foliar micronutrient sprays (zinc, manganese, boron) and "
                "enhanced soil nutrition can slow symptom progression and "
                "maintain some productivity in mildly affected trees."
            ),
            "urgency": "medium",
        },
    ],
}

# ---------------------------------------------------------------------------
# Healthy plant recommendations (general)
# ---------------------------------------------------------------------------
_HEALTHY_RECOMMENDATIONS: List[Recommendation] = [
    {
        "category": "Watering",
        "title": "Maintain consistent soil moisture",
        "description": (
            "Water deeply and infrequently to encourage deep root growth. "
            "Allow the top 2–3 cm of soil to dry between waterings. "
            "Always water at the base of the plant to keep foliage dry."
        ),
        "urgency": "low",
    },
    {
        "category": "Nutrition",
        "title": "Regular balanced fertilisation",
        "description": (
            "Apply a balanced NPK fertiliser (e.g., 10-10-10) according to "
            "soil test results.  Switch to a low-nitrogen, high-potassium "
            "formula during fruiting to support quality and disease resistance."
        ),
        "urgency": "low",
    },
    {
        "category": "Monitoring",
        "title": "Weekly scouting routine",
        "description": (
            "Inspect both surfaces of leaves weekly for early signs of pest "
            "or disease activity.  Early detection is the most cost-effective "
            "plant protection strategy."
        ),
        "urgency": "low",
    },
    {
        "category": "Prevention",
        "title": "Maintain plant hygiene",
        "description": (
            "Remove dead or yellowing foliage promptly.  Sterilise pruning "
            "tools between plants.  Avoid working in the garden when foliage "
            "is wet."
        ),
        "urgency": "low",
    },
]

# ---------------------------------------------------------------------------
# General fallback recommendations (unknown plant/disease)
# ---------------------------------------------------------------------------
_FALLBACK_RECOMMENDATIONS: List[Recommendation] = [
    {
        "category": "Assessment",
        "title": "Consult a local agronomist",
        "description": (
            "For unconfirmed disease identifications, bring a fresh leaf "
            "sample to your local agricultural extension office or certified "
            "crop adviser for laboratory confirmation."
        ),
        "urgency": "medium",
    },
    {
        "category": "Cultural Practice",
        "title": "Improve general growing conditions",
        "description": (
            "Ensure adequate spacing, good drainage, and appropriate soil pH "
            "for your crop.  Stress-free plants are significantly more "
            "resistant to disease and pest pressure."
        ),
        "urgency": "low",
    },
    {
        "category": "Monitoring",
        "title": "Document and track symptom progression",
        "description": (
            "Photograph affected areas every 2–3 days to track whether "
            "symptoms are spreading or stabilising.  This information is "
            "invaluable for diagnosis and treatment decisions."
        ),
        "urgency": "low",
    },
]


class RecommendationService:
    """
    Rule-based recommendation engine.

    All advice is derived from published plant pathology and agronomy
    guidelines.  No data is fabricated.
    """

    def get_recommendations(
        self,
        plant_name: str,
        disease_label: str,
        is_healthy: bool,
    ) -> List[Recommendation]:
        """
        Return a list of care recommendations for the given plant/disease.

        Parameters
        ----------
        plant_name:
            Common name of the identified plant (e.g., ``"Tomato"``).
        disease_label:
            Raw PlantVillage label (e.g., ``"Tomato___Early_blight"``).
        is_healthy:
            True when the disease model predicted the plant is healthy.

        Returns
        -------
        List[Recommendation]
            Each entry is a dict with keys:
            ``category``, ``title``, ``description``, ``urgency``.
        """
        if is_healthy:
            return _HEALTHY_RECOMMENDATIONS

        key = disease_label.lower().strip()
        if key in _DISEASE_RULES:
            logger.debug("Found specific recommendations for label '%s'.", key)
            return _DISEASE_RULES[key]

        # Partial match: look for plant-level recommendations
        plant_key = plant_name.lower().strip()
        for rule_key, rules in _DISEASE_RULES.items():
            if plant_key and rule_key.startswith(plant_key):
                logger.debug(
                    "Partial match: using recommendations for rule key '%s'.", rule_key
                )
                return rules

        logger.debug(
            "No specific recommendations found for plant='%s' disease='%s'. "
            "Returning general fallback advice.",
            plant_name,
            disease_label,
        )
        return _FALLBACK_RECOMMENDATIONS


# Module-level singleton
recommendation_service = RecommendationService()
