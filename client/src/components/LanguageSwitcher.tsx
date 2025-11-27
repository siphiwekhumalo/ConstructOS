import { useTranslation } from 'react-i18next';
import { languages, changeLanguage, getCurrentLanguage } from '@/lib/i18n';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Globe } from 'lucide-react';

export function LanguageSwitcher() {
  const { t } = useTranslation();
  const currentLanguage = getCurrentLanguage();

  return (
    <div className="flex items-center gap-2" data-testid="language-switcher">
      <Globe className="h-4 w-4 text-muted-foreground" />
      <Select
        value={currentLanguage}
        onValueChange={changeLanguage}
      >
        <SelectTrigger 
          className="w-[140px]" 
          data-testid="language-select-trigger"
        >
          <SelectValue placeholder={t('common.selectLanguage')} />
        </SelectTrigger>
        <SelectContent>
          {languages.map((lang) => (
            <SelectItem
              key={lang.code}
              value={lang.code}
              data-testid={`language-option-${lang.code}`}
            >
              <span className="flex items-center gap-2">
                <span>{lang.flag}</span>
                <span>{lang.name}</span>
              </span>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

export function LanguageSwitcherCompact() {
  const currentLanguage = getCurrentLanguage();
  const currentLang = languages.find((l) => l.code === currentLanguage);

  return (
    <Select
      value={currentLanguage}
      onValueChange={changeLanguage}
    >
      <SelectTrigger 
        className="w-auto gap-2 border-none bg-transparent px-2" 
        data-testid="language-select-compact"
      >
        <Globe className="h-4 w-4" />
        <span className="hidden sm:inline">{currentLang?.flag}</span>
      </SelectTrigger>
      <SelectContent align="end">
        {languages.map((lang) => (
          <SelectItem
            key={lang.code}
            value={lang.code}
            data-testid={`language-option-compact-${lang.code}`}
          >
            <span className="flex items-center gap-2">
              <span>{lang.flag}</span>
              <span>{lang.name}</span>
            </span>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
