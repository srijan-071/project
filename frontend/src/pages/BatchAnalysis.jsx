import { useState } from 'react';
import { motion } from 'framer-motion';
import { Layers, Send, Upload } from 'lucide-react';
import { batchAnalyze } from '../services/api';

export default function BatchAnalysis() {
  const [text, setText] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 3);
    if (lines.length === 0) return;
    setLoading(true);
    setError(null);
    try {
      const data = await batchAnalyze(lines);
      setResults(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed');
    }
    setLoading(false);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const content = await file.text();
    setText(content);
  };

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <div className="label-accent" style={{ marginBottom: 4 }}>BATCH ANALYSIS / 03</div>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', fontWeight: 600 }}>Batch News Analyzer</h1>
      </div>

      <div className="panel" style={{ marginBottom: 24 }}>
        <div className="panel-header">
          <span className="panel-title">PASTE MULTIPLE HEADLINES (ONE PER LINE)</span>
          <label className="btn btn-sm" style={{ cursor: 'pointer' }}>
            <Upload size={10} /> UPLOAD FILE
            <input type="file" accept=".txt,.csv" onChange={handleFileUpload} style={{ display: 'none' }} />
          </label>
        </div>
        <div className="panel-body">
          <textarea className="input-terminal" rows={8} value={text} onChange={e => setText(e.target.value)}
            placeholder={"Company reports record quarterly profit...\nShares declined after weak earnings...\nAnnual shareholder meeting scheduled...\nRevenue beat expectations but costs rose..."} style={{ marginBottom: 12 }} />
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <button className="btn btn-primary" onClick={handleAnalyze} disabled={loading}>
              <Layers size={12} /> {loading ? 'ANALYZING...' : 'ANALYZE BATCH'}
            </button>
            <span className="font-mono" style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
              HEADLINES: {text.split('\n').filter(l => l.trim()).length} / 50
            </span>
          </div>
        </div>
      </div>

      {error && (
        <div className="panel" style={{ marginBottom: 24, borderColor: 'rgba(255,59,92,0.3)' }}>
          <div className="panel-body font-mono" style={{ color: 'var(--danger)', fontSize: '0.8rem' }}>{error}</div>
        </div>
      )}

      {results && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          {/* Summary */}
          {results.summary && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 12, marginBottom: 16 }}>
              {[
                ['TOTAL', results.summary.total],
                ['POSITIVE', results.summary.positive_count, 'var(--positive)'],
                ['NEUTRAL', results.summary.neutral_count, 'var(--neutral-color)'],
                ['NEGATIVE', results.summary.negative_count, 'var(--danger)'],
                ['AVG CONF', `${(results.summary.avg_confidence * 100).toFixed(1)}%`, 'var(--accent-primary)'],
              ].map(([label, value, color]) => (
                <div key={label} className="metric-card">
                  <div className="metric-label">{label}</div>
                  <div className="metric-value" style={{ color: color || 'var(--text-primary)', fontSize: '1.4rem', marginTop: 4 }}>{value}</div>
                </div>
              ))}
            </div>
          )}

          {/* Results Table */}
          <div className="panel">
            <div className="panel-header"><span className="panel-title">BATCH RESULTS</span></div>
            <div className="panel-body" style={{ overflowX: 'auto' }}>
              <table className="table-terminal">
                <thead><tr><th>#</th><th>HEADLINE</th><th>SENTIMENT</th><th>CONFIDENCE</th><th>SCORE</th><th>MARKET IMPACT</th></tr></thead>
                <tbody>
                  {results.results?.map(r => (
                    <tr key={r.index}>
                      <td className="font-mono" style={{ fontSize: '0.65rem', color: 'var(--text-dim)' }}>{r.index + 1}</td>
                      <td style={{ maxWidth: 350, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.text}</td>
                      <td>{r.error ? <span className="tag tag-warning">ERROR</span> : <span className={`tag tag-${r.sentiment}`}>{r.sentiment}</span>}</td>
                      <td className="font-mono" style={{ fontSize: '0.72rem' }}>{r.confidence ? `${(r.confidence * 100).toFixed(1)}%` : '—'}</td>
                      <td className="font-mono" style={{ fontSize: '0.72rem', color: (r.sentiment_score || 0) >= 0 ? 'var(--positive)' : 'var(--danger)' }}>
                        {r.sentiment_score != null ? `${r.sentiment_score >= 0 ? '+' : ''}${r.sentiment_score.toFixed(2)}` : '—'}
                      </td>
                      <td className="font-mono" style={{ fontSize: '0.72rem' }}>{r.market_impact || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
