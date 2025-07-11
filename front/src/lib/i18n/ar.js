// lib/i18n/translations/ar.js
export const arTranslations = {
  app: {
    name: 'منصة المزاد'
  },
  
  common: {
    step: 'الخطوة',
    of: 'من',
    yes: 'نعم',
    loading: 'جاري التحميل...',
    processing: 'جاري المعالجة...',
    select: 'اختر',
    save: 'حفظ',
    cancel: 'إلغاء',
    edit: 'تعديل',
    delete: 'حذف',
    confirm: 'تأكيد',
    back: 'رجوع',
    next: 'التالي',
    previous: 'السابق',
    linkCopied: 'تم نسخ الرابط!',
    justNow: 'الآن',
    minutesAgo: '{count} دقيقة مضت',
    hoursAgo: '{count} ساعة مضت',
    yesterday: 'الأمس',
    tryAgain: 'حاول مرة أخرى',
    showFilters: 'إظهار الفلاتر',
    hideFilters: 'إخفاء الفلاتر',
    unknown: 'غير معروف',
    sending: 'جاري الإرسال...',
    refresh: 'تحديث',
    viewAll: 'عرض الكل',
    all: 'الكل',
    search: 'بحث',
    view: 'عرض',
    daysAgo: 'منذ {count} يوم',
    add: 'إضافة',
    create: 'إنشاء',
    filters: 'فلاتر',
    previous: 'السابق',
    next: 'التالي',
    failedToLoad: 'فشل في تحميل البيانات',
    searchPlaceholder: 'بحث في {type}...',
    showingPage: 'عرض صفحة {current} من {total}',
    // Social sharing
    shareOptions: 'خيارات المشاركة',
    facebook: 'مشاركة على فيسبوك',
    twitter: 'مشاركة على تويتر',
    linkedin: 'مشاركة على لينكد إن',
    whatsapp: 'مشاركة على واتساب',
    email: 'مشاركة عبر البريد الإلكتروني',
    copyLink: 'نسخ الرابط',
    contactUs: 'اتصل بنا',
    complete: ''
  },

  contact: {
    getInTouch: 'كن على اتصال'
  },

  share: {
    facebook: 'مشاركة على فيسبوك',
    copy: 'نسخ',
    twitter: 'مشاركة على تويتر',
    linkedin: 'مشاركة على لينكد إن',
    whatsapp: 'مشاركة على واتساب',
    email: 'مشاركة عبر البريد الإلكتروني',
    copyLink: 'نسخ الرابط'
  },

  nav: {
    home: 'الرئيسية',
    properties: 'العقارات',
    auctions: 'المزادات',
    messages: 'الرسائل',
    about: 'من نحن',
    contact: 'اتصل بنا',
    login: 'تسجيل الدخول',
    register: 'تسجيل',
    logout: 'تسجيل الخروج',
    profile: 'الملف الشخصي',
    dashboard: 'لوحة التحكم',

    propertyTypes: {
      residential: 'سكني',
      commercial: 'تجاري',
      land: 'أرض',
      industrial: 'صناعي',
      mixedUse: 'متعدد الاستخدامات'
    }
  },

  search: {
    keyword: 'بحث بالكلمات المفتاحية',
    keywordPlaceholder: 'اسم العقار، الموقع، إلخ',
    propertyType: 'نوع العقار',
    city: 'المدينة',
    cityPlaceholder: 'أدخل اسم المدينة',
    price: 'نطاق السعر',
    size: 'المساحة',
    min: 'الحد الأدنى',
    max: 'الحد الأقصى',
    search: 'بحث',
    clear: 'مسح الفلاتر',
    all: 'الكل',
    allPropertyTypes: 'جميع أنواع العقارات',
    advancedFilters: 'خيارات البحث المتقدمة',
    sort: 'ترتيب حسب',
    clearAll: 'مسح الكل',

    sortOptions: {
      newest: 'الأحدث أولاً',
      priceAsc: 'السعر: من الأقل إلى الأعلى',
      priceDesc: 'السعر: من الأعلى إلى الأقل',
      sizeAsc: 'المساحة: من الأصغر إلى الأكبر',
      sizeDesc: 'المساحة: من الأكبر إلى الأصغر'
    }
  },

  validation: {
    titleRequired: 'العنوان مطلوب',
    propertyTypeRequired: 'نوع العقار مطلوب',
    deedNumberRequired: 'رقم صك الملكية مطلوب',
    descriptionRequired: 'الوصف مطلوب',
    sizeRequired: 'الحجم مطلوب',
    addressRequired: 'عنوان الشارع مطلوب',
    cityRequired: 'المدينة مطلوبة',
    stateRequired: 'المنطقة/المحافظة مطلوبة',
    marketValueRequired: 'القيمة السوقية مطلوبة',
    invalidDeedNumberFormat: 'تنسيق رقم الصك غير صالح',
    invalidSizeFormat: 'تنسيق الحجم غير صالح',
    invalidMarketValueFormat: 'تنسيق القيمة السوقية غير صالح',
    invalidMinimumBidFormat: 'تنسيق الحد الأدنى للمزايدة غير صالح',
    invalidLatitudeFormat: 'تنسيق خط العرض غير صالح',
    invalidLongitudeFormat: 'تنسيق خط الطول غير صالح',
    titleTooLong: 'لا يمكن أن يتجاوز العنوان 255 حرفًا',
    addressTooLong: 'لا يمكن أن يتجاوز العنوان 255 حرفًا',
    cityTooLong: 'لا يمكن أن تتجاوز المدينة 100 حرف',
    stateTooLong: 'لا يمكن أن تتجاوز المنطقة/المحافظة 100 حرف',
    postalCodeTooLong: 'لا يمكن أن يتجاوز الرمز البريدي 20 حرفًا',
    countryTooLong: 'لا يمكن أن تتجاوز الدولة 100 حرف',
    invalidSizeRange: 'يجب أن يكون الحجم أكبر من 0',
    invalidMarketValueRange: 'يجب أن تكون القيمة السوقية أكبر من 0',
    invalidMinimumBidRange: 'يجب أن يكون الحد الأدنى للمزايدة أكبر من 0',
    invalidFloorsFormat: 'تنسيق عدد الطوابق غير صالح',
    invalidYearFormat: 'تنسيق سنة غير صالح',
    subjectRequired: "الموضوع مطلوب",
    subjectTooShort: "يجب أن يكون الموضوع 5 أحرف على الأقل",
    subjectTooLong: "لا يمكن أن يتجاوز الموضوع 255 حرف",
    messageRequired: "الرسالة مطلوبة",
    messageTooShort: "يجب أن تكون الرسالة 10 أحرف على الأقل",
    messageTooLong: "لا يمكن أن تتجاوز الرسالة 2000 حرف",
    roomNameRequired: 'اسم الغرفة مطلوب'
  },

  fileUpload: {
    dropZoneLabel: 'منطقة إسقاط لتحميل الملف',
    selectedFilesList: 'الملفات المحددة',
    uploading: 'جاري التحميل...',
    invalidType: 'نوع ملف غير صالح',
    fileTooLarge: 'الملف كبير جدًا (الحد الأقصى {size} ميجابايت)',
    tooManyFiles: 'عدد كبير جدًا من الملفات (الحد الأقصى {max})',
    removeFile: 'إزالة الملف {name}'
  },

  mediaUploader: {
    dragAndDrop: 'اسحب وأفلت الملفات هنا، أو انقر لتحديد الملفات',
    uploading: 'جاري تحميل ملفات الوسائط...',
    selectFiles: 'تحديد الملفات',
    browse: 'استعراض',
    dropFilesHere: 'أفلت الملفات هنا',
    uploadProgress: 'تقدم التحميل',
    uploadComplete: 'اكتمل التحميل',
    uploadFailed: 'فشل التحميل',
    maxFileSize: 'الحد الأقصى لحجم الملف: {size} ميجابايت',
    allowedFileTypes: 'أنواع الملفات المسموح بها: {types}',
    fileAdded: 'تمت إضافة الملف: {name}',
    fileRemoved: 'تمت إزالة الملف: {name}',
    clearAll: 'مسح الكل'
  },

  location: {
    title: 'الموقع',
    locationDesc: 'حدد موقع العقار على الخريطة',
    address: 'العنوان',
    city: 'المدينة',
    state: 'المنطقة',
    postalCode: 'الرمز البريدي',
    country: 'الدولة',
    latitude: 'خط العرض',
    longitude: 'خط الطول',
    detect: 'تحديد الموقع',
    detectHelp: 'استخدم موقعك الحالي لتحديد موقع العقار',
    detectButton: 'تحديد موقعي',
    useMap: 'استخدم الخريطة',
    enterManually: 'إدخال يدوي',
    mapContainer: 'خريطة الموقع',
    searchPlaceholder: 'ابحث عن موقع...',
    mapInitFailed: 'فشل تهيئة الخريطة',
    mapLoadFailed: 'فشل تحميل الخريطة',
    geolocationNotSupported: 'تحديد الموقع غير مدعوم',
    detectionSuccess: 'تم تحديد موقعك بنجاح',
    detectionFailed: 'فشل تحديد الموقع',
    searchFailed: 'فشل البحث',
    geocodingFailed: 'فشل تحويل الإحداثيات إلى عنوان',
    detecting: 'جاري تحديد موقعك...'
  },

  property: {
    title: 'العقار',
    featured: 'مميز',
    rooms: 'الغرف',
    viewDetails: 'عرض التفاصيل',
    features: 'المميزات',
    amenities: 'المرافق',
    location: 'الموقع',
    propertyDetails: 'تفاصيل العقار',
    galleryTabs: {
      photos: 'صور',
      videos: 'فيديوهات',
      documents: 'مستندات',
      otherFiles: 'ملفات أخرى'
    },
    description: 'الوصف',
    marketValue: 'القيمة السوقية',
    size: 'المساحة',
    propertyType: 'نوع العقار',
    buildingType: 'نوع المبنى',
    yearBuilt: 'سنة البناء',
    floors: 'الطوابق',
    roomList: 'قائمة الغرف',
    roomType: 'نوع الغرفة',
    floor: 'الطابق',
    level: 'مستوى',
    area: 'المساحة',
    relatedAuctions: 'المزادات المرتبطة',
    noAuctions: 'لا توجد مزادات حالية لهذا العقار',
    contactOwner: 'التواصل مع المالك',
    loginToContact: 'يرجى تسجيل الدخول إلى حسابك لإرسال رسالة إلى مالك العقار.',
    message: "رسالتك",
    messagePlaceholder: "مرحباً! أنا مهتم بهذا العقار. هل يمكنك تقديم المزيد من التفاصيل حول...",
    sendMessage: "إرسال الرسالة",
    noLocationData: 'لا تتوفر بيانات الموقع لهذا العقار',
    createProperty: 'إضافة عقار جديد',
    createPropertyDesc: 'املأ التفاصيل لإضافة عقار جديد إلى محفظتك',
    basicInfo: 'المعلومات الأساسية',
    basicInfoDesc: 'معلومات عامة حول العقار',
    locationDesc: 'العنوان والإحداثيات الجغرافية',
    details: 'تفاصيل العقار',
    detailsDesc: 'الحجم والبناء والميزات الخاصة',
    roomsDesc: 'تحديد الغرف داخل هذا العقار',
    financial: 'المعلومات المالية',
    financialDesc: 'القيمة السوقية ومعلومات المزايدة',
    roomFeatures: 'ميزات الغرفة',
    hasWindow: 'تحتوي على نافذة',
    hasBathroom: 'تحتوي على حمام خاص',
    startAddingRooms: 'البدء بإضافة الغرف',
    roomAdded: 'تمت إضافة الغرفة بنجاح',
    coordinates: 'الإحداثيات',
    clickToInteract: 'انقر على الخريطة للتفاعل',
    noImages: 'لا توجد صور',
    noImagesInfo: 'لم يتم تحميل صور لهذا العقار بعد',
    gallery: 'معرض الصور',
    addressInfo: 'معلومات العنوان',
    keyFeatures: 'الميزات الرئيسية',
    featuresAndAmenities: 'الميزات والمرافق',
    nearbyServices: 'الخدمات القريبة',
    nearbyServicesInfo: 'معلومات عن الخدمات القريبة غير متوفرة حاليًا',
    
    // Media Upload Section
    mediaUpload: 'تحميل الوسائط',
    mediaUploadDesc: 'قم بتحميل الصور ومخططات الطوابق والمستندات للعقار الخاص بك. الصيغ المدعومة: JPEG، PNG، GIF، PDF.',
    mediaFiles: 'ملفات الوسائط',
    uploadFiles: 'تحميل الملفات',
    dragDrop: 'أو اسحب وأفلت',
    fileTypes: 'PNG, JPG, GIF حتى 10MB',
    selectedFiles: 'الملفات المحددة',
    
    // Publishing Options
    publishingOptions: 'خيارات النشر',
    published: 'نشر العقار',
    publishedHelp: 'جعل هذا العقار مرئيًا للمستخدمين',
    featuredHelp: 'إظهار هذا العقار في القوائم المميزة',
 
    
    // Room Management
    addRoom: 'إضافة غرفة',
    roomName: 'اسم الغرفة',
    noRooms: 'لم تتم إضافة غرف بعد',
    addRoomHelp: 'استخدم النموذج أعلاه لإضافة غرف إلى هذا العقار',
    remove: 'إزالة',
    actions: 'إجراءات',
    
    // Property Details
    deedNumber: 'رقم الصك',
    deedNumberHelp: 'رقم صك الملكية الرسمي للعقار',
    detectLocation: 'اكتشاف الموقع الحالي',
    detectLocationHelp: 'استخدم موقعك الحالي لهذا العقار',
    minimumBid: 'الحد الأدنى للمزايدة',
    
    // Success/Error Messages
    createSuccess: 'تم إنشاء العقار بنجاح',
    createFailed: 'فشل في إنشاء العقار',
    createSuccessMediaFailed: 'تم إنشاء العقار بنجاح ولكن فشل تحميل بعض الصور',
    unauthorizedMessage: 'يجب أن تكون مسجلاً كمالك عقار أو مقيم عقاري لإضافة عقارات',
    propertyCreatedMessage: 'تم إنشاء العقار بنجاح وهو جاهز للعرض',
    
    // Form Fields
    commaSeparated: 'مفصولة بفواصل',
    addressInfoDesc: 'معلومات تفصيلية عن الموقع',
    sqm: 'متر مربع',
    name: 'الاسم',
    titlePlaceholder: 'أدخل عنوان العقار',
    deedNumberPlaceholder: 'أدخل رقم صك الملكية',
    descriptionPlaceholder: 'وصف تفصيلي للعقار',
    
    // Document Types
    pdfDocument: 'مستند بي دي إف',
    downloadPdf: 'تحميل ملف PDF',
    document: 'مستند',
    downloadDocument: 'تحميل المستند',
    file: 'ملف',
    downloadFile: 'تحميل الملف',
    
    // Gallery
    closeGallery: 'إغلاق المعرض',
    viewImage: 'عرض الصورة',
    mediaItem: 'عنصر وسائط',
    
    // Property Actions
    loading: 'جار تحميل العقار...',
    edit: 'تعديل العقار',
    photos: 'صور العقار',
    
    // Address Fields
    address: 'العنوان',
    city: 'المدينة',
    state: 'المحافظة/المنطقة',
    postalCode: 'الرمز البريدي',
    country: 'الدولة',
    
    // Auction Related
    noActiveAuctions: 'لا توجد مزادات متاحة لهذا العقار حالياً.',
    startAuctionDesc: 'يمكنك بدء مزاد على هذا العقار',
    create: 'إنشاء',
    
    // Tab labels
    tab: {
      overview: 'نظرة عامة',
      rooms: 'الغرف',
      location: 'الموقع',
      gallery: 'المعرض',
      auctions: 'المزادات'
    },

    // Room Types - THIS WAS MISSING!
    roomTypes: {
      bedroom: 'غرفة نوم',
      livingRoom: 'غرفة معيشة',
      kitchen: 'مطبخ',
      bathroom: 'حمام',
      diningRoom: 'غرفة طعام',
      office: 'مكتب',
      guestRoom: 'غرفة ضيوف',
      masterBedroom: 'غرفة نوم رئيسية',
      childrenRoom: 'غرفة أطفال',
      utilityRoom: 'غرفة خدمات',
      storageRoom: 'غرفة تخزين',
      garage: 'مرآب',
      balcony: 'شرفة',
      terrace: 'تراس',
      basement: 'قبو',
      attic: 'علية',
      hallway: 'ممر',
      entrance: 'مدخل',
      laundryRoom: 'غرفة غسيل',
      other: 'أخرى',
      living: 'غرفة معيشة',
      dining: 'غرفة طعام',
      storage: 'غرفة تخزين'
    },

    // Feature Items - These were outside property object
    featureItems: {
      airConditioning: 'تكييف الهواء',
      heating: 'تدفئة',
      parking: 'موقف سيارات',
      garage: 'مرآب',
      pool: 'حمام سباحة',
      swimmingpool: 'حمام سباحة',
      SwimmingPool: 'حمام سباحة',
      garden: 'حديقة',
      security: 'نظام أمان',
      elevator: 'مصعد',
      fireplace: 'مدفأة',
      balcony: 'شرفة',
      terrace: 'تراس',
      storage: 'غرفة تخزين',
      furnished: 'مفروش',
      petsAllowed: 'يسمح بالحيوانات الأليفة',
      wheelchairAccess: 'مدخل للكراسي المتحركة',
      fiberInternet: 'إنترنت فايبر',
      solarPanels: 'ألواح شمسية',
      gym: 'صالة رياضية',
      laundryRoom: 'غرفة غسيل',
      // Arabic keys for direct lookup
      'صالةرياضية': 'صالة رياضية',
      'صالة رياضية': 'صالة رياضية',
      'مفروش': 'مفروش',
      'موقد': 'موقد',
      'مخزن': 'مخزن',
      'غرفةغسيل': 'غرفة غسيل',
      'غرفة غسيل': 'غرفة غسيل',
      'حديقة': 'حديقة',
      'مرآب': 'مرآب',
      'حمام سباحة': 'حمام سباحة',
      'حمامسباحة': 'حمام سباحة',
      'شرفة': 'شرفة',
      'تكييف': 'تكييف هواء',
      'تدفئة': 'تدفئة',
      'مصعد': 'مصعد',
      'نظام أمني': 'نظام أمني',
      'نظامأمني': 'نظام أمني',
      'موقف سيارات': 'موقف سيارات',
      'موقفسيارات': 'موقف سيارات'
    },

    roomFeatureItems: {
      window: 'نافذة',
      privateBathroom: 'حمام خاص',
      walkInCloset: 'خزانة ملابس واسعة',
      ensuite: 'جناح خاص',
      airConditioning: 'تكييف هواء',
      heating: 'تدفئة',
      ceilingFan: 'مروحة سقف',
      hardwoodFloor: 'أرضية خشبية',
      carpetFloor: 'أرضية مفروشة بالسجاد',
      tileFloor: 'أرضية بلاط',
      soundproofing: 'عازل للصوت',
      furnished: 'مفروشة',
      desk: 'مكتب/مساحة عمل',
      tv: 'تلفزيون',
      internetAccess: 'اتصال بالإنترنت',
      naturalLight: 'إضاءة طبيعية',
      view: 'إطلالة جيدة',
      storage: 'مساحة تخزين',
      kingBed: 'سرير كينج',
      queenBed: 'سرير كوين',
      singleBed: 'سرير فردي',
      doubleBed: 'سرير مزدوج',
      bathtub: 'حوض استحمام',
      shower: 'دش',
      jacuzzi: 'جاكوزي',
      bathroom: 'حمام',

    },

    amenityItems: {
      gym: 'صالة رياضية',
      spa: 'سبا',
      sauna: 'ساونا',
      playground: 'ملعب أطفال',
      bbqArea: 'منطقة شواء',
      communityCenter: 'مركز مجتمعي',
      tennisCourtBasketball: 'ملعب تنس/كرة سلة',
      concierge: 'خدمة الكونسيرج',
      businessCenter: 'مركز أعمال',
      guestParking: 'موقف للضيوف',
      laundryService: 'خدمة غسيل الملابس',
      rooftopDeck: 'سطح علوي',
      childcare: 'خدمات رعاية الأطفال',
      petGrooming: 'العناية بالحيوانات الأليفة',
      carCharging: 'شحن السيارات الكهربائية',
      bikeStorage: 'تخزين الدراجات',
      schools: 'مدارس',
      shoppingCenters: 'مراكز تسوق',
      parks: 'منتزهات',
      publicTransportation: 'وسائل النقل العام',
      mosque: 'مسجد',
      hospitals: 'مستشفيات',
      restaurants: 'مطاعم',
      beachAccess: 'وصول للشاطئ',
      sportsFacilities: 'مرافق رياضية',
      university: 'جامعة',


    },

    buildingTypes: {
      apartment: 'شقة',
      villa: 'فيلا',
      building: 'مبنى',
      farmhouse: 'مزرعة',
      shop: 'محل تجاري',
      office: 'مكتب'
    },

    statusTypes: {
      draft: 'مسودة',
      published: 'منشور',
      available: 'متاح',
      underContract: 'تحت العقد',
      sold: 'مباع',
      auction: 'في المزاد'
    },

    error: {
      title: 'تعذر تحميل العقار'
    },

    media: {
      untitled: 'وسائط بدون عنوان'
    }
  },
    
  galleryTabs: {
    photos: 'صور',
    videos: 'فيديوهات',
    documents: 'مستندات',
    otherFiles: 'ملفات أخرى'
  },


    
  properties: {
    title: 'العقارات',
    subtitle: 'تصفح العقارات المتاحة للبيع والمزاد',
    noResults: 'لم يتم العثور على عقارات',
    tryAdjusting: 'حاول تعديل عوامل التصفية أو تحقق لاحقًا',
    backToProperties: 'العودة إلى العقارات',
    contactOwner: "تواصل مع مالك العقار",
    loginToContact: "يرجى تسجيل الدخول إلى حسابك لإرسال رسالة إلى مالك العقار.",
    message: "رسالتك",
    messagePlaceholder: "مرحباً! أنا مهتم بهذا العقار. هل يمكنك تقديم المزيد من التفاصيل حول...",
    sendMessage: "إرسال رسالة",
    totalProperties: 'إجمالي العقارات',
    averagePrice: 'متوسط السعر',
    moreAvailable: 'المزيد من العقارات متاح',
    showingFirst: 'عرض أول',
    of: 'من',
    viewAllProperties: 'عرض جميع العقارات',
    wantToListProperty: 'تريد إدراج عقارك؟'
  },

  auction: {
    title: 'المزادات',
    subtitle: 'تصفح وزايد على المزادات العقارية المتاحة',
    featured: 'مميز',
    currentBid: 'المزايدة الحالية',
    bids: 'مزايدات',
    viewDetails: 'عرض التفاصيل',
    live: 'مباشر الآن',
    biddingActive: 'المزايدة نشطة',
    bidNow: 'زايد الآن',
    description: 'وصف المزاد',
    startingBid: 'سعر البداية',
    bidding: 'المزايدة',
    timeline: 'الجدول الزمني',
    uploadMedia: 'رفع الوسائط',
    termsConditionsDesc: 'الشروط والأحكام الخاصة بالمزاد',
    register: 'التسجيل للمزاد',


    liveBidding: 'المزايدة المباشرة',
    participants: 'المشاركون: {count}',
    nextMinBid: 'أقل مزايدة تالية',
    recentBids: 'المزايدات الأخيرة',


    quickBids: 'مزايدات سريعة',
    quickBidFor: 'مزايدة سريعة بمبلغ {amount}',
    minBid: 'أقل مزايدة',
    powerBid: 'مزايدة قوية',


    bid: 'زايد',
    placeBid: 'ضع مزايدة',
    confirmBid: 'تأكيد المزايدة',
    bidPlaced: 'تم وضع مزايدتك بنجاح!',


    customBid: 'مزايدة مخصصة',
    enterCustomBid: 'أدخل مبلغ مزايدة مخصص',
    submitCustomBid: 'إرسال مزايدة مخصصة',
    advancedBidding: 'مزايدة متقدمة',
    openAdvancedBidding: 'فتح خيارات المزايدة المتقدمة',
    quickBidSuggestions: 'اقتراحات المزايدة السريعة',
    advancedOptions: 'خيارات متقدمة',
    minimumRequired: 'الحد الأدنى المطلوب',
    bidNotesPlaceholder: 'أضف أي ملاحظات مع مزايدتك...',
    bidNotes: 'ملاحظات المزايدة',
    bidNotesHelp: 'أضف أي ملاحظات إضافية مع مزايدتك',
    autoBidUpTo: 'المزايدة التلقائية حتى هذا المبلغ',
    toWin: 'للفوز',
    bidSummary: 'ملخص المزايدة',
    youWillBid: 'ستقوم بالمزايدة بمبلغ',
    withAutoUpTo: 'مع المزايدة التلقائية حتى',
    placeAutoBid: 'وضع مزايدة تلقائية',
    autoBidding: 'المزايدة التلقائية',
    enableAutoBidding: 'تفعيل المزايدة التلقائية',
    maxBidAmount: 'أقصى مبلغ للمزايدة',
    autoBidHelp: 'ضع مزايدات تلقائياً عند تجاوز مزايدتك، حتى المبلغ الأقصى',
    bidStatus: 'حالة المزايدة',
    bidAmount: 'مبلغ المزايدة',
    bidTime: 'وقت المزايدة',
    bidder: 'المزايد',
    you: 'أنت',
    anonymous: 'مجهول',
    winning: 'فائز حالياً',
    outbid: 'تم تجاوز مزايدتك',
    bidTooLow: 'يجب أن تكون المزايدة على الأقل {amount}',
    bidFailed: 'فشل في وضع المزايدة',
    bidAmountRequired: 'مبلغ المزايدة مطلوب',
    invalidBidAmount: 'مبلغ مزايدة غير صالح',
  
    // Registration
    registerForAuction: 'سجل للمزاد',
    registrationRequired: 'التسجيل مطلوب',
    registered: 'مسجل',
  
    // Login Required
    loginRequired: 'تسجيل الدخول مطلوب',
    loginToPlaceBid: 'سجل دخول لوضع مزايدة',
    loginRequiredMessage: 'يجب أن تكون مسجلاً لوضع مزايدة في هذا المزاد',
  
    // Bid Agreement
    bidAgreement: 'اتفاقية المزايدة',
    bidDisclaimer: 'بوضع مزايدة، فإنك توافق على الشروط والأحكام لهذا المزاد.',
  
    // Currency Related
    minimumBid: 'أقل مزايدة',
    totalBids: 'إجمالي المزايدات',
    
    // Additional Status Messages
    placingBid: 'جاري وضع المزايدة...',
    bidSubmitted: 'تم إرسال المزايدة: {amount}',
    bidUpdated: 'تم تحديث المزايدة إلى {amount}',
  
    // Quick Bid Labels
    minBidLabel: 'أقل مزايدة',
    incrementLabel: '+{increment}',
    powerLabel: 'قوية',

    timeRemaining: 'الوقت المتبقي',
    days: 'أيام',
    hours: 'ساعات',
    minutes: 'دقائق',
    seconds: 'ثواني',
    status: 'حالة المزاد',
    statusLive: 'مباشر',
    activeOnly: 'المزادات النشطة فقط',
    winningOnly: 'المزادات الفائزة فقط',
    viewAuction: 'عرض المزاد',
    statusScheduled: 'مجدول',
    statusEnded: 'منتهي',
    statusCompleted: 'مكتمل',
    statusDraft: 'مسودة',
    typeSealed: 'عطاءات مغلقة',
    typeReserve: 'بحد أدنى',
    typeNoReserve: 'بدون حد أدنى',

    bidDetails: 'تفاصيل المزايدة',
    biddingOptions: 'خيارات المزايدة',

    bidHistory: 'سجل المزايدات',
    noBids: 'لم يتم تقديم أي مزايدات بعد',
    bidderName: 'المزايد',

    auctionDetails: 'تفاصيل المزاد',
    startDate: 'تاريخ البدء',
    endDate: 'تاريخ الانتهاء',
    registrationDeadline: 'الموعد النهائي للتسجيل',
    termsConditions: 'الشروط والأحكام',
    auctionEnded: 'انتهى هذا المزاد',
    yourBid: 'مزايدتك',
    highestBid: 'أعلى مزايدة',


    beatCurrentBid: 'تجاوز المزايدة الحالية',
    safeMargin: 'هامش آمن',
    competitive: 'تنافسية',
    aggressive: 'قوية',
    strongBid: 'قوية',
    optional: 'اختياري',
    tabOverview: "نظرة عامة",
    tabHistory: "التاريخ",
    tabDocuments: "المستندات",
    nextBid: "المناقصة التالية",
    safeBid: "مناقصة آمنة",
    customAmount: "مبلغ مخصص",
    customBidAmount: "مبلغ مناقصة مخصص",
    biddingClosed: "المناقصة مغلقة",
    biddingClosedDescription: "هذا المزاد لم يعد يقبل مناقصات.",
    scheduled: "مجدول",
    noImages: "لا توجد صور متاحة",
    noImagesDescription: "لم يتم تحميل أي صور لهذا المزاد بعد.",
    mostActive: 'الأكثر نشاطاً',
    auctionProperty: 'عقار المزاد',
    createAuction: 'إنشاء مزاد جديد',
    createAuctionDesc: 'إعداد مزاد جديد لأحد عقاراتك',
    basicInfo: 'المعلومات الأساسية',
    basicInfoDesc: 'معلومات عامة حول المزاد',
    scheduling: 'الجدولة',
    schedulingDesc: 'تحديد تواريخ البدء والانتهاء والموعد النهائي للتسجيل',
    financial: 'المعلومات المالية',
    financialDesc: 'معلومات المزايدة الأولية والزيادة الدنيا',
    selectProperty: 'اختيار العقار',
    selectPropertyDesc: 'اختر عقارًا للمزاد',
    auctionType: 'نوع المزاد',
    typeSealedDesc: 'لا يمكن للمزايدين رؤية المزايدات الأخرى حتى ينتهي المزاد',
    typeReserveDesc: 'يجب الوصول إلى سعر أدنى لإتمام البيع',
    typeNoReserveDesc: 'سيتم بيع العقار لأعلى مزايد بغض النظر عن السعر',
    publishingOptions: 'خيارات النشر',
    published: 'نشر المزاد',
    publishedHelp: 'جعل هذا المزاد مرئيًا للمستخدمين',
    featuredHelp: 'إظهار هذا المزاد في القوائم المميزة',
    registrationDeadlineHelp: 'الموعد النهائي الاختياري لتسجيل المزايدين',
    noProperties: 'لم يتم العثور على عقارات',
    noPropertiesDesc: 'تحتاج إلى إنشاء عقار قبل أن تتمكن من إنشاء مزاد',
    termsConditionsText: 'نص الشروط والأحكام',
    termsConditionsHelp: 'تضمين أي شروط قانونية أو شروط دفع أو متطلبات خاصة',
    tryAgain: 'حاول مرة أخرى',
    titleRequired: 'عنوان المزاد مطلوب',
    propertyRequired: 'يجب عليك اختيار عقار',
    datesRequired: 'تواريخ البدء والانتهاء مطلوبة',
    startingBidRequired: 'المزايدة الأولية مطلوبة',
    createSuccess: 'تم إنشاء المزاد بنجاح',
    createFailed: 'فشل في إنشاء المزاد',
    create: 'إنشاء مزاد',
    filterByStatus: 'تصفية حسب الحالة',
    filterByType: 'تصفية حسب النوع',
    allStatuses: 'جميع الحالات',
    allTypes: 'جميع الأنواع',
    noResults: 'لم يتم العثور على مزادات',
    tryAdjusting: 'حاول تعديل عوامل التصفية أو تحقق لاحقًا',
    browseProperties: 'تصفح العقارات',
    backToAuctions: 'العودة إلى المزادات',
    shareAuction: 'مشاركة هذا المزاد',
    beTheFirst: 'كن أول من يقدم مزايدة!',
    loginToPlaceBid: 'سجل دخول لتقديم مزايدة',
    loginToRegister: 'سجل دخول للتسجيل',
    needHelp: 'هل تحتاج للمساعدة؟',
    contactSupport: 'اتصل بالدعم',
    you: 'أنت',
    accepted: 'مقبولة',
    rejected: 'مرفوضة',
    pending: 'قيد الانتظار',
    totalBids: 'إجمالي المزايدات',
    startsIn: 'يبدأ في',
    auctionNotStarted: 'لم يبدأ هذا المزاد بعد',
    wonBy: 'فاز بها {name} بمبلغ {amount}',
    minimumIncrement: 'الحد الأدنى للزيادة',
    bidTooLow: 'يجب أن تكون المزايدة على الأقل {amount}',
    bidPlaced: 'تم تقديم مزايدتك بنجاح!',
    loadMore: 'تحميل المزيد',
    endingSoon: 'سينتهي قريبًا',
    biddingTips: 'نصائح المزايدة',
    tip1: 'ابحث جيدًا عن العقار قبل تقديم عرض.',
    tip2: 'حدد ميزانية قصوى ولا تتجاوزها.',
    tip3: 'تابع المزاد عن كثب عند اقتراب وقت الانتهاء.',
    bidDisclaimer: 'بتقديم عرض، فإنك توافق على الشروط والأحكام الخاصة بهذا المزاد.',
    confirmBid: 'تأكيد العرض',
    loginRequired: 'تسجيل الدخول مطلوب',
    loginRequiredMessage: 'يجب أن تكون مسجلاً لتقديم عرض في هذا المزاد.',
    tabDetails: 'التفاصيل',
    tabProperty: 'العقار',
    tabBids: 'سجل العروض',
    tabTerms: 'الشروط',
    propertyInfo: 'معلومات العقار',
    moreImages: 'صور إضافية',
    auctionStatus: 'حالة المزاد',
    noDescription: 'لا يوجد وصف متاح.',
    primaryMedia: 'الصورة الرئيسية',
    setPrimary: 'تعيين كصورة رئيسية',
    removeMedia: 'إزالة',
    primary: 'رئيسية',
    media: 'الوسائط',
    mediaDesc: 'قم بتحميل الصور وملفات الوسائط الأخرى لهذا المزاد.',
    uploadedMedia: 'الوسائط المرفوعة',
    minimumParticipants: 'الحد الأدنى من المشاركين',
    minimumParticipantsHelp: 'الحد الأدنى من المزايدين المطلوبين لصحة المزاد.',
    requireBidVerification: 'طلب تحقق من العرض',
    requireBidVerificationHelp: 'إذا تم التفعيل، يجب التحقق يدويًا من العروض قبل قبولها.',
    autoExtend: 'تمديد تلقائي (دقائق)',
    autoExtendHelp: 'تمديد المزاد تلقائيًا إذا تم تقديم عرض خلال هذا العدد من الدقائق قبل انتهاء الوقت.',
    slugHelp: 'نسخة صديقة لعنوان URL من عنوان المزاد. اتركه فارغًا ليتم إنشاؤه تلقائيًا.',
    updateSuccess: 'تم تحديث المزاد بنجاح!',
    editNotAuthorized: 'غير مخول لتعديل هذا المزاد.',
    updateFailed: 'فشل في تحديث المزاد',
    save: 'حفظ التغييرات',
    delete: 'حذف المزاد',
    deleteConfirm: 'حذف المزاد',
    deleteConfirmTitle: 'هل أنت متأكد؟',
    deleteConfirmMessage: 'لا يمكن التراجع عن هذا الإجراء. سيتم حذف المزاد نهائيًا.',
    confirmDelete: 'نعم، احذف المزاد',
    deleteFailed: 'فشل في حذف المزاد',
    preview: 'معاينة',
    exitPreview: 'الخروج من المعاينة',
    notFound: 'المزاد غير موجود',
    notFoundDesc: 'المزاد الذي تبحث عنه غير موجود أو تم حذفه.',
    bidPlacedSuccess: 'تم تقديم عرضك بنجاح.',
    edit: 'تعديل المزاد',
    editDesc: 'قم بتحديث التفاصيل والإعدادات لهذا المزاد.',
    filterAndSort: 'تصفية وترتيب',
    endDateAfterStart: 'يجب أن يكون تاريخ الانتهاء بعد تاريخ البدء',
    regDeadlineBeforeStart: 'يجب أن يكون آخر موعد للتسجيل قبل تاريخ البدء',
    startDateRequired: 'تاريخ البدء مطلوب',
    endDateRequired: 'تاريخ الانتهاء مطلوب',
    createNewPrompt: 'هل لديك عقار للبيع بالمزاد؟ أنشئ قائمة مزاد جديدة:',
    liveBidding: 'المزايدة المباشرة',
    liveNow: 'مباشر الآن',
    quickBids: 'مزايدات سريعة',
    quickBidFor: 'مزايدة سريعة بمبلغ {amount}',
    enterCustomBid: 'أدخل مبلغ المزايدة المخصص',
    submitCustomBid: 'إرسال المزايدة المخصصة',
    bid: 'زايد',
    advancedBidding: 'مزايدة متقدمة',
    openAdvancedBidding: 'فتح خيارات المزايدة المتقدمة',
    bidUpdated: 'تم تحديث المزايدة إلى {amount}',
    bidSubmitted: 'تم إرسال المزايدة: {amount}',
    confirmLargeBid: 'تأكيد المزايدة الكبيرة',
    largeBidWarning: 'أنت على وشك تقديم مزايدة بمبلغ {amount}. هذا أعلى بكثير من المزايدة الحالية. هل أنت متأكد؟',
    bidHelpText: 'مزايدتك ملزمة ولا يمكن سحبها بعد تقديمها.',
    keyboardShortcuts: 'اختصارات لوحة المفاتيح',
    pressBToBid: 'اضغط B لفتح المزايدة',
    numberKeysQuickBid: 'استخدم أرقام 1-4 للمزايدات السريعة',
    auctionId: 'رقم المزاد',
    views: 'المشاهدات',
    images: 'الصور',
    auctionTabs: 'تبويبات معلومات المزاد',
    auctionInfo: 'معلومات المزاد',
    schedule: 'الجدول الزمني',
    keyDetails: 'التفاصيل الرئيسية',
    refresh: 'تحديث',
    anonymousBidder: 'مزايد مجهول',
    highest: 'الأعلى',
    recentActivity: 'النشاط الأخير',
    newBidPlaced: 'تم تقديم مزايدة جديدة',
    by: 'بواسطة',
    viewAllBids: 'عرض جميع المزايدات',
    noTerms: 'لا توجد شروط متاحة',
    contactForTerms: 'اتصل بالدعم للحصول على الشروط والأحكام',
    liveAuction: 'مزاد مباشر',
    joinAuction: 'انضم إلى هذا المزاد',
    registerDesc: 'سجل للمشاركة في هذا المزاد',
    signInToBid: 'سجل دخول للمزايدة',
    createAccountDesc: 'أنشئ حساب للمشاركة',
    preBiddingAvailable: 'المزايدة المسبقة متاحة',
    preBiddingDesc: 'ضع مزايدات الآن ستصبح نشطة عندما يبدأ المزاد.',
    participants: '{count} مشاركين',
    nextBid: 'المزايدة التالية',
    placeCustomBid: 'تقديم مزايدة مخصصة',
    // submitCustomBid: 'إرسال مزايدة مخصصة',
    minBid: 'الحد الأدنى للمزايدة',
    plusOneInc: 'زيادة واحدة',
    plusIncrement: 'زيادة واحدة',
    plusTwoInc: 'زيادتان',
    plusTwoIncrement: 'زيادتان',
    power: 'مزايدة قوية',
    powerBid: 'مزايدة قوية',
    selectWinner: 'اختيار الفائز بالمزاد',
    selectWinnerDesc: 'راجع جميع المزايدات واختر الفائز. سينهي هذا الإجراء المزاد ويخطر المزايد الفائز.',
    closingNotes: 'ملاحظات الإغلاق (اختياري)',
    closingNotesHelp: 'أضف أي ملاحظات أو شروط للمزايد الفائز',
    endAuction: 'إنهاء المزاد واختيار الفائز',
    selectWinnerEndAuction: 'اختيار الفائز وإنهاء المزاد',
    extend: 'تمديد',

    standardTerms: 'الشروط المعمول بها',
    standardTermsHelp: 'أضف أي شروط أو شروط للمزايد الفائز',
    
    term1: "جميع العروض المقدمة في المزاد نهائية ولا يمكن التراجع عنها تحت أي ظرف.",
    term2: "يلتزم الفائز بالمزاد بإتمام عملية الدفع خلال مدة أقصاها 48 ساعة من وقت إغلاق المزاد.",
    term3: "تُباع جميع العقارات بالحالة الراهنة (كما هي) دون أي ضمانات صريحة أو ضمنية.",
    term4: "يتحمل المشتري مسؤولية إنهاء إجراءات نقل الملكية حسب الأنظمة والقوانين المعمول بها."
    
    
  },

  messages: {
    inquiryAbout: "استفسار حول",
    getInTouch: "تواصل مع مالك العقار",
    sender: "المرسل",
    subject: "الموضوع",
    subjectPlaceholder: "أدخل موضوع رسالتك...",
    aboutProperty: "حول العقار",
    loginRequired: "تسجيل الدخول مطلوب",
    messageSentSuccess: "تم إرسال الرسالة بنجاح!",
    messageDelivered: "تم توصيل رسالتك إلى مالك العقار. سيتواصل معك قريباً.",
    directMessagingNotAvailable: "المراسلة المباشرة غير متاحة في هذا السياق",
    sendError: "فشل في إرسال الرسالة. يرجى المحاولة مرة أخرى.",
    messageDisclaimer: "سيتم مشاركة معلومات الاتصال الخاصة بك مع مالك العقار.",
    title: "الرسائل",
    compose: "إنشاء رسالة",
    total: "إجمالي",
    unread: "غير مقروءة",
    search: "البحث في الرسائل...",
    confirmDelete: "هل أنت متأكد أنك تريد حذف هذه الرسالة؟",
    to: "إلى: {name}",
    from: "من: {name}",
    archive: "أرشفة",
    delete: "حذف",
    close: "إغلاق",
    reply: "الرد",
    relatedProperty: "العقار المرتبط",
    selectToRead: "اختر رسالة للقراءة",
    selectToReadDesc: "اختر رسالة من القائمة على اليسار لعرض محتواها",
    noMessages: "لا توجد رسائل",
    noSearchResults: "لم يتم العثور على رسائل مطابقة لبحثك",
    startConversation: "ابدأ محادثة جديدة بالضغط على زر 'إنشاء رسالة'",
    backToMessages: "العودة إلى الرسائل",
    replyToMessage: "الرد على الرسالة",
    composeNewMessage: "إنشاء رسالة جديدة",
    originalMessage: "الرسالة الأصلية",
    couldNotLoadReplyMessage: "تعذر تحميل الرسالة الأصلية للرد",
    directMessagingNotImplemented: "المراسلة المباشرة غير متاحة حالياً",
    recipientEmailPlaceholder: "أدخل البريد الإلكتروني للمستلم",
    message: "الرسالة",
    messagePlaceholder: "اكتب رسالتك هنا...",
    send: "إرسال الرسالة",
    unknownUser: 'مستخدم غير معروف',
    errorFetchingUser: 'خطأ في جلب بيانات المستخدم',
    allPriorities: 'جميع الأولويات',
    filters: {
      all: "جميع الرسائل",
      inbox: "صندوق الوارد", 
      sent: "المرسلة",
      unread: "غير المقروءة",
      archived: "المؤرشفة"
    },
    form: {
      priority: "أولوية الرسالة"
    },
    priority: {
      title: "أولوية",
      low: "أولوية منخفضة",
      normal: "عادية",
      high: "أولوية عالية",
      urgent: "عاجلة"
    }
  },

  auth: {
    login: 'تسجيل الدخول إلى حسابك',
    email: 'عنوان البريد الإلكتروني',
    password: 'كلمة المرور',
    forgotPassword: 'هل نسيت كلمة المرور؟',
    noAccount: "ليس لديك حساب؟",
    createAccount: 'إنشاء حساب',
    register: 'تسجيل حساب جديد',
    firstName: 'الاسم الأول',
    lastName: 'الاسم الأخير',
    confirmPassword: 'تأكيد كلمة المرور',
    phoneNumber: 'رقم الهاتف',
    dateOfBirth: 'تاريخ الميلاد',
    alreadyAccount: 'هل لديك حساب بالفعل؟',
    signIn: 'تسجيل الدخول',
    resetPassword: 'إعادة تعيين كلمة المرور الخاصة بك',
    sendResetLink: 'إرسال رابط إعادة التعيين',
    resetInstructions: 'أدخل عنوان بريدك الإلكتروني وسنرسل لك تعليمات لإعادة تعيين كلمة المرور الخاصة بك.',
    backToLogin: 'العودة إلى تسجيل الدخول',
    verifyEmail: 'التحقق من بريدك الالكتروني',
    verificationCode: 'رمز التحقق',
    verifyAccount: 'التحقق من الحساب',
    verifyInstructions: 'أدخل رمز التحقق المرسل إلى بريدك الإلكتروني لتفعيل حسابك.',
    verifyingEmail: 'التحقق من البريد الإلكتروني',
    resendCode: 'إعادة إرسال الرمز',
    updateProfile: 'تحديث ملفك الشخصي',
    update: 'تحديث',
    logOut: 'تسجيل الخروج',
    userRole: 'دور المستخدم',
    roleUser: 'مستخدم عادي',
    roleLandlord: 'مالك مستأجر',
    rolePropertyManager: 'مدير عقارات',
    roleOwner: 'مالك العقار',
    roleAppraiser: 'مقيم عقاري',
    roleDataEntry: 'أخصائي إدخال بيانات',
    roleHelp: 'يحدد دورك الإجراءات التي يمكنك تنفيذها في النظام',
    fullName: 'الاسم الكامل',
    rememberMe: 'تذكرنى',
    resetCode: 'رمز إعادة التعيين',
    newPassword: 'كلمة المرور الجديدة',
    enterNewPassword: 'أدخل كلمة المرور الجديدة الخاصة بك',
    resetPasswordFor: 'إعادة تعيين كلمة المرور لـ',
    resetLinkSent: 'تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني',
    verificationCodeResent: 'تم إعادة إرسال رمز التحقق إلى بريدك الإلكتروني',
    registrationSuccess: 'تم التسجيل بنجاح! يرجى مراجعة بريدك الإلكتروني للحصول على تعليمات التحقق.',
    passwordResetSuccess: 'تم إعادة تعيين كلمة المرور الخاصة بك بنجاح.',

    passwordStrength: {
      label: 'قوة كلمة المرور',
      weak: 'ضعيفة',
      fair: 'مقبولة',
      good: 'جيدة',
      strong: 'قوية',
      veryStrong: 'قوية جداً'
    },
    
    // Password Requirements
    passwordRequirements: {
      title: 'متطلبات كلمة المرور',
      minLength: '8 أحرف على الأقل',
      uppercase: 'حرف كبير واحد',
      lowercase: 'حرف صغير واحد',
      number: 'رقم واحد',
      special: 'رمز خاص واحد',
      noCommon: 'ليست كلمة مرور شائعة'
    },
    
    // Password Validation Messages
    passwordValidation: {
      tooShort: 'يجب أن تكون كلمة المرور 8 أحرف على الأقل',
      tooLong: 'لا يمكن أن تتجاوز كلمة المرور 128 حرف',
      noUppercase: 'يجب أن تحتوي كلمة المرور على حرف كبير واحد على الأقل',
      noLowercase: 'يجب أن تحتوي كلمة المرور على حرف صغير واحد على الأقل',
      noNumber: 'يجب أن تحتوي كلمة المرور على رقم واحد على الأقل',
      noSpecial: 'يجب أن تحتوي كلمة المرور على رمز خاص واحد على الأقل',
      tooCommon: 'كلمة المرور هذه شائعة جداً، يرجى اختيار كلمة مرور أخرى',
      containsEmail: 'لا يمكن أن تحتوي كلمة المرور على عنوان بريدك الإلكتروني',
      containsName: 'لا يمكن أن تحتوي كلمة المرور على اسمك'
    },
    
    // Form Validation Messages
    validation: {
      firstNameRequired: 'الاسم الأول مطلوب',
      lastNameRequired: 'الاسم الأخير مطلوب',
      passwordMismatch: 'كلمات المرور غير متطابقة',
      emailRequired: 'البريد الإلكتروني مطلوب',
      emailInvalid: 'البريد الإلكتروني غير صالح',
      passwordRequired: 'كلمة المرور مطلوبة',
      phoneRequired: 'رقم الهاتف مطلوب',
      phoneInvalid: 'رقم الهاتف غير صالح',
      codeInvalid: 'رمز التحقق غير صالح',
      codeRequired: 'رمز التحقق مطلوب',
      emailVerified: '',
      passwordMinLength: ''
      
    },
    
    // Additional Auth Messages
    passwordHint: 'استخدم مزيجاً من الأحرف والأرقام والرموز للحصول على كلمة مرور قوية',
    showPassword: 'إظهار كلمة المرور',
    hidePassword: 'إخفاء كلمة المرور',
    passwordVisible: 'كلمة المرور مرئية',
    passwordHidden: 'كلمة المرور مخفية',
    
    // Account Status
    accountStatus: {
      active: 'نشط',
      inactive: 'غير نشط',
      suspended: 'معلق',
      pending: 'في انتظار التحقق',
      banned: 'محظور'
    },
    
    // Roles
    roleAdmin: 'مدير',
    roleModerator: 'مشرف',
    roleUser: 'مستخدم',
    roleSeller: 'بائع',
    roleBuyer: 'مشتري',
    roleAgent: 'وكيل',
    roleUndefined: 'غير محدد',
    roleundefinedundefined: 'غير محدد',
    
    // Security
    security: {
      title: 'أمان الحساب',
      twoFactor: 'المصادقة الثنائية',
      loginHistory: 'سجل تسجيل الدخول',
      activeSession: 'الجلسات النشطة',
      changePassword: 'تغيير كلمة المرور',
      deleteAccount: 'حذف الحساب'
    }
  },

  profile: {
    myProfile: 'ملفي الشخصي',
    personalInfo: 'المعلومات الشخصية',
    contactInfo: 'معلومات الاتصال',
    companyInfo: 'معلومات الشركة',
    preferenceInfo: 'التفضيلات',
    bio: 'نبذة تعريفية',
    companyName: 'اسم الشركة',
    companyRegistration: 'تسجيل الشركة',
    taxId: 'الرقم الضريبي',
    address: 'العنوان',
    city: 'المدينة',
    state: 'الولاية/المحافظة',
    postalCode: 'الرمز البريدي',
    country: 'الدولة',
    licenseNumber: 'رقم الترخيص',
    licenseExpiry: 'تاريخ انتهاء الترخيص',
    preferredLocations: 'المواقع المفضلة',
    propertyPreferences: 'تفضيلات العقارات',
    changePassword: 'تغيير كلمة المرور',
    currentPassword: 'كلمة المرور الحالية',
    newPassword: 'كلمة المرور الجديدة',
    confirmNewPassword: 'تأكيد كلمة المرور الجديدة',
    myProperties: 'عقاراتي',
    myAuctions: 'مزاداتي',
    myBids: 'مزايداتي',
    addProperty: 'إضافة عقار جديد',
    addAuction: 'إنشاء مزاد جديد',
    personalDetails: 'التفاصيل الشخصية ومعلومات الاتصال',
    notProvided: 'غير محدد',
    memberSince: 'عضو منذ',
    addressInfo: 'معلومات العنوان',
    addressInfoDesc: 'عنوانك الحالي ومعلومات الموقع',
    editProfile: 'تعديل الملف الشخصي',
    passwordChangeSuccess: 'تم تغيير كلمة المرور بنجاح',
    updateSuccess: 'تم تحديث الملف الشخصي بنجاح',
    changePasswordDesc: 'تأكد من أن حسابك آمن بكلمة مرور قوية',
    commaSeparated: 'مفصولة بفواصل'
  },

  error: {
    generic: 'حدث خطأ',
    notFound: 'الصفحة غير موجودة',
    unauthorized: 'وصول غير مصرح به',
    invalidCredentials: 'بريد إلكتروني أو كلمة مرور غير صحيحة',
    emailTaken: 'البريد الإلكتروني مستخدم بالفعل',
    weakPassword: 'كلمة المرور ضعيفة جداً',
    passwordMismatch: 'كلمات المرور غير متطابقة',
    serverError: 'خطأ في الخادم، يرجى المحاولة مرة أخرى لاحقاً',
    invalidToken: 'رمز غير صالح أو منتهي الصلاحية',
    notVerified: 'البريد الإلكتروني غير مؤكد',
    forbidden: 'الوصول محظور',
    noResults: 'لم يتم العثور على نتائج',
    title: 'خطأ',
    fetchFailed: 'فشل في جلب البيانات',
    validationFailed: 'فشل التحقق من صحة البيانات',
    bidFailed: 'فشل في تقديم العرض',
    registrationFailed: 'فشل التسجيل',
    profileLoadFailed: 'فشل في تحميل الملف الشخصي',
    profileUpdateFailed: 'فشل في تحديث الملف الشخصي',
    passwordChangeFailed: 'فشل في تغيير كلمة المرور',
    resetRequestFailed: 'فشل في طلب إعادة تعيين كلمة المرور',
    resetFailed: 'فشل في إعادة تعيين كلمة المرور',
    verificationFailed: 'فشل التحقق',
    resendVerificationFailed: 'فشل في إعادة إرسال رمز التحقق',
    sendingFailed: "فشل في إرسال الرسالة"
  },

  footer: {
    about: 'حول',
    aboutText: 'نحن منصة رائدة لمزادات العقارات تربط بين المشترين والبائعين للعقارات السكنية والتجارية والأراضي.',
    quickLinks: 'روابط سريعة',
    support: 'الدعم',
    help: 'المساعدة',
    faq: 'الأسئلة الشائعة',
    links: 'روابط سريعة',
    legal: 'قانوني',
    terms: 'الشروط والأحكام',
    privacy: 'سياسة الخصوصية',
    cookies: 'سياسة ملفات تعريف الارتباط',
    contact: 'اتصل بنا',
    rights: 'جميع الحقوق محفوظة',
    madeBy: 'صُنع بواسطة',
    followUs: 'تابعنا على',
    newsletter: {
      title: 'ابق على اطلاع',
      description: 'احصل على آخر العقارات والمزادات مباشرة في بريدك الإلكتروني',
      placeholder: 'أدخل بريدك الإلكتروني',
      subscribe: 'اشتراك'
    }
  },

  hero: {
    discover: 'اكتشف',
    premium: 'الفاخرة',
    realEstate: 'العقارات',
    throughAuctions: 'عبر المزادات الذكية',
    subtitle: 'انضم إلى آلاف المستثمرين العقاريين في مزادات شفافة وآمنة للعقارات السكنية والتجارية',
    verified: 'موثقة 100%',
    liveAuctions: 'مزادات مباشرة',
    users: 'أكثر من 15 ألف مستخدم',
    viewAuctions: 'عرض المزادات',
    browseProperties: 'تصفح العقارات'
  },

dashboard: {
  title: 'لوحة التحكم',
  description: 'إدارة العقارات والمزادات والحساب',
  welcome: 'مرحباً بعودتك، {name}!',
  
  // Stats
  totalProperties: 'إجمالي العقارات',
  totalAuctions: 'إجمالي المزادات',
  totalBids: 'إجمالي المزايدات',
  unreadMessages: 'الرسائل غير المقروءة',
  publishedProperties: 'منشورة',
  activeAuctions: 'نشطة',
  winningBids: 'فائزة',
  
  // Performance
  performanceMetrics: 'مقاييس الأداء',
  propertiesThisMonth: 'العقارات هذا الشهر',
  auctionsThisMonth: 'المزادات هذا الشهر',
  avgPropertyValue: 'متوسط قيمة العقار',
  
  // Actions
  quickActions: 'إجراءات سريعة',
  browseProperties: 'تصفح العقارات',
  viewAuctions: 'عرض المزادات',
  addProperty: 'إضافة عقار',

  createAuction: 'إنشاء مزاد',
  
  // Activity
  recentActivity: 'النشاط الأخير',
  noRecentActivity: 'لا يوجد نشاط حديث',
  totalUsers: 'إجمالي المستخدمين',
  verifiedUsers: 'المستخدمين الموثوق بهم',
  
  // System
  systemDashboard: 'لوحة تحكم النظام',
  userPriority: 'أولوية المستخدم',
  
  // Properties
  properties: 'عقاراتي',
  manageProperties: 'إدارة قوائم العقارات الخاصة بك',
  noProperties: 'لم يتم العثور على عقارات',
  noPropertiesDesc: 'لم تقم بإضافة أي عقارات بعد. أنشئ أول قائمة عقار للبدء.',
  
  // Auctions
  auctions: 'مزاداتي',
  manageAuctions: 'إدارة قوائم المزادات الخاصة بك',
  noAuctions: 'لم يتم العثور على مزادات',
  noAuctionsDesc: 'لم تقم بإنشاء أي مزادات بعد. ابدأ مزاداً لأحد عقاراتك.',
  
  // Bids
  bids: 'مزايداتي',
  manageBids: 'عرض وإدارة مزايداتك',
  noBids: 'لم يتم العثور على مزايدات',
  noBidsDesc: 'لم تقم بتقديم أي مزايدات بعد. تصفح المزادات النشطة لبدء المزايدة.',
  
  // Status
  verified: 'موثق',
  unverified: 'غير موثق',
  showing: 'عرض',
  
  // Messages
  loadError: 'فشل في تحميل بيانات لوحة التحكم',
  refreshed: 'تم تحديث لوحة التحكم بنجاح',
  refreshError: 'فشل في تحديث لوحة التحكم',
  loadPropertiesError: 'فشل في تحميل العقارات',
  loadAuctionsError: 'فشل في تحميل المزادات',
  loadBidsError: 'فشل في تحميل المزايدات',


  // System Dashboard
  systemOverview: 'نظرة عامة وإحصائيات النظام',
  userStatistics: 'إحصائيات المستخدمين',
  propertyStatistics: 'إحصائيات العقارات',
  auctionStatistics: 'إحصائيات المزادات',
  biddingStatistics: 'إحصائيات المزايدات',
  
  // System Stats
  activeToday: 'نشط اليوم',
  newThisWeek: 'جديد هذا الأسبوع',
  completedAuctions: 'مكتملة',
  totalAuctionValue: 'إجمالي قيمة المزادات',
  uniqueBidders: 'مزايدون فريدون',
  totalBidValue: 'إجمالي قيمة المزايدات',
  avgBidAmount: 'متوسط مبلغ المزايدة',
  
  // Activity
  todayActivity: 'نشاط اليوم',
  bidsToday: 'مزايدات اليوم',
  auctionsEndingSoon: 'مزادات تنتهي قريباً',
  pendingVerifications: 'تحققات معلقة',
  topCities: 'أهم المدن',
  noData: 'لا توجد بيانات متاحة',
  
  // Common
  viewAll: 'عرض الكل',
  daysAgo: 'أيام مضت',
  to: 'إلى',
  of: 'من',
  yes: 'نعم',
  no: 'لا',
  view: 'عرض',
  activeOnly: 'النشطة فقط',
  winningOnly: 'الفائزة فقط',
  maxBid: 'أعلى مزايدة',
  viewAuction: 'عرض المزاد'
  },

  core: {
    title: 'إدارة العقارات',
    subtitle: 'إدارة شاملة للعقارات والعمليات',
    
    // Navigation
    nav: {
      dashboard: 'لوحة التحكم',
      dashboardDesc: 'نظرة عامة والتحليلات',
      financial: 'المالية',
      financialDesc: 'المعاملات والمصروفات',
      rentals: 'الإيجارات',
      rentalsDesc: 'العقارات وعقود الإيجار',
      maintenance: 'الصيانة',
      maintenanceDesc: 'الطلبات والموردين',
      contracts: 'العقود',
      contractsDesc: 'القوالب والاتفاقيات',
      analytics: 'التحليلات',
      analyticsDesc: 'التقارير والرؤى'
    },

    // Layout
    layout: {
      title: 'إدارة العقارات'
    },

    // Dashboard
    dashboard: {
      title: 'لوحة تحكم إدارة العقارات',
      subtitle: 'نظرة شاملة على محفظة العقارات والعمليات',
      totalProperties: 'إجمالي العقارات',
      monthlyIncome: 'الدخل الشهري',
      occupancyRate: 'معدل الإشغال',
      pendingMaintenance: 'الصيانة المعلقة',
      refresh: 'تحديث',
      viewReports: 'عرض التقارير',
      
      tabs: {
        overview: 'نظرة عامة',
        financial: 'المالية',
        maintenance: 'الصيانة',
        leases: 'عقود الإيجار',
        contracts: 'العقود'
      },

      portfolioOverview: 'نظرة عامة على المحفظة',
      rentalProperties: 'العقارات المؤجرة',
      occupied: 'مؤجرة',
      vacant: 'شاغرة',
      financialPerformance: 'الأداء المالي',
      ytdIncome: 'دخل العام حتى الآن',
      ytdExpenses: 'مصروفات العام حتى الآن',
      netProfit: 'صافي الربح',
      quickActions: 'إجراءات سريعة',
      addTransaction: 'إضافة معاملة',
      newMaintenanceRequest: 'طلب صيانة جديد',
      createContract: 'إنشاء عقد',
      
      overviewCharts: 'سيتم عرض الرسوم البيانية والملخصات العامة هنا',
      maintenanceOverview: 'سيتم عرض ملخص طلبات الصيانة والنشاط الأخير هنا',
      leaseOverview: 'سيتم عرض نظرة عامة على حالة الإيجار والعقود المنتهية الصلاحية هنا',
      contractOverview: 'سيتم عرض نظرة عامة على حالة العقود والتوقيعات المعلقة هنا',
      viewDetails: 'عرض التفاصيل',
      viewAllRequests: 'عرض جميع الطلبات',
      manageLeases: 'إدارة عقود الإيجار',
      viewContracts: 'عرض العقود'
    },

    // Financial Management
    financial: {
      title: 'الإدارة المالية',
      subtitle: 'إدارة المعاملات والمصروفات والتقارير المالية',
      
      // Stats
      totalIncome: 'إجمالي الدخل',
      totalExpenses: 'إجمالي المصروفات',
      netIncome: 'صافي الدخل',
      monthlyIncome: 'الدخل الشهري',
      monthlyExpenses: 'المصروفات الشهرية',
      ytdIncome: 'دخل العام حتى الآن',
      ytdExpenses: 'مصروفات العام حتى الآن',
      
      // Transactions
      transactions: 'المعاملات',
      expenses: 'المصروفات',
      transaction: 'معاملة',
      expense: 'مصروف',
      newTransaction: 'معاملة جديدة',
      transactionType: 'نوع المعاملة',
      income: 'دخل',
      amount: 'المبلغ',
      description: 'الوصف',
      category: 'الفئة',
      date: 'التاريخ',
      property: 'العقار',
      dueDate: 'تاريخ الاستحقاق',
      expenseDate: 'تاريخ المصروف',
      vendorName: 'اسم المورد',
      vendor: 'المورد',
      due: 'مستحق',
      reference: 'مرجع',
      selectType: 'اختر النوع',
      selectCategory: 'اختر الفئة',
      
      // Transaction Types
      transactionTypes: {
        rentPayment: 'دفع إيجار',
        securityDeposit: 'تأمين',
        maintenanceCost: 'تكلفة صيانة',
        auctionPayment: 'دفع مزاد',
        commission: 'عمولة',
        utilityBill: 'فاتورة مرافق',
        insurance: 'تأمين',
        taxPayment: 'دفع ضرائب',
        other: 'أخرى'
      },
      
      // Categories
      categories: {
        rent: 'إيجار',
        utilities: 'المرافق',
        maintenance: 'الصيانة',
        insurance: 'التأمين',
        taxes: 'الضرائب',
        management: 'الإدارة',
        marketing: 'التسويق',
        legal: 'قانوني',
        other: 'أخرى'
      },

      // Status
      status: {
        pending: 'معلق',
        completed: 'مكتمل',
        failed: 'فشل',
        overdue: 'متأخر'
      },

      // Filters
      filters: {
        allTypes: 'جميع الأنواع',
        allCategories: 'جميع الفئات',
        allProperties: 'جميع العقارات',
        allStatus: 'جميع الحالات',
        dateFrom: 'من تاريخ',
        dateTo: 'إلى تاريخ'
      },

      // Sort
      sort: {
        newest: 'الأحدث',
        oldest: 'الأقدم',
        amountHigh: 'المبلغ: عالي',
        amountLow: 'المبلغ: منخفض'
      },

      noTransactions: 'لم يتم العثور على معاملات',
      addFirstTransaction: 'أضف معاملتك الأولى للبدء',
      noItemsFound: 'لم يتم العثور على {type}',
      createFirstItem: 'ابدأ بإنشاء {type} الأول'
    },

    // Rental Management
    rentals: {
      title: 'إدارة الإيجارات',
      subtitle: 'إدارة العقارات المؤجرة وعقود الإيجار وعلاقات المستأجرين',
      
      // Actions
      addProperty: 'إضافة عقار',
      convertToRental: 'تحويل إلى إيجار',
      convertPropertyToRental: 'تحويل العقار إلى إيجار',
      createRentalProperty: 'إنشاء عقار للإيجار',
      selectProperty: 'اختر عقار',
      
      // Stats
      totalProperties: 'إجمالي العقارات',
      occupiedProperties: 'العقارات المؤجرة',
      vacantProperties: 'العقارات الشاغرة',
      occupied: 'مؤجر',
      vacant: 'شاغر',
      activeLeases: 'عقود الإيجار النشطة',
      expiringLeases: 'عقود الإيجار المنتهية الصلاحية',
      expiringSoon: 'تنتهي قريباً',
      within30Days: 'خلال 30 يوم',
      occupancyRate: 'معدل الإشغال',
      occupancyPercent: '{rate}% إشغال',
      monthlyIncome: 'الدخل الشهري',
      
      // Properties
      properties: 'العقارات',
      property: 'عقار',
      newProperty: 'عقار جديد',
      propertyName: 'اسم العقار',
      address: 'العنوان',
      noAddress: 'لا يوجد عنوان',
      untitledProperty: 'عقار بدون عنوان',
      type: 'النوع',
      status: 'الحالة',
      rent: 'الإيجار',
      tenant: 'المستأجر',
      currentTenant: 'المستأجر الحالي',
      rentalPropertiesCount: 'العقارات المؤجرة ({count})',
      bedrooms: 'غرف النوم',
      bathrooms: 'الحمامات',
      bedsBaths: 'غرف/حمامات',
      furnished: 'مفروش',
      petsAllowed: 'الحيوانات الأليفة مسموحة',
      petsOK: 'حيوانات مسموحة',
      availableDate: 'تاريخ الإتاحة',
      
      // Leases
      leases: 'عقود الإيجار',
      lease: 'عقد إيجار',
      newLease: 'عقد إيجار جديد',
      leaseStatus: 'حالة عقد الإيجار',
      leaseAgreementsCount: 'اتفاقيات الإيجار ({count})',
      startDate: 'تاريخ البداية',
      endDate: 'تاريخ النهاية',
      term: 'المدة',
      monthlyRent: 'الإيجار الشهري',
      securityDeposit: 'التأمين',
      perMonth: 'شهرياً',
      leaseExpiresIn: 'ينتهي عقد الإيجار خلال {days} يوم',
      daysRemaining: '{days} يوم متبقي',
      yieldPercent: '{yield}% عائد',
      
      // Rental Types
      rentalType: 'نوع الإيجار',
      rentalTypes: {
        longTerm: 'طويل المدى',
        shortTerm: 'قصير المدى',
        vacation: 'إجازة',
        commercial: 'تجاري',
        longTermRental: 'إيجار طويل المدى',
        shortTermRental: 'إيجار قصير المدى',
        vacationRental: 'إيجار إجازة',
        commercialRental: 'إيجار تجاري'
      },
      
      // Status
      statuses: {
        available: 'متاح',
        occupied: 'مؤجر',
        maintenance: 'تحت الصيانة',
        active: 'نشط',
        expired: 'منتهي الصلاحية',
        terminated: 'منتهي'
      },

      // Filters
      filters: {
        allTypes: 'جميع الأنواع',
        allStatus: 'جميع الحالات'
      },

      // Sort
      sort: {
        newest: 'الأحدث',
        oldest: 'الأقدم',
        rentHigh: 'الإيجار: عالي',
        rentLow: 'الإيجار: منخفض'
      },

      noProperties: 'لم يتم العثور على عقارات',
      addFirstProperty: 'أضف عقارك الأول للبدء',
      noItemsFound: 'لم يتم العثور على {type}',
      createFirstItem: 'ابدأ بإنشاء {type} الأول'
    },

    // Maintenance Management
    maintenance: {
      title: 'إدارة الصيانة',
      subtitle: 'إدارة طلبات الصيانة والموردين وأوامر العمل',
      
      // Actions
      manageVendors: 'إدارة الموردين',
      newRequest: 'طلب جديد',
      newMaintenanceRequest: 'طلب صيانة جديد',
      createRequest: 'إنشاء طلب',
      selectProperty: 'اختر عقار',
      selectCategory: 'اختر فئة',
      
      // Stats
      totalRequests: 'إجمالي الطلبات',
      pending: 'معلق',
      inProgress: 'قيد التنفيذ',
      completed: 'مكتمل',
      emergency: 'طارئ',
      ytdCost: 'تكلفة العام',
      pendingRequests: 'معلقة',
      inProgressRequests: 'قيد التنفيذ',
      completedRequests: 'مكتملة',
      emergencyRequests: 'طارئة',
      totalCostYTD: 'إجمالي التكلفة للعام',
      
      // Navigation
      maintenanceRequestsCount: 'طلبات الصيانة ({count})',
      vendorsCount: 'الموردين ({count})',
      
      // Requests
      requests: 'طلبات الصيانة',
      request: 'طلب',
      requestTitle: 'عنوان الطلب',
      title: 'العنوان',
      description: 'الوصف',
      priority: 'الأولوية',
      category: 'الفئة',
      status: 'الحالة',
      property: 'العقار',
      unknownProperty: 'عقار غير معروف',
      assignedTo: 'مُسند إلى',
      created: 'تم الإنشاء',
      scheduled: 'مجدول',
      requestedDate: 'تاريخ الطلب',
      scheduledDate: 'التاريخ المجدول',
      estimatedCost: 'التكلفة المقدرة',
      actualCost: 'التكلفة الفعلية',
      estimated: 'مقدر',
      
      // Vendors
      vendors: 'الموردين',
      vendor: 'مورد',
      newVendor: 'مورد جديد',
      vendorName: 'اسم المورد',
      contactInfo: 'معلومات الاتصال',
      contact: 'اتصال',
      phone: 'الهاتف',
      email: 'البريد الإلكتروني',
      rate: 'السعر',
      rating: 'التقييم',
      specialties: 'التخصصات',
      preferredVendor: 'مورد مفضل',
      license: 'الرخصة: {number}',
      notSpecified: 'غير محدد',
      
      // Vendor Status
      vendorStatus: {
        active: 'نشط',
        inactive: 'غير نشط'
      },
      
      // Priority levels
      priorities: {
        low: 'منخفضة',
        medium: 'متوسطة',
        high: 'عالية',
        emergency: 'طارئة'
      },

      // Categories
      categories: {
        plumbing: 'السباكة',
        electrical: 'الكهرباء',
        hvac: 'التكييف والتهوية',
        appliances: 'الأجهزة',
        structural: 'هيكلي',
        flooring: 'الأرضيات',
        painting: 'الدهان',
        roofing: 'الأسقف',
        other: 'أخرى'
      },

      // Status
      status: {
        submitted: 'مُقدم',
        inProgress: 'قيد التنفيذ',
        completed: 'مكتمل',
        cancelled: 'ملغي'
      },
      
      statuses: {
        submitted: 'مُقدم',
        in_progress: 'قيد التنفيذ',
        completed: 'مكتمل',
        cancelled: 'ملغي'
      },

      // Filters
      filters: {
        allStatus: 'جميع الحالات',
        allPriority: 'جميع الأولويات',
        allCategories: 'جميع الفئات'
      },

      noRequests: 'لم يتم العثور على طلبات صيانة',
      addFirstRequest: 'قدم طلب الصيانة الأول',
      noItemsFound: 'لم يتم العثور على {type}',
      createFirstItem: 'ابدأ بإنشاء {type} الأول'
    },

    // Contract Management
    contracts: {
      title: 'إدارة العقود',
      subtitle: 'إدارة العقود والقوالب والاتفاقيات القانونية',
      
      // Navigation
      contractsCount: 'العقود ({count})',
      templatesCount: 'القوالب ({count})',
      
      // Stats
      totalContracts: 'إجمالي العقود',
      active: 'نشطة',
      draft: 'مسودة',
      signed: 'موقعة',
      expired: 'منتهية الصلاحية',
      templates: 'القوالب',
      
      // Contracts
      contracts: 'العقود',
      contract: 'عقد',
      template: 'قالب',
      newContract: 'عقد جديد',
      contractTitle: 'عنوان العقد',
      description: 'الوصف',
      parties: 'الأطراف',
      partiesInvolved: 'الأطراف المشاركة',
      partiesPlaceholder: 'مثال: أحمد محمد، شركة إدارة العقارات',
      terms: 'الشروط',
      startDate: 'تاريخ البداية',
      endDate: 'تاريخ النهاية',
      contractValue: 'قيمة العقد',
      created: 'تم الإنشاء',
      
      // Templates
      selectTemplate: 'اختر قالب',
      useTemplate: 'استخدام القالب',
      
      // Form Labels
      status: {
        label: 'الحالة',
        draft: 'مسودة',
        active: 'نشط',
        signed: 'موقع',
        expired: 'منتهي الصلاحية',
        terminated: 'منتهي'
      },

      // Actions
      createContract: 'إنشاء عقد',
      
      // Filters
      filters: {
        allStatus: 'جميع الحالات'
      },
      
      // Empty states
      noItemsFound: 'لم يتم العثور على {type}',
      createFirstItem: 'ابدأ بإنشاء {type} الأول'
    },

    // Analytics
    analytics: {
      title: 'التحليلات والتقارير',
      subtitle: 'رؤى شاملة حول أداء إدارة العقارات',
      
      // Stats
      totalRevenue: 'إجمالي الإيرادات',
      totalExpenses: 'إجمالي المصروفات',
      netIncome: 'صافي الدخل',
      occupancyRate: 'معدل الإشغال',
      maintenanceRequests: 'طلبات الصيانة',
      activeLeases: 'عقود الإيجار النشطة',
      
      // Tabs
      tabs: {
        overview: 'نظرة عامة',
        financial: 'المالية',
        maintenance: 'الصيانة',
        occupancy: 'الإشغال'
      },

      // Date ranges
      dateRanges: {
        last7Days: 'آخر 7 أيام',
        last30Days: 'آخر 30 يوم',
        last90Days: 'آخر 90 يوم',
        lastYear: 'العام الماضي'
      },

      exportReport: 'تصدير التقرير',
      
      // Charts
      revenueVsExpenses: 'الإيرادات مقابل المصروفات',
      propertyPerformance: 'أداء العقارات',
      maintenanceResponse: 'استجابة الصيانة',
      tenantSatisfaction: 'رضا المستأجرين',
      
      // Financial
      financialTrends: 'اتجاهات مالية',
      
      // Maintenance
      maintenanceRequestTrends: 'اتجاهات طلبات الصيانة',
      
      // Occupancy
      currentOccupancy: 'الإشغال الحالي',
      avgLeaseDuration: 'متوسط مدة الإيجار',
      occupancyTrends: 'اتجاهات الإشغال',
      
      chartsPlaceholder: 'سيتم عرض الرسم البياني هنا',
      financialChartsPlaceholder: 'سيتم عرض الرسم البياني للاتجاهات المالية هنا',
      maintenanceChartsPlaceholder: 'سيتم عرض الرسم البياني لاتجاهات الصيانة هنا',
      occupancyChartsPlaceholder: 'سيتم عرض الرسم البياني لاتجاهات الإشغال هنا'
    },

    // Common elements
    common: {
      search: 'بحث',
      filter: 'تصفية',
      sort: 'ترتيب',
      export: 'تصدير',
      print: 'طباعة',
      save: 'حفظ',
      cancel: 'إلغاء',
      edit: 'تعديل',
      view: 'عرض',
      delete: 'حذف',
      create: 'إنشاء',
      add: 'إضافة',
      update: 'تحديث',
      loading: 'جاري التحميل...',
      noData: 'لا توجد بيانات متاحة',
      tryAgain: 'حاول مرة أخرى',
      
      // Sorting
      sortBy: 'ترتيب حسب',
      newest: 'الأحدث',
      oldest: 'الأقدم',
      nameAsc: 'الاسم أ-ي',
      nameDesc: 'الاسم ي-أ',
      amountAsc: 'المبلغ من الأقل للأعلى',
      amountDesc: 'المبلغ من الأعلى للأقل',
      
      // Filters
      allStatus: 'جميع الحالات',
      allCategories: 'جميع الفئات',
      allTypes: 'جميع الأنواع',
      allPriorities: 'جميع الأولويات',
      
      // Actions
      viewDetails: 'عرض التفاصيل',
      viewAll: 'عرض الكل',
      manageAll: 'إدارة الكل',
      
      // Forms
      required: 'مطلوب',
      optional: 'اختياري',
      selectOption: 'اختر خيار',
      enterValue: 'أدخل القيمة'
    },

    // Error messages
    errors: {
      loadFailed: 'فشل في تحميل البيانات',
      saveFailed: 'فشل في الحفظ',
      deleteFailed: 'فشل في الحذف',
      updateFailed: 'فشل في التحديث',
      permissionDenied: 'تم رفض الصلاحية',
      networkError: 'خطأ في الشبكة'
    },

    // Success messages
    success: {
      saved: 'تم الحفظ بنجاح',
      deleted: 'تم الحذف بنجاح',
      updated: 'تم التحديث بنجاح',
      created: 'تم الإنشاء بنجاح'
    }
  }
};