import asyncio
from fastmcp import Client


async def test_server():
    """Test du serveur Error Fixer MCP Server avec le client FastMCP officiel"""
    print("🚀 Démarrage des tests MCP Server Error Fixer")
    print("📍 URL cible : http://localhost:8083/mcp")
    print("="*50)

    # Connexion au serveur MCP via transport streamable-http
    async with Client("http://localhost:8083/mcp") as client:

        # ─────────────────────────────────────────────────────────
        # TEST 1 : Lister les tools disponibles
        # ─────────────────────────────────────────────────────────
        print("\n" + "="*50)
        print("TEST 1 : Lister les Tools MCP")
        print("="*50)

        tools = await client.list_tools()
        print("client.list_tools()")
        print(tools)

        print("--- 🛠️ Tools trouvés ---")
        for tool in tools:
            print(f"  • {tool.name}")
            print(f"    Description: {tool.description or 'N/A'}")


        # ─────────────────────────────────────────────────────────
        # TEST 2 : Appel du tool get_diff_push
        # ─────────────────────────────────────────────────────────
        print("\n" + "="*50)
        print("TEST 2 : get_diff_push")
        print("="*50)

        print("--- 🪛 Appel du tool get_diff_push pour Safwen707/ams_jenkins ---")

        result = await client.call_tool(
            "get_diff_push",
            {
                "repo_owner": "Safwen707",
                "repo_name": "ams_jenkins",
                "commit_sha": "5e74bcd7995c1e8dba8c6be0ef2c329b99ada436"
            }
        )

        print(f"--- ✅ Succès : {result.content[0].text} ---")


        # ─────────────────────────────────────────────────────────
        # TEST 3 : Appel du tool get_jenkins_logs (optionnel)
        # Décommentez si votre serveur Jenkins est accessible
        # ─────────────────────────────────────────────────────────
        # print("\n" + "="*50)
        # print("TEST 3 : get_jenkins_logs")
        # print("="*50)
        #
        # print("--- 🪛 Appel du tool get_jenkins_logs pour job springboot-user-service ---")
        #
        # result = await client.call_tool(
        #     "get_jenkins_logs",
        #     {
        #         "job_name": "springboot-user-service",
        #         "build_number": "42"
        #     }
        # )
        #
        # print(f"--- ✅ Succès : {result.content[0].text} ---")

    print("\n" + "="*50)
    print("✅ Tests terminés")
    print("="*50)


if __name__ == "__main__":
    asyncio.run(test_server())
