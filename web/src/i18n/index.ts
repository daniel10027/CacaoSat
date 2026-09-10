import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import fr from './fr.json';
import en from './en.json';

const stored =
  typeof localStorage !== 'undefined' ? localStorage.getItem('cacaosat.lang') : null;

void i18n.use(initReactI18next).init({
  resources: {
    fr: { translation: fr },
    en: { translation: en },
  },
  lng: stored ?? 'fr',
  fallbackLng: 'fr',
  interpolation: { escapeValue: false },
});

export function setLanguage(lang: 'fr' | 'en'): void {
  void i18n.changeLanguage(lang);
  localStorage.setItem('cacaosat.lang', lang);
}

export default i18n;
