import { en } from './en';
import { ua } from './ua';

import { createContext } from '@lit/context';

export const languages = {
  en,
  ua,
};

export type Language = keyof typeof languages;

export let currentLanguage: Language =
  (localStorage.getItem('lang') as Language | null) ?? 'en';

export const setLanguage = (lang: Language) => {
  currentLanguage = lang;
  localStorage.setItem('lang', lang);
  location.reload();
};

export type Translations = (typeof languages)[Language];

export const t = new Proxy<Translations>(languages[currentLanguage], {
  get(target, key: string) {
    return target[key as keyof Translations] || key; // Return the key if translation is missing
  },
});

export const localeContext = createContext<Translations>;
