import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Cpu, BarChart3, Activity } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { getModelMetrics, getModelComparison } from '../services/api';

const chartStyle = { background: '#111512', border: '1px solid rgba(0,255,136,0.2)', borderRadius: 4, fontFamily: 'JetBrains Mono', fontSize: '0.7rem' };

export default function ModelLab() {
  const [metrics, setMetrics] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getModelMetrics(), getModelComparison()])
      .then(([m, c]) => { setMetrics(m); setComparison(c); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const training = metrics?.training;
  const evaluation = metrics?.evaluation;

  // Training history charts
  const lossData = training?.history?.train_loss?.map((tl, i) => ({
    epoch: i + 1,
    train_loss: tl,
    val_loss: training.history.val_loss[i],
  })) || [];

  const accData = training?.history?.train_acc?.map((ta, i) => ({
    epoch: i + 1,
    train_acc: (ta * 100).toFixed(1),
    val_acc: (training.history.val_acc[i] * 100).toFixed(1),
  })) || [];

  const cm = evaluation?.confusion_matrix;
  const cmLabels = evaluation?.confusion_matrix_labels || ['negative', 'neutral', 'positive'];

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <div className="label-accent" style={{ marginBottom: 4 }}>MODEL LAB / 05</div>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', fontWeight: 600 }}>Model Training & Performance</h1>
      </div>

      {loading ? (
        <div className="panel"><div className="panel-body terminal-loader"><div className="step">LOADING MODEL METRICS...</div></div></div>
      ) : (
        <>
          {/* Model Metadata */}
          {training && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 12, marginBottom: 24 }}>
              {[
                ['MODEL', 'FinSight Transformer v1'],
                ['ARCHITECTURE', 'Custom Transformer Encoder'],
                ['PARAMETERS', training.total_parameters?.toLocaleString()],
                ['MAX TOKENS', training.hyperparameters?.max_seq_len],
                ['ATTENTION HEADS', training.hyperparameters?.num_heads],
                ['ENCODER LAYERS', training.hyperparameters?.num_layers],
              ].map(([label, value]) => (
                <div key={label} className="metric-card">
                  <div className="metric-label">{label}</div>
                  <div className="font-mono" style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: 4 }}>{value}</div>
                </div>
              ))}
            </div>
          )}

          {/* Training Curves */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
            <div className="panel">
              <div className="panel-header"><span className="panel-title">TRAINING vs VALIDATION LOSS</span></div>
              <div className="panel-body" style={{ height: 280 }}>
                {lossData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={lossData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="epoch" tick={{ fontSize: 10 }} />
                      <YAxis tick={{ fontSize: 10 }} />
                      <Tooltip contentStyle={chartStyle} />
                      <Legend wrapperStyle={{ fontSize: '0.65rem', fontFamily: 'JetBrains Mono' }} />
                      <Line type="monotone" dataKey="train_loss" stroke="#00FF88" name="Train Loss" strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="val_loss" stroke="#FF3B5C" name="Val Loss" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}><span className="label-terminal">NO TRAINING DATA</span></div>}
              </div>
            </div>

            <div className="panel">
              <div className="panel-header"><span className="panel-title">TRAINING vs VALIDATION ACCURACY</span></div>
              <div className="panel-body" style={{ height: 280 }}>
                {accData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={accData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="epoch" tick={{ fontSize: 10 }} />
                      <YAxis tick={{ fontSize: 10 }} />
                      <Tooltip contentStyle={chartStyle} />
                      <Legend wrapperStyle={{ fontSize: '0.65rem', fontFamily: 'JetBrains Mono' }} />
                      <Line type="monotone" dataKey="train_acc" stroke="#00FF88" name="Train Acc %" strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="val_acc" stroke="#4DA3FF" name="Val Acc %" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}><span className="label-terminal">NO TRAINING DATA</span></div>}
              </div>
            </div>
          </div>

          {/* Evaluation Metrics */}
          {evaluation && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
              <div className="panel">
                <div className="panel-header"><span className="panel-title">TEST SET PERFORMANCE</span></div>
                <div className="panel-body">
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                    {[
                      ['ACCURACY', evaluation.overall.accuracy],
                      ['PRECISION', evaluation.overall.precision_macro],
                      ['RECALL', evaluation.overall.recall_macro],
                      ['F1 (MACRO)', evaluation.overall.f1_macro],
                      ['F1 (WEIGHTED)', evaluation.overall.f1_weighted],
                      ['INFERENCE', `${evaluation.inference.avg_ms_per_sample}ms`],
                    ].map(([label, value]) => (
                      <div key={label}>
                        <div className="label-terminal" style={{ marginBottom: 2 }}>{label}</div>
                        <div className="font-mono" style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-primary)' }}>
                          {typeof value === 'number' ? (value * 100).toFixed(1) + '%' : value}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Per-class */}
                  <div style={{ marginTop: 16 }}>
                    <div className="label-terminal" style={{ marginBottom: 8 }}>PER-CLASS PERFORMANCE</div>
                    <table className="table-terminal">
                      <thead><tr><th>CLASS</th><th>PRECISION</th><th>RECALL</th><th>F1</th><th>SUPPORT</th></tr></thead>
                      <tbody>
                        {evaluation.per_class && Object.entries(evaluation.per_class).map(([cls, m]) => (
                          <tr key={cls}>
                            <td><span className={`tag tag-${cls}`}>{cls}</span></td>
                            <td className="font-mono" style={{ fontSize: '0.72rem' }}>{(m.precision * 100).toFixed(1)}%</td>
                            <td className="font-mono" style={{ fontSize: '0.72rem' }}>{(m.recall * 100).toFixed(1)}%</td>
                            <td className="font-mono" style={{ fontSize: '0.72rem' }}>{(m.f1 * 100).toFixed(1)}%</td>
                            <td className="font-mono" style={{ fontSize: '0.72rem' }}>{m.support}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              {/* Confusion Matrix */}
              <div className="panel">
                <div className="panel-header"><span className="panel-title">CONFUSION MATRIX</span></div>
                <div className="panel-body">
                  {cm ? (
                    <div>
                      <div style={{ display: 'grid', gridTemplateColumns: `60px repeat(${cm.length}, 1fr)`, gap: 4 }}>
                        <div />
                        {cmLabels.map(l => (
                          <div key={l} className="label-terminal" style={{ textAlign: 'center', fontSize: '0.55rem' }}>
                            {l.slice(0, 3).toUpperCase()}
                          </div>
                        ))}
                        {cm.map((row, ri) => (
                          <>
                            <div key={`l-${ri}`} className="label-terminal" style={{ display: 'flex', alignItems: 'center', fontSize: '0.55rem' }}>
                              {cmLabels[ri]?.slice(0, 3).toUpperCase()}
                            </div>
                            {row.map((val, ci) => {
                              const maxVal = Math.max(...cm.flat());
                              const intensity = maxVal > 0 ? val / maxVal : 0;
                              const isDiag = ri === ci;
                              return (
                                <div key={`${ri}-${ci}`} className="confusion-cell"
                                  style={{ background: isDiag ? `rgba(0,255,136,${intensity * 0.4})` : `rgba(255,59,92,${intensity * 0.3})` }}>
                                  {val}
                                </div>
                              );
                            })}
                          </>
                        ))}
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'center', gap: 16, marginTop: 12 }}>
                        <span className="font-mono" style={{ fontSize: '0.6rem', color: 'var(--text-dim)' }}>ROWS: ACTUAL</span>
                        <span className="font-mono" style={{ fontSize: '0.6rem', color: 'var(--text-dim)' }}>COLS: PREDICTED</span>
                      </div>
                    </div>
                  ) : <span className="label-terminal">NO EVALUATION DATA</span>}
                </div>
              </div>
            </div>
          )}

          {/* Model Comparison */}
          {comparison?.models?.length > 0 && (
            <div className="panel" style={{ marginBottom: 24 }}>
              <div className="panel-header"><span className="panel-title">MODEL COMPARISON LAB</span></div>
              <div className="panel-body" style={{ overflowX: 'auto' }}>
                <table className="table-terminal">
                  <thead>
                    <tr><th>MODEL</th><th>ACCURACY</th><th>F1 SCORE</th><th>INFERENCE</th><th>PARAMS</th><th>SIZE</th></tr>
                  </thead>
                  <tbody>
                    {comparison.models.map((m, i) => (
                      <tr key={i} style={{ background: m.is_primary ? 'rgba(0,255,136,0.04)' : 'transparent' }}>
                        <td>
                          <span className="font-mono" style={{ fontSize: '0.75rem', fontWeight: 600, color: m.is_primary ? 'var(--accent-primary)' : 'var(--text-secondary)' }}>
                            {m.model_name} {m.is_primary && '★'}
                          </span>
                        </td>
                        <td className="font-mono" style={{ fontSize: '0.72rem' }}>{(m.accuracy * 100).toFixed(1)}%</td>
                        <td className="font-mono" style={{ fontSize: '0.72rem' }}>{(m.f1_score * 100).toFixed(1)}%</td>
                        <td className="font-mono" style={{ fontSize: '0.72rem' }}>{m.avg_inference_ms?.toFixed(1)}ms</td>
                        <td className="font-mono" style={{ fontSize: '0.72rem' }}>{m.parameters?.toLocaleString()}</td>
                        <td className="font-mono" style={{ fontSize: '0.72rem' }}>{m.model_size_mb?.toFixed(1)}MB</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {comparison.models.some(m => m.note) && (
                  <div style={{ marginTop: 8, fontSize: '0.65rem', color: 'var(--text-dim)', fontStyle: 'italic' }}>
                    * FinBERT values are published benchmarks for reference only.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Training Summary */}
          {training && (
            <div className="panel">
              <div className="panel-header"><span className="panel-title">TRAINING SUMMARY</span></div>
              <div className="panel-body" style={{ display: 'flex', gap: 32, flexWrap: 'wrap' }}>
                {[
                  ['EPOCHS TRAINED', training.total_epochs_trained],
                  ['BEST VAL F1', `${(training.best_val_f1 * 100).toFixed(1)}%`],
                  ['BEST VAL ACC', `${(training.best_val_acc * 100).toFixed(1)}%`],
                  ['TRAINING TIME', `${training.total_training_time_seconds?.toFixed(0)}s`],
                  ['TRAIN SAMPLES', training.train_samples],
                  ['VAL SAMPLES', training.val_samples],
                  ['DEVICE', training.device],
                  ['BATCH SIZE', training.hyperparameters?.batch_size],
                  ['LEARNING RATE', training.hyperparameters?.learning_rate],
                ].map(([label, value]) => (
                  <div key={label}>
                    <div className="label-terminal" style={{ fontSize: '0.55rem' }}>{label}</div>
                    <div className="font-mono" style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginTop: 2 }}>{value}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {!training && !evaluation && (
            <div className="panel">
              <div className="panel-body" style={{ textAlign: 'center', padding: 48 }}>
                <Cpu size={40} style={{ color: 'var(--text-dim)', marginBottom: 12 }} />
                <div className="label-terminal" style={{ marginBottom: 8 }}>NO MODEL METRICS AVAILABLE</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Train the model first to see training curves, evaluation results, and model comparisons.</div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
