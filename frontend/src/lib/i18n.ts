/**
 * Internationalization (i18n) System
 * Supports English and Kannada
 */

export type Language = 'en' | 'kn';

export interface Translations {
    // Common
    common: {
        loading: string;
        error: string;
        success: string;
        cancel: string;
        save: string;
        delete: string;
        edit: string;
        close: string;
        back: string;
        next: string;
        submit: string;
        search: string;
        filter: string;
        sort: string;
        viewDetails: string;
        download: string;
        upload: string;
        share: string;
    };
    
    // Navigation
    nav: {
        home: string;
        dashboard: string;
        profile: string;
        settings: string;
        logout: string;
        signIn: string;
        signUp: string;
    };
    
    // Landing Page
    landing: {
        title: string;
        subtitle: string;
        getStarted: string;
        learnMore: string;
        features: string;
        howItWorks: string;
        pricing: string;
        contact: string;
    };
    
    // Registration
    registration: {
        title: string;
        selectRole: string;
        patient: string;
        doctor: string;
        patientDesc: string;
        doctorDesc: string;
        continueAs: string;
        alreadyHaveAccount: string;
    };
    
    // Patient Dashboard
    patient: {
        dashboard: string;
        uploadReport: string;
        myReports: string;
        analysis: string;
        riskScore: string;
        conditions: string;
        recommendations: string;
        specialist: string;
        urgency: string;
        improvementPlan: string;
        shareWithDoctor: string;
        bookAppointment: string;
        chatWithAI: string;
        noReports: string;
        uploadFirst: string;
        analyzing: string;
        analysisComplete: string;
    };
    
    // Doctor Dashboard
    doctor: {
        dashboard: string;
        patients: string;
        appointments: string;
        profile: string;
        priorityPatients: string;
        taskBoard: string;
        aiAssistant: string;
        clinicalNotes: string;
        addNote: string;
        viewRecord: string;
        grantedRecords: string;
        noPatients: string;
        waitingForAccess: string;
    };
    
    // Medical Terms
    medical: {
        diabetes: string;
        heartDisease: string;
        kidneyDisease: string;
        hypertension: string;
        cholesterol: string;
        bloodSugar: string;
        bloodPressure: string;
        lowRisk: string;
        mediumRisk: string;
        highRisk: string;
        criticalRisk: string;
    };
    
    // Appointments
    appointments: {
        book: string;
        upcoming: string;
        past: string;
        selectDate: string;
        selectTime: string;
        selectDoctor: string;
        reason: string;
        confirm: string;
        cancel: string;
        reschedule: string;
        status: {
            pending: string;
            confirmed: string;
            completed: string;
            cancelled: string;
        };
    };
    
    // Access Control
    access: {
        grantAccess: string;
        revokeAccess: string;
        accessGranted: string;
        accessRevoked: string;
        expiresIn: string;
        hours: string;
        days: string;
        selectDoctor: string;
        selectDuration: string;
    };
    
    // AI Chat
    chat: {
        askQuestion: string;
        typeMessage: string;
        send: string;
        selectPatient: string;
        aiThinking: string;
        noMessages: string;
        startConversation: string;
    };
}

const translations: Record<Language, Translations> = {
    en: {
        common: {
            loading: 'Loading...',
            error: 'Error',
            success: 'Success',
            cancel: 'Cancel',
            save: 'Save',
            delete: 'Delete',
            edit: 'Edit',
            close: 'Close',
            back: 'Back',
            next: 'Next',
            submit: 'Submit',
            search: 'Search',
            filter: 'Filter',
            sort: 'Sort',
            viewDetails: 'View Details',
            download: 'Download',
            upload: 'Upload',
            share: 'Share',
        },
        nav: {
            home: 'Home',
            dashboard: 'Dashboard',
            profile: 'Profile',
            settings: 'Settings',
            logout: 'Logout',
            signIn: 'Sign In',
            signUp: 'Sign Up',
        },
        landing: {
            title: 'AI-Powered Healthcare Platform',
            subtitle: 'Analyze medical reports with advanced AI and connect with doctors securely',
            getStarted: 'Get Started',
            learnMore: 'Learn More',
            features: 'Features',
            howItWorks: 'How It Works',
            pricing: 'Pricing',
            contact: 'Contact',
        },
        registration: {
            title: 'Join MediChain AI',
            selectRole: 'I am a...',
            patient: 'Patient',
            doctor: 'Doctor',
            patientDesc: 'Upload & analyze reports',
            doctorDesc: 'Review patient records',
            continueAs: 'Continue as',
            alreadyHaveAccount: 'Already have an account?',
        },
        patient: {
            dashboard: 'Patient Dashboard',
            uploadReport: 'Upload Medical Report',
            myReports: 'My Reports',
            analysis: 'Analysis',
            riskScore: 'Risk Score',
            conditions: 'Detected Conditions',
            recommendations: 'Recommendations',
            specialist: 'Recommended Specialist',
            urgency: 'Urgency Level',
            improvementPlan: 'Improvement Plan',
            shareWithDoctor: 'Share with Doctor',
            bookAppointment: 'Book Appointment',
            chatWithAI: 'Chat with AI',
            noReports: 'No medical reports yet',
            uploadFirst: 'Upload your first report to get started',
            analyzing: 'Analyzing your report...',
            analysisComplete: 'Analysis Complete',
        },
        doctor: {
            dashboard: 'Doctor Dashboard',
            patients: 'Patients',
            appointments: 'Appointments',
            profile: 'Profile',
            priorityPatients: 'Priority Patients',
            taskBoard: 'Task Board',
            aiAssistant: 'AI Assistant',
            clinicalNotes: 'Clinical Notes',
            addNote: 'Add Note',
            viewRecord: 'View Record',
            grantedRecords: 'Granted Records',
            noPatients: 'No patients yet',
            waitingForAccess: 'Waiting for patients to grant access',
        },
        medical: {
            diabetes: 'Diabetes',
            heartDisease: 'Heart Disease',
            kidneyDisease: 'Kidney Disease',
            hypertension: 'Hypertension',
            cholesterol: 'High Cholesterol',
            bloodSugar: 'Blood Sugar',
            bloodPressure: 'Blood Pressure',
            lowRisk: 'Low Risk',
            mediumRisk: 'Medium Risk',
            highRisk: 'High Risk',
            criticalRisk: 'Critical Risk',
        },
        appointments: {
            book: 'Book Appointment',
            upcoming: 'Upcoming',
            past: 'Past',
            selectDate: 'Select Date',
            selectTime: 'Select Time',
            selectDoctor: 'Select Doctor',
            reason: 'Reason for Visit',
            confirm: 'Confirm',
            cancel: 'Cancel',
            reschedule: 'Reschedule',
            status: {
                pending: 'Pending',
                confirmed: 'Confirmed',
                completed: 'Completed',
                cancelled: 'Cancelled',
            },
        },
        access: {
            grantAccess: 'Grant Access',
            revokeAccess: 'Revoke Access',
            accessGranted: 'Access Granted',
            accessRevoked: 'Access Revoked',
            expiresIn: 'Expires in',
            hours: 'hours',
            days: 'days',
            selectDoctor: 'Select Doctor',
            selectDuration: 'Select Duration',
        },
        chat: {
            askQuestion: 'Ask a question',
            typeMessage: 'Type your message...',
            send: 'Send',
            selectPatient: 'Select Patient',
            aiThinking: 'AI is thinking...',
            noMessages: 'No messages yet',
            startConversation: 'Start a conversation',
        },
    },
    kn: {
        common: {
            loading: 'ಲೋಡ್ ಆಗುತ್ತಿದೆ...',
            error: 'ದೋಷ',
            success: 'ಯಶಸ್ವಿ',
            cancel: 'ರದ್ದುಮಾಡಿ',
            save: 'ಉಳಿಸಿ',
            delete: 'ಅಳಿಸಿ',
            edit: 'ಸಂಪಾದಿಸಿ',
            close: 'ಮುಚ್ಚಿ',
            back: 'ಹಿಂದೆ',
            next: 'ಮುಂದೆ',
            submit: 'ಸಲ್ಲಿಸಿ',
            search: 'ಹುಡುಕಿ',
            filter: 'ಫಿಲ್ಟರ್',
            sort: 'ವಿಂಗಡಿಸಿ',
            viewDetails: 'ವಿವರಗಳನ್ನು ನೋಡಿ',
            download: 'ಡೌನ್‌ಲೋಡ್',
            upload: 'ಅಪ್‌ಲೋಡ್',
            share: 'ಹಂಚಿಕೊಳ್ಳಿ',
        },
        nav: {
            home: 'ಮುಖಪುಟ',
            dashboard: 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',
            profile: 'ಪ್ರೊಫೈಲ್',
            settings: 'ಸೆಟ್ಟಿಂಗ್‌ಗಳು',
            logout: 'ಲಾಗ್ ಔಟ್',
            signIn: 'ಸೈನ್ ಇನ್',
            signUp: 'ಸೈನ್ ಅಪ್',
        },
        landing: {
            title: 'AI-ಚಾಲಿತ ಆರೋಗ್ಯ ವೇದಿಕೆ',
            subtitle: 'ಸುಧಾರಿತ AI ಯೊಂದಿಗೆ ವೈದ್ಯಕೀಯ ವರದಿಗಳನ್ನು ವಿಶ್ಲೇಷಿಸಿ ಮತ್ತು ವೈದ್ಯರೊಂದಿಗೆ ಸುರಕ್ಷಿತವಾಗಿ ಸಂಪರ್ಕಿಸಿ',
            getStarted: 'ಪ್ರಾರಂಭಿಸಿ',
            learnMore: 'ಇನ್ನಷ್ಟು ತಿಳಿಯಿರಿ',
            features: 'ವೈಶಿಷ್ಟ್ಯಗಳು',
            howItWorks: 'ಇದು ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ',
            pricing: 'ಬೆಲೆ',
            contact: 'ಸಂಪರ್ಕಿಸಿ',
        },
        registration: {
            title: 'ಮೆಡಿಚೈನ್ AI ಗೆ ಸೇರಿ',
            selectRole: 'ನಾನು...',
            patient: 'ರೋಗಿ',
            doctor: 'ವೈದ್ಯರು',
            patientDesc: 'ವರದಿಗಳನ್ನು ಅಪ್‌ಲೋಡ್ ಮತ್ತು ವಿಶ್ಲೇಷಿಸಿ',
            doctorDesc: 'ರೋಗಿಗಳ ದಾಖಲೆಗಳನ್ನು ಪರಿಶೀಲಿಸಿ',
            continueAs: 'ಮುಂದುವರಿಸಿ',
            alreadyHaveAccount: 'ಈಗಾಗಲೇ ಖಾತೆ ಹೊಂದಿದ್ದೀರಾ?',
        },
        patient: {
            dashboard: 'ರೋಗಿ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',
            uploadReport: 'ವೈದ್ಯಕೀಯ ವರದಿ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ',
            myReports: 'ನನ್ನ ವರದಿಗಳು',
            analysis: 'ವಿಶ್ಲೇಷಣೆ',
            riskScore: 'ಅಪಾಯ ಸ್ಕೋರ್',
            conditions: 'ಪತ್ತೆಯಾದ ಪರಿಸ್ಥಿತಿಗಳು',
            recommendations: 'ಶಿಫಾರಸುಗಳು',
            specialist: 'ಶಿಫಾರಸು ಮಾಡಿದ ತಜ್ಞರು',
            urgency: 'ತುರ್ತು ಮಟ್ಟ',
            improvementPlan: 'ಸುಧಾರಣೆ ಯೋಜನೆ',
            shareWithDoctor: 'ವೈದ್ಯರೊಂದಿಗೆ ಹಂಚಿಕೊಳ್ಳಿ',
            bookAppointment: 'ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್ ಬುಕ್ ಮಾಡಿ',
            chatWithAI: 'AI ಯೊಂದಿಗೆ ಚಾಟ್ ಮಾಡಿ',
            noReports: 'ಇನ್ನೂ ಯಾವುದೇ ವೈದ್ಯಕೀಯ ವರದಿಗಳಿಲ್ಲ',
            uploadFirst: 'ಪ್ರಾರಂಭಿಸಲು ನಿಮ್ಮ ಮೊದಲ ವರದಿಯನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ',
            analyzing: 'ನಿಮ್ಮ ವರದಿಯನ್ನು ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...',
            analysisComplete: 'ವಿಶ್ಲೇಷಣೆ ಪೂರ್ಣಗೊಂಡಿದೆ',
        },
        doctor: {
            dashboard: 'ವೈದ್ಯರ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',
            patients: 'ರೋಗಿಗಳು',
            appointments: 'ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್‌ಗಳು',
            profile: 'ಪ್ರೊಫೈಲ್',
            priorityPatients: 'ಆದ್ಯತೆಯ ರೋಗಿಗಳು',
            taskBoard: 'ಕಾರ್ಯ ಬೋರ್ಡ್',
            aiAssistant: 'AI ಸಹಾಯಕ',
            clinicalNotes: 'ಕ್ಲಿನಿಕಲ್ ಟಿಪ್ಪಣಿಗಳು',
            addNote: 'ಟಿಪ್ಪಣಿ ಸೇರಿಸಿ',
            viewRecord: 'ದಾಖಲೆ ನೋಡಿ',
            grantedRecords: 'ನೀಡಿದ ದಾಖಲೆಗಳು',
            noPatients: 'ಇನ್ನೂ ಯಾವುದೇ ರೋಗಿಗಳಿಲ್ಲ',
            waitingForAccess: 'ರೋಗಿಗಳು ಪ್ರವೇಶ ನೀಡಲು ಕಾಯುತ್ತಿದೆ',
        },
        medical: {
            diabetes: 'ಮಧುಮೇಹ',
            heartDisease: 'ಹೃದಯ ರೋಗ',
            kidneyDisease: 'ಮೂತ್ರಪಿಂಡ ರೋಗ',
            hypertension: 'ಅಧಿಕ ರಕ್ತದೊತ್ತಡ',
            cholesterol: 'ಹೆಚ್ಚಿನ ಕೊಲೆಸ್ಟ್ರಾಲ್',
            bloodSugar: 'ರಕ್ತದಲ್ಲಿನ ಸಕ್ಕರೆ',
            bloodPressure: 'ರಕ್ತದೊತ್ತಡ',
            lowRisk: 'ಕಡಿಮೆ ಅಪಾಯ',
            mediumRisk: 'ಮಧ್ಯಮ ಅಪಾಯ',
            highRisk: 'ಹೆಚ್ಚಿನ ಅಪಾಯ',
            criticalRisk: 'ಗಂಭೀರ ಅಪಾಯ',
        },
        appointments: {
            book: 'ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್ ಬುಕ್ ಮಾಡಿ',
            upcoming: 'ಮುಂಬರುವ',
            past: 'ಹಿಂದಿನ',
            selectDate: 'ದಿನಾಂಕ ಆಯ್ಕೆಮಾಡಿ',
            selectTime: 'ಸಮಯ ಆಯ್ಕೆಮಾಡಿ',
            selectDoctor: 'ವೈದ್ಯರನ್ನು ಆಯ್ಕೆಮಾಡಿ',
            reason: 'ಭೇಟಿಯ ಕಾರಣ',
            confirm: 'ದೃಢೀಕರಿಸಿ',
            cancel: 'ರದ್ದುಮಾಡಿ',
            reschedule: 'ಮರುಹೊಂದಿಸಿ',
            status: {
                pending: 'ಬಾಕಿ ಉಳಿದಿದೆ',
                confirmed: 'ದೃಢೀಕರಿಸಲಾಗಿದೆ',
                completed: 'ಪೂರ್ಣಗೊಂಡಿದೆ',
                cancelled: 'ರದ್ದುಗೊಳಿಸಲಾಗಿದೆ',
            },
        },
        access: {
            grantAccess: 'ಪ್ರವೇಶ ನೀಡಿ',
            revokeAccess: 'ಪ್ರವೇಶ ರದ್ದುಮಾಡಿ',
            accessGranted: 'ಪ್ರವೇಶ ನೀಡಲಾಗಿದೆ',
            accessRevoked: 'ಪ್ರವೇಶ ರದ್ದುಗೊಳಿಸಲಾಗಿದೆ',
            expiresIn: 'ಮುಕ್ತಾಯಗೊಳ್ಳುತ್ತದೆ',
            hours: 'ಗಂಟೆಗಳು',
            days: 'ದಿನಗಳು',
            selectDoctor: 'ವೈದ್ಯರನ್ನು ಆಯ್ಕೆಮಾಡಿ',
            selectDuration: 'ಅವಧಿ ಆಯ್ಕೆಮಾಡಿ',
        },
        chat: {
            askQuestion: 'ಪ್ರಶ್ನೆ ಕೇಳಿ',
            typeMessage: 'ನಿಮ್ಮ ಸಂದೇಶವನ್ನು ಟೈಪ್ ಮಾಡಿ...',
            send: 'ಕಳುಹಿಸಿ',
            selectPatient: 'ರೋಗಿಯನ್ನು ಆಯ್ಕೆಮಾಡಿ',
            aiThinking: 'AI ಯೋಚಿಸುತ್ತಿದೆ...',
            noMessages: 'ಇನ್ನೂ ಯಾವುದೇ ಸಂದೇಶಗಳಿಲ್ಲ',
            startConversation: 'ಸಂಭಾಷಣೆ ಪ್ರಾರಂಭಿಸಿ',
        },
    },
};

// Language context
export function getTranslations(lang: Language): Translations {
    return translations[lang] || translations.en;
}

// Helper function to get nested translation
export function t(lang: Language, key: string): string {
    const trans = getTranslations(lang);
    const keys = key.split('.');
    let value: any = trans;
    
    for (const k of keys) {
        value = value?.[k];
    }
    
    return value || key;
}
