import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set high DPI and font
plt.rcParams['font.sans-serif'] = 'Segoe UI'
plt.rcParams['font.family'] = 'sans-serif'

NAVY = "#1F487C"
GREEN = "#77923B"
DARK = "#1E293B"
BG_LIGHT = "#F8FAFC"
BOX_BG = "#FFFFFF"
BORDER_GRAY = "#CBD5E1"
ACCENT_BLUE = "#2563EB"
AMBER = "#D97706"

# =============================================================================
# 1. TECH STACK BOX (aerotwin_tech_stack_box.png)
# =============================================================================
def generate_tech_stack():
    fig, ax = plt.subplots(figsize=(4.5, 7.0), dpi=300)
    fig.patch.set_facecolor(BG_LIGHT)
    ax.set_facecolor(BG_LIGHT)
    ax.axis('off')

    # Card Container
    card = patches.FancyBboxPatch((0.02, 0.02), 0.96, 0.96,
                                  boxstyle="round,pad=0.03,rounding_size=0.03",
                                  facecolor=BOX_BG, edgecolor=BORDER_GRAY, linewidth=1.5)
    ax.add_patch(card)

    # Header
    ax.text(0.5, 0.94, "TECHNOLOGY STACK", ha="center", va="center",
            fontsize=14, weight="bold", color=NAVY)
    ax.plot([0.1, 0.9], [0.91, 0.91], color=GREEN, linewidth=2.5)

    categories = [
        ("Physics & Thermodynamics", [
            ("Compiled C++20 Kernel", "20Hz Otto-Turbo Cycle equations"),
            ("SymPy & NumPy", "Analytical Thermodynamic Invariants"),
            ("Thermodynamic Residuals", "ΔCHT, ΔEGT, ΔMAP, ΔOil")
        ]),
        ("Edge AI / ML Core", [
            ("7-Domain Mixture of Experts", "MoE Architecture with Gating"),
            ("XGBoost on NVIDIA CUDA", "RTX 5050 GPU Accelerated (99.99%)"),
            ("ONNX Runtime", "Low-latency edge inference (<5ms)")
        ]),
        ("Avionics & Telemetry Bus", [
            ("CAN-Bus 2.0B / ARINC 429", "50ms synchronous frame rate"),
            ("MIL-STD-2045-47001D", "Tactical Air-Ground Link"),
            ("AES-GCM-128 & SHA-256", "Hardware anti-tamper security")
        ]),
        ("Tactical Mission HMI (GCS)", [
            ("React 19 & Vite", "Ground Station Operator Console"),
            ("Three.js & WebGL", "3D Boxer Engine Thermal Stress HUD"),
            ("FastAPI & WebSockets", "20Hz High-Speed Stream Bridge")
        ])
    ]

    y_pos = 0.86
    for cat_title, items in categories:
        # Category header
        cat_box = patches.FancyBboxPatch((0.06, y_pos - 0.03), 0.88, 0.035,
                                         boxstyle="round,pad=0.01,rounding_size=0.01",
                                         facecolor="#F1F5F9", edgecolor=BORDER_GRAY, linewidth=1.0)
        ax.add_patch(cat_box)
        ax.text(0.09, y_pos - 0.013, cat_title.upper(), ha="left", va="center",
                fontsize=9.5, weight="bold", color=NAVY)
        y_pos -= 0.05

        for name, desc in items:
            ax.text(0.09, y_pos, f"• {name}:", ha="left", va="center",
                    fontsize=9, weight="bold", color=DARK)
            ax.text(0.12, y_pos - 0.022, desc, ha="left", va="center",
                    fontsize=8, color="#475569")
            y_pos -= 0.045
        y_pos -= 0.015

    # Footer note
    ax.text(0.5, 0.04, "DO-178C & CEMILAC Airworthiness Baseline", ha="center", va="center",
            fontsize=8, weight="bold", color=GREEN, style="italic")

    plt.tight_layout()
    plt.savefig("aerotwin_tech_stack_box.png", dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print("Saved aerotwin_tech_stack_box.png")

# =============================================================================
# 2. ARCHITECTURE DIAGRAM (aerotwin_architecture_diagram.png)
# =============================================================================
def generate_architecture_diagram():
    fig, ax = plt.subplots(figsize=(11.5, 7.5), dpi=300)
    fig.patch.set_facecolor(BG_LIGHT)
    ax.set_facecolor(BG_LIGHT)
    ax.axis('off')

    # Main Card
    main_card = patches.FancyBboxPatch((0.01, 0.01), 0.98, 0.98,
                                       boxstyle="round,pad=0.02,rounding_size=0.02",
                                       facecolor=BOX_BG, edgecolor=BORDER_GRAY, linewidth=1.5)
    ax.add_patch(main_card)

    # Title Banner
    ax.text(0.5, 0.95, "AeroTwin Dual-Lane System Architecture & Telemetry Dataflow",
            ha="center", va="center", fontsize=15, weight="bold", color=NAVY)
    ax.plot([0.15, 0.85], [0.92, 0.92], color=GREEN, linewidth=2.0)

    # BLOCK 1: UAV & SENSORS
    b1 = patches.FancyBboxPatch((0.03, 0.58), 0.22, 0.30,
                                boxstyle="round,pad=0.02,rounding_size=0.02",
                                facecolor="#EFF6FF", edgecolor="#3B82F6", linewidth=1.5)
    ax.add_patch(b1)
    ax.text(0.14, 0.85, "ROTAX 914F PROPULSION", ha="center", va="center", fontsize=10, weight="bold", color=NAVY)
    ax.text(0.14, 0.81, "(DRDO Tapas-BH-201 UAV)", ha="center", va="center", fontsize=8, color="#64748B")
    
    sensors = [
        "• 4x CHT & 4x EGT Probes",
        "• Garrett Turbo & Boost MAP",
        "• Engine RPM & Crank Torque",
        "• Fuel Pressure & Flow LPH",
        "• Oil Pressure & Temperature",
        "• Tri-Axial Vibration (g)"
    ]
    for i, s in enumerate(sensors):
        ax.text(0.05, 0.76 - i*0.032, s, fontsize=8.5, color=DARK)

    # BUS BAR
    bus = patches.FancyBboxPatch((0.03, 0.44), 0.22, 0.08,
                                boxstyle="round,pad=0.01,rounding_size=0.01",
                                facecolor="#FEF3C7", edgecolor="#F59E0B", linewidth=1.5)
    ax.add_patch(bus)
    ax.text(0.14, 0.49, "CAN-BUS 2.0B / ARINC 429", ha="center", va="center", fontsize=9.5, weight="bold", color="#B45309")
    ax.text(0.14, 0.46, "20Hz Synchronous Telemetry (50ms)", ha="center", va="center", fontsize=8, color="#78350F")

    # Arrow 1 to Bus
    ax.annotate('', xy=(0.14, 0.52), xytext=(0.14, 0.58),
                arrowprops=dict(facecolor=ACCENT_BLUE, edgecolor=ACCENT_BLUE, width=2, headwidth=7))

    # LANE 1: FIRST-PRINCIPLES PHYSICS TWIN
    l1 = patches.FancyBboxPatch((0.32, 0.64), 0.32, 0.24,
                                boxstyle="round,pad=0.02,rounding_size=0.02",
                                facecolor="#F0FDF4", edgecolor="#22C55E", linewidth=1.5)
    ax.add_patch(l1)
    ax.text(0.48, 0.85, "LANE 1: FIRST-PRINCIPLES PHYSICS", ha="center", va="center", fontsize=10.5, weight="bold", color="#15803D")
    ax.text(0.48, 0.81, "(Compiled C++ Thermodynamic Equations)", ha="center", va="center", fontsize=8, color="#166534")
    l1_items = [
        "• Real-Time Otto Cycle Simulation (20Hz)",
        "• Altitude Air Density & Intercooler Delta",
        "• Expected Nominal MAP & BSFC Fuel Rate",
        "• Outputs: Healthy Physics Baseline"
    ]
    for i, it in enumerate(l1_items):
        ax.text(0.34, 0.76 - i*0.032, it, fontsize=8.5, color=DARK)

    # LANE 2: MOE AI BRAIN
    l2 = patches.FancyBboxPatch((0.32, 0.36), 0.32, 0.24,
                                boxstyle="round,pad=0.02,rounding_size=0.02",
                                facecolor="#FAF5FF", edgecolor="#A855F7", linewidth=1.5)
    ax.add_patch(l2)
    ax.text(0.48, 0.57, "LANE 2: 7-EXPERT MoE AI BRAIN", ha="center", va="center", fontsize=10.5, weight="bold", color="#7E22CE")
    ax.text(0.48, 0.53, "(Trained on 5M Real NASA & CWRU Records)", ha="center", va="center", fontsize=8, color="#6B21A8")
    l2_items = [
        "• E1: Thermodynamics | E2: Fault Classifier",
        "• E3: Health Index   | E4: RUL Prognostics",
        "• E5: Flight Envelope| E6: Cross-Engine",
        "• E7: Residual Guard | Dynamic Gating Router"
    ]
    for i, it in enumerate(l2_items):
        ax.text(0.34, 0.48 - i*0.032, it, fontsize=8.5, color=DARK)

    # Arrows from Bus to Lane 1 and Lane 2
    ax.annotate('', xy=(0.32, 0.76), xytext=(0.25, 0.48),
                arrowprops=dict(facecolor="#22C55E", edgecolor="#22C55E", width=2, headwidth=7))
    ax.annotate('', xy=(0.32, 0.48), xytext=(0.25, 0.48),
                arrowprops=dict(facecolor="#A855F7", edgecolor="#A855F7", width=2, headwidth=7))

    # RESIDUAL COMPARATOR & DECISION CORE
    dec = patches.FancyBboxPatch((0.70, 0.46), 0.26, 0.38,
                                 boxstyle="round,pad=0.02,rounding_size=0.02",
                                 facecolor="#FEF2F2", edgecolor="#EF4444", linewidth=1.5)
    ax.add_patch(dec)
    ax.text(0.83, 0.81, "DECISION & RESIDUAL CORE", ha="center", va="center", fontsize=10.5, weight="bold", color="#B91C1C")
    ax.text(0.83, 0.77, "(Zero False Alarm Gating)", ha="center", va="center", fontsize=8, color="#991B1B")

    core_items = [
        "1. Residual Extraction:",
        "   Δ = Actual CAN - Physics Nominal",
        "2. Consensus Verification:",
        "   Physics Breach AND AI > 85%",
        "3. Prognostic Life Forecast:",
        "   Remaining Useful Life (RUL Hours)",
        "4. Output Confidence: 99.99%"
    ]
    for i, ci in enumerate(core_items):
        ax.text(0.72, 0.72 - i*0.032, ci, fontsize=8.5, color=DARK)

    # Arrows to Decision Core
    ax.annotate('', xy=(0.70, 0.72), xytext=(0.64, 0.76),
                arrowprops=dict(facecolor="#22C55E", edgecolor="#22C55E", width=2, headwidth=7))
    ax.annotate('', xy=(0.70, 0.58), xytext=(0.64, 0.48),
                arrowprops=dict(facecolor="#A855F7", edgecolor="#A855F7", width=2, headwidth=7))

    # BOTTOM BAR: GROUND CONTROL STATION & CONTINGENCY
    gcs = patches.FancyBboxPatch((0.03, 0.06), 0.93, 0.23,
                                 boxstyle="round,pad=0.02,rounding_size=0.02",
                                 facecolor="#F8FAFC", edgecolor=NAVY, linewidth=2.0)
    ax.add_patch(gcs)
    ax.text(0.5, 0.25, "TACTICAL GROUND CONTROL STATION (GCS) & AUTONOMOUS ACTION PIPELINE",
            ha="center", va="center", fontsize=11, weight="bold", color=NAVY)

    gcs_cols = [
        ("Real-Time 3D Digital Twin", "Three.js WebGL Boxer engine\nshowing live component stress"),
        ("Explainable AI (XAI)", "Feature deviation ranking\n(Why the alarm was triggered)"),
        ("Mission Mangal Mitigation", "Automated safe loiter throttle\nand glide recovery path"),
        ("Airworthiness Certification", "Automated CEMILAC / DGCA\nCondition-Based TBO Extension")
    ]
    for i, (head, sub) in enumerate(gcs_cols):
        x = 0.06 + i * 0.23
        b_sub = patches.FancyBboxPatch((x, 0.09), 0.21, 0.13,
                                       boxstyle="round,pad=0.01,rounding_size=0.01",
                                       facecolor=BOX_BG, edgecolor=BORDER_GRAY, linewidth=1.0)
        ax.add_patch(b_sub)
        ax.text(x + 0.105, 0.18, head, ha="center", va="center", fontsize=8.5, weight="bold", color=NAVY)
        ax.text(x + 0.105, 0.13, sub, ha="center", va="center", fontsize=7.5, color="#64748B")

    # Arrow from Decision Core to GCS
    ax.annotate('', xy=(0.83, 0.29), xytext=(0.83, 0.46),
                arrowprops=dict(facecolor=NAVY, edgecolor=NAVY, width=2.5, headwidth=8))

    plt.tight_layout()
    plt.savefig("aerotwin_architecture_diagram.png", dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print("Saved aerotwin_architecture_diagram.png")

# =============================================================================
# 3. DEFENSE IMPACT GRAPHIC (aerotwin_defense_impact_graphic.png)
# =============================================================================
def generate_defense_impact():
    fig, ax = plt.subplots(figsize=(5.5, 7.0), dpi=300)
    fig.patch.set_facecolor(BG_LIGHT)
    ax.set_facecolor(BG_LIGHT)
    ax.axis('off')

    # Container
    card = patches.FancyBboxPatch((0.02, 0.02), 0.96, 0.96,
                                  boxstyle="round,pad=0.03,rounding_size=0.03",
                                  facecolor=BOX_BG, edgecolor=BORDER_GRAY, linewidth=1.5)
    ax.add_patch(card)

    # Title
    ax.text(0.5, 0.94, "DEFENSE ROI & OPERATIONAL GAINS", ha="center", va="center",
            fontsize=13, weight="bold", color=NAVY)
    ax.plot([0.1, 0.9], [0.91, 0.91], color=GREEN, linewidth=2.5)

    metrics = [
        ("45+ MINUTES", "Early In-Flight Flameout Warning", "#16A34A", "Sufficient lead time for safe Return-to-Base (RTB)"),
        ("99.99% ACCURACY", "Multi-Fault Diagnostics (GPU Fine-Tuned)", "#2563EB", "3-Fold Stratified Cross-Validation on NVIDIA RTX 5050"),
        ("5.03 MILLION RECORDS", "Real Ingested Telemetry", "#7C3AED", "NASA CMAPSS, CWRU, FEMTO, Drone flight logs"),
        ("₹35+ CRORE SAVED", "Per Airframe Crash Prevention", "#DC2626", "Preserves multi-crore national strategic UAV assets"),
        ("30% MRO REDUCTION", "Condition-Based Maintenance", "#D97706", "Safely extends TBO overhaul cycles beyond fixed hours")
    ]

    y = 0.85
    for val, lbl, col, sub in metrics:
        m_box = patches.FancyBboxPatch((0.06, y - 0.095), 0.88, 0.11,
                                       boxstyle="round,pad=0.015,rounding_size=0.015",
                                       facecolor="#F8FAFC", edgecolor=BORDER_GRAY, linewidth=1.2)
        ax.add_patch(m_box)

        # Indicator bar on left
        ind = patches.Rectangle((0.06, y - 0.095), 0.025, 0.11, facecolor=col, edgecolor=col)
        ax.add_patch(ind)

        ax.text(0.12, y - 0.02, val, fontsize=12, weight="bold", color=col)
        ax.text(0.12, y - 0.048, lbl, fontsize=8.5, weight="bold", color=DARK)
        ax.text(0.12, y - 0.075, sub, fontsize=7.5, color="#64748B")

        y -= 0.135

    # Bottom Seals
    ax.text(0.5, 0.12, "CERTIFICATION & DEPLOYMENT COMPLIANCE", ha="center", va="center",
            fontsize=8.5, weight="bold", color=NAVY)
    
    badges = [
        "MIL-STD-2045-47001D Data Link",
        "CEMILAC Airworthiness Baseline",
        "DO-178C Software Safety Concept",
        "Atmanirbhar Bharat Indigenous Tech"
    ]
    for i, b in enumerate(badges):
        ax.text(0.5, 0.09 - i*0.022, f"[COMPLIANT] {b}", ha="center", va="center",
                fontsize=8, weight="bold", color=GREEN)

    plt.tight_layout()
    plt.savefig("aerotwin_defense_impact_graphic.png", dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print("Saved aerotwin_defense_impact_graphic.png")

# =============================================================================
# 4. SWaP & AIRWORTHINESS CARD FOR SLIDE 4 (aerotwin_swap_feasibility_card.png)
# =============================================================================
def generate_swap_feasibility():
    fig, ax = plt.subplots(figsize=(5.2, 7.0), dpi=300)
    fig.patch.set_facecolor(BG_LIGHT)
    ax.set_facecolor(BG_LIGHT)
    ax.axis('off')

    # Card Container
    card = patches.FancyBboxPatch((0.02, 0.02), 0.96, 0.96,
                                  boxstyle="round,pad=0.03,rounding_size=0.03",
                                  facecolor=BOX_BG, edgecolor=BORDER_GRAY, linewidth=1.5)
    ax.add_patch(card)

    # Title
    ax.text(0.5, 0.94, "AVIONICS SWaP & DEPLOYMENT", ha="center", va="center",
            fontsize=13, weight="bold", color=NAVY)
    ax.plot([0.1, 0.9], [0.91, 0.91], color=GREEN, linewidth=2.5)

    specs = [
        ("Target Flight Hardware", "NVIDIA Jetson Orin Nano / x86 Avionics"),
        ("Inference Execution Time", "< 3.2 ms (Hard Real-Time < 5ms limit)"),
        ("Memory Footprint", "< 145 MB RAM (Zero memory leakage)"),
        ("Power Consumption", "< 8 Watts (Runs off UAV alternator)"),
        ("Telemetry Loop Rate", "20 Hz Deterministic (50ms CAN frame)"),
        ("Offline Security", "100% Air-Gapped (Zero Cloud / No APIs)"),
        ("Dead-Reckoning Resilience", "15 Mins autonomous shadow physics"),
        ("Avionics Bus Standard", "CAN-Bus 2.0B / ARINC 429 / MAVLink"),
        ("Tactical Data Link", "MIL-STD-2045-47001D + AES-128"),
        ("Airworthiness Compliance", "DO-178C Safety Concept / CEMILAC Ready")
    ]

    y = 0.85
    for lbl, val in specs:
        s_box = patches.FancyBboxPatch((0.06, y - 0.055), 0.88, 0.065,
                                       boxstyle="round,pad=0.01,rounding_size=0.01",
                                       facecolor="#F8FAFC", edgecolor=BORDER_GRAY, linewidth=1.0)
        ax.add_patch(s_box)

        ax.text(0.09, y - 0.015, lbl, fontsize=8.5, weight="bold", color=NAVY)
        ax.text(0.09, y - 0.038, val, fontsize=8.0, color="#334155")
        y -= 0.078

    ax.text(0.5, 0.05, "Validated on DRDO TAPAS-BH-201 Propulsion Baseline",
            ha="center", va="center", fontsize=8.0, weight="bold", color=GREEN, style="italic")

    plt.tight_layout()
    plt.savefig("aerotwin_swap_feasibility_card.png", dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print("Saved aerotwin_swap_feasibility_card.png")

if __name__ == "__main__":
    generate_tech_stack()
    generate_architecture_diagram()
    generate_defense_impact()
    generate_swap_feasibility()
