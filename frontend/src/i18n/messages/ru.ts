import type { Messages } from './en'

/** 1 товар, 2 товара, 5 товаров. */
function plural(count: number, one: string, few: string, many: string): string {
  const mod10 = count % 10
  const mod100 = count % 100
  if (mod10 === 1 && mod100 !== 11) return one
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return few
  return many
}

/** Russian interface texts. Keys must match en.ts. */
export const ru: Messages = {
  language: {
    label: 'Язык',
  },
  nav: {
    main: 'Главное меню',
    shop: 'Магазин',
    made: 'Как мы делаем',
    inspiration: 'Идеи',
    ingredients: 'Состав',
    care: 'Уход',
    custom: 'На заказ',
    contact: 'Контакты',
  },
  header: {
    search: 'Поиск',
    cart: (count: number) => `Корзина, ${count} ${plural(count, 'товар', 'товара', 'товаров')}`,
    openMenu: 'Открыть меню',
    closeMenu: 'Закрыть меню',
  },
  footer: {
    shop: 'Магазин',
    winter: 'Зимняя коллекция',
    single: 'Отдельные свечи',
    sets: 'Наборы свечей',
    help: 'Помощь',
    made: 'Как мы делаем свечи',
    decorate: 'Декор со свечами',
    ingredients: 'Из чего сделаны наши свечи',
    care: 'Уход за свечами и советы',
    custom: 'Индивидуальные заказы',
    contact: 'Контакты',
    sayHello: 'Напишите нам',
  },
  status: {
    loading: 'Загрузка…',
    loadFailed: 'Не удалось загрузить магазин',
    checkConnection: 'Проверьте подключение к интернету и попробуйте ещё раз.',
    tryAgain: 'Попробовать ещё раз',
    somethingWrong: 'Что-то пошло не так.',
    notFoundTitle: 'Такой страницы нет',
    notFoundText: 'Возможно, ссылка устарела или в адресе опечатка.',
    productNotFoundTitle: 'Мы не нашли эту свечу',
    productNotFoundText: 'Возможно, её переименовали или убрали из магазина.',
    browse: 'Смотреть коллекцию',
  },
  productType: {
    candle: 'Свеча',
    set: 'Набор свечей',
    collection: 'Коллекция',
  },
  category: {
    candle: 'Отдельные свечи',
    set: 'Наборы свечей',
    collection: 'Коллекции',
  },
  cart: {
    add: 'В корзину',
    added: 'Добавлено ✓',
    addedToCart: 'Добавлено в корзину',
    soldOut: 'Нет в наличии',
    soldOutBackSoon: 'Нет в наличии — скоро будет',
    onlyLeft: (count: number) => `Осталось всего ${count} шт.`,
    decrease: 'Уменьшить количество',
    increase: 'Увеличить количество',
    quantity: (count: number) => `Количество: ${count}`,
  },
  home: {
    pageTitle: (studio: string) => `${studio} — расписные свечи и наборы свечей`,
    viewAll: 'Смотреть все',
    empty: 'Новые свечи уже в пути — загляните чуть позже.',
    trainLabel: 'Свечи коллекции',
    showSlide: (title: string) => `Показать: ${title}`,
    madeEyebrow: 'Как мы делаем свечи',
    careLink: 'Уход за свечами и советы',
    beforeAlt: 'Нерасписанное гипсовое изделие',
    afterAlt: 'То же изделие после ручной росписи',
    playVideo: (title: string) => `Смотреть видео: ${title} (откроется в новой вкладке)`,
    shopByType: 'Выбрать по типу',
    stylingIdeas: 'Идеи декора со свечами',
    singleTile: 'Отдельные свечи',
    setsTile: 'Наборы свечей',
    emailLabel: 'Адрес электронной почты',
    emailPlaceholder: 'you@example.com',
    subscribe: 'Подписаться',
    subscribed: 'Спасибо! Подписка на рассылку скоро откроется.',
  },
  product: {
    breadcrumb: 'Навигация',
    home: 'Главная',
    burnTime: 'Время горения',
    size: 'Размер',
    shipsIn: 'Отправка',
    details: 'Подробности',
    care: 'Уход за свечой',
    careGuide: 'Полное руководство по уходу',
    shipping: 'Доставка и возврат',
    scent: 'Аромат:',
    includes: 'В наборе',
    makingOfKicker: 'Как она создаётся',
    makingOfSteps: ['Отливается из гипса', 'Расписывается вручную', 'Заливается воском'],
    glowingAlt: (title: string) => `${title} с горящим пламенем`,
    related: 'Вам может понравиться',
    backToCollection: 'Вернуться к коллекции',
    uniqueChip: 'Ручная роспись · каждая уникальна',
    mainView: 'Основной вид',
    lit: 'Зажжена',
    litAlt: (title: string) => `${title}, зажжённая`,
    photoAlt: (title: string, label: string) => `${title}: ${label}`,
    views: 'Виды товара',
    viewer: 'просмотр товара',
    hintDrag: 'Потяните, чтобы повернуть · Нажмите для увеличения',
    hintClick: 'Нажмите для увеличения',
    previousView: 'Предыдущий вид',
    nextView: 'Следующий вид',
    viewAlt: (title: string, label: string) => `${title} — ${label}`,
  },
  sectionNav: {
    onThisPage: 'На этой странице',
  },
  care: {
    pageTitle: 'Уход за свечами и советы',
    description:
      'Как зажигать, беречь и снова использовать расписные свечи: первый розжиг, подрезка фитиля, где ставить, уход и частые вопросы.',
    sectionTips: 'Советы',
    sectionCare: 'Уход',
    sectionFragrance: 'Аромат',
    sectionFaq: 'Вопросы',
    heroSceneLabel: 'Расписные свечи горят на деревянном столе в тёмной тёплой комнате',
    shelfSceneLabel: 'Расписные свечи-шары на тёплой деревянной полке',
  },
  ingredients: {
    description:
      'Соевый воск, гипс ручного литья, фитили, аромат и цвет — всё, из чего сделаны наши свечи ручной работы.',
    heroSceneLabel: 'Нерасписанная гипсовая основа с рельефными листьями на тёплом льне',
    navLabel: 'Составляющие на этой странице',
    palette: (title: string) => `${title}: палитра`,
  },
  decorate: {
    pageTitle: 'Декор со свечами',
    description:
      'Идеи, как украсить дом свечами и гипсовым декором ручного литья, комната за комнатой, и галерея сцен при свечах.',
    rooms: 'Идеи декора по комнатам',
    openRoom: (title: string, text: string) => `${title}: ${text} Открыть фото.`,
    galleryLabel: (count: number) =>
      `Галерея идей, ${count} фото. Листайте стрелками влево и вправо.`,
    openPicture: (index: number, count: number, caption: string) =>
      `Открыть фото ${index} из ${count}: ${caption}`,
    previousPictures: 'Предыдущие фото',
    nextPictures: 'Следующие фото',
    viewer: 'Просмотр фото',
    closeViewer: 'Закрыть просмотр фото',
    previousPicture: 'Предыдущее фото',
    nextPicture: 'Следующее фото',
    inThisPicture: 'На этом фото:',
  },
}
