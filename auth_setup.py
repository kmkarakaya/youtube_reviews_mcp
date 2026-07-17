#!/usr/bin/env python3
"""
Tek seferlik OAuth kurulumu.
-----------------------------
Bu scripti bir kez çalıştırın. Tarayıcı açılır, YouTube kanalınızın sahibi
olan Google hesabıyla giriş yapıp izin verirsiniz. Sonuçta yanına token.json
dosyası oluşur ve MCP sunucusu bir daha tarayıcı gerektirmez (token otomatik
yenilenir).

Kullanım:
    python auth_setup.py

Gereken dosya: client_secret.json (Google Cloud'dan indirdiğiniz OAuth istemci
dosyası) bu script ile aynı klasörde olmalı.
"""

import os
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

BASE_DIR = Path(os.environ.get("YOUTUBE_MCP_DIR", Path(__file__).parent)).resolve()
CLIENT_SECRET_FILE = BASE_DIR / "client_secret.json"
TOKEN_FILE = BASE_DIR / "token.json"

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]


def main():
    if not CLIENT_SECRET_FILE.exists():
        raise SystemExit(
            f"client_secret.json bulunamadı: {CLIENT_SECRET_FILE}\n"
            "Google Cloud'dan indirip bu klasöre koyun (README 1. adım)."
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
    # Yerel bir sunucu açıp tarayıcı üzerinden yetki alır.
    creds = flow.run_local_server(port=0)

    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    print(f"\n✅ Başarılı. Token kaydedildi: {TOKEN_FILE}")
    print("Artık MCP sunucusunu kullanabilirsiniz.")


if __name__ == "__main__":
    main()
