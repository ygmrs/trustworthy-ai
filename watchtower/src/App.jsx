import { useEffect, useState, useRef } from 'react';
import AgentToggle from './components/AgentToggle.jsx';
import Inbox from './components/Inbox.jsx';
import EmailDetail from './components/EmailDetail.jsx';
import TracePanel from './components/TracePanel.jsx';
import AuditLog from './components/AuditLog.jsx';

export default function App() {
  const [health, setHealth]           = useState(null);
  const [emails, setEmails]           = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState('icarus');
  const [traceSteps, setTraceSteps]   = useState([]);
  const [running, setRunning]         = useState(false);
  const [auditEntries, setAuditEntries] = useState([]);
  const [lastResult, setLastResult]   = useState(null);
  const [tooltipVisible, setTooltipVisible] = useState(false);
  const eventSourceRef = useRef(null);

  useEffect(() => {
    fetch('/api/health')
        .then((r) => r.json())
        .then(setHealth)
        .catch(() => setHealth(null));

    fetch('/api/emails')
        .then((r) => r.json())
        .then((data) => setEmails(data.emails));
  }, []);

  function clearRunState() {
    setTraceSteps([]);
    setLastResult(null);
    setAuditEntries([]);
  }

  function handleSelectEmail(email) {
    setSelectedEmail(email);
    clearRunState();
  }

  function handleAgentChange(agentId) {
    setSelectedAgent(agentId);
    clearRunState();
  }

  async function handleRun() {
    if (!selectedEmail || running) return;
    setRunning(true);
    setTraceSteps([]);
    setLastResult(null);
    setAuditEntries([]);

    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    try {
      const res = await fetch(`/api/run/${selectedAgent}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email_id: selectedEmail.id }),
      });
      const result = await res.json();
      setLastResult(result);
      setTraceSteps(result.trace);

      const auditRes = await fetch('/api/audit');
      const auditData = await auditRes.json();
      setAuditEntries(auditData.entries);
    } catch (err) {
      console.error('Run failed:', err);
    } finally {
      setRunning(false);
    }
  }

  function getVerdictSummary(result) {
    if (result.blocked) return '🛡️  Blocked — Threat prevented by guardrail policy';
    const v = result.verdict.toLowerCase();
    if (['malicious', 'quarantined'].some(term => v.includes(term))) return '🚨  Malicious threat detected — email quarantined';
    if (v.includes('suspicious')) return '⚠️  Suspicious — flagged for review';
    if (v.includes('safe'))       return '✅  Safe — no threats detected';
    return '🔍  Triage complete';
  }

  return (
      <div className="app">
        <header className="header">
          <div className="header-left">
            <h1>AI Agents</h1>
            <span className="subtitle">Engineering AI for Real-World Trust</span>
          </div>
          <div className="header-right">
            {health ? (
                <span className="badge badge-ok">● {health.service} connected</span>
            ) : (
                <span className="badge badge-err">● backend unreachable</span>
            )}
          </div>
        </header>

        <div className="toolbar">
          <AgentToggle selected={selectedAgent} onChange={handleAgentChange} />
          {lastResult && (
              <div className="verdict-wrapper">
                <div
                    className={`verdict ${(() => {
                      if (lastResult.blocked) return 'verdict-blocked';
                      const v = lastResult.verdict.toLowerCase();
                      if (['malicious', 'quarantined'].some(term => v.includes(term))) return 'verdict-malicious';
                      if (v.includes('suspicious')) return 'verdict-warn';
                      if (v.includes('safe'))       return 'verdict-ok';
                      return 'verdict-info';
                    })()}`}
                    onMouseEnter={() => setTooltipVisible(true)}
                    onMouseLeave={() => setTooltipVisible(false)}
                >
                  {getVerdictSummary(lastResult)}
                </div>
                {tooltipVisible && (
                    <div className="verdict-tooltip">
                      {lastResult.blocked
                          ? lastResult.block_reason
                          : lastResult.verdict.replace(/\*\*/g, '').trim()}
                    </div>
                )}
              </div>
          )}
        </div>

        <div className="workspace">
          <aside className="sidebar">
            <Inbox
                emails={emails}
                selectedId={selectedEmail?.id}
                onSelect={handleSelectEmail}
            />
          </aside>

          <main className="content">
            <EmailDetail
                email={selectedEmail}
                onRun={handleRun}
                running={running}
            />
          </main>

          <aside className="tracebar">
            <TracePanel steps={traceSteps} running={running} />
            <AuditLog entries={auditEntries} />
          </aside>
        </div>
      </div>
  );
}