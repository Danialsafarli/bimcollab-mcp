import httpx
import json
from mcp.server.fastmcp import FastMCP

CLIENT_ID     = "PlayGround_Client"
CLIENT_SECRET = "k!xWcjad!u@L%ZWHc%%yKtMTqR%o1be@qWfWYaDL"
TOKEN_URL     = "https://playground.bimcollab.com/identity/connect/token"
BASE_URL      = "https://playground.bimcollab.com/bcf/3.0"

mcp = FastMCP("BIMcollab", host="0.0.0.0", port=8000)

def get_token():
    resp = httpx.post(
        TOKEN_URL,
        content=f"grant_type=client_credentials&client_id={CLIENT_ID}&client_secret=k%21xWcjad%21u%40L%25ZWHc%25%25yKtMTqR%25o1be%40qWfWYaDL&scope=bcf",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15,
    )
    print(f"Token Status: {resp.status_code}")
    print(f"Token Response: {resp.text[:300]}")
    if resp.status_code == 200:
        return resp.json().get("access_token")
    raise Exception(f"Login fehlgeschlagen: {resp.status_code} - {resp.text}")

def auth_headers():
    token = get_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

def ok(resp):
    try:
        return json.dumps(resp.json(), indent=2, ensure_ascii=False)
    except Exception:
        return resp.text

@mcp.tool()
def test_login() -> str:
    """Testet den BIMcollab Login und zeigt die genaue Antwort."""
    try:
        resp = httpx.post(
            TOKEN_URL,
            content="grant_type=client_credentials&client_id=PlayGround_Client&client_secret=k%21xWcjad%21u%40L%25ZWHc%25%25yKtMTqR%25o1be%40qWfWYaDL&scope=bcf",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15,
        )
        return f"Status: {resp.status_code}\nAntwort: {resp.text}"
    except Exception as e:
        return f"Fehler: {e}"

@mcp.tool()
def get_projects() -> str:
    """Listet alle verfuegbaren Projekte auf."""
    resp = httpx.get(f"{BASE_URL}/projects", headers=auth_headers(), timeout=15)
    return ok(resp)

@mcp.tool()
def get_project(project_id: str) -> str:
    """Gibt Details zu einem Projekt zurueck."""
    resp = httpx.get(f"{BASE_URL}/projects/{project_id}", headers=auth_headers(), timeout=15)
    return ok(resp)

@mcp.tool()
def get_project_extensions(project_id: str) -> str:
    """Gibt erlaubte Typen, Status, Prioritaeten fuer ein Projekt zurueck."""
    resp = httpx.get(f"{BASE_URL}/projects/{project_id}/extensions", headers=auth_headers(), timeout=15)
    return ok(resp)

@mcp.tool()
def get_topics(project_id: str) -> str:
    """Listet alle Topics eines Projekts auf."""
    resp = httpx.get(f"{BASE_URL}/projects/{project_id}/topics", headers=auth_headers(), timeout=15)
    return ok(resp)

@mcp.tool()
def get_topic(project_id: str, topic_id: str) -> str:
    """Gibt ein einzelnes Topic zurueck."""
    resp = httpx.get(f"{BASE_URL}/projects/{project_id}/topics/{topic_id}", headers=auth_headers(), timeout=15)
    return ok(resp)

@mcp.tool()
def create_topic(project_id: str, title: str, description: str = "", topic_type: str = "Issue", topic_status: str = "Open", priority: str = "", assigned_to: str = "", due_date: str = "") -> str:
    """Erstellt ein neues Topic (Issue)."""
    payload = {"title": title, "topic_type": topic_type, "topic_status": topic_status}
    if description: payload["description"] = description
    if priority: payload["priority"] = priority
    if assigned_to: payload["assigned_to"] = assigned_to
    if due_date: payload["due_date"] = due_date
    resp = httpx.post(f"{BASE_URL}/projects/{project_id}/topics", headers=auth_headers(), json=payload, timeout=15)
    return ok(resp)

@mcp.tool()
def update_topic(project_id: str, topic_id: str, title: str = "", description: str = "", topic_type: str = "", topic_status: str = "", priority: str = "", assigned_to: str = "", due_date: str = "") -> str:
    """Aktualisiert ein bestehendes Topic."""
    payload = {}
    if title: payload["title"] = title
    if description: payload["description"] = description
    if topic_type: payload["topic_type"] = topic_type
    if topic_status: payload["topic_status"] = topic_status
    if priority: payload["priority"] = priority
    if assigned_to: payload["assigned_to"] = assigned_to
    if due_date: payload["due_date"] = due_date
    resp = httpx.put(f"{BASE_URL}/projects/{project_id}/topics/{topic_id}", headers=auth_headers(), json=payload, timeout=15)
    return ok(resp)

@mcp.tool()
def delete_topic(project_id: str, topic_id: str) -> str:
    """Loescht ein Topic dauerhaft."""
    resp = httpx.delete(f"{BASE_URL}/projects/{project_id}/topics/{topic_id}", headers=auth_headers(), timeout=15)
    return "Geloescht" if resp.status_code == 204 else ok(resp)

@mcp.tool()
def get_comments(project_id: str, topic_id: str) -> str:
    """Gibt alle Kommentare zu einem Topic zurueck."""
    resp = httpx.get(f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/comments", headers=auth_headers(), timeout=15)
    return ok(resp)

@mcp.tool()
def create_comment(project_id: str, topic_id: str, comment: str) -> str:
    """Fuegt einen neuen Kommentar hinzu."""
    resp = httpx.post(f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/comments", headers=auth_headers(), json={"comment": comment}, timeout=15)
    return ok(resp)

@mcp.tool()
def update_comment(project_id: str, topic_id: str, comment_id: str, comment: str) -> str:
    """Bearbeitet einen Kommentar."""
    resp = httpx.put(f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/comments/{comment_id}", headers=auth_headers(), json={"comment": comment}, timeout=15)
    return ok(resp)

@mcp.tool()
def delete_comment(project_id: str, topic_id: str, comment_id: str) -> str:
    """Loescht einen Kommentar."""
    resp = httpx.delete(f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/comments/{comment_id}", headers=auth_headers(), timeout=15)
    return "Geloescht" if resp.status_code == 204 else ok(resp)

@mcp.tool()
def get_viewpoints(project_id: str, topic_id: str) -> str:
    """Gibt alle Viewpoints eines Topics zurueck."""
    resp = httpx.get(f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/viewpoints", headers=auth_headers(), timeout=15)
    return ok(resp)

@mcp.tool()
def get_viewpoint_components(project_id: str, topic_id: str, viewpoint_id: str) -> str:
    """Gibt die IFC-Komponenten eines Viewpoints zurueck."""
    resp = httpx.get(f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}/components", headers=auth_headers(), timeout=15)
    return ok(resp)

@mcp.tool()
def delete_viewpoint(project_id: str, topic_id: str, viewpoint_id: str) -> str:
    """Loescht einen Viewpoint."""
    resp = httpx.delete(f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/viewpoints/{viewpoint_id}", headers=auth_headers(), timeout=15)
    return "Geloescht" if resp.status_code == 204 else ok(resp)

@mcp.tool()
def get_related_topics(project_id: str, topic_id: str) -> str:
    """Gibt alle verwandten Topics zurueck."""
    resp = httpx.get(f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/related_topics", headers=auth_headers(), timeout=15)
    return ok(resp)

@mcp.tool()
def get_document_references(project_id: str, topic_id: str) -> str:
    """Gibt alle Dokumentverweise eines Topics zurueck."""
    resp = httpx.get(f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/document_references", headers=auth_headers(), timeout=15)
    return ok(resp)

@mcp.tool()
def create_document_reference(project_id: str, topic_id: str, url: str, description: str = "") -> str:
    """Fuegt einen externen Dokumentverweis hinzu."""
    payload = {"url": url, "is_external": True}
    if description: payload["description"] = description
    resp = httpx.post(f"{BASE_URL}/projects/{project_id}/topics/{topic_id}/document_references", headers=auth_headers(), json=payload, timeout=15)
    return ok(resp)

@mcp.tool()
def get_files(project_id: str) -> str:
    """Listet alle IFC-Dateien eines Projekts auf."""
    resp = httpx.get(f"{BASE_URL}/projects/{project_id}/files", headers=auth_headers(), timeout=15)
    return ok(resp)

if __name__ == "__main__":
    print("BIMcollab MCP Server startet...")
    mcp.run(transport="sse")
