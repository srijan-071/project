import { FileText, Terminal, Cpu, BarChart3, Zap, Shield } from 'lucide-react';

const sections = [
  {
    title: 'OVERVIEW',
    icon: FileText,
    content: `FinSight AI is a custom Transformer-based financial sentiment analysis platform. It classifies financial news into Positive, Neutral, or Negative sentiment, predicts market impact, extracts financial entities, detects risk signals, and provides explainable AI through attention visualization.

The core model is a lightweight Transformer Encoder built from scratch using PyTorch, trained on the Financial PhraseBank dataset. Unlike traditional sentiment analyzers that count positive/negative keywords, FinSight AI uses self-attention mechanisms to understand contextual relationships between financial words.`,
  },
  {
    title: 'MODEL ARCHITECTURE',
    icon: Cpu,
    content: `The FinSight Transformer consists of:

• Token Embedding Layer (vocab × 128 dims)
• Sinusoidal Positional Encoding
• 3 Transformer Encoder Blocks, each containing:
  - Multi-Head Self-Attention (4 heads, 32 dim/head)
  - Add & Layer Normalization
  - Feed-Forward Network (128 → 256 → 128 with GELU)
  - Add & Layer Normalization
• CLS Token Pooling
• Classification Head (128 → 64 → 3 with dropout)
• Softmax Output

The model uses ~500K trainable parameters, making it lightweight enough for CPU inference while maintaining genuine Transformer capabilities.`,
  },
  {
    title: 'ANALYSIS PIPELINE',
    icon: Terminal,
    content: `When you submit text for analysis, the following pipeline executes:

1. Text Cleaning — URLs removed, financial symbols normalized, lowercased
2. Tokenization — Custom word-level tokenizer with [CLS] token prepended
3. Model Inference — Forward pass through Transformer encoder
4. Sentiment Classification — Positive/Neutral/Negative with confidence
5. Market Impact Prediction — Bullish/Bearish with impact score and horizon
6. Entity Extraction — Companies, people, sectors, currencies, events
7. Keyword Extraction — Top financial signals weighted by attention
8. Risk Detection — Financial, regulatory, operational, market risk
9. Explainability — Attention weights, token importance, model reasoning
10. Contradiction Detection — Conflicting signals across sentences
11. Sentiment DNA — Multi-dimensional sentiment fingerprint`,
  },
  {
    title: 'API REFERENCE',
    icon: Zap,
    content: `All endpoints accept/return JSON. Base URL: http://localhost:8000

POST /api/analyze
  Body: { "text": "..." }
  Returns: Full analysis with sentiment, market impact, entities, risk, attention

POST /api/analyze/what-if
  Body: { "original_text": "...", "modified_text": "..." }
  Returns: Side-by-side comparison with deltas

POST /api/analyze/playground
  Body: { "text": "..." }
  Returns: Quick analysis with attention weights

POST /api/batch-analyze
  Body: { "texts": ["...", "..."] }
  Returns: Batch results with summary stats

POST /api/compare
  Body: { "text_a": "...", "text_b": "..." }
  Returns: Detailed comparison of two articles

GET /api/history?limit=50&offset=0&sentiment=positive&search=apple
GET /api/model/info
GET /api/model/metrics
GET /api/model/architecture
GET /api/model/comparison
GET /api/analytics/summary`,
  },
  {
    title: 'DATASET',
    icon: BarChart3,
    content: `The model is trained on the Financial PhraseBank dataset, which contains ~4,800 English financial sentences annotated by financial experts.

Labels: Positive, Neutral, Negative
Split: 80% Train / 10% Validation / 10% Test
Agreement: sentences_allagree subset (highest annotator agreement)

The dataset was cleaned, deduplicated, and stratified-split to ensure balanced representation across all classes.`,
  },
  {
    title: 'IMPORTANT DISCLAIMER',
    icon: Shield,
    content: `FinSight AI predicts textual sentiment and likely market implications based on language analysis. It does NOT:

• Predict actual stock prices or market movements
• Provide financial advice
• Guarantee trading outcomes
• Access real-time market data

All predictions represent model-estimated textual sentiment analysis and must not be considered financial advice. The system analyzes language patterns, not market data. Performance metrics shown are from actual model evaluation on test data — no values are fabricated.`,
  },
];

export default function Documentation() {
  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <div className="label-accent" style={{ marginBottom: 4 }}>DOCUMENTATION / 08</div>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', fontWeight: 600 }}>System Documentation</h1>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {sections.map(section => (
          <div key={section.title} className="panel">
            <div className="panel-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <section.icon size={14} style={{ color: 'var(--accent-primary)' }} />
                <span className="panel-title">{section.title}</span>
              </div>
            </div>
            <div className="panel-body">
              <pre style={{
                fontFamily: 'var(--font-body)',
                fontSize: '0.82rem',
                color: 'var(--text-secondary)',
                lineHeight: 1.7,
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
              }}>
                {section.content}
              </pre>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
