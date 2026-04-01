from engine.tools.browsing_tool import BrowsingTool

def debug_browsing():
    bt = BrowsingTool()
    url = "https://it.wikipedia.org/wiki/Python_(linguaggio_di_programmazione)"
    print(f"🌍 Tentativo di browsing su: {url}")
    
    res = bt.browse_url(url)
    if res["success"]:
        print(f"✅ Successo! Titolo: {res['title']}")
        print(f"📄 Contenuto (primi 100 char): {res['content'][:100]}...")
    else:
        print(f"❌ Fallimento: {res.get('error', 'Errore sconosciuto')}")

if __name__ == "__main__":
    debug_browsing()
