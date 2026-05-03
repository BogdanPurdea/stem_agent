import os
from stem_agent.graph import graph

def visualize():
    # 1. Generate Mermaid text
    mermaid_text = graph.get_graph().draw_mermaid()
    print("--- Mermaid Graph Definition ---")
    print(mermaid_text)
    print("--- End of Mermaid ---\n")

    # 2. Try to save as PNG (requires internet for Mermaid.ink or local pygraphviz/mermaid-cli)
    try:
        png_data = graph.get_graph().draw_mermaid_png()
        output_path = "visual/graph_visualization.png"
        with open(output_path, "wb") as f:
            f.write(png_data)
        print(f"Graph visualization saved to: {os.path.abspath(output_path)}")
    except Exception as e:
        print(f"Could not generate PNG: {e}")
        print("Tip: Ensure you have an active internet connection for the Mermaid.ink API.")

if __name__ == "__main__":
    visualize()
