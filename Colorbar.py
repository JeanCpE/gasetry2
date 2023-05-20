from branca.element import MacroElement

class Colorbar(MacroElement):
    def __init__(self, colors, vmin, vmax, font_size=12, width_percentage=100):
        self.colors = colors
        self.vmin = vmin
        self.vmax = vmax
        self.font_size = font_size
        self.width_percentage = width_percentage

    def to_html(self):
        n_colors = len(self.colors)
        color_stops = []
        for i, color in enumerate(self.colors):
            stop_percent = i / (n_colors - 1) * 100
            color_stops.append(f'{color} {stop_percent}%')

        gradient = ', '.join(color_stops)
        html = f"""
            <div style="width: {self.width_percentage}%; height: 20px; background: linear-gradient(to right, {gradient});"></div>
            <div style="font-size: {self.font_size}px; margin-top: 5px; text-align: center;">
                <span style="float: left;">{self.vmin}</span>
                <span style="float: right;">{self.vmax}</span>
            </div>
        """
        return html