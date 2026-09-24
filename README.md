# Proje: Kararsızım — Kapsamlı Proje Dokümantasyonu & Mimari Planı

---

## 1. Proje Genel Bakışı & Amacı
**Kararsızım**, günlük hayatta iki ya da daha fazla seçenek arasında kararsız kalan insanların ("Bugün sinemaya mı gitsem, restorana mı?", "Hangi telefonu alsam?", "Hangi filmi izlesem?") hızlıca anket açıp topluluğun fikrini alabildiği, genç, dinamik ve renkli bir sosyal oylama platformudur.

- **Ana Felsefe:** Hızlı, eğlenceli, sade ve zahmetsiz etkileşim.
- **Odak:** Karmaşık sosyal medya özellikleri (takip etme, mesajlaşma vb.) yerine doğrudan soru-cevap ve oylama odaklı bir prototip (MVP).

---

## 2. Kullanıcı Rolleri & Yetkilendirme

| Özellik | Ziyaretçi (Giriş Yapmamış) | Kayıtlı Kullanıcı |
| :--- | :---: | :---: |
| **Anketleri Görüntüleme** | Evet | Evet |
| **Anketleri Oylama** | Evet (Anonim/Session tabanlı) | Evet |
| **Sonuçları Canlı Görme** | Evet | Evet |
| **Yeni Anket Oluşturma** | Hayır (Kayıt olmaya yönlendirilir) | Evet |
| **Kendi Anketlerini Yönetme** | Hayır | Evet |

### Kayıt ve Gizlilik Kuralları:
- **Kayıt Alanları:** `Kullanıcı Adı (username)`, `E-posta (email)`, `Parola (password)`.
- **Gizlilik:** Kullanıcının e-posta adresi hiçbir arayüzde veya ankette **asla gösterilmez**.
- **Görünürlük:** Anket kartlarında ve detaylarında sadece kullanıcının seçtiği `@kullanici_adi` görünür.
- **Takip Mekanizması Yok:** Takipçi, takip edilen, arkadaş ekleme gibi karmaşık sistemler MVP kapsamında yer almaz.

---

## 3. Temel Fonksiyonel Özellikler

### 3.1. Anket Oluşturma (Sadece Giriş Yapmış Kullanıcılar)
- **Başlık/Soru:** Kullanıcının kararsız kaldığı soru (Maksimum 250 karakter).
- **Açıklama (Opsiyonel):** Kararsızlık hakkında ek detay veya bağlam.
- **Seçenekler:** **En az 2, en fazla 5** seçenek eklenebilir.
- **Kategori/Etiket (Opsiyonel):** *Yemek, Eğlence, Teknoloji, Moda, Günlük Yaşam vb.*
- **Dinamik Seçenek Alanı:** JavaScript ile "Seçenek Ekle (+)" butonu (5 seçeneğe ulaşınca buton pasifleşir, en az 2 seçenek kalana kadar silme butonu aktiftir).

### 3.2. Oylama Sistemi & Mükerrer Oy Engelleme
- Ziyaretçiler ve kayıtlı kullanıcılar tek tıkla oy verebilir.
- **Mükerrer Oy Engelleme Mekanizması:**
  - *Kayıtlı Kullanıcılar için:* `User` + `Poll` tabanlı veritabanı kontrolü.
  - *Misafir Kullanıcılar için:* `Session Key` veya `Cookie / IP Hash` kontrolü ile aynı tarayıcıdan tek oy sınırı.
- **Anlık Geri Bildirim:** Oy verildiğinde sayfa yenilenmeden (Fetch / AJAX) oy yüzdeleri ve toplam oy sayıları animasyonlu bir şekilde güncellenir.
- **Kesin Oylama:** Oylar tek seferliktir, sonradan değiştirilemez.

### 3.3. Ana Sayfa & Akış (Feed)
- **Filtreler:**
  - **Popülerler:** En çok oy alan kararsızlıklar.
  - **En Yeniler:** Son eklenen anketler.
- **Arama Kutusu:** Başlığa göre arama yapabilme.

---

## 4. Teknoloji Yığını (Tech Stack)

```mermaid
flowchart TD
    subgraph Frontend["Frontend (Vanilla & Modern UI)"]
        HTML["HTML5 (Django Templates)"]
        CSS["CSS3 (Modern & Renkli Stil)"]
        JS["Vanilla JavaScript (Fetch API & Animasyonlar)"]
    end

    subgraph Backend["Backend"]
        Django["Python & Django 5.x/6.x"]
        Auth["Django Standart Auth (Username/Password)"]
    end

    subgraph Database["Database (Supabase)"]
        Postgres["Supabase PostgreSQL"]
    end

    subgraph Hosting["Deployment"]
        Vercel["Vercel Serverless (WSGI Handler)"]
    end

    Frontend --> Backend
    Backend --> Postgres
    Backend -. Deployed on .-> Vercel
```

- **Backend:** Python 3.11+, Django 5.x / 6.x
- **Veritabanı:** Supabase (Barındırılan PostgreSQL)
- **Frontend:** Django Template Engine, Vanilla HTML5, Modern CSS3 (Flexbox/Grid), Vanilla JavaScript
- **Deployment Platformu:** Vercel (Serverless Functions / `vercel.json` WSGI desteği)
- **Kütüphaneler & Paketler:**
  - `django`
  - `psycopg2-binary`
  - `dj-database-url`
  - `python-dotenv`
  - `whitenoise`

---

## 5. Veritabanı Mimarisi (Supabase / PostgreSQL)

```mermaid
erDiagram
    AUTH_USER ||--o{ POLL : creates
    POLL ||--|{ OPTION : contains
    POLL ||--o{ VOTE : receives
    OPTION ||--o{ VOTE : chosen_in
    AUTH_USER ||--o{ VOTE : casts

    AUTH_USER {
        int id PK
        string username "Benzersiz ve arayüzde görünen isim"
        string email "Gizli tutulan e-posta"
        string password "Hashlenmiş parola"
        datetime date_joined
    }

    POLL {
        int id PK
        int user_id FK "Anketi oluşturan kullanıcı"
        string question "Soru başlığı"
        text description "Ekstra açıklama (opsiyonel)"
        datetime created_at
        boolean is_active "Anket aktif mi?"
    }

    OPTION {
        int id PK
        int poll_id FK "Bağlı olduğu anket"
        string text "Seçenek metni"
        int order "Görünüm sırası (1-5)"
    }

    VOTE {
        int id PK
        int poll_id FK
        int option_id FK
        int user_id FK "Giriş yapmışsa kullanıcı ID (opsiyonel)"
        string session_key "Misafir kullanıcı için session/hash"
        datetime created_at
    }
```

---

## 6. Arayüz (UI/UX) & Tasarım Konsepti

Genç nesle hitap eden, enerjik, modern ve dikkat çekici bir görsel stil:

### Renk Paleti (Canlı & Enerjik)
- **Arka Plan:** Çok açık soft krem / lavanta tonu (`#F8F9FE` veya `#F5F3FF`)
- **Ana Vurgu Rengi (Primary):** Canlı Elektrik Moru (`#7C3AED`) / İndigo (`#6366F1`)
- **İkincil Canlı Renkler (Accent):**
  - Neon Mercan / Pembe: `#FF5E7E`
  - Canlı Turkuaz / Nane: `#06D6A0`
  - Güneş Sarısı: `#FFD166`
  - Gök Mavisi: `#3B82F6`
- **Kart Yapısı (Card Design):** Yumuşak gölgeli veya modern neo-brutalist hafif kalın kenarlıklı (`border: 2px solid #1E1B4B; box-shadow: 4px 4px 0px #1E1B4B;`) kartlar.
- **Butonlar & İpuçları:** Tıklama hissi yüksek, mikro ölçeklenme (`transform: scale(1.02);`) efektli butonlar.
- **Sonuç Grafikleri:** Seçeneklerin içinde renkli dolgu barları (% oranında dolan yumuşak gradientli çizgiler).

---

## 7. Proje Dizin Yapısı

```text
kararsizim/
│
├── core/                       # Django proje ayarları
│   ├── __init__.py
│   ├── settings.py             # Supabase & Vercel yapılandırmaları
│   ├── urls.py
│   └── wsgi.py                 # Vercel entrypoint
│
├── polls/                      # Anket Uygulaması
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py               # Poll, Option, Vote modelleri
│   ├── views.py                # Liste, Oluşturma, Oy Verme (AJAX)
│   ├── forms.py                # Anket & Seçenek Doğrulama Formları
│   └── urls.py
│
├── accounts/                   # Kullanıcı Yönetimi
│   ├── __init__.py
│   ├── views.py                # Kayıt, Giriş, Çıkış
│   ├── forms.py                # Kayıt & Giriş Formları
│   └── urls.py
│
├── static/                     # CSS, JS ve Görsel Dosyaları
│   ├── css/
│   │   └── style.css           # Genç ve renkli modern stiller
│   └── js/
│       ├── poll_create.js      # Dinamik 2-5 seçenek ekleme/çıkarma
│       └── vote.js             # Sayfa yenilenmeden AJAX oy verme
│
├── templates/                  # HTML Şablonları
│   ├── base.html               # Ortak Header, Navigasyon ve Footer
│   ├── polls/
│   │   ├── poll_list.html      # Ana sayfa (Anket akışı & filtreler)
│   │   ├── poll_detail.html    # Tekil anket görünümü & oylama
│   │   └── poll_create.html    # Yeni anket oluşturma sayfası
│   └── accounts/
│       ├── login.html          # Giriş sayfası
│       ├── register.html       # Kayıt ol sayfası
│       └── profile.html        # Profil & anket yönetim sayfası
│
├── vercel.json                 # Vercel dağıtım yapılandırması
├── requirements.txt            # Python bağımlılıkları
├── .env.example                # Ortam değişkenleri şablonu
└── manage.py
```

---

## 8. Güvenlik ve Performans Notları

1. **Supabase Connection Pooling:** Vercel serverless ortamında Django her istekte yeni bağlantı açabileceğinden, Supabase Transaction Pooler (Port 6543) connection string'i kullanılmaktadır.
2. **SECRET_KEY & DEBUG:** Canlıya (Vercel) çıkarken `DEBUG = False` ve `SECRET_KEY` çevre değişkenlerinden (Environment Variables) çekilmelidir.
3. **Mükerrer Oy Koruması:** Misafir kullanıcıların tarayıcı oturumları (`request.session.session_key`) ve kayıtlı kullanıcı hesapları baz alınarak aynı ankete ikinci kez oy verilmesi veritabanı kısıtları ile engellenmiştir.
