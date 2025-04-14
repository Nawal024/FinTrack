from app import app  # noqa: F401
import routes  # noqa: F401
from utils import create_default_categories_if_empty

# Create default categories if the categories table is empty
create_default_categories_if_empty()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
