# McAlister Wing case using overset capability

The objective of this study is to establish the performance of the DES
turbulence modeling for simulations of the McAlister experiments. The
experimental setup and data for this case can be found
in
[NACA 0015 wing pressure and trailing vortex measurements (1981) McAlister and Takahashi](http://www.dtic.mil/cgi-bin/GetTRDoc?AD=ADA257317).

For these runs, the initial conditions were set as follows. The Re =
\frac{c \rho V_\infty}{\mu} = 1.5 * 10^6 (corresponding to V_\infty =
46 m/s, M_\infty = 0.13, see page 9 of the McAlister paper). The
density of air is \rho=1.225 kg/m^3. The viscosity is defined by the
Reynolds number, \mu = \frac{\rho c V_\infty}{Re} = 0.00003756 kg/(m s).

The turbulence modeling framework is DES, a hybrid RANS-LES framework,
with SST as the RANS model and Smagorinsky as the LES
model. Implementation details can be found
[here](http://nalu-wind.readthedocs.io/en/latest/source/theory/turbulenceModeling.html)
and
[here](http://nalu-wind.readthedocs.io/en/latest/source/theory/supportedEquationSet.html#shearstress-transport-sst-rans-model-suite)
in the Nalu theory documentation. The IC and inflow BC for the SST
model variables are set according to k_farfield = 3/2 TI^2 U_\infty =
0.69, where TI = 0.1, and omega_farfield = 5 U_\infty / c = 230 1/s.

