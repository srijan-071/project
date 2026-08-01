import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Trash2, Upload, Clipboard, BookOpen, AlertTriangle } from 'lucide-react';
import { analyzeText, whatIfAnalysis } from '../services/api';

// ─── Subcomponents (inline for cohesion) ─────────────────

function SentimentBadge({ sentiment, confidence }) {
  const cls = `sentiment-badge sentiment-badge-${sentiment}`;
  return (
    <div className={cls}>
      <span>{sentiment?.toUpperCase()}</span>
      <span style={{ fontSize: '0.75rem', fontWeight: 400 }}>{(confidence * 100).toFixed(1)}%</span>
    </div>
  );
}

function ProbabilityBars({ probabilities }) {
  const items = [
    { label: 'Positive', value: probabilities?.positive || 0, cls: 'positive' },
    { label: 'Neutral', value: probabilities?.neutral || 0, cls: 'neutral' },
    { label: 'Negative', value: probabilities?.negative || 0, cls: 'negative' },
  ];
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {items.map(item => (
        <div key={item.label}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
            <span className="label-terminal">{item.label}</span>
            <span className="font-mono" style={{ fontSize: '0.7rem', color: `var(--${item.cls === 'neutral' ? 'neutral-color' : item.cls})` }}>
              {(item.value * 100).toFixed(1)}%
            </span>
          </div>
          <div className="progress-bar">
            <div className={`progress-fill progress-fill-${item.cls === 'neutral' ? 'neutral' : item.cls === 'positive' ? 'positive' : 'negative'}`} 
                 style={{ width: `${item.value * 100}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

function MarketImpactGauge({ marketImpact }) {
  if (!marketImpact) return null;
  const score = marketImpact.impact_score || 50;
  return (
    <div className="panel" style={{ marginBottom: 16 }}>
      <div className="panel-header"><span className="panel-title">EXPECTED MARKET IMPACT</span></div>
      <div className="panel-body">
        <div className={`sentiment-badge sentiment-badge-${score >= 60 ? 'positive' : score <= 40 ? 'negative' : 'neutral'}`}
             style={{ marginBottom: 12 }}>
          {marketImpact.market_impact?.toUpperCase()}
        </div>
        <div className="label-terminal" style={{ marginBottom: 6 }}>MARKET IMPACT SCORE</div>
        <div className="gauge-track" style={{ marginBottom: 4 }}>
          <div className="gauge-marker" style={{ left: `${score}%` }} />
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span className="font-mono" style={{ fontSize: '0.6rem', color: 'var(--danger)' }}>BEARISH</span>
          <span className="font-mono" style={{ fontSize: '0.6rem', color: 'var(--neutral-color)' }}>NEUTRAL</span>
          <span className="font-mono" style={{ fontSize: '0.6rem', color: 'var(--positive)' }}>BULLISH</span>
        </div>
        <div className="font-mono" style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: 8, textAlign: 'center' }}>
          {score >= 50 ? '+' : ''}{score} / 100
        </div>
        {/* Horizon */}
        {marketImpact.horizon && (
          <div style={{ marginTop: 16 }}>
            <div className="label-terminal" style={{ marginBottom: 8 }}>ESTIMATED IMPACT HORIZON</div>
            {Object.entries(marketImpact.horizon).map(([key, val]) => (
              <div key={key} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'capitalize' }}>{key.replace('_', ' ')}</span>
                <span className="font-mono" style={{ fontSize: '0.7rem', color: val.impact?.includes('Bullish') ? 'var(--positive)' : val.impact?.includes('Bearish') ? 'var(--danger)' : 'var(--neutral-color)' }}>
                  {val.impact} ({(val.confidence*100).toFixed(0)}%)
                </span>
              </div>
            ))}
          </div>
        )}
        <div style={{ marginTop: 12, fontSize: '0.65rem', color: 'var(--text-dim)', fontStyle: 'italic' }}>
          {marketImpact.disclaimer}
        </div>
      </div>
    </div>
  );
}

function RiskPanel({ risk }) {
  if (!risk) return null;
  const categories = [
    { key: 'financial_risk', label: 'FINANCIAL' },
    { key: 'regulatory_risk', label: 'REGULATORY' },
    { key: 'operational_risk', label: 'OPERATIONAL' },
    { key: 'market_risk', label: 'MARKET' },
  ];
  const levelColor = (level) => level === 'HIGH' ? 'var(--danger)' : level === 'MEDIUM' ? 'var(--warning)' : 'var(--positive)';
  return (
    <div className="panel" style={{ marginBottom: 16 }}>
      <div className="panel-header"><span className="panel-title">RISK SIGNALS</span></div>
      <div className="panel-body">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
          {categories.map(cat => {
            const data = risk[cat.key];
            if (!data) return null;
            return (
              <div key={cat.key} style={{ background: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)', padding: 10, border: '1px solid var(--border-color)' }}>
                <div className="label-terminal" style={{ marginBottom: 4, fontSize: '0.6rem' }}>{cat.label}</div>
                <div className="font-mono" style={{ fontSize: '0.85rem', fontWeight: 700, color: levelColor(data.level) }}>
                  {data.level}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function SentimentDNA({ dna }) {
  if (!dna) return null;
  const items = [
    { label: 'Optimism', value: dna.optimism },
    { label: 'Risk', value: dna.risk },
    { label: 'Uncertainty', value: dna.uncertainty },
    { label: 'Growth', value: dna.growth },
    { label: 'Profitability', value: dna.profitability },
    { label: 'Volatility', value: dna.volatility },
  ];
  return (
    <div className="panel" style={{ marginBottom: 16 }}>
      <div className="panel-header"><span className="panel-title">SENTIMENT DNA</span></div>
      <div className="panel-body">
        {items.map(item => (
          <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
            <span style={{ width: 85, fontSize: '0.72rem', color: 'var(--text-muted)' }}>{item.label}</span>
            <div className="dna-bar-track"><div className="dna-bar-fill" style={{ width: `${item.value}%` }} /></div>
            <span className="font-mono" style={{ width: 30, fontSize: '0.72rem', color: 'var(--text-secondary)', textAlign: 'right' }}>{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function HighlightedText({ highlights }) {
  if (!highlights || highlights.length === 0) return null;
  return (
    <div style={{ lineHeight: 1.8, fontSize: '0.9rem' }}>
      {highlights.map((h, i) => {
        const cls = h.type === 'positive' ? 'highlight-positive' : h.type === 'negative' ? 'highlight-negative' : h.type === 'important' ? 'highlight-important' : '';
        return <span key={i}><span className={cls}>{h.word}</span> </span>;
      })}
    </div>
  );
}

function BullBearPanel({ evidence }) {
  if (!evidence) return null;
  return (
    <div className="panel" style={{ marginBottom: 16 }}>
      <div className="panel-header"><span className="panel-title">BULL vs BEAR EVIDENCE</span></div>
      <div className="panel-body">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          <div>
            <div className="label-terminal" style={{ color: 'var(--positive)', marginBottom: 8 }}>BULLISH SIGNALS</div>
            {evidence.bullish?.map((s, i) => (
              <div key={i} style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: 4 }}>
                <span style={{ color: 'var(--positive)' }}>↑</span> {s}
              </div>
            ))}
            {(!evidence.bullish || evidence.bullish.length === 0) && <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>No bullish signals</span>}
          </div>
          <div>
            <div className="label-terminal" style={{ color: 'var(--danger)', marginBottom: 8 }}>BEARISH SIGNALS</div>
            {evidence.bearish?.map((s, i) => (
              <div key={i} style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: 4 }}>
                <span style={{ color: 'var(--danger)' }}>↓</span> {s}
              </div>
            ))}
            {(!evidence.bearish || evidence.bearish.length === 0) && <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>No bearish signals</span>}
          </div>
        </div>
        <div style={{ marginTop: 12, display: 'flex', gap: 4, alignItems: 'center' }}>
          <div className="progress-bar" style={{ flex: 1 }}>
            <div className="progress-fill progress-fill-positive" style={{ width: `${evidence.bullish_percentage || 50}%` }} />
          </div>
          <span className="font-mono" style={{ fontSize: '0.65rem', color: 'var(--positive)', width: 35, textAlign: 'right' }}>{evidence.bullish_percentage}%</span>
        </div>
      </div>
    </div>
  );
}

function EntityCards({ entities }) {
  if (!entities?.entities || entities.entities.length === 0) return null;
  const typeColor = { 'Company': 'var(--accent-primary)', 'Person': 'var(--info)', 'Sector': 'var(--warning)', 'Currency': 'var(--accent-bright)', 'Country': 'var(--text-secondary)', 'Financial Metric': 'var(--info)', 'Economic Event': 'var(--warning)' };
  return (
    <div className="panel" style={{ marginBottom: 16 }}>
      <div className="panel-header"><span className="panel-title">FINANCIAL ENTITIES ({entities.count})</span></div>
      <div className="panel-body" style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
        {entities.entities.map((e, i) => (
          <div key={i} className="tag" style={{ borderColor: typeColor[e.type] || 'var(--border-color)', color: typeColor[e.type] || 'var(--text-secondary)' }}>
            <span style={{ fontSize: '0.55rem', opacity: 0.7 }}>{e.type?.toUpperCase()}</span>
            <span>{e.entity}</span>
            {e.sentiment && <span style={{ opacity: 0.7 }}>• {e.sentiment}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}

function SentenceTimeline({ sentences }) {
  if (!sentences || sentences.length === 0) return null;
  return (
    <div className="panel" style={{ marginBottom: 16 }}>
      <div className="panel-header"><span className="panel-title">SENTENCE-LEVEL ANALYSIS</span></div>
      <div className="panel-body">
        {sentences.map((s, i) => (
          <div key={i} style={{ display: 'flex', gap: 12, marginBottom: 10, alignItems: 'flex-start' }}>
            <div style={{ minWidth: 24, textAlign: 'center' }}>
              <span className="font-mono" style={{ fontSize: '0.6rem', color: 'var(--text-dim)' }}>S{i+1}</span>
            </div>
            <div style={{ width: 4, borderRadius: 2, background: s.sentiment === 'positive' ? 'var(--positive)' : s.sentiment === 'negative' ? 'var(--danger)' : 'var(--neutral-color)', minHeight: 30, flexShrink: 0 }} />
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: 3 }}>{s.sentence}</div>
              <div style={{ display: 'flex', gap: 8 }}>
                <span className={`tag tag-${s.sentiment}`}>{s.sentiment}</span>
                <span className="font-mono" style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{(s.confidence*100).toFixed(1)}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function AttentionHeatmap({ attentionWeights, tokens }) {
  if (!attentionWeights || attentionWeights.length === 0 || !tokens) return null;
  const [selectedLayer, setSelectedLayer] = useState(0);
  const [selectedHead, setSelectedHead] = useState(0);
  const [hoveredCell, setHoveredCell] = useState(null);

  const layerData = attentionWeights[selectedLayer];
  if (!layerData?.weights) return null;
  const headWeights = layerData.weights[selectedHead];
  if (!headWeights) return null;

  const displayTokens = tokens.slice(0, Math.min(tokens.length, 25));
  const size = displayTokens.length;
  const cellSize = Math.max(16, Math.min(28, 500 / size));

  return (
    <div className="panel" style={{ marginBottom: 16 }}>
      <div className="panel-header">
        <span className="panel-title">TRANSFORMER ATTENTION MAP</span>
        <div style={{ display: 'flex', gap: 8 }}>
          {attentionWeights.map((_, i) => (
            <button key={i} className={`btn btn-sm ${selectedLayer === i ? 'btn-primary' : ''}`} onClick={() => setSelectedLayer(i)}>L{i+1}</button>
          ))}
          <div style={{ width: 1, height: 20, background: 'var(--border-color)' }} />
          {[0,1,2,3].map(h => (
            <button key={h} className={`btn btn-sm ${selectedHead === h ? 'btn-primary' : ''}`} onClick={() => setSelectedHead(h)}>H{h+1}</button>
          ))}
        </div>
      </div>
      <div className="panel-body" style={{ overflowX: 'auto' }}>
        <div style={{ display: 'inline-block', position: 'relative' }}>
          {/* Column labels */}
          <div style={{ display: 'flex', marginLeft: cellSize * 3.5 }}>
            {displayTokens.map((t, i) => (
              <div key={i} style={{ width: cellSize, textAlign: 'center', transform: 'rotate(-45deg)', transformOrigin: 'bottom left', fontFamily: 'var(--font-mono)', fontSize: '0.55rem', color: 'var(--text-muted)', height: cellSize * 2, display: 'flex', alignItems: 'flex-end', justifyContent: 'center' }}>
                {t.length > 6 ? t.slice(0, 5) + '…' : t}
              </div>
            ))}
          </div>
          {/* Rows */}
          {displayTokens.map((rowToken, ri) => (
            <div key={ri} style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ width: cellSize * 3.5, fontFamily: 'var(--font-mono)', fontSize: '0.55rem', color: 'var(--text-muted)', textAlign: 'right', paddingRight: 6, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {rowToken}
              </div>
              {displayTokens.map((_, ci) => {
                const weight = headWeights[ri]?.[ci] ?? 0;
                const opacity = Math.max(0.05, weight);
                return (
                  <div key={ci} className="heatmap-cell"
                    style={{ width: cellSize, height: cellSize, background: `rgba(0, 255, 136, ${opacity})`, border: hoveredCell?.r === ri && hoveredCell?.c === ci ? '1px solid var(--accent-bright)' : '1px solid transparent' }}
                    onMouseEnter={() => setHoveredCell({ r: ri, c: ci, w: weight })}
                    onMouseLeave={() => setHoveredCell(null)} />
                );
              })}
            </div>
          ))}
        </div>
        {hoveredCell && (
          <div className="font-mono" style={{ marginTop: 8, fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
            {displayTokens[hoveredCell.r]} → {displayTokens[hoveredCell.c]} | Attention Weight: <span style={{ color: 'var(--accent-primary)' }}>{hoveredCell.w.toFixed(4)}</span>
          </div>
        )}
      </div>
    </div>
  );
}

function NewsImpactMeter({ newsImpact }) {
  if (!newsImpact) return null;
  const levelColor = { 'LOW': 'var(--text-muted)', 'MEDIUM': 'var(--warning)', 'HIGH': 'var(--accent-primary)', 'CRITICAL': 'var(--danger)' };
  return (
    <div className="panel" style={{ marginBottom: 16 }}>
      <div className="panel-header"><span className="panel-title">NEWS IMPACT</span></div>
      <div className="panel-body" style={{ textAlign: 'center' }}>
        <div className="font-mono" style={{ fontSize: '2rem', fontWeight: 700, color: levelColor[newsImpact.impact_level] || 'var(--text-primary)' }}>
          {newsImpact.impact_score} <span style={{ fontSize: '0.9rem', fontWeight: 400 }}>/ 100</span>
        </div>
        <div className="font-mono" style={{ fontSize: '0.8rem', fontWeight: 600, color: levelColor[newsImpact.impact_level], marginTop: 4 }}>
          {newsImpact.impact_level} IMPACT
        </div>
        <div className="gauge-track" style={{ marginTop: 12 }}>
          <div className="gauge-marker" style={{ left: `${newsImpact.impact_score}%` }} />
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 4 }}>
          <span className="font-mono" style={{ fontSize: '0.55rem', color: 'var(--text-dim)' }}>LOW</span>
          <span className="font-mono" style={{ fontSize: '0.55rem', color: 'var(--text-dim)' }}>MEDIUM</span>
          <span className="font-mono" style={{ fontSize: '0.55rem', color: 'var(--text-dim)' }}>HIGH</span>
          <span className="font-mono" style={{ fontSize: '0.55rem', color: 'var(--text-dim)' }}>CRITICAL</span>
        </div>
      </div>
    </div>
  );
}

function KeywordTags({ keywords }) {
  if (!keywords || keywords.length === 0) return null;
  return (
    <div className="panel" style={{ marginBottom: 16 }}>
      <div className="panel-header"><span className="panel-title">TOP FINANCIAL SIGNALS</span></div>
      <div className="panel-body" style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
        {keywords.map((k, i) => (
          <span key={i} className="tag tag-info">{k.keyword}</span>
        ))}
      </div>
    </div>
  );
}

function EventDetection({ events }) {
  if (!events || events.length === 0) return null;
  const impColor = { 'HIGH': 'var(--danger)', 'MEDIUM': 'var(--warning)', 'LOW': 'var(--text-muted)' };
  return (
    <div className="panel" style={{ marginBottom: 16 }}>
      <div className="panel-header"><span className="panel-title">EVENTS DETECTED</span></div>
      <div className="panel-body" style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
        {events.map((e, i) => (
          <div key={i} style={{ background: 'var(--bg-primary)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', padding: '8px 12px' }}>
            <div className="font-mono" style={{ fontSize: '0.75rem', fontWeight: 600, marginBottom: 2 }}>{e.event?.toUpperCase()}</div>
            <span className="font-mono" style={{ fontSize: '0.6rem', color: impColor[e.importance] }}>{e.importance}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function WhatIfPanel({ originalText, result }) {
  const [modifiedText, setModifiedText] = useState(originalText);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);

  const runWhatIf = async () => {
    if (!modifiedText.trim() || modifiedText === originalText) return;
    setLoading(true);
    try {
      const data = await whatIfAnalysis(originalText, modifiedText);
      setComparison(data);
    } catch (err) { console.error(err); }
    setLoading(false);
  };

  return (
    <div className="panel" style={{ marginBottom: 16 }}>
      <div className="panel-header"><span className="panel-title">WHAT IF? ANALYSIS</span></div>
      <div className="panel-body">
        <div className="label-terminal" style={{ marginBottom: 6 }}>MODIFY THE TEXT AND COMPARE</div>
        <textarea className="input-terminal" rows={3} value={modifiedText} onChange={e => setModifiedText(e.target.value)} style={{ fontSize: '0.8rem', marginBottom: 8 }} />
        <button className="btn btn-primary btn-sm" onClick={runWhatIf} disabled={loading}>{loading ? 'ANALYZING...' : 'RUN COMPARISON'}</button>
        {comparison && (
          <div style={{ marginTop: 16, display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
            <div style={{ textAlign: 'center' }}>
              <div className="label-terminal" style={{ marginBottom: 4 }}>ORIGINAL</div>
              <div className={`font-mono`} style={{ fontSize: '1.1rem', fontWeight: 700, color: comparison.original.sentiment_score >= 0 ? 'var(--positive)' : 'var(--danger)' }}>
                {comparison.original.sentiment_score >= 0 ? '+' : ''}{comparison.original.sentiment_score.toFixed(2)}
              </div>
              <div className={`tag tag-${comparison.original.sentiment}`} style={{ marginTop: 4 }}>{comparison.original.sentiment}</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div className="label-terminal" style={{ marginBottom: 4 }}>MODIFIED</div>
              <div className="font-mono" style={{ fontSize: '1.1rem', fontWeight: 700, color: comparison.modified.sentiment_score >= 0 ? 'var(--positive)' : 'var(--danger)' }}>
                {comparison.modified.sentiment_score >= 0 ? '+' : ''}{comparison.modified.sentiment_score.toFixed(2)}
              </div>
              <div className={`tag tag-${comparison.modified.sentiment}`} style={{ marginTop: 4 }}>{comparison.modified.sentiment}</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div className="label-terminal" style={{ marginBottom: 4 }}>DELTA</div>
              <div className="font-mono" style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--warning)' }}>
                {comparison.delta.sentiment_score >= 0 ? '+' : ''}{comparison.delta.sentiment_score.toFixed(2)}
              </div>
              {comparison.delta.sentiment_changed && <span className="tag tag-warning" style={{ marginTop: 4 }}>SHIFTED</span>}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


// ─── Sample Data ─────────────────────────────────────────

const SAMPLES = [
  { label: 'POSITIVE', text: 'Apple reported record quarterly revenue of $123.9 billion, driven by strong demand for iPhone 15 Pro and Services growth. Operating margins improved to 33.4% while the company raised its annual guidance for the second consecutive quarter.' },
  { label: 'NEGATIVE', text: 'Shares of the company declined 8% after it reported weaker-than-expected revenue and reduced its annual guidance citing macroeconomic headwinds. Operating expenses increased 15% while customer acquisition costs rose significantly.' },
  { label: 'NEUTRAL', text: 'The company announced that its annual shareholder meeting will take place next month. The board of directors will present the fiscal year review and discuss upcoming strategic initiatives for the next quarter.' },
  { label: 'MIXED', text: 'Revenue exceeded analyst expectations by 12%, reaching $45.2 billion for the quarter. However, operating profit declined 8% due to rising costs in supply chain and increased investment in AI infrastructure.' },
];

const LOADING_STEPS = [
  'ANALYZING TEXT',
  'TOKENIZING...',
  'BUILDING ATTENTION MATRIX...',
  'EXTRACTING CONTEXT...',
  'CLASSIFYING SENTIMENT...',
  'CALCULATING MARKET IMPACT...',
  'EXTRACTING ENTITIES...',
  'DETECTING RISK SIGNALS...',
  'ANALYSIS COMPLETE ✓',
];


// ─── Main Component ─────────────────────────────────────

export default function Intelligence() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState(null);
  const textareaRef = useRef(null);

  const tokenCount = text.trim() ? text.trim().split(/\s+/).length : 0;

  const handleAnalyze = async () => {
    if (!text.trim() || text.trim().length < 5) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setLoadingStep(0);

    // Animate loading steps
    const stepInterval = setInterval(() => {
      setLoadingStep(prev => {
        if (prev >= LOADING_STEPS.length - 1) { clearInterval(stepInterval); return prev; }
        return prev + 1;
      });
    }, 300);

    try {
      const data = await analyzeText(text);
      clearInterval(stepInterval);
      setLoadingStep(LOADING_STEPS.length - 1);
      setTimeout(() => {
        setResult(data);
        setLoading(false);
      }, 400);
    } catch (err) {
      clearInterval(stepInterval);
      setLoading(false);
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'object' ? detail : { code: 'ERR_NETWORK', message: detail || 'Failed to connect to server. Is the backend running?' });
    }
  };

  const handlePaste = async () => {
    try {
      const clip = await navigator.clipboard.readText();
      setText(clip);
    } catch { /* ignore */ }
  };

  return (
    <div>
      {/* Page Title */}
      <div style={{ marginBottom: 24 }}>
        <div className="label-accent" style={{ marginBottom: 4 }}>FINANCIAL INTELLIGENCE / 01</div>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', fontWeight: 600 }}>
          Intelligence Terminal
        </h1>
      </div>

      {/* Input Section */}
      <div className="panel" style={{ marginBottom: 24 }}>
        <div className="panel-header">
          <span className="panel-title">INPUT ANALYSIS</span>
          <div style={{ display: 'flex', gap: 6 }}>
            {SAMPLES.map(sample => (
              <button key={sample.label} className="btn btn-sm btn-ghost" onClick={() => setText(sample.text)}>
                <BookOpen size={10} /> {sample.label}
              </button>
            ))}
          </div>
        </div>
        <div className="panel-body">
          <textarea
            ref={textareaRef}
            className="input-terminal"
            rows={6}
            value={text}
            onChange={e => setText(e.target.value)}
            placeholder="Paste financial news or market commentary..."
            style={{ marginBottom: 12 }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="btn btn-primary" onClick={handleAnalyze} disabled={loading || !text.trim()}>
                <Send size={12} /> {loading ? 'ANALYZING...' : 'ANALYZE INTELLIGENCE'}
              </button>
              <button className="btn btn-sm" onClick={() => { setText(''); setResult(null); setError(null); }}>
                <Trash2 size={12} /> CLEAR
              </button>
              <button className="btn btn-sm" onClick={handlePaste}><Clipboard size={12} /> PASTE</button>
            </div>
            <span className="font-mono" style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
              TOKENS: <span style={{ color: tokenCount > 256 ? 'var(--danger)' : 'var(--accent-primary)' }}>{tokenCount}</span> / 256
            </span>
          </div>
        </div>
      </div>

      {/* Loading Animation */}
      <AnimatePresence>
        {loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="panel" style={{ marginBottom: 24 }}>
            <div className="panel-body terminal-loader">
              {LOADING_STEPS.slice(0, loadingStep + 1).map((step, i) => (
                <div key={i} className={`step ${i < loadingStep ? 'complete' : ''}`} style={{ animationDelay: `${i * 0.1}s` }}>{step}</div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error */}
      {error && (
        <div className="panel" style={{ marginBottom: 24, borderColor: 'rgba(255, 59, 92, 0.3)' }}>
          <div className="panel-body" style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
            <AlertTriangle size={18} style={{ color: 'var(--danger)', flexShrink: 0, marginTop: 2 }} />
            <div>
              <div className="font-mono" style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--danger)', marginBottom: 4 }}>
                ANALYSIS INTERRUPTED — {error.code}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{error.message}</div>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      <AnimatePresence>
        {result && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
            {/* Model Inspector Bar */}
            <div className="panel" style={{ marginBottom: 16, borderColor: 'rgba(0,255,136,0.2)' }}>
              <div className="panel-body" style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
                {[
                  ['INFERENCE', `${result.latency_ms}ms`],
                  ['TOKENS', result.num_tokens],
                  ['PREDICTION', result.sentiment?.toUpperCase()],
                  ['CONFIDENCE', `${(result.confidence*100).toFixed(1)}%`],
                  ['UNCERTAINTY', result.uncertainty?.level],
                ].map(([label, value]) => (
                  <div key={label}>
                    <div className="label-terminal" style={{ fontSize: '0.55rem' }}>{label}</div>
                    <div className="font-mono" style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--accent-primary)' }}>{value}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Main Grid: Left 7col + Right 5col */}
            <div style={{ display: 'grid', gridTemplateColumns: '7fr 5fr', gap: 16 }}>
              {/* LEFT COLUMN */}
              <div>
                {/* Highlighted Article */}
                <div className="panel" style={{ marginBottom: 16 }}>
                  <div className="panel-header"><span className="panel-title">ANALYZED ARTICLE</span></div>
                  <div className="panel-body">
                    <HighlightedText highlights={result.highlights} />
                  </div>
                </div>

                {/* Explainable AI */}
                <div className="panel" style={{ marginBottom: 16 }}>
                  <div className="panel-header"><span className="panel-title">WHY DID THE MODEL PREDICT THIS?</span></div>
                  <div className="panel-body">
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
                      <div>
                        <div className="label-terminal" style={{ color: 'var(--positive)', marginBottom: 6 }}>TOP POSITIVE SIGNALS</div>
                        {result.positive_signals?.map((s, i) => (
                          <div key={i} className="font-mono" style={{ fontSize: '0.75rem', color: 'var(--positive)', marginBottom: 3 }}>{s.word}</div>
                        ))}
                        {(!result.positive_signals || result.positive_signals.length === 0) && <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>None detected</span>}
                      </div>
                      <div>
                        <div className="label-terminal" style={{ color: 'var(--danger)', marginBottom: 6 }}>TOP NEGATIVE SIGNALS</div>
                        {result.negative_signals?.map((s, i) => (
                          <div key={i} className="font-mono" style={{ fontSize: '0.75rem', color: 'var(--danger)', marginBottom: 3 }}>{s.word}</div>
                        ))}
                        {(!result.negative_signals || result.negative_signals.length === 0) && <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>None detected</span>}
                      </div>
                    </div>
                    <div style={{ background: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)', padding: 12, border: '1px solid var(--border-color)' }}>
                      <div className="label-terminal" style={{ marginBottom: 6 }}>MODEL REASONING</div>
                      <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.6, fontStyle: 'italic' }}>{result.reasoning}</div>
                    </div>
                  </div>
                </div>

                {/* Entity Cards */}
                <EntityCards entities={result.entities} />

                {/* Bull vs Bear */}
                <BullBearPanel evidence={result.market_impact?.bull_bear_evidence} />

                {/* Sentence Timeline */}
                <SentenceTimeline sentences={result.sentence_analysis} />

                {/* Attention Map */}
                <AttentionHeatmap attentionWeights={result.attention_weights} tokens={result.tokens} />

                {/* What If */}
                <WhatIfPanel originalText={text} result={result} />
              </div>

              {/* RIGHT COLUMN */}
              <div>
                {/* Sentiment */}
                <div className="panel" style={{ marginBottom: 16 }}>
                  <div className="panel-header"><span className="panel-title">OVERALL SENTIMENT</span></div>
                  <div className="panel-body">
                    <SentimentBadge sentiment={result.sentiment} confidence={result.confidence} />
                    <div style={{ marginTop: 12 }}>
                      <div className="label-terminal" style={{ marginBottom: 4 }}>SENTIMENT SCORE</div>
                      <div className="font-mono" style={{ fontSize: '1.6rem', fontWeight: 700, color: result.sentiment_score >= 0 ? 'var(--positive)' : 'var(--danger)' }}>
                        {result.sentiment_score >= 0 ? '+' : ''}{result.sentiment_score?.toFixed(2)}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>{result.interpretation}</div>
                    </div>
                    <div style={{ marginTop: 16 }}>
                      <ProbabilityBars probabilities={result.probabilities} />
                    </div>
                  </div>
                </div>

                {/* Market Impact */}
                <MarketImpactGauge marketImpact={result.market_impact} />

                {/* News Impact */}
                <NewsImpactMeter newsImpact={result.news_impact} />

                {/* Risk */}
                <RiskPanel risk={result.risk} />

                {/* Sentiment DNA */}
                <SentimentDNA dna={result.sentiment_dna} />

                {/* Keywords */}
                <KeywordTags keywords={result.keywords} />

                {/* Events */}
                <EventDetection events={result.events} />

                {/* Contradiction */}
                {result.contradictions?.detected && (
                  <div className="panel" style={{ marginBottom: 16, borderColor: 'rgba(255, 176, 32, 0.3)' }}>
                    <div className="panel-header"><span className="panel-title" style={{ color: 'var(--warning)' }}>⚠ CONFLICTING SIGNALS</span></div>
                    <div className="panel-body" style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      {result.contradictions.message}
                    </div>
                  </div>
                )}

                {/* Uncertainty */}
                <div className="panel" style={{ marginBottom: 16 }}>
                  <div className="panel-header"><span className="panel-title">MODEL CONFIDENCE</span></div>
                  <div className="panel-body" style={{ textAlign: 'center' }}>
                    <div className="font-mono" style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--accent-primary)' }}>
                      {(result.confidence * 100).toFixed(1)}%
                    </div>
                    <div className="font-mono" style={{ fontSize: '0.75rem', color: result.uncertainty?.level === 'Low' ? 'var(--positive)' : result.uncertainty?.level === 'High' ? 'var(--danger)' : 'var(--warning)' }}>
                      UNCERTAINTY: {result.uncertainty?.level?.toUpperCase()}
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 6 }}>{result.uncertainty?.message}</div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
