import { createI18n } from 'vue-i18n'
import zhTW from './zh-TW'
import en from './en'

const messages = {
  'zh-TW': zhTW,
  'en': en
}

export const i18n = createI18n({
  legacy: false,
  locale: 'zh-TW', // 默認使用繁體中文
  fallbackLocale: 'en',
  messages
})

export default i18n
