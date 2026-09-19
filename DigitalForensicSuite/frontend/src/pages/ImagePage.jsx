import { useState, useRef, useCallback } from 'react';
import { ImageIcon, Upload, X, Eye, EyeOff, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import { analyzeImage } from '../api/client.js';

/* ── Upload Zone Component ─────────────────────────────────── */
function DropZone({ file, onFile, accept, label }) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);

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
      style={{ padding: '40px 24px', position: 'relative' }}
      onDrop={handleDrop}
      onDragOver={handleDrag}
      onDragLeave={handleDrag}
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        style={{ display: 'none' }}
        onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])}
      />
      {file ? (
        <div className="flex flex-col items-center gap-4">
          <img
            src={URL.createObjectURL(file)}
            alt="preview"
            style={{ maxHeight: 160, maxWidth: '100%', borderRadius: 'var(--radius-md)', objectFit: 'contain' }}
          />
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span className="badge badge-success">{file.name}</span>
            <button
              className="btn btn-ghost"
              style={{ padding: '4px 8px' }}
              onClick={(e) => { e.stopPropagation(); onFile(null); }}
            >
              <X size={14} />
            </button>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-4" style={{ color: 'var(--clr-text-secondary)' }}>
          <div style={{
            width: 56, height: 56, borderRadius: 'var(--radius-md)',
            background: 'rgba(59,130,246,0.12)', border: '1px solid rgba(59,130,246,0.3)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: 'var(--clr-primary)',
          }}>
            <Upload size={24} />
          </div>
          <div style={{ textAlign: 'center' }}>
            <p style={{ fontWeight: 600, color: 'var(--clr-text-primary)', marginBottom: 4 }}>{label}</p>
            <p className="text-sm">Drag & drop or click to browse</p>
            <p className="text-xs" style={{ marginTop: 4, color: 'var(--clr-text-muted)' }}>JPEG · PNG · BMP · TIFF</p>
          </div>
        </div>
      )}
    </div>
  );
}

/* ── Confidence Bar ─────────────────────────────────────────── */
function ConfidenceBar({ value, color }) {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
        <span className="text-sm" style={{ color: 'var(--clr-text-secondary)' }}>Confidence</span>
        <span style={{ fontWeight: 700, color, fontVariantNumeric: 'tabular-nums' }}>
          {(value * 100).toFixed(1)}%
        </span>
      </div>
      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{
            width: `${value * 100}%`,
            background: color,
            boxShadow: `0 0 8px ${color}66`,
          }}
        />
      </div>
    </div>
  );
}

/* ── Result Card ────────────────────────────────────────────── */
function ResultCard({ result, file }) {
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showEla, setShowEla] = useState(true);
  const isForged  = result.verdict === 'FORGED';
  const verdictColor = isForged ? 'var(--clr-accent-rose)' : 'var(--clr-accent-emerald)';

  return (
    <div className="card-elevated fade-in" style={{ marginTop: 32 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {isForged
            ? <AlertCircle size={28} style={{ color: 'var(--clr-accent-rose)' }} />
            : <CheckCircle size={28} style={{ color: 'var(--clr-accent-emerald)' }} />}
          <div>
            <h3 style={{ margin: 0, color: verdictColor }}>{result.verdict}</h3>
            <p className="text-sm" style={{ margin: 0 }}>
              {isForged ? 'Manipulation detected' : 'No manipulation detected'}
            </p>
          </div>
        </div>
        <span className={`badge ${isForged ? 'badge-danger' : 'badge-success'}`}>
          {isForged ? '⚠ Forged' : '✓ Authentic'}
        </span>
      </div>

      {/* Stats grid */}
      <div className="grid-2" style={{ marginBottom: 24, gap: 16 }}>
        <div style={{ background: 'var(--clr-bg-elevated)', borderRadius: 'var(--radius-md)', padding: '12px 16px' }}>
          <p className="text-xs" style={{ color: 'var(--clr-text-muted)', marginBottom: 4 }}>P(Authentic)</p>
          <p style={{ fontWeight: 700, fontSize: '1.2rem', color: 'var(--clr-accent-emerald)' }}>
            {(result.p_authentic * 100).toFixed(1)}%
          </p>
        </div>
        <div style={{ background: 'var(--clr-bg-elevated)', borderRadius: 'var(--radius-md)', padding: '12px 16px' }}>
          <p className="text-xs" style={{ color: 'var(--clr-text-muted)', marginBottom: 4 }}>P(Forged)</p>
          <p style={{ fontWeight: 700, fontSize: '1.2rem', color: 'var(--clr-accent-rose)' }}>
            {(result.p_forged * 100).toFixed(1)}%
          </p>
        </div>
      </div>

      <ConfidenceBar value={result.confidence} color={verdictColor} />

      {/* Explainability evidence */}
      <div style={{ marginTop: 28 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
          <Eye size={17} style={{ color: 'var(--clr-accent-cyan)' }} />
          <h4 style={{ margin: 0 }}>Why the model decided this</h4>
        </div>
        <p className="text-sm" style={{ lineHeight: 1.7, marginBottom: 14 }}>
          {result.explanation || 'The visual evidence below shows the model input and attribution map.'}
        </p>
        {result.explanation_basis?.length > 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 18 }}>
            {result.explanation_basis.map((item) => (
              <span className="badge badge-info" key={item}>{item}</span>
            ))}
          </div>
        )}
        <div className="grid-3" style={{ gap: 12 }}>
          <EvidencePanel label="Original image" image={file ? URL.createObjectURL(file) : null} />
          <EvidencePanel
            label="ELA evidence"
            image={result.ela_b64 ? `data:image/png;base64,${result.ela_b64}` : null}
            visible={showEla}
            onToggle={() => setShowEla((value) => !value)}
          />
          <EvidencePanel
            label="Grad-CAM attribution"
            image={result.heatmap_b64 ? `data:image/png;base64,${result.heatmap_b64}` : null}
            visible={showHeatmap}
            onToggle={() => setShowHeatmap((value) => !value)}
          />
        </div>
        <p className="text-xs" style={{ marginTop: 12, color: 'var(--clr-text-muted)' }}>
          These visualisations explain model attention; they do not independently prove manipulation.
        </p>
      </div>

      {/* Heatmap toggle */}
      {result.heatmap_b64 && (
        <div style={{ marginTop: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
            <span className="text-sm" style={{ fontWeight: 600 }}>Grad-CAM Heatmap</span>
            <button
              id="heatmap-toggle-btn"
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

function EvidencePanel({ label, image, visible = true, onToggle }) {
  return (
    <div style={{ minWidth: 0 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <span className="text-xs" style={{ fontWeight: 700 }}>{label}</span>
        {onToggle && (
          <button className="btn btn-ghost" style={{ padding: '2px 6px', fontSize: '0.7rem' }} onClick={onToggle}>
            {visible ? 'Hide' : 'Show'}
          </button>
        )}
      </div>
      <div style={{ minHeight: 150, borderRadius: 'var(--radius-md)', overflow: 'hidden', border: '1px solid var(--clr-border)', background: 'var(--clr-bg-elevated)' }}>
        {visible && image && <img src={image} alt={label} style={{ width: '100%', aspectRatio: '1 / 1', objectFit: 'cover', display: 'block' }} />}
      </div>
    </div>
  );
}

/* ── Image Forensics Page ───────────────────────────────────── */
export default function ImagePage() {
  const [file,    setFile]    = useState(null);
  const [loading, setLoading] = useState(false);
  const [result,  setResult]  = useState(null);
  const [error,   setError]   = useState(null);

  async function handleAnalyse() {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzeImage(file);
      setResult(data);
    } catch (err) {
      setError(err.userMessage || 'Analysis failed. Is the backend running?');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fade-in" style={{ padding: '60px 0 80px' }}>
      <div className="container" style={{ maxWidth: 720 }}>

        {/* Header */}
        <div style={{ marginBottom: 40 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
            <div style={{
              width: 48, height: 48, borderRadius: 'var(--radius-md)',
              background: 'rgba(59,130,246,0.15)', border: '1px solid rgba(59,130,246,0.3)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: 'var(--clr-primary)',
            }}>
              <ImageIcon size={22} />
            </div>
            <div>
              <h2 style={{ margin: 0 }}>Image Forgery Detection</h2>
              <p className="text-sm" style={{ margin: 0 }}>EfficientNet-B0 + ELA + Grad-CAM · Trained on CASIA v2.0</p>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <span className="badge badge-info">EfficientNet-B0</span>
            <span className="badge badge-primary">ELA Pipeline</span>
            <span className="badge badge-info">Grad-CAM XAI</span>
            <span className="badge badge-primary">CASIA v2.0</span>
          </div>
        </div>

        {/* Upload */}
        <div className="card" style={{ marginBottom: 24 }}>
          <h4 style={{ marginBottom: 16 }}>Upload Image</h4>
          <DropZone
            file={file}
            onFile={setFile}
            accept="image/jpeg,image/png,image/bmp,image/tiff"
            label="Drop your image here"
          />
        </div>

        {/* Analyse button */}
        <button
          id="analyse-image-btn"
          className="btn btn-primary w-full"
          style={{ padding: '14px 24px', fontSize: '1rem' }}
          disabled={!file || loading}
          onClick={handleAnalyse}
        >
          {loading ? (
            <><div className="spinner" style={{ width: 18, height: 18 }} /> Analysing…</>
          ) : (
            <><ImageIcon size={16} /> Analyse Image</>
          )}
        </button>

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
        {result && <ResultCard result={result} file={file} />}
      </div>
    </div>
  );
}
