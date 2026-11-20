---
id: flight-delay-risk-model
title: Cascading Flight-Delay Risk Model
type: project
scale: 2                     # TODO: provisional, based on the draft rubric
skills: [Python, PyTorch, Pandas, Feature engineering, Data fusion]
summary: "Cascading-delay risk model for DFW airport, presented to American Airlines as 1 of 6 finalists among 30 teams in the American Airlines Data Challenge."
links: []                    # TODO: add the repo link if there is one
---
- Built a cascading-delay risk identification model specialized to DFW airport, presented to AA as 1 of 6 finalists among 30 teams.
- Performed data fusion across multi-source aviation data (flight, weather, and atmospheric datasets), reconciling mismatched time granularities and join keys into a unified training set.
- Engineered 40+ features to train 4-layer PyTorch neural network flagging flights at high risk of propagating delays with 0.65 F1.
