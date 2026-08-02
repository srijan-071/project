import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Clock, Search, Trash2, Filter } from 'lucide-react';
import { getHistory, deleteHistoryItem } from '../services/api';

export default function History() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sentimentFilter, setSentimentFilter] = useState('');
  const [page, setPage] = useState(0);
  const LIMIT = 20;

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const params = { limit: LIMIT, offset: page * LIMIT };
      if (sentimentFilter) params.sentiment = sentimentFilter;
      if (search) params.search = search;
      const result = await getHistory(params);
      setData(result);
    } catch { setData(null); }
    setLoading(false);
  };

  useEffect(() => { fetchHistory(); }, [page, sentimentFilter]);

  const handleSearch = () => { setPage(0); fetchHistory(); };
  const handleDelete = async (id) => {
    await deleteHistoryItem(id);
    fetchHistory();
  };

  const totalPages = data ? Math.ceil(data.total / LIMIT) : 0;

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <div className="label-accent" style={{ marginBottom: 4 }}>HISTORY / 07</div>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', fontWeight: 600 }}>Analysis History</h1>
      </div>

      {/* Filters */}
      <div className="panel" style={{ marginBottom: 16 }}>
        <div className="panel-body" style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: 200, display: 'flex', gap: 8 }}>
            <input className="input-terminal" placeholder="Search articles..." value={search} onChange={e => setSearch(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSearch()} style={{ padding: '8px 12px', fontSize: '0.8rem' }} />
            <button className="btn btn-sm" onClick={handleSearch}><Search size={12} /></button>
          </div>
          <div style={{ display: 'flex', gap: 6 }}>
            {['', 'positive', 'neutral', 'negative'].map(f => (
              <button key={f} className={`btn btn-sm ${sentimentFilter === f ? 'btn-primary' : ''}`}
                onClick={() => { setSentimentFilter(f); setPage(0); }}>
                {f ? f.toUpperCase() : 'ALL'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="panel">
        <div className="panel-header">
          <span className="panel-title">ANALYZED ARTICLES ({data?.total || 0})</span>
        </div>
        <div className="panel-body" style={{ overflowX: 'auto' }}>
          {loading ? (
            <div className="terminal-loader"><div className="step">LOADING HISTORY...</div></div>
          ) : data?.items?.length > 0 ? (
            <>
              <table className="table-terminal">
                <thead>
                  <tr><th>TIME</th><th>TEXT</th><th>SENTIMENT</th><th>CONFIDENCE</th><th>SCORE</th><th>MARKET</th><th></th></tr>
                </thead>
                <tbody>
                  {data.items.map(item => (
                    <tr key={item.id}>
                      <td className="font-mono" style={{ fontSize: '0.65rem', color: 'var(--text-dim)', whiteSpace: 'nowrap' }}>
                        {item.created_at ? new Date(item.created_at).toLocaleString() : '—'}
                      </td>
                      <td style={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{item.text}</td>
                      <td><span className={`tag tag-${item.sentiment}`}>{item.sentiment}</span></td>
                      <td className="font-mono" style={{ fontSize: '0.72rem' }}>{(item.confidence * 100).toFixed(1)}%</td>
                      <td className="font-mono" style={{ fontSize: '0.72rem', color: item.sentiment_score >= 0 ? 'var(--positive)' : 'var(--danger)' }}>
                        {item.sentiment_score >= 0 ? '+' : ''}{item.sentiment_score?.toFixed(2)}
                      </td>
                      <td className="font-mono" style={{ fontSize: '0.72rem' }}>{item.market_impact}</td>
                      <td>
                        <button className="btn btn-sm btn-ghost" onClick={() => handleDelete(item.id)} style={{ padding: '4px 6px' }}>
                          <Trash2 size={12} style={{ color: 'var(--danger)' }} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* Pagination */}
              {totalPages > 1 && (
                <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginTop: 16 }}>
                  <button className="btn btn-sm" disabled={page === 0} onClick={() => setPage(p => p - 1)}>PREV</button>
                  <span className="font-mono" style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center' }}>
                    {page + 1} / {totalPages}
                  </span>
                  <button className="btn btn-sm" disabled={page >= totalPages - 1} onClick={() => setPage(p => p + 1)}>NEXT</button>
                </div>
              )}
            </>
          ) : (
            <div style={{ textAlign: 'center', padding: 48 }}>
              <Clock size={32} style={{ color: 'var(--text-dim)', marginBottom: 12 }} />
              <div className="label-terminal" style={{ marginBottom: 8 }}>NO HISTORY YET</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Analyzed articles will appear here automatically.</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
