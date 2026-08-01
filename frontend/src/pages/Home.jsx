import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Terminal, Cpu, ArrowRight, Activity, Shield, BarChart3, Zap } from 'lucide-react';

const BOOT_LINES = [
  { text: 'INITIALIZING FINSIGHT ENGINE...', delay: 0 },
  { text: 'TOKENIZER...............READY', delay: 400 },
  { text: 'TRANSFORMER.............READY', delay: 800 },
  { text: 'ATTENTION HEADS.........04', delay: 1100 },
  { text: 'ENCODER LAYERS..........03', delay: 1400 },
  { text: 'FINANCIAL LEXICON.......LOADED', delay: 1700 },
  { text: 'RISK ENGINE.............LOADED', delay: 2000 },
  { text: 'MODEL STATUS............ONLINE', delay: 2300 },
  { text: 'WAITING FOR INTELLIGENCE_', delay: 2700 },
];

const features = [
  { icon: Activity, title: 'SENTIMENT ANALYSIS', desc: 'Custom Transformer-based financial sentiment classification with confidence scoring' },
  { icon: BarChart3, title: 'MARKET IMPACT', desc: 'Predict bullish/bearish market implications from textual financial signals' },
  { icon: Shield, title: 'RISK DETECTION', desc: 'Multi-category risk signal extraction: financial, regulatory, operational, market' },
  { icon: Zap, title: 'EXPLAINABLE AI', desc: 'Attention visualization and model reasoning — understand WHY predictions occur' },
  { icon: Cpu, title: 'MODEL INSPECTOR', desc: 'Training metrics, confusion matrix, architecture visualization, model comparison' },
  { icon: Terminal, title: 'BATCH & COMPARE', desc: 'Analyze multiple headlines simultaneously or compare two articles side-by-side' },
];

export default function Home() {
  const navigate = useNavigate();
  const [visibleLines, setVisibleLines] = useState([]);

  useEffect(() => {
    BOOT_LINES.forEach((line, i) => {
      setTimeout(() => {
        setVisibleLines(prev => [...prev, line.text]);
      }, line.delay);
    });
  }, []);

  return (
    <div style={{ minHeight: 'calc(100vh - 48px)' }}>
      {/* Hero Section */}
      <section className="hero-bg bg-grid" style={{ 
        padding: '80px 0 60px', 
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', display: 'flex', gap: 60, alignItems: 'center', flexWrap: 'wrap' }}>
          {/* Left */}
          <div style={{ flex: 1, minWidth: 320 }}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <div className="label-terminal" style={{ marginBottom: 16, color: 'var(--text-dim)' }}>
                AI FINANCIAL INTELLIGENCE SYSTEM / v1.0
              </div>
              <h1 style={{ 
                fontFamily: 'var(--font-display)',
                fontSize: '3.2rem',
                fontWeight: 700,
                lineHeight: 1.1,
                letterSpacing: '-0.03em',
                marginBottom: 20,
              }}>
                READ BETWEEN<br />
                <span style={{ color: 'var(--accent-primary)' }}>THE MARKET LINES.</span>
              </h1>
              <p style={{ 
                fontFamily: 'var(--font-body)',
                fontSize: '1rem',
                color: 'var(--text-secondary)',
                lineHeight: 1.6,
                maxWidth: 480,
                marginBottom: 32,
              }}>
                Custom Transformer intelligence for financial sentiment, market signals,
                and explainable textual analysis. Built from scratch with self-attention.
              </p>

              <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                <button 
                  className="btn btn-primary" 
                  onClick={() => navigate('/intelligence')}
                  style={{ fontSize: '0.8rem', padding: '12px 28px' }}
                >
                  <Terminal size={14} />
                  LAUNCH TERMINAL
                  <ArrowRight size={14} />
                </button>
                <button 
                  className="btn"
                  onClick={() => navigate('/architecture')}
                  style={{ fontSize: '0.8rem', padding: '12px 28px' }}
                >
                  <Cpu size={14} />
                  EXPLORE MODEL
                </button>
              </div>
            </motion.div>
          </div>

          {/* Right — Terminal Animation */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            style={{ flex: 1, minWidth: 360 }}
          >
            <div className="panel" style={{ maxWidth: 500 }}>
              <div className="panel-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--danger)' }} />
                  <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--warning)' }} />
                  <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--accent-primary)' }} />
                </div>
                <span className="panel-title">finsight_terminal</span>
              </div>
              <div className="panel-body" style={{ 
                fontFamily: 'var(--font-mono)',
                fontSize: '0.72rem',
                lineHeight: 1.9,
                minHeight: 260,
                background: 'var(--bg-primary)',
              }}>
                {visibleLines.map((line, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    style={{ 
                      color: line.includes('READY') || line.includes('LOADED') || line.includes('ONLINE') 
                        ? 'var(--accent-primary)' 
                        : line.includes('04') || line.includes('03')
                        ? 'var(--text-secondary)'
                        : 'var(--text-muted)'
                    }}
                  >
                    <span style={{ color: 'var(--accent-muted)' }}>&gt; </span>
                    {line}
                  </motion.div>
                ))}
                {visibleLines.length === BOOT_LINES.length && (
                  <span className="cursor-blink" style={{ color: 'var(--accent-primary)' }} />
                )}
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section style={{ padding: '60px 0' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <div className="label-accent" style={{ marginBottom: 8 }}>
            CAPABILITIES
          </div>
          <h2 style={{ 
            fontFamily: 'var(--font-display)',
            fontSize: '1.6rem',
            fontWeight: 600,
            marginBottom: 32,
          }}>
            Intelligence Modules
          </h2>

          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', 
            gap: 16 
          }}>
            {features.map((feat, i) => (
              <motion.div
                key={feat.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * i, duration: 0.4 }}
                className="panel"
                style={{ cursor: 'default' }}
              >
                <div className="panel-body" style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
                  <div style={{ 
                    width: 36, height: 36, borderRadius: 'var(--radius-sm)',
                    background: 'rgba(0, 255, 136, 0.08)',
                    border: '1px solid rgba(0, 255, 136, 0.2)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    flexShrink: 0,
                  }}>
                    <feat.icon size={16} style={{ color: 'var(--accent-primary)' }} />
                  </div>
                  <div>
                    <div style={{ 
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.72rem',
                      fontWeight: 600,
                      letterSpacing: '0.08em',
                      marginBottom: 6,
                      color: 'var(--text-primary)',
                    }}>
                      {feat.title}
                    </div>
                    <div style={{ 
                      fontSize: '0.8rem',
                      color: 'var(--text-muted)',
                      lineHeight: 1.5,
                    }}>
                      {feat.desc}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Technical specs footer */}
      <section style={{ 
        padding: '24px 0',
        borderTop: '1px solid var(--border-color)',
      }}>
        <div style={{ 
          maxWidth: 1200, 
          margin: '0 auto', 
          display: 'flex', 
          justifyContent: 'center',
          gap: 40, 
          flexWrap: 'wrap' 
        }}>
          {[
            ['ARCHITECTURE', 'Custom Transformer'],
            ['PARAMETERS', '~500K'],
            ['ATTENTION HEADS', '4'],
            ['ENCODER LAYERS', '3'],
            ['MAX TOKENS', '256'],
            ['DATASET', 'Financial PhraseBank'],
          ].map(([label, value]) => (
            <div key={label} style={{ textAlign: 'center' }}>
              <div className="label-terminal" style={{ marginBottom: 4 }}>{label}</div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
                {value}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
