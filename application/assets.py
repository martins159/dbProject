"""Compile static asset bundles."""

from flask_assets import Bundle, Environment

def compile_auth_assets(app):
    """Configure authorization asset bundles."""
    assets = Environment(app)
    Environment.auto_build = True
    Environment.debug = False
    # Stylesheets Bundle
    less_bundle = Bundle(
        "src/less/account.less",
        filters="less,cssmin",
        output="dist/css/account.css",
        extra={"rel": "stylesheet/less"},
    )
	# Register assets
    assets.register("less_all", less_bundle)
    # Build assets in development mode
    if app.config["FLASK_ENV"] != "production":
        less_bundle.build(force=True)
	
def compile_assets(app):
    """Compile all asset bundles."""
    compile_auth_assets(app)