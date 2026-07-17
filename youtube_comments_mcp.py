#!/usr/bin/env python3
"""
YouTube Comments MCP Server
---------------------------
Cowork / Claude Desktop için YouTube kanalına gelen yorumları okuyup
cevap yazmayı sağlayan bir MCP sunucusu. Tarayıcı gerektirmez;
resmi YouTube Data API v3 üzerinden çalışır.

Sağladığı araçlar (tools):
  - list_recent_comments : Kanala gelen son üst düzey yorumları getirir
  - reply_to_comment     : Bir yoruma cevap yazar
  - get_channel_info     : Bağlı kanalın kimlik bilgisini döner

Dosyalar (hepsi bu script ile aynı klasörde, ya da YOUTUBE_MCP_DIR):
  - client_secret.json : Google Cloud OAuth istemci dosyası
  - token.json         : auth_setup.py ile üretilen yetki token'ı
  - replied.json       : Cevaplanan yorum ID'lerinin yerel kaydı
"""

import os
import json
import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Ayarlar ---------------------------------------------------------------

BASE_DIR = Path(os.environ.get("YOUTUBE_MCP_DIR", Path(__file__).parent)).resolve()
TOKEN_FILE = BASE_DIR / "token.json"
CLIENT_SECRET_FILE = BASE_DIR / "client_secret.json"
REPLIED_FILE = BASE_DIR / "replied.json"

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

mcp = FastMCP("youtube-comments")


# --- Yardımcılar -----------------------------------------------------------

def _get_service():
    """Yetkilendirilmiş YouTube Data API v3 servisini döner."""
    if not TOKEN_FILE.exists():
        raise RuntimeError(
            f"token.json bulunamadı: {TOKEN_FILE}. Önce auth_setup.py çalıştırın."
        )
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
        else:
            raise RuntimeError(
                "Yetki süresi doldu ve yenilenemedi. auth_setup.py'i tekrar çalıştırın."
            )
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def _load_replied():
    if REPLIED_FILE.exists():
        try:
            return set(json.loads(REPLIED_FILE.read_text(encoding="utf-8")))
        except Exception:
            return set()
    return set()


def _save_replied(ids):
    REPLIED_FILE.write_text(json.dumps(sorted(ids)), encoding="utf-8")


def _my_channel_id(youtube):
    resp = youtube.channels().list(part="id,snippet", mine=True).execute()
    items = resp.get("items", [])
    if not items:
        raise RuntimeError("Bağlı hesapta kanal bulunamadı.")
    return items[0]["id"], items[0]["snippet"]["title"]


# --- Araçlar (tools) -------------------------------------------------------

@mcp.tool()
def get_channel_info() -> dict:
    """Bağlı YouTube kanalının ID ve adını döner. Bağlantıyı test etmek için kullanın."""
    youtube = _get_service()
    cid, title = _my_channel_id(youtube)
    return {"channel_id": cid, "title": title}


@mcp.tool()
def list_recent_comments(max_results: int = 25, only_unanswered: bool = True) -> list:
    """Kanala gelen son üst düzey yorumları getirir (en yeniden eskiye).

    Args:
        max_results: Getirilecek yorum sayısı (1-100).
        only_unanswered: True ise, kanal sahibinin cevaplamadığı ve daha önce
            bu araçla cevaplanmamış yorumları döner.

    Döner: her biri şu alanları içeren yorum listesi:
        comment_id, author, text, published_at, like_count, video_id,
        reply_count, owner_has_replied
    """
    youtube = _get_service()
    channel_id, _ = _my_channel_id(youtube)
    replied_local = _load_replied()

    # Tavan 500'e kadar; only_unanswered=True iken cevaplanmamışları bulmak için
    # gerektiği kadar sayfa gezilir (her sayfa API'de en fazla 100 yorum).
    max_results = max(1, min(int(max_results), 500))
    collected = []
    page_token = None

    while len(collected) < max_results:
        req = youtube.commentThreads().list(
            part="snippet,replies",
            allThreadsRelatedToChannelId=channel_id,
            order="time",
            maxResults=min(100, max_results - len(collected)),
            textFormat="plainText",
            pageToken=page_token,
        )
        resp = req.execute()

        for item in resp.get("items", []):
            top = item["snippet"]["topLevelComment"]
            top_id = top["id"]
            sn = top["snippet"]
            total_replies = item["snippet"].get("totalReplyCount", 0)

            # Kanal sahibi bu thread'e cevap vermiş mi?
            owner_replied = False
            for rep in item.get("replies", {}).get("comments", []):
                if rep["snippet"].get("authorChannelId", {}).get("value") == channel_id:
                    owner_replied = True
                    break
            if top_id in replied_local:
                owner_replied = True

            if only_unanswered and owner_replied:
                continue

            collected.append({
                "comment_id": top_id,
                "author": sn.get("authorDisplayName"),
                "text": sn.get("textDisplay"),
                "published_at": sn.get("publishedAt"),
                "like_count": sn.get("likeCount", 0),
                "video_id": item["snippet"].get("videoId"),
                "reply_count": total_replies,
                "owner_has_replied": owner_replied,
            })
            if len(collected) >= max_results:
                break

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return collected


@mcp.tool()
def reply_to_comment(comment_id: str, text: str) -> dict:
    """Belirtilen yoruma cevap yazar (comments.insert).

    Args:
        comment_id: Cevaplanacak üst düzey yorumun ID'si
            (list_recent_comments'tan gelen comment_id).
        text: Gönderilecek cevap metni.

    Döner: gönderilen cevabın id'si ve durumu.
    """
    if not text or not text.strip():
        raise ValueError("Boş cevap gönderilemez.")
    youtube = _get_service()
    try:
        resp = youtube.comments().insert(
            part="snippet",
            body={"snippet": {"parentId": comment_id, "textOriginal": text}},
        ).execute()
    except HttpError as e:
        return {"ok": False, "error": str(e)}

    replied = _load_replied()
    replied.add(comment_id)
    _save_replied(replied)

    return {
        "ok": True,
        "reply_id": resp.get("id"),
        "replied_to": comment_id,
        "sent_at": datetime.datetime.utcnow().isoformat() + "Z",
    }


@mcp.tool()
def list_held_comments(max_results: int = 50, include_likely_spam: bool = True) -> list:
    """İncelemeye alınmış (held) yorumları getirir — yani yayında GÖRÜNMEYEN,
    moderasyon bekleyen yorumlar.

    Args:
        max_results: Getirilecek yorum sayısı (1-100).
        include_likely_spam: True ise 'olası spam' yorumlarını da ayrıca getirir.

    Döner: her biri comment_id, author, text, published_at, video_id ve
        moderation_status ('heldForReview' veya 'likelySpam') içeren liste.
    """
    youtube = _get_service()
    channel_id, _ = _my_channel_id(youtube)
    max_results = max(1, min(int(max_results), 100))

    statuses = ["heldForReview"]
    if include_likely_spam:
        statuses.append("likelySpam")

    results = []
    for status in statuses:
        page_token = None
        while len(results) < max_results:
            try:
                resp = youtube.commentThreads().list(
                    part="snippet",
                    allThreadsRelatedToChannelId=channel_id,
                    moderationStatus=status,
                    maxResults=min(100, max_results - len(results)),
                    textFormat="plainText",
                    pageToken=page_token,
                ).execute()
            except HttpError as e:
                results.append({"error": f"{status} getirilemedi: {e}"})
                break

            for item in resp.get("items", []):
                top = item["snippet"]["topLevelComment"]
                sn = top["snippet"]
                results.append({
                    "comment_id": top["id"],
                    "author": sn.get("authorDisplayName"),
                    "text": sn.get("textDisplay"),
                    "published_at": sn.get("publishedAt"),
                    "video_id": item["snippet"].get("videoId"),
                    "moderation_status": status,
                })
            page_token = resp.get("nextPageToken")
            if not page_token:
                break

    return results


@mcp.tool()
def set_moderation_status(comment_id: str, status: str, ban_author: bool = False) -> dict:
    """Bir yorumun moderasyon durumunu değiştirir (onayla / reddet).

    Args:
        comment_id: Etkilenecek yorumun ID'si (list_held_comments'tan gelen comment_id).
        status: 'published' (onayla/yayınla), 'rejected' (reddet) veya
            'heldForReview' (tekrar incelemeye al).
        ban_author: True ve status='rejected' ise, yorum sahibini kanalda engeller.
            (Sadece reddederken anlamlıdır.)

    Döner: işlemin durumu.
    """
    status = status.strip()
    if status not in ("published", "rejected", "heldForReview"):
        raise ValueError("status yalnızca 'published', 'rejected' veya 'heldForReview' olabilir.")

    youtube = _get_service()
    params = {"id": comment_id, "moderationStatus": status}
    if status == "rejected" and ban_author:
        params["banAuthor"] = True

    try:
        youtube.comments().setModerationStatus(**params).execute()
    except HttpError as e:
        return {"ok": False, "error": str(e)}

    return {"ok": True, "comment_id": comment_id, "new_status": status, "banned_author": bool(ban_author and status == "rejected")}


if __name__ == "__main__":
    mcp.run()
