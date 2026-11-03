export default {
  // Navigation
  nav: {
    overview: '概要',
    inventory: '在庫',
    orders: '注文',
    finance: '財務',
    demandForecast: '需要予測',
    restocking: '在庫補充',
    reports: 'レポート',
    companyName: '触媒コンポーネンツ',
    subtitle: '在庫管理システム'
  },

  // Dashboard
  dashboard: {
    title: '概要',
    kpi: {
      title: '主要業績評価指標',
      inventoryTurnover: '在庫回転率',
      ordersFulfilled: '注文履行数',
      orderFillRate: '注文充足率',
      revenue: '収益（注文）',
      revenueYTD: '収益（注文）年初来',
      revenueMTD: '収益（注文）月初来',
      avgDeliveryTime: '平均配送時間（日）',
      promisedLeadTime: '約束リードタイム',
      goal: '目標'
    },
    summary: {
      title: '概要'
    },
    orderHealth: {
      title: '注文状況',
      totalOrders: '総注文数',
      revenue: '収益',
      avgOrderValue: '平均注文額',
      onTimeRate: '定時配達率',
      avgFulfillmentDays: '平均履行日数',
      total: '合計'
    },
    ordersByMonth: {
      title: '月別注文数'
    },
    inventoryValue: {
      title: 'カテゴリ別在庫価値'
    },
    inventoryShortages: {
      title: '在庫不足',
      viewAll: 'すべて表示',
      noShortages: '在庫不足なし - すべての注文を履行できます！',
      noData: '選択したフィルターのデータがありません',
      orderId: '注文ID',
      sku: 'SKU',
      itemName: '品目名',
      quantityNeeded: '必要数量',
      quantityAvailable: '在庫数量',
      shortage: '不足',
      daysDelayed: '遅延日数',
      priority: '優先度',
      unitsShort: '単位不足',
      days: '{count}日'
    },
    topProducts: {
      title: '収益別トップ製品',
      sku: 'SKU',
      product: '製品',
      category: 'カテゴリ',
      warehouse: '倉庫',
      stockStatus: '在庫状況',
      revenue: '収益',
      unitsOrdered: '注文数量',
      firstOrder: '初回注文',
      inStock: '在庫あり',
      lowStock: '在庫僅少'
    }
  },

  // Inventory
  inventory: {
    title: '在庫',
    description: 'すべての在庫品目の追跡と管理',
    stockLevels: '在庫レベル',
    skus: 'SKU',
    searchPlaceholder: '品目名で検索...',
    clearSearch: '検索をクリア',
    totalItems: '総品目数',
    totalValue: '総価値',
    lowStockItems: '在庫僅少品目',
    warehouses: '倉庫',
    table: {
      sku: 'SKU',
      itemName: '品目名',
      name: '名前',
      category: 'カテゴリ',
      warehouse: '倉庫',
      quantity: '数量',
      quantityOnHand: '手持在庫数',
      reorderPoint: '再注文点',
      unitCost: '単価',
      unitPrice: '単価',
      totalValue: '総価値',
      location: '場所',
      status: 'ステータス'
    }
  },

  // Orders
  orders: {
    title: '注文',
    description: '顧客注文の表示と管理',
    allOrders: 'すべての注文',
    totalOrders: '総注文数',
    totalRevenue: '総収益',
    avgOrderValue: '平均注文額',
    onTimeDelivery: '定時配達',
    itemsCount: '{count}件',
    quantity: '数量',
    submittedOrders: '発注済み補充注文',
    noSubmittedOrders: '発注済みの補充注文はまだありません。',
    leadTimeDays: '{days}日',
    table: {
      leadTime: 'リードタイム',
      totalCost: '合計金額',
      orderNumber: '注文番号',
      orderId: '注文ID',
      orderDate: '注文日',
      date: '日付',
      customer: '顧客',
      category: 'カテゴリ',
      warehouse: '倉庫',
      items: '品目',
      value: '価格',
      totalValue: '合計金額',
      status: 'ステータス',
      expectedDelivery: '予定配達日',
      actualDelivery: '実際の配達日'
    }
  },

  // Finance/Spending
  finance: {
    title: '財務ダッシュボード',
    description: '収益、コスト、財務パフォーマンスの追跡',
    totalRevenue: '総収益',
    totalCosts: '総コスト',
    netProfit: '純利益',
    avgOrderValue: '平均注文額',
    fromOrders: '{count}件の注文から',
    costBreakdown: '調達 + 運営 + 人件費 + 間接費',
    margin: 'マージン',
    perOrderRevenue: '注文あたりの収益',
    revenueVsCosts: {
      title: '月別収益対コスト',
      revenue: '収益',
      costs: '総コスト'
    },
    monthlyCostFlow: {
      title: '月別コストフロー',
      procurement: '調達',
      operational: '運営',
      labor: '人件費',
      overhead: '間接費'
    },
    categorySpending: {
      title: 'カテゴリ別支出',
      ofTotal: '全体の'
    },
    transactions: {
      title: '最近の取引',
      id: 'ID',
      description: '説明',
      vendor: 'ベンダー',
      date: '日付',
      amount: '金額'
    }
  },

  // Demand Forecast
  demand: {
    title: '需要予測',
    description: '需要動向の分析と将来のニーズの予測',
    increasingDemand: '需要増加',
    stableDemand: '需要安定',
    decreasingDemand: '需要減少',
    itemsCount: '{count}件',
    more: 'さらに...',
    demandForecasts: '需要予測',
    table: {
      sku: 'SKU',
      itemName: '品目名',
      currentDemand: '現在の需要',
      forecastedDemand: '予測需要',
      change: '変化',
      trend: 'トレンド',
      period: '期間'
    }
  },

  // Restocking
  restocking: {
    title: '在庫補充',
    description: '予算を設定し、需要予測で優先度の高い品目を発注します',
    budget: '利用可能予算',
    fullRestockCost: '全品目補充コスト: {amount}',
    allocated: '割当額',
    remaining: '残額',
    itemsRecommended: '推奨品目数',
    recommendations: '推奨品目',
    notCovered: 'この予算では{count}品目が対象外です',
    partial: '一部',
    placeOrder: '発注する',
    placing: '発注中...',
    orderPlaced: '発注 {orderNumber} を送信しました。{days}日後に納品予定です。',
    viewInOrders: '注文一覧で表示',
    allStocked: 'すべての予測品目は在庫が十分か、発注済みです。',
    budgetTooLow: '推奨品目を表示するには予算を増やしてください。',
    loadFailed: '在庫補充の推奨品目を読み込めませんでした。',
    orderFailed: '発注できませんでした。もう一度お試しください。',
    table: {
      sku: 'SKU',
      item: '品目',
      trend: '傾向',
      forecast: '予測',
      onHand: '在庫数',
      onOrder: '発注済み数',
      shortfall: '不足数',
      orderQty: '発注数',
      unitCost: '単価',
      lineTotal: '小計',
      leadTime: 'リードタイム'
    }
  },

  // Filters
  filters: {
    timePeriod: '期間',
    location: '場所',
    category: 'カテゴリ',
    orderStatus: '注文ステータス',
    all: 'すべて',
    allMonths: 'すべての月'
  },

  // Statuses
  status: {
    delivered: '配達済み',
    shipped: '出荷済み',
    processing: '処理中',
    backordered: 'バックオーダー',
    submitted: '発注済み',
    inStock: '在庫あり',
    lowStock: '在庫僅少',
    adequate: '適量'
  },

  // Trends
  trends: {
    increasing: '増加',
    stable: '安定',
    decreasing: '減少'
  },

  // Priority
  priority: {
    high: '高',
    medium: '中',
    low: '低'
  },

  // Categories
  categories: {
    circuitBoards: '回路基板',
    sensors: 'センサー',
    actuators: 'アクチュエータ',
    controllers: 'コントローラー',
    powerSupplies: '電源'
  },

  // Spending Categories
  spendingCategories: {
    rawMaterials: '原材料',
    components: '部品',
    equipment: '設備',
    consumables: '消耗品'
  },

  // Warehouses
  warehouses: {
    sanFrancisco: 'サンフランシスコ',
    london: 'ロンドン',
    tokyo: '東京'
  },

  // Months
  months: {
    jan: '1月',
    feb: '2月',
    mar: '3月',
    apr: '4月',
    may: '5月',
    jun: '6月',
    jul: '7月',
    aug: '8月',
    sep: '9月',
    oct: '10月',
    nov: '11月',
    dec: '12月',
    january: '1月',
    february: '2月',
    march: '3月',
    april: '4月',
    june: '6月',
    july: '7月',
    august: '8月',
    september: '9月',
    october: '10月',
    november: '11月',
    december: '12月'
  },

  // Profile Menu
  profile: {
    profileDetails: 'プロフィール詳細',
    myTasks: 'マイタスク',
    logout: 'ログアウト'
  },

  // Profile Details Modal
  profileDetails: {
    title: 'プロフィール詳細',
    email: 'メールアドレス',
    department: '部署',
    location: '勤務地',
    phone: '電話番号',
    joinDate: '入社日',
    employeeId: '社員ID',
    close: '閉じる'
  },

  // Tasks Modal
  tasks: {
    title: 'マイタスク',
    taskTitle: 'タスク名',
    taskTitlePlaceholder: 'タスク名を入力...',
    priority: '優先度',
    dueDate: '期限',
    addTask: 'タスクを追加',
    noTasks: 'タスクがありません。上記からタスクを追加してください！'
  },

  // Language
  language: {
    english: 'English',
    japanese: '日本語',
    selectLanguage: '言語を選択'
  },

  // Common
  common: {
    loading: '読み込み中...',
    error: 'エラー',
    noData: 'データがありません',
    viewDetails: '詳細を見る',
    close: '閉じる',
    save: '保存',
    cancel: 'キャンセル',
    search: '検索',
    filter: 'フィルター',
    export: 'エクスポート',
    items: '件'
  },

  // Product Names
  productNames: {
    'Single Layer PCB Assembly': '単層PCB組立',
    'Dual Layer PCB Assembly': '二層PCB組立',
    'Multi Layer PCB Assembly': '多層PCB組立',
    'Temperature Sensor Module': '温度センサーモジュール',
    'Humidity Sensor Module': '湿度センサーモジュール',
    'Pressure Sensor Module': '圧力センサーモジュール',
    'Proximity Sensor': '近接センサー',
    'Ultrasonic Distance Sensor': '超音波距離センサー',
    'Micro Servo Motor': 'マイクロサーボモータ',
    'Standard Servo Motor': '標準サーボモータ',
    'Stepper Motor NEMA 17': 'ステッピングモータNEMA 17',
    '8-bit Microcontroller': '8ビットマイコン',
    '32-bit ARM Microcontroller': '32ビットARMマイコン',
    'Digital Signal Processor': 'デジタル信号処理装置',
    '3-Axis Accelerometer': '3軸加速度センサー',
    'Gyroscope Module': 'ジャイロスコープモジュール',
    'Light Dependent Resistor': '光依存抵抗器',
    'Coil Spring Heavy Duty': 'コイルばね(重量用)',
    'Compression Spring': '圧縮ばね',
    'PWM Motor Controller': 'PWMモータコントローラ',
    'H-Bridge Motor Driver': 'Hブリッジモータドライバ',
    'Stepper Motor NEMA 23': 'ステッピングモータNEMA 23',
    'Drive Pulley': 'ドライブプーリー',
    'LED Driver IC': 'LEDドライバIC',
    '5V 10A Switching Power Supply': '5V 10Aスイッチング電源',
    '12V 5A Power Supply Module': '12V 5A電源モジュール',
    '24V 3A Industrial Power Supply': '24V 3A産業用電源',
    'Dual Output ±15V Power Supply': 'デュアル出力±15V電源',
    '48V DC Power Supply Unit': '48V DC電源ユニット',
    'USB-C PD 100W Power Supply': 'USB-C PD 100W電源',
    'Battery Backup Power Supply': 'バッテリバックアップ電源',
    'Adjustable Bench Power Supply': '可変ベンチ電源'
  },

  // Customer Names
  customerNames: {
    'MegaCorp Industries': 'メガコープ工業',
    'Elite Systems Corp': 'エリートシステムズ',
    'Horizon Technologies': 'ホライズン技術',
    'FastAssembly Ltd': 'ファストアセンブリー',
    'TechSolutions Group': 'テックソリューションズグループ',
    'Apex Engineering': 'アペックスエンジニアリング',
    'Superior Manufacturing': 'スーペリアマニュファクチャリング',
    'Cascade Manufacturing': 'カスケードマニュファクチャリング',
    'Acme Manufacturing Corp': 'アクメ製造',
    'TechBuild Industries': 'テックビルド工業',
    'Advanced Components Inc': 'アドバンストコンポーネンツ',
    'Premier Industries': 'プレミア工業',
    'Stellar Components Ltd': 'ステラコンポーネンツ',
    'Dynamic Systems Ltd': 'ダイナミックシステムズ'
  },

  // Purchase orders for backlog items (Dashboard shortages table + PurchaseOrderModal)
  purchaseOrders: {
    createPO: '発注書を作成',
    viewPO: '発注書を表示',
    createTitle: '発注書の作成',
    viewTitle: '発注書の詳細',
    close: '閉じる',
    cancel: 'キャンセル',
    submit: '発注書を作成',
    submitting: '作成中...',
    loading: '発注書を読み込み中...',
    sku: 'SKU',
    orderId: '注文ID',
    quantityNeeded: '必要数量',
    quantityAvailable: '利用可能数量',
    shortfall: '不足数',
    supplierName: '仕入先名',
    supplierPlaceholder: '仕入先名を入力',
    quantity: '数量',
    unitCostIn: '単価 ({currency})',
    alreadyExists: 'この品目には既に発注書が存在していました。既存の発注書を表示しています。',
    expectedDelivery: '納品予定日',
    orderTotal: '発注合計',
    notesOptional: '備考 (任意)',
    notesPlaceholder: 'この発注に関する備考を入力',
    poId: '発注書ID',
    status: 'ステータス',
    supplier: '仕入先',
    unitCost: '単価',
    total: '合計',
    createdDate: '作成日',
    notes: '備考',
    noNotes: '備考なし',
    statuses: {
      pending: '保留中'
    },
    errors: {
      supplierRequired: '仕入先名は必須です',
      supplierTooLong: '仕入先名は200文字以内で入力してください',
      quantityInvalid: '0より大きい整数を入力してください',
      unitCostInvalid: '0より大きい金額を入力してください',
      deliveryRequired: '納品予定日を選択してください',
      notesTooLong: '備考は1000文字以内で入力してください',
      createFailed: '発注書の作成に失敗しました。もう一度お試しください。',
      loadFailed: '発注書の読み込みに失敗しました。',
      notFound: 'この商品の発注書が見つかりません。'
    }
  },

  // Performance reports view (views/Reports.vue)
  reports: {
    title: 'パフォーマンスレポート',
    description: '四半期ごとの業績指標と月次トレンドを表示します',
    loading: 'レポートを読み込み中...',
    loadFailed: 'レポートの読み込みに失敗しました: {message}',
    // Quarter values arrive from the API as "Q1-2025"; these templates rebuild that label per locale
    quarterLabel: '{year}年第{quarter}四半期',
    // {month} is the localized month name from months.* (already "1月"), so only the year is prefixed
    monthLabel: '{year}年{month}',
    quarterly: {
      title: '四半期業績',
      quarter: '四半期',
      totalOrders: '総注文数',
      totalRevenue: '総収益',
      avgOrderValue: '平均注文額',
      fulfillmentRate: '履行率'
    },
    monthlyTrend: {
      title: '月次収益推移'
    },
    monthOverMonth: {
      title: '前月比分析',
      month: '月',
      orders: '注文数',
      revenue: '収益',
      change: '変化',
      growthRate: '成長率'
    },
    stats: {
      totalRevenueYtd: '総収益（年初来）',
      avgMonthlyRevenue: '月平均収益',
      totalOrdersYtd: '総注文数（年初来）',
      bestQuarter: '最高業績の四半期'
    }
  },

  // Backlog management view (views/Backlog.vue, route /backlog)
  backlog: {
    title: 'バックログ管理',
    description: '在庫不足の追跡と解消',
    loading: 'バックログを読み込み中...',
    loadFailed: 'バックログの読み込みに失敗しました: {message}',
    itemsTitle: 'バックログ項目',
    noBacklog: 'バックログ項目なし - すべての注文を履行できます！',
    // {priority} is filled from priority.* ("高" -> "優先度: 高")
    priorityStat: '優先度: {priority}',
    totalItems: 'バックログ項目の合計',
    unitsShort: '{count}単位不足',
    days: '{count}日',
    poPlaced: '発注書作成済み',
    table: {
      orderId: '注文ID',
      sku: 'SKU',
      itemName: '品目名',
      quantityNeeded: '必要数量',
      quantityAvailable: '在庫数量',
      shortage: '不足',
      daysDelayed: '遅延日数',
      priority: '優先度'
    }
  }
}
