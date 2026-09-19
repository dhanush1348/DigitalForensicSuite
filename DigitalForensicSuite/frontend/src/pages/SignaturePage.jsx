import { useState, useRef, useCallback } from 'react';
import { PenLine, Upload, X, Eye, EyeOff, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import { analyzeSignature } from '../api/client.js';

/* ── Signature Upload Zone ──────────────────────────────────── */
function SigDropZone({ id, file, onFile, label, color }) {
  const [dragging, setDragging] = useState(false);
  const inputRef  = useRef(null);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files?.[0];
    if (f) onFile(f);
  }, [onFile]);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    setDragging(e.type === 'dragover');
  }, []);

  return (
    <div
      className={`upload-zone ${dragging ? 'drag-over' : ''}`}
      style={{
        padding: '28px 16px', cursor: 'pointer',
        borderColor: file ? `${color}66` : undefined,
        background: file ? `${color}08` : undefined,
      }}
      onDrop={handleDrop}
      onDragOver={handleDrag}
      onDragLeave={handleDrag}
      onClick={() => inputRef.current?.click()}
    >
      <input
        id={id}
        ref={inputRef}
        type="file"
        accept=".jpg,.jpeg,.png,.bmp"
        style={{ display: 'none' }}
        onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])}
      />
      {file ? (
        <div className="flex flex-col items-center gap-3">
          <img
            src={URL.createObjectURL(file)}
            alt={label}
            style={{
              maxHeight: 120, maxWidth: '100%',
              borderRadius: 'var(--radius-md)',
              objectFit: 'contain',
              filter: 'invert(1) hue-rotate(0deg)',  // show dark ink on light
            }}
          />
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span className="badge badge-info" style={{ fontSize: '0.7rem' }}>{file.name.slice(0, 22)}</span>
            <button
              className="btn btn-ghost"
              style={{ padding: '2px 6px' }}
              onClick={(e) => { e.stopPropagation(); onFile(null); }}
            >
              <X size={12} />
            </button>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-3" style={{ color: 'var(--clr-text-secondary)' }}>
          <div style={{
            width: 48, height: 48, borderRadius: 'var(--radius-md)',
            background: `${color}15`, border: `1px solid ${color}44`,
            display: 'flex', alignItems: 'center', justifyContent: 'center', color,
          }}>
            <Upload size={20} />
          </div>
          <div style={{ textAlign: 'center' }}>
            <p style={{ fontWeight: 600, color: 'var(--clr-text-primary)', marginBottom: 2, fontSize: '0.9rem' }}>{label}</p>
            <p className="text-xs">Click or drag to upload</p>
          </div>
        </div>
      )}
    </div>
  );
}

/* ── Similarity Gauge ───────────────────────────────────────── */
function SimilarityGauge({ percent, verdict }) {
  const isGenuine = verdict === 'GENUINE';
  const color     = isGenuine ? 'var(--clr-accent-emerald)' : 'var(--clr-accent-rose)';
  const radius    = 52;
  const circ      = 2 * Math.PI * radius;
  const offset    = circ - (percent / 100) * circ;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
      <svg width="130" height="130" style={{ transform: 'rotate(-90deg)' }}>
        <circle cx="65" cy="65" r={radius} fill="none" stroke="var(--clr-bg-elevated)" strokeWidth="10" />
        <circle
          cx="65" cy="65" r={radius}
          fill="none" stroke={color} strokeWidth="10"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 1s ease' }}
        />
      </svg>
      <div style={{ marginTop: -108, textAlign: 'center', lineHeight: 1.2 }}>
        <div style={{ fontSize: '1.6rem', fontWeight: 800, color }}>{percent.toFixed(0)}%</div>
        <div className="text-xs" style={{ color: 'var(--clr-text-secondary)' }}>Similarity</div>
      </div>
      <div style={{ marginTop: 52 }} />
    </div>
  );
}

/* ── Result Card ────────────────────────────────────────────── */
function ResultCard({ result }) {
  const [showHeatmap, setShowHeatmap] = useState(false);
  const isGenuine    = result.verdict === 'GENUINE';
  const verdictColor = isGenuine ? 'var(--clr-accent-emerald)' : 'var(--clr-accent-rose)';

  return (
    <div className="card-elevated fade-in" style={{ marginTop: 32 }}>
      {/* Verdict header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 28 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {isGenuine
            ? <CheckCircle size={28} style={{ color: verdictColor }} />
            : <AlertCircle size={28} style={{ color: verdictColor }} />}
          <div>
            <h3 style={{ margin: 0, color: verdictColor }}>{result.verdict}</h3>
            <p className="text-sm" style={{ margin: 0 }}>
              {isGenuine ? 'Signatures match — likely genuine' : 'Signatures differ — possible forgery'}
            </p>
          </div>
        </div>
        <span className={`badge ${isGenuine ? 'badge-success' : 'badge-danger'}`}>
          {isGenuine ? '✓ Genuine' : '⚠ Forged'}
        </span>
      </div>

      {/* Gauge + stats */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 32, flexWrap: 'wrap', marginBottom: 24 }}>
        <SimilarityGauge percent={result.similarity_percent} verdict={result.verdict} />
        <div style={{ flex: 1, minWidth: 180 }}>
          <div style={{ background: 'var(--clr-bg-elevated)', borderRadius: 'var(--radius-md)', padding: '12px 16px', marginBottom: 12 }}>
            <p className="text-xs" style={{ color: 'var(--clr-text-muted)', marginBottom: 4 }}>Similarity Score</p>
            <p style={{ fontWeight: 700, fontSize: '1.3rem', color: verdictColor }}>
              {result.similarity_percent.toFixed(1)}%
            </p>
          </div>
          <div style={{ background: 'var(--clr-bg-elevated)', borderRadius: 'var(--radius-md)', padding: '12px 16px' }}>
            <p className="text-xs" style={{ color: 'var(--clr-text-muted)', marginBottom: 4 }}>Confidence</p>
            <p style={{ fontWeight: 700, fontSize: '1.3rem', color: verdictColor }}>
              {(result.confidence * 100).toFixed(1)}%
            </p>
          </div>
        </div>
      </div>

      {/* Confidence bar */}
      <div style={{ marginBottom: 20 }}>
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{
              width: `${result.similarity_percent}%`,
              background: verdictColor,
              boxShadow: `0 0 8px ${verdictColor}66`,
            }}
          />
        </div>
      </div>

      {/* Heatmap */}
      {result.heatmap_b64 && (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
            <span className="text-sm" style={{ fontWeight: 600 }}>Grad-CAM — Questioned Signature</span>
            <button
              id="sig-heatmap-toggle-btn"
              className="btn btn-ghost"
              style={{ padding: '4px 12px', fontSize: '0.8rem' }}
              onClick={() => setShowHeatmap(p => !p)}
            >
              {showHeatmap ? <><EyeOff size={14} /> Hide</> : <><Eye size={14} /> Show</>}
            </button>
          </div>
          {showHeatmap && (
            <div className="fade-in" style={{ borderRadius: 'var(--radius-md)', overflow: 'hidden', border: '1px solid var(--clr-border)' }}>
              <img
                src={`data:image/png;base64,${result.heatmap_b64}`}
                alt="Grad-CAM heatmap"
                style={{ width: '100%', display: 'block' }}
              />
            </div>
          )}
        </div>
      )}

      <p className="text-xs" style={{ marginTop: 16, color: 'var(--clr-text-muted)', textAlign: 'right' }}>
        ⏱ {result.processing_time_ms.toFixed(0)} ms
      </p>
    </div>
  );
}

/* ── Signature Verification Page ────────────────────────────── */
export default function SignaturePage() {
  const [refFile,   setRefFile]   = useState(null);
  const [queryFile, setQueryFile] = useState(null);
  const [loading,   setLoading]   = useState(false);
  const [result,    setResult]    = useState(null);
  const [error,     setError]     = useState(null);

  const ready = refFile && queryFile;

  async function handleVerify() {
    if (!ready) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzeSignature(refFile, queryFile);
      setResult(data);
    } catch (err) {
      setError(err.userMessage || 'Verification failed. Is the backend running?');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fade-in" style={{ padding: '60px 0 80px' }}>
      <div className="container" style={{ maxWidth: 800 }}>

        {/* Header */}
        <div style={{ marginBottom: 40 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
            <div style={{
              width: 48, height: 48, borderRadius: 'var(--radius-md)',
              background: 'rgba(6,182,212,0.15)', border: '1px solid rgba(6,182,212,0.3)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: 'var(--clr-accent-cyan)',
            }}>
              <PenLine size={22} />
            </div>
            <div>
              <h2 style={{ margin: 0 }}>Signature Verification</h2>
              <p className="text-sm" style={{ margin: 0 }}>Siamese ResNet18 + Contrastive Loss + Grad-CAM · Trained on CEDAR</p>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <span className="badge badge-info">Siamese ResNet18</span>
            <span className="badge badge-primary">Contrastive Loss</span>
            <span className="badge badge-info">Grad-CAM XAI</span>
            <span className="badge badge-primary">CEDAR Dataset</span>
          </div>
        </div>

        {/* Upload panels */}
        <div className="card" style={{ marginBottom: 24 }}>
          <h4 style={{ marginBottom: 20 }}>Upload Signature Pair</h4>
          <div className="grid-2" style={{ gap: 20 }}>
            <div>
              <p className="text-sm" style={{ marginBottom: 10, fontWeight: 600, color: 'var(--clr-accent-emerald)' }}>
                ① Reference Signature
              </p>
              <p className="text-xs" style={{ marginBottom: 12, color: 'var(--clr-text-muted)' }}>
                Known authentic / ground-truth signature
              </p>
              <SigDropZone
                id="ref-sig-upload"
                file={refFile}
                onFile={setRefFile}
                label="Reference Signature"
                color="var(--clr-accent-emerald)"
              />
            </div>
            <div>
              <p className="text-sm" style={{ marginBottom: 10, fontWeight: 600, color: 'var(--clr-accent-rose)' }}>
                ② Questioned Signature
              </p>
              <p className="text-xs" style={{ marginBottom: 12, color: 'var(--clr-text-muted)' }}>
                Signature to verify against the reference
              </p>
              <SigDropZone
                id="query-sig-upload"
                file={queryFile}
                onFile={setQueryFile}
                label="Questioned Signature"
                color="var(--clr-accent-rose)"
              />
            </div>
          </div>
        </div>

        {/* Verify button */}
        <button
          id="verify-signature-btn"
          className="btn btn-primary w-full"
          style={{ padding: '14px 24px', fontSize: '1rem' }}
          disabled={!ready || loading}
          onClick={handleVerify}
        >
          {loading ? (
            <><div className="spinner" style={{ width: 18, height: 18 }} /> Verifying…</>
          ) : (
            <><PenLine size={16} /> Verify Signature</>
          )}
        </button>

        {!ready && !loading && (
          <p className="text-xs" style={{ textAlign: 'center', marginTop: 10, color: 'var(--clr-text-muted)' }}>
            Upload both signatures to enable verification
          </p>
        )}

        {/* Error */}
        {error && (
          <div className="fade-in" style={{
            marginTop: 24, padding: '14px 18px',
            background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.3)',
            borderRadius: 'var(--radius-md)', color: 'var(--clr-accent-rose)',
            display: 'flex', alignItems: 'center', gap: 10,
          }}>
            <AlertCircle size={18} /> {error}
          </div>
        )}

        {/* Result */}
        {result && <ResultCard result={result} />}
      </div>
    </div>
  );
}
