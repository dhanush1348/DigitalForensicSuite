import {
  Shield,
  FileText,
  CheckCircle,
  AlertTriangle,
  Cpu,
  Database,
  BookOpen,
  Award,
  Layers,
  Search,
} from 'lucide-react';

export default function AboutPage() {
  const references = [
    {
      id: 1,
      authors: 'Yoldar, M. T., Eryiğit, R., & Cantürk, N. (2025)',
      title: 'Explainable AI in Signature Forgery Detection',
      journal: 'Pattern Recognition Letters, Elsevier, Vol. 198, pp. 93–100',
      doi: '10.1016/j.patrec.2025.10.003',
    },
    {
      id: 2,
      authors: 'Stergiou, K., Ougiaroglou, S., & Sidiropoulos, A. (2025)',
      title: 'Signature Forgery Detection Using Deep and Machine Learning',
      journal: 'International Journal of Reliable and Quality E-Healthcare (SAGE)',
      doi: '10.1177/18724981251330068',
    },
    {
      id: 3,
      authors: 'Xu, Z., Zhang, X., Li, R., Tang, Z., Huang, Q., & Zhang, J. (2025)',
      title: 'FakeShield: Explainable Image Forgery Detection and Localization via Multi-modal Large Language Models',
      journal: 'International Conference on Learning Representations (ICLR 2025)',
      doi: 'ICLR 2025 Conference Proceeding',
    },
    {
      id: 4,
      authors: 'Wu, X., Chen, X., Wu, X., Li, D., Chen, Z., He, Y., & Zhao, C. (2025)',
      title: 'Explainable Image-Centric Forgery Detection: A Survey',
      journal: 'SSRN Preprint',
      doi: 'SSRN-2025-Survey',
    },
    {
      id: 5,
      authors: 'Selvaraju, R. R., Cogswell, M., Das, A., Vedantam, R., Parikh, D., & Batra, D. (2017)',
      title: 'Grad-CAM: Visual Explanations from Deep Networks via Gradient-Based Localization',
      journal: 'Proceedings of the IEEE International Conference on Computer Vision (ICCV 2017)',
      doi: '10.1109/ICCV.2017.74',
    },
  ];

  return (
    <div className="fade-in" style={{ padding: '60px 0 100px' }}>
      <div className="container" style={{ maxWidth: 960 }}>

        {/* Institution Banner */}
        <div style={{
          background: 'linear-gradient(135deg, rgba(59,130,246,0.12) 0%, rgba(139,92,246,0.12) 100%)',
          border: '1px solid var(--clr-border-accent)',
          borderRadius: 'var(--radius-lg)',
          padding: '28px 36px',
          textAlign: 'center',
          marginBottom: 40,
        }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, color: 'var(--clr-primary)', marginBottom: 8 }}>
            <Award size={18} />
            <span style={{ fontSize: '0.85rem', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
              Department of Information Technology
            </span>
          </div>
          <h3 style={{ margin: '0 0 4px', fontSize: '1.3rem' }}>
            S R K R ENGINEERING COLLEGE (A)
          </h3>
          <p className="text-sm" style={{ margin: '0 0 12px', color: 'var(--clr-text-secondary)' }}>
            China Amiram, Bhimavaram - 534204 · 4/4 B.Tech (IT / AI&DS / CSBS) 2nd Semester (R23) AY-2026-2027
          </p>
          <div className="badge badge-primary" style={{ fontSize: '0.8rem', padding: '4px 14px' }}>
            Project Work Proposal & Documentation
          </div>
        </div>

        {/* Main Title & Subtitle */}
        <div style={{ textAlign: 'center', marginBottom: 48 }}>
          <h1 style={{ fontSize: '2.2rem', marginBottom: 16 }}>
            <span className="text-gradient">SecureVision-XAI</span>
          </h1>
          <h3 style={{ fontWeight: 500, color: 'var(--clr-text-primary)', maxWidth: 780, margin: '0 auto 20px', lineHeight: 1.4 }}>
            An Explainable AI Framework for Signature Verification and Image Forgery Detection
          </h3>
          <p className="text-sm text-muted" style={{ maxWidth: 680, margin: '0 auto' }}>
            Multi-modal forensic authentication using Siamese Neural Networks, EfficientNet-B0, and Grad-CAM visual explanations.
          </p>
        </div>

        {/* Abstract */}
        <div className="card-elevated" style={{ marginBottom: 32 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
            <BookOpen size={22} style={{ color: 'var(--clr-primary)' }} />
            <h3 style={{ margin: 0 }}>Abstract</h3>
          </div>
          <p style={{ lineHeight: 1.8, fontSize: '0.98rem' }}>
            The increasing use of digital documents in banking, legal services, education, and e-governance has made
            document authentication a critical challenge. Traditional signature verification methods are often manual,
            time-consuming, and prone to human error, while manipulated digital images can bypass basic security checks.
            This project proposes <strong>SecureVision-XAI</strong>, a dual-module framework that independently performs
            offline signature verification and digital image forgery detection using deep learning and Explainable Artificial Intelligence (XAI).
          </p>
          <p style={{ lineHeight: 1.8, fontSize: '0.98rem', marginTop: 12 }}>
            The first module verifies whether a handwritten signature is genuine or forged using a Siamese Neural Network with a pretrained CNN backbone.
            The second module detects digitally manipulated images, such as copy-move and splicing forgeries, using an EfficientNet/CNN backbone with Error Level Analysis (ELA).
            Grad-CAM is integrated into both modules to generate visual explanations that highlight the image regions influencing the model's decisions.
            The system provides confidence scores, similarity measurements, tampering localization, and downloadable verification reports.
          </p>
        </div>

        {/* Problem Statement */}
        <div className="card" style={{ marginBottom: 32, borderColor: 'rgba(245,158,11,0.3)', background: 'rgba(245,158,11,0.03)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
            <AlertTriangle size={22} style={{ color: 'var(--clr-accent-amber)' }} />
            <h3 style={{ margin: 0 }}>Problem Statement</h3>
          </div>
          <p style={{ lineHeight: 1.8, fontSize: '0.95rem' }}>
            The rapid digitization of documents has increased the risk of forged signatures and manipulated digital images.
            Existing verification systems generally focus on only one problem — either signature verification or image forgery detection —
            and often behave as "black-box" models without explaining their predictions. This lack of transparency limits their adoption
            in sensitive domains such as banking, legal documentation, and forensic investigations. There is a need for an integrated AI-based
            framework that independently performs signature verification and image forgery detection while providing interpretable explanations for every prediction.
          </p>
        </div>

        {/* Existing vs Proposed System Comparison */}
        <div className="grid-2" style={{ gap: 24, marginBottom: 40 }}>
          {/* Existing */}
          <div className="card" style={{ borderColor: 'rgba(244,63,94,0.3)', background: 'rgba(244,63,94,0.03)' }}>
            <h4 style={{ color: 'var(--clr-accent-rose)', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
              <AlertTriangle size={18} /> Existing Systems & Limitations
            </h4>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 10 }}>
              {[
                'Perform only signature verification OR only image forgery detection (siloed tools).',
                'Most models provide only binary outputs (Genuine/Forged) with zero explanation.',
                'No explainability (Black-box models — hard for legal & forensic trust).',
                'Limited ability to detect sophisticated or skilled stroke/compression forgeries.',
                'Require manual forensic analysis for final court/bank verification.',
              ].map((item, idx) => (
                <li key={idx} className="text-sm" style={{ display: 'flex', gap: 8, alignItems: 'flex-start' }}>
                  <span style={{ color: 'var(--clr-accent-rose)', fontWeight: 'bold' }}>✕</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Proposed */}
          <div className="card" style={{ borderColor: 'rgba(16,185,129,0.3)', background: 'rgba(16,185,129,0.03)' }}>
            <h4 style={{ color: 'var(--clr-accent-emerald)', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
              <CheckCircle size={18} /> Proposed SecureVision-XAI
            </h4>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 10 }}>
              {[
                'Unified dual-module system for both signature verification & image forgery detection.',
                'Explainable AI via Grad-CAM heatmaps showing exact driving pixel regions.',
                'Continuous confidence scores & cosine similarity percentages.',
                'Localizes copy-move, splicing, and compression tampering.',
                'Instant inference via FastAPI REST backend with modern React interface.',
              ].map((item, idx) => (
                <li key={idx} className="text-sm" style={{ display: 'flex', gap: 8, alignItems: 'flex-start' }}>
                  <span style={{ color: 'var(--clr-accent-emerald)', fontWeight: 'bold' }}>✓</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Modules Breakdown */}
        <div style={{ marginBottom: 48 }}>
          <h2 style={{ textAlign: 'center', marginBottom: 32 }}>Dual-Module System Architecture</h2>
          <div className="grid-2" style={{ gap: 24 }}>
            
            {/* Module 1 */}
            <div className="card-elevated">
              <div className="badge badge-info" style={{ marginBottom: 12 }}>Module 1</div>
              <h4 style={{ color: 'var(--clr-accent-cyan)', marginBottom: 12 }}>Signature Verification</h4>
              <p className="text-sm" style={{ marginBottom: 16 }}>
                Uses a <strong>Siamese Neural Network</strong> with a shared ResNet18 backbone trained on CEDAR / BHSig260 signature datasets.
              </p>
              <ul style={{ paddingLeft: 20, fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: 6, color: 'var(--clr-text-secondary)' }}>
                <li>Upload reference (genuine) signature</li>
                <li>Upload questioned signature</li>
                <li>Grayscale → Otsu thresholding → morphological cleaning</li>
                <li>128-d L2-normalized embedding extraction</li>
                <li>Cosine similarity metric (0–100%)</li>
                <li>Grad-CAM visual heatmap on pen stroke regions</li>
              </ul>
            </div>

            {/* Module 2 */}
            <div className="card-elevated">
              <div className="badge badge-primary" style={{ marginBottom: 12 }}>Module 2</div>
              <h4 style={{ color: 'var(--clr-primary)', marginBottom: 12 }}>Image Forgery Detection</h4>
              <p className="text-sm" style={{ marginBottom: 16 }}>
                Fine-tuned <strong>EfficientNet-B0</strong> with Error Level Analysis (ELA) pipeline trained on CASIA v2.0 dataset.
              </p>
              <ul style={{ paddingLeft: 20, fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: 6, color: 'var(--clr-text-secondary)' }}>
                <li>Upload any digital image (JPEG/PNG/BMP/TIFF)</li>
                <li>ELA re-compression (Q=95, 10x diff amplification)</li>
                <li>Detect Copy-Move, Image Splicing, and Resampling</li>
                <li>Localize tampered pixel regions</li>
                <li>Output class probabilities P(Authentic) vs P(Forged)</li>
                <li>Grad-CAM visual heatmap overlay</li>
              </ul>
            </div>

          </div>
        </div>

        {/* Datasets & Tech Stack */}
        <div className="card-elevated" style={{ marginBottom: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <Database size={22} style={{ color: 'var(--clr-accent-violet)' }} />
            <h3 style={{ margin: 0 }}>Supported Datasets & Benchmark Source Links</h3>
          </div>
          
          {/* Dataset Links Box */}
          <div style={{
            background: 'var(--clr-bg-elevated)',
            border: '1px solid var(--clr-border-accent)',
            borderRadius: 'var(--radius-md)',
            padding: '16px 20px',
            marginBottom: 24,
          }}>
            <h5 style={{ color: 'var(--clr-primary)', marginBottom: 12 }}>Official Benchmark Repositories</h5>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8 }}>
                <span className="text-sm" style={{ fontWeight: 600 }}>Signature Dataset (CEDAR & BHSig260):</span>
                <a
                  href="https://www.kaggle.com/datasets/ishanikathuria/handwritten-signature-datasets"
                  target="_blank"
                  rel="noreferrer"
                  className="badge badge-primary"
                  style={{ textDecoration: 'none', padding: '6px 12px' }}
                >
                  Kaggle: Handwritten Signature Datasets ↗
                </a>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8 }}>
                <span className="text-sm" style={{ fontWeight: 600 }}>Image Forgery (CASIA 2.0 Corrected Groundtruth):</span>
                <a
                  href="https://github.com/SunnyHaze/CASIA2.0-Corrected-Groundtruth"
                  target="_blank"
                  rel="noreferrer"
                  className="badge badge-info"
                  style={{ textDecoration: 'none', padding: '6px 12px' }}
                >
                  GitHub: CASIA2.0-Corrected-Groundtruth ↗
                </a>
              </div>
            </div>
          </div>

          <div className="grid-2" style={{ gap: 24 }}>
            <div>
              <h5 style={{ color: 'var(--clr-accent-cyan)', marginBottom: 10 }}>Signature Datasets</h5>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                <span className="badge badge-primary">CEDAR Dataset ✓</span>
                <span className="badge badge-info">BHSig260</span>
                <span className="badge badge-info">GPDS Signature</span>
                <span className="badge badge-info">DeepSignDB</span>
              </div>
            </div>
            <div>
              <h5 style={{ color: 'var(--clr-primary)', marginBottom: 10 }}>Image Forgery Datasets</h5>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                <span className="badge badge-primary">CASIA v2.0 ✓</span>
                <span className="badge badge-info">Columbia Splicing</span>
                <span className="badge badge-info">COVERAGE</span>
                <span className="badge badge-info">IMD2020</span>
              </div>
            </div>
          </div>
        </div>


        {/* Formal References */}
        <div className="card-elevated">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 24 }}>
            <FileText size={22} style={{ color: 'var(--clr-primary)' }} />
            <h3 style={{ margin: 0 }}>Academic References</h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {references.map((ref) => (
              <div key={ref.id} style={{
                background: 'var(--clr-bg-elevated)',
                border: '1px solid var(--clr-border)',
                borderRadius: 'var(--radius-md)',
                padding: '14px 18px',
              }}>
                <p style={{ fontWeight: 600, fontSize: '0.92rem', margin: '0 0 4px', color: 'var(--clr-text-primary)' }}>
                  [{ref.id}] {ref.title}
                </p>
                <p className="text-xs text-muted" style={{ margin: '0 0 4px' }}>
                  {ref.authors} — <em>{ref.journal}</em>
                </p>
                <span className="badge badge-info" style={{ fontSize: '0.7rem' }}>
                  DOI: {ref.doi}
                </span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
