export default function AuditLog({ entries }) {
    if (!entries || entries.length === 0) {
        return (
            <div className="audit-log">
                <div className="audit-header">Audit Log</div>
                <p className="audit-empty">No entries yet.</p>
            </div>
        );
    }

    return (
        <div className="audit-log">
            <div className="audit-header">Audit Log</div>
            <ul className="audit-list">
                {entries.map((entry, i) => (
                    <li key={i} className="audit-entry">
            <span className="audit-time">
              {new Date(entry.timestamp).toLocaleTimeString()}
            </span>
                        <span className="audit-agent">{entry.agent_id}</span>
                        <span className="audit-action">{entry.action}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
}