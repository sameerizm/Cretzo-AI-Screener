// React Component for CV Screening
// Install: npm install lucide-react

import React, { useState } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle, AlertTriangle, XCircle } from 'lucide-react';

// Replace with your actual API URL
const API_URL = 'http://localhost:8000/screen';
// For deployed: const API_URL = 'https://your-app.onrender.com/screen';

export default function CVScreening() {
  const [jdFile, setJdFile] = useState(null);
  const [skills, setSkills] = useState('');
  const [cvFiles, setCvFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!jdFile || !skills || cvFiles.length === 0) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    const formData = new FormData();
    formData.append('jd_file', jdFile);
    formData.append('must_have_skills', skills);
    
    cvFiles.forEach(file => {
      formData.append('cv_files', file);
    });

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(`Failed to screen CVs: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getVerdictStyle = (verdict) => {
    if (verdict.includes('Strong')) return 'border-green-500 bg-green-50';
    if (verdict.includes('Partial')) return 'border-yellow-500 bg-yellow-50';
    return 'border-red-500 bg-red-50';
  };

  const getVerdictIcon = (verdict) => {
    if (verdict.includes('Strong')) return <CheckCircle className="text-green-600" size={24} />;
    if (verdict.includes('Partial')) return <AlertTriangle className="text-yellow-600" size={24} />;
    return <XCircle className="text-red-600" size={24} />;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 to-indigo-700 p-4">
      <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-2xl p-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-8 text-center">
          🎯 CV Screening System
        </h1>

        <div className="space-y-6">
          {/* Job Description File */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Job Description File *
            </label>
            <div className="flex items-center justify-center w-full">
              <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <FileText className="w-10 h-10 mb-3 text-gray-400" />
                  <p className="mb-2 text-sm text-gray-500">
                    <span className="font-semibold">Click to upload</span> JD file
                  </p>
                  <p className="text-xs text-gray-500">TXT, PDF, or DOCX</p>
                </div>
                <input
                  type="file"
                  className="hidden"
                  accept=".txt,.pdf,.docx"
                  onChange={(e) => setJdFile(e.target.files[0])}
                  required
                />
              </label>
            </div>
            {jdFile && (
              <p className="mt-2 text-sm text-green-600">✓ {jdFile.name}</p>
            )}
          </div>

          {/* Must-Have Skills */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Must-Have Skills (comma-separated) *
            </label>
            <input
              type="text"
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
              placeholder="e.g., Python, FastAPI, Docker, SQL"
              value={skills}
              onChange={(e) => setSkills(e.target.value)}
              required
            />
          </div>

          {/* CV Files */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Candidate CV Files (multiple) *
            </label>
            <div className="flex items-center justify-center w-full">
              <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <Upload className="w-10 h-10 mb-3 text-gray-400" />
                  <p className="mb-2 text-sm text-gray-500">
                    <span className="font-semibold">Click to upload</span> CV files
                  </p>
                  <p className="text-xs text-gray-500">Select multiple files</p>
                </div>
                <input
                  type="file"
                  className="hidden"
                  accept=".txt,.pdf,.docx"
                  multiple
                  onChange={(e) => setCvFiles(Array.from(e.target.files))}
                  required
                />
              </label>
            </div>
            {cvFiles.length > 0 && (
              <p className="mt-2 text-sm text-green-600">
                ✓ {cvFiles.length} file(s) selected
              </p>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="button"
            onClick={handleSubmit}
            disabled={loading}
            className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-4 rounded-lg font-semibold text-lg hover:shadow-lg transform hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Processing...' : 'Screen Candidates'}
          </button>
        </div>

        {/* Loading Spinner */}
        {loading && (
          <div className="mt-8 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
            <p className="mt-4 text-purple-600 font-semibold">Processing CVs...</p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mt-6 bg-red-50 border-l-4 border-red-500 p-4 rounded">
            <div className="flex items-center">
              <AlertCircle className="text-red-500 mr-3" />
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="mt-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">
              📊 Screening Results ({results.total_candidates} candidates)
            </h2>

            <div className="space-y-4">
              {results.results.map((result, index) => (
                <div
                  key={index}
                  className={`border-l-4 rounded-lg p-6 ${getVerdictStyle(result.verdict)}`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-gray-800">
                        {index + 1}. {result.candidate_filename}
                      </h3>
                      <div className="flex items-center mt-2">
                        {getVerdictIcon(result.verdict)}
                        <span className="ml-2 font-semibold text-lg">
                          {result.verdict}
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-4xl font-bold text-purple-600">
                        {result.final_score}
                      </div>
                      <div className="text-sm text-gray-600">/ 100</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div className="bg-white rounded-lg p-3 text-center">
                      <div className="text-sm text-gray-600">Skill Match</div>
                      <div className="text-xl font-bold text-gray-800">
                        {result.skill_analysis.skill_match_percentage}%
                      </div>
                    </div>
                    <div className="bg-white rounded-lg p-3 text-center">
                      <div className="text-sm text-gray-600">JD Overlap</div>
                      <div className="text-xl font-bold text-gray-800">
                        {result.jd_overlap_percentage}%
                      </div>
                    </div>
                    <div className="bg-white rounded-lg p-3 text-center">
                      <div className="text-sm text-gray-600">Skills</div>
                      <div className="text-xl font-bold text-gray-800">
                        {result.skill_analysis.matched_count}/{result.skill_analysis.total_required}
                      </div>
                    </div>
                  </div>

                  <div>
                    <div className="text-sm font-semibold text-gray-700 mb-2">
                      Skills Analysis:
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {result.skill_analysis.matched_skills.map((skill, i) => (
                        <span
                          key={i}
                          className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm"
                        >
                          ✓ {skill}
                        </span>
                      ))}
                      {result.skill_analysis.missing_skills.map((skill, i) => (
                        <span
                          key={i}
                          className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm"
                        >
                          ✗ {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
