import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Box, ChevronDown, ChevronRight } from 'lucide-react';
import { getModelArchitecture } from '../services/api';

const ARCHITECTURE_STEPS = [
  { id: 'input', label: 'INPUT TEXT', icon: '📝', color: 'var(--text-secondary)', description: 'Raw financial text input: headlines, articles, or market commentary. The text is first received as a string of characters.' },
  { id: 'cleaning', label: 'TEXT CLEANING', icon: '🧹', color: 'var(--warning)', description: 'Remove URLs, normalize currency symbols, clean special characters, and lowercase the text. Financial-specific preprocessing converts "$" to "dollar", "%" to "percent", etc.' },
  { id: 'tokenization', label: 'TOKENIZATION', icon: '🔤', color: 'var(--info)', description: 'Split clean text into word tokens using a custom word-level tokenizer trained on the Financial PhraseBank corpus. Special tokens [CLS] and [PAD] are added.' },
  { id: 'embedding', label: 'TOKEN EMBEDDINGS', icon: '📊', color: 'var(--accent-primary)', description: 'Each token ID is mapped to a learned dense vector of dimension 128. These embeddings capture semantic relationships between financial words. Vectors are scaled by √d for training stability.' },
  { id: 'positional', label: 'POSITIONAL ENCODING', icon: '📍', color: 'var(--accent-bright)', description: 'Sinusoidal positional encodings are added to embeddings so the model knows word order. Uses sin/cos functions at different frequencies: PE(pos, 2i) = sin(pos / 10000^(2i/d)).' },
  { id: 'attention', label: 'MULTI-HEAD SELF-ATTENTION', icon: '🔗', color: '#FF6B88', description: 'The core innovation: 4 attention heads independently compute Query, Key, Value projections. Scaled dot-product attention lets each word attend to every other word, learning contextual relationships regardless of distance.', details: 'Attention(Q,K,V) = softmax(QK^T / √d_k) · V\n\nEach head has dimension 32 (128/4 heads). Outputs are concatenated and projected back to 128 dimensions.' },
  { id: 'addnorm1', label: 'ADD & LAYER NORM', icon: '➕', color: 'var(--neutral-color)', description: 'Residual connection preserves original token information (x + Attention(x)), and Layer Normalization stabilizes training by normalizing across the embedding dimension.' },
  { id: 'ffn', label: 'FEED-FORWARD NETWORK', icon: '⚡', color: 'var(--warning)', description: 'Two linear transformations with GELU activation: FFN(x) = Linear₂(GELU(Linear₁(x))). Hidden dimension expands from 128 to 256 then compresses back. Applied independently to each position.' },
  { id: 'addnorm2', label: 'ADD & LAYER NORM', icon: '➕', color: 'var(--neutral-color)', description: 'Second residual connection and normalization: x + FFN(x). This pattern is repeated for all 3 encoder layers.' },
  { id: 'encoder', label: 'TRANSFORMER ENCODER × 3', icon: '🔄', color: 'var(--accent-primary)', description: 'The above attention + FFN block is stacked 3 times. Each layer builds progressively more abstract representations. Earlier layers capture local patterns, later layers capture global financial context.' },
  { id: 'cls', label: 'CLS POOLING', icon: '🎯', color: 'var(--info)', description: 'The [CLS] token (first position) aggregates information from the entire sequence through attention. Its final representation is extracted as a fixed-size vector representing the full article context.' },
  { id: 'dropout', label: 'DROPOUT (0.2)', icon: '🎲', color: 'var(--text-muted)', description: 'Randomly zeroes 20% of elements during training to prevent overfitting and improve generalization to unseen financial text.' },
  { id: 'classifier', label: 'CLASSIFICATION HEAD', icon: '🧠', color: 'var(--accent-bright)', description: 'Two-layer MLP: Linear(128→64) + GELU + Dropout + Linear(64→3). Maps the contextual CLS representation to 3 class logits.' },
  { id: 'softmax', label: 'SOFTMAX OUTPUT', icon: '📈', color: 'var(--positive)', description: 'Softmax converts raw logits to probability distribution over 3 classes. Output: [P(negative), P(neutral), P(positive)]. The class with highest probability is the predicted sentiment.' },
];

export default function Architecture() {
  const [selectedStep, setSelectedStep] = useState(null);
  const [archInfo, setArchInfo] = useState(null);

  useEffect(() => {
    getModelArchitecture().then(setArchInfo).catch(() => {});
  }, []);

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <div className="label-accent" style={{ marginBottom: 4 }}>ARCHITECTURE / 06</div>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', fontWeight: 600 }}>Transformer Architecture Visualizer</h1>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        {/* Left: Architecture Flow */}
        <div>
          <div className="panel">
            <div className="panel-header"><span className="panel-title">ARCHITECTURE FLOW</span></div>
            <div className="panel-body">
              {ARCHITECTURE_STEPS.map((step, i) => (
                <motion.div key={step.id} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}>
                  {/* Connector line */}
                  {i > 0 && (
                    <div style={{ display: 'flex', justifyContent: 'center', padding: '2px 0' }}>
                      <div style={{ width: 1, height: 16, background: 'var(--border-color)' }} />
                    </div>
                  )}

                  <div
                    style={{
                      display: 'flex', alignItems: 'center', gap: 12, padding: '10px 14px',
                      background: selectedStep === step.id ? 'rgba(0,255,136,0.06)' : 'transparent',
                      border: `1px solid ${selectedStep === step.id ? 'var(--accent-primary)' : 'var(--border-color)'}`,
                      borderRadius: 'var(--radius-sm)', cursor: 'pointer',
                      transition: 'all 0.2s',
                    }}
                    onClick={() => setSelectedStep(selectedStep === step.id ? null : step.id)}
                  >
                    <span style={{ fontSize: '1.1rem', width: 24, textAlign: 'center' }}>{step.icon}</span>
                    <span className="font-mono" style={{ fontSize: '0.72rem', fontWeight: 600, letterSpacing: '0.08em', color: step.color, flex: 1 }}>
                      {step.label}
                    </span>
                    {selectedStep === step.id ? <ChevronDown size={14} style={{ color: 'var(--accent-primary)' }} /> : <ChevronRight size={14} style={{ color: 'var(--text-dim)' }} />}
                  </div>

                  {/* Expanded details */}
                  <AnimatePresence>
                    {selectedStep === step.id && (
                      <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
                        style={{ overflow: 'hidden', marginLeft: 24, borderLeft: `2px solid ${step.color}`, paddingLeft: 16, marginTop: 4 }}>
                        <div style={{ padding: '8px 0' }}>
                          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: 8 }}>{step.description}</div>
                          {step.details && (
                            <div style={{ background: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)', padding: 10, border: '1px solid var(--border-color)' }}>
                              <pre className="font-mono" style={{ fontSize: '0.65rem', color: 'var(--accent-primary)', whiteSpace: 'pre-wrap' }}>{step.details}</pre>
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Architecture Info */}
        <div>
          {/* Tensor Dimensions */}
          <div className="panel" style={{ marginBottom: 16 }}>
            <div className="panel-header"><span className="panel-title">TENSOR DIMENSIONS</span></div>
            <div className="panel-body">
              {archInfo?.components ? (
                archInfo.components.map((comp, i) => (
                  <div key={i} style={{ marginBottom: 12, paddingBottom: 12, borderBottom: i < archInfo.components.length - 1 ? '1px solid var(--border-color)' : 'none' }}>
                    <div className="font-mono" style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--accent-primary)', marginBottom: 4 }}>{comp.name}</div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 6 }}>{comp.description}</div>
                    <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                      {comp.input_shape && <span className="tag tag-neutral">IN: {comp.input_shape}</span>}
                      {comp.output_shape && <span className="tag tag-positive">OUT: {comp.output_shape}</span>}
                      {comp.parameters > 0 && <span className="tag tag-info">PARAMS: {comp.parameters.toLocaleString()}</span>}
                    </div>
                    {/* Sub-components */}
                    {comp.sub_components?.map((sub, si) => (
                      <div key={si} style={{ marginLeft: 16, marginTop: 8, paddingLeft: 12, borderLeft: '1px solid var(--border-color)' }}>
                        <div className="font-mono" style={{ fontSize: '0.65rem', fontWeight: 600, color: 'var(--text-secondary)' }}>{sub.name}</div>
                        <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', marginTop: 2 }}>{sub.description}</div>
                      </div>
                    ))}
                  </div>
                ))
              ) : (
                <div style={{ textAlign: 'center', padding: 24 }}>
                  <Box size={32} style={{ color: 'var(--text-dim)', marginBottom: 8 }} />
                  <div className="label-terminal">LOAD MODEL FOR ARCHITECTURE DETAILS</div>
                </div>
              )}
            </div>
          </div>

          {/* Model Summary */}
          {archInfo && (
            <div className="panel">
              <div className="panel-header"><span className="panel-title">MODEL SUMMARY</span></div>
              <div className="panel-body">
                {[
                  ['Model Name', archInfo.model_name],
                  ['Vocabulary Size', archInfo.vocab_size?.toLocaleString()],
                  ['Embedding Dim', archInfo.embed_dim],
                  ['Attention Heads', archInfo.num_heads],
                  ['Encoder Layers', archInfo.num_layers],
                  ['FF Dimension', archInfo.ff_dim],
                  ['Max Sequence', archInfo.max_seq_len],
                  ['Output Classes', archInfo.num_classes],
                  ['Total Parameters', archInfo.total_parameters?.toLocaleString()],
                  ['Status', archInfo.status?.toUpperCase()],
                ].map(([label, value]) => (
                  <div key={label} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid rgba(0,255,136,0.06)' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{label}</span>
                    <span className="font-mono" style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-primary)' }}>{value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
