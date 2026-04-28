import base64
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from cricify import fetch_live_events, fetch_channel_streams, parse_stream_link

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MANIFEST = {
    "id": "org.cricify.addon",
    "version": "1.0.0",
    "name": "Cricify",
    "description": "Cricify live streaming Stremio addon",
    "types": ["tv"],
    "catalogs": [
        {
            "type": "tv",
            "id": "cricify_live",
            "name": "Live Events",
            "extra": []
        }
    ],
    "resources": ["catalog", "meta", "stream"],
    "behaviorHints": {
        "configurable": True
    }
}

@app.get("/")
def read_root():
    return {"message": "Cricify Addon is running. Add /manifest.json to Stremio."}

@app.get("/manifest.json")
def get_manifest():
    return MANIFEST

@app.get("/catalog/tv/cricify_live.json")
def get_catalog():
    events = fetch_live_events()
    metas = []
    
    for event in events:
        event_info = event.get("eventInfo", {})
        title = event.get("title", "Unknown Event")
        slug = event.get("slug", "")
        
        team_a = event_info.get("teamA", "")
        team_b = event_info.get("teamB", "")
        if team_a and team_b:
            if team_a == team_b:
                display_title = team_a
            else:
                display_title = f"{team_a} vs {team_b}"
        else:
            display_title = title
            
        category = event_info.get("eventCat", event.get("cat", "Other"))

        # Meta obj for Stremio
        metas.append({
            "id": f"cricify:{slug}",
            "type": "tv",
            "name": display_title,
            "poster": "", # Can use the generated match card URL if needed
            "posterShape": "landscape",
            "description": f"Category: {category}\n" + (f"Event: {event_info.get('eventName', '')}" if event_info.get('eventName') else ""),
        })

    return {"metas": metas}

@app.get("/meta/tv/{id}.json")
def get_meta(id: str):
    if not id.startswith("cricify:"):
        return {"meta": {}}
        
    slug = id.replace("cricify:", "")
    events = fetch_live_events()
    event = next((e for e in events if e.get("slug") == slug), None)
    
    if not event:
        return {"meta": {}}

    event_info = event.get("eventInfo", {})
    title = event.get("title", "Unknown Event")
    
    team_a = event_info.get("teamA", "")
    team_b = event_info.get("teamB", "")
    if team_a and team_b:
        if team_a == team_b:
            display_title = team_a
        else:
            display_title = f"{team_a} vs {team_b}"
    else:
        display_title = title

    meta = {
        "id": id,
        "type": "tv",
        "name": display_title,
        "posterShape": "landscape",
        "description": f"Event: {event_info.get('eventName', '')}"
    }

    return {"meta": meta}

@app.get("/stream/tv/{id}.json")
def get_stream(id: str):
    if not id.startswith("cricify:"):
        return {"streams": []}
        
    slug = id.replace("cricify:", "")
    channel_data = fetch_channel_streams(slug)
    
    if not channel_data or not channel_data.get("streamUrls"):
        return {"streams": []}
        
    streams = []
    
    for stream in channel_data.get("streamUrls", []):
        link = stream.get("link")
        if not link: continue
            
        url, headers = parse_stream_link(link)
        server_name = stream.get("title", "Server")
        
        stremio_stream = {
            "name": f"Cricify\n{server_name}",
            "description": f"Type: {stream.get('type', 'Unknown')}",
            "url": url,
            "behaviorHints": {
                "notWebReady": True
            }
        }
        
        if headers:
            stremio_stream["behaviorHints"]["headers"] = headers
            
        # Handle DRM if type is "7"
        if stream.get("type") == "7":
            # MPD with DRM (ClearKey)
            drm_info = stream.get("api", "").split(":")
            if len(drm_info) == 2:
                # Add custom behavior hints or query params for external players
                # Stremio's native Exoplayer might need specific format for ClearKey
                # We pass keys in the description for transparency, and try to pass to player if supported
                try:
                    drm_kid_hex = drm_info[0].replace("-", "")
                    drm_key_hex = drm_info[1].replace("-", "")
                    
                    stremio_stream["description"] += f"\nDRM ClearKey"
                    # Note: We can't directly play DRM in default stremio web player
                except Exception:
                    pass
                
        streams.append(stremio_stream)
        
    return {"streams": streams}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
