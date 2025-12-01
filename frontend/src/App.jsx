import React, { useState } from 'react';
import './App.css';

function App() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('resume');
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setResumeFile(e.target.files[0]);
  };

  const handleOptimize = async () => {
    if (!resumeFile || !jobDescription) {
      alert("Please upload a resume and provide a job description.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('resume_file', resumeFile);
    formData.append('job_description', jobDescription);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/optimize`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadContent = (filename, content) => {
    const element = document.createElement('a');
    const file = new Blob([content], { type: 'text/markdown' });
    element.href = URL.createObjectURL(file);
    element.download = filename;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const handleCopy = (content) => {
    navigator.clipboard.writeText(content);
    alert("Copied to clipboard!");
  };

  return (
    <div className="app-container">

      <div className={`main-layout ${result ? 'split-view' : 'centered-view'}`}>

        {/* Left Panel: Input */}
        <section className="glass-card input-panel">
          <header className="app-header">
            <div className="icon-badge">✨</div>
            <h1>Career Catalyst</h1>
            <p className="subtitle">Ignite your professional journey</p>
          </header>

          <div className="input-group">
            <label htmlFor="resume-upload">Upload Resume (TXT/MD/PDF)</label>
            <div className="drop-zone">
              <input
                type="file"
                id="resume-upload"
                accept=".txt,.md,.pdf"
                onChange={handleFileChange}
              />
              <label htmlFor="resume-upload">
                {resumeFile ? (
                  <div className="file-info">
                    <span className="file-icon">📄</span>
                    <span className="file-name">{resumeFile.name}</span>
                    <span className="file-change-text">Click to change</span>
                  </div>
                ) : (
                  <div className="upload-placeholder">
                    <span className="icon">📂</span>
                    <span>Drag & drop or click to upload</span>
                    <span className="sub-text">Supports TXT, MD, PDF</span>
                  </div>
                )}
              </label>
            </div>
          </div>

          <div className="input-group">
            <label htmlFor="jd-input">Job Description</label>
            <textarea
              id="jd-input"
              placeholder="Paste the job description here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
            ></textarea>
          </div>

          <button
            className="cta-button"
            onClick={handleOptimize}
            disabled={loading}
          >
            {loading ? (
              <div className="loading-state">
                <div className="spinner"></div>
                <span>Optimizing...</span>
              </div>
            ) : (
              'Ignite Career 🚀'
            )}
          </button>

          {error && <div className="error-message">{error}</div>}
        </section>

        {/* Right Panel: Output */}
        {result && (
          <section className="glass-card output-panel">
            <div className="panel-header">
              <div className="header-left">
                <h3>Optimization Results</h3>
                <span className="badge">AI Generated</span>
              </div>
              <div className="header-actions">
                <div className="tabs">
                  <button
                    className={`tab-btn ${activeTab === 'resume' ? 'active' : ''}`}
                    onClick={() => setActiveTab('resume')}
                  >
                    Resume
                  </button>
                  <button
                    className={`tab-btn ${activeTab === 'cover' ? 'active' : ''}`}
                    onClick={() => setActiveTab('cover')}
                  >
                    Cover Letter
                  </button>
                </div>
              </div>
            </div>

            <div className="editor-window">
              <div className="window-bar">
                <div className="traffic-lights">
                  <div className="light red"></div>
                  <div className="light yellow"></div>
                  <div className="light green"></div>
                </div>
                <div className="filename-display">
                  {activeTab === 'resume' ? 'tailored_resume.md' : 'cover_letter.md'}
                </div>
              </div>

              <div className="content-area code-scroll-area">
                <pre>
                  {(activeTab === 'resume' ? result.resume_content : result.cover_letter_content) || "No content generated. Please try again."}
                </pre>
              </div>

              <div style={{ padding: '1rem', borderTop: '1px solid #27272a', display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button
                  className="primary-btn-small"
                  style={{ background: '#3f3f46', color: '#fff' }}
                  onClick={() => handleCopy(
                    activeTab === 'resume' ? result.resume_content : result.cover_letter_content
                  )}
                >
                  Copy 📋
                </button>
                <button
                  className="primary-btn-small"
                  onClick={() => downloadContent(
                    activeTab === 'resume' ? 'tailored_resume.md' : 'cover_letter.md',
                    activeTab === 'resume' ? result.resume_content : result.cover_letter_content
                  )}
                >
                  Download ⬇️
                </button>
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}

export default App;
