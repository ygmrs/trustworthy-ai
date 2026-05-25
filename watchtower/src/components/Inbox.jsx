export default function Inbox({ emails, selectedId, onSelect }) {
    function senderDomain(address) {
        return address.split('@')[1] ?? address;
    }

    function timeLabel(iso) {
        const d = new Date(iso);
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    return (
        <div className="inbox">
            <div className="inbox-header">Reported Emails</div>
            <ul className="inbox-list">
                {emails.map((email) => (
                    <li
                        key={email.id}
                        className={`inbox-item ${selectedId === email.id ? 'selected' : ''}`}
                        onClick={() => onSelect(email)}
                    >
                        <div className="inbox-item-top">
                            <span className="inbox-sender">{email.sender.name}</span>
                            <span className="inbox-time">{timeLabel(email.received_at)}</span>
                        </div>
                        <div className="inbox-subject">{email.subject}</div>
                        <div className="inbox-domain">{senderDomain(email.sender.address)}</div>
                    </li>
                ))}
            </ul>
        </div>
    );
}