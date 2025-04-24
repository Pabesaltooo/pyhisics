$$
\boxed{\text{Faraday-Lenz:} \quad {\huge \varepsilon}_{\text{F-L}} = - \frac{d\Phi_m}{dt} = - \frac{d}{dt} \iint_S \vec{B} \cdot d \vec{S}} \\[1em]
\boxed{\text{Kirchoff-en 2. legea: \quad} {\huge \varepsilon}_{\text{K}} = \sum \Delta V_i  \xlongequal{\text{RC}} \Delta V_R + \Delta V_C = \frac{Q}{C} + IR = \frac{Q}{C} + \frac{dQ}{dt} R}
$$
---



$$
{\huge \varepsilon}_{\text{F-L}} 
 =  - \frac{d\Phi_m }{dt}  = - \frac{d}{dt} \iint_S \vec{B} \cdot d \vec{S} \quad \xlongequal{\vec B(t) \perp d \vec S} \quad - \frac{d}{dt} B(t) \iint_S d S = - S \frac{d}{dt} B(t) \quad \xlongequal{B(t) = B_0 t} \quad - S \frac{d}{dt} B_0 t = -S B_0 
$$

$$
{\huge \varepsilon}_{\text{K}} = \sum \Delta V_i  \xlongequal{\text{RC}} \Delta V_R + \Delta V_C = \frac{Q}{C} + IR = \frac{Q}{C} + \frac{dQ}{dt} R \quad \Longrightarrow \quad  \frac{dQ}{dt} = \frac{{\huge \varepsilon}_{\text{K}}}{R} - \frac{Q}{RC}  = -\frac{{\huge \varepsilon}_{\text{K}} C-Q}{RC}
$$

$$

\frac{dQ}{dt} \xlongequal{{\ \varepsilon} = S B_0 \\ } -\frac{S B_0 C-Q}{RC} \quad \Longrightarrow \quad \frac{dQ}{S B_0 C-Q} = - \frac{dt}{RC} \quad \Longrightarrow \quad \int_{Q_0}^{Q} \frac{dQ}{S B_0 C-Q} = \int_{t_0}^{t}- \frac{dt}{RC} \\
\ln\left|\,  S B_0 C -Q \,\right| {\huge |}_{Q_0}^{Q} = -\frac{t}{RC}{\huge |}_{t_0}^{t} \quad \Longrightarrow \quad \ln \left|\,  \frac{S B_0 C - Q}{S B_0 C - \cancel{Q_0}} \,\right| = -\frac{t - \cancel{t_0}}{RC} \quad \Longrightarrow \quad \frac{S B_0 C - Q}{S B_0 C} = e^{-{t}/{RC}} \\[1em]

S B_0 C - Q = S B_0 C e^{-{t}/{RC}} \quad \Longrightarrow \quad - Q = S B_0 C e^{-{t}/{RC}} - S B_0 C\quad \Longrightarrow \quad \boxed{Q = {S B_0 C} {\left( 1 - e^{-{t}/{RC}} \right)}}
$$

$$
I = \frac{dQ}{dt} = \frac{d}{dt} {S B_0 C} {\left( 1 - e^{-{t}/{RC}} \right)} = \cancel{\frac{d}{dt} {S B_0 C} \cdot 1}  + \frac{d}{dt} {S B_0 C} {\left(- e^{-{t}/{RC}} \right)}  = \boxed{\frac{S B_0}{R} { e^{-{t}/{RC}} } = I}
$$
