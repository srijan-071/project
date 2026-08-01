import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, TrendingUp, AlertTriangle, Activity } from 'lucide-react';
import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { getAnalyticsSummary } from '../services/api';

const COLORS = { positive: '#00FF88', neutral: '#A0A7A3', negative: '#FF3B5C' };

export default function MarketPulse() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAnalyticsSummary()
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const sentimentPieData = data?.sentiment_distribution ? [
    { name: 'Positive', value: data.sentiment_distribution.positive, color: COLORS.positive },
    { name: 'Neutral', value: data.sentiment_distribution.neutral, color: COLORS.neutral },
    { name: 'Negative', value: data.sentiment_distribution.negative, color: COLORS.negative },
  ] : [];

  const timelineData = data?.timeline?.map((t, i) => ({
    index: i,
    score: t.score,
    date: t.date?.split('T')[0] || `#${i}`,
  })).reverse() || [];

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <div className="label-accent" style={{ marginBottom: 4 }}>MARKET PULSE / 02</div>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', fontWeight: 600 }}>Market Sentiment Dashboard</h1>
      </div>

      {/* Top Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
        {[
          { label: 'MARKET MOOD', value: `${data?.market_mood || 50}%`, sub: data?.market_mood >= 60 ? 'BULLISH' : data?.market_mood <= 40 ? 'BEARISH' : 'NEUTRAL', color: data?.market_mood >= 60 ? 'var(--positive)' : data?.market_mood <= 40 ? 'var(--danger)' : 'var(--neutral-color)', icon: TrendingUp },
          { label: 'NEWS ANALYZED', value: data?.total_analyzed?.toLocaleString() || '0', sub: 'TOTAL', color: 'var(--info)', icon: BarChart3 },
          { label: 'AVG CONFIDENCE', value: data?.avg_confidence ? `${(data.avg_confidence * 100).toFixed(1)}%` : '—', sub: 'MODEL', color: 'var(--accent-primary)', icon: Activity },
          { label: 'HIGH-RISK', value: data?.high_risk_count || 0, sub: 'ARTICLES', color: 'var(--danger)', icon: AlertTriangle },
        ].map((card, i) => (
          <motion.div key={card.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }} className="metric-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div className="metric-label">{card.label}</div>
                <div className="metric-value" style={{ color: card.color, marginTop: 8 }}>{card.value}</div>
                <div className="font-mono" style={{ fontSize: '0.6rem', color: 'var(--text-dim)', marginTop: 2 }}>{card.sub}</div>
              </div>
              <card.icon size={18} style={{ color: card.color, opacity: 0.5 }} />
            </div>
          </motion.div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        {/* Sentiment Distribution */}
        <div className="panel">
          <div className="panel-header"><span className="panel-title">SENTIMENT DISTRIBUTION</span></div>
          <div className="panel-body" style={{ height: 250 }}>
            {sentimentPieData.some(d => d.value > 0) ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={sentimentPieData} dataKey="value" cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={3} stroke="none">
                    {sentimentPieData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: '#111512', border: '1px solid rgba(0,255,136,0.2)', borderRadius: 4, fontFamily: 'JetBrains Mono', fontSize: '0.7rem' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-dim)' }}>
                <div style={{ textAlign: 'center' }}>
                  <BarChart3 size={32} style={{ marginBottom: 8, opacity: 0.3 }} />
                  <div className="label-terminal">NO DATA YET</div>
                  <div style={{ fontSize: '0.75rem', marginTop: 4 }}>Analyze articles to populate</div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Sentiment Timeline */}
        <div className="panel">
          <div className="panel-header"><span className="panel-title">SENTIMENT TIMELINE</span></div>
          <div className="panel-body" style={{ height: 250 }}>
            {timelineData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={timelineData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="index" tick={{ fontSize: 10 }} />
                  <YAxis domain={[-1, 1]} tick={{ fontSize: 10 }} />
                  <Tooltip contentStyle={{ background: '#111512', border: '1px solid rgba(0,255,136,0.2)', borderRadius: 4, fontFamily: 'JetBrains Mono', fontSize: '0.7rem' }} />
                  <Line type="monotone" dataKey="score" stroke="#00FF88" strokeWidth={2} dot={{ fill: '#00FF88', r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-dim)' }}>
                <div style={{ textAlign: 'center' }}>
                  <Activity size={32} style={{ marginBottom: 8, opacity: 0.3 }} />
                  <div className="label-terminal">NO TIMELINE DATA</div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Market Mood Index */}
        <div className="panel">
          <div className="panel-header"><span className="panel-title">MARKET MOOD INDEX</span></div>
          <div className="panel-body" style={{ textAlign: 'center', padding: 32 }}>
            <div className="font-mono" style={{ fontSize: '3rem', fontWeight: 700, color: (data?.market_mood || 50) >= 60 ? 'var(--positive)' : (data?.market_mood || 50) <= 40 ? 'var(--danger)' : 'var(--neutral-color)' }}>
              {data?.market_mood || 50}
            </div>
            <div className="gauge-track" style={{ margin: '16px auto', maxWidth: 300 }}>
              <div className="gauge-marker" style={{ left: `${data?.market_mood || 50}%` }} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', maxWidth: 300, margin: '0 auto' }}>
              <span className="font-mono" style={{ fontSize: '0.6rem', color: 'var(--danger)' }}>EXTREME BEARISH</span>
              <span className="font-mono" style={{ fontSize: '0.6rem', color: 'var(--neutral-color)' }}>NEUTRAL</span>
              <span className="font-mono" style={{ fontSize: '0.6rem', color: 'var(--positive)' }}>EXTREME BULLISH</span>
            </div>
          </div>
        </div>

        {/* Recent Analyses */}
        <div className="panel">
          <div className="panel-header"><span className="panel-title">RECENT ANALYSES</span></div>
          <div className="panel-body">
            {data?.recent && data.recent.length > 0 ? (
              <table className="table-terminal">
                <thead><tr><th>TEXT</th><th>SENTIMENT</th><th>CONFIDENCE</th></tr></thead>
                <tbody>
                  {data.recent.map(item => (
                    <tr key={item.id}>
                      <td style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{item.text}</td>
                      <td><span className={`tag tag-${item.sentiment}`}>{item.sentiment}</span></td>
                      <td className="font-mono" style={{ fontSize: '0.7rem' }}>{(item.confidence * 100).toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div style={{ textAlign: 'center', padding: 32, color: 'var(--text-dim)' }}>
                <div className="label-terminal">NO RECENT ANALYSES</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
