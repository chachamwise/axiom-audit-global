"""
AXIOM AUDIT: GLOBAL EDITION v1.1 (SOVEREIGN RELEASE)
Features: Custom Domain Routing (aquaflux.co.tz), Viral Loop, GPLv3 Legal Shield.
Copyright (C) 2026 Chacha Mwise / Aquaflux Tech (Tanzania)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Powered by AXIOM RE Kernel.
"""

import streamlit as st
import time
from datetime import datetime
from fpdf import FPDF

__version__ = "1.1"  # Official Release Version

# ==============================================================================
# 1. THE PHYSICS ENGINE (AXIOM RE KERNEL)
# ==============================================================================
class AxiomGlobalEngine:
    """
    Core Physics Engine for Axiom Audit.
    Decouples hydraulic performance from electrical input using IEC standards.
    """
    def __init__(self, rated_kw: float, cost_per_unit: float, currency_symbol: str, co2_factor: float = 0.4):
        # Input Sanitization
        self.RATED_POWER = abs(float(rated_kw)) if float(rated_kw) > 0 else 1.0
        self.UNIT_COST = abs(float(cost_per_unit))
        self.CURR = currency_symbol
        self.CO2_FACTOR = co2_factor

    def analyze_energy_health(self, voltage: float, i1: float, i2: float, i3: float) -> tuple:
        """Diagnoses Grid Quality and Phase Balance."""
        volt_status = "STABLE"
        if voltage < 370:
            volt_status = "CRITICAL: UNDER-VOLTAGE (Overheating Risk)"
        elif voltage > 460:
            volt_status = "CRITICAL: SURGE (Insulation Risk)"
            
        avg_amps = (i1 + i2 + i3) / 3
        if avg_amps > 0:
            max_dev = max(abs(i1 - avg_amps), abs(i2 - avg_amps), abs(i3 - avg_amps))
            imbalance_pct = (max_dev / avg_amps) * 100
        else:
            imbalance_pct = 0.0
            
        imb_status = "BALANCED"
        if imbalance_pct > 2.0:
            imb_status = f"WARNING: {imbalance_pct:.1f}% IMBALANCE"
        if imbalance_pct > 5.0:
            imb_status = f"CRITICAL: {imbalance_pct:.1f}% IMBALANCE (Winding Failure)"
            
        return volt_status, imb_status, imbalance_pct, avg_amps

    def analyze_pump(self, voltage: float, i1: float, i2: float, i3: float, pressure_bar: float, pf: float = 0.85) -> dict:
        """Performs the Full System Audit (Electrical + Hydraulic)."""
        if voltage < 1: voltage = 1.0

        # --- A. ELECTRICAL ANALYSIS ---
        volt_status, imb_status, imb_pct, avg_amps = self.analyze_energy_health(voltage, i1, i2, i3)
        
        real_kw_in = (voltage * avg_amps * pf * 1.732) / 1000.0
        rated_amps_est = (self.RATED_POWER * 1000) / (voltage * 1.732 * pf)
        load_percent = (avg_amps / rated_amps_est) * 100 if rated_amps_est > 0 else 0
        
        # --- B. HYDRAULIC ESTIMATION ---
        head_m = pressure_bar * 10.197 # Convert Bar to Meters Head
        est_eff_overall = 0.60 
        if head_m > 1.0:
            est_flow = (real_kw_in * est_eff_overall * 3600) / (head_m * 9.81)
        else:
            est_flow = 0.0

        # --- C. EFFICIENCY DECOUPLING (IEC STANDARD) ---
        if load_percent < 50: est_motor_eff = 0.85 
        elif load_percent > 110: est_motor_eff = 0.89 
        else: est_motor_eff = 0.92 

        shaft_power_kw = real_kw_in * est_motor_eff
        hydraulic_power = (est_flow * head_m * 9.81) / 3600.0

        if shaft_power_kw > 0.1:
            pump_eff_pct = (hydraulic_power / shaft_power_kw) * 100
            pump_eff_pct = min(99.9, pump_eff_pct) 
        else:
            pump_eff_pct = 0.0
            
        total_sys_eff = (hydraulic_power / real_kw_in * 100) if real_kw_in > 0 else 0.0

        # --- D. DIAGNOSTIC LOGIC ---
        status, reason, severity = "OPTIMAL", "System operating within normal parameters.", "NORMAL"
        
        if "CRITICAL" in volt_status: status, reason, severity = "DANGER: GRID INSTABILITY", volt_status, "CRITICAL"
        elif "CRITICAL" in imb_status: status, reason, severity = "DANGER: PHASE IMBALANCE", "Motor windings degrading.", "CRITICAL"
        elif load_percent < 30: status, reason, severity = "CRITICAL: DRY RUN DETECTED", "Amperage too low (<30%). Pump likely spinning in air.", "CRITICAL"
        elif load_percent > 65 and pressure_bar < 1.5: status, reason, severity = "CRITICAL: BURST PIPE / ZERO HEAD", "High Power vs. Low Pressure. Massive hydraulic loss.", "CRITICAL"
        elif pressure_bar > 8.0 and est_flow < 2.0: status, reason, severity = "WARNING: BLOCKAGE / DEAD-HEAD", "Pressure exceeding safety limits with zero flow.", "WARNING"
        elif load_percent > 105: status, reason, severity = "WARNING: MOTOR OVERLOAD", "Thermal risk.", "WARNING"
        elif pump_eff_pct < 45 and severity == "NORMAL": status, reason, severity = "WARNING: POOR EFFICIENCY", "Pump hydraulic efficiency is very low. Possible worn impeller.", "WARNING"

        # FINANCIAL IMPACT
        cost_per_month = real_kw_in * self.UNIT_COST * 24 * 30
        co2_per_month = (real_kw_in * self.CO2_FACTOR * 24 * 30) / 1000.0
        
        potential_savings = 0.0
        if total_sys_eff < 50 and total_sys_eff > 0:
             optimal_kw = (hydraulic_power / 0.60) / 0.92
             optimal_cost = optimal_kw * self.UNIT_COST * 24 * 30
             potential_savings = max(0, cost_per_month - optimal_cost)
        elif severity != "NORMAL":
             potential_savings = cost_per_month * 0.25

        return {
            "kw": real_kw_in, "flow": est_flow, "cost_mo": cost_per_month, "savings": potential_savings,
            "co2_ton": co2_per_month, "status": status, "reason": reason, "severity": severity,
            "head": head_m, "load_pct": load_percent, "currency": self.CURR, "volt_status": volt_status,
            "imb_status": imb_status, "imb_pct": imb_pct, "input_volts": voltage,
            "eff_motor": est_motor_eff * 100, "eff_pump": pump_eff_pct, "eff_total": total_sys_eff
        }

# ==============================================================================
# 2. REPORT GENERATORS (TEXT & PDF)
# ==============================================================================
def generate_text_report(data, station, engineer):
    """Generates the Viral WhatsApp-ready Text Report"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    report = f"""
*AXIOM INFRASTRUCTURE AUDIT*
----------------------------
*Station:* {station}
*Date:* {timestamp}
*Status:* {data['status']}

*METRICS:*
• Flow: {data['flow']:.1f} m3/h
• Pressure: {data['head']:.1f} m
• Efficiency: {data['eff_total']:.1f}%
• Waste/Mo: {data['currency']} {data['savings']:,.0f}

*DIAGNOSIS:* {data['reason']}
----------------------------
*Powered by Aquaflux Tech*
*Tool:* https://audit.aquaflux.co.tz
"""
    return report

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'AXIOM INFRASTRUCTURE AUDIT REPORT', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'Powered by Aquaflux Tech | Global Edition', 0, 1, 'C')
        self.ln(5)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()} | AUDIT ID: {int(time.time())}', 0, 0, 'C')

def generate_pdf_report(data, station, engineer):
    """Generates the Official Signed PDF Certificate"""
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Info Block
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 10, f"  STATION ID: {station}      |      AUDITOR: {engineer}      |      DATE: {datetime.now().strftime('%Y-%m-%d')}", 0, 1, 'L', 1)
    pdf.ln(10)
    
    # Status
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '1. EXECUTIVE SUMMARY', 0, 1)
    pdf.set_font('Arial', '', 11)
    status_color = (0, 128, 0) # Green
    if data['severity'] == "CRITICAL": status_color = (200, 0, 0) # Red
    elif data['severity'] == "WARNING": status_color = (255, 140, 0) # Orange
    pdf.set_text_color(*status_color)
    pdf.cell(0, 8, f"STATUS: {data['status']}", 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"RISK FACTOR: {data['reason']}", 0, 1)
    pdf.ln(5)

    # Metrics
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '2. SYSTEM METRICS', 0, 1)
    pdf.set_font('Courier', '', 10)
    metrics = [
        ("Flow Rate", f"{data['flow']:.1f} m3/h", "Voltage", f"{data['input_volts']} V"),
        ("Pressure", f"{data['head']:.1f} m", "Imbalance", f"{data['imb_pct']:.1f} %"),
        ("System Eff", f"{data['eff_total']:.1f} %", "Motor Load", f"{data['load_pct']:.0f} %"),
        ("Monthly Bill", f"{data['currency']} {data['cost_mo']:,.0f}", "CO2 Emissions", f"{data['co2_ton']:.2f} Tons")
    ]
    col_w = 45
    for row in metrics:
        pdf.cell(col_w, 8, row[0], 1)
        pdf.cell(col_w, 8, row[1], 1)
        pdf.cell(col_w, 8, row[2], 1)
        pdf.cell(col_w, 8, row[3], 1)
        pdf.ln()
    pdf.ln(10)

    # Detected Waste Box
    pdf.set_fill_color(0, 0, 0)
    pdf.set_text_color(0, 230, 118)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 15, f"   DETECTED WASTE: {data['currency']} {data['savings']:,.0f} / MONTH", 0, 1, 'C', 1)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'I', 10)
    pdf.ln(5)
    if data['savings'] > 0:
        pdf.multi_cell(0, 6, "RECOMMENDATION: Installation of AXIOM CONTROL DRIVE is recommended to eliminate this waste and protect infrastructure. Standard ROI < 12 Months.")
    
    # SOVEREIGN LINK IN FOOTER
    pdf.ln(5)
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(0, 0, 255)
    link_url = "https://audit.aquaflux.co.tz"
    pdf.cell(0, 10, f"Run your own audit at: {link_url}", 0, 1, 'C', link=link_url)

    return pdf.output(dest='S').encode('latin-1')

# ==============================================================================
# 3. MAIN UI (INDUSTRIAL THEME)
# ==============================================================================
def main():
    st.set_page_config(page_title="AXIOM AUDIT", layout="centered", page_icon="🌍")

    # --- CSS: STEALTH & HIGH CONTRAST ---
    st.markdown("""
    <style>
        footer {visibility: hidden;} header {visibility: hidden;} .stApp { background-color: #050505; }
        
        /* High Contrast Inputs */
        .stNumberInput label, .stTextInput label, .stSelectbox label, .stRadio label { 
            color: #ffffff !important; font-weight: 800 !important; font-size: 1rem !important; 
        }
        .stNumberInput input, .stTextInput input { 
            color: #00E676 !important; font-weight: bold; background-color: #1a1a1a; border: 1px solid #333; 
        }
        
        /* Metrics */
        div[data-testid="stMetric"] { background-color: #1e1e1e; border-left: 6px solid #00E676; padding: 15px; border-radius: 5px; }
        div[data-testid="stMetricLabel"] { color: #aaaaaa !important; }
        div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.8rem; }
        
        /* Footer & Button */
        footer:after { content:'© 2026 Aquaflux Tech | AXIOM AUDIT v1.1'; visibility: visible; display: block; position: relative; padding: 15px; color: #444; text-align: center; font-family: monospace; }
        div.stButton > button:first-child { background: linear-gradient(to right, #00C853, #00E676); color: black; font-weight: 900; border-radius: 4px; height: 55px; width: 100%; font-size: 18px; text-transform: uppercase; border: none; }
    </style>
    """, unsafe_allow_html=True)

    st.title("🌍 AXIOM AUDIT")

    # --- JOB SETUP (Top Expander) ---
    with st.expander("📋 JOB SETUP & CURRENCY (Click to Edit)", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            eng_name = st.text_input("Auditor Name", placeholder="e.g. Eng. Chacha")
            site_name = st.text_input("Station ID", placeholder="e.g. PUMP-001")
        with c2:
            currency_map = {"TZS (Tsh)": "Tsh", "USD ($)": "$", "KES (Ksh)": "Ksh", "EUR (€)": "€"}
            curr_choice = st.selectbox("Currency", list(currency_map.keys()), index=0)
            curr_sym = currency_map[curr_choice]
            # Demo Button
            if st.button("Load Demo Data 🎲"):
                st.session_state.update({'demo_cost': 280.0 if "TZS" in curr_choice else 0.15, 'demo_volts': 415.0, 'demo_amps': 55.0, 'demo_press': 4.2, 'demo_kw': 30.0})
                st.rerun()

    # --- METHODOLOGY EXPANDER (LEGAL SHIELD) ---
    with st.expander("ℹ️ HOW IT WORKS & LICENSE"):
        st.markdown("""
        **1. The Physics of Truth:**
        Most audits only measure Power (kW). We use **IEC Decoupling** to separate Electrical Loss (Motor) from Hydraulic Loss (Pump), proving exactly where the waste is.
        
        **2. Zero-Bias Transparency:**
        This software is **Free & Open Source**, licensed under the **GNU GPLv3**.
        * ✅ You are free to inspect the math.
        * ✅ You are free to modify the code.
        * ⚖️ **Condition:** If you distribute modified versions, they must also be GPLv3 (Open Source).
        
        *Source Code:* [github.com/chacha-mwise/axiom-audit-global](https://github.com/chacha-mwise/axiom-audit-global)
        """)

    # --- SESSION STATE INITIALIZATION ---
    if 'demo_cost' not in st.session_state: st.session_state.update({'demo_cost':None, 'demo_volts':415.0, 'demo_amps':None, 'demo_press':None, 'demo_kw':None})

    # --- INPUTS ---
    st.markdown("### 🔌 POWER READINGS")
    col_a, col_b = st.columns([1, 2])
    with col_a: volts = st.number_input("VOLTAGE (V)", value=st.session_state['demo_volts'], step=1.0, help="Standard: 415V")
    with col_b:
        phase_mode = st.radio("Mode", ["3-Phase (Precision)", "1-Phase (Quick)"], horizontal=True, label_visibility="collapsed")
        if phase_mode == "3-Phase (Precision)":
            ic1, ic2, ic3 = st.columns(3)
            with ic1: i1 = st.number_input("AMPS L1", value=st.session_state['demo_amps'], placeholder="0.0")
            with ic2: i2 = st.number_input("AMPS L2", value=st.session_state['demo_amps'], placeholder="0.0")
            with ic3: i3 = st.number_input("AMPS L3", value=st.session_state['demo_amps'], placeholder="0.0")
            ready_power = all(x is not None for x in [i1, i2, i3])
            avg_i = (i1+i2+i3)/3 if ready_power else 0.0
        else:
            single_amp = st.number_input("TOTAL AMPS", value=st.session_state['demo_amps'], placeholder="0.0")
            ready_power = single_amp is not None
            i1=i2=i3=avg_i = single_amp if ready_power else 0.0

    st.markdown("### 💧 HYDRAULIC READINGS")
    col_c, col_d = st.columns(2)
    with col_c: press = st.number_input("PRESSURE (Bar)", value=st.session_state['demo_press'], placeholder="0.0")
    with col_d: rated_kw = st.number_input("MOTOR RATING (kW)", value=st.session_state['demo_kw'], placeholder="Nameplate kW")

    # Cost Input (Critical for ROI)
    unit_cost = st.number_input(f"Electricity Rate ({curr_sym}/kWh)", value=st.session_state['demo_cost'], placeholder="Check Bill...")
    
    # --- EXECUTION ---
    if st.button("RUN DIAGNOSTIC 🚀", type="primary"):
        if not (ready_power and press is not None and rated_kw is not None and unit_cost is not None):
            st.error("⚠️ MISSING DATA: Please fill all fields.")
        else:
            with st.spinner("Initializing Axiom Physics Kernel..."):
                time.sleep(0.5)
                try:
                    engine = AxiomGlobalEngine(rated_kw, unit_cost if unit_cost > 0 else 1.0, curr_sym, 0.4)
                    results = engine.analyze_pump(volts, i1, i2, i3, press)
                    
                    # RESULTS DISPLAY
                    st.markdown("---")
                    sev = results['severity']
                    if sev == "CRITICAL": st.error(f"## STATUS: {results['status']}")
                    elif sev == "WARNING": st.warning(f"## STATUS: {results['status']}")
                    else: st.success(f"## STATUS: {results['status']}")
                    st.info(f"📋 **Diagnosis:** {results['reason']}")

                    tab1, tab2, tab3 = st.tabs(["💰 FINANCIAL", "⚡ ELECTRICAL", "💧 HYDRAULIC"])
                    with tab1:
                        m1, m2 = st.columns(2)
                        m1.metric("OpEx/Mo", f"{curr_sym} {results['cost_mo']:,.0f}")
                        m2.metric("Detected Waste", f"{curr_sym} {results['savings']:,.0f}", delta_color="inverse")
                    with tab2:
                        e1, e2 = st.columns(2)
                        e1.metric("Voltage", f"{results['input_volts']} V")
                        e2.metric("Imbalance", f"{results['imb_pct']:.1f}%")
                    with tab3:
                        h1, h2, h3 = st.columns(3)
                        h1.metric("Flow", f"{results['flow']:.1f} m³/h")
                        h2.metric("Sys Eff.", f"{results['eff_total']:.1f}%")
                        h3.metric("Load", f"{results['load_pct']:.0f}%")

                    # REPORT GENERATION (IMMUTABLE PREVIEW + SMART PDF)
                    st.markdown("---")
                    st.markdown("### 📄 Export Results")
                    final_site = site_name if site_name else "Unknown_Station"
                    final_eng = eng_name if eng_name else "Engineer"
                    
                    # Generate Data
                    text_report = generate_text_report(results, final_site, final_eng)
                    pdf_bytes = generate_pdf_report(results, final_site, final_eng)
                    
                    # 1. Immutable Preview
                    st.caption("🔍 READ-ONLY PREVIEW (Copy Enabled, Edit Disabled)")
                    st.text_area("Report Preview", value=text_report, height=300, disabled=True)
                    
                    # 2. Smart Filename
                    today_str = datetime.now().strftime("%Y-%m-%d")
                    st.download_button(
                        label="💾 DOWNLOAD SIGNED PDF CERTIFICATE",
                        data=pdf_bytes,
                        file_name=f"AXIOM_AUDIT_{final_site}_{today_str}.pdf",
                        mime="application/pdf"
                    )

                except Exception as e: st.error(f"⚠️ ERROR: {e}")

if __name__ == "__main__":
    main()