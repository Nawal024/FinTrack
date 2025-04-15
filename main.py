from app import app  # noqa: F401
import routes  # noqa: F401
from utils import create_default_categories_if_empty

# Create default categories if the categories table is empty
create_default_categories_if_empty()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
 
