# YouTube Yorum Cevaplama + Moderasyon — Cowork için MCP Sunucusu

Kanalına gelen **video yorumlarını** her sabah tarayıp cevaplayan ve incelemede
bekleyen (held) yorumları modere eden bir MCP sunucusu. Tarayıcı otomasyonu yok —
doğrudan **YouTube Data API v3** kullanır, bu yüzden hızlı ve kararlıdır.

> **Önemli sınır:** YouTube API'si **Topluluk (Community) gönderisi yorumlarını
> desteklemez.** Bu sistem yalnızca video yorumlarını işler; topluluk gönderisi
> yorumları elle (Studio'dan) cevaplanır.

**Cevap politikası (zamanlanmış görevde uygulanır):**

- Süre/tamamlama yorumları (ör. "2 saat 9 dakika") → eğitimi sonuna kadar izleyene özel teşekkür
- Etkileşim/destek yorumları (ör. "+D e s t e k+", "etkileşim") → kısa teşekkür (spam sayılmaz)
- Basit teşekkür/övgü → otomatik kısa teşekkür
- Soru içerenler → taslak hazırlanır, sen onaylayınca gönderilir
- Siyasi/imalı yorumlar → cevaplanmaz, held ise onaylanmaz (tarafsızlık)

---

## Dosyalar (hepsi `C:\Codes\youtube_mcp` klasöründe)

| Dosya                       | Ne işe yarar                                                                                                                                   |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `youtube_comments_mcp.py` | MCP sunucusu — 5 araç:`get_channel_info`, `list_recent_comments`, `reply_to_comment`, `list_held_comments`, `set_moderation_status` |
| `auth_setup.py`           | OAuth yetkilendirme scripti (`token.json` üretir)                                                                                            |
| `requirements.txt`        | Python bağımlılıkları                                                                                                                      |
| `gunluk_gorev_promptu.md` | Zamanlanmış görevin prompt metni (referans)                                                                                                  |
| `client_secret.json`      | *(sen ekledin)* Google Cloud OAuth istemci dosyası                                                                                           |
| `token.json`              | *(otomatik oluşur)* Yetki token'ı                                                                                                           |

---

## Adım 1 — Google Cloud kurulumu (tek seferlik)

1. [Google Cloud Console](https://console.cloud.google.com/)'da proje oluştur.
2. **APIs & Services > Library** → **YouTube Data API v3**'ü etkinleştir.
3. Yeni arayüzde **Google Auth Platform**:
   - **Branding/Overview**: uygulama adı ve destek e-postası.
   - **Audience**: User type **External**; kanal sahibi hesabı test kullanıcısı ekle.
   - **Publishing status**: **In production** yap ("PUBLISH APP"). Bu önemli —
     "Testing" modunda token her **7 günde bir** geçersiz olur; production'da olmaz.
4. **Clients / Credentials** → **Create OAuth client ID** → tür **Desktop app** →
   JSON'u indir, adını `client_secret.json` yap ve klasöre koy.

---

## Adım 2 — Python bağımlılıkları

`C:\Codes\youtube_mcp` klasöründe komut penceresi aç (adres çubuğuna `cmd` yazıp Enter):

```
pip install -r requirements.txt
```

---

## Adım 3 — Yetkilendirme (token alma)

```
C:\Users\KMK\miniconda3\python.exe auth_setup.py
```

Tarayıcı açılır. Sırasıyla:

1. Kanal sahibi Google hesabıyla giriş yap.
2. **"Google bu uygulamayı doğrulamadı"** uyarısı çıkarsa (kendi uygulaman
   olduğu için normaldir): sol alttaki **"Gelişmiş" / "Advanced"** → altta çıkan
   **"... (güvenli değil) sayfasına git"** bağlantısına tıkla.
3. İzin ekranında **"İzin ver / Allow"** de.
4. Komut penceresinde **"✅ Başarılı. Token kaydedildi"** görünce tamam.

`token.json` klasörde oluşur. (Uygulama production'da olduğu için token kalıcıdır.)

---

## Adım 4 — Claude Desktop'a MCP olarak ekle

`%APPDATA%\Claude\claude_desktop_config.json` dosyasını **Claude kapalıyken** aç ve
`mcpServers` altına ekle:

```json
{
  "mcpServers": {
    "youtube-comments": {
      "command": "C:\\Users\\KMK\\miniconda3\\python.exe",
      "args": ["C:\\Codes\\youtube_mcp\\youtube_comments_mcp.py"],
      "env": { "YOUTUBE_MCP_DIR": "C:\\Codes\\youtube_mcp" }
    }
  }
}
```

Kaydet, Claude'u tamamen kapatıp yeniden aç. (Config'i Claude açıkken düzenlersen
kapanışta üzerine yazabilir — bu yüzden önce kapat.)

---

## Adım 5 — Test et

Yeni bir sohbette: *"get_channel_info aracını çağır ve kanalımın adını söyle."*
Kanal adın gelirse bağlantı tamam.

---

## Adım 6 — Her sabah otomatik çalıştır

`gunluk_gorev_promptu.md` içeriğiyle Cowork'te zamanlanmış görev kurulur
(`youtube-yorum-cevaplama`, her sabah). Görev: held moderasyonu → video
yorumlarına cevap → yapısal rapor. Kenar çubuğundaki **Scheduled** bölümünden
görülür; bir kez **Run now** yaparak izinleri önden onaylaman önerilir.

---

## Sorun giderme

**`invalid_grant: Token has been expired or revoked`** → Token düşmüş. Çözüm:
Adım 3'teki `auth_setup.py`'yi tekrar çalıştır (yeni `token.json` üretir). Tekrar
tekrar yaşanıyorsa Adım 1.3'teki **Publishing status = In production** ayarını yap.

**Araçlar Claude'da görünmüyor** → Config'i Claude kapalıyken düzenle, sonra aç.
Developer/Connectors yerine yeni araçlar sohbette araç çağrısıyla test edilir.

**"Yeni cevapsız yorum yok" ama Studio'da yorum görüyorum** → O yorumlar büyük
ihtimalle **Topluluk gönderilerinde** (API erişemez) ya da senin kendi
yorumların/siyasi yorumlar (kurallar gereği atlanır).

---

## Kota, kapsam ve güvenlik

- Günlük ücretsiz kota **10.000 birim**; yorum okuma ~1, cevap yazma ~50 birim. Fazlasıyla yeter.
- Sunucu yalnızca yorum **okuma**, **cevap yazma** ve **moderasyon** (onayla/held) yapar.
  `rejected`/yazar engelleme yalnızca senin açık talimatınla yapılır; video yükleme/silme yetkisi yoktur.
- `client_secret.json` ve `token.json` dosyalarını kimseyle paylaşma — kanalına yazma erişimi verirler.
