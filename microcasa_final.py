import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import graphviz
import time
from datetime import datetime
import random

# ==============================================================================
# 1. SYSTEM CONFIGURATION & STATE MANAGEMENT
# ==============================================================================

st.set_page_config(
    page_title="MICROCASA 2026: Ultra Edition",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Complex Session State
if 'slide_index' not in st.session_state:
    st.session_state.slide_index = 0
if 'simulation_log' not in st.session_state:
    st.session_state.simulation_log = []
if 'sensor_active' not in st.session_state:
    st.session_state.sensor_active = False
if 'geo_data' not in st.session_state:
    # Pre-seed with some data around USM Penang for the Heatmap to look good immediately
    # Base coords: 5.356, 100.30 (USM)
    st.session_state.geo_data = pd.DataFrame({
        "lat": np.random.uniform(5.350, 5.360, 50),
        "lon": np.random.uniform(100.29, 100.31, 50),
        "temp": np.random.normal(28, 4, 50),
        "humidity": np.random.normal(60, 10, 50),
        "time": [datetime.now()] * 50
    })

# ==============================================================================
# 2. ADVANCED CSS ARCHITECTURE (ANIMATIONS & LAYOUTS)
# ==============================================================================

def inject_custom_css():
    st.markdown("""
    <style>
        /* --- 1. CORE RESET & FONTS --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* Hide Default Streamlit Elements */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}
        
        /* Main Container Fix */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 5rem !important;
            max-width: 95% !important;
        }

        /* Background */
        .stApp {
            background-color: #f4f7f6;
            font-family: 'Inter', sans-serif;
        }

        /* --- 2. ANIMATIONS --- */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translate3d(0, 40px, 0); }
            to { opacity: 1; transform: translate3d(0, 0, 0); }
        }
        
        @keyframes blink {
            50% { opacity: 0; }
        }

        /* --- 3. COMPONENT CLASSES --- */
        
        /* The Main Slide Card */
        .slide-card {
            background: #ffffff;
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.08);
            padding: 3.5rem;
            margin-bottom: 2rem;
            border-top: 8px solid #c0392b;
            animation: fadeInUp 0.6s ease-out;
            position: relative;
            overflow: hidden;
        }

        /* Typography */
        h1.hero-title {
            font-family: 'Inter', sans-serif;
            font-weight: 800;
            font-size: 4rem;
            background: -webkit-linear-gradient(120deg, #2c3e50, #c0392b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
            letter-spacing: -2px;
            line-height: 1.1;
        }
        
        h2.section-header {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            font-size: 2.2rem;
            color: #2c3e50;
            border-left: 10px solid #c0392b;
            padding-left: 20px;
            margin-bottom: 30px;
        }

        /* The "Terminal" Simulator */
        .terminal-window {
            background-color: #1e1e1e;
            border-radius: 10px;
            padding: 20px;
            font-family: 'JetBrains Mono', monospace;
            color: #00ff00;
            height: 300px;
            overflow-y: auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            border: 1px solid #333;
        }
        .terminal-line {
            margin: 5px 0;
            border-bottom: 1px solid #333;
            padding-bottom: 2px;
        }

        /* Telemetry Panel */
        .telemetry-panel {
            background-color: #2c3e50;
            color: white;
            padding: 15px;
            border-radius: 10px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            height: 300px;
            overflow-y: auto;
        }

        /* The "Mobile Phone" Simulator */
        .mobile-frame {
            background-color: #333;
            border-radius: 30px;
            padding: 15px;
            width: 300px;
            height: 550px;
            margin: 0 auto;
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
            border: 4px solid #555;
            position: relative;
        }
        .mobile-screen {
            background-color: white;
            border-radius: 20px;
            height: 100%;
            width: 100%;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .appsheet-header {
            background-color: #2980b9;
            color: white;
            padding: 15px;
            font-weight: bold;
            text-align: center;
        }
        .appsheet-body {
            padding: 20px;
            flex-grow: 1;
            background-color: #f8f9fa;
        }

        /* Metric Box */
        .metric-box {
            background: white;
            border: 1px solid #eee;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(0,0,0,0.03);
        }
        .metric-box:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.1);
            border-color: #c0392b;
        }
        .metric-value {
            font-size: 3rem;
            font-weight: 800;
            color: #c0392b;
        }
        .metric-label {
            font-size: 1rem;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Quote Card */
        .quote-card {
            background: linear-gradient(to right, #fff5f5, #ffffff);
            border-left: 5px solid #c0392b;
            padding: 30px;
            font-size: 1.25rem;
            font-style: italic;
            color: #444;
            margin: 20px 0;
            border-radius: 0 15px 15px 0;
        }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==============================================================================
# 3. RESEARCH DATA KERNEL (THE TRUTH SOURCE)
# ==============================================================================

class ResearchData:
    """Encapsulates all N=8 Matched Pair Data from the Manuscript"""
    
    @staticmethod
    def demographics():
        return {
            "Science_Bg": 88,
            "Zero_Coding": 75,
            "No_LowCode": 80,
            "No_Dashboard": 63
        }

    @staticmethod
    def aggregated_domains():
        return pd.DataFrame({
            "Domain": ["Knowledge (K)", "Behavioral Intent (B)", "Confidence (C)"],
            "Pre_Mean": [2.92, 3.39, 3.83],
            "Post_Mean": [4.53, 4.36, 4.35],
            "Gain": [1.61, 0.97, 0.52],
            "Effect_Size": [2.98, 1.61, 0.85]
        })

    @staticmethod
    def knowledge_items():
        return pd.DataFrame({
            "Item": ["API Integration", "Dashboard Goals", "Hazard Prediction", "Open Data", "Automation"],
            "Pre": [2.50, 2.63, 2.75, 2.88, 2.88],
            "Post": [4.50, 4.63, 4.50, 4.50, 4.50],
            "Gain": [2.00, 2.00, 1.75, 1.63, 1.63]
        }).sort_values('Gain', ascending=True)

    @staticmethod
    def individual_trajectories():
        return pd.DataFrame({
            "Student": [f"S{i}" for i in range(1, 9)],
            "Pre_Intent": [3.25, 3.50, 3.00, 3.75, 3.10, 3.40, 3.30, 3.60],
            "Post_Intent": [4.50, 4.75, 4.25, 4.80, 4.40, 4.60, 4.50, 4.35]
        })

    @staticmethod
    def quotes():
        return [
            {"text": "Simulation made the concept of a 'sensor' real without needing the physical board... it removes the hardware-dependency.", "theme": "Barrier Removal"},
            {"text": "Turning complex data into clear insights via dashboards was especially valuable... I can see the flood before it happens.", "theme": "Strategic Vision"},
            {"text": "The coding (Apps Script) was hard to follow at first... but I see how it ensures continuous data flow.", "theme": "Productive Friction"}
        ]

# ==============================================================================
# 4. SLIDE CONTROLLERS (THE CONTENT)
# ==============================================================================

def render_header(title, subtitle=None):
    st.markdown(f'<h2 class="section-header">{title}</h2>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"*{subtitle}*", unsafe_allow_html=True)
    st.markdown("---")

def slide_0_hero():
    st.markdown('<div class="slide-card">', unsafe_allow_html=True)
    
    c1, c2 = st.columns([1.8, 1])
    
    with c1:
        st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)
        st.markdown('<h1 class="hero-title">FROM SIMULATED SENSOR<br>TO STRATEGIC MANAGEMENT</h1>', unsafe_allow_html=True)
        st.markdown("### A Validated Pedagogical Model for Instilling Proactive AI and Digital Competency in Environmental Health")
        
        st.markdown("""
        <div style="background: #ecf0f1; padding: 20px; border-radius: 10px; border-left: 5px solid #2c3e50; margin-top: 30px;">
        <strong>PRESENTERS:</strong><br>
        Syazwan Aizat Ismail, Abd Muhaimin Amiruddin, Nur Azzalia Kamaruzaman, Muaz Mohd Zaini Makhtar, Syamimi Shamsuddin, Muhammad Iftishah Ramdan, and Nor Asniza Ishak<br>
        <em>Universiti Sains Malaysia & Partners</em>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚀 BEGIN KEYNOTE PRESENTATION", use_container_width=True):
            st.session_state.slide_index = 1
            st.rerun()

    with c2:
        st.markdown("""
        <div style="text-align: right;">
            <img src="https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?q=80&w=2070&auto=format&fit=crop" 
                 style="border-radius: 20px; box-shadow: -20px 20px 0px #c0392b; width: 100%; object-fit: cover; height: 500px;">
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def slide_1_problem_context():
    st.markdown('<div class="slide-card">', unsafe_allow_html=True)
    render_header("1. The Context: The 'Digital Divide' in EH")
    
    st.markdown("""
    Environmental Health is shifting from **Reactive Manual Inspection** to **Proactive Digital Surveillance**. 
    However, current pedagogical frameworks are failing to keep pace.
    """)
    
    c1, c2, c3 = st.columns([1, 0.2, 1])
    
    with c1:
        st.error("### ❌ The Old Paradigm")
        st.markdown("""
        * **Method:** Paper-based checklists.
        * **Latency:** Monthly reports (Reactive).
        * **Education:** Theoretical, no hardware exposure.
        * **Role:** "The Inspector"
        """)
        st.image("https://images.unsplash.com/photo-1517048676732-d65bc937f952?q=80&w=2070&auto=format&fit=crop", caption="Manual Entry = Dead Data", width=400)
    
    with c2:
        st.markdown("<div style='display:flex; align-items:center; height:400px; justify-content:center;'><h1 style='font-size:4rem; color:#ccc;'>➜</h1></div>", unsafe_allow_html=True)
    
    with c3:
        st.success("### ✅ The New Paradigm (IR 4.0)")
        st.markdown("""
        * **Method:** IoT Sensors & APIs.
        * **Latency:** Real-time dashboards (Proactive).
        * **Education:** **MICROCASA Model: Microcontroller-based Integrated Cloud Analytics and Strategic Automation**.
        * **Role:** "The System Architect"
        """)
        st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop", caption="Digital Strategy = Live Data", width=400)

    st.markdown("---")
    st.markdown("### The Pedagogical Barrier")
    st.warning("How do we teach **IoT Hardware** to distance learners? We cannot ship 500 Arduino kits to 500 homes. It is logistically impossible.")
    st.markdown('</div>', unsafe_allow_html=True)

def slide_2_solution_pipeline():
    st.markdown('<div class="slide-card">', unsafe_allow_html=True)
    render_header("2. The Solution: MICROCASA Pipeline")
    st.markdown("**'Simulated-to-Strategic'**: A verified data lifecycle that removes the hardware dependency.")

    graph = graphviz.Digraph()
    graph.attr(rankdir='LR', bgcolor='transparent')
    graph.attr('node', shape='rect', style='filled, rounded', fontname='Helvetica', penwidth='0', margin='0.2')
    
    graph.node('1', 'STAGE 1: WOKWI\n(Simulated Edge)', fillcolor='#2c3e50', fontcolor='white')
    graph.node('2', 'STAGE 2: APPSHEET\n(Field Acquisition)', fillcolor='#27ae60', fontcolor='white')
    graph.node('3', 'STAGE 3: APPS SCRIPT\n(API Automation)', fillcolor='#f39c12', fontcolor='black')
    graph.node('4', 'STAGE 4: LOOKER\n(Strategic Dashboard)', fillcolor='#c0392b', fontcolor='white')
    
    graph.edge('1', '2', label=' Virtual Signals', color='#7f8c8d')
    graph.edge('2', '3', label=' JSON Payload', color='#7f8c8d')
    graph.edge('3', '4', label=' Decision Intel', color='#7f8c8d')
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.graphviz_chart(graph, use_container_width=True)
    with col2:
        st.info("**Why this works:**\n\nBy simulating the sensor in Stage 1, we remove the 'Black Box' of data origin without the risk of fried circuits or driver incompatibility.")

    st.markdown('</div>', unsafe_allow_html=True)

def slide_3_tech_1_wokwi():
    st.markdown('<div class="slide-card">', unsafe_allow_html=True)
    render_header("3. Technology Deep Dive: Wokwi (The Edge)")
    
    st.markdown("### 📡 VISIBLE TELEMETRY & DATA STREAM")
    
    c1, c2, c3 = st.columns([1, 1, 0.8])
    
    with c1:
        st.markdown("### The Simulation")
        st.write("Wokwi allows students to write C++ code for an ESP32 microprocessor directly in the browser. They learn **logic**, not wiring.")
        st.markdown("**Student Task:** Program a DHT22 sensor to trigger an alert if Temperature > 30°C.")
        
        if st.button("▶️ COMPILE & UPLOAD TO SIMULATOR"):
            st.session_state.sensor_active = True
            st.session_state.simulation_log = []
            st.toast("Compiling C++ Code...", icon="⚙️")
            time.sleep(1)
            st.toast("Uploading to Virtual ESP32...", icon="📡")
            
    with c2:
        st.markdown("### Virtual Serial Monitor")
        log_container = st.empty()
        
    with c3:
        st.markdown("### Live Register View")
        data_table = st.empty()

    # Logic Loop
    if st.session_state.sensor_active:
        logs = ["[BOOT] ESP32 Initialized...", "[WIFI] Connected!"]
        
        # We need a placeholder list to show "Live" table rows
        live_rows = []

        for _ in range(5):
            # 1. Generate Data
            temp = round(random.uniform(25.0, 34.0), 1)
            humid = round(random.uniform(50, 80), 1)
            
            # 2. Simulate Geospatial Tagging (USM Penang Area)
            lat = round(5.35 + random.uniform(-0.01, 0.01), 4)
            lon = round(100.30 + random.uniform(-0.01, 0.01), 4)
            
            status = "NORMAL" if temp < 30 else "ALERT!!"
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # 3. Add to Logs
            logs.append(f"[{timestamp}] T:{temp}C H:{humid}% -> {status}")
            
            # 4. Add to Data Table (Visible Telemetry)
            live_rows.append({"Time": timestamp, "Temp": temp, "Humid": humid, "Lat": lat, "Lon": lon})
            
            # 5. Add to Global Geo State for Heatmap later
            new_row = pd.DataFrame([{"lat": lat, "lon": lon, "temp": temp, "humidity": humid, "time": datetime.now()}])
            st.session_state.geo_data = pd.concat([st.session_state.geo_data, new_row], ignore_index=True)

            # Render
            log_html = "".join([f'<div class="terminal-line">{l}</div>' for l in logs])
            with c2:
                st.markdown(f'<div class="terminal-window">{log_html}<div class="terminal-line" style="animation: blink 1s infinite;">_</div></div>', unsafe_allow_html=True)
            
            with c3:
                # Showing the raw data frame constructing in real-time
                st.markdown(f"""
                <div class="telemetry-panel">
                <strong>REGISTER MAP:</strong><br>
                Address: 0x3F<br>
                Payload: JSON<br>
                ----------------<br>
                Temp: <span style="color:#e74c3c">{temp}</span><br>
                Humid: <span style="color:#3498db">{humid}</span><br>
                Geo: {lat}, {lon}
                </div>
                """, unsafe_allow_html=True)
                
            time.sleep(0.8) # Simulate processing delay
            
    else:
        with c2:
            st.markdown('<div class="terminal-window"><div class="terminal-line">Waiting for upload...</div></div>', unsafe_allow_html=True)
        with c3:
            st.info("System Offline")

    st.markdown('</div>', unsafe_allow_html=True)

def slide_4_tech_2_appsheet():
    st.markdown('<div class="slide-card">', unsafe_allow_html=True)
    render_header("4. Technology Deep Dive: AppSheet (Field Acquisition)")
    
    st.markdown("Once the sensor logic is understood, students build a **No-Code Interface** to standardize data collection in the field.")

    c1, c2, c3 = st.columns([1, 1, 1])
    
    with c1:
        st.markdown("### The Logic")
        st.write("AppSheet acts as the 'Controller'. It takes raw input and enforces data types (GPS, Image, Decimal).")
        st.info("Students learn to build *Constraint Rules* (e.g., Temperature cannot be negative).")
        
    with c2:
        # THE MOBILE PHONE SIMULATOR
        st.markdown("""
        <div class="mobile-frame">
            <div class="mobile-screen">
                <div class="appsheet-header">
                    <div>☰ Field Sensor V1</div>
                </div>
                <div class="appsheet-body">
                    <p style="color:#777; font-size:12px;">LOCATION ID</p>
                    <div style="background:#eee; padding:10px; border-radius:5px; margin-bottom:10px;">Lab_Sector_7</div>
                    
                    <p style="color:#777; font-size:12px;">SENSOR READING (°C)</p>
                    <div style="background:#eee; padding:10px; border-radius:5px; margin-bottom:10px; color: #c0392b; font-weight:bold;">32.5</div>
                    
                    <p style="color:#777; font-size:12px;">GEOSPATIAL TAG</p>
                    <div style="background:#ddd; height:40px; border-radius:5px; display:flex; align-items:center; padding-left:10px; color:#555; margin-bottom:20px;">
                        📍 5.3562, 100.3015
                    </div>
                </div>
                <div style="padding:15px; background:white; border-top:1px solid #eee;">
                     <div style="background:#2980b9; color:white; text-align:center; padding:10px; border-radius:20px;">SYNC NOW</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("### Interactive Form Logic")
        st.write("Test the validation logic taught to students:")
        
        with st.form("mobile_sim"):
            val = st.number_input("Enter Temp (°C)", value=32.5)
            loc = st.text_input("Location", "Sector 7")
            submitted = st.form_submit_button("Submit to Cloud")
            
            if submitted:
                if val > 50:
                    st.error("Error: Value exceeds realistic sensor range.")
                else:
                    # Generate specific coords for this entry
                    lat = 5.355 + random.uniform(-0.005, 0.005)
                    lon = 100.30 + random.uniform(-0.005, 0.005)
                    
                    st.success(f"✅ Data synced! GPS Tagged: {lat:.4f}, {lon:.4f}")
                    
                    # Update Map Data for Slide 6
                    new_row = pd.DataFrame([{"lat": lat, "lon": lon, "temp": val, "humidity": 60, "time": datetime.now()}])
                    st.session_state.geo_data = pd.concat([st.session_state.geo_data, new_row], ignore_index=True)
                    
                    # Mini Map Preview
                    df_mini = pd.DataFrame({'lat': [lat], 'lon': [lon]})
                    st.map(df_mini, zoom=14, size=50)
                    
    st.markdown('</div>', unsafe_allow_html=True)

def slide_5_tech_3_gas():
    st.markdown('<div class="slide-card">', unsafe_allow_html=True)
    render_header("5. Technology Deep Dive: Apps Script (The Bridge)")
    
    st.markdown("This is where the 'Inspector' becomes the 'Architect'. Students write **Low-Code** scripts to automate the flow.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Productive Friction")
        st.write("""
        This stage recorded the highest qualitative anxiety but the **highest quantitative gain (+2.00)**.
        
        **Concepts Taught:**
        1. **APIs (doPost)**: Receiving the JSON payload from the AppSheet webhook.
        2. **Logic Parsing**: `if (temp > 35)`
        3. **Automation**: Triggering an email alert automatically.
        """)
        
    with col2:
        st.markdown("### The Automation Code")
        st.code("""
function doPost(e) {
  // 1. Parse the Incoming Webhook
  var data = JSON.parse(e.postData.contents);
  var temp = data.Temperature;
  
  // 2. Open the Strategic Database
  var sheet = SpreadsheetApp.openById("MICROCASA_DB");
  
  // 3. Apply Strategic Logic (The 'Brain')
  if (temp > 35.0) {
     MailApp.sendEmail({
       to: "manager@usm.my", 
       subject: "CRITICAL ALERT: " + data.Location, 
       body: "Action required. Sensor reading: " + temp
     });
  }
  
  // 4. Archive Data for Looker
  sheet.appendRow([new Date(), temp, data.Location]);
}
        """, language="javascript")
        
    st.info("💡 **Key Finding:** By writing this code, students realized that 'Data' is fluid, not static.")
    st.markdown('</div>', unsafe_allow_html=True)

def slide_6_tech_4_looker():
    st.markdown('<div class="slide-card">', unsafe_allow_html=True)
    render_header("6. Technology Deep Dive: Looker Studio (Strategy)")
    
    st.markdown("The final stage: Visualizing risk to enable **Strategic Decision Making**.")
    
    # Use Session State Data (generated from Slide 3 and 4 interactions)
    df_vis = st.session_state.geo_data
    
    # Interactive Tabs
    tab1, tab2 = st.tabs(["🔥 Interactive Geospatial Heatmap", "📉 Temporal Trend"])
    
    with tab1:
        st.markdown("### 🗺️ Risk Density Map (USM Campus)")
        st.caption("Interactive Heatmap: Visualizing high-temperature clusters reported by student sensors.")
        
        # INTERACTIVE HEATMAP (Plotly Mapbox)
        fig_map = px.density_mapbox(
            df_vis, 
            lat='lat', 
            lon='lon', 
            z='temp', 
            radius=20,
            center=dict(lat=5.356, lon=100.30), 
            zoom=14,
            mapbox_style="carto-positron",
            title="Real-Time Sensor Density Heatmap",
            color_continuous_scale="Viridis"
        )
        fig_map.update_layout(height=500, margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
        
    with tab2:
        # Standard Line Chart
        fig = px.line(df_vis, y='temp', title="Incoming Data Stream", markers=True)
        fig.add_hline(y=35, line_dash="dash", line_color="red", annotation_text="Critical Threshold")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

def slide_7_methodology():
    st.markdown('<div class="slide-card">', unsafe_allow_html=True)
    render_header("7. Methodology & Cohort Profile")
    
    st.write("We utilized a **Matched-Pair Longitudinal Study** ($N=8$) involving postgraduate Environmental Health students.")
    
    c1, c2 = st.columns([1, 1.5])
    
    with c1:
        st.markdown("### The Challenge")
        st.write("The cohort was academically strong but digitally novice.")
        
        # Demographic Metrics
        demo = ResearchData.demographics()
        col_a, col_b = st.columns(2)
        col_a.metric("Zero Coding Exp", f"{demo['Zero_Coding']}%", delta_color="inverse")
        col_b.metric("No Low-Code Exp", f"{demo['No_LowCode']}%", delta_color="inverse")
        
    with c2:
        st.markdown("### Digital Deficiencies at Baseline")
        # Donut Chart
        df_demo = pd.DataFrame({
            'Category': ['Science Bg (Strong)', 'Coding Exp (Weak)', 'Dashboard Exp (Weak)'],
            'Value': [88, 25, 37] # Inverted values for visual
        })
        fig = px.bar(df_demo, x='Value', y='Category', orientation='h', color='Value', title="Entry Profile Competency (%)", range_x=[0,100])
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

def slide_8_results_overview():
    st.markdown('<div class="slide-card">', unsafe_allow_html=True)
    render_header("8. Quantitative Findings: The 'Big' Numbers")
    
    st.markdown("### Aggregated Domain Competency Gains")
    
    df_res = ResearchData.aggregated_domains()
    
    # 3D Bar Chart Effect
    fig = go.Figure(data=[
        go.Bar(name='Pre-Test', x=df_res['Domain'], y=df_res['Pre_Mean'], marker_color='#95a5a6'),
        go.Bar(name='Post-Test', x=df_res['Domain'], y=df_res['Post_Mean'], marker_color='#c0392b')
    ])
    fig.update_layout(barmode='group', title="Mean Likert Scores (1-5)", height=500, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
    
    # Key Metrics Row
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="metric-box"><div class="metric-value">+1.61</div><div class="metric-label">Knowledge Gain (d=2.98)</div></div>', unsafe_allow_html=True)
    c2.markdown('<div class="metric-box"><div class="metric-value">+0.97</div><div class="metric-label">Intent Gain</div></div>', unsafe_allow_html=True)
    c3.markdown('<div class="metric-box"><div class="metric-value">+0.52</div><div class="metric-label">Confidence Stabilized</div></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def slide_9_deep_dive_results():
    st.markdown('<div class="slide-card">', unsafe_allow_html=True)
    render_header("9. Deep Dive: The 'Aha!' Moment")
    
    st.write("Where did the growth come from? **The Bridge Technologies.**")
    
    df_items = ResearchData.knowledge_items()
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        # Funnel or Bar Chart
        fig = px.bar(df_items, y='Item', x='Gain', orientation='h', 
                     text='Gain', color='Gain', color_continuous_scale='Reds',
                     title="Net Gain per Technical Topic (Max +2.00)")
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=500)
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.markdown("### Key Insight")
        st.info("""
        **API Integration** and **Dashboard Goals** saw the highest gain (**+2.00**).
        
        This proves that Simulation successfully demystified the 'Black Box'.
        
        Students didn't just learn *wiring*; they learned **Data Flow**.
        """)

    st.markdown('</div>', unsafe_allow_html=True)

def slide_10_trajectories():
    st.markdown('<div class="slide-card">', unsafe_allow_html=True)
    render_header("10. The Managerial Shift: Trajectories")
    
    st.markdown("The ultimate goal: Shifting identity from **Passive Inspector** to **Proactive System Architect**.")
    
    df_traj = ResearchData.individual_trajectories()
    
    # Parallel Coordinates Plot simulated via Line Chart
    fig = go.Figure()
    
    # Add lines for each student
    for i, row in df_traj.iterrows():
        fig.add_trace(go.Scatter(
            x=['Pre-Test', 'Post-Test'],
            y=[row['Pre_Intent'], row['Post_Intent']],
            mode='lines+markers',
            name=row['Student'],
            line=dict(width=3),
            marker=dict(size=12)
        ))
        
    fig.update_layout(
        title="Individual Trajectories: Intent to Automate Repetitive Tasks (N=8)",
        yaxis_title="Intent Score (1-5)",
        xaxis_title="Assessment Phase",
        template="plotly_white",
        height=500,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.success("✅ **Result:** 100% of the cohort showed an upward trajectory. No student was left behind.")
    st.markdown('</div>', unsafe_allow_html=True)

def slide_11_qualitative():
    st.markdown('<div class="slide-card">', unsafe_allow_html=True)
    render_header("11. Qualitative Validation: Voice of the Student")
    
    st.markdown("Quantitative data tells us *what* happened. Qualitative data tells us *why*.")
    
    quotes = ResearchData.quotes()
    
    for q in quotes:
        st.markdown(f"""
        <div class="quote-card">
            <strong>THEME: {q['theme']}</strong><br>
            "{q['text']}"
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("### Career Alignment")
    st.progress(100)
    st.caption("100% of participants envisioned applying these skills to **Flood Early Warning** and **Air Quality Monitoring**.")

    st.markdown('</div>', unsafe_allow_html=True)

def slide_12_conclusion():
    st.markdown('<div class="slide-card">', unsafe_allow_html=True)
    render_header("12. Conclusion & Future Work")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🗝️ Key Takeaways")
        st.success("""
        1. **Simulation > Hardware:** For Distance Ed, Wokwi logic is cleaner and more scalable than physical kits.
        2. **Logic is King:** Teaching the API flow (+2.00 gain) is more valuable than teaching wiring.
        3. **Identity Shift:** We successfully turned Inspectors into Architects.
        """)
        
    with col2:
        st.markdown("### 🔮 The Future: Agentic AI")
        st.warning("""
        The biggest friction point was **coding syntax**. 
        
        **Next Step:** Integrate an **Agentic AI Tutor** into the pipeline to help students debug their Apps Script logic in real-time, reducing syntax frustration while preserving logic learning.
        """)
        
    st.markdown("---")
    
    c1, c2 = st.columns([1, 4])
    with c1:
        # QR Code Placeholder
        st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=MICROCASA2026", width=150, caption="Scan for Paper")
    with c2:
        st.markdown("# Thank You")
        st.markdown("**Dr. Syazwan Aizat Ismail**")
        st.markdown("drsai@usm.my | Universiti Sains Malaysia")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# 5. MAIN NAVIGATION LOGIC
# ==============================================================================

# List of Slide Functions in Order
slides = [
    slide_0_hero,
    slide_1_problem_context,
    slide_2_solution_pipeline,
    slide_3_tech_1_wokwi,
    slide_4_tech_2_appsheet,
    slide_5_tech_3_gas,
    slide_6_tech_4_looker,
    slide_7_methodology,
    slide_8_results_overview,
    slide_9_deep_dive_results,
    slide_10_trajectories,
    slide_11_qualitative,
    slide_12_conclusion
]

# Sidebar Navigation (Auto-Synced)
with st.sidebar:
    st.markdown("## MICROCASA 2026")
    st.markdown("---")
    
    # Create a mapping of names
    slide_names = [
        "0. Start",
        "1. The Context",
        "2. The Solution",
        "3. Tech: Wokwi",
        "4. Tech: AppSheet",
        "5. Tech: Apps Script",
        "6. Tech: Looker",
        "7. Methodology",
        "8. Quant Results",
        "9. Deep Dive",
        "10. Trajectories",
        "11. Qualitative",
        "12. Conclusion"
    ]
    
    selected_slide_name = st.radio(
        "Navigate Slides:", 
        slide_names, 
        index=st.session_state.slide_index
    )
    
    # Update state if sidebar is clicked
    new_index = slide_names.index(selected_slide_name)
    if new_index != st.session_state.slide_index:
        st.session_state.slide_index = new_index
        st.rerun()
    
    st.markdown("---")
    st.progress((st.session_state.slide_index + 1) / len(slides))
    st.caption("Universiti Sains Malaysia © 2026")

# Render Active Slide
current_slide_func = slides[st.session_state.slide_index]
current_slide_func()

# Bottom Navigation Buttons
st.markdown("<br>", unsafe_allow_html=True)
col_prev, col_spacer, col_next = st.columns([1, 4, 1])

with col_prev:
    if st.session_state.slide_index > 0:
        if st.button("⬅️ PREVIOUS", use_container_width=True):
            st.session_state.slide_index -= 1
            st.rerun()

with col_next:
    if st.session_state.slide_index < len(slides) - 1:
        if st.button("NEXT ➡️", use_container_width=True):
            st.session_state.slide_index += 1
            st.rerun()
