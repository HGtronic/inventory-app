// Deterministic mock data for the shop admin. Everything is generated once at
// module load from a seeded PRNG so every run sees the same catalog.

function createRandom(seed) {
  let state = seed >>> 0;
  return function next() {
    state = (state + 0x6d2b79f5) >>> 0;
    let t = state;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const rand = createRandom(20260611);
const randInt = (min, max) => Math.floor(rand() * (max - min + 1)) + min;
const pick = (list) => list[Math.floor(rand() * list.length)];
const money = (value) => Math.round(value * 100) / 100;
const pad = (value, size) => String(value).padStart(size, "0");

const CATEGORY_NAMES = [
  "Audio",
  "Cameras",
  "Cables",
  "Chargers",
  "Displays",
  "Drones",
  "Gaming",
  "Hubs",
  "Keyboards",
  "Laptops",
  "Lighting",
  "Memory",
  "Microphones",
  "Mice",
  "Monitors",
  "Networking",
  "Printers",
  "Projectors",
  "Routers",
  "Scanners",
  "Security",
  "Smart Home",
  "Speakers",
  "Storage",
  "Tablets",
  "Tripods",
  "Webcams",
  "Wearables",
  "Batteries",
  "Adapters",
  "Cases",
  "Controllers",
  "Headsets",
  "Power Strips",
  "Stands",
  "Software",
  "Toner",
  "Furniture",
  "Cleaning",
  "Packaging",
];

const ADJECTIVES = [
  "Compact",
  "Wireless",
  "Pro",
  "Ultra",
  "Portable",
  "Slim",
  "Rugged",
  "Smart",
  "Classic",
  "Premium",
];
const NOUNS = [
  "Dock",
  "Panel",
  "Kit",
  "Module",
  "Station",
  "Bundle",
  "Unit",
  "Pack",
  "Series",
  "Set",
];
const FIRST_NAMES = [
  "Avery",
  "Jordan",
  "Morgan",
  "Riley",
  "Casey",
  "Taylor",
  "Quinn",
  "Harper",
  "Rowan",
  "Sasha",
  "Elliot",
  "Devon",
];
const LAST_NAMES = [
  "Hartley",
  "Okafor",
  "Lindqvist",
  "Moreau",
  "Tanaka",
  "Brennan",
  "Castillo",
  "Novak",
  "Ibarra",
  "Whitaker",
  "Duval",
  "Petrov",
];
const CITIES = [
  "Portland",
  "Austin",
  "Denver",
  "Chicago",
  "Boston",
  "Seattle",
  "Atlanta",
  "Phoenix",
  "Madison",
  "Raleigh",
];
const ORDER_STATUSES = ["pending", "paid", "shipped", "cancelled", "refunded"];

const categories = CATEGORY_NAMES.map((name, i) => ({ id: i + 1, name }));

const products = Array.from({ length: 3000 }, (_, i) => ({
  id: `P${pad(i + 1, 4)}`,
  sku: `SKU-${10000 + i}`,
  name: `${pick(ADJECTIVES)} ${pick(NOUNS)} ${randInt(100, 999)}`,
  categoryId: randInt(1, 40),
  price: money(4.99 + rand() * 495),
  stock: randInt(0, 600),
  rating: Math.round((3 + rand() * 2) * 10) / 10,
}));

const customers = Array.from({ length: 300 }, (_, i) => {
  const first = pick(FIRST_NAMES);
  const last = pick(LAST_NAMES);
  const roll = rand();
  return {
    id: `C${pad(i + 1, 3)}`,
    name: `${first} ${last}`,
    email: `${first}.${last}${i + 1}@example.com`.toLowerCase(),
    city: pick(CITIES),
    status: roll < 0.2 ? "inactive" : roll > 0.88 ? "vip" : "active",
    lifetimeValue: money(50 + rand() * 24950),
  };
});

const ORDER_SPAN_MS = 180 * 24 * 60 * 60 * 1000;
const ORDER_START_MS = Date.UTC(2026, 4, 1);

const orders = Array.from({ length: 600 }, (_, i) => {
  const customer = pick(customers);
  const chosen = new Set();
  const itemCount = randInt(1, 4);
  while (chosen.size < itemCount) chosen.add(pick(products));
  const items = [...chosen].map((p) => ({
    sku: p.sku,
    qty: randInt(1, 5),
    price: p.price,
  }));
  const total = money(
    items.reduce((sum, item) => sum + item.qty * item.price, 0),
  );
  const timestamp =
    ORDER_START_MS +
    Math.floor((i / 600) * ORDER_SPAN_MS) +
    randInt(0, 3600 * 1000 * 12);
  return {
    id: `O${1001 + i}`,
    customerId: customer.id,
    customerName: customer.name,
    date: new Date(timestamp).toISOString(),
    total,
    status: pick(ORDER_STATUSES),
    flagged: rand() < 0.05,
    items,
  };
});

const LATENCY_MS = 60;

// Resolves with a fresh copy so callers can never mutate the shared source data.
function respond(data) {
  return new Promise((resolve) => {
    setTimeout(() => resolve(structuredClone(data)), LATENCY_MS);
  });
}

export function fetchProducts() {
  return respond(products);
}

export function fetchCategories() {
  return respond(categories);
}

export function fetchOrders() {
  return respond(orders);
}

export function fetchCustomers() {
  return respond(customers);
}
