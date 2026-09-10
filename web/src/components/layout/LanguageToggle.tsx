import { useTranslation } from 'react-i18next';
import { setLanguage } from '@/i18n';
import { cn } from '@/lib/cn';

export function LanguageToggle() {
  const { i18n } = useTranslation();
  const lang = i18n.language.startsWith('en') ? 'en' : 'fr';
  return (
    <div className="flex overflow-hidden rounded-lg border border-white/10 text-xs font-semibold">
      {(['fr', 'en'] as const).map((l) => (
        <button
          key={l}
          onClick={() => setLanguage(l)}
          className={cn(
            'px-2.5 py-1.5 uppercase transition-colors',
            lang === l ? 'bg-ci-orange text-white' : 'text-sand/60 hover:text-white',
          )}
        >
          {l}
        </button>
      ))}
    </div>
  );
}
