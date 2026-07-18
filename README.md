# YouTube Yorum Cevaplama — Cowork için MCP Sunucusu

Kanalına gelen yorumları her sabah tarayıp cevap yazmayı sağlayan bir MCP sunucusu.
Tarayıcı otomasyonu yok — doğrudan **YouTube Data API v3** kullanır, bu yüzden hızlı ve kararlıdır.

**Politika (zamanlanmış görevde uygulanır):**
- **Moderasyon:** İncelemeye alınmış (held/olası spam) yorumlardan zararsız
  olanlar → otomatik onaylanır. Olumsuz, gerçek spam veya siyasi/imalı olanlar →
  held bırakılır, elle karar verirsin.
- **Cevap:** Soru **içermeyen** basit yorumlar (teşekkür, "elinize sağlık" vb.)
  → otomatik cevap. Soru **içeren** yorumlar → taslak hazırlanır, sen
  onaylayınca gönderilir.

---

## Dosyalar

| Dosya | Ne işe yarar |
|---|---|
| `youtube_comments_mcp.py` | MCP sunucusu (5 araç: kanal bilgisi, yorum getir, cevap yaz, held yorumları getir, moderasyon durumu değiştir) |
| `auth_setup.py` | Tek seferlik OAuth yetkilendirme scripti (token.json üretir) |
| `requirements.txt` | Python bağımlılıkları |
| `client_secret.json` | *(sen ekleyeceksin)* Google Cloud OAuth istemci dosyası |
| `token.json` | *(otomatik oluşur)* Yetki token'ı |

Hepsini tek bir klasöre koy, örn: `C:\youtube-mcp\`

---

## Adım 1 — Google Cloud kurulumu (tek seferlik)

1. [Google Cloud Console](https://console.cloud.google.com/)'a git, yeni bir proje oluştur.
2. **APIs & Services > Library** → **YouTube Data API v3**'ü etkinleştir.
3. **APIs & Services > OAuth consent screen**:
   - User Type: **External**
   - Uygulama adını gir, zorunlu alanları doldur.
   - **Test users** kısmına kanalının sahibi olan Google hesabını ekle.
   - Scope olarak `.../auth/youtube.force-ssl` yeterli.
4. **APIs & Services > Credentials** → **Create Credentials > OAuth client ID**:
   - Application type: **Desktop app**
   - JSON'u indir, adını `client_secret.json` yapıp klasöre koy.

> Not: Uygulama "Testing" modundayken token 7 günde bir yenilenmesi gerekebilir.
> Sürekli çalışması için OAuth consent screen'i **Publish** (yayınla) edersen bu sınır kalkar.

---

## Adım 2 — Python bağımlılıkları

Klasörde bir terminal aç:

```bash
pip install -r requirements.txt
```

---

## Adım 3 — Yetkilendirme (tek seferlik)

```bash
python auth_setup.py
```

Tarayıcı açılır → kanalının sahibi olan hesapla giriş yap → izin ver.
Bittiğinde klasörde `token.json` oluşur. Bir daha tarayıcı gerekmez (token otomatik yenilenir).

---

## Adım 4 — Claude Desktop'a MCP olarak ekle

Claude Desktop ayar dosyasını aç:

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

`mcpServers` altına şunu ekle (yolları kendi klasörüne göre düzelt):

```json
{
  "mcpServers": {
    "youtube-comments": {
      "command": "python",
      "args": ["C:\\youtube-mcp\\youtube_comments_mcp.py"],
      "env": {
        "YOUTUBE_MCP_DIR": "C:\\youtube-mcp"
      }
    }
  }
}
```

> `python` komutu PATH'te değilse tam yol ver (örn. `C:\\Python312\\python.exe`).
> macOS'ta ters bölü yerine normal yol: `"/Users/kmk/youtube-mcp/youtube_comments_mcp.py"`.

Claude Desktop'ı tamamen kapatıp yeniden aç. Artık Claude'da şu araçlar görünür:
`get_channel_info`, `list_recent_comments`, `reply_to_comment`,
`list_held_comments`, `set_moderation_status`.

---

## Adım 5 — Test et

Cowork/Claude'a şunu yaz:

> Kanalıma bağlı mı kontrol et (get_channel_info) ve son 5 cevaplanmamış yorumu getir.

Kanal adın ve yorumlar gelirse kurulum tamam.

---

## Adım 6 — Her sabah otomatik çalıştır

`gunluk_gorev_promptu.md` dosyasındaki promptu kullanarak Cowork'te zamanlanmış
bir görev oluştur (ben bunu senin için kurabilirim). Görev her sabah:
1. Held (incelemede bekleyen) yorumları çeker, zararsız olanları otomatik
   onaylar, şüphelileri held bırakır,
2. Cevaplanmamış yayındaki yorumları çeker,
3. Soru içermeyenlere otomatik cevap yazar, soru içerenlere taslak hazırlayıp
   sana onaya sunar,
4. Hepsini tek bir yapısal raporda özetler.

---

## Kota ve maliyet

YouTube Data API günlük ücretsiz kota: **10.000 birim**.
Yorum okuma ~1, cevap yazma ~50 birim. Günde onlarca cevap yazsan bile kota bitmez.

## Güvenlik

Bu sunucu video yükleme/silme gibi yetkiler içermez, ama şunları yapabilir:
yorum **okuma**, yorumlara **cevap yazma**, ve yorum **moderasyonu**
(`set_moderation_status` ile bir yorumu yayınlama/reddetme, `ban_author=true`
ile yorum sahibini kanaldan **engelleme**). Bu son ikisi kanalına yazma/yönetim
erişimi gerektirir; `client_secret.json` ve `token.json` dosyalarını kimseyle
paylaşma.
