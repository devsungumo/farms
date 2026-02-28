# Farms — Backend Architecture

## Stack

| Layer | Tool |
|---|---|
| Framework | Django 6 |
| API | Django REST Framework |
| Auth | django-allauth + djangorestframework-simplejwt |
| Payments | Paystack |
| Admin UI | django-unfold (modern Tailwind-based admin skin) |
| File Storage | Cloudflare R2 via django-storages (S3-compatible) |
| DB (dev) | SQLite → swappable via repository layer |

---

## Core Design Rules

1. **Views are thin.** They parse the request, call one service method, return the response.
2. **Services own logic.** All business rules live in `services.py`. Services never import Django ORM directly.
3. **Repositories own DB access.** All ORM calls live in `repositories.py`. Services call repositories, not models.
4. **Models are data shapes only.** No business logic, no queries beyond `__str__` and `save` overrides for slug generation.
5. **Serializers handle I/O.** Input validation and output formatting only — no logic.

This means swapping the database requires only changes to `repositories.py`.

---

## App Map

```
apps/
├── user/        Authentication, custom User model
├── blog/        Posts, categories, tags
├── products/    Product catalog, categories, images
├── inventory/   Stock levels and movement log
├── cart/        Session cart (anonymous) + DB cart (authenticated), merged at login
├── orders/      Order lifecycle, order items, status tracking
├── delivery/    Zones, weight-based fee calculation
└── payments/    Paystack initialisation, verification, webhook handling
```

---

## Per-App File Contract

Every app follows this structure. Only create a file when it's needed.

```
app/
├── models.py         Data shape only
├── repositories.py   All ORM queries — the only place models are queried
├── services.py       Business logic — calls repositories, not models
├── serializers.py    DRF input validation and output formatting
├── views.py          HTTP layer — calls services, returns responses
├── urls.py           URL routing
└── admin.py          Django admin registration
```

---

## Data Flow

```
Request
  └── View (parse input, call service)
        └── Service (business logic, calls repository)
              └── Repository (ORM query, returns plain data or model instances)
                    └── Database
```

Response travels back up the same chain. The service never sees `HttpRequest`. The repository never sees business logic.

---

## App Details

### user
- Custom `User` model: `email` as `USERNAME_FIELD`, no `username`
- `UserManager` handles `create_user` / `create_superuser`
- Auth via allauth (email + password)
- JWT issued via `simplejwt` on login

### blog
- Models: `Category`, `Tag`, `Post`
- `Post` has `status` (draft/published), `is_featured`, `published_at`, `season`
- Admin manages all content
- API is read-only (frontend consumes, admin publishes)

### products
- Models: `Category`, `Product`, `ProductImage`
- `Product` has `price`, `unit` (lb/bunch/pint/etc.), `season`, `is_organic`, `is_featured`, `is_available`
- Stock level lives in `inventory`, not here
- Out-of-stock products remain visible — `is_available` reflects stock state but is set by inventory service

### inventory
- Models: `StockRecord`, `StockMovement`
- `StockRecord` — one per product, holds current `quantity`
- `StockMovement` — append-only log: `product`, `delta` (±), `reason`, `timestamp`
- `inventory/services.py` → `adjust_stock(product_id, delta, reason)`: writes movement, updates record, flips `product.is_available` if stock hits 0
- Only the inventory service touches stock. Orders call inventory service on payment confirmed.

### cart
- Models: `Cart`, `CartItem`
- `Cart` has either `user` (FK, nullable) or `session_key` (for anonymous)
- **Merge at login:** when a user authenticates, `cart/services.py → merge_carts(session_key, user)` moves anonymous cart items into the user's cart, discarding the session cart
- Cart item holds `product`, `quantity` only — price is always fetched live from `Product` to prevent stale pricing

### delivery
- Models: `DeliveryZone`
- `DeliveryZone` fields: `name`, `base_fee`, `per_kg_rate`
- Fee formula: `base_fee + (order_weight_kg × per_kg_rate)`
- `Product` carries a `weight_kg` field (added during build)
- `delivery/services.py → calculate_fee(zone_id, cart_items)`: sums weight from cart items, applies zone formula, returns fee as `Decimal`
- Admin manages zones and rates

### orders
- Models: `Order`, `OrderItem`
- `Order` fields: `user`, `delivery_zone`, `delivery_fee`, `subtotal`, `total`, `status`, `paystack_reference`
- Status flow (enforced in service, not model):

  ```
  pending → paid → processing → dispatched → delivered
                ↘ cancelled
          paid → refunded
  ```

- `orders/services.py → create_order(user, cart, zone_id)`:
  1. Calls `delivery/services.py` to calculate fee
  2. Snapshots cart items into `OrderItem` records (price frozen at order time)
  3. Creates `Order` with status `pending`
  4. Clears the cart
  5. Returns the order

- Status transitions are explicit service methods: `mark_paid()`, `mark_dispatched()`, etc.

### payments
- No payment logic in the model — `PaymentRecord` is a log only
- Models: `PaymentRecord` — `order`, `reference`, `amount`, `status`, `provider`, `raw_response`
- `payments/services.py → initialize(order_id)`: calls Paystack API, stores reference, returns `authorization_url`
- `payments/services.py → verify(reference)`: calls Paystack verify endpoint, updates `PaymentRecord`, calls `orders/services.py → mark_paid()`, calls `inventory/services.py → adjust_stock()` for each item
- `payments/services.py → handle_webhook(payload, signature)`: validates Paystack HMAC signature, calls `verify()` — this is the source of truth for payment confirmation
- Webhook endpoint requires no auth (Paystack calls it server-to-server), but validates signature

---

## API Versioning

All endpoints under `/api/v1/`. Version in URL, not header — simpler for frontend teams.

## Auth Endpoints
```
POST   /api/v1/auth/signup/
POST   /api/v1/auth/login/          → returns access + refresh JWT
POST   /api/v1/auth/token/refresh/
POST   /api/v1/auth/logout/
```

## Blog Endpoints (public, read-only)
```
GET    /api/v1/blog/posts/
GET    /api/v1/blog/posts/<slug>/
GET    /api/v1/blog/categories/
```

## Product Endpoints (public, read-only)
```
GET    /api/v1/products/             ?category=&season=&is_organic=&is_featured=
GET    /api/v1/products/<slug>/
GET    /api/v1/products/categories/
```

## Delivery Endpoints
```
GET    /api/v1/delivery/zones/
POST   /api/v1/delivery/calculate/   body: {zone_id, cart_id} → {delivery_fee, breakdown}
```

## Cart Endpoints (session or JWT)
```
GET    /api/v1/cart/
POST   /api/v1/cart/add/             body: {product_id, quantity}
PATCH  /api/v1/cart/items/<id>/      body: {quantity}
DELETE /api/v1/cart/items/<id>/
DELETE /api/v1/cart/clear/
```

## Order Endpoints (JWT required)
```
POST   /api/v1/orders/checkout/      body: {zone_id} → creates order, returns order_id
GET    /api/v1/orders/
GET    /api/v1/orders/<id>/
```

## Payment Endpoints
```
POST   /api/v1/payments/initialize/          body: {order_id} → {authorization_url, reference}
GET    /api/v1/payments/verify/<reference>/  → {status, order}
POST   /api/v1/payments/webhook/             Paystack server callback — no JWT, HMAC verified
```

---

## Checkout Flow (end-to-end)

```
1. User fills cart (anonymous or authenticated)
2. User logs in → carts merged
3. Frontend fetches /delivery/zones/, user picks zone
4. Frontend POSTs /delivery/calculate/ → shows delivery fee
5. Frontend POSTs /orders/checkout/ {zone_id} → order created, status=pending
6. Frontend POSTs /payments/initialize/ {order_id} → gets authorization_url
7. Frontend redirects to Paystack
8. Paystack redirects back → frontend calls /payments/verify/<ref>/
9. Paystack also hits /payments/webhook/ (source of truth)
10. On confirmed payment:
    - order.status → paid
    - inventory adjusted per order item
    - stock-out products flipped to is_available=False
```

---

## Admin Panel

### UI Framework: django-unfold

`django-unfold` replaces the default Django admin skin with a clean, modern Tailwind interface.
It is fully compatible with all standard Django admin features — no admin logic changes required.
Install it and register it above `django.contrib.admin` in `INSTALLED_APPS`.

Custom branding is set in `settings.py` under `UNFOLD = { "SITE_TITLE": "Farms Admin", ... }`.

---

### Admin Design Principles

- Every model that the business needs to manage has a registered `ModelAdmin`
- Read-only audit models (stock movements, payment records) are registered as view-only — no add/change/delete permissions
- Related objects that cannot exist without a parent (order items, product images) are managed as **inlines** — no separate list pages
- Bulk **actions** are provided for common operations so admin never needs to open records one by one
- **list_display** always shows the most useful columns up front
- **list_filter** and **search_fields** are set on every list view so admin can find records fast
- **date_hierarchy** is set on time-sensitive models (orders, payments, posts)

---

### Admin per App

#### blog
| Feature | Detail |
|---|---|
| `PostAdmin` | list: title, author, category, status, is_featured, published_at |
| | filters: status, category, season, is_featured |
| | search: title, content, author email |
| | actions: **Publish selected**, **Unpublish selected**, **Feature selected** |
| | inline: `TagInline` (M2M tag assignment on post form) |
| | date_hierarchy: published_at |
| `CategoryAdmin` | list: name, season, post count |
| `TagAdmin` | list: name, post count |

#### products
| Feature | Detail |
|---|---|
| `ProductAdmin` | list: name, category, price, unit, season, is_organic, is_available, is_featured, stock (from inventory) |
| | filters: category, season, is_organic, is_available, is_featured |
| | search: name, description |
| | actions: **Mark as available**, **Mark as unavailable**, **Feature selected**, **Unfeature selected** |
| | inline: `ProductImageInline` (add/reorder/delete gallery images on product form) |
| `CategoryAdmin` | list: name, product count |

#### inventory
| Feature | Detail |
|---|---|
| `StockRecordAdmin` | list: product, quantity, last updated |
| | actions: **Adjust stock** (opens a custom intermediate form where admin enters delta + reason) |
| | No add via admin — records are created automatically when a product is created |
| `StockMovementAdmin` | **View-only** — no add, change, delete |
| | list: product, delta, reason, timestamp |
| | filters: reason |
| | date_hierarchy: timestamp |

#### orders
| Feature | Detail |
|---|---|
| `OrderAdmin` | list: order id, user, status, total, delivery_zone, created_at |
| | filters: status, delivery_zone |
| | search: user email, paystack_reference |
| | actions: **Mark as processing**, **Mark as dispatched**, **Mark as delivered**, **Mark as cancelled** |
| | inline: `OrderItemInline` (read-only — items are frozen at order time) |
| | date_hierarchy: created_at |
| | Status field is read-only on the form — transitions happen via actions only |

#### delivery
| Feature | Detail |
|---|---|
| `DeliveryZoneAdmin` | list: name, base_fee, per_kg_rate, active |
| | actions: **Activate selected zones**, **Deactivate selected zones** |
| | Admin creates/edits zones and adjusts rates without touching code |

#### payments
| Feature | Detail |
|---|---|
| `PaymentRecordAdmin` | **View-only** — no add, change, delete |
| | list: reference, order, amount, status, provider, created_at |
| | filters: status, provider |
| | search: reference, order id |
| | date_hierarchy: created_at |
| | `raw_response` field shown collapsed (full Paystack JSON visible if needed) |

#### user
| Feature | Detail |
|---|---|
| `UserAdmin` | list: email, first_name, last_name, is_staff, is_active, date_joined |
| | search: email, first_name, last_name |
| | filters: is_staff, is_active |
| | actions: **Activate selected**, **Deactivate selected** |
| | Password shown as masked — change via the standard Django password reset |

---

### Custom Admin Actions (summary)

All actions that change state call the relevant **service method** — they do not manipulate models directly.

| Action | Calls |
|---|---|
| Publish post | `blog/services.py → publish_post(post_id)` |
| Adjust stock | `inventory/services.py → adjust_stock(product_id, delta, reason)` |
| Mark order dispatched | `orders/services.py → mark_dispatched(order_id)` |
| Mark order delivered | `orders/services.py → mark_delivered(order_id)` |
| Mark order cancelled | `orders/services.py → cancel_order(order_id)` |

This keeps admin actions consistent with API actions — the same service method runs either way.

---

### Admin Navigation (django-unfold sidebar)

Sidebar sections group related models so admin sees a clear menu:

```
Content
  └── Posts
  └── Blog Categories
  └── Tags

Store
  └── Products
  └── Product Categories
  └── Inventory
  └── Stock Movements

Orders & Payments
  └── Orders
  └── Payments

Delivery
  └── Delivery Zones

Users
  └── Users
```

---

## File Storage — Cloudflare R2

All user-uploaded files (product images, blog cover images, category images) are stored in Cloudflare R2, not on the local filesystem. R2 is S3-compatible, so `django-storages` with the S3 backend handles it via boto3.

### How it works

- `ImageField` and `FileField` in models are unchanged — they still declare `upload_to` paths
- Django's storage backend (configured in `settings.py`) transparently routes uploads to R2
- Files are served directly from R2 via a public bucket URL or a custom domain (e.g. `media.yourdomain.com`)
- In development, `django-storages` can fall back to local filesystem via an env flag

### Settings structure

```
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# R2 credentials (loaded from environment variables, never hardcoded)
AWS_ACCESS_KEY_ID        = env("R2_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY    = env("R2_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME  = env("R2_BUCKET_NAME")
AWS_S3_ENDPOINT_URL      = env("R2_ENDPOINT_URL")   # https://<account>.r2.cloudflarestorage.com
AWS_S3_CUSTOM_DOMAIN     = env("R2_PUBLIC_DOMAIN")  # e.g. media.yourdomain.com
AWS_DEFAULT_ACL          = None                      # R2 manages access at bucket level
AWS_S3_FILE_OVERWRITE    = False
```

### What this means for models

Nothing changes in model definitions. `upload_to` paths (e.g. `products/covers/%Y/%m/`) become the key prefix inside the R2 bucket. The storage layer is transparent to services and repositories.

### Credentials rule

R2 keys, bucket name, and endpoint URL are always read from environment variables. They are never committed to the codebase. A `.env.example` file documents the required variables.

---

## Dependencies to Add

```
djangorestframework
djangorestframework-simplejwt
dj-rest-auth
django-unfold          # professional admin UI
django-storages[s3]    # S3-compatible storage (Cloudflare R2)
boto3                  # AWS/S3 client used by django-storages
django-environ         # environment variable loading (.env support)
requests               # for Paystack API calls
Pillow                 # ImageField support
```

---

## Robustness Additions

### Settings Split
`farms/settings/` replaces the single `settings.py`:
```
farms/settings/
    __init__.py
    base.py          ← all shared config, secrets loaded from env
    development.py   ← DEBUG=True, local file storage, console email
    production.py    ← R2 storage, secure cookies, strict hosts
```
`manage.py`, `wsgi.py`, `asgi.py` default to `farms.settings.development`.
Production sets `DJANGO_SETTINGS_MODULE=farms.settings.production` in the environment.

### Core App — `apps/core`
Shared infrastructure used by all other apps. Not a business domain — just plumbing.
```
apps/core/
    exceptions.py   ← custom DRF exception handler
    responses.py    ← ApiResponse helper (consistent JSON shape)
    pagination.py   ← custom PageNumberPagination
    views.py        ← health check view
    urls.py         ← /api/health/
```

### Consistent API Response Shape
Every endpoint returns the same envelope:
```json
{"success": true,  "data": {...}}
{"success": false, "error": "validation_error", "message": "...", "details": {...}}
```
Set via `EXCEPTION_HANDLER` in `REST_FRAMEWORK` settings. Frontend never needs to guess the shape.

### CORS — `django-cors-headers`
`CorsMiddleware` added above `CommonMiddleware`. `CORS_ALLOWED_ORIGINS` loaded from env.

### Filtering — `django-filter`
`DjangoFilterBackend` set globally in `REST_FRAMEWORK`. Every list view declares `filterset_fields` — no filter logic in views or services.

### Pagination
Custom `PageNumberPagination` in `apps/core/pagination.py`. `PAGE_SIZE=20`. All list endpoints paginated by default.

### API Docs — `drf-spectacular`
OpenAPI schema auto-generated from serializers and views. Available at:
- `GET /api/schema/` — raw schema (YAML)
- `GET /api/schema/swagger-ui/` — interactive Swagger UI

### DRF Throttling
Set globally — anonymous: 100/day, authenticated: 1000/day. Auth endpoints get tighter per-view throttle overrides.

### JWT — `djangorestframework-simplejwt`
- Access token lifetime: 60 minutes
- Refresh token lifetime: 7 days
- `ROTATE_REFRESH_TOKENS = True` — new refresh token issued on each refresh
- `BLACKLIST_AFTER_ROTATION = True` — old refresh tokens invalidated
- `rest_framework_simplejwt.token_blacklist` in INSTALLED_APPS

### Webhook Idempotency
Before processing any Paystack webhook: check if `PaymentRecord` for that `reference` already has `status=success`. If yes, return 200 immediately. No double-processing.

### UUID for Orders & Payments
`Order` and `PaymentRecord` have a `public_id = UUIDField(default=uuid.uuid4, editable=False, unique=True)`. This is what the frontend and Paystack use. Integer PKs never leave the backend.

### Soft Delete Policy
- Products → never deleted, only `is_available=False`
- Orders → never deleted, only `status=cancelled`
- Posts → never deleted, only `status=draft`
- No soft-delete framework needed — just enforced by services

### Structured Logging
Python logging configured in `base.py`. Named loggers per app:
- `apps.payments` — every webhook received, verified, failed
- `apps.inventory` — every stock adjustment
- `apps.orders` — every status transition

### Health Check
`GET /api/health/ → {"status": "ok"}` — no auth required. Used by deployment platform to verify app is running.

### `DEFAULT_AUTO_FIELD`
Set to `BigAutoField` in base.py to avoid migration warnings.

---

## Dependencies to Add

```
djangorestframework
djangorestframework-simplejwt
dj-rest-auth
django-unfold          # professional admin UI
django-cors-headers    # CORS for separate frontend
django-filter          # query param filtering on list endpoints
drf-spectacular        # OpenAPI schema + Swagger UI
django-storages[s3]    # S3-compatible storage (Cloudflare R2)
boto3                  # AWS/S3 client used by django-storages
django-environ         # environment variable loading (.env support)
requests               # for Paystack API calls
Pillow                 # ImageField support
factory-boy            # test data factories (dev/test only)
```

---

## Build Order

1. Settings split + `.env.example` + `requirements.txt`
2. `apps/core` — response envelope, exception handler, pagination, health check
3. `django-unfold` branding + DRF + JWT + CORS wired into settings
4. Blog — models, admin, API
5. Products + Inventory — models, admin, API
6. Delivery zones — models, admin, calculate endpoint
7. Cart — models, admin view, API (anon + auth + merge)
8. Orders + checkout — models, admin with actions, API
9. Payments (Paystack) — models, admin view-only, API + webhook
