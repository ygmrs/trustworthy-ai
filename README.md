# Trustworthy AI

Companion repository for the talk **"Engineering AI for Real-World Trust:
From Prototypes to Production-Grade Systems"** by Yagmur Sahin
at SECON NJ 2026.

This repo contains a live demo comparing two AI agents performing the
same phishing-triage task:

- **Icarus** — a naked prototype agent. Classifies threats correctly on the happy path.
  No input guards, no output controls, no observability, no audit trail.
  Correctness depends entirely on the model. No guarantees. No proof.
- **Aegis** — the same agent wrapped in four engineering pillars:
  containment, observability, verifiability, governance.
  Same model, same task, same prompt. Different engineering.

## Structure

```
trustworthy-ai/
├── agent-forge/     Python + FastAPI backend hosting both agents
├── watchtower/      React + Vite frontend — inbox UI and live trace panel
├── docs/            Architecture diagrams and slide assets
├── .gitignore
└── README.md
```

## Quickstart

See [`agent-forge/README.md`](agent-forge/README.md) and
[`watchtower/README.md`](watchtower/README.md).

## The Four Pillars

Aegis is engineered around four pillars:

1. **Security** — sandboxed tools, scoped permissions, blast-radius limits
2. **Observability** — structured traces of every step, replayable
3. **Guardrails** — input and output guards, risk gating on tool calls
4. **Governance** — append-only audit log with full accountability

## Icarus vs. Aegis

### Icarus Execution

![Icarus execution on attack email](docs/icarus-execution.png)

Icarus processed the attack email and forwarded the user’s inbox to the attacker-controlled address. No guardrail blocked the action, no policy violation was surfaced, and the data exfiltration path remained unchecked.

### Aegis Block

![Aegis block on attack email](docs/aegis-block.png)

Aegis evaluated the same email before LLM execution. The input guard fired with 100% confidence, the LLM was not called, the matched attack pattern was identified, and the decision was recorded through auditable/replayable trace entries.

### Live AI Agent Runs

<video src="docs/live-ai-agent-runs.mp4" controls width="100%">
  Your browser does not support the video tag.
</video>

[Watch the full live AI agent run demo](docs/ai-agents.mov)

This recording shows the end-to-end live demo flow: Icarus executing the phishing-triage task without containment, guardrails, observability, or auditability; and Aegis running the same scenario with input protection, trace visibility, policy enforcement, and auditable decision records.

## Author

**Yagmur Sahin** — Head & VP of Engineering  
IEEE Senior Member · 5 US Patents · M.S. Computer Engineering


## License

Released under the [MIT License](LICENSE).

MIT License — open source, free to use, fork, and distribute with attribution.

If this architecture, the four-pillar pattern influences your production AI systems, or any part of this codebase in your own work, a credit or a star goes a long way.

© 2026 Yagmur Sahin. All rights reserved under the MIT License.
