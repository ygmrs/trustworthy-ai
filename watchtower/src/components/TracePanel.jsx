import { useEffect, useRef } from 'react';

const KIND_LABELS = {
    thinking: { icon: '◌', cls: 'trace-thinking' },
    tool_call: { icon: '⚙', cls: 'trace-tool' },
    tool_result: { icon: '↩', cls: 'trace-result' },
    guard_pass: { icon: '✓', cls: 'trace-pass' },
    guard_block: { icon: '✕', cls: 'trace-block' },
    audit: { icon: '📋', cls: 'trace-audit' },
    final: { icon: '◉', cls: 'trace-final' },
};

export default function TracePanel({ steps, running }) {
    const bottomRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [steps]);

    return (
        <div className="trace-panel">
            <div className="trace-header">
                <span>Agent Trace</span>
                {running && <span className="trace-live">● LIVE</span>}
            </div>

            <div className="trace-body">
                {steps.length === 0 && !running && (
                    <p className="trace-empty">Run triage to see the agent's reasoning here.</p>
                )}

                {steps.map((step) => {
                    const meta = KIND_LABELS[step.kind] ?? { icon: '·', cls: '' };
                    return (
                        <div key={step.step} className={`trace-step ${meta.cls}`}>
                            <span className="trace-icon">{meta.icon}</span>
                            <div className="trace-content">
                                <span className="trace-label">{step.label}</span>
                                {step.detail && <span className="trace-detail">{step.detail}</span>}
                                {step.data && (
                                    <pre className="trace-data">{JSON.stringify(step.data, null, 2)}</pre>
                                )}
                            </div>
                        </div>
                    );
                })}
                <div ref={bottomRef} />
            </div>
        </div>
    );
}