'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { Language, getTranslations, Translations } from '@/lib/i18n';

interface LanguageContextType {
    language: Language;
    setLanguage: (lang: Language) => void;
    t: (key: string) => string;
    translations: Translations;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
    const [language, setLanguageState] = useState<Language>('en');
    const [translations, setTranslations] = useState<Translations>(getTranslations('en'));

    // Load language preference from localStorage on mount
    useEffect(() => {
        const savedLang = localStorage.getItem('medichain-language') as Language;
        if (savedLang === 'en' || savedLang === 'kn') {
            setLanguageState(savedLang);
            setTranslations(getTranslations(savedLang));
        }
    }, []);

    const setLanguage = (lang: Language) => {
        setLanguageState(lang);
        setTranslations(getTranslations(lang));
        localStorage.setItem('medichain-language', lang);
    };

    const t = (key: string): string => {
        const keys = key.split('.');
        let value: any = translations;
        
        for (const k of keys) {
            value = value?.[k];
        }
        
        return value || key;
    };

    return (
        <LanguageContext.Provider value={{ language, setLanguage, t, translations }}>
            {children}
        </LanguageContext.Provider>
    );
}

export function useLanguage() {
    const context = useContext(LanguageContext);
    if (!context) {
        throw new Error('useLanguage must be used within a LanguageProvider');
    }
    return context;
}
