# OmniSciences Research

Open research and public APIs from [OmniSciences LLC](https://omnisciences.io).

## What's Here

### Client SDK (`omnisciences/`)

Python client for the OmniSciences API platform:

```bash
pip install omnisciences
```

```python
from omnisciences.client import DTIClient, PCETClient, PortfolioClient

# DTI curvature analysis
dti = DTIClient(api_key="omni_...")
result = dti.analyze(tensors=my_tensors)

# PCET rate prediction
pcet = PCETClient(api_key="omni_...")
rate = pcet.compute_rate(delta_G=-0.5, lambda_reorg=1.2, coupling=0.01)

# Riemannian portfolio optimization
port = PortfolioClient(api_key="omni_...")
weights = port.optimize(returns=my_returns, method="min_variance")
```

### Demo Notebooks (`notebooks/`)

Interactive Colab notebooks — no install required:

| Notebook | Description | Colab |
|----------|-------------|-------|
| `dti_demo.ipynb` | Diffusion tensor curvature analysis | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sausterm/omniscience-research/blob/main/notebooks/dti_demo.ipynb) |
| `pcet_demo.ipynb` | PCET rate prediction with Monte Carlo UQ | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sausterm/omniscience-research/blob/main/notebooks/pcet_demo.ipynb) |
| `portfolio_demo.ipynb` | Riemannian portfolio optimization | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sausterm/omniscience-research/blob/main/notebooks/portfolio_demo.ipynb) |
| `bci_demo.ipynb` | Brain-computer interface signal analysis | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sausterm/omniscience-research/blob/main/notebooks/bci_demo.ipynb) |
| `integration_*.ipynb` | Third-party integrations (cvxportfolio, PyPortfolioOpt, Riskfolio) | |

### omni_toolkit (`omni_toolkit/`)

Open-source math library for symmetric space physics. Paper reproducibility code.

```bash
cd omni_toolkit && pip install -e ".[dev]"
```

Modules: `core/` (Lie algebras, symmetric spaces, curvature), `dynamics/` (RG running, effective potentials), `topology/` (index theorems, complex structures), `mixing/`, `fermions/`, `breaking/`, `consistency/`.

### Research Papers (`papers/`)

| Programme | Papers | Topic |
|-----------|--------|-------|
| **Consciousness** | Structural Idealism, Formal Correspondences, Technical Appendix | Θ: Con → MB functorial correspondence |
| **Metric Bundle** | Papers 1–8 | Gauge unification from Met(X⁴) geometry |
| **Portfolio** | Riemannian Portfolio Optimization | SPD manifold methods for finance |

### Computation Scripts (`computations/`)

Python verification scripts for the Metric Bundle papers: `core/`, `fermions/`, `mixing/`, `symmetry_breaking/`, `cosmology/`, `consistency/`, `quantum/`, `consciousness/`.

## API Products

| Product | Endpoint | Description |
|---------|----------|-------------|
| **PCET Engine** | `pcet.omnisciences.io` | Proton-coupled electron transfer rate prediction |
| **DTI Analysis** | `dti.omnisciences.io` | Riemannian diffusion tensor imaging |
| **Portfolio** | `portfolio.omnisciences.io` | SPD manifold portfolio optimization |
| **BCI Analysis** | `bci.omnisciences.io` | Brain-computer interface signal analysis |

Free tier available for all products. See [omnisciences.io](https://omnisciences.io) for pricing.

## Key Results

### Physics (Metric Bundle Programme)
- DeWitt metric on Met(X⁴) has signature **(6,4)** → SO(6,4) → **Pati-Salam** gauge group
- sin²θ_W = 0.2312 from two-step PS running (exact match to observation)
- α_PS = 27/(128π²) ≈ 0.0214 (7% from observed, zero free parameters)
- N_G = 3 generations from Spin^c index on K3

### Consciousness (Θ: Con → MB)
- Functorial correspondence between Conscious Agent networks and Markov blanket systems
- Compositional structure preserved under BMIC
- Inverse mapping: Agenthood Tetrad (N1–N4) characterizes representable systems

### PCET Engine
- 15 benchmark enzyme systems validated (~15% mean error)
- Multi-channel vibronic rates with Monte Carlo uncertainty quantification
- Sub-100ms inference

## Licenses

- **Papers** (`.tex`, `.pdf`): [CC BY 4.0](LICENSE-CC-BY-4.0)
- **Code** (`.py`): [MIT](LICENSE-MIT)

## Citation

See [CITATION.cff](CITATION.cff) for machine-readable citation metadata.

## Author

**Sloan Austermann** — OmniSciences LLC — sloan@omnisciences.org
