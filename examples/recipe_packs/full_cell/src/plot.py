"""Real/local data rendering; demo generation is a separate executable."""
from recipe_runtime import run

def render(config, tables):
    from renderer import render as render_figure
    return render_figure(config, tables)

if __name__ == "__main__":
    raise SystemExit(run("full_cell", render))
