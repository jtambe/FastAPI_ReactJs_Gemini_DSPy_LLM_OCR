import React, { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await fetch('http://localhost:8000/upload_invoice', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('Upload failed');
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError('Failed to upload or extract data.');
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h2>Invoice OCR Upload</h2>
        <form onSubmit={handleSubmit}>
          <input type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={handleFileChange} />
          <button type="submit" disabled={loading || !file}>Upload</button>
        </form>
        {loading && <p>Processing...</p>}
        {error && <p style={{color: 'red'}}>{error}</p>}
        {result && (
          <div>
            <h3>Extracted Invoice Data:</h3>
            <p><strong>Total Net Worth:</strong> {result.total_net_worth}</p>
            <p><strong>Total VAT:</strong> {result.total_vat}</p>
            <p><strong>Gross Worth:</strong> {result.gross_worth}</p>
            <p><strong>File Name:</strong> {result.file_name}</p>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
