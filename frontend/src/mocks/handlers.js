// src/mocks/handlers.js
import { http, HttpResponse, delay } from "msw";

// Sample user and drink data to keep the UI interactive without a backend
const sampleUser = {
  user_id: 1,
  username: "demo_user",
  email: "demo@drinkwise.test",
  joindate: new Date("2024-01-05").toISOString(),
  access_token: "demo-token",
  token_type: "bearer",
  profile_picture: "",
  description: "I enjoy balanced, medium-sweet drinks.",
  is_verified: true,
  verification_completed: true,
  age: 28,
  preference_finished: true,
};

const sampleDrinks = [
  {
    drink_id: 101,
    name: "Caramel Cold Brew",
    description: "Slow-steeped cold brew with caramel syrup and a dash of cream.",
    category: "coffee",
    price_tier: "$$",
    sweetness_level: 6,
    caffeine_content: 180,
    sugar_content: 18,
    calorie_content: 160,
    image_url: "",
    is_alcoholic: false,
    alcohol_content: 0,
    safety_flags: [],
    created_at: new Date("2024-04-01").toISOString(),
    updated_at: new Date("2024-10-01").toISOString(),
    ingredients: [
      { ingredient_name: "Cold brew concentrate", quantity: "6 oz", is_allergen: false },
      { ingredient_name: "Caramel syrup", quantity: "1.5 tbsp", is_allergen: false },
      { ingredient_name: "Cream", quantity: "1 oz", is_allergen: true },
    ],
    tags: ["cold", "sweet", "coffee"],
  },
  {
    drink_id: 102,
    name: "Matcha Oat Latte",
    description: "Earthy ceremonial matcha with creamy oat milk and light vanilla.",
    category: "tea",
    price_tier: "$$",
    sweetness_level: 4,
    caffeine_content: 75,
    sugar_content: 8,
    calorie_content: 120,
    image_url: "",
    is_alcoholic: false,
    alcohol_content: 0,
    safety_flags: [],
    created_at: new Date("2024-03-15").toISOString(),
    updated_at: new Date("2024-09-20").toISOString(),
    ingredients: [
      { ingredient_name: "Matcha", quantity: "2 tsp", is_allergen: false },
      { ingredient_name: "Oat milk", quantity: "8 oz", is_allergen: false },
      { ingredient_name: "Vanilla syrup", quantity: "1 tsp", is_allergen: false },
    ],
    tags: ["warm", "tea", "oat"],
  },
  {
    drink_id: 103,
    name: "Berry Ginger Fizz",
    description: "Sparkling berry mocktail with ginger, lime, and mint.",
    category: "mocktail",
    price_tier: "$",
    sweetness_level: 5,
    caffeine_content: 0,
    sugar_content: 12,
    calorie_content: 90,
    image_url: "",
    is_alcoholic: false,
    alcohol_content: 0,
    safety_flags: [],
    created_at: new Date("2024-02-10").toISOString(),
    updated_at: new Date("2024-10-10").toISOString(),
    ingredients: [
      { ingredient_name: "Mixed berries", quantity: "3 oz", is_allergen: false },
      { ingredient_name: "Ginger syrup", quantity: "1 tbsp", is_allergen: false },
      { ingredient_name: "Sparkling water", quantity: "4 oz", is_allergen: false },
    ],
    tags: ["sparkling", "fruit", "mocktail"],
  },
];

let userInteractions = {
  101: {
    user_id: sampleUser.user_id,
    drink_id: 101,
    times_consumed: 2,
    is_favorite: true,
    rating: 4.5,
    is_not_for_me: false,
    viewed_at: new Date().toISOString(),
    last_consumed: new Date().toISOString(),
  },
};

export const handlers = [
  // Auth
  http.post("*/auth/login", async ({ request }) => {
    const body = await request.json();
    await delay(150);
    return HttpResponse.json({
      ...sampleUser,
      username: body.username || sampleUser.username,
    });
  }),
  http.post("*/auth/register", async ({ request }) => {
    const body = await request.json();
    await delay(200);
    return HttpResponse.json({
      ...sampleUser,
      username: body.username || sampleUser.username,
      email: body.email || sampleUser.email,
    });
  }),
  http.get("*/auth/me", async () => {
    await delay(100);
    return HttpResponse.json(sampleUser);
  }),
  http.post("*/auth/logout", () => {
    return HttpResponse.json({ message: "Logged out" });
  }),

  // Catalog
  http.get("*/catalog/drinks", ({ request }) => {
    const url = new URL(request.url);
    const page = Number(url.searchParams.get("page") || 1);
    const limit = Number(url.searchParams.get("limit") || 12);
    const search = (url.searchParams.get("search_text") || "").toLowerCase();

    const filtered = sampleDrinks.filter((d) =>
      d.name.toLowerCase().includes(search)
    );
    const start = (page - 1) * limit;
    const paged = filtered.slice(start, start + limit);
    return HttpResponse.json({
      drinks: paged,
      total: filtered.length,
      page,
      limit,
      total_pages: Math.max(1, Math.ceil(filtered.length / limit)),
    });
  }),
  http.get("*/catalog/drinks/:id", ({ params }) => {
    const drink = sampleDrinks.find((d) => d.drink_id === Number(params.id));
    if (!drink) {
      return HttpResponse.json({ error: "Drink not found" }, { status: 404 });
    }
    return HttpResponse.json(drink);
  }),

  // Recommendations and similar
  http.get("*/recommendations/drinks", ({ request }) => {
    const url = new URL(request.url);
    const limit = Number(url.searchParams.get("limit") || 6);
    const similar = sampleDrinks.slice(0, limit);
    return HttpResponse.json({
      similar_drinks: similar,
      count: similar.length,
    });
  }),
  http.get("*/recommendations/similar/:id", ({ params }) => {
    const similar = sampleDrinks.filter((d) => d.drink_id !== Number(params.id));
    return HttpResponse.json({
      drink_id: Number(params.id),
      similar_drinks: similar,
      count: similar.length,
    });
  }),
  http.get("*/recommendations/users", () => {
    return HttpResponse.json({
      recommendations: sampleDrinks.map((d, idx) => ({
        drink: d,
        score: 0.9 - idx * 0.1,
        recommendation_type: "hybrid",
      })),
    });
  }),

  // User drink interactions
  http.get("*/user-drinks/:id", ({ params }) => {
    const id = Number(params.id);
    const interaction = userInteractions[id];
    if (!interaction) {
      return HttpResponse.json(null, { status: 204 });
    }
    return HttpResponse.json(interaction);
  }),
  http.put("*/user-drinks/:id", async ({ params, request }) => {
    const id = Number(params.id);
    const patch = await request.json();
    const existing = userInteractions[id] || {
      user_id: sampleUser.user_id,
      drink_id: id,
      times_consumed: 0,
      is_favorite: false,
      rating: 0,
      is_not_for_me: false,
      viewed_at: new Date().toISOString(),
      last_consumed: null,
    };
    const updated = { ...existing, ...patch, last_consumed: new Date().toISOString() };
    userInteractions[id] = updated;
    return HttpResponse.json(updated);
  }),

  // Preferences and favorites
  http.get("*/preferences", () => {
    return HttpResponse.json({
      user_id: sampleUser.user_id,
      sweetness_preference: 6,
      bitterness_preference: 4,
      caffeine_limit: 200,
      calorie_limit: 400,
      preferred_price_tier: "$$",
      preferred_categories: ["coffee", "tea"],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    });
  }),
  http.get("*/user-favorites", () => {
    return HttpResponse.json({
      favorites: sampleDrinks.slice(0, 2),
      total_count: 2,
    });
  }),

  // Taste quiz
  http.get("*/quiz/provide", () => {
    const questions = [
      {
        question_id: 1,
        question_text: "How sweet do you like your drinks?",
        options: [
          { option_id: 11, option_text: "Not sweet at all" },
          { option_id: 12, option_text: "Lightly sweet" },
          { option_id: 13, option_text: "Balanced" },
          { option_id: 14, option_text: "Very sweet" },
        ],
      },
      {
        question_id: 2,
        question_text: "Pick a flavor note you enjoy most:",
        options: [
          { option_id: 21, option_text: "Nutty" },
          { option_id: 22, option_text: "Fruity" },
          { option_id: 23, option_text: "Spiced" },
          { option_id: 24, option_text: "Herbal" },
        ],
      },
    ];
    return HttpResponse.json({
      questions,
      total_questions: questions.length,
    });
  }),
  http.post("*/quiz/submit", async ({ request }) => {
    await request.json();
    return HttpResponse.json({ message: "Quiz submitted", preferences_updated: true });
  }),
];
