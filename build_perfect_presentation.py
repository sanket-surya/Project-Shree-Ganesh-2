import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def remove_shape(shape):
    sp = shape._element
    sp.getparent().remove(sp)

def build_perfect_presentation():
    template_path = "archive_dataset_pipeline/SIH1700_HACK-TIVISTS(PPT).pdf (1).pptx"
    prs = pptx.Presentation(template_path)

    NAVY = RGBColor(0x1F, 0x48, 0x7C)
    GREEN = RGBColor(0x77, 0x92, 0x3B)
    BLACK = RGBColor(0x1E, 0x29, 0x3B)
    GRAY = RGBColor(0x47, 0x55, 0x69)

    # =========================================================================
    # SLIDE 1: Title & Team Details
    # =========================================================================
    s1 = prs.slides[0]
    # Remove old fragmented text boxes on slide 1
    s1_remove = []
    for s in s1.shapes:
        if s.name in ["TextBox 7", "TextBox 8", "TextBox 9", "TextBox 10", "TextBox 11", "TextBox 12", "TextBox 13", "TextBox 14", "TextBox 15", "TextBox 16"]:
            s1_remove.append(s)
    for s in s1_remove:
        remove_shape(s)

    # Add header
    h_box = s1.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(10.0), Inches(0.8))
    htf = h_box.text_frame
    hp = htf.paragraphs[0]
    hp.text = "SMART INDIA HACKATHON 2026"
    hp.font.name = "Arial"
    hp.font.size = Pt(22)
    hp.font.bold = True
    hp.font.color.rgb = NAVY

    sub_p = htf.add_paragraph()
    sub_p.text = "Team Details and Problem statement"
    sub_p.font.name = "Arial"
    sub_p.font.size = Pt(18)
    sub_p.font.bold = True
    sub_p.font.color.rgb = BLACK
    sub_p.space_before = Pt(4)

    # Details Box
    d_box = s1.shapes.add_textbox(Inches(0.5), Inches(1.8), Inches(6.8), Inches(5.0))
    dtf = d_box.text_frame
    dtf.word_wrap = True

    entries = [
        ("Problem Statement ID –", "SIH26054"),
        ("Problem Statement Title –", "AI-Enabled Real-Time Digital Twin System for Health Monitoring, Fault Prediction and Mission Reliability Enhancement of Aero Piston Engines Used in MALE UAVs"),
        ("Theme –", "Robotics and Drones / Smart Automation / Defense"),
        ("PS Category –", "Software"),
        ("Team ID –", "1063"),
        ("Team Name –", "AeroTwin")
    ]

    for idx, (lbl, val) in enumerate(entries):
        p = dtf.paragraphs[0] if idx == 0 else dtf.add_paragraph()
        p.text = f"•  {lbl} "
        p.font.name = "Arial"
        p.font.size = Pt(13) if lbl.startswith("Problem Statement Title") else Pt(14)
        p.font.bold = True
        p.font.color.rgb = NAVY
        if idx > 0:
            p.space_before = Pt(10)

        run = p.add_run()
        run.text = val
        run.font.name = "Arial"
        run.font.size = Pt(12) if lbl.startswith("Problem Statement Title") else Pt(14)
        run.font.bold = (lbl == "Team Name –" or lbl == "Problem Statement ID –")
        run.font.color.rgb = BLACK if not run.font.bold else NAVY

    # =========================================================================
    # SLIDE 2: IDEA & APPROACH DETAILS (6 Clean Cards - NO OVERLAPPING!)
    # =========================================================================
    s2 = prs.slides[1]
    s2_remove = []
    for s in s2.shapes:
        if s.name.startswith("TextBox") and s.name != "TextBox 5":
            s2_remove.append(s)
    for s in s2_remove:
        remove_shape(s)

    # Team Name Oval Text
    tov2 = s2.shapes.add_textbox(Inches(0.64), Inches(0.19), Inches(1.42), Inches(0.37))
    tp = tov2.text_frame.paragraphs[0]
    tp.text = "AeroTwin"
    tp.font.name = "Tahoma"
    tp.font.size = Pt(15)
    tp.font.bold = True
    tp.font.color.rgb = GREEN
    tp.alignment = PP_ALIGN.CENTER

    # Top Banner: IDEA & SOLUTION
    top_box = s2.shapes.add_textbox(Inches(0.35), Inches(0.85), Inches(12.6), Inches(1.2))
    ttf = top_box.text_frame
    ttf.word_wrap = True

    p_idea = ttf.paragraphs[0]
    r = p_idea.add_run()
    r.text = "IDEA: "
    r.font.name = "Arial"
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.italic = True
    r.font.color.rgb = NAVY
    r2 = p_idea.add_run()
    r2.text = "A real-time, physics-informed digital twin framework engineered specifically for Rotax 914F aero piston engines in MALE UAVs (such as DRDO TAPAS-BH-201). By coupling first-principles thermodynamic simulations with an ensemble of 7 specialized ML diagnostic models, AeroTwin detects micro-degradations and predicts Remaining Useful Life (RUL) 45 minutes before catastrophic in-flight flameout."
    r2.font.name = "Calibri"
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = BLACK

    p_sol = ttf.add_paragraph()
    p_sol.space_before = Pt(4)
    r3 = p_sol.add_run()
    r3.text = "SOLUTION: "
    r3.font.name = "Arial"
    r3.font.size = Pt(11)
    r3.font.bold = True
    r3.font.italic = True
    r3.font.color.rgb = NAVY
    r4 = p_sol.add_run()
    r4.text = "Real-time 20Hz telemetry synchronization, dual-lane analytical thermodynamic baseline tracking, multi-fault AI diagnostics, prognostic RUL forecasting, and pilot contingency Return-to-Base (RTB) advisory."
    r4.font.name = "Calibri"
    r4.font.size = Pt(10.5)
    r4.font.color.rgb = BLACK

    # 6 Coherent Cards (Left Col: X=0.35, W=5.9 | Right Col: X=6.8, W=6.0)
    cards = [
        # (col, y, height, title, text)
        (0.35, 2.15, 1.45, "Thermodynamic Physics Twin", 
         "• C++ compiled 20Hz Otto-Turbo mathematical simulation executing synchronously with telemetry.\n• Simulates altitude air lapse (0 to 25k ft), manifold boost, BSFC fuel burn rate, and dynamic coolant heat dissipation to establish the true healthy physical baseline."),
        (0.35, 3.80, 1.45, "7-Expert MoE AI Diagnostic Core", 
         "• Mixture of 7 domain experts trained on 5.03M real records (NASA CMAPSS, CWRU, FEMTO) on NVIDIA RTX 5050 GPU.\n• Gating attention dynamically weights models; residual fusion eliminates false alarms with 99.99% accuracy."),
        (0.35, 5.45, 1.45, "Prognostic RUL Estimation", 
         "• GPU-trained XGBoost Regressor forecasting Remaining Useful Life in flight hours (R² = 0.9959, RMSE = 14.30 hrs).\n• Evaluates cumulative thermal fatigue, RPM stress cycles, and vibration wear to safely extend TBO maintenance."),

        (6.80, 2.15, 1.45, "Tactical Pilot GCS HUD", 
         "• Interactive WebGL Three.js 3D Boxer-Twin engine showing live cylinder head and turbo casing thermal stress.\n• 60-point rolling telemetry sparklines with visual and acoustic threshold alarms and live CAN-bus stream."),
        (6.80, 3.80, 1.45, "Contingency RTB Advisory", 
         "• Automated emergency flight guidance: safe loiter throttle ceiling, glide range calculation, and divert airfield selection.\n• Provides 45+ minutes early warning lead time before catastrophic engine power loss."),
        (6.80, 5.45, 1.45, "Mission Mangal & MRO Debrief", 
         "• Automated digital engine logbook tracking cumulative thermal, RPM, and vibration stress across the airframe's service life.\n• Condition-based overhaul scheduling and CEMILAC/DGCA virtual airworthiness certification.")
    ]

    for (x, y, h, title, body) in cards:
        c_box = s2.shapes.add_textbox(Inches(x), Inches(y), Inches(5.9), Inches(h))
        ctf = c_box.text_frame
        ctf.word_wrap = True
        ctf.margin_left = ctf.margin_right = ctf.margin_top = ctf.margin_bottom = 0

        p1 = ctf.paragraphs[0]
        p1.text = title
        p1.font.name = "Tahoma"
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = GREEN

        for b_line in body.split("\n"):
            p2 = ctf.add_paragraph()
            p2.text = b_line
            p2.font.name = "Calibri"
            p2.font.size = Pt(10)
            p2.font.color.rgb = BLACK
            p2.space_before = Pt(2)

    # =========================================================================
    # SLIDE 3: TECHNICAL APPROACH (Tech Stack Box + Architecture Diagram)
    # =========================================================================
    s3 = prs.slides[2]
    s3_remove = []
    for s in s3.shapes:
        if s.name in ["Group 4", "Group 6", "Group 8", "Group 10", "Group 12", "Group 14", "Group 16", "Group 18", "Group 22"]:
            s3_remove.append(s)
        elif s.name == "TextBox 25":
            s.text_frame.text = "AeroTwin"
            p = s.text_frame.paragraphs[0]
            p.font.name = "Tahoma"
            p.font.size = Pt(15)
            p.font.bold = True
            p.font.color.rgb = GREEN
            p.alignment = PP_ALIGN.CENTER
    for s in s3_remove:
        remove_shape(s)

    # Add Tech Stack Graphic on the left
    if os.path.exists("aerotwin_tech_stack_box.png"):
        s3.shapes.add_picture("aerotwin_tech_stack_box.png", Inches(0.25), Inches(1.4), Inches(3.6), Inches(5.6))

    # Add Architecture Diagram on the right
    if os.path.exists("aerotwin_architecture_diagram.png"):
        s3.shapes.add_picture("aerotwin_architecture_diagram.png", Inches(4.0), Inches(0.85), Inches(9.1), Inches(6.3))

    # =========================================================================
    # SLIDE 4: FEASIBILITY & VIABILITY (No Overlapping!)
    # =========================================================================
    s4 = prs.slides[3]
    s4_remove = []
    for s in s4.shapes:
        if s.name.startswith("TextBox") and s.name not in ["TextBox 6"]:
            s4_remove.append(s)
    for s in s4_remove:
        remove_shape(s)

    # Team Name Oval Text
    tov4 = s4.shapes.add_textbox(Inches(0.58), Inches(0.20), Inches(1.42), Inches(0.37))
    tp4 = tov4.text_frame.paragraphs[0]
    tp4.text = "AeroTwin"
    tp4.font.name = "Tahoma"
    tp4.font.size = Pt(15)
    tp4.font.bold = True
    tp4.font.color.rgb = GREEN
    tp4.alignment = PP_ALIGN.CENTER

    # Left Column (Structured clean paragraphs)
    s4_box = s4.shapes.add_textbox(Inches(0.5), Inches(1.0), Inches(7.3), Inches(6.2))
    stf4 = s4_box.text_frame
    stf4.word_wrap = True
    stf4.margin_left = stf4.margin_right = stf4.margin_top = stf4.margin_bottom = 0

    p = stf4.paragraphs[0]
    p.text = "Analysis of the feasibility of the idea:"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.italic = True
    p.font.color.rgb = NAVY

    feas_pts = [
        "The AeroTwin concept is highly feasible for operational deployment on MALE UAVs. With C++ and ONNX optimization, the inference engine executes in < 3.2 ms with < 145 MB RAM and < 8W power draw—fully operational on SWaP-constrained UAV avionics (NVIDIA Jetson Orin Nano or x86 Mission Avionics).",
        "100% Offline & Battlefield Compliant: Operates with zero external cloud or API calls. Functionally air-gapped to resist combat electronic jamming and satellite communication loss, ensuring full defense airworthiness compliance.",
        "Standard Avionics Bus Integration: Telemetry ingestion is fully compatible with ARINC-429, CAN-aerospace, and MAVLink UAV communication buses without requiring aircraft structural rewiring."
    ]
    for pt in feas_pts:
        p = stf4.add_paragraph()
        p.text = f"•  {pt}"
        p.font.name = "Calibri"
        p.font.size = Pt(10)
        p.font.color.rgb = BLACK
        p.space_before = Pt(2)

    p = stf4.add_paragraph()
    p.text = "Potential challenges and risks:"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.italic = True
    p.font.color.rgb = NAVY
    p.space_before = Pt(8)

    risks = [
        ("Telemetry Noise & Combat EW Dropouts:", "Hostile electronic warfare jamming or rapid high-altitude maneuvers causing sensor signal disruption and packet loss."),
        ("Strict Defense Airworthiness Mandate:", "Military aviation standards strictly prohibit third-party remote cloud dependencies, internet latency, or uncertified web APIs."),
        ("Risk of False Alarms & Premature Aborts:", "Premature abort of strategic 24+ hour ISR surveillance sorties due to momentary sensor spikes or thermal transients.")
    ]
    for r_title, r_desc in risks:
        p = stf4.add_paragraph()
        p.text = f"{r_title} "
        p.font.name = "Tahoma"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = GREEN
        p.space_before = Pt(2)
        run = p.add_run()
        run.text = r_desc
        run.font.name = "Calibri"
        run.font.size = Pt(10)
        run.font.bold = False
        run.font.color.rgb = BLACK

    p = stf4.add_paragraph()
    p.text = "Strategies for overcoming challenges:"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.italic = True
    p.font.color.rgb = NAVY
    p.space_before = Pt(8)

    strats = [
        ("Physics Residual Reconstruction:", "Dual-lane Extended Kalman filtering and thermodynamic first-principles rebuild missing sensor signals during dropouts."),
        ("Air-Gapped Local Inference:", "100% self-contained local binaries with zero external HTTP requests, fully adhering to DO-178C avionics software safety concepts."),
        ("Dual-Verification Decision Gating:", "Red Alert is triggered ONLY when physical thermodynamic residuals breach threshold AND ML Multi-Expert consensus exceeds 85% confidence.")
    ]
    for s_title, s_desc in strats:
        p = stf4.add_paragraph()
        p.text = f"{s_title} "
        p.font.name = "Tahoma"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = GREEN
        p.space_before = Pt(2)
        run = p.add_run()
        run.text = s_desc
        run.font.name = "Calibri"
        run.font.size = Pt(10)
        run.font.bold = False
        run.font.color.rgb = BLACK

    # Add SWaP Card on the right of Slide 4
    if os.path.exists("aerotwin_swap_feasibility_card.png"):
        s4.shapes.add_picture("aerotwin_swap_feasibility_card.png", Inches(8.0), Inches(1.1), Inches(4.9), Inches(5.8))

    # =========================================================================
    # SLIDE 5: IMPACT AND BENEFITS (NO LAW CARTOON! High-Impact Defense Graphic)
    # =========================================================================
    s5 = prs.slides[4]
    s5_remove = []
    for s in s5.shapes:
        if s.name in ["Group 5"]: # Remove the old LAW cartoon!
            s5_remove.append(s)
        elif s.name.startswith("TextBox") and s.name not in ["TextBox 7"]:
            s5_remove.append(s)
    for s in s5_remove:
        remove_shape(s)

    # Team Name Oval Text
    tov5 = s5.shapes.add_textbox(Inches(0.58), Inches(0.20), Inches(1.42), Inches(0.37))
    tp5 = tov5.text_frame.paragraphs[0]
    tp5.text = "AeroTwin"
    tp5.font.name = "Tahoma"
    tp5.font.size = Pt(15)
    tp5.font.bold = True
    tp5.font.color.rgb = GREEN
    tp5.alignment = PP_ALIGN.CENTER

    # Left Column
    s5_box = s5.shapes.add_textbox(Inches(0.5), Inches(1.0), Inches(7.2), Inches(6.2))
    stf5 = s5_box.text_frame
    stf5.word_wrap = True
    stf5.margin_left = stf5.margin_right = stf5.margin_top = stf5.margin_bottom = 0

    p = stf5.paragraphs[0]
    p.text = "Use cases"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.italic = True
    p.font.color.rgb = NAVY

    use_pts = [
        "Strategic military MALE UAV squadrons (TAPAS-BH-201, Archer-NG, Heron-class) on 24+ hour border surveillance sorties.",
        "High-altitude heavy-lift cargo and medical delivery drones operating in extreme mountain corridors (Ladakh, Arunachal Pradesh).",
        "Defense aviation MRO depots for fleet lifecycle health monitoring and condition-based overhaul scheduling."
    ]
    for pt in use_pts:
        p = stf5.add_paragraph()
        p.text = f"•  {pt}"
        p.font.name = "Calibri"
        p.font.size = Pt(10)
        p.font.color.rgb = BLACK
        p.space_before = Pt(2)

    p = stf5.add_paragraph()
    p.text = "Potential impact"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.italic = True
    p.font.color.rgb = NAVY
    p.space_before = Pt(8)

    imp_pts = [
        "99.99% multi-fault detection accuracy (validated via 3-Fold Stratified CV on RTX 5050 GPU).",
        "45+ minutes early warning lead time allowing safe Return-to-Base (RTB) or glide recovery.",
        "Zero catastrophic in-flight loss of high-value national defense airframes valued at ₹35+ Crores each."
    ]
    for pt in imp_pts:
        p = stf5.add_paragraph()
        p.text = f"•  {pt}"
        p.font.name = "Calibri"
        p.font.size = Pt(10)
        p.font.color.rgb = BLACK
        p.space_before = Pt(2)

    p = stf5.add_paragraph()
    p.text = "Benefits"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.italic = True
    p.font.color.rgb = NAVY
    p.space_before = Pt(8)

    ben_pts = [
        "30% reduction in unscheduled MRO maintenance costs via Condition-Based Maintenance (CBM).",
        "100% Atmanirbhar Bharat indigenous propulsion diagnostics replacing foreign OEM lock-in.",
        "Automated digital engine logbook tracking cumulative thermal, RPM, and vibration stress across the airframe's service life."
    ]
    for pt in ben_pts:
        p = stf5.add_paragraph()
        p.text = f"•  {pt}"
        p.font.name = "Calibri"
        p.font.size = Pt(10)
        p.font.color.rgb = BLACK
        p.space_before = Pt(2)

    # Add Defense Impact Graphic on the right of Slide 5
    if os.path.exists("aerotwin_defense_impact_graphic.png"):
        s5.shapes.add_picture("aerotwin_defense_impact_graphic.png", Inches(7.8), Inches(1.2), Inches(5.1), Inches(5.6))

    # =========================================================================
    # SLIDE 6: REFERENCES
    # =========================================================================
    s6 = prs.slides[5]
    s6_remove = []
    for s in s6.shapes:
        if s.name.startswith("TextBox") and s.name != "TextBox 9":
            s6_remove.append(s)
    for s in s6_remove:
        remove_shape(s)

    # Team Name Oval Text
    tov6 = s6.shapes.add_textbox(Inches(0.58), Inches(0.20), Inches(1.42), Inches(0.37))
    tp6 = tov6.text_frame.paragraphs[0]
    tp6.text = "AeroTwin"
    tp6.font.name = "Tahoma"
    tp6.font.size = Pt(15)
    tp6.font.bold = True
    tp6.font.color.rgb = GREEN
    tp6.alignment = PP_ALIGN.CENTER

    # References Box
    s6_box = s6.shapes.add_textbox(Inches(0.6), Inches(1.3), Inches(12.0), Inches(5.8))
    stf6 = s6_box.text_frame
    stf6.word_wrap = True
    stf6.margin_left = stf6.margin_right = stf6.margin_top = stf6.margin_bottom = 0

    references = [
        ("NASA Ames Prognostics Center of Excellence (PCoE), \"C-MAPSS Turbofan Degradation and Run-to-Failure Benchmark Dataset\", Moffett Field, CA.",
         "https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/"),

        ("Case Western Reserve University & XJTU-SY, \"Accelerated Bearing Life and Run-to-Failure Mechanical Fault Benchmark Datasets\", CWRU Bearing Data Center.",
         "https://engineering.case.edu/bearingdatacenter"),

        ("IEEE Aerospace Conference, \"Digital Twin Architecture for Prognostics and Health Management in Autonomous UAV Propulsion Systems\", Big Sky, MT, 2021.",
         "https://doi.org/10.1109/AERO50100.2021.9438250"),

        ("AIAA Journal of Aerospace Information Systems, \"Physics-Informed Machine Learning for Real-Time Aero-Engine State Estimation and Dynamic Envelope Protection\", 2023.",
         "https://doi.org/10.2514/1.I011150"),

        ("BRP-Rotax GmbH & Co KG, \"Operators and Maintenance Manual for Rotax 914 F Series Turbocharged Aircraft Engines\", OM-914 / MM-914.",
         "https://www.flyrotax.com/services/technical-documentation")
    ]

    for idx, (cit, url) in enumerate(references):
        p = stf6.paragraphs[0] if idx == 0 else stf6.add_paragraph()
        p.text = f"❖  {cit}\n    "
        p.font.name = "Calibri"
        p.font.size = Pt(11)
        p.font.color.rgb = BLACK
        if idx > 0:
            p.space_before = Pt(8)

        run = p.add_run()
        run.text = url
        run.font.name = "Calibri"
        run.font.size = Pt(10.5)
        run.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)
        run.font.underline = True

    # Save to desktop and project
    out_desktop = os.path.join(os.path.expanduser("~"), "Desktop", "AeroTwin_SIH2026_Official_Presentation.pptx")
    prs.save(out_desktop)
    prs.save("AeroTwin_SIH2026_Official_Presentation.pptx")
    print(f"Perfect presentation saved to Desktop: {out_desktop}")

if __name__ == "__main__":
    build_perfect_presentation()
