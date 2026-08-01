import { useState } from 'react';
import { motion } from 'framer-motion';
import { GitCompare, Send } from 'lucide-react';
import { compareArticles } from '../services/api';

function ComparisonCard({ label, data }) {
  if (!data) return null;
  return (
    <div className="panel">
      <div className="panel-header"><span className="panel-title">{label}</span></div>
      <div className="panel-body">
        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: 12, lineHeight: 1.5 }}>{data.text}</div>

        <div className={`sentiment-badge sentiment-badge-${data.sentiment}`} style={{ marginBottom: 12 }}>
          {data.sentiment?.toUpperCase()} — {(data.confidence * 100).toFixed(1)}%
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 12 }}>
          <div>
            <div className="label-terminal" style={{ marginBottom: 2 }}>SENTIMENT SCORE</div>
            <div className="font-mono" style={{ fontSize: '1.2rem', fontWeight: 700, color: data.sentiment_score >= 0 ? 'var(--positive)' : 'var(--danger)' }}>
              {data.sentiment_score >= 0 ? '+' : ''}{data.sentiment_score?.toFixed(2)}
            </div>
          </div>
          <div>
            <div className="label-terminal" style={{ marginBottom: 2 }}>MARKET IMPACT</div>
            <div className="font-mono" style={{ fontSize: '1rem', fontWeight: 600, color: (data.market_impact?.impact_score || 50) >= 60 ? 'var(--positive)' : (data.market_impact?.impact_score || 50) <= 40 ? 'var(--danger)' : 'var(--neutral-color)' }}>
              {data.market_impact?.market_impact}
            </div>
          </div>
        </div>

        {/* Probabilities */}
        {data.probabilities && Object.entries(data.probabilities).map(([key, val]) => (
          <div key={key} style={{ marginBottom: 4 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
              <span className="label-terminal">{key}</span>
              <span className="font-mono" style={{ fontSize: '0.7rem' }}>{(val * 100).toFixed(1)}%</span>
            </div>
            <div className="progress-bar">
              <div className={`progress-fill progress-fill-${key === 'positive' ? 'positive' : key === 'negative' ? 'negative' : 'neutral'}`} style={{ width: `${val * 100}%` }} />
            </div>
          </div>
        ))}

        {/* Entities */}
        {data.entities?.entities?.length > 0 && (
          <div style={{ marginTop: 12 }}>
            <div className="label-terminal" style={{ marginBottom: 6 }}>ENTITIES</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
              {data.entities.entities.map((e, i) => (
                <span key={i} className="tag tag-info">{e.entity}</span>
              ))}
            </div>
          </div>
        )}

        {/* Keywords */}
        {data.keywords?.length > 0 && (
          <div style={{ marginTop: 12 }}>
            <div className="label-terminal" style={{ marginBottom: 6 }}>KEYWORDS</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
              {data.keywords.map((k, i) => (
                <span key={i} className="tag tag-neutral">{k.keyword || k}</span>
              ))}
            </div>
          </div>
        )}

        {/* Risk */}
        {data.risk && (
          <div style={{ marginTop: 12 }}>
            <div className="label-terminal" style={{ marginBottom: 4 }}>RISK LEVEL</div>
            <span className="font-mono" style={{ fontSize: '0.8rem', fontWeight: 600, color: data.risk.overall_risk_level === 'HIGH' ? 'var(--danger)' : data.risk.overall_risk_level === 'MEDIUM' ? 'var(--warning)' : 'var(--positive)' }}>
              {data.risk.overall_risk_level} ({data.risk.overall_risk_score}/100)
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

export default function Compare() {
  const [textA, setTextA] = useState('');
  const [textB, setTextB] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCompare = async () => {
    if (!textA.trim() || !textB.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await compareArticles(textA.trim(), textB.trim());
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Comparison failed');
    }
    setLoading(false);
  };

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <div className="label-accent" style={{ marginBottom: 4 }}>COMPARISON / 04</div>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', fontWeight: 600 }}>News Comparison Mode</h1>
      </div>

      {/* Input */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
        <div className="panel">
          <div className="panel-header"><span className="panel-title">ARTICLE A</span></div>
          <div className="panel-body">
            <textarea className="input-terminal" rows={5} value={textA} onChange={e => setTextA(e.target.value)} placeholder="Paste first article..." />
          </div>
        </div>
        <div className="panel">
          <div className="panel-header"><span className="panel-title">ARTICLE B</span></div>
          <div className="panel-body">
            <textarea className="input-terminal" rows={5} value={textB} onChange={e => setTextB(e.target.value)} placeholder="Paste second article..." />
          </div>
        </div>
      </div>

      <div style={{ textAlign: 'center', marginBottom: 24 }}>
        <button className="btn btn-primary" onClick={handleCompare} disabled={loading || !textA.trim() || !textB.trim()}>
          <GitCompare size={14} /> {loading ? 'COMPARING...' : 'COMPARE ARTICLES'}
        </button>
      </div>

      {error && <div className="panel" style={{ marginBottom: 24, borderColor: 'rgba(255,59,92,0.3)' }}><div className="panel-body font-mono" style={{ color: 'var(--danger)', fontSize: '0.8rem' }}>{error}</div></div>}

      {result && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          {/* Delta Summary */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 16 }}>
            {[
              ['SCORE DELTA', `${result.deltas.sentiment_score >= 0 ? '+' : ''}${result.deltas.sentiment_score.toFixed(2)}`, result.deltas.sentiment_score >= 0 ? 'var(--positive)' : 'var(--danger)'],
              ['CONFIDENCE Δ', `${result.deltas.confidence >= 0 ? '+' : ''}${(result.deltas.confidence * 100).toFixed(1)}%`],
              ['IMPACT Δ', `${result.deltas.impact_score >= 0 ? '+' : ''}${result.deltas.impact_score}`],
              ['SENTIMENT', result.deltas.sentiment_match ? 'MATCH' : 'DIFFERS', result.deltas.sentiment_match ? 'var(--positive)' : 'var(--warning)'],
            ].map(([label, value, color]) => (
              <div key={label} className="metric-card">
                <div className="metric-label">{label}</div>
                <div className="metric-value" style={{ color: color || 'var(--text-primary)', fontSize: '1.2rem', marginTop: 4 }}>{value}</div>
              </div>
            ))}
          </div>

          {/* Side-by-side Results */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <ComparisonCard label="ARTICLE A" data={result.article_a} />
            <ComparisonCard label="ARTICLE B" data={result.article_b} />
          </div>
        </motion.div>
      )}
    </div>
  );
}
