import streamlit as st
import os
import json
from pathlib import Path

from directory_scanner import scan_directory
from graph_visualization import create_force_directed_graph
from utils import get_safe_path

# Try to import envscan detection (optional)
try:
    from envscan.detector import find_python_environments
except Exception:
    # Fallback when envscan package isn't available during development
    def find_python_environments(path, max_depth=3, include_hidden=False, follow_symlinks=False):
        return []

# Set page configuration
st.set_page_config(
    page_title="Directory Visualizer",
    page_icon="📂",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Directory Structure Visualizer - A tool to visualize directory structures as interactive force-directed graphs."
    }
)

# Initialize session state variables if they don't exist
if 'directory_data' not in st.session_state:
    st.session_state.directory_data = None
if 'selected_directory' not in st.session_state:
    st.session_state.selected_directory = None

def main():
    # App title and description
    st.title("Directory Structure Visualizer")
    st.markdown("Visualize your directory structure as an interactive force-directed graph.")
    
    # Sidebar for directory selection
    with st.sidebar:
        st.header("Directory Selection")
        
        # Option to use a sample directory or choose a path
        option = st.radio(
            "Choose an option:",
            ["Enter directory path", "Use current working directory"]
        )
        
        if option == "Enter directory path":
            directory_path = st.text_input("Enter directory path:", "")
        else:
            directory_path = os.getcwd()
            st.info(f"Using current directory: {directory_path}")
        
        depth_limit = st.slider("Max directory depth:", 1, 10, 3)
        
        if st.button("Visualize Directory"):
            if directory_path:
                # Show a progress message while scanning
                progress_placeholder = st.empty()
                progress_bar = st.progress(0)
                progress_placeholder.text("Validating directory path...")
                
                # Validate path
                safe_path = get_safe_path(directory_path)
                if safe_path:
                    try:
                        progress_bar.progress(20)
                        progress_placeholder.text("Scanning directory structure...")
                        
                        # Scan directory
                        st.session_state.selected_directory = safe_path
                        dir_data = scan_directory(safe_path, depth_limit)
                        
                        # Attempt to detect Python environments (non-blocking)
                        try:
                            detected_envs = find_python_environments(str(safe_path), max_depth=depth_limit, include_hidden=False, follow_symlinks=False)
                        except Exception:
                            detected_envs = []

                        progress_bar.progress(80)
                        progress_placeholder.text("Processing data for visualization...")

                        # Store data in session state
                        st.session_state.directory_data = dir_data
                        st.session_state.detected_envs = detected_envs

                        progress_bar.progress(100)
                        progress_placeholder.text("Rendering visualization...")

                        # Refresh the page to show visualization
                        st.rerun()
                    except Exception as e:
                        progress_placeholder.empty()
                        progress_bar.empty()
                        st.error(f"Error scanning directory: {str(e)}")
                else:
                    st.error("Invalid directory path")
            else:
                st.warning("Please enter a directory path")
    
    # Main area for visualization
    if st.session_state.directory_data:
        # Display basic directory info
        st.subheader(f"Directory: {st.session_state.selected_directory}")
        
        # Convert directory data to JSON for D3.js
        directory_json = json.dumps(st.session_state.directory_data)
        
        # Create and display the force-directed graph
        create_force_directed_graph(directory_json)
        
        # Show some statistics about the directory
        stats = calculate_directory_stats(st.session_state.directory_data)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Files", stats["file_count"])
        with col2:
            st.metric("Total Folders", stats["folder_count"])
        with col3:
            st.metric("Max Depth", stats["max_depth"])
        
        # Show detected python environments (from envscan)
        with st.expander("Detected Python Environments"):
            envs = st.session_state.get("detected_envs", [])
            if envs:
                for e in envs:
                    path = e.get("path", "")
                    env_type = e.get("type", "")
                    name = e.get("name", "")
                    python_ver = e.get("python", "")
                    st.write(f"{path} — {env_type} — {name} — {python_ver}")
                try:
                    st.download_button("Export environments (JSON)", json.dumps(envs), file_name="envs.json")
                except Exception:
                    pass
            else:
                st.info("No Python environments detected.")
        
        # Help information
        with st.expander("How to use the visualization"):
            st.markdown("""
            - **Drag nodes** to rearrange the graph
            - **Hover over nodes** to see file/folder details
            - **Click on nodes** to highlight connections
            - **Scroll** to zoom in/out
            - **Drag the background** to pan around
            """)
    else:
        st.info("Select a directory from the sidebar to visualize its structure.")

def calculate_directory_stats(data):
    """Calculate basic statistics about the directory structure."""
    file_count = 0
    folder_count = 0
    max_depth = 0
    
    def traverse(node, depth=0):
        nonlocal file_count, folder_count, max_depth
        max_depth = max(max_depth, depth)
        
        if node["type"] == "file":
            file_count += 1
        else:
            folder_count += 1
            for child in node.get("children", []):
                traverse(child, depth + 1)
    
    traverse(data)
    
    return {
        "file_count": file_count,
        "folder_count": folder_count,
        "max_depth": max_depth
    }

if __name__ == "__main__":
    main()
