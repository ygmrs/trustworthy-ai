export default function EmailDetail({ email, onRun, running }) {
    if (!email) {
        return (
            <div className="email-detail email-detail-empty">
                <p>Select an email from the inbox to begin triage.</p>
            </div>
        );
    }

    return (
        <div className="email-detail">
            <div className="email-meta">
                <div className="email-field">
                    <span className="field-label">From</span>
                    <span className="field-value">
            {email.sender.name} &lt;{email.sender.address}&gt;
          </span>
                </div>
                <div className="email-field">
                    <span className="field-label">Subject</span>
                    <span className="field-value">{email.subject}</span>
                </div>
            </div>

            <pre className="email-body">{email.body}</pre>

            <button className="run-btn" onClick={onRun} disabled={running}>
                {running ? 'Triaging…' : '▶  Run Triage'}
            </button>
        </div>
    );
}