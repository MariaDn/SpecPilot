import { en } from './en';
import { ua } from './ua';

export const languages = {
  en,
  ua,
};

export type Language = keyof typeof languages;

let currentLanguage: Language = 'en';

export const setLanguage = (lang: Language) => {
  currentLanguage = lang;
};

export type Translations = typeof languages[Language];

export const t = new Proxy<Translations>(languages[currentLanguage], {
  get(target, key: string) {
    return target[key as keyof Translations] || key; // Return the key if translation is missing
  }
});