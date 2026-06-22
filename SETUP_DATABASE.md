# Database Setup (pick ONE)

## Why Supabase failed

The Cursor Supabase plugin error **"No organizations found"** means your Supabase account has no organization yet. Fix it:

1. Go to https://supabase.com/dashboard
2. Click **New organization** → give it a name → create
3. Click **New project** → name it `codevector-products` → set a DB password → create
4. Wait ~2 minutes for the project to provision
5. Go to **Project Settings → Database → Connection string → URI**
6. Copy the string (replace `[YOUR-PASSWORD]` with your password)
7. Paste into `.env` as `DATABASE_URL=...`

Then run:

```powershell
.\setup.ps1
```

---

## Option B: Neon (recommended — faster, no org issue)

1. Go to https://neon.tech and sign up (free, no card)
2. Click **New Project** → name `codevector-products`
3. Copy the **connection string** from the dashboard
4. Paste into `.env`:

```
DATABASE_URL=postgresql://user:pass@host/neondb?sslmode=require
```

5. Run:

```powershell
.\setup.ps1
```

---

## Option C: Neon CLI (terminal)

```powershell
neonctl auth          # opens browser — log in
neonctl projects create --name codevector-products
neonctl connection-string
```

Copy the output into `.env`, then:

```powershell
.\setup.ps1
```
