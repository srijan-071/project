import { Activity } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function Header() {
  const [sessionId] = useState(() => String(Math.floor(Math.random() * 99999)).padStart(5, '0'));
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(interval);
  }, []);

  const items = [
    { label: 'SYSTEM', value: 'ACTIVE', color: 'var(--accent-primary)' },
    { label: 'MODEL', value: 'FINSIGHT-TX' },
    { label: 'LATENCY', value: '~47MS' },
    { label: 'SESSION', value: sessionId },
  ];

  return (
    <header className="app-header">
      <div style={{ display: 'flex', alignItems: 'center', gap: 24, flex: 1 }}>
        {/* Title */}
        <span style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '0.65rem',
          fontWeight: 600,
          letterSpacing: '0.12em',
          color: 'var(--text-muted)',
        }}>
          FINANCIAL INTELLIGENCE TERMINAL
        </span>

        {/* Divider */}
        <div style={{ width: 1, height: 20, background: 'var(--border-color)' }} />

        {/* Status Items */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
          {items.map(item => (
            <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.6rem',
                letterSpacing: '0.08em',
                color: 'var(--text-dim)',
              }}>
                {item.label}
              </span>
              <span style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.6rem',
                fontWeight: 600,
                letterSpacing: '0.06em',
                color: item.color || 'var(--text-secondary)',
              }}>
                // {item.value}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Right side */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '0.6rem',
          color: 'var(--text-dim)',
        }}>
          {time.toLocaleTimeString('en-US', { hour12: false })}
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span className="status-dot status-dot-online" />
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '0.6rem',
            fontWeight: 600,
            color: 'var(--accent-primary)',
          }}>
            MODEL ONLINE
          </span>
        </div>
      </div>
    </header>
  );
}
