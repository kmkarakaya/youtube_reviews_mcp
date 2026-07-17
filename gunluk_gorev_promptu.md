# Günlük YouTube Yorum + Moderasyon — Zamanlanmış Görev Promptu

Sıra: **1) Held moderasyonu → 2) Yayındaki yorumlara cevap → 3) Yapısal rapor.**
(Aynısı Cowork "Scheduled" bölümünde kayıtlı; bu kopya referans içindir.)

---

## ADIM 1: Held (incelemede bekleyen) yorumların moderasyonu

- `list_held_comments` → `max_results=100`, `include_likely_spam=true`.
- Her held yorum için:
  - **Etkileşim/destek yorumları** ("+D e s t e k+", "etkileşim", "@", ".", tek
    emoji vb.) → spam DEĞİL, **onayla**.
  - ONAYLA ayrıca: negatiflik (küfür, hakaret, aşağılama, nefret, taciz, tehdit)
    YOK **ve** gerçek spam/reklam/link DEĞİL **ve** siyasi/ideolojik/imalı DEĞİL →
    `set_moderation_status(status="published")` ile **otomatik onayla**.
  - Olumsuzluk VEYA gerçek spam (link/reklam) VAR → **onaylama**, held bırak.
  - Siyasi/ideolojik/imalı → **onaylama**, held bırak. Rapora "siyasi/imalı" nedeniyle al.
  - Sınırda/belirsiz → **onaylama**, held bırak, "belirsiz" olarak rapora al.
  - `rejected` ve `ban_author` ASLA otomatik yapılmaz; sadece açık talimatla.

## ADIM 2: Yayındaki yorumlara cevap

(Not: Adım 1'de onaylanan yorumlar artık yayında; burada da karşına çıkabilir.)

- `list_recent_comments` → `only_unanswered=true`, `max_results=100`. Dönen TÜM
  cevaplanmamış yorumları işle; ilk birkaçıyla yetinme.
- **SİYASİ/İMALI** (cevap yazma): Siyasi/ideolojik/imalı/kışkırtıcı yorumlara
  tarafsızlık için **cevap yazma**; sadece raporda "cevaplanmadı: siyasi/imalı"
  olarak belirt. Örnek: "...TÜBİTAK diye güzide bir araştırma kurumumuz vardı ama işte".
- **ETKİLEŞİM/DESTEK**: Kısa/destek yorumları ("+D e s t e k+", "etkileşim", "@",
  ".", tek emoji, tek kelime) — izleyicilerden yorum bırakmalarını rica ettiğim için
  gelir, **spam değildir**. Kısa teşekkürle (ör. "Desteğiniz için teşekkürler 🙏")
  hemen cevapla.
- **SÜRE/TAMAMLAMA** (özel, önemli): Yorum bir video süresi/zaman damgası ise
  (örn. "2 saat 28 dakika 8 saniye", "2 saat 9 dakika", "1:45:30") → izleyici
  eğitimi **sonuna kadar** izlemiş demektir (video sonundaki şifre). Sonuna kadar
  izledikleri için özel, içten ve tekdüze olmayan teşekkür yaz, **hemen gönder**.
- **BASİT** (soru yok): kısa, samimi teşekkür yaz, `reply_to_comment` ile **hemen gönder**.
- **SORULU**: gönderme; taslağı raporda göster, onay iste, onaylanınca gönder.
  Taslak yazarken: teknik cevabı **biliyorsan** doğrudan/öz cevap ver; soru
  **belirsizse** hiçbir yardım vaadi vermeden sadece nazikçe tam anlayamadığını
  söyle ("Sorunuzu tam anlayamadım 🙏").

## ADIM 3: Yapısal rapor (sabit şablon)

```
## 📊 Günlük Yorum Raporu — {tarih}

### 1. Held Moderasyon
- Toplam: X | Otomatik onaylanan: Y | Onaylanmayan: Z
[Onaylanmayanlar tablosu: Yazar | Alıntı | Neden]

### 2. Yayındaki Yorumlara Cevap
- Otomatik cevaplanan: A
[Tablo: Yazar | Yorum | Gönderilen cevap]

### 3. ⏳ Onayını Bekleyenler (sorulu)
- Adet: B
[Tablo: # | Yazar | Yorum | Önerilen taslak]

### 4. ✅ Senden Beklenen Aksiyon
- Maddeler: onaylanacak taslaklar, elle bakılacak held yorumlar
```

Rapor sonunda: "Onaylanacak taslak var mı? Numara ver, göndereyim." diye sor.

## Uyulması zorunlu kurallar

- GELECEK TAAHHÜDÜ / YARDIM VAADİ YASAK. Şunları ASLA yazma: "birlikte bakarız",
  "paylaşırsanız bakarım/yardımcı olurum", "yardımcı olmaya çalışırım",
  "yapacağım/ekleyeceğim". Ya bildiğin teknik cevabı ver, ya da belirsizse sadece
  nazikçe anlayamadığını söyle. Nötr teşekkür: "Yorumunuz için teşekkürler!
  Geri bildiriminizi dikkate alacağım 🙏".
- Veri seti / kod / sunum kaynakları **AI SAGE** üyeleriyle paylaşılıyor.
  Soranı kanal üyeliğine (Katıl/Join) yönlendir; link verme.
- Emin olamadığın yorumu SORULU'ya al ve sor; küfür/spam'e cevap yazma.
- Bilmediğin bilgiyi (link, tarih, teknik detay) uydurma.
- Aynı kişi aynı yorumu birden fazla videoda yaptıysa her birine ayrı cevap ver.
```
