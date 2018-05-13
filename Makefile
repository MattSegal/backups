# Requires watchdog from pip
dev:
	watchmedo \
	auto-restart \
	--directory . \
	--recursive \
	--pattern '*.py' \
	--pattern '*.css' \
	--pattern '*.html' \
	-- \
	python3 src/app.py
