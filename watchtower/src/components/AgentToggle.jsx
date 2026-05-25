export default function AgentToggle({ selected, onChange }) {
    const agents = [
        { id: 'icarus', label: 'Icarus', sub: 'The prototype' },
        { id: 'aegis', label: 'Aegis', sub: 'The engineered agent' },
    ];

    return (
        <div className="agent-toggle">
            {agents.map((agent) => (
                <button
                    key={agent.id}
                    className={`toggle-btn toggle-${agent.id} ${selected === agent.id ? 'active' : ''}`}
                    onClick={() => onChange(agent.id)}
                >
                    <span className="toggle-name">{agent.label}</span>
                    <span className="toggle-sub">{agent.sub}</span>
                </button>
            ))}
        </div>
    );
}