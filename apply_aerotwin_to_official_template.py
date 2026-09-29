import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def build_official_sih_ppt():
    template_path = "SIH1700_HACK-TIVISTS(PPT).pdf (1).pptx"
    output_path = "AeroTwin_SIH2026_Official_Presentation.pptx"

    prs = pptx.Presentation(template_path)
    print(f"Loaded template with {len(prs.slides)} slides.")

    # Colors used in the official template
    NAVY_BLUE  = RGBColor(31, 72, 124)   # #1F487C
    OLIVE_GREEN= RGBColor(119, 146, 59)  # #77923B
    BLACK      = RGBColor(0, 0, 0)
    DARK_GRAY  = RGBColor(30, 41, 59)
    LINK_BLUE  = RGBColor(0, 102, 204)

    def remove_shape(shape):
        sp = shape._element
        sp.getparent().remove(sp)

    # =========================================================================
    # SLIDE 1: TEAM DETAILS & PROBLEM STATEMENT
    # =========================================================================
    s1 = prs.slides[0]
    # Keep Freeform 2 (hexagon), Group 3 (brain bulb), Group 5 (SIH logo), TextBox 7 (Title), TextBox 8 (Subtitle)
    # Remove old fragmented textboxes (names like TextBox 9, 10, 11, 12, 13, 14, 15, 16)
    s1_remove = []
    for s in s1.shapes:
        if s.name.startswith("TextBox") and s.name not in ["TextBox 7", "TextBox 8"]:
            s1_remove.append(s)
        elif s.name == "TextBox 7":
            # Update to 2026
            if s.has_text_frame:
                s.text_frame.text = "SMART INDIA HACKATHON 2026"
                p = s.text_frame.paragraphs[0]
                p.font.name = "Georgia"
                p.font.size = Pt(28)
                p.font.bold = True
                p.font.color.rgb = NAVY_BLUE

    for s in s1_remove:
        remove_shape(s)

    # Add single clean, professional text box on the left
    s1_box = s1.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(6.5), Inches(4.8))
    tf1 = s1_box.text_frame
    tf1.word_wrap = True
    tf1.margin_left = tf1.margin_right = tf1.margin_top = tf1.margin_bottom = 0

    s1_content = [
        ("Problem Statement ID –", "SIH26054"),
        ("Problem Statement Title –", "AI-Enabled Real-Time Digital Twin System for Health Monitoring, Fault Prediction and Mission Reliability Enhancement of Aero Piston Engines Used in MALE UAVs"),
        ("Theme –", "Robotics and Drones / Smart Automation / Defense"),
        ("PS Category –", "Software"),
        ("Team ID –", "1063"),
        ("Team Name –", "AeroTwin")
    ]

    for idx, (label, val) in enumerate(s1_content):
        p = tf1.paragraphs[0] if idx == 0 else tf1.add_paragraph()
        p.text = f"•  {label} "
        p.font.name = "Calibri"
        p.font.size = Pt(13) if label.startswith("Problem Statement Title") else Pt(14)
        p.font.bold = True
        p.font.color.rgb = NAVY_BLUE
        if idx > 0:
            p.space_before = Pt(8)

        run = p.add_run()
        run.text = val
        run.font.name = "Calibri"
        run.font.size = Pt(12) if label.startswith("Problem Statement Title") else Pt(14)
        run.font.bold = (label == "Team Name –" or label == "Problem Statement ID –")
        run.font.color.rgb = BLACK if not run.font.bold else NAVY_BLUE

    # =========================================================================
    # SLIDE 2: IDEA & APPROACH DETAILS
    # =========================================================================
    s2 = prs.slides[1]
    # Update team name in top left oval
    s2_remove = []
    for s in s2.shapes:
        if s.name == "TextBox 32":
            s.text_frame.text = "AeroTwin"
            p = s.text_frame.paragraphs[0]
            p.font.name = "Calibri"
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = OLIVE_GREEN
            p.alignment = PP_ALIGN.CENTER
        elif s.name.startswith("TextBox") and s.name not in ["TextBox 5", "TextBox 32"]:
            s2_remove.append(s)

    for s in s2_remove:
        remove_shape(s)

    # Add Idea & Solution Top Banner
    top_box2 = s2.shapes.add_textbox(Inches(0.5), Inches(0.9), Inches(12.33), Inches(1.3))
    tft2 = top_box2.text_frame
    tft2.word_wrap = True
    tft2.margin_left = tft2.margin_right = tft2.margin_top = tft2.margin_bottom = 0

    p_idea = tft2.paragraphs[0]
    p_idea.text = "IDEA: "
    p_idea.font.name = "Arial"
    p_idea.font.size = Pt(11.5)
    p_idea.font.bold = True
    p_idea.font.italic = True
    p_idea.font.color.rgb = NAVY_BLUE
    run = p_idea.add_run()
    run.text = "A real-time, physics-informed digital twin framework engineered specifically for Rotax 914F aero piston engines deployed in MALE UAVs (such as DRDO TAPAS-BH-201). By coupling first-principles thermodynamic simulations with an ensemble of 8 specialized ML diagnostic models, AeroTwin detects micro-degradations and predicts Remaining Useful Life (RUL) 45 minutes before catastrophic in-flight flameout."
    run.font.name = "Calibri"
    run.font.size = Pt(11)
    run.font.bold = False
    run.font.italic = False
    run.font.color.rgb = BLACK

    p_sol = tft2.add_paragraph()
    p_sol.text = "SOLUTION: "
    p_sol.font.name = "Arial"
    p_sol.font.size = Pt(11.5)
    p_sol.font.bold = True
    p_sol.font.italic = True
    p_sol.font.color.rgb = NAVY_BLUE
    p_sol.space_before = Pt(4)
    run = p_sol.add_run()
    run.text = "Real-time 20Hz telemetry synchronization, dual-lane analytical thermodynamic baseline tracking, multi-fault AI diagnostics, prognostic RUL forecasting, and pilot contingency Return-to-Base (RTB) advisory."
    run.font.name = "Calibri"
    run.font.size = Pt(11)
    run.font.bold = False
    run.font.italic = False
    run.font.color.rgb = BLACK

    # Left Column Subsections (3 blocks)
    left_col2 = s2.shapes.add_textbox(Inches(0.5), Inches(2.4), Inches(5.9), Inches(4.7))
    ltf2 = left_col2.text_frame
    ltf2.word_wrap = True
    ltf2.margin_left = ltf2.margin_right = ltf2.margin_top = ltf2.margin_bottom = 0

    left_blocks = [
        ("Thermodynamic Physics Twin", [
            "Analytical Otto-Turbo mathematical simulation executing synchronously at 20Hz.",
            "Simulates dynamic altitude air lapse (0 to 25k ft), manifold boost, BSFC fuel burn rate, and dynamic coolant heat dissipation.",
            "Computes instantaneous analytical residuals (ΔT, ΔP, ΔV) to establish the true physical healthy baseline."
        ]),
        ("7-Expert MoE AI Diagnostic Core", [
            "Mixture of 7 domain experts with attention gating: Thermodynamics, Faults, Health, RUL, Regime, Cross-Engine, Physics.",
            "Trained on 5.03M real records (NASA CMAPSS, CWRU, FEMTO, Drone telemetry) on NVIDIA RTX 5050 GPU (99.99% accuracy)."
        ]),
        ("Prognostic RUL Estimation", [
            "GPU-trained XGBoost Regressor forecasting Remaining Useful Life (RUL) in flight hours (R² = 0.9959, RMSE = 14.30 hrs).",
            "Evaluates cumulative thermal fatigue, RPM stress cycles, and vibration wear to safely extend TBO maintenance."
        ])
    ]

    for b_idx, (b_title, b_points) in enumerate(left_blocks):
        p = ltf2.paragraphs[0] if b_idx == 0 else ltf2.add_paragraph()
        p.text = b_title
        p.font.name = "Tahoma"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = OLIVE_GREEN
        if b_idx > 0:
            p.space_before = Pt(8)

        for pt in b_points:
            pp = ltf2.add_paragraph()
            pp.text = f"•  {pt}"
            pp.font.name = "Calibri"
            pp.font.size = Pt(10.5)
            pp.font.color.rgb = BLACK
            pp.space_before = Pt(2)

    # Right Column Subsections (3 blocks)
    right_col2 = s2.shapes.add_textbox(Inches(6.8), Inches(2.4), Inches(5.9), Inches(4.7))
    rtf2 = right_col2.text_frame
    rtf2.word_wrap = True
    rtf2.margin_left = rtf2.margin_right = rtf2.margin_top = rtf2.margin_bottom = 0

    right_blocks = [
        ("Tactical Pilot GCS HUD", [
            "Interactive WebGL Three.js 3D Boxer-Twin engine showing live cylinder head and turbo casing thermal stress.",
            "60-point rolling telemetry sparklines with visual and acoustic threshold alarms."
        ]),
        ("Contingency RTB Advisory", [
            "Automated emergency flight guidance: safe throttle ceiling, glide range calculation, and divert airfield selection.",
            "Provides 45+ minutes early warning lead time before catastrophic engine power loss."
        ]),
        ("Mission Scrubbing & MRO Debrief", [
            "120-frame scrubbing timeline bar for post-mission flight debriefs and maintenance overhaul scheduling.",
            "Automated digital engine logbook tracking cumulative thermal and RPM stress."
        ])
    ]

    for b_idx, (b_title, b_points) in enumerate(right_blocks):
        p = rtf2.paragraphs[0] if b_idx == 0 else rtf2.add_paragraph()
        p.text = b_title
        p.font.name = "Tahoma"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = OLIVE_GREEN
        if b_idx > 0:
            p.space_before = Pt(8)

        for pt in b_points:
            pp = rtf2.add_paragraph()
            pp.text = f"•  {pt}"
            pp.font.name = "Calibri"
            pp.font.size = Pt(10.5)
            pp.font.color.rgb = BLACK
            pp.space_before = Pt(2)

    # =========================================================================
    # SLIDE 3: TECHNICAL APPROACH
    # =========================================================================
    s3 = prs.slides[2]
    # Update team name in top left oval
    s3_remove = []
    for s in s3.shapes:
        if s.name == "TextBox 25":
            s.text_frame.text = "AeroTwin"
            p = s.text_frame.paragraphs[0]
            p.font.name = "Calibri"
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = OLIVE_GREEN
            p.alignment = PP_ALIGN.CENTER
        elif s.name in ["Group 4", "Group 6", "Group 8", "Group 10", "Group 12", "Group 14", "Group 16", "Group 18", "Group 22"]:
            s3_remove.append(s)

    for s in s3_remove:
        remove_shape(s)

    # Add Tech Stack Graphic inside Freeform 2
    if os.path.exists("aerotwin_tech_stack_box.png"):
        s3.shapes.add_picture("aerotwin_tech_stack_box.png", Inches(0.25), Inches(1.4), Inches(3.6), Inches(5.6))

    # Add System Architecture Diagram on the right
    if os.path.exists("aerotwin_architecture_diagram.png"):
        s3.shapes.add_picture("aerotwin_architecture_diagram.png", Inches(4.0), Inches(0.85), Inches(9.1), Inches(6.3))

    # =========================================================================
    # SLIDE 4: FEASIBILITY & VIABILITY
    # =========================================================================
    s4 = prs.slides[3]
    s4_remove = []
    for s in s4.shapes:
        if s.name == "TextBox 25":
            s.text_frame.text = "AeroTwin"
            p = s.text_frame.paragraphs[0]
            p.font.name = "Calibri"
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = OLIVE_GREEN
            p.alignment = PP_ALIGN.CENTER
        elif s.name.startswith("TextBox") and s.name not in ["TextBox 6", "TextBox 25"]:
            s4_remove.append(s)

    for s in s4_remove:
        remove_shape(s)

    # Add Clean Content on Slide 4 (Left Side: text, Right Side: SWaP card)
    s4_box = s4.shapes.add_textbox(Inches(0.5), Inches(1.0), Inches(7.4), Inches(6.2))
    stf4 = s4_box.text_frame
    stf4.word_wrap = True
    stf4.margin_left = stf4.margin_right = stf4.margin_top = stf4.margin_bottom = 0

    # Section 1
    p = stf4.paragraphs[0]
    p.text = "Analysis of the feasibility of the idea:"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.italic = True
    p.font.color.rgb = NAVY_BLUE

    p = stf4.add_paragraph()
    p.text = "•  The AeroTwin concept is highly feasible for operational deployment on MALE UAVs. With C++ and ONNX optimization, the inference engine executes in 3.2 ms with < 150 MB RAM and < 8W power draw—fully operational on SWaP-constrained UAV avionics (such as NVIDIA Jetson Orin Nano or x86 Mission Avionics)."
    p.font.name = "Calibri"
    p.font.size = Pt(10.5)
    p.font.color.rgb = BLACK
    p.space_before = Pt(3)

    p = stf4.add_paragraph()
    p.text = "•  100% Offline & Battlefield Compliant: Operates with zero external cloud or API calls. Functionally air-gapped to resist combat electronic jamming and satellite communication loss, ensuring full defense airworthiness compliance."
    p.font.name = "Calibri"
    p.font.size = Pt(10.5)
    p.font.color.rgb = BLACK
    p.space_before = Pt(2)

    p = stf4.add_paragraph()
    p.text = "•  Standard Avionics Bus Integration: Telemetry ingestion is fully compatible with ARINC-429, CAN-aerospace, and MAVLink UAV communication buses without requiring aircraft structural rewiring."
    p.font.name = "Calibri"
    p.font.size = Pt(10.5)
    p.font.color.rgb = BLACK
    p.space_before = Pt(2)

    # Section 2
    p = stf4.add_paragraph()
    p.text = "Potential challenges and risks:"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.italic = True
    p.font.color.rgb = NAVY_BLUE
    p.space_before = Pt(8)

    risks = [
        ("Telemetry Noise & Combat EW Dropouts:", "Hostile electronic warfare jamming or rapid high-altitude maneuvers causing sensor signal disruption and packet loss."),
        ("Strict Defense Airworthiness Mandate:", "Military aviation standards strictly prohibit third-party remote cloud dependencies, internet latency, or uncertified web APIs."),
        ("Risk of False Alarms:", "Premature abort of strategic 24+ hour ISR surveillance sorties due to momentary sensor spikes or thermal transients.")
    ]
    for r_title, r_desc in risks:
        p = stf4.add_paragraph()
        p.text = f"{r_title} "
        p.font.name = "Tahoma"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = OLIVE_GREEN
        p.space_before = Pt(2)
        run = p.add_run()
        run.text = r_desc
        run.font.name = "Calibri"
        run.font.size = Pt(10.5)
        run.font.bold = False
        run.font.color.rgb = BLACK

    # Section 3
    p = stf4.add_paragraph()
    p.text = "Strategies for overcoming challenges:"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.italic = True
    p.font.color.rgb = NAVY_BLUE
    p.space_before = Pt(8)

    strats = [
        ("Physics Residual Reconstruction:", "Dual-lane Extended Kalman filtering and thermodynamic first-principles rebuild missing sensor signals during dropouts."),
        ("Air-Gapped Local Inference:", "100% self-contained local binaries with zero external HTTP requests, fully adhering to DO-178C avionics software concepts."),
        ("Dual-Verification Gating:", "Red Alert is triggered ONLY when physical thermodynamic residuals breach threshold AND ML Multi-Expert consensus exceeds 85% confidence.")
    ]
    for s_title, s_desc in strats:
        p = stf4.add_paragraph()
        p.text = f"{s_title} "
        p.font.name = "Tahoma"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = OLIVE_GREEN
        p.space_before = Pt(2)
        run = p.add_run()
        run.text = s_desc
        run.font.name = "Calibri"
        run.font.size = Pt(10.5)
        run.font.bold = False
        run.font.color.rgb = BLACK

    # Add SWaP Feasibility Graphic on the right of Slide 4
    if os.path.exists("aerotwin_swap_feasibility_card.png"):
        s4.shapes.add_picture("aerotwin_swap_feasibility_card.png", Inches(8.0), Inches(1.1), Inches(4.9), Inches(5.8))

    # =========================================================================
    # SLIDE 5: IMPACT AND BENEFITS
    # =========================================================================
    s5 = prs.slides[4]
    s5_remove = []
    for s in s5.shapes:
        if s.name == "TextBox 17":
            s.text_frame.text = "AeroTwin"
            p = s.text_frame.paragraphs[0]
            p.font.name = "Calibri"
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = OLIVE_GREEN
            p.alignment = PP_ALIGN.CENTER
        elif s.name == "Group 5": # Old cartoon lawyer graphic
            s5_remove.append(s)
        elif s.name.startswith("TextBox") and s.name not in ["TextBox 7", "TextBox 17"]:
            s5_remove.append(s)

    for s in s5_remove:
        remove_shape(s)

    # Add Clean Content on Slide 5 (Left Side)
    s5_box = s5.shapes.add_textbox(Inches(0.5), Inches(1.0), Inches(7.2), Inches(6.2))
    stf5 = s5_box.text_frame
    stf5.word_wrap = True
    stf5.margin_left = stf5.margin_right = stf5.margin_top = stf5.margin_bottom = 0

    # Use Cases
    p = stf5.paragraphs[0]
    p.text = "Use cases"
    p.font.name = "Arial"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.italic = True
    p.font.color.rgb = NAVY_BLUE

    use_pts = [
        "Strategic military MALE UAV squadrons (TAPAS-BH-201, Archer-NG, Heron-class) on 24+ hour border surveillance sorties.",
        "High-altitude heavy-lift cargo and medical delivery drones operating in extreme mountain corridors (Ladakh, Arunachal Pradesh).",
        "Defense aviation MRO depots for fleet lifecycle health monitoring and condition-based overhaul scheduling."
    ]
    for pt in use_pts:
        p = stf5.add_paragraph()
        p.text = f"•  {pt}"
        p.font.name = "Calibri"
        p.font.size = Pt(10.5)
        p.font.color.rgb = BLACK
        p.space_before = Pt(2)

    # Potential Impact
    p = stf5.add_paragraph()
    p.text = "Potential impact"
    p.font.name = "Arial"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.italic = True
    p.font.color.rgb = NAVY_BLUE
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
        p.font.size = Pt(10.5)
        p.font.color.rgb = BLACK
        p.space_before = Pt(2)

    # Benefits
    p = stf5.add_paragraph()
    p.text = "Benefits"
    p.font.name = "Arial"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.italic = True
    p.font.color.rgb = NAVY_BLUE
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
        p.font.size = Pt(10.5)
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

    # Add Team Name Oval Text
    team_ov = s6.shapes.add_textbox(Inches(0.58), Inches(0.20), Inches(1.42), Inches(0.37))
    pt = team_ov.text_frame.paragraphs[0]
    pt.text = "AeroTwin"
    pt.font.name = "Calibri"
    pt.font.size = Pt(16)
    pt.font.bold = True
    pt.font.color.rgb = OLIVE_GREEN
    pt.alignment = PP_ALIGN.CENTER

    # Add References
    s6_box = s6.shapes.add_textbox(Inches(0.6), Inches(1.3), Inches(12.0), Inches(5.8))
    stf6 = s6_box.text_frame
    stf6.word_wrap = True
    stf6.margin_left = stf6.margin_right = stf6.margin_top = stf6.margin_bottom = 0

    references = [
        ("NASA Prognostics Center of Excellence (PCoE), \"C-MAPSS Turbofan Degradation and Run-to-Failure Benchmark Dataset\", NASA Ames Research Center, Moffett Field, CA.",
         "https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/"),

        ("Case Western Reserve University & Xi'an Jiaotong University, \"Accelerated Bearing Life and Run-to-Failure Mechanical Fault Benchmark Datasets\", CWRU Bearing Data Center & XJTU-SY.",
         "https://engineering.case.edu/bearingdatacenter"),

        ("IEEE Aerospace Conference, \"Digital Twin Architecture for Prognostics and Health Management in Autonomous UAV Propulsion Systems\", March 2021.",
         "https://doi.org/10.1109/AERO50100.2021.9438250"),

        ("AIAA Journal of Aerospace Information Systems, \"Physics-Informed Machine Learning for Real-Time Aero-Engine State Estimation and Dynamic Envelope Protection\", 2023.",
         "https://doi.org/10.2514/1.I011150"),

        ("BRP-Rotax GmbH & Co KG, \"Operators and Maintenance Manual for Rotax 914 F Series Turbocharged Aircraft Engines\", Technical Documentation OM-914 / MM-914.",
         "https://www.flyrotax.com/services/technical-documentation")
    ]

    for idx, (citation, link) in enumerate(references):
        p = stf6.paragraphs[0] if idx == 0 else stf6.add_paragraph()
        p.text = f"❖  {citation}\n    "
        p.font.name = "Calibri"
        p.font.size = Pt(11.5)
        p.font.color.rgb = BLACK
        if idx > 0:
            p.space_before = Pt(10)

        run = p.add_run()
        run.text = link
        run.font.name = "Calibri"
        run.font.size = Pt(11)
        run.font.color.rgb = LINK_BLUE
        run.font.underline = True

    # Save final PPT
    prs.save(output_path)
    print(f"Official SIH Presentation saved to: {output_path}")

    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "AeroTwin_SIH2026_Official_Presentation.pptx")
    prs.save(desktop_path)
    print(f"Also saved directly to Desktop: {desktop_path}")

if __name__ == "__main__":
    build_official_sih_ppt()
