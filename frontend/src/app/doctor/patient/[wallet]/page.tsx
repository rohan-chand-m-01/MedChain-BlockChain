"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { usePrivy } from "@privy-io/react-auth";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from "recharts";

interface Analysis {
  id: string;
  file_name: string;
  summary: string;
  risk_score: number;
  conditions: string[];
  specialist: string;
  created_at: string;
}

interface MedicalDataPoint {
  value: number;
  unit: string;
  date: string;
}

export default function PatientDetailView() {
  const params = useParams();
  const router = useRouter();
  const { user, authenticated } = usePrivy();
  
  const patientWallet = params.wallet as string;
  
  const [loading, setLoading] = useState(true);
  const [patient, setPatient] = useState<any>(null);
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState<Analysis | null>(null);
  const [medicalData, setMedicalData] = useState<Record<string, MedicalDataPoint[]>>({});
  const [comprehensiveAnalysis, setComprehensiveAnalysis] = useState("");
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  
  // Consultation notes state
  const [chiefComplaint, setChiefComplaint] = useState("");
  const [diagnosis, setDiagnosis] = useState("");
  const [treatmentPlan, setTreatmentPlan] = useState("");
  const [notes, setNotes] = useState("");
  const [savingNotes, setSavingNotes] = useState(false);

  useEffect(() => {
    if (!authenticated) {
      router.push("/");
      return;
    }
    loadPatientData();
  }, [authenticated, patientWallet]);

  const loadPatientData = async () => {
    if (!user?.wallet?.address) return;

    try {
      setLoading(true);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/doctor/patient/${patientWallet}/complete?doctor_wallet=${user.wallet.address}`
      );
      
      if (!response.ok) {
        throw new Error("Failed to load patient data");
      }

      const data = await response.json();
      setPatient(data.patient);
      setAnalyses(data.analyses);
      setMedicalData(data.medical_data);
      
      if (data.analyses.length > 0) {
        setSelectedAnalysis(data.analyses[0]);
      }
    } catch (error) {
      console.error("Error loading patient data:", error);
      alert("Failed to load patient data");
    } finally {
      setLoading(false);
    }
  };

  const generateComprehensiveAnalysis = async () => {
    if (!user?.wallet?.address) return;

    try {
      setLoadingAnalysis(true);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/doctor/patient/${patientWallet}/comprehensive-analysis?doctor_wallet=${user.wallet.address}`,
        { method: "POST" }
      );

      const data = await response.json();
      setComprehensiveAnalysis(data.analysis);
    } catch (error) {
      console.error("Error generating analysis:", error);
      alert("Failed to generate comprehensive analysis");
    } finally {
      setLoadingAnalysis(false);
    }
  };

  const extractMedicalData = async () => {
    if (!user?.wallet?.address) return;

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/doctor/patient/${patientWallet}/extract-medical-data?doctor_wallet=${user.wallet.address}`,
        { method: "POST" }
      );

      const data = await response.json();
      alert(`Extracted ${data.extracted_count} data points for graphing`);
      await loadPatientData(); // Reload to get new data
    } catch (error) {
      console.error("Error extracting medical data:", error);
      alert("Failed to extract medical data");
    }
  };

  const saveConsultationNotes = async () => {
    if (!user?.wallet?.address) return;

    try {
      setSavingNotes(true);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/doctor/consultation-notes?doctor_wallet=${user.wallet.address}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            patient_wallet: patientWallet,
            chief_complaint: chiefComplaint,
            diagnosis: diagnosis,
            treatment_plan: treatmentPlan,
            notes: notes,
            is_draft: false
          })
        }
      );

      if (response.ok) {
        alert("Consultation notes saved successfully!");
      }
    } catch (error) {
      console.error("Error saving notes:", error);
      alert("Failed to save consultation notes");
    } finally {
      setSavingNotes(false);
    }
  };

  const generateMedicalSummaryPDF = async () => {
    if (!user?.wallet?.address) return;

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/doctor/generate-pdf/medical-summary?patient_wallet=${patientWallet}&doctor_wallet=${user.wallet.address}`,
        { method: "POST" }
      );

      const data = await response.json();
      if (data.pdf_url) {
        window.open(data.pdf_url, "_blank");
      } else {
        alert("PDF generated successfully!");
      }
    } catch (error) {
      console.error("Error generating PDF:", error);
      alert("Failed to generate PDF");
    }
  };

  // Prepare graph data
  const prepareGraphData = (dataType: string) => {
    const data = medicalData[dataType] || [];
    return data.map(point => ({
      date: new Date(point.date).toLocaleDateString(),
      value: point.value,
      unit: point.unit
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading patient data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <button
            onClick={() => router.back()}
            className="text-indigo-600 hover:text-indigo-700 flex items-center gap-2"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Patient Detail View</h1>
        </div>

        {/* Patient Profile Card */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Patient Profile</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-500">Name</p>
              <p className="font-semibold">{patient?.full_name || "Unknown"}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Date of Birth</p>
              <p className="font-semibold">{patient?.date_of_birth || "N/A"}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Phone</p>
              <p className="font-semibold">{patient?.whatsapp_phone?.replace("whatsapp:", "") || "N/A"}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Email</p>
              <p className="font-semibold">{patient?.email || "N/A"}</p>
            </div>
          </div>
          <div className="mt-4">
            <p className="text-sm text-gray-500">Total Medical Records</p>
            <p className="text-2xl font-bold text-indigo-600">{analyses.length}</p>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Medical Files List */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Medical Files</h3>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {analyses.map((analysis) => (
                <button
                  key={analysis.id}
                  onClick={() => setSelectedAnalysis(analysis)}
                  className={`w-full text-left p-3 rounded-lg border-2 transition-colors ${
                    selectedAnalysis?.id === analysis.id
                      ? "border-indigo-500 bg-indigo-50"
                      : "border-gray-200 hover:border-indigo-300"
                  }`}
                >
                  <p className="font-semibold text-sm truncate">{analysis.file_name}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(analysis.created_at).toLocaleDateString()}
                  </p>
                  <div className="mt-1">
                    <span
                      className={`text-xs px-2 py-1 rounded-full ${
                        analysis.risk_score >= 70
                          ? "bg-red-100 text-red-700"
                          : analysis.risk_score >= 40
                          ? "bg-yellow-100 text-yellow-700"
                          : "bg-green-100 text-green-700"
                      }`}
                    >
                      Risk: {analysis.risk_score}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Selected File Details */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow-md p-6">
            {selectedAnalysis ? (
              <>
                <h3 className="text-xl font-bold text-gray-900 mb-4">
                  {selectedAnalysis.file_name}
                </h3>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-semibold text-gray-700">Summary</p>
                    <p className="text-gray-600">{selectedAnalysis.summary}</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-700">Conditions</p>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {selectedAnalysis.conditions.map((condition, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                        >
                          {condition}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-700">Specialist</p>
                    <p className="text-gray-600">{selectedAnalysis.specialist}</p>
                  </div>
                </div>
              </>
            ) : (
              <p className="text-gray-500">Select a file to view details</p>
            )}
          </div>
        </div>

        {/* Medical Graphs */}
        {Object.keys(medicalData).length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Medical Data Trends</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Glucose Graph */}
              {medicalData.glucose && (
                <div>
                  <h4 className="font-semibold text-gray-700 mb-2">Glucose Levels</h4>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={prepareGraphData("glucose")}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <ReferenceLine y={100} stroke="green" strokeDasharray="3 3" label="Normal" />
                      <Line type="monotone" dataKey="value" stroke="#8b5cf6" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* Blood Pressure Graph */}
              {(medicalData.bp_systolic || medicalData.bp_diastolic) && (
                <div>
                  <h4 className="font-semibold text-gray-700 mb-2">Blood Pressure</h4>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={prepareGraphData("bp_systolic")}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <ReferenceLine y={120} stroke="orange" strokeDasharray="3 3" />
                      <Line type="monotone" dataKey="value" stroke="#ef4444" strokeWidth={2} name="Systolic" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
            <button
              onClick={extractMedicalData}
              className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Extract More Data Points
            </button>
          </div>
        )}

        {/* RAG-Based Comprehensive Analysis */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-gray-900">Comprehensive Analysis</h3>
            <button
              onClick={generateComprehensiveAnalysis}
              disabled={loadingAnalysis}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300"
            >
              {loadingAnalysis ? "Analyzing..." : "Generate AI Analysis"}
            </button>
          </div>
          {comprehensiveAnalysis ? (
            <div className="prose max-w-none">
              <div className="whitespace-pre-wrap text-gray-700">{comprehensiveAnalysis}</div>
            </div>
          ) : (
            <p className="text-gray-500">Click "Generate AI Analysis" to analyze all patient records together</p>
          )}
        </div>

        {/* Consultation Notes */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Consultation Notes</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Chief Complaint
              </label>
              <input
                type="text"
                value={chiefComplaint}
                onChange={(e) => setChiefComplaint(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="Patient's main concern..."
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Diagnosis
              </label>
              <textarea
                value={diagnosis}
                onChange={(e) => setDiagnosis(e.target.value)}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="Clinical diagnosis..."
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Treatment Plan
              </label>
              <textarea
                value={treatmentPlan}
                onChange={(e) => setTreatmentPlan(e.target.value)}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="Recommended treatment..."
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Additional Notes
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="Any additional observations..."
              />
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Actions</h3>
          <div className="flex flex-wrap gap-4">
            <button
              onClick={saveConsultationNotes}
              disabled={savingNotes}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300"
            >
              {savingNotes ? "Saving..." : "Save Consultation Notes"}
            </button>
            <button
              onClick={generateMedicalSummaryPDF}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Generate Medical Summary PDF
            </button>
            <button
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Generate Consultation Report PDF
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
