"""
Power electronics knowledge documents for RAG.

Contains curated content on topologies, design principles, and best practices.
"""

KNOWLEDGE_DOCUMENTS = [
    {
        "id": "buck_basics",
        "content": """
        Buck Converter (Step-Down) Basics:
        - Converts higher DC voltage to lower DC voltage
        - Duty cycle D = V_out / V_in
        - Continuous conduction mode (CCM) when inductor current never reaches zero
        - Inductor value: L = V_out * (1-D) / (f_sw * delta_I)
        - Output capacitor filters the inductor current ripple
        - Efficiency typically 85-95% with synchronous rectification
        - Use when V_out < V_in (e.g., 12V to 5V, 24V to 3.3V)
        """,
        "metadata": {"topic": "buck", "type": "topology"},
    },
    {
        "id": "boost_basics",
        "content": """
        Boost Converter (Step-Up) Basics:
        - Converts lower DC voltage to higher DC voltage
        - Duty cycle D = 1 - (V_in / V_out)
        - Right-half-plane zero limits bandwidth at high duty cycle
        - Inductor value: L = V_in * D / (f_sw * delta_I)
        - Output diode carries full load current when switch is off
        - Use when V_out > V_in (e.g., 5V to 12V, battery to 24V)
        - Avoid duty cycle > 0.9 for stability
        """,
        "metadata": {"topic": "boost", "type": "topology"},
    },
    {
        "id": "buck_boost_basics",
        "content": """
        Buck-Boost Converter Basics:
        - Output voltage polarity is inverted (negative output)
        - Can step up or step down: |V_out| = V_in * D / (1-D)
        - Duty cycle D = |V_out| / (V_in + |V_out|)
        - Good for wide input range (e.g., battery 9-18V to -12V)
        - Non-inverting variants: SEPIC, Cuk (same input/output ground)
        - Higher component stress than Buck or Boost alone
        """,
        "metadata": {"topic": "buck_boost", "type": "topology"},
    },
    {
        "id": "flyback_basics",
        "content": """
        Flyback Converter Basics:
        - Isolated topology using coupled inductor (transformer)
        - Stores energy in transformer during switch on, delivers during switch off
        - Turns ratio N = Ns/Np sets voltage ratio: V_out = V_in * N * D / (1-D)
        - Suitable for low to medium power (< 100W typically)
        - Requires snubber circuit for MOSFET protection
        - DCM (discontinuous) or CCM operation possible
        - Use when galvanic isolation is required (safety, multiple outputs)
        """,
        "metadata": {"topic": "flyback", "type": "topology"},
    },
    {
        "id": "inductor_selection",
        "content": """
        Inductor Selection Guidelines:
        - Saturation current must exceed peak inductor current (I_out + delta_I/2)
        - DCR (DC resistance) affects efficiency: lower DCR = less loss
        - Core material: ferrite for high frequency (>100kHz), powdered iron for lower
        - Shielded inductors reduce EMI radiation
        - Typical ripple: 20-40% of load current for good balance
        - For Buck: I_peak = I_out + delta_I/2, ensure I_sat > I_peak
        """,
        "metadata": {"topic": "components", "type": "selection"},
    },
    {
        "id": "capacitor_selection",
        "content": """
        Capacitor Selection for Power Converters:
        - Output cap: low ESR critical for ripple reduction (use MLCC or low-ESR electrolytic)
        - Input cap: handles high ripple current, use low-ESR types
        - Voltage rating: derate 20-50% (e.g., 25V cap for 12V application)
        - MLCC: watch for DC bias and temperature derating (capacitance drops)
        - Electrolytic: higher ESR, use for bulk capacitance at lower frequency
        - Ripple current rating must exceed actual ripple
        """,
        "metadata": {"topic": "components", "type": "selection"},
    },
    {
        "id": "mosfet_selection",
        "content": """
        MOSFET Selection for Power Converters:
        - Vds rating: 1.5-2x max voltage (e.g., 60V for 24V input)
        - Rds(on) and Qg trade-off: lower Rds = higher Qg, consider switching loss
        - For high frequency (>200kHz): prioritize Qg, Qgd for switching loss
        - Body diode: use fast recovery or sync rectifier to avoid reverse recovery
        - Gate drive: ensure sufficient current for fast switching (reduce losses)
        - Thermal: RthJA and power dissipation determine heatsink need
        """,
        "metadata": {"topic": "components", "type": "selection"},
    },
    {
        "id": "switching_frequency",
        "content": """
        Switching Frequency Trade-offs:
        - Higher f_sw: smaller L and C, but higher switching losses and EMI
        - 100-500 kHz common for DC-DC converters
        - Below 100 kHz: larger magnetics, lower cost, easier EMI
        - Above 1 MHz: very small size, but gate drive and layout critical
        - Consider controller capability and dead-time at high frequency
        - EMI filter size decreases with higher frequency (smaller L, C)
        """,
        "metadata": {"topic": "design", "type": "general"},
    },
    {
        "id": "efficiency_considerations",
        "content": """
        Efficiency Optimization:
        - Conduction losses: I^2 * R (MOSFET Rds, inductor DCR, diode Vf)
        - Switching losses: proportional to f_sw, V, I, and transition time
        - Synchronous rectification: replace diode with MOSFET for 2-5% gain
        - Dead time: minimize but avoid shoot-through
        - Gate drive: strong drive reduces switching time and loss
        - Layout: short high-current paths, proper grounding
        - Light load: consider PFM or burst mode for better efficiency
        """,
        "metadata": {"topic": "design", "type": "general"},
    },
    {
        "id": "pwm_basics",
        "content": """
        PWM (Pulse Width Modulation) Basics:
        - Duty cycle D = t_on / T_sw (on-time / period)
        - Average output voltage = D * V_in for Buck
        - Voltage mode control: compare error amplifier output to ramp
        - Current mode control: inner current loop, outer voltage loop
        - Current mode advantages: inherent current limiting, easier compensation
        - Slope compensation needed for current mode at D > 0.5
        """,
        "metadata": {"topic": "control", "type": "general"},
    },
]
