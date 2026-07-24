import { useState } from 'react';
import {
  Shield,
  ImageIcon,
  Video,
  PenLine,
  History,
  FileText,
  ChevronRight,
  Zap,
  Lock,
  BarChart2,
} from 'lucide-react';

/* ── Page labels ──────────────────────────────────────────── */
const PAGES = ['home', 'image', 'video', 'signature', 'history', 'about'];

/* ── Navigation ──────────────────────────────────────────── */
function Navbar({ page, setPage }) {
  const links = [
    { id: 'image',     label: 'Image',     icon: <ImageIcon size={15} /> },
    { id: 'video',     label: 'Video',     icon: <Video     size={15} /> },
    { id: 'signature', label: 'Signature', icon: <PenLine   size={15} /> },
    { id: 'history',   label: 'History',   icon: <History   size={15} /> },
    { id: 'about',     label: 'About',     icon: <FileText  size={15} /> },
  ];
  return (
    <nav className="nav">
      <div className="container nav-inner">
        <button className="nav-logo" onClick={() => setPage('home')}
          style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
          ⬡ Digital Forensic Suite
        </button>
        <ul className="nav-links">
          {links.map(l => (
            <li key={l.id}>
              <button
                id={`nav-${l.id}`}
                className={`nav-link flex items-center gap-2 ${page === l.id ? 'active' : ''}`}
                style={{ background: 'none', border: 'none', cursor: 'pointer' }}
                onClick={() => setPage(l.id)}
              >
                {l.icon} {l.label}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}

/* ── Hero / Home ─────────────────────────────────────────── */
function HomePage({ setPage }) {
  const engines = [
    {
      id: 'image', icon: <ImageIcon size={28} />, color: 'var(--clr-primary)',
      title: 'Image Forgery',
      desc: 'ELA + CNN detection with Grad-CAM heatmap overlays for pixel-level explainability.',
    },
    {
      id: 'video', icon: <Video size={28} />, color: 'var(--clr-accent-violet)',
      title: 'Deepfake Video',
      desc: 'CNN + Bi-LSTM frame analysis with suspicious-frame timeline and per-frame confidence.',
    },
    {
      id: 'signature', icon: <PenLine size={28} />, color: 'var(--clr-accent-cyan)',
      title: 'Signature Verification',
      desc: 'Siamese EfficientNetB3 network computing similarity scores with FAR/FRR metrics.',
    },
  ];

  const features = [
    { icon: <Zap size={20} />, title: 'Fast Inference', desc: 'Optimised pipelines return results in seconds.' },
    { icon: <Lock size={20} />, title: 'Explainable AI', desc: 'Grad-CAM heatmaps show which pixels drove the verdict.' },
    { icon: <BarChart2 size={20} />, title: 'PDF Reports', desc: 'Download court-ready forensic reports with one click.' },
  ];

  return (
    <div className="fade-in">
      {/* Hero */}
      <section style={{
        padding: '80px 0 64px',
        textAlign: 'center',
        background: 'radial-gradient(ellipse 80% 60% at 50% 0%, rgba(59,130,246,0.12), transparent)',
      }}>
        <div className="container">
          <div className="flex justify-center mb-4">
            <span className="badge badge-primary" style={{ fontSize: '0.8rem', padding: '6px 14px' }}>
              <Shield size={13} /> AI-Powered Forensics
            </span>
          </div>
          <h1 style={{ marginBottom: '24px' }}>
            Detect. Analyse.{' '}
            <span className="text-gradient">Prove.</span>
          </h1>
          <p style={{ maxWidth: '600px', margin: '0 auto 40px', fontSize: '1.15rem', lineHeight: 1.7 }}>
            A multi-modal deep learning system for detecting image manipulation,
            deepfake video, and signature forgery — with explainable AI and
            downloadable forensic reports.
          </p>
          <div className="flex justify-center gap-4">
            <button id="hero-start-btn" className="btn btn-primary" onClick={() => setPage('image')}>
              Get Started <ChevronRight size={16} />
            </button>
            <button id="hero-about-btn" className="btn btn-secondary" onClick={() => setPage('about')}>
              Learn More
            </button>
          </div>
        </div>
      </section>

      {/* Engine Cards */}
      <section style={{ padding: '64px 0' }}>
        <div className="container">
          <h2 style={{ textAlign: 'center', marginBottom: '48px' }}>Three Detection Engines</h2>
          <div className="grid-3">
            {engines.map(e => (
              <div key={e.id} className="card" style={{ cursor: 'pointer' }}
                onClick={() => setPage(e.id)}>
                <div style={{
                  width: 56, height: 56, borderRadius: 'var(--radius-md)',
                  background: `${e.color}22`, border: `1px solid ${e.color}44`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: e.color, marginBottom: 'var(--space-5)',
                }}>
                  {e.icon}
                </div>
                <h4 style={{ marginBottom: 'var(--space-2)' }}>{e.title}</h4>
                <p className="text-sm">{e.desc}</p>
                <div className="flex items-center gap-2 mt-4" style={{ color: e.color }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>Open Engine</span>
                  <ChevronRight size={14} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Strip */}
      <section style={{ padding: '48px 0 80px' }}>
        <div className="container">
          <div className="grid-3">
            {features.map(f => (
              <div key={f.title} className="flex gap-4" style={{ alignItems: 'flex-start' }}>
                <div style={{
                  flexShrink: 0, width: 40, height: 40,
                  borderRadius: 'var(--radius-sm)',
                  background: 'var(--clr-bg-elevated)',
                  border: '1px solid var(--clr-border)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: 'var(--clr-primary)',
                }}>
                  {f.icon}
                </div>
                <div>
                  <h4 style={{ marginBottom: 4 }}>{f.title}</h4>
                  <p className="text-sm">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

/* ── Placeholder Page ─────────────────────────────────────── */
function PlaceholderPage({ title, icon, color }) {
  return (
    <div className="fade-in" style={{ padding: '80px 0', textAlign: 'center' }}>
      <div className="container">
        <div style={{
          width: 72, height: 72, borderRadius: 'var(--radius-lg)',
          background: `${color}22`, border: `1px solid ${color}44`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color, margin: '0 auto 24px', fontSize: 32,
        }}>
          {icon}
        </div>
        <h2 style={{ marginBottom: 12 }}>{title}</h2>
        <p style={{ maxWidth: 480, margin: '0 auto' }}>
          This page is under active development (Week 1 scaffolding). The backend
          service and model will be wired up here once training is complete.
        </p>
        <div className="badge badge-warning mt-6" style={{ margin: '24px auto 0' }}>
          🚧 Coming in Week 2–3
        </div>
      </div>
    </div>
  );
}

/* ── App Root ─────────────────────────────────────────────── */
export default function App() {
  const [page, setPage] = useState('home');

  function renderPage() {
    switch (page) {
      case 'home':      return <HomePage setPage={setPage} />;
      case 'image':     return <PlaceholderPage title="Image Forensics"        icon={<ImageIcon />} color="var(--clr-primary)" />;
      case 'video':     return <PlaceholderPage title="Video Deepfake Analysis" icon={<Video />}    color="var(--clr-accent-violet)" />;
      case 'signature': return <PlaceholderPage title="Signature Verification"  icon={<PenLine />}  color="var(--clr-accent-cyan)" />;
      case 'history':   return <PlaceholderPage title="Analysis History"        icon={<History />}  color="var(--clr-accent-emerald)" />;
      case 'about':     return <PlaceholderPage title="About the Project"       icon={<FileText />} color="var(--clr-accent-amber)" />;
      default:          return <HomePage setPage={setPage} />;
    }
  }

  return (
    <div className="page-wrapper">
      <Navbar page={page} setPage={setPage} />
      <main style={{ flex: 1 }}>
        {renderPage()}
      </main>
      <footer style={{
        borderTop: '1px solid var(--clr-border)',
        padding: 'var(--space-6) 0',
        textAlign: 'center',
      }}>
        <p className="text-sm text-muted">
          Digital Forensic Suite · 4-person team · 6-week sprint · Week 1 ✅
        </p>
      </footer>
    </div>
  );
}
