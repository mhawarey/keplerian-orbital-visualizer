# Dynamic Keplerian Orbital Visualizer

An interactive 3D orbital mechanics visualization tool. Input the six classical Keplerian orbital elements and visualize the resulting orbit around Earth with real-time animation, ground track projection, and orbital energy analysis.

## Features

- **Six Keplerian Elements Input** — Semi-major axis, eccentricity, inclination, RAAN, argument of periapsis, true anomaly
- **3D Orbital Visualization** — Matplotlib-based interactive 3D plot with Earth sphere
- **Real-Time Animation** — Satellite propagation using Kepler's equation (Newton-Raphson solver)
- **Ground Track Projection** — Sub-satellite point trace on Earth's surface
- **Orbital Energy Graph** — Velocity vs. true anomaly with live marker
- **Adjustable Speed** — Animation speed control from 0.1× to 10×

## Physics Implementation

- Kepler's Third Law for orbital period
- Mean ↔ Eccentric ↔ True anomaly conversions
- Full 3D rotation matrices (ω, i, Ω) for reference frame transformation
- Vis-viva equation for velocity computation

## Requirements

```
numpy
matplotlib
tkinter (included with Python)
```

## Usage

```bash
pip install numpy matplotlib
python orbital_visualization_dynamic.py
```

## Author

**Dr. Mosab Hawarey**
PhD, Geodetic & Photogrammetric Engineering (ITU) | MSc, Geomatics (Purdue) | MBA (Wales) | BSc, MSc (METU)

- GitHub: https://github.com/mhawarey
- Personal: https://hawarey.org/mosab
- ORCID: https://orcid.org/0000-0001-7846-951X

## License

MIT License
