"""
BIMcollab MCP Server - Alle BCF 3.0 Funktionen
================================================
Installation:  pip install mcp httpx
Starten:       python bimcollab_server.py

Fuer Railway-Deployment: Procfile mit "web: python bimcollab_server.py" erstellen
"""

import httpx
import json
from mcp.server.fastmcp import FastMCP

# ─── Zugangsdaten (Playground) ───────────────────────────────────────────────
CLIENT_ID     = "PlayGround_Client"
CLIENT_SECRET = "k!xWcjad!u@L%ZWHc%%yKtMTqR%o1be@qWfWYaDL"
TOKEN_URL     = "https://playground.bimcollab.com/identity/connect/token"
BASE_URL      = "https://playground.bimcollab.com/bcf/3.0"
# ─────────────────────────────────────────────────────────────────────────────

mcp = FastMCP("BIMcollab", host="0.0.0.0", port=8000)
```

Dann **"Commit changes"** → Railway startet neu (~2 Min)

---

**Fix 2 — Claude.ai URL anpassen**

Die URL muss `/sse` am Ende haben:
```
https://bimcollab-mcp-production.up.railway.app/sse

# ── Hilfsfunktion: Token holen ────────────────────────────────────────────────
def get_token() -> str:
    resp = httpx.post(TOKEN_URL, data={
        "grant_type":    "client_credentials",
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope":         "bcf openid offline_access",
    }, timeout=15)
    resp.raise_for_status()
    return resp.json()["access_token"]

def headers() -> dict:
    return {
        "Authorization": f"Bearer {get_token()}",
        "Content-Type":  "application/json",
    }

def ok(resp: httpx.Response) -> str:
    try:
        return json.dumps(resp.json(), indent=2, ensure_ascii=False)
    except Exception:
        return resp.text


# ════════════════════════════════════════════════════════════════════════════
#  AUTH
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def get_auth_info() -> str:
    """Gibt die OAuth2-Endpunkte und unterstützten Grant-Types zurück."""
    resp = httpx.get(f"{BASE_URL}/auth", headers=headers(), timeout=15)
    return ok(resp)


# ════════════════════════════════════════════════════════════════════════════
#  PROJEKTE
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def get_projects() -> str:
    """Listet alle verfügbaren Projekte auf."""
    resp = httpx.get(f"{BASE_URL}/projects", headers=headers(), timeout=15)
    return ok(resp)

@mcp.tool()
def get_project(project_id: str) -> str:
    """Gibt Details zu einem bestimmten Projekt zurück.
    
    Args:
        project_id: Die ID des Projekts (aus get_projects)
    """
    resp = httpx.get(f"{BASE_URL}/projects/{project_id}", headers=headers(), timeout=15)
    return ok(resp)

@mcp.tool()
def update_project(project_id: str, name: str) -> str:
    """Ändert den Namen eines Projekts.
    
    Args:
        project_id: Die ID des Projekts
        name:       Neuer Name
    """
    resp = httpx.put(
        f"{BASE_URL}/projects/{project_id}",
        headers=headers(), timeout=15,
        json={"name": name},
    )
    return ok(resp)

@mcp.tool()
def get_project_extensions(project_id: str) -> str:
    """Gibt erlaubte Typen, Status, Prioritäten usw. für ein Projekt zurück.
    
    Args:
        project_id: Die ID des Projekts
    """
    resp = httpx.get(f"{BASE_URL}/projects/{project_id}/extensions", headers=headers(), timeout=15)
    return ok(resp)


# ════════════════════════════════════════════════════════════════════════════
#  TOPICS (Issues)
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def get_topics(project_id: str) -> str:
    """Listet alle Topics (Issues) eines Projekts auf.
    
    Args:
        project_id: Die ID des Projekts
    """
    resp = httpx.get(f"{BASE_URL}/projects/{project_id}/topics", headers=headers(), timeout=15)
    return ok(resp)

@mcp.tool()
def get_topic(project_id: str, topic_id: str) -> str:
    """Gibt ein einzelnes Topic zurück.
    
    Args:
        project_id: Die ID des Projekts
        topic_id:   Die ID des Topics
    """
    resp = httpx.get(f"{BASE_URL}/projects/{project_id}/topics/{topic_id}", headers=headers(), timeout=15)
    return ok(resp)

@mcp.tool()
def create_topic(
    project_id:   str,
    title:        str,
    description:  str = "",
    topic_type:   str = "Issue",
    topic_status: str = "Open",
    priority:     str = "",
    assigned_to:  str = "",
    due_date:     str = "",
) -> str:
    """Erstellt ein neues Topic (Issue) in einem Projekt.
    
    Args:
        project_id:   Die ID des Projekts
        title:        Titel des Issues (Pflichtfeld)
        description:  Beschreibung
        topic_type:   z.B. "Issue", "Request", "Fault"
        topic_status: z.B. "Open", "In Progress", "Closed"
        priority:     z.B. "Critical", "Major", "Normal", "Minor"
        assigned_to:  E-Mail-Adresse des Verantwortlichen
        due_date:     Fälligkeitsdatum ISO-Format, z.B. "2025-12-31T00:00:00Z"
    """
    payload: dict = {"title": title, "topic_type": topic_type, "topic_status": topic_status}
    if description:  payload["description"]  = description
    if priority:     payload["priority"]      = priority
    if assigned_to:  payload["assigned_to"]   = assigned_to
    if due_date:     payload["due_date"]       = due_date

    resp = httpx.post(
        f"{BASE_URL}/projects/{project_id}/topics",
        headers=headers(), json=payload, timeout=15,
    )
    return ok(resp)

@mcp.tool()
def update_topic(
    project_id:   str,
    topic_id:     str,
    title:        str = "",
    description:  str = "",
    topic_type:   str = "",
    topic_status: str = "",
    priority:     str = "",
    assigned_to:  str = "",
    due_date:     str = "",
) -> str:
    """Aktualisiert ein bestehendes Topic. Nur ausgefüllte Felder werden geändert.
    
    Args:
        project_id:   Die ID des Projekts
        topic_id:     Die ID des Topics
        title:        Neuer Titel
        description:  Neue Beschreibung
        topic_type:   Neuer Typ
        topic_status: Neuer Status
        priority:     Neue Priorität
        assigned_to:  Neue zugewiesene Person (E-Mail)
        due_date:     Neues Fälligkeitsdatum
    """
    payload: dict = {}
    if title:        payload["title"]         = title
    if description:  payload["description"]   = description
    if topic_type:   payload["topic_type"]    = topic_type
    if topic_status: payload["topic_status"]  = topic_status
    if priority:     payload["priority"]      = priority
    if assigned_to:  payload["assigned_to"]   = assigned_to
    if due_date:     payload["due_date"]       = due_date

    resp = httpx.put(
        f"{BASE_URL}/projects/{project_id}/topics/{topic_id}",
        headers=headers(), json=payload, timeout=15,
    )
    return ok(resp)

@mcp.tool()
def delete_topic(project_id: str, topic_id: str) -> str:
    """Löscht ein Topic dauerhaft.
    
    Args:
        project_id: Die ID des Projekts
        topic_id:   Die ID des Topics
    """
    resp = httpx.delete(
        f"{BASE_URL}/projects/{project_id}/topics/{topic_id}",
        headers=headers(), timeout=15,
    )
    return "Gelöscht" if resp.status_code == 204 else ok(resp)


# ════════════════════════════════════════════════════════════════════════════
#  KOMMENTARE
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def get_comments(project_id: str, topic_id: str) -> str:
    """Gibt alle Kommentare zu einem Topic zurück.
    
    Args:
        project_id: Die ID des Projekts
        topic_id:   Die ID des Topics
    """
    resp = httpx.get(
        f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/comments",
        headers=headers(), timeout=15,
    )
    return ok(resp)

@mcp.tool()
def get_comment(project_id: str, topic_id: str, comment_id: str) -> str:
    """Gibt einen einzelnen Kommentar zurück.
    
    Args:
        project_id: Die ID des Projekts
        topic_id:   Die ID des Topics
        comment_id: Die ID des Kommentars
    """
    resp = httpx.get(
        f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/comments/{comment_id}",
        headers=headers(), timeout=15,
    )
    return ok(resp)

@mcp.tool()
def create_comment(project_id: str, topic_id: str, comment: str, viewpoint_id: str = "") -> str:
    """Fügt einen neuen Kommentar zu einem Topic hinzu.
    
    Args:
        project_id:   Die ID des Projekts
        topic_id:     Die ID des Topics
        comment:      Der Kommentartext
        viewpoint_id: Optional: ID eines verknüpften Viewpoints
    """
    payload: dict = {"comment": comment}
    if viewpoint_id:
        payload["viewpoint"] = {"guid": viewpoint_id}

    resp = httpx.post(
        f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/comments",
        headers=headers(), json=payload, timeout=15,
    )
    return ok(resp)

@mcp.tool()
def update_comment(project_id: str, topic_id: str, comment_id: str, comment: str) -> str:
    """Bearbeitet einen Kommentar.
    
    Args:
        project_id: Die ID des Projekts
        topic_id:   Die ID des Topics
        comment_id: Die ID des Kommentars
        comment:    Neuer Text
    """
    resp = httpx.put(
        f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/comments/{comment_id}",
        headers=headers(), json={"comment": comment}, timeout=15,
    )
    return ok(resp)

@mcp.tool()
def delete_comment(project_id: str, topic_id: str, comment_id: str) -> str:
    """Löscht einen Kommentar.
    
    Args:
        project_id: Die ID des Projekts
        topic_id:   Die ID des Topics
        comment_id: Die ID des Kommentars
    """
    resp = httpx.delete(
        f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/comments/{comment_id}",
        headers=headers(), timeout=15,
    )
    return "Gelöscht" if resp.status_code == 204 else ok(resp)


# ════════════════════════════════════════════════════════════════════════════
#  VIEWPOINTS
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def get_viewpoints(project_id: str, topic_id: str) -> str:
    """Gibt alle Viewpoints (Kameraansichten) eines Topics zurück.
    
    Args:
        project_id: Die ID des Projekts
        topic_id:   Die ID des Topics
    """
    resp = httpx.get(
        f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/viewpoints",
        headers=headers(), timeout=15,
    )
    return ok(resp)

@mcp.tool()
def get_viewpoint(project_id: str, topic_id: str, viewpoint_id: str) -> str:
    """Gibt einen einzelnen Viewpoint zurück.
    
    Args:
        project_id:   Die ID des Projekts
        topic_id:     Die ID des Topics
        viewpoint_id: Die ID des Viewpoints
    """
    resp = httpx.get(
        f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}",
        headers=headers(), timeout=15,
    )
    return ok(resp)

@mcp.tool()
def create_viewpoint(
    project_id:  str,
    topic_id:    str,
    camera_x:    float = 0.0,
    camera_y:    float = 0.0,
    camera_z:    float = 10.0,
    target_x:    float = 0.0,
    target_y:    float = 0.0,
    target_z:    float = 0.0,
) -> str:
    """Erstellt einen neuen Viewpoint mit Perspektivkamera.
    
    Args:
        project_id: Die ID des Projekts
        topic_id:   Die ID des Topics
        camera_x/y/z: Kameraposition in Weltkoordinaten
        target_x/y/z: Zielpunkt der Kamera
    """
    payload = {
        "perspective_camera": {
            "camera_view_point": {"x": camera_x, "y": camera_y, "z": camera_z},
            "camera_direction":  {"x": target_x - camera_x, "y": target_y - camera_y, "z": target_z - camera_z},
            "camera_up_vector":  {"x": 0, "y": 0, "z": 1},
            "field_of_view": 60,
        }
    }
    resp = httpx.post(
        f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/viewpoints",
        headers=headers(), json=payload, timeout=15,
    )
    return ok(resp)

@mcp.tool()
def delete_viewpoint(project_id: str, topic_id: str, viewpoint_id: str) -> str:
    """Löscht einen Viewpoint.
    
    Args:
        project_id:   Die ID des Projekts
        topic_id:     Die ID des Topics
        viewpoint_id: Die ID des Viewpoints
    """
    resp = httpx.delete(
        f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}",
        headers=headers(), timeout=15,
    )
    return "Gelöscht" if resp.status_code == 204 else ok(resp)

@mcp.tool()
def get_viewpoint_snapshot(project_id: str, topic_id: str, viewpoint_id: str) -> str:
    """Gibt die URL des Screenshot-Bilds eines Viewpoints zurück.
    
    Args:
        project_id:   Die ID des Projekts
        topic_id:     Die ID des Topics
        viewpoint_id: Die ID des Viewpoints
    """
    url = f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}/snapshot"
    return f"Snapshot-URL: {url}\n(Mit Authorization-Header abrufbar)"

@mcp.tool()
def get_viewpoint_components(project_id: str, topic_id: str, viewpoint_id: str) -> str:
    """Gibt die sichtbaren/ausgewählten IFC-Komponenten eines Viewpoints zurück.
    
    Args:
        project_id:   Die ID des Projekts
        topic_id:     Die ID des Topics
        viewpoint_id: Die ID des Viewpoints
    """
    resp = httpx.get(
        f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}/components",
        headers=headers(), timeout=15,
    )
    return ok(resp)


# ════════════════════════════════════════════════════════════════════════════
#  RELATED TOPICS (Verknüpfungen zwischen Issues)
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def get_related_topics(project_id: str, topic_id: str) -> str:
    """Gibt alle verwandten Topics zurück.
    
    Args:
        project_id: Die ID des Projekts
        topic_id:   Die ID des Topics
    """
    resp = httpx.get(
        f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/related_topics",
        headers=headers(), timeout=15,
    )
    return ok(resp)

@mcp.tool()
def create_related_topic(project_id: str, topic_id: str, related_topic_id: str) -> str:
    """Verknüpft zwei Topics miteinander.
    
    Args:
        project_id:        Die ID des Projekts
        topic_id:          Die ID des Ausgangs-Topics
        related_topic_id:  Die ID des zu verknüpfenden Topics
    """
    resp = httpx.post(
        f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/related_topics",
        headers=headers(),
        json=[{"related_topic_guid": related_topic_id}],
        timeout=15,
    )
    return ok(resp)


# ════════════════════════════════════════════════════════════════════════════
#  DOCUMENT REFERENCES (Dateiverweise)
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def get_document_references(project_id: str, topic_id: str) -> str:
    """Gibt alle Dokumentverweise eines Topics zurück.
    
    Args:
        project_id: Die ID des Projekts
        topic_id:   Die ID des Topics
    """
    resp = httpx.get(
        f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/document_references",
        headers=headers(), timeout=15,
    )
    return ok(resp)

@mcp.tool()
def create_document_reference(
    project_id:   str,
    topic_id:     str,
    url:          str,
    description:  str = "",
) -> str:
    """Fügt einen externen Dokumentverweis zu einem Topic hinzu.
    
    Args:
        project_id:  Die ID des Projekts
        topic_id:    Die ID des Topics
        url:         URL des Dokuments
        description: Beschreibung des Verweises
    """
    payload: dict = {"url": url, "is_external": True}
    if description:
        payload["description"] = description

    resp = httpx.post(
        f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/document_references",
        headers=headers(), json=payload, timeout=15,
    )
    return ok(resp)


# ════════════════════════════════════════════════════════════════════════════
#  DATEIEN / FILES
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def get_files(project_id: str) -> str:
    """Listet alle IFC-Dateien auf, die einem Projekt zugeordnet sind.
    
    Args:
        project_id: Die ID des Projekts
    """
    resp = httpx.get(f"{BASE_URL}/projects/{project_id}/files", headers=headers(), timeout=15)
    return ok(resp)


# ════════════════════════════════════════════════════════════════════════════
#  EINTRAG STARTEN
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("BIMcollab MCP Server startet...")
    mcp.run(transport="sse")
