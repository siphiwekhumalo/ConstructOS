import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

const isBrowser = typeof window !== 'undefined';

const getStoredLanguage = (): string | null => {
  if (!isBrowser) return null;
  try {
    return localStorage.getItem('constructos_language');
  } catch {
    return null;
  }
};

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    supportedLngs: ['en', 'af', 'zu'],
    
    debug: false,
    
    interpolation: {
      escapeValue: false,
    },
    
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },
    
    detection: {
      order: isBrowser ? ['localStorage', 'navigator', 'htmlTag'] : ['navigator'],
      lookupLocalStorage: 'constructos_language',
      caches: isBrowser ? ['localStorage'] : [],
    },
    
    ns: ['translation'],
    defaultNS: 'translation',
    
    react: {
      useSuspense: true,
    },
  });

export const languages = [
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'af', name: 'Afrikaans', flag: '🇿🇦' },
  { code: 'zu', name: 'isiZulu', flag: '🇿🇦' },
];

export const changeLanguage = (languageCode: string) => {
  i18n.changeLanguage(languageCode);
  if (isBrowser) {
    try {
      localStorage.setItem('constructos_language', languageCode);
    } catch {
    }
  }
};

export const getCurrentLanguage = () => {
  return i18n.language || getStoredLanguage() || 'en';
};

export default i18n;
