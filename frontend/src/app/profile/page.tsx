"use client";

import { useState, useEffect } from "react";
import { usePrivy } from "@privy-io/react-auth";
import { useRouter } from "next/navigation";
import { truncateAddress, copyToClipboard } from "@/utils/formatAddress";

export default function ProfilePage() {
  const { user, authenticated } = usePrivy();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [profile, setProfile] = useState<any>(null);
  const [role, setRole] = useState<"patient" | "doctor">("patient");
  
  // Form state
  const [fullName, setFullName] = useState("");
  const [whatsappPhone, setWhatsappPhone] = useState("");
  const [email, setEmail] = useState("");
  const [dateOfBirth, setDateOfBirth] = useState("");
  const [gender, setGender] = useState("");
  const [bloodType, setBloodType] = useState("");
  const [allergies, setAllergies] = useState("");
  const [emergencyContact, setEmergencyContact] = useState("");
  const [emergencyContactPhone, setEmergencyContactPhone] = useState("");
  const [specialty, setSpecialty] = useState("");
  const [bio, setBio] = useState("");
  const [copiedAddress, setCopiedAddress] = useState(false);

  useEffect(() => {
    if (!authenticated) {
      router.push("/");
      return;
    }

    // Get role from localStorage
    const storedRole = localStorage.getItem("userRole") as "patient" | "doctor";
    if (storedRole) {
      setRole(storedRole);
    }

    loadProfile();
  }, [authenticated, user]);

  const loadProfile = async () => {
    // Get wallet address from Privy user
    const walletAddress = user?.wallet?.address || user?.id;
    if (!walletAddress) {
      console.error("No wallet address or user ID found");
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const currentRole = localStorage.getItem("userRole") || "patient";
      
      const endpoint = currentRole === "patient" 
        ? `/api/profiles/patient/${walletAddress}`
        : `/api/profiles/doctor/${walletAddress}`;

      console.log("Loading profile from:", `${process.env.NEXT_PUBLIC_API_URL}${endpoint}`);
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`);
      
      if (!response.ok) {
        console.error("Failed to load profile:", response.status, response.statusText);
        const errorText = await response.text();
        console.error("Error response:", errorText);
        setLoading(false);
        return;
      }
      
      const data = await response.json();

      console.log("Profile data received:", data);

      if (data.exists) {
        setProfile(data);
        setFullName(data.full_name || data.name || "");
        setWhatsappPhone(data.whatsapp_phone?.replace("whatsapp:", "") || "");
        setEmail(data.email || "");
        setDateOfBirth(data.date_of_birth || "");
        setGender(data.gender || "");
        setBloodType(data.blood_type || "");
        setAllergies(data.allergies || "");
        setEmergencyContact(data.emergency_contact || "");
        setEmergencyContactPhone(data.emergency_contact_phone?.replace("whatsapp:", "") || "");
        setSpecialty(data.specialty || "");
        setBio(data.bio || "");
      }
    } catch (error) {
      console.error("Error loading profile:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    // Get wallet address from Privy user
    const walletAddress = user?.wallet?.address || user?.id;
    if (!walletAddress) {
      alert("Unable to identify user. Please try logging in again.");
      return;
    }

    if (!fullName) {
      alert("Please enter your full name");
      return;
    }

    try {
      setSaving(true);
      
      const endpoint = role === "patient"
        ? `/api/profiles/patient/${walletAddress}`
        : `/api/profiles/doctor/${walletAddress}`;

      const body = role === "patient"
        ? {
            full_name: fullName,
            whatsapp_phone: whatsappPhone,
            email: email,
            date_of_birth: dateOfBirth,
            gender: gender,
            blood_type: bloodType,
            allergies: allergies,
            emergency_contact: emergencyContact,
            emergency_contact_phone: emergencyContactPhone,
          }
        : {
            name: fullName,
            specialty: specialty,
            whatsapp_phone: whatsappPhone,
            email: email,
            bio: bio,
          };

      console.log("Saving profile to:", `${process.env.NEXT_PUBLIC_API_URL}${endpoint}`);
      console.log("Profile data:", body);

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const responseData = await response.json();
      console.log("Save response:", responseData);

      if (response.ok) {
        alert("Profile saved successfully!");
        await loadProfile();
      } else {
        console.error("Failed to save profile:", responseData);
        alert(`Failed to save profile: ${responseData.detail || "Unknown error"}`);
      }
    } catch (error) {
      console.error("Error saving profile:", error);
      alert(`Error saving profile: ${error instanceof Error ? error.message : "Unknown error"}`);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold text-gray-900">
              {role === "patient" ? "Patient Profile" : "Doctor Profile"}
            </h1>
            <span className="px-4 py-2 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium">
              {role.charAt(0).toUpperCase() + role.slice(1)}
            </span>
          </div>

          <div className="space-y-6">
            {/* Full Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Name *
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Enter your full name"
              />
            </div>

            {/* WhatsApp Phone */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                WhatsApp Phone Number
              </label>
              <input
                type="tel"
                value={whatsappPhone}
                onChange={(e) => setWhatsappPhone(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="+1234567890"
              />
              <p className="mt-1 text-sm text-gray-500">
                Include country code (e.g., +1 for US, +91 for India)
              </p>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="your@email.com"
              />
            </div>

            {/* Patient-specific fields */}
            {role === "patient" && (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Date of Birth
                    </label>
                    <input
                      type="date"
                      value={dateOfBirth}
                      onChange={(e) => setDateOfBirth(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Gender
                    </label>
                    <select
                      value={gender}
                      onChange={(e) => setGender(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    >
                      <option value="">Select gender</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="other">Other</option>
                      <option value="prefer_not_to_say">Prefer not to say</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Blood Type
                  </label>
                  <select
                    value={bloodType}
                    onChange={(e) => setBloodType(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  >
                    <option value="">Select blood type</option>
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Known Allergies
                  </label>
                  <textarea
                    value={allergies}
                    onChange={(e) => setAllergies(e.target.value)}
                    rows={3}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="List any known allergies (medications, food, etc.)"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Emergency Contact Name
                    </label>
                    <input
                      type="text"
                      value={emergencyContact}
                      onChange={(e) => setEmergencyContact(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      placeholder="Emergency contact person"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Emergency Contact Phone
                    </label>
                    <input
                      type="tel"
                      value={emergencyContactPhone}
                      onChange={(e) => setEmergencyContactPhone(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      placeholder="+1234567890"
                    />
                  </div>
                </div>
              </>
            )}

            {/* Doctor-specific fields */}
            {role === "doctor" && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Specialty
                  </label>
                  <input
                    type="text"
                    value={specialty}
                    onChange={(e) => setSpecialty(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="e.g., Cardiology, General Practice"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Bio
                  </label>
                  <textarea
                    value={bio}
                    onChange={(e) => setBio(e.target.value)}
                    rows={4}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="Tell patients about yourself..."
                  />
                </div>
              </>
            )}

            {/* Save Button */}
            <div className="flex gap-4 pt-4">
              <button
                onClick={handleSave}
                disabled={saving || !fullName}
                className="flex-1 bg-indigo-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                {saving ? "Saving..." : "Save Profile"}
              </button>
              
              <button
                onClick={() => router.back()}
                className="px-6 py-3 border border-gray-300 rounded-lg font-medium hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>

          {/* Wallet Address */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 mb-1">Wallet Address</p>
                <p className="font-mono text-sm text-gray-900">
                  {truncateAddress(user?.wallet?.address || user?.id, 10, 8)}
                </p>
              </div>
              <button
                onClick={async () => {
                  await copyToClipboard(user?.wallet?.address || user?.id || '');
                  setCopiedAddress(true);
                  setTimeout(() => setCopiedAddress(false), 2000);
                }}
                className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                {copiedAddress ? (
                  <>
                    <svg className="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-sm text-green-600">Copied!</span>
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    <span className="text-sm text-gray-600">Copy</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
