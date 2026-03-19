"""
Power electronics knowledge documents for RAG.

Contains curated content on topologies, design principles, and best practices.
Content derived from Erickson & Maksimovic, Fundamentals of Power Electronics, 3rd Ed.
"""

KNOWLEDGE_DOCUMENTS = [
    # === Erickson Ch2: Steady-State Analysis ===
    {
        "id": "erickson_volt_second_balance",
        "content": """
        Inductor Volt-Second Balance (Erickson Ch2):
        In steady state, the net change in inductor current over one switching period is zero.
        Therefore: integral of v_L(t) over T_s = 0, or <v_L> = 0.
        The total volt-seconds (area under v_L) must be zero each period.
        Application: sketch inductor voltage in each subinterval, equate average to zero, solve for V.
        Example Buck: (Vg-V)*D*Ts + (-V)*D'*Ts = 0 => V = D*Vg.
        """,
        "metadata": {"source": "erickson", "chapter": 2, "topic": "analysis", "type": "theory"},
    },
    {
        "id": "erickson_capacitor_charge_balance",
        "content": """
        Capacitor Charge (Amp-Second) Balance (Erickson Ch2):
        In steady state, the net change in capacitor voltage over one switching period is zero.
        Therefore: integral of i_C(t) over T_s = 0, or <i_C> = 0.
        The average capacitor current must be zero in equilibrium.
        Use this to find steady-state inductor currents and other dc quantities.
        """,
        "metadata": {"source": "erickson", "chapter": 2, "topic": "analysis", "type": "theory"},
    },
    {
        "id": "erickson_small_ripple",
        "content": """
        Small-Ripple (Linear-Ripple) Approximation (Erickson Ch2):
        In well-designed converters, switching ripple is much smaller than dc component: |v_ripple| << V.
        Approximation: v(t) ≈ V, i_L(t) ≈ I. Replace exponential waveforms with linear segments.
        Valid when switching period << natural time constants. Do NOT apply to discontinuous waveforms
        (switch voltage, switch current, inductor voltage). Simplifies analysis greatly.
        Typical ripple: output voltage < 1% of V, inductor current 10-20% of I.
        """,
        "metadata": {"source": "erickson", "chapter": 2, "topic": "analysis", "type": "theory"},
    },
    {
        "id": "erickson_buck_inductor_ripple",
        "content": """
        Buck Converter Inductor Current Ripple (Erickson Ch2):
        delta_i_L = (Vg - V) * D * Ts / (2*L) = V * (1-D) * Ts / (2*L)
        To achieve desired ripple: L = (Vg - V) * D * Ts / (2 * delta_i_L)
        Peak inductor current = I + delta_i_L. Peak flows through switch and diode.
        Typical delta_i_L: 10-20% of full-load dc component I.
        """,
        "metadata": {"source": "erickson", "chapter": 2, "topic": "buck", "type": "formula"},
    },
    {
        "id": "erickson_conversion_ratios",
        "content": """
        DC Conversion Ratios M(D) = V/Vg (Erickson Ch2):
        Buck: M(D) = D. Output always <= input.
        Boost: M(D) = 1/(1-D) = 1/D'. Output >= input. Tends to infinity as D->1.
        Buck-Boost: M(D) = -D/(1-D). Inverting. Can step up or down in magnitude.
        D' = 1 - D (complement of duty cycle).
        """,
        "metadata": {"source": "erickson", "chapter": 2, "topic": "topology", "type": "formula"},
    },
    {
        "id": "erickson_boost_analysis",
        "content": """
        Boost Converter Steady-State Analysis (Erickson Ch2):
        Volt-second balance: Vg*D*Ts + (Vg-V)*D'*Ts = 0 => V = Vg/D'.
        Capacitor charge balance gives inductor dc current: I = V/(R*D').
        Inductor voltage: +Vg when switch on, (Vg-V) when switch off. Vg-V < 0 => V > Vg.
        Practical limit: component losses limit max output voltage.
        """,
        "metadata": {"source": "erickson", "chapter": 2, "topic": "boost", "type": "theory"},
    },
    # === Erickson Ch3: Losses and Efficiency ===
    {
        "id": "erickson_dc_transformer",
        "content": """
        DC Transformer Model (Erickson Ch3):
        Ideal dc-dc converter can be modeled as ideal transformer with turns ratio 1:M(D).
        Power in = power out (lossless). M(D) = V/Vg depends on topology and duty cycle.
        Can add loss elements: inductor DCR, switch Rds, diode Vf.
        Efficiency eta = P_out / P_in. Quality factor Q = P_out / P_loss = eta/(1-eta).
        High Q (e.g. 9 for 90% efficiency) enables small cooling system and high power density.
        """,
        "metadata": {"source": "erickson", "chapter": 3, "topic": "modeling", "type": "theory"},
    },
    {
        "id": "erickson_efficiency_importance",
        "content": """
        Why High Efficiency Matters (Erickson Ch1):
        Efficiency eta = P_out / P_in. Loss P_loss = P_in - P_out.
        Q = P_out / P_loss = eta/(1-eta). At 90% efficiency, Q=9; loss = 11% of output.
        Maximum output power limited by cooling system capacity to remove P_loss.
        Higher efficiency => smaller cooling system, smaller size, lower temperature, better reliability.
        Goal: construct converters of small size that process substantial power at high efficiency.
        """,
        "metadata": {"source": "erickson", "chapter": 1, "topic": "efficiency", "type": "theory"},
    },
    # === Erickson Ch4: Switches ===
    {
        "id": "erickson_switch_modes",
        "content": """
        Switch Modes for High Efficiency (Erickson Ch1):
        Avoid: resistors, linear-mode semiconductors (dissipate power).
        Use: capacitors, inductors (ideally lossless), switched-mode semiconductors.
        Switch off: current zero => P=0. Switch on (saturated): voltage small => P small.
        SPDT switch: duty cycle D = fraction of time in position 1. <v_s> = D*Vg.
        L-C low-pass filter removes switching harmonics, passes dc. Cutoff f0 << f_sw.
        """,
        "metadata": {"source": "erickson", "chapter": 1, "topic": "switching", "type": "theory"},
    },
    {
        "id": "erickson_switch_quadrants",
        "content": """
        Switch Applications by Quadrant (Erickson Ch4):
        Single-quadrant: Buck freewheeling diode, Boost input diode.
        Current-bidirectional 2-quadrant: synchronous rectifier (current can reverse).
        Voltage-bidirectional 2-quadrant: bridge leg for inverter.
        Four-quadrant: full bridge. Synchronous rectifiers replace diodes for higher efficiency.
        """,
        "metadata": {"source": "erickson", "chapter": 4, "topic": "switches", "type": "theory"},
    },
    # === Erickson Ch5: DCM ===
    {
        "id": "erickson_dcm",
        "content": """
        Discontinuous Conduction Mode DCM (Erickson Ch5):
        Occurs when inductor current reaches zero before end of switching period.
        Mode boundary: K = 2*L/(R*Ts) < K_crit(D). DCM when load is light or L is small.
        Conversion ratio M(D,K) in DCM differs from CCM. Output voltage increases with load.
        DCM common in: PFC, light-load efficiency, flyback at low power.
        """,
        "metadata": {"source": "erickson", "chapter": 5, "topic": "dcm", "type": "theory"},
    },
    # === Erickson Ch6: Converter Circuits ===
    {
        "id": "erickson_isolated_topologies",
        "content": """
        Isolated Converter Topologies (Erickson Ch6):
        Full-bridge and half-bridge: isolated Buck, transformer resets via volt-second balance.
        Forward: single-ended, needs reset winding or demag. Good for 100-300W.
        Push-pull: two switches, transformer flux balanced. Flyback: coupled inductor, DCM or CCM.
        Boost-derived isolated: flyback, boost-flyback. SEPIC and Cuk have isolated versions.
        Isolation needed for: safety, multiple outputs, voltage level shifting.
        """,
        "metadata": {"source": "erickson", "chapter": 6, "topic": "isolation", "type": "topology"},
    },
    # === Erickson Ch7-8: AC Modeling ===
    {
        "id": "erickson_ac_modeling",
        "content": """
        AC Modeling of Converters (Erickson Ch7):
        Averaging: trapezoidal moving average gives continuous quantities.
        Perturbation and linearization: d(t)=D+d_hat, v(t)=V+v_hat. Small-signal model.
        Canonical circuit model: standard form for control-to-output, line-to-output.
        State-space averaging: dx/dt = A*x + B*u, averaged over switching states.
        Used for control loop design, stability analysis, compensator design.
        """,
        "metadata": {"source": "erickson", "chapter": 7, "topic": "modeling", "type": "theory"},
    },
    {
        "id": "erickson_rhp_zero",
        "content": """
        Right-Half-Plane Zero (Erickson Ch8):
        Boost and Buck-Boost have RHP zero in control-to-output transfer function.
        RHP zero: gain increases with frequency, phase decreases. Limits achievable bandwidth.
        Cannot be compensated by poles/zeros in left half-plane. Must set crossover below RHP zero.
        Physical origin: increase in duty cycle initially decreases inductor current (Boost).
        Design: keep crossover frequency well below RHP zero frequency.
        """,
        "metadata": {"source": "erickson", "chapter": 8, "topic": "control", "type": "theory"},
    },
    # === Erickson Ch9: Controller Design ===
    {
        "id": "erickson_compensator_types",
        "content": """
        Compensator Types (Erickson Ch9):
        Lead (PD): adds phase boost, improves transient. Zero at lower freq than pole.
        Lag (PI): increases low-freq gain, reduces steady-state error. Pole at origin + zero.
        PID: combined lead-lag. Design for crossover frequency and phase margin (e.g. 52 deg).
        Phase margin: 360 - phase of T at crossover. Related to closed-loop damping.
        Nyquist criterion: for stability, T(s) must not encircle -1.
        """,
        "metadata": {"source": "erickson", "chapter": 9, "topic": "control", "type": "theory"},
    },
    # === Erickson Ch10: Basic Magnetics ===
    {
        "id": "erickson_magnetic_circuits",
        "content": """
        Magnetic Circuits (Erickson Ch10):
        MMF F = H*l_m (magnetomotive force), Flux Phi = B*A_c. Reluctance R = l/(mu*A_c).
        F = Phi*R (analog of Ohm's law). Magnetic circuits solved like electrical circuits.
        Faraday's law: v(t) = n*dPhi/dt = n*A_c*dB/dt. Ampere's law: H*l_m = n*i.
        Inductance L = mu*n^2*A_c/l_m. Saturation: B_sat 1-2T (iron), 0.25-0.5T (ferrite).
        Air gap: R_g = l_g/(mu_0*A_c). Gap prevents saturation, stabilizes L. R_c << R_g typical.
        """,
        "metadata": {"source": "erickson", "chapter": 10, "topic": "magnetics", "type": "theory"},
    },
    {
        "id": "erickson_transformer_model",
        "content": """
        Transformer Modeling (Erickson Ch10):
        Ideal transformer: v1/v2 = n1/n2, i1*n1 = i2*n2. Nonzero core reluctance => magnetizing L.
        Leakage flux (does not link both windings) => series leakage inductances.
        Conventional transformer saturates when applied volt-seconds too large. Air gap has no effect.
        Prevent saturation: increase A_c or primary turns. Flyback: coupled inductor, stores energy.
        """,
        "metadata": {"source": "erickson", "chapter": 10, "topic": "magnetics", "type": "theory"},
    },
    {
        "id": "erickson_core_loss",
        "content": """
        Core Loss and Materials (Erickson Ch10):
        Core loss: hysteresis (B-H loop) + eddy currents. Trade-off: B_sat vs P_fe.
        Laminated iron: highest B_sat (1-2T), highest loss. Ferrite: lowest loss, lowest B_sat (0.25-0.5T).
        Powdered iron, amorphous alloy: between. Skin depth delta = 1/sqrt(pi*mu*f*sigma).
        Eddy currents in windings: skin effect (self), proximity effect (neighboring conductors).
        Interleaving windings reduces proximity loss. MMF diagram for field distribution.
        """,
        "metadata": {"source": "erickson", "chapter": 10, "topic": "magnetics", "type": "theory"},
    },
    # === Erickson Ch11: Inductor Design ===
    {
        "id": "erickson_kg_method",
        "content": """
        Kg Method for Inductor Design (Erickson Ch11):
        Geometrical constant Kg measures effective magnetic size for given copper loss.
        Constraints: max flux density B_max, inductance L, winding resistance R (or P_cu).
        Air gap dominates: n*i = Phi*R_g. B_max = mu_0*n*I_max/l_g. L = n^2/R_g.
        First-pass: select core with Kg sufficient for application, compute gap, turns, wire size.
        Filter inductor: air gap prevents saturation at I_peak = I + delta_i. P_cu = I_rms^2*R.
        """,
        "metadata": {"source": "erickson", "chapter": 11, "topic": "magnetics", "type": "design"},
    },
    # === Erickson Ch12: Transformer Design ===
    {
        "id": "erickson_transformer_design",
        "content": """
        Transformer Design (Erickson Ch12):
        Constraints: core loss, flux density, copper loss. Total loss = P_fe + P_cu.
        Optimum flux density: balance core loss vs copper loss. Delta_B affects both.
        First-pass procedure: choose core, find optimum Delta_B, compute turns, wire sizes.
        AC inductor: different from filter inductor; flux swings both directions.
        """,
        "metadata": {"source": "erickson", "chapter": 12, "topic": "magnetics", "type": "design"},
    },
    # === Erickson Ch13-16: Design-Oriented Analysis ===
    {
        "id": "erickson_feedback_theorem",
        "content": """
        Feedback Theorem (Erickson Ch13):
        Middlebrook's feedback theorem: null double injection for design-oriented analysis.
        Enables analytical solution of complex systems. Applied to compensators, regulators.
        Extra Element Theorem (EET): add element to circuit, find transfer function change.
        n-EET: multiple extra elements. Used for damping resonances, input filter design.
        """,
        "metadata": {"source": "erickson", "chapter": 13, "topic": "analysis", "type": "theory"},
    },
    {
        "id": "erickson_averaged_switch",
        "content": """
        Averaged Switch Modeling (Erickson Ch14):
        Circuit averaging: obtain time-invariant circuit. Perturbation and linearization for ac model.
        Averaged switch network: replace switching elements with equivalent averaged model.
        Enables SPICE simulation of converter dynamics without switching. CCM and DCM models.
        Inclusion of conduction losses in averaged simulation.
        """,
        "metadata": {"source": "erickson", "chapter": 14, "topic": "modeling", "type": "theory"},
    },
    # === Erickson Ch17: Input Filter ===
    {
        "id": "erickson_input_filter",
        "content": """
        Input Filter Design (Erickson Ch17):
        Conducted EMI: input filter attenuates switching harmonics. Design problem: filter affects
        converter transfer functions and can cause instability. Impedance inequalities: Z_out_filter
        << Z_in_converter. Damping: Rf-Cb parallel, Rf-Lb parallel, or Rf-Lb series.
        Undamped input filter can destabilize converter. Nyquist criterion for exact stability boundary.
        Cascading filter sections for higher attenuation.
        """,
        "metadata": {"source": "erickson", "chapter": 17, "topic": "emi", "type": "design"},
    },
    # === Erickson Ch18: Current-Programmed Control ===
    {
        "id": "erickson_current_programmed",
        "content": """
        Current-Programmed Control (Erickson Ch18):
        Inner current loop, outer voltage loop. Inherent current limiting. Oscillation for D > 0.5
        without slope compensation. Tan-Middlebrook model with trapezoidal averaging.
        Transfer functions differ from voltage mode: simpler, single pole. Input filter addition.
        Average current-mode control (ACM): alternative to peak current mode. Sampled-data
        effects at high frequency (near f_sw/2).
        """,
        "metadata": {"source": "erickson", "chapter": 18, "topic": "control", "type": "theory"},
    },
    # === Erickson Ch19: Digital Control ===
    {
        "id": "erickson_digital_control",
        "content": """
        Digital Control of Converters (Erickson Ch19):
        A/D and DPWM quantization. Sampling and delays in control loop. Z-transform for
        discrete-time portion, Laplace for analog. Continuous-to-discrete mapping.
        Digital compensator design: discrete-time realization. Quantization effects.
        Controller delays reduce achievable bandwidth.
        """,
        "metadata": {"source": "erickson", "chapter": 19, "topic": "control", "type": "theory"},
    },
    # === Erickson Ch20-21: Rectifiers and PFC ===
    {
        "id": "erickson_pfc",
        "content": """
        Power Factor and Rectifiers (Erickson Ch20-21):
        Power factor = P/(V_rms*I_rms). Nonlinear loads draw harmonic currents.
        Ideal rectifier: resistive emulation, sinusoidal current, unity power factor.
        CCM Boost PFC: high-quality rectification. DCM Boost, DCM Flyback alternatives.
        Control: average current, current-programmed, CrM, hysteretic, nonlinear carrier.
        Single-phase and three-phase systems. Harmonic standards (IEC, etc.).
        """,
        "metadata": {"source": "erickson", "chapter": 21, "topic": "pfc", "type": "theory"},
    },
    # === Erickson Ch22-23: Resonant and Soft Switching ===
    {
        "id": "erickson_resonant",
        "content": """
        Resonant Converters (Erickson Ch22):
        Sinusoidal tank waveforms vs rectangular PWM. Series resonant, parallel resonant.
        Full bridge below resonance: zero-current switching (ZCS). Above resonance: ZVS.
        Load-dependent: ZVS/ZCS boundary depends on R. LLC: three-element tank, popular for
        isolated high-efficiency. Subharmonic modes in series resonant converter.
        """,
        "metadata": {"source": "erickson", "chapter": 22, "topic": "resonant", "type": "theory"},
    },
    {
        "id": "erickson_soft_switching",
        "content": """
        Soft Switching (Erickson Ch23):
        ZCS quasi-resonant switch: current zero at turn-off. ZVS quasi-resonant: voltage zero at turn-on.
        Reduces switching loss. Diode, MOSFET, IGBT switching mechanisms.
        Zero-voltage transition (ZVT) full bridge. Auxiliary switch approach. ARCP.
        Soft switching in PWM converters: add resonant elements, auxiliary circuits.
        """,
        "metadata": {"source": "erickson", "chapter": 23, "topic": "resonant", "type": "theory"},
    },
    # === Original PEA documents (retained) ===
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
