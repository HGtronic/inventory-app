export default {
  // Navigation
  nav: {
    overview: 'Overview',
    inventory: 'Inventory',
    orders: 'Orders',
    finance: 'Finance',
    demandForecast: 'Demand Forecast',
    restocking: 'Restocking',
    reports: 'Reports',
    companyName: 'Catalyst Components',
    subtitle: 'Inventory Management System'
  },

  // Dashboard
  dashboard: {
    title: 'Overview',
    kpi: {
      title: 'Key Performance Indicators',
      inventoryTurnover: 'Inventory Turnover Rate',
      ordersFulfilled: 'Orders Fulfilled',
      orderFillRate: 'Order Fill Rate',
      revenue: 'Revenue (Orders)',
      revenueYTD: 'Revenue (Orders) YTD',
      revenueMTD: 'Revenue (Orders) MTD',
      avgDeliveryTime: 'Avg Delivery Time (Days)',
      promisedLeadTime: 'Promised lead time',
      goal: 'Goal'
    },
    summary: {
      title: 'Summary'
    },
    orderHealth: {
      title: 'Order Health',
      totalOrders: 'Total Orders',
      revenue: 'Revenue',
      avgOrderValue: 'Avg Order Value',
      onTimeRate: 'On-Time Rate',
      avgFulfillmentDays: 'Avg Fulfillment (Days)',
      total: 'Total'
    },
    ordersByMonth: {
      title: 'Orders by Month'
    },
    inventoryValue: {
      title: 'Inventory Value by Category'
    },
    inventoryShortages: {
      title: 'Inventory Shortages',
      viewAll: 'View all',
      noShortages: 'No inventory shortages - all orders can be fulfilled!',
      noData: 'No inventory data for selected filters',
      orderId: 'Order ID',
      sku: 'SKU',
      itemName: 'Item Name',
      quantityNeeded: 'Quantity Needed',
      quantityAvailable: 'Quantity Available',
      shortage: 'Shortage',
      daysDelayed: 'Days Delayed',
      priority: 'Priority',
      unitsShort: 'units short',
      days: '{count} day | {count} days'
    },
    topProducts: {
      title: 'Top Products by Revenue',
      sku: 'SKU',
      product: 'Product',
      category: 'Category',
      warehouse: 'Warehouse',
      stockStatus: 'Stock Status',
      revenue: 'Revenue',
      unitsOrdered: 'Units Ordered',
      firstOrder: 'First Order',
      inStock: 'In Stock',
      lowStock: 'Low Stock'
    }
  },

  // Inventory
  inventory: {
    title: 'Inventory',
    description: 'Track and manage all inventory items',
    stockLevels: 'Stock Levels',
    skus: 'SKUs',
    searchPlaceholder: 'Search by item name...',
    clearSearch: 'Clear search',
    totalItems: 'Total Items',
    totalValue: 'Total Value',
    lowStockItems: 'Low Stock Items',
    warehouses: 'Warehouses',
    table: {
      sku: 'SKU',
      itemName: 'Item Name',
      name: 'Name',
      category: 'Category',
      warehouse: 'Warehouse',
      quantity: 'Quantity',
      quantityOnHand: 'Quantity on Hand',
      reorderPoint: 'Reorder Point',
      unitCost: 'Unit Cost',
      unitPrice: 'Unit Price',
      totalValue: 'Total Value',
      location: 'Location',
      status: 'Status'
    }
  },

  // Orders
  orders: {
    title: 'Orders',
    description: 'View and manage customer orders',
    allOrders: 'All Orders',
    totalOrders: 'Total Orders',
    totalRevenue: 'Total Revenue',
    avgOrderValue: 'Avg Order Value',
    onTimeDelivery: 'On-Time Delivery',
    itemsCount: '{count} item | {count} items',
    quantity: 'Qty',
    submittedOrders: 'Submitted Orders',
    noSubmittedOrders: 'No submitted restock orders yet.',
    leadTimeDays: '{days} days',
    table: {
      leadTime: 'Lead Time',
      totalCost: 'Total Cost',
      orderNumber: 'Order Number',
      orderId: 'Order ID',
      orderDate: 'Order Date',
      date: 'Date',
      customer: 'Customer',
      category: 'Category',
      warehouse: 'Warehouse',
      items: 'Items',
      value: 'Value',
      totalValue: 'Total Value',
      status: 'Status',
      expectedDelivery: 'Expected Delivery',
      actualDelivery: 'Actual Delivery'
    }
  },

  // Finance/Spending
  finance: {
    title: 'Finance Dashboard',
    description: 'Track revenue, costs, and financial performance',
    totalRevenue: 'Total Revenue',
    totalCosts: 'Total Costs',
    netProfit: 'Net Profit',
    avgOrderValue: 'Avg Order Value',
    fromOrders: 'From {count} orders',
    costBreakdown: 'Procurement + Operational + Labor + Overhead',
    margin: 'margin',
    perOrderRevenue: 'Per order revenue',
    revenueVsCosts: {
      title: 'Monthly Revenue vs Costs',
      revenue: 'Revenue',
      costs: 'Total Costs'
    },
    monthlyCostFlow: {
      title: 'Monthly Cost Flow',
      procurement: 'Procurement',
      operational: 'Operational',
      labor: 'Labor',
      overhead: 'Overhead'
    },
    categorySpending: {
      title: 'Spending by Category',
      ofTotal: 'of total'
    },
    transactions: {
      title: 'Recent Transactions',
      id: 'ID',
      description: 'Description',
      vendor: 'Vendor',
      date: 'Date',
      amount: 'Amount'
    }
  },

  // Demand Forecast
  demand: {
    title: 'Demand Forecast',
    description: 'Analyze demand trends and forecasts',
    increasingDemand: 'Increasing Demand',
    stableDemand: 'Stable Demand',
    decreasingDemand: 'Decreasing Demand',
    itemsCount: '{count} item | {count} items',
    more: 'more...',
    demandForecasts: 'Demand Forecasts',
    table: {
      sku: 'SKU',
      itemName: 'Item Name',
      currentDemand: 'Current Demand',
      forecastedDemand: 'Forecasted Demand',
      change: 'Change',
      trend: 'Trend',
      period: 'Period'
    }
  },

  // Restocking
  restocking: {
    title: 'Restocking',
    description: 'Set a budget and order what the demand forecast needs most',
    budget: 'Available Budget',
    fullRestockCost: 'Full restock cost: {amount}',
    allocated: 'Allocated',
    remaining: 'Remaining',
    itemsRecommended: 'Items Recommended',
    recommendations: 'Recommended Items',
    notCovered: '{count} item not covered by this budget | {count} items not covered by this budget',
    partial: 'Partial',
    placeOrder: 'Place Order',
    placing: 'Placing order...',
    orderPlaced: 'Order {orderNumber} submitted. Expected delivery in {days} days.',
    viewInOrders: 'View in Orders',
    allStocked: 'All forecast items are fully stocked or already on order.',
    budgetTooLow: 'Increase the budget to see recommendations.',
    loadFailed: 'Failed to load restocking recommendations.',
    orderFailed: 'Could not place the order. Please try again.',
    table: {
      sku: 'SKU',
      item: 'Item',
      trend: 'Trend',
      forecast: 'Forecast',
      onHand: 'On Hand',
      onOrder: 'On Order',
      shortfall: 'Shortfall',
      orderQty: 'Order Qty',
      unitCost: 'Unit Cost',
      lineTotal: 'Line Total',
      leadTime: 'Lead Time'
    }
  },

  // Filters
  filters: {
    timePeriod: 'Time Period',
    location: 'Location',
    category: 'Category',
    orderStatus: 'Order Status',
    all: 'All',
    allMonths: 'All Months'
  },

  // Statuses
  status: {
    delivered: 'Delivered',
    shipped: 'Shipped',
    processing: 'Processing',
    backordered: 'Backordered',
    submitted: 'Submitted',
    inStock: 'In Stock',
    lowStock: 'Low Stock',
    adequate: 'Adequate'
  },

  // Trends
  trends: {
    increasing: 'increasing',
    stable: 'stable',
    decreasing: 'decreasing'
  },

  // Priority
  priority: {
    high: 'High',
    medium: 'Medium',
    low: 'Low'
  },

  // Categories
  categories: {
    circuitBoards: 'Circuit Boards',
    sensors: 'Sensors',
    actuators: 'Actuators',
    controllers: 'Controllers',
    powerSupplies: 'Power Supplies'
  },

  // Spending Categories
  spendingCategories: {
    rawMaterials: 'Raw Materials',
    components: 'Components',
    equipment: 'Equipment',
    consumables: 'Consumables'
  },

  // Warehouses
  warehouses: {
    sanFrancisco: 'San Francisco',
    london: 'London',
    tokyo: 'Tokyo'
  },

  // Months
  months: {
    jan: 'Jan',
    feb: 'Feb',
    mar: 'Mar',
    apr: 'Apr',
    may: 'May',
    jun: 'Jun',
    jul: 'Jul',
    aug: 'Aug',
    sep: 'Sep',
    oct: 'Oct',
    nov: 'Nov',
    dec: 'Dec',
    january: 'January',
    february: 'February',
    march: 'March',
    april: 'April',
    june: 'June',
    july: 'July',
    august: 'August',
    september: 'September',
    october: 'October',
    november: 'November',
    december: 'December'
  },

  // Profile Menu
  profile: {
    profileDetails: 'Profile Details',
    myTasks: 'My Tasks',
    logout: 'Logout'
  },

  // Profile Details Modal
  profileDetails: {
    title: 'Profile Details',
    email: 'Email',
    department: 'Department',
    location: 'Location',
    phone: 'Phone',
    joinDate: 'Join Date',
    employeeId: 'Employee ID',
    close: 'Close'
  },

  // Tasks Modal
  tasks: {
    title: 'My Tasks',
    taskTitle: 'Task Title',
    taskTitlePlaceholder: 'Enter task title...',
    priority: 'Priority',
    dueDate: 'Due Date',
    addTask: 'Add Task',
    noTasks: 'No tasks yet. Add your first task above!'
  },

  // Language
  language: {
    english: 'English',
    japanese: 'Japanese',
    selectLanguage: 'Select Language'
  },

  // Common
  common: {
    loading: 'Loading...',
    error: 'Error',
    noData: 'No data available',
    viewDetails: 'View Details',
    close: 'Close',
    save: 'Save',
    cancel: 'Cancel',
    search: 'Search',
    filter: 'Filter',
    export: 'Export',
    items: 'items'
  },

  // Purchase orders for backlog items (Dashboard shortages table + PurchaseOrderModal)
  purchaseOrders: {
    createPO: 'Create PO',
    viewPO: 'View PO',
    createTitle: 'Create Purchase Order',
    viewTitle: 'Purchase Order Details',
    close: 'Close',
    cancel: 'Cancel',
    submit: 'Create Purchase Order',
    submitting: 'Creating...',
    loading: 'Loading purchase order...',
    sku: 'SKU',
    orderId: 'Order ID',
    quantityNeeded: 'Quantity Needed',
    quantityAvailable: 'Quantity Available',
    shortfall: 'Shortfall',
    supplierName: 'Supplier Name',
    supplierPlaceholder: 'Enter supplier name',
    quantity: 'Quantity',
    unitCostIn: 'Unit Cost ({currency})',
    alreadyExists: 'A purchase order already existed for this item. Showing the existing order.',
    expectedDelivery: 'Expected Delivery',
    orderTotal: 'Order Total',
    notesOptional: 'Notes (optional)',
    notesPlaceholder: 'Add any notes for this order',
    poId: 'PO ID',
    status: 'Status',
    supplier: 'Supplier',
    unitCost: 'Unit Cost',
    total: 'Total',
    createdDate: 'Created',
    notes: 'Notes',
    noNotes: 'No notes',
    statuses: {
      pending: 'Pending'
    },
    errors: {
      supplierRequired: 'Supplier name is required',
      supplierTooLong: 'Supplier name must be 200 characters or fewer',
      quantityInvalid: 'Enter a whole number greater than 0',
      unitCostInvalid: 'Enter an amount greater than 0',
      deliveryRequired: 'Select an expected delivery date',
      notesTooLong: 'Notes must be 1000 characters or fewer',
      createFailed: 'Failed to create the purchase order. Please try again.',
      loadFailed: 'Failed to load the purchase order.',
      notFound: 'No purchase order found for this item.'
    }
  },

  // Performance reports view (views/Reports.vue)
  reports: {
    title: 'Performance Reports',
    description: 'View quarterly performance metrics and monthly trends',
    loading: 'Loading reports...',
    loadFailed: 'Failed to load reports: {message}',
    // Quarter values arrive from the API as "Q1-2025"; these templates rebuild that label per locale
    quarterLabel: 'Q{quarter}-{year}',
    // {month} is the localized short month name from months.*, {year} the four-digit year
    monthLabel: '{month} {year}',
    quarterly: {
      title: 'Quarterly Performance',
      quarter: 'Quarter',
      totalOrders: 'Total Orders',
      totalRevenue: 'Total Revenue',
      avgOrderValue: 'Avg Order Value',
      fulfillmentRate: 'Fulfillment Rate'
    },
    monthlyTrend: {
      title: 'Monthly Revenue Trend'
    },
    monthOverMonth: {
      title: 'Month-over-Month Analysis',
      month: 'Month',
      orders: 'Orders',
      revenue: 'Revenue',
      change: 'Change',
      growthRate: 'Growth Rate'
    },
    stats: {
      totalRevenueYtd: 'Total Revenue (YTD)',
      avgMonthlyRevenue: 'Avg Monthly Revenue',
      totalOrdersYtd: 'Total Orders (YTD)',
      bestQuarter: 'Best Performing Quarter'
    }
  },

  // Backlog management view (views/Backlog.vue, route /backlog)
  backlog: {
    title: 'Backlog Management',
    description: 'Track and resolve inventory shortages',
    loading: 'Loading backlog...',
    loadFailed: 'Failed to load backlog: {message}',
    itemsTitle: 'Backlog Items',
    noBacklog: 'No backlog items - all orders can be fulfilled!',
    // {priority} is filled from priority.* ("High" -> "High Priority")
    priorityStat: '{priority} Priority',
    totalItems: 'Total Backlog Items',
    unitsShort: '{count} units short',
    days: '{count} day | {count} days',
    poPlaced: 'PO placed',
    table: {
      orderId: 'Order ID',
      sku: 'SKU',
      itemName: 'Item Name',
      quantityNeeded: 'Quantity Needed',
      quantityAvailable: 'Quantity Available',
      shortage: 'Shortage',
      daysDelayed: 'Days Delayed',
      priority: 'Priority'
    }
  }
}
