/**
 * Recover Access Button Component
 * 
 * Professional, visually compelling recovery interface
 * Designed to inspire confidence in the recovery process
 */

'use client';

import { useState } from 'react';
import { usePrivy } from '@privy-io/react-auth';

export function RecoverAccessButton() {
  const { login } = usePrivy();
  const [showModal, setShowModal] = useState(false);
  const [step, setStep] = useState(0);

  const recoverySteps = [
    {
      icon: '🔐',
      title: 'Login with the same method',
      description: 'Use Google, email, etc.',
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
    },
    {
      icon: '🔑',
      title: 'Privy recovers your wallet',
      description: 'Keys automatically restored',
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
    },
    {
      icon: '✓',
      title: 'Access restored!',
      description: 'View your encrypted reports',
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
    },
  ];

  return (
    <>
      {/* Trigger Button */}
      <button
        onClick={() => setShowModal(true)}
        className="group relative inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200 overflow-hidden"
      >
        {/* Animated background */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-700 to-indigo-700 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
        
        {/* Content */}
        <span className="relative flex items-center gap-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          Recover Your Access
        </span>
      </button>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-auto animate-scale-in">
            {/* Header */}
            <div className="relative bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 p-8 text-white">
              {/* Close button */}
              <button
                onClick={() => {
                  setShowModal(false);
                  setStep(0);
                }}
                className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-full bg-white/20 hover:bg-white/30 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>

              {/* Title */}
              <div className="flex items-center gap-3 mb-2">
                <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center text-2xl">
                  🔐
                </div>
                <h2 className="text-2xl font-bold">Recover Your Access</h2>
              </div>
              <p className="text-blue-100 text-sm">
                Get back into your encrypted medical reports
              </p>

              {/* Decorative elements */}
              <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
              <div className="absolute bottom-0 left-0 w-48 h-48 bg-purple-500/10 rounded-full blur-2xl translate-y-1/2 -translate-x-1/2" />
            </div>

            {/* Content */}
            <div className="p-8">
              {/* Good News Banner */}
              <div className="mb-8 p-4 bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-bold text-green-900 mb-1">Good News!</h3>
                    <p className="text-sm text-green-800">
                      Your encrypted reports are safe and recoverable.
                    </p>
                  </div>
                </div>
              </div>

              {/* Recovery Steps */}
              <div className="space-y-4 mb-8">
                {recoverySteps.map((stepData, index) => {
                  const isActive = step === index;
                  const isCompleted = step > index;

                  return (
                    <div
                      key={index}
                      className={`relative p-5 rounded-xl border-2 transition-all duration-300 cursor-pointer ${
                        isActive
                          ? `${stepData.bgColor} ${stepData.borderColor} shadow-lg scale-105`
                          : isCompleted
                          ? 'bg-gray-50 border-gray-200 opacity-75'
                          : 'bg-white border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => setStep(index)}
                    >
                      <div className="flex items-center gap-4">
                        {/* Step number/icon */}
                        <div
                          className={`flex-shrink-0 w-14 h-14 rounded-xl flex items-center justify-center text-2xl font-bold transition-all duration-300 ${
                            isActive || isCompleted
                              ? `bg-gradient-to-br ${stepData.color} text-white shadow-lg`
                              : 'bg-gray-100 text-gray-400'
                          }`}
                        >
                          {isCompleted ? '✓' : stepData.icon}
                        </div>

                        {/* Content */}
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                              Step {index + 1}
                            </span>
                            {isCompleted && (
                              <span className="text-xs bg-green-500 text-white px-2 py-0.5 rounded-full">
                                Complete
                              </span>
                            )}
                          </div>
                          <h4 className="font-bold text-gray-900 mb-1">
                            {stepData.title}
                          </h4>
                          <p className="text-sm text-gray-600">
                            {stepData.description}
                          </p>
                        </div>

                        {/* Arrow indicator */}
                        {isActive && (
                          <div className="flex-shrink-0">
                            <svg className="w-6 h-6 text-gray-400 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                            </svg>
                          </div>
                        )}
                      </div>

                      {/* Progress bar */}
                      {isActive && (
                        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-200 rounded-b-xl overflow-hidden">
                          <div
                            className={`h-full bg-gradient-to-r ${stepData.color} animate-progress`}
                          />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Security Info */}
              <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-xl">
                <div className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div className="text-sm text-blue-900">
                    <p className="font-semibold mb-1">How it works:</p>
                    <p className="text-blue-800">
                      Privy uses advanced cryptography to securely store your wallet keys. 
                      When you login with the same method, your keys are automatically recovered 
                      and your encrypted reports become accessible again.
                    </p>
                  </div>
                </div>
              </div>

              {/* Action Button */}
              <button
                onClick={() => {
                  setShowModal(false);
                  login();
                }}
                className="w-full group relative px-8 py-4 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white rounded-xl font-bold text-lg shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all duration-200 overflow-hidden"
              >
                {/* Animated shine effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                
                {/* Content */}
                <span className="relative flex items-center justify-center gap-2">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                  </svg>
                  Recover My Access Now
                  <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </span>
              </button>

              {/* Footer note */}
              <p className="mt-4 text-center text-xs text-gray-500">
                No passwords required • Secure by design • Your data stays encrypted
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Add animations to global styles */}
      <style jsx global>{`
        @keyframes fade-in {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes scale-in {
          from {
            opacity: 0;
            transform: scale(0.95);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }

        @keyframes progress {
          from {
            transform: translateX(-100%);
          }
          to {
            transform: translateX(100%);
          }
        }

        .animate-fade-in {
          animation: fade-in 0.2s ease-out;
        }

        .animate-scale-in {
          animation: scale-in 0.3s ease-out;
        }

        .animate-progress {
          animation: progress 2s ease-in-out infinite;
        }
      `}</style>
    </>
  );
}
