import streamlit as st
import streamlit.components.v1 as components
from typing import Optional

class TrafficApp:
    report: str
    density: int
    red_on: bool
    green_on: bool
    gmaps_api_key: Optional[str]

    def __init__(self) -> None:
        """Initialize the Streamlit app and load session state."""
        # Configure the Streamlit page
        st.set_page_config(page_title="Traffic Management/Strategy", layout="wide")

        # Initialize or retrieve the report from session state
        self.report = st.session_state.get("report", "")  # type: str

        # Load Google Maps API key from Streamlit secrets (Optional)
        self.gmaps_api_key = st.secrets.get("GMAPS_API_KEY")  # type: Optional[str]

        # Initialize control defaults
        self.density = 0  # type: int
        self.red_on = False  # type: bool
        self.green_on = False  # type: bool

    def render(self) -> None:
        """Render the entire application layout."""
        st.title("🚦 Traffic Management / Strategy")
        col1, col2 = st.columns([3, 1])

        with col1:
            self.render_map()
        with col2:
            self.render_controls()

        st.markdown("---")
        st.caption("⚙️ Built with Streamlit and Google Maps API")

    def render_map(self) -> None:
        """Render the map view using Google Maps Embed API."""
        st.subheader("Map View")

        # Default geographic parameters
        lat: float = 37.7749
        lon: float = -122.4194
        zoom: int = 12

        if not self.gmaps_api_key:
            st.warning(
                "Google Maps API key not found."
                " Please set 'GMAPS_API_KEY' in Streamlit secrets."
            )
            return

        # Construct the embed URL
        map_url: str = (
            f"https://www.google.com/maps/embed/v1/view"
            f"?key={self.gmaps_api_key}"
            f"&center={lat},{lon}"
            f"&zoom={zoom}"
        )

        # Embed via iframe
        components.html(
            f'<iframe width="100%" height="600" src="{map_url}" allowfullscreen></iframe>',
            width="100%",
            height=600,
        )

    def render_controls(self) -> None:
        """Render the control panel for traffic strategy."""
        st.subheader("Controls")

        # Traffic density slider
        self.density = st.slider(
            label="Density",
            min_value=0,
            max_value=100,
            value=getattr(self, 'density', 50),
            help="Traffic density (%)"
        )  # type: int

        # Red/Green toggles
        col_r, col_g = st.columns(2)
        with col_r:
            self.red_on = st.checkbox("Red", value=getattr(self, 'red_on', False))  # type: bool
        with col_g:
            self.green_on = st.checkbox("Green", value=getattr(self, 'green_on', False))  # type: bool

        # Optimize & Generate Report
        if st.button("Optimize & Generate Report"):  # type: ignore
            st.success("Optimization complete! Report generated below.")
            self.report = (
                f"Density set to {self.density}%. Red={self.red_on}, Green={self.green_on}."
            )
            st.session_state.report = self.report  # type: str

        # Display report
        self.report = st.text_area(
            label="Report",
            value=self.report,
            height=300,
            placeholder="Your report will appear here..."
        )  # type: str

if __name__ == "__main__":
    app = TrafficApp()
    app.render()
